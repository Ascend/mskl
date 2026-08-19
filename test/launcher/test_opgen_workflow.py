#!/usr/bin/python
# -*- coding: UTF-8 -*-
# -------------------------------------------------------------------------
# This file is part of the MindStudio project.
# Copyright (c) 2025 Huawei Technologies Co.,Ltd.
#
# MindStudio is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#
#          http://license.coscl.org.cn/MulanPSL2
#
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
# -------------------------------------------------------------------------
import os
import shutil
import numpy as np
import unittest
from unittest.mock import patch

from mskl.launcher.opgen_workflow import (
    TilingOutput,
    tiling_func,
    get_kernel_from_binary,
    TMP_FOLDER,
    _build_io_info,
)
from mskl.launcher import opgen_workflow
from mskl.launcher.context import context
from mskl.utils import safe_check

tiling_dict = {
    "blockdim": 8,
    "workspace_size": 64,
    "tiling_data": [1, 2, 3, 4],
    "tiling_key": 1111,
}


def mock_tiling_func():
    return tiling_dict


def _touch(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('test file')


def _build_workspace(with_tiling_so=True, kernel_o_files=(), kernel_soc='ascend910b'):
    ws = os.path.join(os.getcwd(), '_test_mskl_ws')
    if os.path.exists(ws):
        shutil.rmtree(ws, ignore_errors=True)
    base = os.path.join(
        ws,
        'build_out/_CPack_Packages/Linux/External/custom.run/packages/vendors/customize/op_impl/ai_core/tbe',
    )
    if with_tiling_so:
        _touch(os.path.join(base, 'op_tiling/liboptiling.so'))
    for o in kernel_o_files:
        _touch(os.path.join(base, 'kernel', kernel_soc, 'custom_op', o))
    return ws


class TestOpgenWorkflow(unittest.TestCase):
    LIB = 'test_tiling.so'
    CPP = '_mskl_gen_tiling.cpp'
    TIL_LIB = '_mskl_gen_tiling.so'
    KERNEL_CPP = '_mskl_gen_binary_launch.cpp'
    KERNEL_LIB = '_mskl_gen_binary_module.so'
    KERNEL_BINARY_PATH = 'kernel.o'

    @classmethod
    def setUpClass(cls):
        with os.fdopen(
            os.open(TestOpgenWorkflow.LIB, safe_check.OPEN_FLAGS, safe_check.SAVE_DATA_FILE_AUTHORITY), 'w'
        ) as f:
            f.truncate()
            f.write('this is a test so')
        with os.fdopen(
            os.open(TestOpgenWorkflow.KERNEL_BINARY_PATH, safe_check.OPEN_FLAGS, safe_check.SAVE_DATA_FILE_AUTHORITY),
            'w',
        ) as f:
            f.truncate()
            f.write('this is a test kernel binary file')

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(TMP_FOLDER):
            shutil.rmtree(TMP_FOLDER, ignore_errors=True)
        if os.path.exists(TestOpgenWorkflow.LIB):
            os.remove(TestOpgenWorkflow.LIB)
        if os.path.exists(TestOpgenWorkflow.CPP):
            os.remove(TestOpgenWorkflow.CPP)
        if os.path.exists(TestOpgenWorkflow.TIL_LIB):
            os.remove(TestOpgenWorkflow.LIB)
        if os.path.exists(TestOpgenWorkflow.KERNEL_BINARY_PATH):
            os.remove(TestOpgenWorkflow.KERNEL_BINARY_PATH)
        if os.path.exists(TestOpgenWorkflow.KERNEL_CPP):
            os.remove(TestOpgenWorkflow.KERNEL_CPP)
        if os.path.exists(TestOpgenWorkflow.KERNEL_LIB):
            os.remove(TestOpgenWorkflow.KERNEL_LIB)

    @patch("mskl.launcher.opgen_workflow.compile_tiling")
    def test_tiling_func_execute_success(self, mock_compile_tiling):
        # 消除对cann的编译依赖
        mock_compile_tiling.return_value = mock_tiling_func

        a = np.random.uniform(1, 100, [2, 32]).astype(np.float16)
        b = np.random.uniform(1, 100, [2, 32]).astype(np.float16)
        c = np.zeros([2, 32]).astype(np.float16)
        inputs_info = [
            {"shape": [2, 32], "dtype": "float16", "format": "ND"},
            {"shape": [2, 32], "dtype": "float16", "format": "ND"},
        ]
        outputs_info = [{"shape": [2, 32], "dtype": "float16", "format": "ND"}]
        output = tiling_func(
            op_type="AddCustom",
            inputs_info=inputs_info,
            outputs_info=outputs_info,
            inputs=[a, b],
            outputs=[c],
            attr={
                "a1": 1,
                "a2": False,
                "a3": "ssss",
                "a4": 1.2,
                "a5": [111.111, 111.222, 111.333],
                "a6": [True, False],
                "a7": ["asdf", "zxcv"],
                "a8": [[1, 2, 3, 4], [5, 6, 7, 8], [5646, 2345]],
                "a9": [111, 222, 333],
            },
            lib_path=TestOpgenWorkflow.LIB,
        )
        mock_compile_tiling.assert_called_once()
        self.assertEqual(output.blockdim, TilingOutput(tiling_dict).blockdim)

    @patch("mskl.launcher.opgen_workflow.compile_tiling")
    def test_tiling_func_with_list_attr_tensor_list_execute_success(self, mock_compile_tiling):
        # 消除对cann的编译依赖
        mock_compile_tiling.return_value = mock_tiling_func

        a = np.random.uniform(1, 100, [2, 32]).astype(np.float16)
        b = np.random.uniform(1, 100, [2, 32]).astype(np.float16)
        c = np.zeros([2, 32]).astype(np.float16)
        inputs_info = [
            [
                {"shape": [2, 32], "dtype": "float16", "format": "ND"},
                {"shape": [2, 32], "dtype": "float16", "format": "ND"},
                {"shape": [2, 32], "dtype": "float16", "format": "ND"},
            ],
            {"shape": [2, 32], "dtype": "float16", "format": "ND"},
        ]
        outputs_info = [{"shape": [2, 32], "dtype": "float16", "format": "ND"}]
        output = tiling_func(
            op_type="AddCustom",
            inputs_info=inputs_info,
            outputs_info=outputs_info,
            inputs=[[a, a, b], b],
            outputs=[c],
            attr=[
                {"name": "a1", "dtype": "int", "value": 1},
                {"name": "a2", "dtype": "bool", "value": False},
                {"name": "a3", "dtype": "str", "value": "ssss"},
                {"name": "a3_1", "dtype": "string", "value": "ssss"},
                {"name": "a4", "dtype": "float", "value": 1.2},
                {"name": "a5", "dtype": "list_float", "value": [111.111, 111.222, 111.333]},
                {"name": "a6", "dtype": "list_bool", "value": [True, False]},
                {"name": "a7", "dtype": "list_str", "value": ["asdf", "zxcv"]},
                {"name": "a7_1", "dtype": "list_string", "value": ["asdf", "zxcv"]},
                {"name": "a8", "dtype": "list_list_int", "value": [[1, 2, 3, 4], [5, 6, 7, 8], [5646, 2345]]},
                {"name": "a9", "dtype": "list_int", "value": [111, 222, 333]},
                {"name": "a10", "dtype": "list_int", "value": []},
                {"name": "a11", "dtype": "int64", "value": 2},
                {"name": "a12", "dtype": "float32", "value": 1.3},
            ],
            lib_path=TestOpgenWorkflow.LIB,
        )
        mock_compile_tiling.assert_called_once()
        self.assertEqual(output.blockdim, TilingOutput(tiling_dict).blockdim)

    @patch("mskl.launcher.opgen_workflow.compile_kernel_binary")
    def test_get_kernel_from_binary_execute_success(self, mock_compile_kernel_binary):
        with patch('mskl.utils.launcher_utils.check_runtime_impl', return_value=True):
            with patch('mskl.utils.launcher_utils.get_cann_path', return_value=""):
                mock_compile_kernel_binary.return_value = None
                context.tiling_output = TilingOutput(tiling_dict)
                context.op_type = 'TestOpType'

                kernel = get_kernel_from_binary(TestOpgenWorkflow.KERNEL_BINARY_PATH, 'mix')
                mock_compile_kernel_binary.assert_called_once()
                self.assertEqual(kernel, None)

    @patch("mskl.launcher.opgen_workflow.compile_tiling")
    def test_tiling_func_auto_search_liboptiling_by_workspace(self, mock_compile_tiling):
        mock_compile_tiling.return_value = mock_tiling_func
        ws = _build_workspace(with_tiling_so=True)

        a = np.random.uniform(1, 100, [2, 32]).astype(np.float16)
        b = np.random.uniform(1, 100, [2, 32]).astype(np.float16)
        c = np.zeros([2, 32]).astype(np.float16)
        inputs_info = [
            {"shape": [2, 32], "dtype": "float16", "format": "ND"},
            {"shape": [2, 32], "dtype": "float16", "format": "ND"},
        ]
        outputs_info = [{"shape": [2, 32], "dtype": "float16", "format": "ND"}]
        try:
            output = tiling_func(
                op_type="AddCustom",
                inputs_info=inputs_info,
                outputs_info=outputs_info,
                inputs=[a, b],
                outputs=[c],
                workspace=ws,
            )
            mock_compile_tiling.assert_called_once()
            self.assertEqual(output.blockdim, TilingOutput(tiling_dict).blockdim)
            self.assertEqual(context.workspace, os.path.abspath(ws))
            expected_so = os.path.join(
                ws,
                'build_out/_CPack_Packages/Linux/External/custom.run/packages/vendors/customize/'
                'op_impl/ai_core/tbe/op_tiling/liboptiling.so',
            )
            gen_cpp = os.path.join(TMP_FOLDER, f'_mskl_gen_tiling.{opgen_workflow.TILING_FUNC_CNT}.cpp')
            with open(gen_cpp, 'r', encoding='utf-8') as f:
                self.assertIn(os.path.realpath(expected_so), f.read())
        finally:
            context.workspace = None
            if os.path.exists(ws):
                shutil.rmtree(ws, ignore_errors=True)

    @patch("mskl.launcher.opgen_workflow.compile_tiling")
    def test_tiling_func_explicit_lib_path_priority_over_workspace(self, mock_compile_tiling):
        mock_compile_tiling.return_value = mock_tiling_func
        ws = _build_workspace(with_tiling_so=True)
        with open(TestOpgenWorkflow.LIB, 'w', encoding='utf-8') as f:
            f.write('this is a test so')

        a = np.random.uniform(1, 100, [2, 32]).astype(np.float16)
        b = np.random.uniform(1, 100, [2, 32]).astype(np.float16)
        c = np.zeros([2, 32]).astype(np.float16)
        inputs_info = [
            {"shape": [2, 32], "dtype": "float16", "format": "ND"},
            {"shape": [2, 32], "dtype": "float16", "format": "ND"},
        ]
        outputs_info = [{"shape": [2, 32], "dtype": "float16", "format": "ND"}]
        try:
            output = tiling_func(
                op_type="AddCustom",
                inputs_info=inputs_info,
                outputs_info=outputs_info,
                inputs=[a, b],
                outputs=[c],
                lib_path=TestOpgenWorkflow.LIB,
                workspace=ws,
            )
            mock_compile_tiling.assert_called_once()
            self.assertEqual(output.blockdim, TilingOutput(tiling_dict).blockdim)
            gen_cpp = os.path.join(TMP_FOLDER, f'_mskl_gen_tiling.{opgen_workflow.TILING_FUNC_CNT}.cpp')
            with open(gen_cpp, 'r', encoding='utf-8') as f:
                gen_src = f.read()
            self.assertIn(os.path.realpath(TestOpgenWorkflow.LIB), gen_src)
            self.assertNotIn('liboptiling.so', gen_src)
        finally:
            context.workspace = None
            if os.path.exists(ws):
                shutil.rmtree(ws, ignore_errors=True)

    @patch("mskl.launcher.opgen_workflow.compile_kernel_binary")
    def test_get_kernel_from_binary_auto_search_single_o(self, mock_compile_kernel_binary):
        with patch('mskl.utils.launcher_utils.check_runtime_impl', return_value=True):
            with patch('mskl.utils.launcher_utils.get_cann_path', return_value=""):
                mock_compile_kernel_binary.return_value = None
                ws = _build_workspace(with_tiling_so=False, kernel_o_files=['TestOpType_1.o'])
                context.tiling_output = TilingOutput(tiling_dict)
                context.op_type = 'TestOpType'
                context.workspace = os.path.abspath(ws)
                try:
                    kernel = get_kernel_from_binary(None, 'mix', 1)
                    mock_compile_kernel_binary.assert_called_once()
                    self.assertEqual(kernel, None)
                    gen_cpp = os.path.join(
                        TMP_FOLDER, f'_mskl_gen_binary_launch.{opgen_workflow.GET_KERNEL_FROM_BINARY_CNT}.cpp'
                    )
                    with open(gen_cpp, 'r', encoding='utf-8') as f:
                        self.assertIn('TestOpType_1.o', f.read())
                finally:
                    context.workspace = None
                    if os.path.exists(ws):
                        shutil.rmtree(ws, ignore_errors=True)

    def test_get_kernel_from_binary_auto_search_select_by_soc(self):
        # 多个soc目录下存在同名同tiling_key的kernel，应优先选择与设备soc匹配的
        with patch('mskl.launcher.opgen_workflow.compile_kernel_binary') as mock_compile_kernel_binary:
            with patch('mskl.utils.launcher_utils.check_runtime_impl', return_value=True):
                with patch('mskl.utils.launcher_utils.get_cann_path', return_value=""):
                    with patch('mskl.launcher.opgen_workflow.get_device_soc_name', return_value='Ascend950PR_9579'):
                        mock_compile_kernel_binary.return_value = None
                        ws = _build_workspace(
                            with_tiling_so=False, kernel_o_files=['TestOpType_1.o'], kernel_soc='ascend910_93'
                        )
                        _build_workspace_extra = os.path.join(
                            os.getcwd(),
                            '_test_mskl_ws',
                            'build_out/_CPack_Packages/Linux/External/custom.run/packages/vendors/customize/'
                            'op_impl/ai_core/tbe/kernel',
                        )
                        for soc in ('ascend950', 'ascend910b'):
                            os.makedirs(os.path.join(_build_workspace_extra, soc, 'custom_op'), exist_ok=True)
                            _touch(os.path.join(_build_workspace_extra, soc, 'custom_op', 'TestOpType_1.o'))
                        context.tiling_output = TilingOutput(tiling_dict)
                        context.op_type = 'TestOpType'
                        context.workspace = os.path.abspath(ws)
                        try:
                            kernel = get_kernel_from_binary(None, 'mix', 1)
                            mock_compile_kernel_binary.assert_called_once()
                            self.assertEqual(kernel, None)
                            gen_cpp = os.path.join(
                                TMP_FOLDER,
                                f'_mskl_gen_binary_launch.{opgen_workflow.GET_KERNEL_FROM_BINARY_CNT}.cpp',
                            )
                            with open(gen_cpp, 'r', encoding='utf-8') as f:
                                self.assertIn('ascend950/custom_op/TestOpType_1.o', f.read())
                                self.assertNotIn('ascend910_93', f.read())
                        finally:
                            context.workspace = None
                            if os.path.exists(ws):
                                shutil.rmtree(ws, ignore_errors=True)

    def test_build_io_info_from_tensors(self):
        x = np.zeros([8, 2048], dtype=np.float16)
        y = np.zeros([8, 2048], dtype=np.float16)
        z = np.zeros([8, 2048], dtype=np.float16)
        info = _build_io_info([x, y], [z], None, None)
        self.assertEqual(info['inputs'][0]['dtype'], 'float16')
        self.assertEqual(info['inputs'][0]['format'], 'ND')
        self.assertEqual(info['inputs'][0]['shape'], [8, 2048])
        self.assertEqual(len(info['inputs']), 2)
        self.assertEqual(info['outputs'][0]['dtype'], 'float16')

    @patch("mskl.launcher.opgen_workflow.compile_kernel_binary")
    def test_get_kernel_from_binary_auto_search_select_by_json(self, mock_compile_kernel_binary):
        # 多个soc相同、同算子名的kernel，根据同目录json中的dtype区分
        with patch('mskl.utils.launcher_utils.check_runtime_impl', return_value=True):
            with patch('mskl.utils.launcher_utils.get_cann_path', return_value=""):
                with patch('mskl.launcher.opgen_workflow.get_device_soc_name', return_value='Ascend950PR_9579'):
                    mock_compile_kernel_binary.return_value = None
                    ws = _build_workspace(
                        with_tiling_so=False,
                        kernel_soc='ascend950',
                        kernel_o_files=['TestOpType_f16.o', 'TestOpType_f32.o'],
                    )
                    # 为两个 .o 生成描述不同dtype的json
                    base = os.path.join(
                        ws,
                        'build_out/_CPack_Packages/Linux/External/custom.run/packages/vendors/customize/'
                        'op_impl/ai_core/tbe/kernel/ascend950/custom_op',
                    )
                    for o_name, dtype in (('TestOpType_f16.o', 'float16'), ('TestOpType_f32.o', 'float32')):
                        meta = {
                            'supportInfo': {
                                'inputs': [{'dtype': dtype, 'format': 'ND', 'shape': [-2]}],
                                'outputs': [{'dtype': dtype, 'format': 'ND', 'shape': [-2]}],
                            }
                        }
                        with open(os.path.join(base, o_name[:-1] + 'json'), 'w', encoding='utf-8') as f:
                            import json

                            json.dump(meta, f)
                    context.tiling_output = TilingOutput(tiling_dict)
                    context.op_type = 'TestOpType'
                    context.workspace = os.path.abspath(ws)
                    context.io_info = {
                        'inputs': [{'dtype': 'float16', 'format': 'ND', 'shape': [8, 2048]}],
                        'outputs': [{'dtype': 'float16', 'format': 'ND', 'shape': [8, 2048]}],
                    }
                    try:
                        kernel = get_kernel_from_binary(None, 'mix', 1)
                        mock_compile_kernel_binary.assert_called_once()
                        self.assertEqual(kernel, None)
                        gen_cpp = os.path.join(
                            TMP_FOLDER, f'_mskl_gen_binary_launch.{opgen_workflow.GET_KERNEL_FROM_BINARY_CNT}.cpp'
                        )
                        with open(gen_cpp, 'r', encoding='utf-8') as f:
                            self.assertIn('TestOpType_f16.o', f.read())
                    finally:
                        context.workspace = None
                        context.io_info = None
                        if os.path.exists(ws):
                            shutil.rmtree(ws, ignore_errors=True)

    def test_get_kernel_from_binary_auto_search_no_o_found(self):
        ws = _build_workspace(with_tiling_so=False)
        context.tiling_output = TilingOutput(tiling_dict)
        context.op_type = 'TestOpType'
        context.workspace = os.path.abspath(ws)
        try:
            self.assertRaises(FileNotFoundError, get_kernel_from_binary, None, 'mix', 1)
        finally:
            context.workspace = None
            if os.path.exists(ws):
                shutil.rmtree(ws, ignore_errors=True)
