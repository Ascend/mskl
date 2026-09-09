# MindStudio Kernel Launcher Installation Guide

<br>

## 1. Installation Notes

This tool is integrated into CANN. If CANN is already installed and you do not need to update this tool, you can use it directly without following the installation steps in this document.

If CANN is not yet installed in your environment, see the [CANN Quick Installation](https://www.hiascend.com/en/cann/download) guide to install the Ascend NPU driver and CANN software (including Toolkit and the ops package), and configure the environment variables.

If you need to upgrade this tool separately or use the latest version, you can install it in the following three ways: [online installation](#21-online-installation), [offline installation](#22-offline-installation), [source installation](#23-source-installation).

## 2. Installation Methods

### 2.1 Online Installation

If your device has internet access, you can automatically download and install the tool with a single command. Visit the MindStudio [download](https://www.hiascend.com/en/developer/software/mindstudio/download) page in the Ascend Community, select the corresponding CANN version, and choose online installation as the installation method. The system will guide you through the subsequent steps.

### 2.2 Offline Installation

For devices in environments without external network access, such as enterprise intranets, first download the complete offline installation package on a machine with internet access, then transfer it to the target device for installation. Refer to the Ascend Community MindStudio [download](https://www.hiascend.com/en/developer/software/mindstudio/download) page, select the corresponding CANN version, choose offline installation as the installation method, and obtain the corresponding installation package and operation guide.

### 2.3 Source Installation

If you need to use features from the latest code or modify the source code to enhance functionality, you can download the code from this repository, compile and package the tool yourself, and complete the installation.

#### 2.3.1 Environment Preparation

Configure the environment according to the following document: [Operator Tool Development Environment Setup Guide](https://gitcode.com/Ascend/msot/blob/master/docs/en/common/dev_env_setup.md).

#### 2.3.2 Building the Wheel Package

- Clone this repository.

    ```sh
    git clone https://gitcode.com/Ascend/mskl.git
    ```

- Build the package.

    ```sh
    cd mskl
    python3 build.py
    ```

- Build output: `./output/mindstudio_kl-xxxxx.whl`

#### 2.3.3 Installing the Wheel Package

```sh
cd output
pip3 install mindstudio_kl-xxxxx.whl
```

When the output information contains the following, it indicates that the software package has been installed successfully.

```text
Successfully install mindstudio-kl-xxx
```

## 3. Installation Verification

After installation, run the following command to verify whether the tool was installed successfully:

```shell
python3 -c "import mskl; print('All is OK')"
```

 If no error is reported and the output displays `All is OK`, the installation is successful.

## 4. Uninstallation

You can uninstall it by following these steps:

1. Download the script.

   ```bash
   curl -O https://inst.obs.cn-north-4.myhuaweicloud.com/26.1.0/ms_install.py
   ```

   > [!NOTE]
   >
   > - An internet connection is required for downloading. If the environment does not allow internet access or is offline, download the script in an environment with internet access first, and then copy it to the target device.
   > - If the command does not respond or errors such as connection failure or SSL certificate issues occur, see [FAQ](https://www.hiascend.com/developer/blog/details/02176213671719317003).
   > - The version number 26.0.0 may change as the software evolves. Replace it with the actual version number when you use the command.

2. Execute the uninstallation.

   ```bash
   python ms_install.py uninstall {tools_name}
   ```

   Where `{tools_name}` is configured as the name of the tool to be uninstalled. You can query it using the `python ms_install.py help` command, and the tool name will be displayed under the Available Tools field in the printed information.

   The following information is printed upon successful uninstallation:

   ```text
   Successfully uninstalled 1 tool ({tools_name})
   ```

## 5. Upgrade

Upgrading means "uninstall first, then install". Directly execute the installation command, and the tool will automatically uninstall the old version and guide you through the overwrite installation.

You can use the `pip3 show mindstudio-kl` command to view the version information in the current environment and then select the version to upgrade to. When upgrading, pay attention to the version compatibility. For details, see the [Version Description](https://gitcode.com/Ascend/release-management/blob/master/MindStudio/master/release_notes_en.md).
