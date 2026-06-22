#!/usr/bin/python3
# -*- coding: utf-8 -*-
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
import argparse
import glob
import logging
import os
import shutil
import subprocess
import sys
import traceback
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class BuildManager:
    """
    统一构建管理：依赖拉取 → 编译出包 / 单元测试。

    用法:
        python build.py                  完整构建（拉取依赖 + 打包 whl）
        python build.py local            本地构建（跳过依赖拉取, 打包 whl）
        python build.py test             单元测试（拉取依赖 + 执行 pytest）
        python build.py test local       单元测试（跳过依赖拉取, 执行 pytest）
        python build.py -r <revision>    指定依赖的内部源码仓(例如msopcom)的 Git 分支/标签/commit
        python build.py -v <version>     指定构建版本号，同时覆盖 --build-version 和 --whl-version
        python build.py -e KEY=VALUE     指定额外构建选项，可多次使用

    参数说明:
        - 参数: command : 构建动作: 为空时为全构建, local 为跳过依赖下载, test 为运行单元测试。
        - 参数: -r, --revision : 指定 Git 修订版本或标签用于依赖检出。
        - 参数: -v, --version : 指定构建版本号；若设置，则同时覆盖 --build-version 和 --whl-version 的值。
        - 参数: --build-version, --whl-version : 历史参数，保留用于兼容；设置了 --version 时以 --version 为准。
        - 参数: -e, --extra : 额外构建选项，格式为 KEY=VALUE，可多次指定。

    产物归档:
        产品构建完成后，归档到 artifacts/ 目录中。
    """

    def __init__(self):
        self.project_root = Path(__file__).resolve().parent
        argument_parser = argparse.ArgumentParser(description='Build the project and optionally run tests.')
        argument_parser.add_argument(
            'command',
            nargs='*',
            default=[],
            choices=[[], 'local', 'test'],
            help='Build action: omit for full build, "local" to skip dependency download, "test" to run unit tests',
        )
        argument_parser.add_argument(
            '-r', '--revision', help='Specify Git revision for internal dependent repo (e.g., msopcom).'
        )
        argument_parser.add_argument(
            '--build-version', type=str, default=None, help='Build version for run/exe/dmg packages'
        )
        argument_parser.add_argument(
            '--whl-version', type=str, default=None, help='WHL version for Python wheel packages'
        )
        argument_parser.add_argument(
            '-v',
            '--version',
            type=str,
            default=None,
            help='Build version, overrides --build-version and --whl-version if set',
        )
        argument_parser.add_argument(
            '-e',
            '--extra',
            metavar='KEY=VALUE',
            action='append',
            default=[],
            help='Extra build options in KEY=VALUE format, can be specified multiple times',
        )
        self.parsed_arguments = argument_parser.parse_args()

        if self.parsed_arguments.version is not None:
            self.parsed_arguments.build_version = self.parsed_arguments.version
            self.parsed_arguments.whl_version = self.parsed_arguments.version

    def _execute_command(self, command_sequence, timeout_seconds=36000, cwd=None, env=None):
        logging.info("Running: %s", " ".join(command_sequence))
        subprocess.run(command_sequence, timeout=timeout_seconds, check=True, cwd=cwd, env=env)

    def _run_unit_tests(self):
        unit_test_build_dir = self.project_root / "build_ut"
        unit_test_build_dir.mkdir(mode=0o750, exist_ok=True)
        os.chdir(unit_test_build_dir)

        env = os.environ.copy()
        env['PYTHONPATH'] = str(self.project_root) + os.pathsep + env.get('PYTHONPATH', '')
        env['PYTHONPYCACHEPREFIX'] = str(unit_test_build_dir)

        self._execute_command([sys.executable, "-m", "pip", "install", "numpy"], env=env)

        report_dir = unit_test_build_dir / "report"
        test_cmd = [
            "coverage3",
            "run",
            "--branch",
            "--source=" + str(self.project_root),
            "-m",
            "pytest",
            str(self.project_root / "test" / "launcher"),
            str(self.project_root / "test" / "op_tune"),
            "--junitxml=" + str(report_dir / "final.xml"),
            "-W",
            "ignore::DeprecationWarning",
        ]

        logging.info("============ start to execute Python code UT test ============")
        self._execute_command(test_cmd, env=env)
        self._execute_command(["coverage3", "xml", "-o", str(report_dir / "coverage.xml")], env=env)
        self._execute_command(["coverage3", "html", "-d", str(report_dir)], env=env)
        self._execute_command(["coverage3", "report", "-m"], env=env)

    def _run_product_build(self):
        output_dir = self.project_root / "output"
        output_dir.mkdir(mode=0o750, exist_ok=True)

        self._execute_command(
            [
                sys.executable,
                "setup.py",
                "bdist_wheel",
                "--dist-dir",
                str(output_dir),
            ]
        )

        for whl in glob.glob(str(output_dir / "mskl*.whl")):
            os.chmod(whl, 0o550)

    def _archive_artifacts(self):
        """将产品构建产物（output 目录下的 .whl）归档到工程根目录的 artifacts 目录。"""
        artifact_patterns = ("*.whl",)
        output_dir = self.project_root / "output"
        artifacts_dir = self.project_root / "artifacts"
        artifacts_dir.mkdir(exist_ok=True)

        if not output_dir.exists():
            logging.warning("Output directory not found, skip archiving: %s", output_dir)
            return

        for pattern in artifact_patterns:
            for artifact in output_dir.rglob(pattern):
                destination = artifacts_dir / artifact.name
                logging.info("Archiving artifact: %s -> %s", artifact, destination)
                shutil.copy2(artifact, destination)

    def run(self):
        os.chdir(self.project_root)

        # 将 --whl-version 传入环境变量，供 setup.py 通过 os.environ.get('WHL_VERSION') 读取
        whl_version = self.parsed_arguments.whl_version
        if whl_version:
            os.environ['WHL_VERSION'] = whl_version
            logging.info("WHL_VERSION set to: %s", whl_version)

        build_version = self.parsed_arguments.build_version
        if build_version:
            logging.info("--build-version: %s", build_version)

        for option in self.parsed_arguments.extra:
            key, _, value = option.partition('=')
            logging.info("--extra: %s = %s", key, value)

        if 'test' in self.parsed_arguments.command:
            self._run_unit_tests()
        else:
            self._run_product_build()
            self._archive_artifacts()


if __name__ == "__main__":
    try:
        BuildManager().run()
    except Exception:
        logging.error("Unexpected error: %s", traceback.format_exc())
        sys.exit(1)
