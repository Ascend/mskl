# MindStudio Kernel Launch 常见问题

## 安装类

### 安装 whl 包时提示找不到文件

**问题现象**

执行 `pip3 install mindstudio_kl-xxxxx.whl` 时报错：

```text
ERROR: mindstudio_kl-xxxxx.whl is not a valid wheel filename
```

或

```text
ERROR: Could not find a version that satisfies the requirement mindstudio_kl
```

**原因分析**

- 情况一：未进入 `output` 目录，或 whl 文件名与实际不符。
- 情况二：pip 版本过低，不支持当前 whl 包格式。

**解决方案**

1. 确认已进入 `output` 目录，使用 `ls` 查看实际 whl 文件名：

    ```shell
    cd mskl/output
    ls *.whl
    ```

2. 使用实际文件名安装：

    ```shell
    pip3 install mindstudio_kl-26.0.0-py3-none-any.whl
    ```

3. 若 pip 版本过低，先升级 pip：

    ```shell
    pip3 install --upgrade pip
    ```

### 在线安装时提示网络连接失败

**问题现象**

在线安装或使用 `curl -O` 下载卸载脚本时出现：

```text
curl: (7) Failed to connect to ... port 443: Connection refused
```

**原因分析**

设备处于内网环境或防火墙阻止了对外部网络的访问。

**解决方案**

1. 改用离线安装方式：在可联网的机器上下载离线安装包，再传输至目标设备。请参见昇腾社区 MindStudio [下载](https://www.hiascend.com/developer/software/mindstudio/download) 页面，选择对应的 CANN 版本和"离线安装"。
2. 若仅需下载卸载脚本，可在可联网环境下载后拷贝到目标设备执行。

---

## 环境类

### import mskl 时报 ModuleNotFoundError

**问题现象**

```text
>>> import mskl
ModuleNotFoundError: No module named 'mskl'
```

**原因分析**

msKL 未安装或安装的 Python 环境与当前使用的 Python 不一致。

**解决方案**

1. 确认 msKL 已安装：

    ```shell
    pip3 list | grep mindstudio
    ```

2. 若无输出，请参照[安装指南](../install_guide/mskl_install_guide.md)重新安装。

3. 若已安装但仍报错，检查当前 Python 路径与安装时的 pip 是否对应：

    ```shell
    which python3
    which pip3
    ```

    确保两者在同一环境下（如都在虚拟环境或系统 Python 中）。

### 运行环境预检时提示 Python 包版本不满足

**问题现象**

执行环境预检命令后未输出 `All is OK`，而是抛出 `AssertionError` 或 `ModuleNotFoundError`：

```text
ModuleNotFoundError: No module named 'packaging'
```

或

```text
AssertionError
```

**原因分析**

缺少必要的 Python 依赖包，或依赖包版本不符合要求。

**解决方案**

1. 安装缺失的依赖包：

    ```shell
    pip3 install numpy sympy scipy attrs psutil decorator packaging
    ```

2. 注意 numpy 版本需 ≤ 1.26.4，若版本过高需降级：

    ```shell
    pip3 install 'numpy<=1.26.4'
    ```

3. 重新执行环境预检命令确认通过。

---

## 运行类

### 运行 Kernel 时提示权限错误

**问题现象**

运行 Kernel 时出现以下报错：

```text
raise PermissionError(f'Path {path} cannot have write permission of group.')
PermissionError: Path /any_path/_gen_module.so cannot have write permission of group.
```

**原因分析**

当前用户创建的文件的默认权限过大（具有 group 写权限）。

**解决方案**

先使用 `umask -S` 命令查询权限配置，再使用 `umask 0022` 命令调整权限配置。

```sh
$ umask -S
$ umask 0022
u=rwx,g=rx,o=rx
```

### 调用算子时提示设备异常或卡住不动

**问题现象**

执行 `python3 mskl_demo.py` 后进程卡住，很长时间无输出，或报错：

```text
[ERROR] device 0 is not available
```

**原因分析**

- 默认使用的 NPU 卡（device_id=0）可能被其他进程占用或状态异常。
- 算子未成功部署到 CANN 环境中。

**解决方案**

1. 确认算子已成功部署到 CANN：

    ```shell
    find $ASCEND_HOME_PATH -name "*AddCustom*"
    ```

2. 尝试更换 NPU 卡 ID，修改脚本中的 `NPU_ID` 或 `device_id` 参数：

    ```python
    NPU_ID = 1  # 尝试其他可用卡
    ```

3. 查看 NPU 卡状态：

    ```shell
    npu-smi info
    ```

    确认目标卡状态正常且未被其他任务占用。

### tiling_func 调用报错：找不到 tiling 函数

**问题现象**

```text
[ERROR] Failed to find tiling function for op_type: xxx
```

**原因分析**

- `op_type` 参数填写错误，与实际算子类型不匹配。
- `lib_path` 指定的 liboptiling.so 路径不正确或文件不存在。
- 算子未在 CANN 环境中正确部署。

**解决方案**

1. 确认 `op_type` 参数与 tiling 函数实现中的算子类型完全一致（大小写敏感）：

    ```python
    tiling_output = mskl.tiling_func(
        op_type="AddCustom",  # 需与实现中完全一致
        ...
    )
    ```

2. 使用 `find` 命令确认 liboptiling.so 文件存在：

    ```shell
    find . -name 'liboptiling.so'
    ```

3. 若算子曾经部署过且修改了 tiling 函数，需要在 CANN 环境中重新部署算子。

### get_kernel_from_binary 找不到 .o 文件

**问题现象**

```text
[ERROR] Kernel binary file not found: xxx.o
```

**原因分析**

- 指定的 `.o` 文件路径不正确。
- 编译产物 `.o` 文件名因硬件或操作系统不同而存在差异。

**解决方案**

1. 使用 `find` 命令查找实际的 `.o` 文件：

    ```shell
    find $ASCEND_HOME_PATH -name "*.o" | grep -i addcustom
    ```

2. 将查询到的绝对路径填入 `KERNEL_BINARY_PATH` 变量。

3. 若使用 `kernel_type` 参数，确保设置为正确的类型（`vec`、`cube` 或 `mix`）：

    ```python
    kernel = mskl.get_kernel_from_binary(KERNEL_BINARY_PATH, kernel_type='vec')
    ```

---

## 调优类

### 自动调优运行很慢，如何处理？

**问题现象**

执行 `autotune` 或 `autotune_v2` 时，整个搜索过程耗时过长。

**原因分析**

- `configs` 搜索空间过大，参数组合数量太多。
- `warmup` 预热时间或 `repeat` 重放次数设置过高。
- 设备上有其他任务在并行运行。

**解决方案**

1. 缩小搜索空间：先使用 3~5 组参数组合进行粗调，找到较优范围后再加密搜索：

    ```python
    @mskl.autotune(configs=[
        {'L1TileShape': 'GemmShape<64, 128, 256>', 'L0TileShape': 'GemmShape<64, 128, 64>'},
        {'L1TileShape': 'GemmShape<128, 128, 256>', 'L0TileShape': 'GemmShape<128, 128, 64>'},
        {'L1TileShape': 'GemmShape<128, 256, 256>', 'L0TileShape': 'GemmShape<128, 256, 64>'},
    ], warmup=500, repeat=3, device_ids=[0])
    ```

2. 降低 `warmup`（默认 300μs）和 `repeat`（默认 1）的值。

3. 确保单 Device 上仅运行一个 msKL 自动调优任务，不与其他算子程序并行。

4. 设置 debug 日志级别查看详细耗时分布：

    ```shell
    export MSKL_LOG_LEVEL=0
    ```

### 自动调优结果中所有参数组合耗时相近，无法选出最优

**问题现象**

autotune 输出的各组参数耗时几乎相同，`Best config` 与其余组合差距极小。

**原因分析**

搜索空间中的参数变化范围太小，或者性能瓶颈不在当前调优的参数上。

**解决方案**

1. 扩大搜索空间的参数变化范围，尝试更极端的取值。
2. 确认当前调优的参数确实是性能瓶颈所在（可通过 Profiling 工具辅助定位）。
3. 增加 `warmup` 预热时间使性能数据更稳定：

    ```python
    @mskl.autotune(configs=[...], warmup=2000, repeat=5)
    ```

### 自动调优过程中报编译错误

**问题现象**

```text
[ERROR] Compilation failed for config: {...}
```

**原因分析**

某些参数组合导致生成的代码无法编译通过（如模板参数取值不合理）。

**解决方案**

1. 检查报错的 `config` 组合中的参数值是否合法（如数值是否在硬件允许范围内）。
2. `autotune` 接口会自动跳过编译失败的组合并继续尝试其余组合，不影响整体流程。可从输出中剔除导致编译失败的 config 条目。
3. 参照文档中「参数替换原则」确认标记方式正确（`// tunable` vs `// tunable: 别名`）。

---

## 编译类

### 执行 build.py 编译失败

**问题现象**

```text
$ python3 build.py
[ERROR] build failed: ...
```

**原因分析**

- 缺少编译依赖（如编译器、CANN 开发包未安装）。
- Python 版本不满足要求（需 ≥ 3.7.5）。

**解决方案**

1. 确认 Python 版本：

    ```shell
    python3 --version
    ```

2. 参照《[算子工具开发环境安装指导](https://gitcode.com/Ascend/msot/blob/master/docs/zh/common/dev_env_setup.md)》完成完整的环境配置。

3. 确认 CANN 环境变量已正确设置：

    ```shell
    source $ASCEND_HOME_PATH/set_env.sh
    ```

### 编译生成的 .o 文件名与文档示例不一致

**问题现象**

编译完成后，生成的 `.o` 文件名称与文档示例中的不同，脚本报错找不到文件。

**原因分析**

不同的硬件平台和操作系统生成的 `.o` 文件名称可能存在差异（文件名中包含硬件架构标识等信息）。

**解决方案**

使用 `find` 命令查找实际生成的文件名，然后将实际路径填入脚本：

```shell
find . -name "*.o"
```

将查询到的实际文件名替换脚本中的 `KERNEL_BINARY_PATH` 值即可。文档示例中的文件名仅供参考。

---

## 兼容性类

### CANN 版本与 msKL 版本不匹配

**问题现象**

运行时出现类似以下报错：

```text
ImportError: libascend_hal.so: cannot open shared object file
```

或

```text
[ERROR] ASCEND_HOME_PATH is invalid
```

**原因分析**

- 安装的 CANN 版本与 msKL 版本不兼容。
- 环境变量 `ASCEND_HOME_PATH` 指向了错误或不存在路径。

**解决方案**

1. 确认当前 CANN 版本：

    ```shell
    cat $ASCEND_HOME_PATH/version.cfg
    ```

2. 对照[版本说明](../release_notes/release_notes.md)中的配套关系表，确认 CANN 版本与 msKL 版本匹配：
    - msKL 26.0.0 推荐 CANN 9.0.0 及以上
    - msKL 8.3.0 要求 CANN 8.2.RC1 及以上

3. 若版本不匹配，请升级 CANN 或降级 msKL 版本。

4. 确认环境变量正确：

    ```shell
    echo $ASCEND_HOME_PATH
    ls $ASCEND_HOME_PATH/set_env.sh
    ```

5. 重新加载环境变量后重试：

    ```shell
    source $ASCEND_HOME_PATH/set_env.sh
    ```
