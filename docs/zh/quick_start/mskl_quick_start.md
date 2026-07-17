# msKL 算子 Kernel 轻量化调用快速入门

<br>

## 1. 概述

使用 msKL 工具可以利用其提供的接口在 Python 脚本中快速实现 Kernel 下发的代码生成、编译及运行。
本文档基于入门教程中开发的简易加法算子，演示 msKL 工具的核心功能，帮助初学者直观感受其为算子开发过程带来的高效性与便捷性。

本章节以您已完成<a href="https://gitcode.com/Ascend/msot/blob/master/docs/zh/quick_start/op_tool_quick_start.md" target="_blank">《算子开发工具链快速入门》</a>的全流程操作为前提；若尚未体验，建议先完成该指南以获得更佳的学习效果。

## 2. 操作步骤

### 2.1【环境】必备环境准备（强制前置 ⚠️）

🛑 **本节为强制前置步骤！跳过将导致后续操作大量出现失败。**  
本教程**仅支持**标准化 CANN 容器环境，不兼容裸机、虚拟机或其他非标准容器部署。

#### 2.1.1 安装 CANN 容器环境

✅ **请严格按以下指南完成环境安装：**  
👉 **<a href="https://gitcode.com/Ascend/msot/blob/master/docs/zh/quick_start/installation_guide.md" target="_blank">《昇腾 AI 算子开发工具链学习环境安装指南》</a>**

> ⏱️ **外网可达环境下预计耗时：约 3 分钟**  
> 安装完成后，您将获得一个预装所有算子工具、示例代码和依赖库的标准化容器环境。

#### 2.1.2 执行环境自检脚本（必须通过！）

在如下正式体验前，请**全文复制下方整段脚本**，粘贴到终端执行，只有输出全部显示为 [PASS] 才能继续：

```bash
# 1. 容器环境检查
[ -f /.dockerenv ] && [ -n "$ASCEND_HOME_PATH" ] && [ -n "$ATB_HOME_PATH" ] && echo -e "\033[32m[PASS] CANN 容器环境 OK \033[0m" || echo -e "\033[31m[FAIL] 非标容器或未进入容器！\033[0m"
# 2. 示例代码仓检查
[ -d ~/ot_demo/msot/example/quick_start ] && echo -e "\033[32m[PASS] 示例代码仓 OK\033[0m" || echo -e "\033[31m[FAIL] 代码仓缺失\033[0m"
```

### 2.2【前提】算子工程准备完成

按照<a href="https://gitcode.com/Ascend/msot/blob/master/docs/zh/quick_start/op_tool_quick_start.md#23开发构建算子工程msopgen" target="_blank">《算子开发工具链快速入门》</a>中 2.3 节操作，完成算子工程准备。

### 2.3 【轻量调用】Python 脚本中 Kernel 轻量化调用（msKL）

> [!NOTE]   
> **知识点：mskl 接口调用机制简介**   
>
> 1. `mskl.tiling_func` 接口   
>通过此接口，开发者可指定 Tiling 动态库（.so 文件）与算子类型（op_type），精准调用目标 Tiling 函数；同时，通过传入 inputs_shape、attr 等参数，可灵活构造 TilingContext，实现无需依赖 ACLNN 框架的轻量化 Tiling 调用。   
> Tiling 函数的执行结果包含 blockdim（核函数启动数量）、workspace（工作空间内存）以及序列化的 tiling_data 结构体数据，既可用于 Tiling 逻辑验证，也可作为后续 Kernel 调用的必要输入。      
> 2. `mskl.get_kernel_from_binary` 接口   
>通过此接口，开发者可指定算子的 Kernel 二进制文件（.o 文件）及其函数签名参数，实现 Kernel 的快速加载与调用。
> Kernel 所需的输入/输出张量可直接传入 numpy.array，执行完成后，可立即读取输出张量内容，用于精度比对或功能验证。   
> 3. 与其他算子工具链无缝集成   
> 开发者仅需通过工具命令直接启动 mskl Python 脚本即可，例如：`mskl python3 mskl_demo.py`

#### 2.3.1 开发 Python 调用脚本

执行如下命令：

```shell
cd ~/ot_demo/workspace/src/AddCustom
vi mskl_demo.py
```

按如下内容创建文件 `mskl_demo.py`：

```python
import numpy as np
import mskl

# 编译生成的 kernel 二进制.o文件在 CANN 中的路径，请更换为实际路径
KERNEL_BINARY_PATH = "/usr/local/Ascend/cann-8.5.0/opp/vendors/customize/op_impl/ai_core/tbe/kernel/ascend910b/add_custom/AddCustom_ab1b6750d7f510985325b603cb06dc8b.o"

# tiling 库在 CANN 中的路径，请更换为实际路径
TILING_LIB_PATH = "/usr/local/Ascend/cann-8.5.0/opp/vendors/customize/op_impl/ai_core/tbe/op_tiling/liboptiling.so"

# 张量形状、数据类型、NPU卡ID
TENSOR_SHAPE = (8, 4096)
TENSOR_DTYPE = np.float16
NPU_ID = 0

def add_custom(a, b, c, workspace, tiling_data):
    kernel = mskl.get_kernel_from_binary(KERNEL_BINARY_PATH)
    return kernel(a, b, c, workspace, tiling_data, device_id=NPU_ID)


def main():
    """主函数：执行 AddCustom 算子并验证结果正确性。"""

    # 1. 准备输入/输出张量
    a = np.random.randint(1, 5, TENSOR_SHAPE).astype(TENSOR_DTYPE)
    b = np.random.randint(1, 5, TENSOR_SHAPE).astype(TENSOR_DTYPE)
    c = np.zeros(TENSOR_SHAPE, dtype=TENSOR_DTYPE)
    golden = (a + b).astype(TENSOR_DTYPE)

    # 2. 调用 TilingFunc 获取分块策略和工作空间
    tiling_output = mskl.tiling_func(
        op_type="AddCustom",
        inputs=[a, b],
        outputs=[c],
        lib_path=TILING_LIB_PATH,
    )

    # 3. 执行算子 Kernel
    add_custom(a, b, c, tiling_output.workspace, tiling_output.tiling_data)

    # 4. 验证结果正确性
    result = "success" if np.array_equal(c, golden) else "failed"
    print(f"compare {result}.")


if __name__ == "__main__":
    main()

```

#### 2.3.2 对脚本进行适配

> [!NOTE]
> 以下命令依赖 `$ASCEND_HOME_PATH` 环境变量，该变量指向 CANN 安装路径（通常在安装 CANN 后通过 `source set_env.sh` 配置）。若未设置，请先执行 `source ${CANN安装路径}/set_env.sh`。

执行如下命令，将查询到的 .o 文件绝对路径填入`mskl_demo.py`的 `KERNEL_BINARY_PATH` 变量中：

```shell
find $ASCEND_HOME_PATH -name *AddCustom*o
```

执行以下命令，将查询到的 .so 文件绝对路径填入`mskl_demo.py`的 `TILING_LIB_PATH` 变量中：

```shell
find $ASCEND_HOME_PATH -path */customize/* -name liboptiling.so
```

#### 2.3.3 执行脚本，调用算子

> [!CAUTION]    
> 请在成功部署算子到 CANN 后再调用，否则会报错。

```shell
python3 mskl_demo.py
```

如果执行成功，输出如下：

```text
root@ubuntu122:~/ot_demo/workspace/src/AddCustom# python3 mskl_demo.py 
[INFO ] Load tiling library /usr/local/Ascend/cann-8.5.0/opp/vendors/customize/op_impl/ai_core/tbe/op_tiling/lib/linux/aarch64/libcust_opmaster_rt2.0.so
[INFO ] Set kernel_type as vec, you can change this value by input [kernel_type] in [mskl.get_kernel_from_binary] manually.
compare success.
```

如果执行失败或卡住，可能是默认的0卡异常，可以尝试修改`mskl_demo.py`中的`NPU_ID`改用其他可用卡。
