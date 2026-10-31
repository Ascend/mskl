# msKL Development Guide

<br>

This document describes how to set up the development environment for MindStudio Kernel Launcher (msKL), build the project, and run UT unit tests.

## 1. Prerequisites

### 1.1 Prerequisite Knowledge

Before starting development, read [msKL Repository Architecture](./architecture.md) to learn about the code framework and core processes.

### 1.2 Environment Preparation

Follow [msKL Installation Guide — Source Installation](../install_guide/mskl_install_guide.md#231-environment-preparation) to set up the build and test environment.

> **Note:** The environment image build method and the supporting software versions are maintained by the *MindStudio Unified Build Image Creation Guide* and are not redefined in this repository.

## 2. Build

Run the following in the project root directory:

```bash
python3 build.py
```

### 2.1 Build Artifacts

After a successful build, the output is generated in the `artifacts` directory.

### 2.2 Build Cleanup

To perform a full rebuild, delete the build directory and run the preceding steps again:

```bash
rm -rf build
```

## 3. Unit Tests

### 3.1 Running Tests

```bash
python3 build.py test
```

When all tests pass, the output is similar to the following example:

```text
[----------] 59 tests from CoreApi (8ms total)
```

```text
========== 59 passed in 2.05s ==========
```

> **Pass criteria:** The tests pass when the number of cases run matches the number of cases reported as `passed`. If any case is reported as `failed`, locate the cause of the failure from the logs.

### 3.2 Cleaning the Test Environment

Delete the UT build directory and run the tests again:

```bash
rm -rf build_ut
```
