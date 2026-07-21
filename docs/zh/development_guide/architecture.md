# msKL 代码仓架构说明

## 1. 项目概述

MindStudio Kernel Launcher（msKL）是一个面向昇腾AI处理器的算子Kernel轻量化调用与自动调优工具。项目采用 Python 实现，以 whl 包形式发布，包名为 `mindstudio-kl`，顶层模块名为 `mskl`。

## 2. 目录结构总览

```text
mskl/
├── build.py                    # 构建/测试入口脚本
├── setup.py                    # whl 包打包配置
├── requirement.txt             # Python 依赖清单
├── MANIFEST.in                 # 打包清单
├── LICENSE                     # 木兰宽松许可证 v2
├── README.md / README_EN.md    # 项目说明（中/英）
│
├── mskl/                       # ===== 主包 =====
│   ├── __init__.py             # 顶层入口，导出全部公开 API
│   │
│   ├── launcher/               # ----- 算子调用子系统 -----
│   │   ├── __init__.py         # 导出 KernelInvokeConfig / Launcher / compile / tiling_func 等
│   │   ├── config.py           # 配置类：KernelInvokeConfig / TilingConfig / KernelBinaryInvokeConfig
│   │   ├── code_generator.py   # C++ 下发代码生成器：Launcher 类
│   │   ├── compiler.py         # 编译器：CompiledKernel / CompiledExecutable / compile / compile_executable
│   │   ├── context.py          # 全局上下文：跨模块状态维护
│   │   ├── driver.py           # NPU 驱动层：NPULauncher / TensorListHolder / 设备交互
│   │   ├── opgen_workflow.py   # msOpGen 工作流：tiling_func / get_kernel_from_binary / TilingOutput
│   │   ├── dtype_convert.py    # [预留] 数据类型转换
│   │   └── dump_parser.py      # [预留] dump 数据解析
│   │
│   ├── optune/                 # ----- 自动调优子系统 -----
│   │   ├── __init__.py         # 导出 autotune / autotune_v2 装饰器
│   │   ├── tuner.py            # 调优引擎：Autotuner 类（预启动→参数替换→编译→性能采集→对比）
│   │   ├── kernel_modifier.py  # 代码修改器：Replacer 类（// tunable 标记替换）
│   │   └── kernel_prof.py      # 性能采集器：Monitor 类（基于 MSPTI 的 Kernel 耗时监控）
│   │
│   └── utils/                  # ----- 公共工具 -----
│       ├── __init__.py         # 空
│       ├── autotune_utils.py   # 自动调优辅助：参数校验、tensor 类型判断、文件 I/O、JSON 解析
│       ├── const_variables.py  # [预留] 常量定义
│       ├── launcher_utils.py   # 启动工具：CANN 路径获取、runtime 能力检测
│       ├── logger.py           # 日志模块
│       └── safe_check.py       # 安全检查：FileChecker（文件权限/大小/属主校验）
│
├── test/                       # ===== 测试 =====
│   ├── conftest.py             # pytest 全局配置（fixtures、hooks）
│   ├── pytest.ini              # pytest 配置文件
│   ├── launcher/               # 调用子系统测试
│   │   ├── test_code_generator.py  # C++ 代码生成测试
│   │   ├── test_compiler.py        # 编译器测试
│   │   ├── test_config.py          # 配置类测试
│   │   ├── test_driver.py          # NPU 驱动层测试
│   │   └── test_opgen_workflow.py  # msOpGen 工作流测试
│   ├── op_tune/                # 自动调优测试
│   │   ├── test_autotune.py        # autotune 装饰器测试
│   │   ├── test_autotune_utils.py  # 调优工具函数测试
│   │   ├── test_kernel_modifier.py # 代码替换器测试
│   │   └── test_kernel_prof.py     # 性能采集器测试
│   └── utils/                  # 工具模块测试
│       ├── test_base.py            # 基础测试工具
│       ├── test_logger.py          # 日志模块测试
│       └── test_safe_check.py      # 安全检查测试
│
├── pre-commit/                 # ===== 代码规范 =====
│   ├── pyproject.toml          # pre-commit 配置
│   └── typos.toml              # 拼写检查配置
│
└── docs/                       # ===== 文档 =====
    ├── zh/                     # 中文文档
    └── en/                     # 英文文档
```

## 3. 核心子系统详解

### 3.1 算子调用子系统（`mskl/launcher/`）

对外提供 msKL 最基础的算子 Kernel 调用能力。

**数据流：**

```text
用户 Python 脚本
    │
    ├─ tiling_func(op_type, inputs, ...)
    │    ├─ [config.py] TilingConfig 解析参数
    │    ├─ [code_generator.py] Launcher.code_gen() → 生成 C++ tiling 调用代码
    │    ├─ [compiler.py] compile_tiling() → 编译为 .so
    │    └─ [opgen_workflow.py] TilingOutput → 返回 blockdim / workspace / tiling_data
    │
    └─ get_kernel_from_binary(kernel.o)
         ├─ [config.py] KernelBinaryInvokeConfig
         ├─ [code_generator.py] Launcher.code_gen() → 生成 C++ kernel 下发代码
         ├─ [compiler.py] compile_kernel_binary() → 编译为 .so → CompiledKernel
         ├─ [driver.py] NPULauncher → 加载 .so 并调用 NPU 执行
         └─ 返回 CompiledKernel 实例
```

**核心类/函数：**

| 组件 | 文件 | 职责 |
|------|------|------|
| `TilingConfig` | `config.py` | 解析 tiling_func 的所有入参，生成 C++ 所需的结构化配置 |
| `KernelInvokeConfig` | `config.py` | 封装 kernel 源码文件路径和函数名 |
| `Launcher` | `code_generator.py` | 将 Python 配置转为 C++ 下发代码（code_gen 方法） |
| `CompiledKernel` | `compiler.py` | 编译后的 Kernel 对象，支持 `kernel[blockdim](args)` 调用 |
| `CompiledExecutable` | `compiler.py` | 编译后的可执行程序对象（应用级调优场景） |
| `NPULauncher` | `driver.py` | 运行时加载 .so 并在 NPU 上执行 Kernel |
| `Context` | `context.py` | 全局上下文，维护 tiling_output / op_type / kernel_args 等状态 |
| `TilingOutput` | `opgen_workflow.py` | tiling_func 的返回值封装 |

### 3.2 自动调优子系统（`mskl/optune/`）

在调用子系统基础上，提供自动化的参数搜索和性能对比能力。

**数据流：**

```text
用户 @mskl.autotune(configs=[...]) 装饰的函数
    │
    ├─ [tuner.py] Autotuner.pre_launch() → 预启动一次，捕获 kernel 上下文
    │
    ├─ 遍历 configs 中的每组参数：
    │    ├─ [kernel_modifier.py] Replacer.replace_src_with_config()
    │    │    └─ 查找 // tunable 标记 → 替换参数 → 写入临时 .cpp 文件
    │    ├─ [compiler.py] compile() → 编译修改后的代码
    │    ├─ [kernel_prof.py] Monitor.start() → 启动 MSPTI 监控
    │    ├─ [tuner.py] Autotuner.launch() → 执行 Kernel + warmup
    │    ├─ [kernel_prof.py] Monitor.stop() → 获取耗时
    │    └─ 记录耗时和参数组合
    │
    └─ 输出所有组合的耗时对比和最优组合
```

**核心类/函数：**

| 组件 | 文件 | 职责 |
|------|------|------|
| `autotune` | `tuner.py` | Kernel 级调优装饰器，使用 `CompiledKernel` 模式 |
| `autotune_v2` | `tuner.py` | 应用级调优装饰器，使用 `CompiledExecutable` 模式 |
| `Replacer` | `kernel_modifier.py` | C++ 源码参数替换引擎，支持 `// tunable` 和 `// tunable: 别名` 两种标记 |
| `Monitor` | `kernel_prof.py` | 基于 MSPTI 的 Kernel 执行时间采集器 |

### 3.3 公共工具模块（`mskl/utils/`）

为上层模块提供通用能力。

| 组件 | 文件 | 职责 |
|------|------|------|
| 参数校验 | `autotune_utils.py` | configs / warmup / repeat / device_ids 等参数合法性检查 |
| Tensor 工具 | `autotune_utils.py` | `is_torch_or_numpy_tensor` / `canonical_tensor` 等 tensor 类型判断和转换 |
| 文件 I/O | `autotune_utils.py` | `get_file_lines` / `load_json` 等文件读写辅助 |
| CANN 路径 | `launcher_utils.py` | `get_cann_path()` 从环境变量获取 CANN 安装路径 |
| Runtime 检测 | `launcher_utils.py` | `check_runtime_impl()` 检测 NPU runtime 是否支持 V2 接口 |
| 安全检查 | `safe_check.py` | `FileChecker` 类：文件权限/属主/大小/软链接等安全检查 |
| 日志 | `logger.py` | 统一日志输出 |

## 4. 模块依赖关系

```text
mskl/__init__.py
    ├── mskl.launcher (算子调用)
    │       ├── config.py         ← 独立
    │       ├── code_generator.py ← config, context, utils
    │       ├── compiler.py       ← config, driver, utils
    │       ├── driver.py         ← code_generator, utils
    │       ├── opgen_workflow.py ← config, code_generator, compiler, context, utils
    │       └── context.py        ← 独立
    │
    └── mskl.optune (自动调优)
            ├── tuner.py          ← launcher(compiler, code_generator, config, context, driver), utils
            ├── kernel_modifier.py ← utils
            └── kernel_prof.py    ← utils, mspti (外部)

mskl.utils ← 独立（被 launcher 和 optune 共同依赖）
```

## 5. 外部依赖

| 依赖 | 用途 |
|------|------|
| `numpy` | Tensor 数据处理 |
| `torch`（可选） | PyTorch Tensor 支持 |
| `mspti`（昇腾） | Kernel 性能监控（`Monitor` 使用） |
| `acl`（昇腾） | AscendCL 设备管理 |
| `CANN`（昇腾） | NPU 驱动和运行时（通过 `ASCEND_HOME_PATH` 环境变量定位） |

## 6. 构建与测试

- **编译打包：** `python build.py` → 生成 `output/mindstudio_kl-{version}-py3-none-any.whl`
- **安装：** `pip3 install output/mindstudio_kl-*.whl`
- **运行 UT 测试：** `python build.py test` → 使用 pytest 执行全量单测
- **测试框架：** pytest，配置见 `test/pytest.ini`
