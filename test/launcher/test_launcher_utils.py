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
import json
import unittest

from mskl.utils.launcher_utils import (
    get_workspace_path,
    search_tiling_so,
    search_kernel_binary_files,
    match_kernel_binary_by_op_type,
    match_kernel_binary_by_soc,
    match_kernel_binary_by_json,
    _match_json_shape,
)


def _touch(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('test file')


class TestLauncherUtils(unittest.TestCase):
    def setUp(self):
        self.workspace = './_test_mskl_workspace'
        self._cleanup()
        os.makedirs(self.workspace, exist_ok=True)

    def tearDown(self):
        self._cleanup()

    def _cleanup(self):
        if os.path.exists(self.workspace):
            import shutil

            shutil.rmtree(self.workspace, ignore_errors=True)

    def test_get_workspace_path_default_to_cwd(self):
        self.assertEqual(get_workspace_path(), os.getcwd())

    def test_get_workspace_path_with_relative_path(self):
        os.makedirs(self.workspace, exist_ok=True)
        self.assertEqual(get_workspace_path(self.workspace), os.path.abspath(self.workspace))

    def test_get_workspace_path_invalid(self):
        for invalid in ['', None]:
            if invalid is None:
                continue  # None表示使用当前目录
            self.assertRaises(ValueError, get_workspace_path, invalid)

    def test_get_workspace_path_not_exist(self):
        nonexist = os.path.join(self.workspace, 'not_exist_dir')
        self.assertRaises(FileNotFoundError, get_workspace_path, nonexist)

    def test_search_tiling_so_found(self):
        so_path = os.path.join(
            self.workspace,
            'build_out/_CPack_Packages/Linux/External/custom.run/packages/vendors/customize/'
            'op_impl/ai_core/tbe/op_tiling/liboptiling.so',
        )
        _touch(so_path)
        self.assertEqual(search_tiling_so(self.workspace), os.path.abspath(so_path))

    def test_search_tiling_so_not_found(self):
        self.assertIsNone(search_tiling_so(self.workspace))

    def test_search_tiling_so_prefer_cpack(self):
        # 同时存在时优先选择_CPack_Packages/op_tiling下的liboptiling.so
        cpack_so = os.path.join(
            self.workspace,
            'build_out/_CPack_Packages/Linux/External/custom.run/packages/vendors/customize/'
            'op_impl/ai_core/tbe/op_tiling/liboptiling.so',
        )
        other_so = os.path.join(self.workspace, 'op_host/liboptiling.so')
        _touch(cpack_so)
        _touch(other_so)
        self.assertEqual(search_tiling_so(self.workspace), os.path.abspath(cpack_so))

    def test_search_kernel_binary_files_only_in_kernel_dir(self):
        kernel_o = os.path.join(
            self.workspace,
            'build_out/_CPack_Packages/Linux/External/custom.run/packages/vendors/customize/'
            'op_impl/ai_core/tbe/kernel/ascend910b/custom_op/OpCustom_1.o',
        )
        other_o = os.path.join(
            self.workspace,
            'build_out/_CPack_Packages/Linux/External/custom.run/packages/vendors/customize/'
            'op_impl/ai_core/tbe/op_tiling/other.o',
        )
        _touch(kernel_o)
        _touch(other_o)
        result = search_kernel_binary_files(self.workspace)
        self.assertEqual(result, [os.path.abspath(kernel_o)])

    def test_match_kernel_binary_by_op_type(self):
        o_files = [
            '/p/kernel/ascend950/add_custom/AddCustom_hash_0.o',
            '/p/kernel/ascend950/leaky_relu_custom/LeakyReluCustom_hash_0.o',
            '/p/kernel/ascend950/add_custom_template/AddCustomTemplate_hash_1.o',
        ]
        self.assertEqual(
            match_kernel_binary_by_op_type(o_files, 'AddCustom'),
            ['/p/kernel/ascend950/add_custom/AddCustom_hash_0.o'],
        )
        # 未传op_type时不进行过滤
        self.assertEqual(match_kernel_binary_by_op_type(o_files, None), o_files)

    def test_match_kernel_binary_by_soc(self):
        o_files = [
            '/p/kernel/ascend910_93/add_custom/AddCustom_hash_0.o',
            '/p/kernel/ascend950/add_custom/AddCustom_hash_0.o',
            '/p/kernel/ascend910b/add_custom/AddCustom_hash_0.o',
        ]
        self.assertEqual(
            match_kernel_binary_by_soc(o_files, 'Ascend950PR_9579'),
            ['/p/kernel/ascend950/add_custom/AddCustom_hash_0.o'],
        )
        # 空soc名称时不匹配
        self.assertEqual(match_kernel_binary_by_soc(o_files, ''), [])

    def test_match_json_shape(self):
        # 全为负值（[-2]）表示动态shape
        self.assertTrue(_match_json_shape([-2], [8, 2048]))
        # -1 表示该维度动态
        self.assertTrue(_match_json_shape([-1, 8], [4, 8]))
        self.assertTrue(_match_json_shape([-1, 8], [16, 8]))
        # 固定维度需要精确匹配
        self.assertFalse(_match_json_shape([8, 2048], [4, 8]))
        # rank不匹配
        self.assertFalse(_match_json_shape([8], [8, 2048]))

    def test_match_kernel_binary_by_json(self):
        kernel_a = os.path.join(self.workspace, 'kernel/ascend950/add_custom_template/AddCustomTemplate_hashA.o')
        kernel_b = os.path.join(self.workspace, 'kernel/ascend950/add_custom_template/AddCustomTemplate_hashB.o')
        _touch(kernel_a)
        _touch(kernel_b)
        for kernel, dtype in ((kernel_a, 'float16'), (kernel_b, 'float32')):
            json_path = kernel[:-1] + 'json'
            meta = {
                'supportInfo': {
                    'inputs': [
                        {
                            'name': 'x',
                            'dtype': dtype,
                            'format': 'ND',
                            'shape': [-2],
                            'format_match_mode': 'FormatAgnostic',
                        },
                        {
                            'name': 'y',
                            'dtype': dtype,
                            'format': 'ND',
                            'shape': [-2],
                            'format_match_mode': 'FormatAgnostic',
                        },
                    ],
                    'outputs': [
                        {
                            'name': 'z',
                            'dtype': dtype,
                            'format': 'ND',
                            'shape': [-2],
                            'format_match_mode': 'FormatAgnostic',
                        },
                    ],
                }
            }
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(meta, f)

        io_info = {
            'inputs': [
                {'dtype': 'float16', 'format': 'ND', 'shape': [8, 2048]},
                {'dtype': 'float16', 'format': 'ND', 'shape': [8, 2048]},
            ],
            'outputs': [{'dtype': 'float16', 'format': 'ND', 'shape': [8, 2048]}],
        }
        matched = match_kernel_binary_by_json([kernel_a, kernel_b], io_info)
        self.assertEqual(matched, [kernel_a])
        # json不存在时不参与匹配
        self.assertEqual(match_kernel_binary_by_json(['/p/kernel/x/no_meta.o'], io_info), [])


if __name__ == '__main__':
    unittest.main()
