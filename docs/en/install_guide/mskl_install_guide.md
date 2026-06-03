# MindStudio Kernel Launcher Installation Guide

## 1. Packaging the whl File

```sh
python3 build.py
```

Build output: ./output/mindstudio_kl-xxxxx.whl

## 2. Installing the whl File

```sh
cd output
pip3 install mindstudio_kl-xxxxx.whl
```

## 3. Upgrade

If you need to replace an existing installed whl package in the runtime environment with a new whl package, perform the following installation operation:

```sh
pip3 install mindstudio_kl-xxxxx.whl --force-reinstall
```

During the installation process, if prompted whether to replace the existing package:
Enter "y", and the installation package will automatically complete the upgrade operation.

## 4. Uninstallation

To uninstall, use the following command:

```sh
pip3 uninstall mindstudio_kl-xxxxx.whl 
```
