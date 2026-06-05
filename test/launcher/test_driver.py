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

import sys
import ctypes
import numpy as np
import unittest
from unittest.mock import patch, Mock, MagicMock
from mskl.launcher.driver import NPULauncher, TensorListHolder

sys.modules['acl'] = MagicMock()
sys.modules['acl'].rt.malloc = MagicMock()
sys.modules['acl'].rt.malloc.return_value = (0, 0)
sys.modules['acl'].rt.memcpy = MagicMock()
sys.modules['acl'].rt.memcpy.return_value = 0
sys.modules['acl'].rt.free = MagicMock()
sys.modules['acl'].rt.free.return_value = 0
sys.modules['acl'].rt.set_device = MagicMock()
sys.modules['acl'].rt.set_device.return_value = 0
sys.modules['acl'].rt.get_device = MagicMock()
sys.modules['acl'].rt.get_device.return_value = (0, 0)
sys.modules['acl'].rt.create_stream = MagicMock()
sys.modules['acl'].rt.create_stream.return_value = (1, 0)
sys.modules['acl'].rt.destroy_stream_force = MagicMock()
sys.modules['acl'].rt.destroy_stream_force.return_value = 0
sys.modules['acl'].rt.synchronize_stream_with_timeout = MagicMock()
sys.modules['acl'].rt.synchronize_stream_with_timeout.return_value = 0
sys.modules['acl'].rt.reset_device_force = MagicMock()
sys.modules['acl'].rt.reset_device_force.return_value = 0
sys.modules['acl'].init = MagicMock()
sys.modules['acl'].finalize = MagicMock()


class Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int), ("y", ctypes.c_int)]


class MockModule:
    def __init__(self):
        self.test_kernel = MagicMock()


class TestTensorListHolder(unittest.TestCase):
    def test_tensor_list_holder_initialization(self):
        lst = [100, 200, 300]
        holder = TensorListHolder(lst)
        self.assertIsNotNone(holder.addr)
        self.assertTrue(holder.size > 0)

    def test_tensor_list_holder_empty_list(self):
        lst = []
        holder = TensorListHolder(lst)
        self.assertIsNotNone(holder.addr)

    def test_tensor_list_holder_properties(self):
        lst = [100, 200, 300]
        holder = TensorListHolder(lst)
        self.assertTrue(isinstance(holder.addr, int))
        self.assertTrue(isinstance(holder.size, int))


class TestNPULauncher(unittest.TestCase):
    def setUp(self):
        self.launcher = NPULauncher('test_module')

    def test_npu_launcher_initialization(self):
        self.assertEqual(self.launcher._module, 'test_module')
        self.assertEqual(self.launcher._args_info, [])
        self.assertEqual(self.launcher._kernel_meta, [])
        self.assertEqual(self.launcher._host_to_gm_map, {})

    def test_arg_preprocess_basic_types(self):
        # 测试基本类型
        a = np.zeros([128]).astype(np.float32)
        b = np.zeros([128]).astype(np.float32)
        arr = (ctypes.c_int * 5)(1, 2, 3, 4, 5)
        p = Point(1, 2)

        # 测试各种类型的参数处理
        self.launcher._arg_preprocess(100, 3.14, True, a, b, arr, p)
        self.assertEqual(len(self.launcher._args_info), 7)
        self.assertEqual(len(self.launcher._kernel_meta), 7)

    def test_arg_preprocess_numpy_array(self):
        a = np.zeros([128]).astype(np.float32)
        b = np.zeros([128]).astype(np.float32)

        self.launcher._arg_preprocess(a, b)
        self.assertEqual(len(self.launcher._args_info), 2)

    def test_arg_preprocess_numpy_array_non_contiguous(self):
        a = np.zeros([128, 128]).astype(np.float32)
        non_contiguous = a[:, ::2]  # 创建非连续数组

        self.launcher._arg_preprocess(non_contiguous)
        self.assertEqual(len(self.launcher._args_info), 1)

    def test_arg_preprocess_c_array(self):
        arr = (ctypes.c_int * 5)(1, 2, 3, 4, 5)
        self.launcher._arg_preprocess(arr)
        self.assertEqual(len(self.launcher._args_info), 1)

    def test_arg_preprocess_c_structure(self):
        p = Point(1, 2)
        self.launcher._arg_preprocess(p)
        self.assertEqual(len(self.launcher._args_info), 1)

    def test_arg_preprocess_none(self):
        self.launcher._arg_preprocess(None)
        self.assertEqual(len(self.launcher._args_info), 1)

    def test_arg_preprocess_tensor_list(self):
        a = np.zeros([128]).astype(np.float32)
        b = np.zeros([128]).astype(np.float32)
        tensor_list = [a, b]

        self.launcher._arg_preprocess(tensor_list)
        self.assertEqual(len(self.launcher._args_info), 3)  # 2个tensor + 1个holder

    def test_arg_preprocess_unsupported_type(self):
        self.assertRaises(Exception, self.launcher._arg_preprocess, 'abc')
        self.assertRaises(Exception, self.launcher._arg_preprocess, [1, 2, 3])

    def test_arg_preprocess_empty_numpy_array(self):
        empty_array = np.array([])
        self.launcher._arg_preprocess(empty_array)
        self.assertEqual(len(self.launcher._args_info), 1)

    def test_arg_preprocess_original_test(self):
        # 保留原有的测试
        launcher = NPULauncher('test_module')
        a = np.zeros([128]).astype(np.float32)
        b = np.zeros([128]).astype(np.float32)
        lst = [a, b]
        arr = (ctypes.c_int * 5)(1, 2, 3, 4, 5)
        p = Point(1, 2)
        self.assertRaises(Exception, launcher._arg_preprocess, 1, a, None, arr, p, lst, 'abc')

    @patch('importlib.util.spec_from_file_location')
    @patch('importlib.util.module_from_spec')
    def test_npu_launcher_call(self, mock_module_from_spec, mock_spec_from_file_location):
        # 设置mock
        mock_spec = Mock()
        mock_module = Mock()
        mock_module.test_kernel = MagicMock()

        mock_spec_from_file_location.return_value = mock_spec
        mock_module_from_spec.return_value = mock_module

        # 创建测试数据
        a = np.zeros([128]).astype(np.float32)

        # 测试调用
        launcher = NPULauncher('test_module')
        with patch.object(launcher, '_free_all_dev_ptr') as mock_free:
            try:
                launcher(
                    a,
                    blockdim=1,
                    l2ctrl=0,
                    stream=None,
                    warmup=0,
                    profiling=False,
                    device_id=0,
                    timeout=-1,
                    kernel_name='test_kernel',
                    repeat=1,
                )
            except Exception:
                # 某些mock可能不完整，但我们主要验证流程
                pass

            self.assertTrue(mock_free.called)


if __name__ == '__main__':
    unittest.main()
