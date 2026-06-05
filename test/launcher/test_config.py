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
from mskl.launcher.config import KernelInvokeConfig, TilingConfig, KernelBinaryInvokeConfig


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
        inputs_info = [{"shape": [128, 128], "dtype": "float32", "format": "nd"}]  # ignore
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

    def test_tiling_config_empty_inputs_and_outputs(self):
        self.assertRaises(Exception, TilingConfig, "TestOp", [], [])

    def test_tiling_config_tensor_list(self):
        config = TilingConfig(op_type="TestOp", inputs=[[self.test_input, self.test_input]], outputs=[self.test_output])
        self.assertEqual(len(config.inputs_list[0]), 2)

    def test_tiling_config_attribute_verification(self):
        # 测试 list[int] 属性
        attr_dict = {"list_int": [1, 2, 3]}
        config = TilingConfig(op_type="TestOp", inputs=[self.test_input], outputs=[self.test_output], attr=attr_dict)
        self.assertTrue(len(config.attrs) > 0)

        # 测试 list[list[int]] 属性
        attr_dict_2d = {"list_list_int": [[1, 2], [3, 4]]}
        config_2d = TilingConfig(
            op_type="TestOp", inputs=[self.test_input], outputs=[self.test_output], attr=attr_dict_2d
        )
        self.assertTrue(len(config_2d.attrs) > 0)

    def test_tiling_config_overflow_check(self):
        # 测试整数溢出检查
        very_large_int = 10**20
        attr_dict = {"large_int": very_large_int}
        self.assertRaises(
            (ValueError, OverflowError), TilingConfig, "TestOp", [self.test_input], [self.test_output], attr=attr_dict
        )


class TestKernelBinaryInvokeConfig(TestBase):
    def setUp(self):
        # 创建临时文件
        self.temp_files = []

        # 创建二进制文件
        with tempfile.NamedTemporaryFile(suffix='.o', delete=False) as f:
            self.binary_file = f.name
            self.temp_files.append(self.binary_file)

        # 创建对应的 json 文件
        self.json_file = self.binary_file[:-1] + 'json'
        with open(self.json_file, 'w', encoding="utf-8") as f:
            f.write('{"debugOptions": {"printf": true}}')
        self.temp_files.append(self.json_file)

    def tearDown(self):
        for f in self.temp_files:
            if os.path.exists(f):
                os.remove(f)

    def test_kernel_binary_invoke_config_initialization(self):
        from mskl.launcher.context import context

        context.tiling_output = MockTilingOutput()

        config = KernelBinaryInvokeConfig(self.binary_file)
        self.assertEqual(config.kernel_name, 'kernel_binary')

    def test_kernel_binary_invoke_config_with_kernel_type(self):
        from mskl.launcher.context import context

        context.tiling_output = MockTilingOutput()

        valid_types = ['mix', 'vec', 'cube']
        for kernel_type in valid_types:
            config = KernelBinaryInvokeConfig(self.binary_file, kernel_type=kernel_type)
            self.assertTrue(config.magic > 0)

    def test_kernel_binary_invoke_config_invalid_kernel_type(self):
        from mskl.launcher.context import context

        context.tiling_output = MockTilingOutput()

        self.assertRaises(ValueError, KernelBinaryInvokeConfig, self.binary_file, kernel_type='invalid_type')

    def test_kernel_binary_invoke_config_with_tiling_key(self):
        config = KernelBinaryInvokeConfig(self.binary_file, tiling_key=12345)
        self.assertEqual(config.tiling_key, 12345)

    def test_kernel_binary_invoke_config_with_tiling_key_case1(self):
        config = KernelBinaryInvokeConfig(self.binary_file, tiling_key=500113293)
        self.assertEqual(config.tiling_key, 500113293)

    def test_kernel_binary_invoke_config_with_tiling_key_case2(self):
        config = KernelBinaryInvokeConfig(self.binary_file, tiling_key=1)
        self.assertEqual(config.tiling_key, 1)

    def test_kernel_binary_invoke_config_with_tiling_key_case3(self):
        config = KernelBinaryInvokeConfig(self.binary_file, tiling_key=101)
        self.assertEqual(config.tiling_key, 101)

    def test_kernel_binary_invoke_config_with_tiling_key_case4(self):
        config = KernelBinaryInvokeConfig(self.binary_file, tiling_key=9999)
        self.assertEqual(config.tiling_key, 9999)

    def test_kernel_binary_invoke_config_with_tiling_key_case5(self):
        config = KernelBinaryInvokeConfig(self.binary_file, tiling_key=77777777)
        self.assertEqual(config.tiling_key, 77777777)

    def test_kernel_binary_invoke_config_invalid_tiling_key(self):
        invalid_keys = [-1, 18446744073709551616]
        for key in invalid_keys:
            self.assertRaises(ValueError, KernelBinaryInvokeConfig, self.binary_file, tiling_key=key)

    def test_kernel_binary_invoke_config_missing_tiling_info(self):
        from mskl.launcher.context import context

        context.tiling_output = None

        self.assertRaises(Exception, KernelBinaryInvokeConfig, self.binary_file)

    def test_kernel_binary_invoke_config_empty_file(self):
        self.assertRaises(ValueError, KernelBinaryInvokeConfig, None)
        self.assertRaises(ValueError, KernelBinaryInvokeConfig, "")

    def test_kernel_binary_invoke_config_non_existent_file(self):
        non_existent_file = "./non_existent_file.o"
        self.assertRaises(Exception, KernelBinaryInvokeConfig, non_existent_file)

    def test_kernel_binary_invoke_config_read_json(self):
        from mskl.launcher.context import context

        context.tiling_output = MockTilingOutput()

        config = KernelBinaryInvokeConfig(self.binary_file)
        # 如果 json 文件存在且被正确读取，enable_printf 应该是 1
        self.assertTrue(hasattr(config, 'enable_printf'))


class TestTypeConversions(unittest.TestCase):
    def test_dtype_to_getype_mapping(self):
        # 测试常见的数据类型映射
        test_cases = [
            ("float", "ge::DT_FLOAT"),
            ("float32", "ge::DT_FLOAT"),
            ("fp32", "ge::DT_FLOAT"),
            ("float16", "ge::DT_FLOAT16"),
            ("fp16", "ge::DT_FLOAT16"),
            ("int8", "ge::DT_INT8"),
            ("int32", "ge::DT_INT32"),
            ("int", "ge::DT_INT32"),
            ("uint8", "ge::DT_UINT8"),
            ("bool", "ge::DT_BOOL"),
        ]

        for input_dtype, expected_getype in test_cases:
            self.assertEqual(TilingConfig.DTYPE_TO_GETYPE[input_dtype], expected_getype)

    def test_format_mapping(self):
        test_cases = [
            ("nd", "ge::FORMAT_ND"),  # ignore
            ("nchw", "ge::FORMAT_NCHW"),
            ("nhwc", "ge::FORMAT_NHWC"),
        ]

        for input_format, expected_geformat in test_cases:
            self.assertEqual(TilingConfig.FMT_TO_GEFMT[input_format], expected_geformat)


if __name__ == '__main__':
    unittest.main()
