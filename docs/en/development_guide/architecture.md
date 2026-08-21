# msKL Repository Architecture

## 1. Project Overview

MindStudio Kernel Launcher (msKL) is a lightweight tool for operator kernel invocation and automatic tuning on Ascend AI processors. The project is implemented in Python and distributed as a wheel package named `mindstudio-kl`, with the top-level module named `mskl`.

## 2. Directory Structure Overview

```text
mskl/
├── build.py                    # Build/test entry script
├── setup.py                    # Wheel package build configuration
├── requirement.txt             # Python dependency list
├── MANIFEST.in                 # Packaging manifest
├── LICENSE                     # Mulan Permissive Software License v2
├── README.md / README_EN.md    # Project description (Chinese/English)
│
├── mskl/                       # ===== Main package =====
│   ├── __init__.py             # Top-level entry point, exports all public APIs
│   │
│   ├── launcher/               # ----- Operator invocation subsystem -----
│   │   ├── __init__.py         # Exports KernelInvokeConfig / Launcher / compile / tiling_func, and so on
│   │   ├── config.py           # Configuration classes: KernelInvokeConfig / TilingConfig / KernelBinaryInvokeConfig
│   │   ├── code_generator.py   # C++ dispatch code generator: Launcher class
│   │   ├── compiler.py         # Compiler: CompiledKernel / CompiledExecutable / compile / compile_executable
│   │   ├── context.py          # Global context: cross-module state management
│   │   ├── driver.py           # NPU driver layer: NPULauncher / TensorListHolder / device interaction
│   │   ├── opgen_workflow.py   # msOpGen workflow: tiling_func / get_kernel_from_binary / TilingOutput
│   │   ├── dtype_convert.py    # [Reserved] Data type conversion
│   │   └── dump_parser.py      # [Reserved] Dump data parsing
│   │
│   ├── optune/                 # ----- Automatic tuning subsystem -----
│   │   ├── __init__.py         # Exports the autotune / autotune_v2 decorators
│   │   ├── tuner.py            # Tuning engine: Autotuner class (prelaunch → parameter replacement → compilation → performance collection → comparison)
│   │   ├── kernel_modifier.py  # Code modifier: Replacer class (replaces // tunable markers)
│   │   └── kernel_prof.py      # Performance collector: Monitor class (msPTI-based kernel execution time monitoring)
│   │
│   └── utils/                  # ----- Common utilities -----
│       ├── __init__.py         # Empty
│       ├── autotune_utils.py   # Autotuning helpers: parameter validation, tensor type detection, file I/O, JSON parsing
│       ├── const_variables.py  # [Reserved] Constant definitions
│       ├── launcher_utils.py   # Launch utilities: CANN path retrieval, runtime capability detection
│       ├── logger.py           # Logging module
│       └── safe_check.py       # Safety check: FileChecker (file permission/size/owner validation)
│
├── test/                       # ===== Tests =====
│   ├── conftest.py             # pytest global configuration (fixtures, hooks)
│   ├── pytest.ini              # pytest configuration file
│   ├── launcher/               # Invocation subsystem tests
│   │   ├── test_code_generator.py  # C++ code generation tests
│   │   ├── test_compiler.py        # Compiler tests
│   │   ├── test_config.py          # Configuration class tests
│   │   ├── test_driver.py          # NPU driver layer tests
│   │   └── test_opgen_workflow.py  # msOpGen workflow tests
│   ├── op_tune/                # Automatic tuning tests
│   │   ├── test_autotune.py        # autotune decorator tests
│   │   ├── test_autotune_utils.py  # Tuning utility function tests
│   │   ├── test_kernel_modifier.py # Code replacer tests
│   │   └── test_kernel_prof.py     # Performance collector tests
│   └── utils/                  # Utility module tests
│       ├── test_base.py            # Basic test utilities
│       ├── test_logger.py          # Logging module tests
│       └── test_safe_check.py      # Safety check tests
│
├── pre-commit/                 # ===== Code standards =====
│   ├── pyproject.toml          # pre-commit configuration
│   └── typos.toml              # Typo check configuration
│
└── docs/                       # ===== Documentation =====
    ├── zh/                     # Chinese documentation
    └── en/                     # English documentation
```

## 3. Core Subsystem Details

### 3.1 Operator Invocation Subsystem (`mskl/launcher/`)

This subsystem provides the most basic operator kernel invocation capability of msKL.

**Data Flow:**

```text
User Python script
    │
    ├─ tiling_func(op_type, inputs, ...)
    │    ├─ [config.py] TilingConfig parses the parameters
    │    ├─ [code_generator.py] Launcher.code_gen() → generates C++ tiling invocation code
    │    ├─ [compiler.py] compile_tiling() → compiles to .so
    │    └─ [opgen_workflow.py] TilingOutput → returns blockdim / workspace / tiling_data
    │
    └─ get_kernel_from_binary(kernel.o)
         ├─ [config.py] KernelBinaryInvokeConfig
         ├─ [code_generator.py] Launcher.code_gen() → generates C++ kernel dispatch code
         ├─ [compiler.py] compile_kernel_binary() → compiles to .so → CompiledKernel
         ├─ [driver.py] NPULauncher → loads the .so and invokes NPU execution
         └─ returns a CompiledKernel instance
```

**Core Classes and Functions:**

| Component | File | Responsibility |
|------|------|------|
| TilingConfig | config.py | Parses all input parameters of `tiling_func` and generates the structured configuration required by C++. |
| KernelInvokeConfig | config.py | Encapsulates the kernel source file path and function name. |
| Launcher | code_generator.py | Converts Python configuration into C++ dispatch code (the `code_gen` method). |
| CompiledKernel | compiler.py | The compiled kernel object, supporting invocation as `kernel[blockdim](args)` |
| CompiledExecutable | compiler.py | The compiled executable object (for application-level tuning scenarios) |
| NPULauncher | driver.py | Loads the `.so` at runtime and executes the kernel on the NPU. |
| Context | context.py | Global context that maintains state such as `tiling_output`/`op_type`/`kernel_args` |
| TilingOutput | opgen_workflow.py | Wrapper for the return value of `tiling_func` |

### 3.2 Automatic Tuning Subsystem (`mskl/optune/`)

Building on the invocation subsystem, it provides automated parameter search and performance comparison capabilities.

**Data Flow:**

```text
User function decorated with @mskl.autotune(configs=[...])
    │
    ├─ [tuner.py] Autotuner.pre_launch() → prelaunches once and captures the kernel context
    │
    ├─ Iterate over each parameter group in configs:
    │    ├─ [kernel_modifier.py] Replacer.replace_src_with_config()
    │    │    └─ Find the // tunable marker → replace the parameter → write to a temporary .cpp file
    │    ├─ [compiler.py] compile() → compiles the modified code
    │    ├─ [kernel_prof.py] Monitor.start() → starts msPTI monitoring
    │    ├─ [tuner.py] Autotuner.launch() → executes the kernel + warmup
    │    ├─ [kernel_prof.py] Monitor.stop() → retrieves the elapsed time
    │    └─ Record the elapsed time and the parameter group
    │
    └─ Output the elapsed time comparison for all groups and the optimal group
```

**Core Classes and Functions:**

| Component | File | Responsibility |
|------|------|------|
| autotune | tuner.py | Kernel-level tuning decorator that uses the `CompiledKernel` mode |
| autotune_v2 | tuner.py | Application-level tuning decorator that uses the `CompiledExecutable` mode |
| Replacer | kernel_modifier.py | C++ source parameter replacement engine that supports both the `// tunable` and `// tunable: alias` markers |
| Monitor | kernel_prof.py | msPTI-based collector of kernel execution time |

### 3.3 Common Utility Module (`mskl/utils/`)

It provides common capabilities for the upper-layer modules.

| Component | File | Responsibility |
|------|------|------|
| Parameter validation | autotune_utils.py | Checks the validity of parameters such as `configs`/`warmup`/`repeat`/`device_ids`. |
| Tensor utilities | autotune_utils.py | Tensor type detection and conversion via `is_torch_or_numpy_tensor`/`canonical_tensor` |
| File I/O | autotune_utils.py | File read/write helpers such as `get_file_lines`/`load_json` |
| CANN path | launcher_utils.py | `get_cann_path()` retrieves the CANN installation path from environment variables. |
| Runtime detection | launcher_utils.py | `check_runtime_impl()` checks whether the NPU runtime supports the V2 interface. |
| Safety check | safe_check.py | `FileChecker` class: security checks on file permissions, owner, size, and symlinks |
| Logging | logger.py | Unified log output |

## 4. Module Dependencies

```text
mskl/__init__.py
    ├── mskl.launcher (operator invocation)
    │       ├── config.py         ← independent
    │       ├── code_generator.py ← config, context, utils
    │       ├── compiler.py       ← config, driver, utils
    │       ├── driver.py         ← code_generator, utils
    │       ├── opgen_workflow.py ← config, code_generator, compiler, context, utils
    │       └── context.py        ← independent
    │
    └── mskl.optune (automatic tuning)
            ├── tuner.py          ← launcher(compiler, code_generator, config, context, driver), utils
            ├── kernel_modifier.py ← utils
            └── kernel_prof.py    ← utils, msPTI (external)

mskl.utils ← independent (commonly depended on by launcher and optune)
```

## 5. External Dependencies

| Dependency | Purpose |
|------|------|
| numpy | Tensor data processing |
| torch (optional) | PyTorch Tensor support |
| msPTI (Ascend) | Kernel performance monitoring (used by `Monitor`) |
| ACL (Ascend) | AscendCL device management |
| CANN (Ascend) | NPU driver and runtime (located via the `ASCEND_HOME_PATH` environment variable) |

## 6. Build and Test

- **Build and package:** Run `python build.py`. `output/mindstudio_kl-{version}-py3-none-any.whl` is generated.
- **Install:** Run `pip3 install output/mindstudio_kl-*.whl`.
- **Run unit tests:** Run `python build.py test`. The full unit test suite is executed with `pytest`.
- **Test framework:** `pytest`, with configuration in `test/pytest.ini`
