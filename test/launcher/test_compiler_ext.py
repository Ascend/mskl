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

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from mskl.launcher import compiler
from mskl.launcher.context import context


class FakeResult:
    def __init__(self, returncode=0, stdout='', stderr=''):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class TestThreadSafeSet(unittest.TestCase):
    def setUp(self):
        context.reset()

    def tearDown(self):
        context.reset()

    def test_add_unique_path(self):
        paths = compiler.ThreadSafeSet()
        self.assertEqual(paths.add('/tmp/lib_gen_module.so'), '/tmp/lib_gen_module.so')

    def test_add_duplicate_path_gets_suffix(self):
        paths = compiler.ThreadSafeSet()
        paths.add('/tmp/lib_gen_module.so')
        self.assertEqual(paths.add('/tmp/lib_gen_module.so'), '/tmp/lib_gen_module.1.so')

    def test_add_duplicate_path_increases_suffix(self):
        paths = compiler.ThreadSafeSet()
        paths.add('/tmp/lib_gen_module.so')
        paths.add('/tmp/lib_gen_module.1.so')
        self.assertEqual(paths.add('/tmp/lib_gen_module.so'), '/tmp/lib_gen_module.2.so')

    def test_add_duplicate_custom_name_warns(self):
        paths = compiler.ThreadSafeSet()
        paths.add('/tmp/custom.so')
        with patch('mskl.launcher.compiler.logger.warning') as mock_warning:
            self.assertEqual(paths.add('/tmp/custom.so'), '/tmp/custom.1.so')
            mock_warning.assert_called_once()


class TestCompiledKernel(unittest.TestCase):
    def setUp(self):
        context.reset()
        with patch('mskl.launcher.compiler.NPULauncher'), patch(
            'mskl.launcher.compiler.CompiledKernel._check_constructor_input'
        ):
            self.kernel = compiler.CompiledKernel('_gen_module.so', 'kernel_name')
        self.kernel.__run__ = MagicMock()

    def tearDown(self):
        context.reset()

    def test_getitem_launches_with_blockdim(self):
        self.kernel[8](1, 2)
        self.kernel.__run__.assert_called_once()
        self.assertEqual(self.kernel.__run__.call_args.kwargs['blockdim'], 8)

    def test_call_without_tiling_output_raises(self):
        context.tiling_output = None
        with self.assertRaises(Exception):
            self.kernel()

    def test_call_with_tiling_output(self):
        context.tiling_output = MagicMock(blockdim=4)
        with patch.object(self.kernel, 'launch') as mock_launch:
            self.kernel(1, 2)
            self.assertEqual(mock_launch.call_args.args, (1, 2))
            self.assertEqual(mock_launch.call_args.kwargs, {'blockdim': 4})

    def test_launch_uses_defaults(self):
        context.tiling_output = MagicMock(blockdim=2)
        self.kernel.launch(1, 2, blockdim=2)
        kwargs = self.kernel.__run__.call_args.kwargs
        self.assertEqual(kwargs['blockdim'], 2)
        self.assertEqual(kwargs['timeout'], 300000)
        self.assertEqual(kwargs['repeat'], 1)
        self.assertEqual(kwargs['kernel_name'], 'kernel_name')
        self.assertEqual(context.blockdim, 2)
        self.assertEqual(context.kernel_args, (1, 2))

    def test_launch_with_autotune_keeps_context(self):
        context.autotune_in_progress = True
        self.kernel.launch(1, blockdim=2, stream=3, device_id=0, timeout=10, kernel_name='other', repeat=2)
        kwargs = self.kernel.__run__.call_args.kwargs
        self.assertEqual(kwargs['stream'], 3)
        self.assertEqual(kwargs['device_id'], 0)
        self.assertEqual(kwargs['timeout'], 10)
        self.assertEqual(kwargs['kernel_name'], 'other')
        self.assertEqual(kwargs['repeat'], 2)
        self.assertIsNone(context.blockdim)

    def test_launch_invalid_blockdim_raises(self):
        with self.assertRaises(Exception):
            self.kernel.launch(1, blockdim=0)

    def test_launch_invalid_stream_raises(self):
        with self.assertRaises(Exception):
            self.kernel.launch(1, blockdim=1, stream='bad')

    def test_launch_invalid_device_id_raises(self):
        with self.assertRaises(Exception):
            self.kernel.launch(1, blockdim=1, device_id='bad')

    def test_launch_invalid_timeout_raises(self):
        with self.assertRaises(Exception):
            self.kernel.launch(1, blockdim=1, timeout='bad')

    def test_launch_invalid_kernel_name_raises(self):
        with self.assertRaises(Exception):
            self.kernel.launch(1, blockdim=1, kernel_name=1)


class TestCompileKernel(unittest.TestCase):
    def setUp(self):
        context.reset()
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.build_script = os.path.join(self.tmp_dir.name, 'build.sh')
        self.launch_src = os.path.join(self.tmp_dir.name, 'launch.cpp')
        self.output_so = os.path.join(self.tmp_dir.name, 'gen_module.so')
        for path in (self.build_script, self.launch_src, self.output_so):
            with open(path, 'w', encoding='utf-8'):
                pass

    def tearDown(self):
        context.reset()
        self.tmp_dir.cleanup()

    def test_check_compile_input_invalid_output(self):
        with self.assertRaises(Exception):
            compiler._check_compie_input(self.build_script, self.launch_src, 'gen_module.bin', False)

    def test_compile_use_cache_missing_file_raises(self):
        with patch('mskl.launcher.compiler._check_compie_input'):
            with self.assertRaises(Exception):
                compiler.compile(
                    self.build_script,
                    self.launch_src,
                    os.path.join(self.tmp_dir.name, 'missing.so'),
                    use_cache=True,
                )

    def test_compile_use_cache_returns_kernel(self):
        with patch('mskl.launcher.compiler._check_compie_input'), patch(
            'mskl.launcher.compiler.CompiledKernel'
        ) as mock_kernel:
            result = compiler.compile(self.build_script, self.launch_src, self.output_so, use_cache=True)
        mock_kernel.assert_called_once()
        self.assertIs(result, mock_kernel.return_value)

    def test_compile_success(self):
        with patch('mskl.launcher.compiler._check_compie_input'), patch(
            'mskl.launcher.compiler.CompiledKernel'
        ) as mock_kernel, patch('mskl.launcher.compiler.subprocess.run', return_value=FakeResult(stdout='ok')):
            result = compiler.compile(self.build_script, self.launch_src, self.output_so)
        mock_kernel.assert_called_once()
        self.assertIs(result, mock_kernel.return_value)

    def test_compile_failure_raises(self):
        with patch('mskl.launcher.compiler._check_compie_input'), patch(
            'mskl.launcher.compiler.subprocess.run', return_value=FakeResult(returncode=1, stderr='error')
        ):
            with self.assertRaises(Exception):
                compiler.compile(self.build_script, self.launch_src, self.output_so)


class TestCompiledExecutable(unittest.TestCase):
    def setUp(self):
        context.reset()
        self.checker_patcher = patch.object(compiler.CompiledExecutable, '_check_constructor_input')
        self.checker_patcher.start()

    def tearDown(self):
        self.checker_patcher.stop()
        context.reset()

    def test_get_executable_path(self):
        executable = compiler.CompiledExecutable('_gen_executable')
        self.assertEqual(executable.get_executable_path(), '_gen_executable')

    def test_launch_prelaunch_returns_empty(self):
        context.prelaunch_flag = True
        executable = compiler.CompiledExecutable('_gen_executable')
        self.assertEqual(executable(1, 2), '')

    def test_launch_success(self):
        executable = compiler.CompiledExecutable('_gen_executable')
        with patch('mskl.launcher.compiler.subprocess.run', return_value=FakeResult(stdout='output')):
            self.assertEqual(executable(1, 2), '')

    def test_launch_with_profiling_cmd(self):
        executable = compiler.CompiledExecutable('_gen_executable')
        with patch(
            'mskl.launcher.compiler.subprocess.run', return_value=FakeResult()
        ) as mock_run:
            executable(1, profiling_cmd=['msprof'])
        cmd = mock_run.call_args.args[0]
        self.assertEqual(cmd, ['msprof', '_gen_executable', '1'])

    def test_launch_autotune_returns_stdout(self):
        context.autotune_in_progress = True
        executable = compiler.CompiledExecutable('_gen_executable')
        with patch('mskl.launcher.compiler.subprocess.run', return_value=FakeResult(stdout='output')):
            self.assertEqual(executable(1), 'output')

    def test_launch_failure_raises(self):
        executable = compiler.CompiledExecutable('_gen_executable')
        with patch('mskl.launcher.compiler.subprocess.run', return_value=FakeResult(returncode=1, stderr='error')):
            with self.assertRaises(Exception):
                executable(1)


class TestCompileExecutable(unittest.TestCase):
    def setUp(self):
        context.reset()
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.build_script = os.path.join(self.tmp_dir.name, 'build.sh')
        self.src_file = os.path.join(self.tmp_dir.name, 'launch.cpp')
        self.output_bin = os.path.join(self.tmp_dir.name, 'gen_executable')
        for path in (self.build_script, self.src_file, self.output_bin):
            with open(path, 'w', encoding='utf-8'):
                pass

    def tearDown(self):
        context.reset()
        self.tmp_dir.cleanup()

    def test_use_cache_missing_file_raises(self):
        with self.assertRaises(Exception):
            compiler.compile_executable(
                self.build_script, self.src_file, os.path.join(self.tmp_dir.name, 'missing'), use_cache=True
            )

    def test_prelaunch_returns_executable(self):
        context.prelaunch_flag = True
        executable = compiler.compile_executable(self.build_script, self.src_file, self.output_bin)
        self.assertEqual(context.build_script, self.build_script)
        self.assertEqual(context.kernel_src_file, os.path.realpath(self.src_file))
        self.assertEqual(executable.get_executable_path(), os.path.realpath(self.output_bin))

    def test_compile_success(self):
        with patch('mskl.launcher.compiler.subprocess.run', return_value=FakeResult(stdout='ok')):
            executable = compiler.compile_executable(self.build_script, self.src_file, self.output_bin)
        self.assertEqual(executable.get_executable_path(), os.path.realpath(self.output_bin))

    def test_compile_failure_raises(self):
        with patch('mskl.launcher.compiler.subprocess.run', return_value=FakeResult(returncode=1, stderr='error')):
            with self.assertRaises(Exception):
                compiler.compile_executable(self.build_script, self.src_file, self.output_bin)
