#!/bin/bash

# -------------------------------------------------------------------------
# This file is part of the MindStudio project.
# Copyright (c) 2026 Huawei Technologies Co.,Ltd.
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

# 代码行覆盖率统计脚本。
#
# 用法:
#   bash test/generate_coverage.sh
#
# 环境变量:
#   COVERAGE_THRESHOLD  行覆盖率门限（百分比），默认 80。
#
# 产物（build_ut/coverage 目录）:
#   coverage_report.txt  文本覆盖率报告
#   coverage.xml         Cobertura 格式报告
#   report/              HTML 报告
#   report.tar.gz        HTML 报告压缩包

echo "***************Generate Coverage*****************"

CUR_DIR=$(dirname "$(readlink -f "$0")")
TOP_DIR=${CUR_DIR}/..
BUILD_DIR=${TOP_DIR}/build_ut
COVERAGE_PATH=${BUILD_DIR}/coverage
THRESHOLD=${COVERAGE_THRESHOLD:-80}

if ! [[ "${THRESHOLD}" =~ ^[0-9]+$ ]] || [ "${THRESHOLD}" -lt 0 ] || [ "${THRESHOLD}" -gt 100 ]; then
    echo "COVERAGE_THRESHOLD (${THRESHOLD}) must be an integer between 0 and 100."
    exit 1
fi

if [ -d "${COVERAGE_PATH}" ]; then
    rm -rf "${COVERAGE_PATH}"
fi

mkdir -p "${COVERAGE_PATH}"
mkdir -p "${BUILD_DIR}"
cd "${BUILD_DIR}" || exit 1

# 只统计产品代码（mskl 包），不统计测试代码和构建脚本
export PYTHONPATH="${TOP_DIR}${PYTHONPATH:+:${PYTHONPATH}}"
export PYTHONPYCACHEPREFIX="${BUILD_DIR}"

coverage3 erase

coverage3 run --source="${TOP_DIR}/mskl" -m pytest \
    "${TOP_DIR}/test/launcher" \
    "${TOP_DIR}/test/op_tune" \
    --junitxml="${COVERAGE_PATH}/test_detail.xml" \
    -W ignore::DeprecationWarning
TEST_RC=$?

coverage3 report -m | tee "${COVERAGE_PATH}/coverage_report.txt"
coverage3 xml -o "${COVERAGE_PATH}/coverage.xml"
coverage3 html -d "${COVERAGE_PATH}/report"
cp "${COVERAGE_PATH}/test_detail.xml" "${COVERAGE_PATH}/report/" 2>/dev/null

if [ "${TEST_RC}" -ne 0 ]; then
    THRESHOLD_RC=0
    echo "Unit tests failed, skip coverage threshold check."
else
    coverage3 report --fail-under="${THRESHOLD}"
    THRESHOLD_RC=$?
fi

cd "${COVERAGE_PATH}" || exit 1
tar -zcvf report.tar.gz ./report

if [ "${TEST_RC}" -ne 0 ]; then
    exit "${TEST_RC}"
fi

if [ "${THRESHOLD_RC}" -ne 0 ]; then
    echo "Line coverage is below the threshold of ${THRESHOLD}%."
    exit "${THRESHOLD_RC}"
fi

echo "Line coverage check passed (threshold: ${THRESHOLD}%)."
