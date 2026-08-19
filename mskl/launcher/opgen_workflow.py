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
import numpy as np
from .config import TilingConfig, KernelBinaryInvokeConfig
from .code_generator import Launcher
from .compiler import compile_tiling, compile_kernel_binary, CompiledKernel
from .context import context
from ..utils.safe_check import FileChecker, DATA_DIRECTORY_AUTHORITY
from ..utils.launcher_utils import (
    get_workspace_path,
    search_kernel_binary_files,
    match_kernel_binary_by_op_type,
    match_kernel_binary_by_soc,
    match_kernel_binary_by_json,
    get_device_soc_name,
)
from ..utils import logger

TILING_FUNC_CNT = 0
GET_KERNEL_FROM_BINARY_CNT = 0
TMP_FOLDER = 'mindstudio_mskl_gen'


def init_tmp_folder():
    path = os.path.abspath(TMP_FOLDER)
    if os.path.exists(path):
        checker = FileChecker(path, 'dir')
        if not checker.check_input_file():
            raise PermissionError(f'{path} check permission failed, please delete it first')
    os.makedirs(path, mode=DATA_DIRECTORY_AUTHORITY, exist_ok=True)
    return path


class TilingOutput:
    def __init__(self, tiling_output: dict):
        self.blockdim = tiling_output["blockdim"]
        # for printf
        self.workspace_size = tiling_output["workspace_size"] + 75 * 1024 * 1024
        self.workspace = np.zeros(self.workspace_size).astype(np.uint8)
        self.tiling_data = np.array(tiling_output["tiling_data"], dtype=np.uint8)
        self.tiling_key = tiling_output["tiling_key"]


def _tensor_dtype(t) -> str:
    """获取tensor的dtype字符串（float16/float32等），供kernel .o的json匹配使用。"""
    if t is None:
        return ''
    if isinstance(t, np.ndarray):
        return t.dtype.name
    if hasattr(t, 'dtype'):
        return str(t.dtype).replace('torch.', '')
    return ''


def _build_io_info(inputs, outputs, inputs_info, outputs_info) -> dict:
    """从tiling_func入参提取inputs/outputs的dtype/format/shape信息，用于kernel .o自动匹配。"""

    def _io_of(t, info):
        if info is None:
            info = {}
        dtype = _tensor_dtype(t) or info.get('dtype', '')
        fmt = info.get('format', '') or 'ND'
        shape = list(t.shape) if (t is not None and hasattr(t, 'shape')) else list(info.get('shape', []))
        return {'dtype': dtype, 'format': fmt, 'shape': shape}

    def _flatten(tensors, infos):
        tensors = list(tensors) if tensors else []
        infos = list(infos) if infos else []
        length = max(len(tensors), len(infos))
        res = []
        for i in range(length):
            t = tensors[i] if i < len(tensors) else None
            info = infos[i] if i < len(infos) else None
            if isinstance(t, list) or isinstance(info, list):
                t_list = t if isinstance(t, list) else [None]
                info_list = info if isinstance(info, list) else [info]
                for j in range(max(len(t_list), len(info_list))):
                    res.append(
                        _io_of(t_list[j] if j < len(t_list) else None, info_list[j] if j < len(info_list) else None)
                    )
            else:
                res.append(_io_of(t, info))
        return res

    return {
        'inputs': _flatten(inputs, inputs_info),
        'outputs': _flatten(outputs, outputs_info),
    }


def tiling_func(
    op_type: str,
    inputs: list = None,
    outputs: list = None,
    lib_path: str = None,
    inputs_info: list = None,
    outputs_info: list = None,
    attr=None,
    soc_version: str = None,
    workspace: str = None,
) -> TilingOutput:
    """
    :param op_type: op type, e.g. AddCustom
    :param inputs: tensors of kernel inputs
    :param outputs: tensors of kernel outputs
    :param lib_path: optional, path of liboptiling.so. If not set, it will be searched recursively in
                     the <workspace> directory (the package under _CPack_Packages/op_tiling is preferred)
    :param inputs_info: info of kernel inputs
    :param outputs_info: info of kernel outputs
    :param attr: attrs of the op
    :param soc_version: soc version
    :param workspace: optional, root directory of the op project, default is current directory.
                      Used to search liboptiling.so and kernel .o automatically
    :return: TilingOutput
    """
    global TILING_FUNC_CNT
    TILING_FUNC_CNT += 1
    workspace = get_workspace_path(workspace)
    context.workspace = workspace
    context.io_info = _build_io_info(inputs, outputs, inputs_info, outputs_info)
    config = TilingConfig(op_type, inputs, outputs, lib_path, inputs_info, outputs_info, attr, soc_version, workspace)
    tmp_path = init_tmp_folder()
    cpp_path = os.path.join(tmp_path, f'_mskl_gen_tiling.{TILING_FUNC_CNT}.cpp')
    Launcher(config).code_gen(cpp_path)
    so_path = os.path.join(tmp_path, f'_mskl_gen_tiling.{TILING_FUNC_CNT}.so')
    run_tiling_func = compile_tiling(cpp_path, so_path)
    tiling_output = run_tiling_func()
    if tiling_output is None:
        raise Exception('Call tiling_func failed')
    output = TilingOutput(tiling_output)
    context.tiling_output = output
    context.op_type = config.op_type
    logger.debug(f'Call tiling_func {TILING_FUNC_CNT} success, op_type is {op_type}')
    return output


def _auto_search_kernel_binary() -> str:
    """根据tiling_func传入的workspace自动搜索kernel .o文件。
    选取顺序：算子名(op_type) -> 设备soc目录 -> 同目录json(dtype/format/shape)。
    """
    workspace = context.workspace if context.workspace is not None else os.getcwd()
    o_files = search_kernel_binary_files(workspace)
    if not o_files:
        raise FileNotFoundError(
            f'Cannot find any kernel .o file under {workspace}, please input [kernel_binary_file] or check [workspace]'
        )
    # 1. 按算子名过滤：kernel .o 文件名以 <op_type>_ 开头
    op_type = context.op_type
    if op_type:
        o_files = match_kernel_binary_by_op_type(o_files, op_type)
    if not o_files:
        raise FileNotFoundError(
            f'Cannot find kernel .o matching op_type {op_type} under {workspace}, '
            f'please input [kernel_binary_file] or check [op_type]'
        )
    if len(o_files) == 1:
        return o_files[0]
    # 2. 优先选择与当前设备soc匹配的kernel .o
    soc_files = match_kernel_binary_by_soc(o_files, get_device_soc_name())
    candidates = soc_files if soc_files else o_files
    if len(candidates) == 1:
        return candidates[0]
    # 3. 根据kernel .o同目录json中的inputs/outputs信息（dtype/format/shape）区分
    json_files = match_kernel_binary_by_json(candidates, context.io_info)
    if len(json_files) == 1:
        return json_files[0]
    if len(json_files) > 1:
        logger.warning(
            f'Multiple kernel .o files match op_type {op_type}, soc and io: '
            f'{json_files}, use the first one {json_files[0]}'
        )
        return json_files[0]
    logger.warning(f'Multiple kernel .o files match op_type {op_type}: {candidates}, use the first one {candidates[0]}')
    return candidates[0]


def get_kernel_from_binary(
    kernel_binary_file: str = None, kernel_type: str = None, tiling_key: int = None
) -> CompiledKernel:
    """
    :param kernel_binary_file: optional, path of kernel.o. If not set, it will be searched recursively in
                               the <workspace> directory and matched by op_type/soc/json
    :param kernel_type: ['mix', 'cube', 'vec']
    :param tiling_key: None will use tiling_func()'s return value
    :return: CompiledKernel
    """
    global GET_KERNEL_FROM_BINARY_CNT
    GET_KERNEL_FROM_BINARY_CNT += 1
    if kernel_binary_file is None:
        if tiling_key is None:
            if context.tiling_output is None:
                raise Exception('Please call mskl.tiling_func or assign [tiling_key]')
            tiling_key = context.tiling_output.tiling_key
        kernel_binary_file = _auto_search_kernel_binary()
        logger.debug(f'Automatically searched kernel binary file is {kernel_binary_file}')
    config = KernelBinaryInvokeConfig(kernel_binary_file, kernel_type, tiling_key)
    tmp_path = init_tmp_folder()
    context.opgen_tmp_dir_path = tmp_path
    cpp_path = os.path.join(tmp_path, f'_mskl_gen_binary_launch.{GET_KERNEL_FROM_BINARY_CNT}.cpp')
    Launcher(config).code_gen(cpp_path)
    so_path = os.path.join(tmp_path, f'_mskl_gen_binary_module.{GET_KERNEL_FROM_BINARY_CNT}.so')
    kernel = compile_kernel_binary(cpp_path, so_path)
    logger.debug(
        f'Call get_kernel_from_binary {GET_KERNEL_FROM_BINARY_CNT} success, kernel path is {kernel_binary_file}'
    )
    return kernel
