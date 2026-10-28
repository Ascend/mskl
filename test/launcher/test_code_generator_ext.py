#!/usr/bin/python
# -*- coding: UTF-8 -*-
# -------------------------------------------------------------------------
# This file is part of the MindStudio project.
# Copyright (c) 2026 Huawei Technologies Co.,Ltd.
#
# MindStudio is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
#
#          http://license.coscl.org.cn/MulanPSL2
#
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
# -------------------------------------------------------------------------

import ctypes
import os
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from mskl.launcher.code_generator import (
    KernelBinaryLauncher,
    KernelLauncher,
    Launcher,
    TilingLauncher,
    format_of,
    pytype_to_cpp,
)
from mskl.launcher.config import KernelBinaryInvokeConfig, KernelInvokeConfig, TilingConfig
from mskl.launcher.context import context


def make_tiling_config():
    return TilingConfig(
        op_type='Add',
        inputs=[np.zeros([2, 2], dtype=np.float32)],
        outputs=[np.zeros([2, 2], dtype=np.float32)],
    )


class NamedStruct(ctypes.Structure):
    @staticmethod
    def get_namespace():
        return 'Ns::'


class Tensor:
    pass


Tensor.__module__ = 'torch'


class TestTypeConvert(unittest.TestCase):
    def test_pytype_to_cpp_supported(self):
        self.assertEqual(pytype_to_cpp('int'), 'int')
        self.assertEqual(pytype_to_cpp('c_float'), 'float')
        self.assertEqual(pytype_to_cpp('c_int32'), 'int32_t')

    def test_pytype_to_cpp_unsupported(self):
        with self.assertRaises(Exception):
            pytype_to_cpp('unknown_type')

    def test_format_of_supported(self):
        self.assertEqual(format_of('int'), 'i')
        self.assertEqual(format_of('c_double'), 'd')
        self.assertEqual(format_of('c_uint64'), 'K')

    def test_format_of_unsupported(self):
        with self.assertRaises(Exception):
            format_of('unknown_type')


class TestKernelLauncher(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.kernel_src = os.path.join(self.tmp_dir.name, 'kernel.cpp')
        with open(self.kernel_src, 'w', encoding='utf-8'):
            pass
        context.autotune_in_progress = True

    def tearDown(self):
        context.reset()
        self.tmp_dir.cleanup()

    def test_code_gen_all_arg_types(self):
        context.decl_args = [
            1,
            2**40,
            ctypes.c_float(1.0),
            np.zeros(2, dtype=np.float32),
            NamedStruct(),
            object(),
            Tensor(),
        ]
        context.template_args = ['int']
        launcher = KernelLauncher(KernelInvokeConfig(self.kernel_src, 'BasicMatmul'))
        gen_file = os.path.join(self.tmp_dir.name, 'gen.cpp')

        self.assertEqual(launcher.code_gen(gen_file), gen_file)
        with open(gen_file, encoding='utf-8') as f:
            content = f.read()
        self.assertIn('BasicMatmul', content)
        self.assertIn('unsigned long long arg1;', content)
        self.assertIn('Ns::NamedStruct *arg4;', content)
        self.assertIn('__gm__ uint8_t *arg6;', content)
        self.assertIn('<int>', content)

    def test_code_gen_list_arg_raises(self):
        context.decl_args = [[1, 2]]
        context.template_args = []
        launcher = KernelLauncher(KernelInvokeConfig(self.kernel_src, 'BasicMatmul'))
        with self.assertRaises(Exception):
            launcher.code_gen(os.path.join(self.tmp_dir.name, 'gen.cpp'))

    def test_code_gen_invalid_dir_raises(self):
        context.decl_args = [1]
        context.template_args = []
        launcher = KernelLauncher(KernelInvokeConfig(self.kernel_src, 'BasicMatmul'))
        with self.assertRaises(Exception):
            launcher.code_gen(os.path.join(self.tmp_dir.name, 'not_exist', 'gen.cpp'))


class TestTilingLauncher(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_code_gen(self):
        gen_file = os.path.join(self.tmp_dir.name, 'tiling.cpp')
        launcher = TilingLauncher(make_tiling_config())

        self.assertEqual(launcher.code_gen(gen_file), gen_file)
        self.assertTrue(os.path.exists(gen_file))

        # 已存在文件时覆盖生成
        self.assertEqual(launcher.code_gen(gen_file), gen_file)

    def test_code_gen_existing_file_with_invalid_permission(self):
        gen_file = os.path.join(self.tmp_dir.name, 'tiling.cpp')
        with open(gen_file, 'w', encoding='utf-8'):
            pass
        launcher = TilingLauncher(make_tiling_config())
        with patch('mskl.launcher.code_generator.FileChecker.check_input_file', return_value=False):
            with self.assertRaises(PermissionError):
                launcher.code_gen(gen_file)


class TestKernelBinaryLauncher(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.binary_file = os.path.join(self.tmp_dir.name, 'kernel.bin')
        with open(self.binary_file, 'w', encoding='utf-8'):
            pass

    def tearDown(self):
        context.reset()
        self.tmp_dir.cleanup()

    def _make_config(self):
        return KernelBinaryInvokeConfig(self.binary_file, kernel_type='vec', tiling_key=1)

    def test_code_gen_without_op_type_raises(self):
        context.op_type = None
        launcher = KernelBinaryLauncher(self._make_config())
        with self.assertRaises(Exception):
            launcher.code_gen(os.path.join(self.tmp_dir.name, 'launch.cpp'))

    def test_code_gen_with_runtime_impl(self):
        context.op_type = 'Add'
        gen_file = os.path.join(self.tmp_dir.name, 'launch.cpp')
        launcher = KernelBinaryLauncher(self._make_config())
        with patch('mskl.launcher.code_generator.check_runtime_impl', return_value=True):
            self.assertEqual(launcher.code_gen(gen_file), gen_file)
        self.assertTrue(os.path.exists(gen_file))

        # 已存在文件时覆盖生成
        with patch('mskl.launcher.code_generator.check_runtime_impl', return_value=True):
            self.assertEqual(launcher.code_gen(gen_file), gen_file)

    def test_code_gen_without_runtime_impl(self):
        context.op_type = 'Add'
        gen_file = os.path.join(self.tmp_dir.name, 'launch_acl.cpp')
        launcher = KernelBinaryLauncher(self._make_config())
        with patch('mskl.launcher.code_generator.check_runtime_impl', return_value=False):
            self.assertEqual(launcher.code_gen(gen_file), gen_file)
        self.assertTrue(os.path.exists(gen_file))


class TestLauncherDispatch(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.kernel_src = os.path.join(self.tmp_dir.name, 'kernel.cpp')
        with open(self.kernel_src, 'w', encoding='utf-8'):
            pass
        context.autotune_in_progress = True
        context.decl_args = [1]
        context.template_args = []

    def tearDown(self):
        context.reset()
        self.tmp_dir.cleanup()

    def test_launcher_dispatch_kernel(self):
        launcher = Launcher(KernelInvokeConfig(self.kernel_src, 'BasicMatmul'))
        self.assertIsInstance(launcher.launcher, KernelLauncher)

    def test_launcher_dispatch_tiling(self):
        launcher = Launcher(make_tiling_config())
        self.assertIsInstance(launcher.launcher, TilingLauncher)

    def test_launcher_dispatch_unknown_config(self):
        with self.assertRaises(Exception):
            Launcher(None)
