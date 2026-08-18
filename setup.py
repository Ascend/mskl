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
