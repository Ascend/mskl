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

import json
import os
from mskl.utils import logger
from mskl.utils.safe_check import FileChecker

TILING_SO_NAME = 'liboptiling.so'
KERNEL_DIR_NAME = 'kernel'
# 递归搜索workspace时跳过的目录，避免遍历无关内容
_SKIP_DIRS = {'.git', '__pycache__', 'node_modules', '.venv', 'third_party'}


def get_workspace_path(workspace: str = None) -> str:
    """将workspace参数归一化为绝对路径，未指定时使用当前目录。"""
    if workspace is None:
        workspace = os.getcwd()
    if not isinstance(workspace, str) or not workspace:
        raise ValueError('workspace should be a non-empty str')
    workspace = os.path.abspath(workspace)
    checker = FileChecker(workspace, "dir")
    if not checker.check_input_file():
        if not os.path.exists(workspace):
            raise FileNotFoundError(f'workspace {workspace} not exist, please verify path')
        raise PermissionError(f'workspace {workspace} check permission failed, please verify path and permissions')
    return workspace


def search_tiling_so(workspace: str = None):
    """在整个workspace目录下递归搜索 liboptiling.so。
    存在多个时，优先选择打包产物（路径含 _CPack_Packages 或 op_tiling）中的文件。
    """
    workspace = get_workspace_path(workspace)
    found = []
    for dirpath, dirnames, filenames in os.walk(workspace):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for name in filenames:
            if name == TILING_SO_NAME:
                found.append(os.path.join(dirpath, name))
    if not found:
        return None
    for path in found:
        parts = os.path.normpath(path).split(os.sep)
        if '_CPack_Packages' in parts or 'op_tiling' in parts:
            return path
    return found[0]


def search_kernel_binary_files(workspace: str = None):
    """在整个workspace目录下递归搜索路径含 kernel 目录的 *.o 文件。"""
    workspace = get_workspace_path(workspace)
    o_files = []
    for dirpath, dirnames, filenames in os.walk(workspace):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        if KERNEL_DIR_NAME not in dirpath.split(os.sep):
            continue
        for name in filenames:
            if name.endswith('.o'):
                o_files.append(os.path.join(dirpath, name))
    return o_files


def match_kernel_binary_by_op_type(o_files, op_type: str):
    """从kernel .o文件中，根据算子名称（文件名以 <op_type>_ 开头）筛选出匹配的文件。"""
    if not op_type:
        return o_files
    prefix = op_type + '_'
    return [o_file for o_file in o_files if os.path.basename(o_file).startswith(prefix)]


def get_device_soc_name() -> str:
    """获取当前设备soc名称（如 Ascend950PR_9579），获取失败时返回空串。"""
    cann_path = get_cann_path()
    try:
        import ctypes

        acl = ctypes.CDLL(os.path.join(cann_path, 'lib64/libascendcl.so'), mode=ctypes.RTLD_GLOBAL)
        acl.aclrtGetSocName.restype = ctypes.c_char_p
        name = acl.aclrtGetSocName()
        if name:
            return name.decode()
    except Exception as e:  # 获取失败时回退到rtGetSocVersion
        logger.debug(f'Get soc name by aclrtGetSocName failed: {e}')
    try:
        import ctypes

        rt = ctypes.CDLL(os.path.join(cann_path, 'lib64/libruntime.so'), mode=ctypes.RTLD_GLOBAL)
        rt.rtGetSocVersion.argtypes = [ctypes.c_char_p, ctypes.c_uint64]
        rt.rtGetSocVersion.restype = ctypes.c_int
        buf = ctypes.create_string_buffer(64)
        if rt.rtGetSocVersion(buf, 64) == 0 and buf.value:
            return buf.value.decode()
    except Exception as e:  # 获取失败时返回空串，后续回退到默认匹配
        logger.debug(f'Get soc version by rtGetSocVersion failed: {e}')
    return ''


def _get_soc_dir(o_file: str) -> str:
    """从kernel .o路径中提取soc目录名，路径形如 .../kernel/<soc>/<op>/<file>.o。"""
    parts = os.path.normpath(o_file).split(os.sep)
    try:
        idx = parts.index(KERNEL_DIR_NAME)
        if idx + 1 < len(parts):
            return parts[idx + 1].lower()
    except ValueError:
        pass
    return ''


def match_kernel_binary_by_soc(o_files, soc_name: str):
    """按设备soc（如 Ascend950PR_9579）筛选kernel .o，优先匹配路径中soc目录与设备soc一致的。"""
    if not soc_name:
        return []
    soc_lower = soc_name.lower()
    matched = []
    for o_file in o_files:
        soc_dir = _get_soc_dir(o_file)
        # ascend950 匹配 Ascend950PR_9579 / ascend950pr；ascend910b 匹配 Ascend910B3 等
        if soc_dir and (soc_lower.startswith(soc_dir) or soc_dir.startswith(soc_lower)):
            matched.append(o_file)
    return matched


def _normalize_dtype(dtype: str) -> str:
    """归一化dtype名称，兼容 float/float32、half/float16 等别名。"""
    if not dtype:
        return ''
    aliases = {
        'half': 'float16',
        'float': 'float32',
        'fp16': 'float16',
        'fp32': 'float32',
        'fp64': 'float64',
        'double': 'float64',
        'int': 'int32',
    }
    d = str(dtype).lower()
    return aliases.get(d, d)


def _match_json_dtype(json_dtype: str, actual_dtype: str) -> bool:
    if not json_dtype or not actual_dtype:
        return True  # 信息缺失时不作为排除条件
    return _normalize_dtype(json_dtype) == _normalize_dtype(actual_dtype)


def _match_json_format(json_format: str, actual_format: str, match_mode: str = '') -> bool:
    if not json_format or not actual_format:
        return True
    if 'agnostic' in str(match_mode).lower():
        return True  # FormatAgnostic：任意format均可
    return str(json_format).lower() == str(actual_format).lower()


def _match_json_shape(json_shape, actual_shape) -> bool:
    if not json_shape:
        return True
    # 全部为负值（如 [-2]）表示动态shape，匹配任意shape
    if all(dim < 0 for dim in json_shape):
        return True
    if len(json_shape) != len(actual_shape):
        return False
    for json_dim, actual_dim in zip(json_shape, actual_shape):
        if json_dim < 0:  # 单个维度为负值表示该维度动态
            continue
        if json_dim != actual_dim:
            return False
    return True


def _json_supports_io(meta: dict, io_info: dict) -> bool:
    """判断kernel meta json中记录的inputs/outputs是否与本次调用的io信息匹配。"""
    support = meta.get('supportInfo', {})
    for io_key, actual_list in (('inputs', io_info.get('inputs', [])), ('outputs', io_info.get('outputs', []))):
        json_list = support.get(io_key, [])
        if len(actual_list) > len(json_list):
            return False
        for idx, actual in enumerate(actual_list):
            spec = json_list[idx] or {}
            if not _match_json_dtype(spec.get('dtype', ''), actual.get('dtype', '')):
                return False
            if not _match_json_format(
                spec.get('format', ''), actual.get('format', ''), spec.get('format_match_mode', '')
            ):
                return False
            if not _match_json_shape(spec.get('shape'), actual.get('shape', [])):
                return False
    return True


def match_kernel_binary_by_json(o_files, io_info: dict):
    """根据kernel .o同目录json中的inputs/outputs信息（dtype/format/shape）筛选kernel .o。"""
    if not o_files or not io_info:
        return []
    matched = []
    for o_file in o_files:
        json_path = o_file[:-1] + 'json'  # .o -> .json
        if not os.path.exists(json_path):
            continue
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
        except Exception as e:  # json解析失败时跳过该候选
            logger.warning(f'Read kernel meta json {json_path} failed, skip it. error: {e}')
            continue
        if _json_supports_io(meta, io_info):
            matched.append(o_file)
    return matched


def get_cann_path() -> str:
    cann_path = os.getenv('ASCEND_HOME_PATH')
    if cann_path is None or not os.path.isdir(cann_path):
        raise Exception('ASCEND_HOME_PATH is invalid, please check your environment variables')
    checker = FileChecker(cann_path, "dir")
    if not checker.check_input_file():
        raise Exception(
            f'ASCEND_HOME_PATH {cann_path} permission check failed, please verify path ownership and permissions.'
        )
    return cann_path


def check_runtime_impl():
    cann_path = get_cann_path()
    if os.path.exists(os.path.join(cann_path, "lib64/libruntime.so")):
        import ctypes

        runtime_lib = ctypes.CDLL(os.path.join(cann_path, "lib64/libruntime.so"), mode=ctypes.RTLD_GLOBAL)
        if hasattr(runtime_lib, "rtKernelLaunchWithHandleV2") and callable(
            getattr(runtime_lib, "rtKernelLaunchWithHandleV2")
        ):
            return True
    return False
