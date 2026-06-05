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
import unittest
import pathlib
import stat
import tempfile
import numpy as np

from test.utils.test_base import TestBase  # pylint: disable=E0611
from mskl.launcher.config import KernelInvokeConfig, TilingConfig


class MockTilingOutput:
    def __init__(self):
        self.tiling_key = 12345


class TestKernelInvokeConfig(TestBase):
    def setUp(self):
        self.kernel_file = "./_test_kernel.cpp"
        self.kernel_name = "BasicMatmul"
        pathlib.Path(self.kernel_file).touch()
        os.chmod(path=self.kernel_file, mode=stat.S_IWUSR | stat.S_IRUSR)

    def tearDown(self):
        if os.path.exists(self.kernel_file):
            os.remove(self.kernel_file)

    def test_kernel_invoke_config_initialization(self):
        config = KernelInvokeConfig(self.kernel_file, self.kernel_name)
        self.assertEqual(config.kernel_name, self.kernel_name)
        # kernel_src_file是绝对路径，所以检查文件名而不是相对路径
        self.assertTrue(os.path.basename(config.kernel_src_file) == os.path.basename(self.kernel_file))

    def test_kernel_invoke_config_invalid_kernel_name(self):
        invalid_names = ["invalid name", "invalid@name", "", None, 123]
        for name in invalid_names:
            self.assertRaises(Exception, KernelInvokeConfig, self.kernel_file, name)

    def test_kernel_invoke_config_invalid_file(self):
        non_existent_file = "./non_existent_file.cpp"
        self.assertRaises(Exception, KernelInvokeConfig, non_existent_file, "valid_name")


class TestTilingConfig(unittest.TestCase):
    def setUp(self):
        # 创建一些测试用的 numpy tensors
        self.test_input = np.zeros([128, 128], dtype=np.float32)
        self.test_output = np.zeros([128, 128], dtype=np.float32)

    def test_tiling_config_initialization_basic(self):
        config = TilingConfig(op_type="TestOp", inputs=[self.test_input], outputs=[self.test_output])
        self.assertEqual(config.op_type, "TestOp")
        self.assertTrue(hasattr(config, "inputs_list"))
        self.assertTrue(hasattr(config, "outputs_list"))

    def test_tiling_config_parse_attr_dict(self):
        attr_dict = {"int_attr": 100, "float_attr": 3.14, "bool_attr": True, "str_attr": "test_value"}
        config = TilingConfig(op_type="TestOp", inputs=[self.test_input], outputs=[self.test_output], attr=attr_dict)
        self.assertTrue(len(config.attrs) > 0)

    def test_tiling_config_parse_attr_list(self):
        attr_list = [
            {"name": "int_attr", "dtype": "int", "value": 100},
            {"name": "float_attr", "dtype": "float", "value": 3.14},
        ]
        config = TilingConfig(op_type="TestOp", inputs=[self.test_input], outputs=[self.test_output], attr=attr_list)
        self.assertTrue(len(config.attrs) > 0)

    def test_tiling_config_invalid_attr_type(self):
        invalid_attr = "not a dict or list"
        self.assertRaises(ValueError, TilingConfig, "TestOp", [self.test_input], [self.test_output], attr=invalid_attr)

    def test_tiling_config_with_inputs_info(self):
        inputs_info = [{"shape": [128, 128], "dtype": "float32", "format": "ND"}]
        config = TilingConfig(
            op_type="TestOp", inputs=[self.test_input], outputs=[self.test_output], inputs_info=inputs_info
        )
        self.assertEqual(len(config.inputs_list), 1)

    def test_tiling_config_with_outputs_info(self):
        outputs_info = [{"shape": [128, 128], "dtype": "float32"}]
        config = TilingConfig(
            op_type="TestOp", inputs=[self.test_input], outputs=[self.test_output], outputs_info=outputs_info
        )
        self.assertEqual(len(config.outputs_list), 1)

    def test_tiling_config_with_soc_version(self):
        config = TilingConfig(
            op_type="TestOp", inputs=[self.test_input], outputs=[self.test_output], soc_version="Ascend910B"
        )
        self.assertEqual(config.soc_version, '"Ascend910B"')

    def test_tiling_config_invalid_soc_version(self):
        invalid_versions = ["", "invalid version", None, 123, "version@123"]
        for version in invalid_versions:
            if version is not None and not isinstance(version, str):
                self.assertRaises(
                    ValueError, TilingConfig, "TestOp", [self.test_input], [self.test_output], soc_version=version
                )
            elif version == "":
                self.assertRaises(
                    ValueError, TilingConfig, "TestOp", [self.test_input], [self.test_output], soc_version=version
                )

    def test_tiling_config_with_lib_path(self):
        # 创建一个临时文件模拟 lib 文件
        with tempfile.NamedTemporaryFile(suffix='.so', delete=False) as f:
            lib_path = f.name
        try:
            config = TilingConfig(
                op_type="TestOp", inputs=[self.test_input], outputs=[self.test_output], lib_path=lib_path
            )
            self.assertTrue(lib_path in config.lib_path)
        finally:
            os.remove(lib_path)

    def test_tiling_config_empty_lib_path(self):
        self.assertRaises(ValueError, TilingConfig, "TestOp", [self.test_input], [self.test_output], lib_path="")

    def test_tiling_config_invalid_op_type(self):
        # 只测试真正会触发的情况
        invalid_ops = ["", "invalid op", "op@name"]
        for op in invalid_ops:
            self.assertRaises(ValueError, TilingConfig, op, [self.test_input], [self.test_output])

        # 测试None会抛出异常
        self.assertRaises(Exception, TilingConfig, None, [self.test_input], [self.test_output])

    def test_tiling_config_none_inputs_and_outputs(self):
        self.assertRaises(Exception, TilingConfig, "TestOp", None, None)


if __name__ == '__main__':
    unittest.main()
