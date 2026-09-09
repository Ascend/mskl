# msKL Lightweight Kernel Call Quick Start

<br>

## 1. Overview

Using the msKL tool, you can leverage its provided interfaces to quickly implement code generation, compilation, and execution for Kernel launch within a Python script.
This document demonstrates the core functionality of the msKL tool based on the simple addition operator developed in the introductory tutorial, helping beginners intuitively experience the efficiency and convenience it brings to the operator development process.

This chapter assumes that you have completed the full workflow in the <a href="https://gitcode.com/Ascend/msot/blob/master/docs/en/quick_start/op_tool_quick_start.md" target="_blank">Operator Development Toolchain Quick Start</a>. If you have not yet done so, you are advised to complete the guide first for a better learning experience.

## 2. Procedure

### 2.1 [Environment] Required Environment Preparation (Mandatory Prerequisite ⚠️)

🛑 **This section is a mandatory prerequisite. Skipping it will cause numerous failures in subsequent operations.**
This tutorial **supports only** standardized CANN container environments. It is incompatible with bare-metal, virtual machine, or other non-standard container deployments.

#### 2.1.1 Installing the CANN Container Environment

✅ **Strictly follow the guide below to complete environment installation:**
👉 **<a href="https://gitcode.com/Ascend/msot/blob/master/docs/en/quick_start/installation_guide.md" target="_blank">Ascend AI Operator Development Toolchain Learning Environment Installation Guide</a>**

> ⏱️ **Estimated time with external network access: approximately 3 minutes**
> After installation, you will have a standardized container environment preinstalled with all operator tools, sample code, and dependent libraries.

#### 2.1.2 Running the Environment Self-Check Script (Must Pass!)

Before starting the formal tutorial, **copy the entire script below** and paste it into the terminal to run it. Continue only when every output line displays [PASS]:

```bash
# 1. Container environment check
[ -f /.dockerenv ] && [ -n "$ASCEND_HOME_PATH" ] && [ -n "$ATB_HOME_PATH" ] && echo -e "\033[32m[PASS] CANN 容器环境 OK \033[0m" || echo -e "\033[31m[FAIL] 非标容器或未进入容器！\033[0m"
# 2. Sample code repository check
[ -d ~/ot_demo/msot/example/quick_start ] && echo -e "\033[32m[PASS] 示例代码仓 OK\033[0m" || echo -e "\033[31m[FAIL] 代码仓缺失\033[0m"
```

### 2.2 [Prerequisite] Operator Project Preparation Completed

Follow the instructions in Section 2.3 of <a href="https://gitcode.com/Ascend/msot/blob/master/docs/en/quick_start/op_tool_quick_start.md#23-developing-and-building-the-operator-project-msopgen" target="_blank">Operator Development Toolchain Quick Start</a> to prepare the operator project.

### 2.3 [Lightweight Call] Lightweight Kernel Call in Python Scripts (msKL)

> [!NOTE]
> 
> **Key Point: Introduction to the mskl Interface Invocation Mechanism**
>
> 1. The `mskl.tiling_func` interface
> Through this interface, you can specify the Tiling dynamic library (.so file) and operator type (`op_type`) to precisely invoke the target Tiling function. By passing parameters such as `inputs_shape` and `attr`, you can also flexibly construct a `TilingContext` and invoke Tiling without relying on the ACLNN framework.
> The execution result of the Tiling function includes `blockdim` (number of kernel launches), `workspace` (workspace memory), and serialized `tiling_data` structure data. You can use these results to verify the Tiling logic and as necessary input for subsequent Kernel calls.
> 2. The `mskl.get_kernel_from_binary` interface
> Through this interface, you can specify the Kernel binary file of the operator (.o file) and function signature parameters to quickly load and invoke the Kernel.
> You can directly pass the input/output tensors required by the Kernel as `numpy.array`. After execution, you can immediately read the output tensor contents for precision comparison or functional verification.
> 3. Seamless integration with other operator toolchains
> You only need to launch the mskl Python script directly with a tool command, for example: `mskl python3 mskl_demo.py`.

#### 2.3.1 Developing the Python Script

Run the following command:

```shell
cd ~/ot_demo/workspace/src/AddCustom
vi mskl_demo.py
```

Create the file `mskl_demo.py` with the following content:

```python
import numpy as np
import mskl

# Path to the compiled kernel binary .o file in CANN. Replace with the actual path
KERNEL_BINARY_PATH = "/usr/local/Ascend/cann-8.5.0/opp/vendors/customize/op_impl/ai_core/tbe/kernel/ascend910b/add_custom/AddCustom_ab1b6750d7f510985325b603cb06dc8b.o"

# Path to the tiling library in CANN. Replace with the actual path
TILING_LIB_PATH = "/usr/local/Ascend/cann-8.5.0/opp/vendors/customize/op_impl/ai_core/tbe/op_tiling/liboptiling.so"

# Tensor shapes, data types, NPU card ID
TENSOR_SHAPE = (8, 4096)
TENSOR_DTYPE = np.float16
NPU_ID = 0

def add_custom(a, b, c, workspace, tiling_data):
    kernel = mskl.get_kernel_from_binary(KERNEL_BINARY_PATH)
    return kernel(a, b, c, workspace, tiling_data, device_id=NPU_ID)


def main():
    """Main function: execute the AddCustom operator and verify the result correctness."""

    # 1. Prepare input/output tensors
    a = np.random.randint(1, 5, TENSOR_SHAPE).astype(TENSOR_DTYPE)
    b = np.random.randint(1, 5, TENSOR_SHAPE).astype(TENSOR_DTYPE)
    c = np.zeros(TENSOR_SHAPE, dtype=TENSOR_DTYPE)
    golden = (a + b).astype(TENSOR_DTYPE)

    # 2. Call TilingFunc to obtain tiling strategy and workspace
    tiling_output = mskl.tiling_func(
        op_type="AddCustom",
        inputs=[a, b],
        outputs=[c],
        lib_path=TILING_LIB_PATH,
    )

    # 3. Execute the operator kernel
    add_custom(a, b, c, tiling_output.workspace, tiling_output.tiling_data)

    # 4. Verify the correctness of the result
    result = "success" if np.array_equal(c, golden) else "failed"
    print(f"compare {result}.")


if __name__ == "__main__":
    main()

```

#### 2.3.2 Adapting the Script

> [!NOTE]
> 
> The following commands depend on the `$ASCEND_HOME_PATH` environment variable, which points to the CANN installation path and is usually configured by running `source set_env.sh` after CANN is installed. If it is not set, run `source ${CANN installation path}/set_env.sh` first.

Run the following command, and fill the absolute path of the found .o file into the `KERNEL_BINARY_PATH` variable in `mskl_demo.py`:

```shell
find $ASCEND_HOME_PATH -name *AddCustom*o
```

Run the following command, and fill the absolute path of the found .so file into the `TILING_LIB_PATH` variable in `mskl_demo.py`:

```shell
find $ASCEND_HOME_PATH -path */customize/* -name liboptiling.so
```

#### 2.3.3 Executing the Script and Calling the Operator

> [!CAUTION]
> Call the operator only after it has been successfully deployed to CANN. Otherwise, an error will be reported.

```shell
python3 mskl_demo.py
```

If execution is successful, the output is as follows:

```text
root@ubuntu122:~/ot_demo/workspace/src/AddCustom# python3 mskl_demo.py
[INFO ] Load tiling library /usr/local/Ascend/cann-8.5.0/opp/vendors/customize/op_impl/ai_core/tbe/op_tiling/lib/linux/aarch64/libcust_opmaster_rt2.0.so
[INFO ] Set kernel_type as vec, you can change this value by input [kernel_type] in [mskl.get_kernel_from_binary] manually.
compare success.
```

If execution fails or hangs, the default NPU 0 may be abnormal. Try modifying `NPU_ID` in `mskl_demo.py` to use another available NPU.
