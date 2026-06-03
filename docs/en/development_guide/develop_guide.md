# MindStudio Kernel Launcher Development Guide

<br>

## 1. Development Environment Preparation

Follow the document below to configure the environment: [Operator Tool Development Environment Installation Guide](https://gitcode.com/Ascend/msot/blob/master/docs/en/common/dev_env_setup.md).

## 2. Compilation and Packaging

```shell
python build.py
```

## 3. Executing UT Tests

```shell
python build.py test
```

If the output is similar to the following, and the number of run test cases equals the number of passed test cases, it indicates success:

```text
[----------] 59 tests from CoreApi (8ms total) 
```

```text
========== 59 passed in 2.05s ==========
```
