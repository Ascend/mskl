# MindStudio Kernel Launcher 安装指南

<br>

## 1. 安装说明

msKL工具的安装方式包括：

- 使用CANN包安装：msKL工具完整功能已集成在CANN包中，请参考《[CANN 快速安装](https://www.hiascend.com/cann/download)》安装昇腾NPU驱动和CANN软件（包含Toolkit和ops包），并配置环境变量。
- 源码编译安装：如需使用最新代码的功能，或对源码进行修改以增强功能，可下载本仓库代码，自行编译、打包工具并完成安装，具体请参见[源码编译安装](#2-源码编译安装)。

## 2. 源码编译安装

如需使用最新代码的功能，或对源码进行修改以增强功能，可下载本仓库代码，自行编译、打包工具并完成安装。

### 2.1 环境准备

请按照以下文档进行环境配置：《[算子工具开发环境安装指导](https://gitcode.com/Ascend/msot/blob/master/docs/zh/common/dev_env_setup.md)》。

### 2.2 打包whl包

- 克隆本仓库

    ```sh
    git clone https://gitcode.com/Ascend/mskl.git
    ```

- 构建打包

    ```sh
    cd mskl
    python3 build.py
    ```

- 构建输出：./output/mindstudio_kl-xxxxx.whl

### 2.3 安装whl包

```sh
cd output
pip3 install mindstudio_kl-xxxxx.whl
```

### 2.4 升级

如需使用whl包替换运行环境原有已安装的whl包，执行如下安装操作：

```sh
pip3 install mindstudio_kl-xxxxx.whl --force-reinstall
```

### 2.5 卸载

卸载则通过如下命令卸载：

```sh
pip3 uninstall mindstudio-kl
```
