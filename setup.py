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

import os
from setuptools import setup, find_packages

os.makedirs("output", exist_ok=True)
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='mindstudio-kl',
    version=os.environ.get('WHL_VERSION', '26.0.0'),
    author=' mskl',
    author_email='mskl',
    description='mskl',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitcode.com/Ascend/mskl',
    packages=find_packages(),
    include_package_data=True,
    license='Mulan PSL v2',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    options={
        'bdist_wheel': {
            'dist_dir': 'output',
        }
    },
    python_requires='>=3.6',
)
