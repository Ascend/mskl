# MindStudio Kernel Launcher 开发指南

<br>

## 1. 代码仓架构

在开始开发之前，建议先阅读 [《msKL 代码仓架构说明》](./architecture.md)，了解项目的目录结构、核心子系统（算子调用/自动调优）、模块依赖关系和数据流。

## 2. 开发环境准备

请按照以下文档进行环境配置：[《算子工具开发环境安装指导》](https://gitcode.com/Ascend/msot/blob/master/docs/zh/common/dev_env_setup.md)。

## 3. 编译打包

### 3.1 编译命令

在项目根目录下执行以下命令进行 mskl 编译：

```shell
python build.py
```

### 3.2 编译结果说明

编译结果生成到 output 目录下：

```text
output/
|-- mindstudio_kl-26.0.0-py3-none-any.whl  # 安装包
```

### 3.3 清理/重新编译

重新执行[第 3.1 节](#31-编译命令)即可，编译结果安装包会自动刷新。

## 4. 执行 UT 测试

在项目根目录下执行以下命令执行 UT 用例：

```shell
python build.py test
```

如果输出类似如下，且运行的用例数和通过用例数相同，即表示成功：

```text
[----------] 59 tests from CoreApi (8ms total) 
```

```text
========== 59 passed in 2.05s ==========
```
