# msKL Lightweight Kernel Call Quick Start

<br>

## 1. Overview

Using the msKL tool, you can leverage its provided interfaces to quickly implement code generation, compilation, and execution for Kernel launch within a Python script.
This document demonstrates the core functionality of the msKL tool based on the simple addition operator developed in the introductory tutorial, helping beginners intuitively experience the efficiency and convenience it brings to the operator development process.

### 1.1 Recommendations

This section assumes you have completed the full workflow of the [Ascend Operator Development Toolchain Quick Start](https://gitcode.com/Ascend/msot/blob/master/docs/en/quick_start/op_tool_quick_start.md). If you have not yet experienced it, it is recommended that you read this guide first for a better learning outcome.

### 1.2 Environment Preparation

Please strictly follow the <a href="https://gitcode.com/Ascend/msot/blob/master/docs/en/common/dev_env_setup.md" target="_blank">Operator Tool Development Environment Setup Guide</a> to complete environment installation and workspace configuration.
Even if you already have a similar environment, you must re-execute the steps in this guide to ensure all dependent components, environment variables, etc., are complete and consistent.

## 2. Procedure

### 2.1 [Environment] Runtime Environment Pre-check

#### 2.1.1 Confirming Python Dependency Packages Are Installed

Run the following command. If the output is "All is OK", it indicates that the required Python packages and their versions meet the specifications:

```shell
python3 -c "import numpy, sympy, scipy, attrs, psutil, decorator; from packaging import version; assert version.parse(numpy.__version__) <= version.parse('1.26.4'); print('All is OK')"
```

If an error is reported, refer to [Section 1.2](#12-environment-preparation) for correct installation.

### 2.2 [Prerequisite] Operator Project Preparation Completed

Follow the instructions in <a href="https://gitcode.com/Ascend/msot/blob/master/docs/en/quick_start/op_tool_quick_start.md" target="_blank">Ascend Operator Development Toolchain Quick Start</a> to complete Sections 2.1 and 2.3.

### 2.3 [Lightweight Call] Lightweight Kernel Call in Python Scripts (msKL)

> [!NOTE]Description
>**Introduction to the msKPP Interface Invocation Mechanism**
> 
> 1. `mskl.tiling_func`
> Through this interface, developers can specify the Tiling dynamic library (.so file) and operator type (op_type) to precisely invoke the target Tiling function. Additionally, by passing parameters such as inputs_shape and attr, they can flexibly construct a TilingContext, enabling lightweight Tiling invocation without relying on the ACLNN framework.
>The execution result of the Tiling function includes blockdim (number of kernel function launches), workspace (workspace memory), and serialized tiling_data structure data, which can be used for Tiling logic verification and also serve as necessary input for subsequent Kernel invocation.
> 2. `mskl.get_kernel_from_binary`
> Through this API, developers can specify the Kernel binary file (.o file) and its function signature parameters to quickly load and invoke the Kernel.
> Input/output tensors required by the Kernel can be directly passed as numpy.array. After execution, the output tensor content can be immediately read for precision comparison or functional verification.   
> 3. Seamless integration with other operator toolchains   
> Developers only need to launch the mskl Python script directly via a tool command, for example: `mskl python3 mskl_demo.py`

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

# Path to the compiled kernel binary .o file in CANN. Replace with the actual path.
KERNEL_BINARY_PATH = "/usr/local/Ascend/cann-8.5.0/opp/vendors/customize/op_impl/ai_core/tbe/kernel/ascend910b/add_custom/AddCustom_ab1b6750d7f510985325b603cb06dc8b.o"

# Path to the tiling library in CANN. Replace with the actual path.
TILING_LIB_PATH = "/usr/local/Ascend/cann-8.5.0/opp/vendors/customize/op_impl/ai_core/tbe/op_tiling/liboptiling.so"

# Tensor shapes, data types, NPU card ID
TENSOR_SHAPE = (8, 4096)
TENSOR_DTYPE = np.float16
NPU_ID = 0

def add_custom(a, b, c, workspace, tiling_data):
    kernel = mskl.get_kernel_from_binary(KERNEL_BINARY_PATH)
    return kernel(a, b, c, workspace, tiling_data, device_id=NPU_ID)


def main():
    """Main function: Execute the AddCustom operator and verify the correctness of the result."""

    # 1. Prepare input/output tensors.
    a = np.random.randint(1, 5, TENSOR_SHAPE).astype(TENSOR_DTYPE)
    b = np.random.randint(1, 5, TENSOR_SHAPE).astype(TENSOR_DTYPE)
    c = np.zeros(TENSOR_SHAPE, dtype=TENSOR_DTYPE)
    golden = (a + b).astype(TENSOR_DTYPE)

    # 2. Call TilingFunc to obtain tiling strategy and workspace.
    tiling_output = mskl.tiling_func(
        op_type="AddCustom",
        inputs=[a, b],
        outputs=[c],
        lib_path=TILING_LIB_PATH,
    )

    # 3. Execute the operator kernel.
    add_custom(a, b, c, tiling_output.workspace, tiling_output.tiling_data)

    # 4. Verify the correctness of the result.
    result = "success" if np.array_equal(c, golden) else "failed"
    print(f"compare {result}.")


if __name__ == "__main__":
    main()

```

#### 2.3.2 Adapting the Script

Run the following command, and fill the absolute path of the found .o file into the `KERNEL_BINARY_PATH` variable in `mskl_demo.py`:

```shell
find $ASCEND_HOME_PATH -name *AddCustom*o
```

Run the following command, and fill the absolute path of the found .so file into the `TILING_LIB_PATH` variable in `mskl_demo.py`:

```shell
find $ASCEND_HOME_PATH -path */customize/* -name liboptiling.so
```

#### 2.3.3 Executing the Script and Calling the Operator
>
>[!CAUTION] Note
>Please ensure the operator has been successfully deployed to CANN before calling it; otherwise, an error will be reported.

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
