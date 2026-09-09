# MindStudio Kernel Launch FAQ

## 1. Installation Issues

### 1.1 File Not Found When Installing the Wheel Package

**Symptom**

Running the `pip3 install mindstudio_kl-xxxxx.whl` command reports the following error:

```text
ERROR: mindstudio_kl-xxxxx.whl is not a valid wheel filename
```

or

```text
ERROR: Could not find a version that satisfies the requirement mindstudio_kl
```

**Cause Analysis**

- Case 1: You did not enter the `output` directory, or the wheel file name does not match the actual file name.
- Case 2: The `pip` version is too old and does not support the current wheel package format.

**Solution**

1. Confirm that you have entered the `output` directory, and use `ls` to check the actual wheel file name:

    ```shell
    cd mskl/output
    ls *.whl
    ```

2. Install the package using the actual file name:

    ```shell
    pip3 install mindstudio_kl-26.0.0-py3-none-any.whl
    ```

3. If the `pip` version is too old, upgrade `pip` first:

    ```shell
    pip3 install --upgrade pip
    ```

### 1.2 Network Connection Failure During Online Installation

**Symptom**

The following error occurs during online installation or when you use `curl -O` to download the uninstall script:

```text
curl: (7) Failed to connect to ... port 443: Connection refused
```

**Cause Analysis**

The device is on an intranet, or the firewall blocks access to external networks.

**Solution**

1. Switch to offline installation: download the offline installation package on a machine with internet access, and then transfer it to the target device. See the MindStudio [Download](https://www.hiascend.com/en/developer/software/mindstudio/download) page on the Ascend community, and select the corresponding CANN version and "Offline Installation".
2. If you only need the uninstall script, download it in an environment with internet access, and then copy it to the target device and run it.

---

## 2. Environment Issues

### 2.1 ModuleNotFoundError When Importing mskl

**Symptom**

```text
>>> import mskl
ModuleNotFoundError: No module named 'mskl'
```

**Cause Analysis**

msKL is not installed, or the Python environment used for installation differs from the one currently in use.

**Solution**

1. Confirm that msKL is installed:

    ```shell
    pip3 list | grep mindstudio
    ```

2. If there is no output, reinstall msKL by following the [installation guide](../install_guide/mskl_install_guide.md).

3. If msKL is installed but the error persists, check whether the current Python path matches the `pip` used during installation:

    ```shell
    which python3
    which pip3
    ```

    Ensure that both are in the same environment (for example, both in a virtual environment or both in the system Python).

### 2.2 Python Package Version Requirement Not Met During Environment Precheck

**Symptom**

After you run the environment precheck command, the output is not `All is OK`. Instead, the command raises an `AssertionError` or `ModuleNotFoundError`:

```text
ModuleNotFoundError: No module named 'packaging'
```

or

```text
AssertionError
```

**Cause Analysis**

Necessary Python dependency packages are missing, or the dependency package versions do not meet the requirements.

**Solution**

1. Install the missing dependency packages:

    ```shell
    pip3 install numpy sympy scipy attrs psutil decorator packaging
    ```

2. Note that the `numpy` version must be ≤ 1.26.4. If the version is too high, downgrade it:

    ```shell
    pip3 install 'numpy<=1.26.4'
    ```

3. Run the environment precheck command again to confirm that it passes.

---

## 3. Runtime Issues

### 3.1 Permission Error When Running a Kernel

**Symptom**

The following error occurs when you run a Kernel:

```text
raise PermissionError(f'Path {path} cannot have write permission of group.')
PermissionError: Path /any_path/_gen_module.so cannot have write permission of group.
```

**Cause Analysis**

The default permissions of files created by the current user are too permissive (they include group write permission).

**Solution**

First use the `umask -S` command to query the permission configuration, and then use the `umask 0022` command to adjust it.

```sh
$ umask -S
$ umask 0022
u=rwx,g=rx,o=rx
```

### 3.2 Device Error or Hang When Calling an Operator

**Symptom**

After you run `python3 mskl_demo.py`, the process hangs with no output for a long time, or it reports the following error:

```text
[ERROR] device 0 is not available
```

**Cause Analysis**

- The NPU used by default (`device_id=0`) may be occupied by another process or be in an abnormal state.
- The operator was not successfully deployed to the CANN environment.

**Solution**

1. Confirm that the operator was successfully deployed to CANN:

    ```shell
    find $ASCEND_HOME_PATH -name "*AddCustom*"
    ```

2. Try changing the NPU ID by modifying the `NPU_ID` or `device_id` parameter in the script:

    ```python
    NPU_ID = 1  # Try another available device
    ```

3. Check the NPU status:

    ```shell
    npu-smi info
    ```

    Confirm that the target device is in a normal state and is not occupied by other tasks.

### 3.3 tiling_func Call Error: Tiling Function Not Found

**Symptom**

```text
[ERROR] Failed to find tiling function for op_type: xxx
```

**Cause Analysis**

- The `op_type` parameter is filled in incorrectly and does not match the actual operator type.
- The path of `liboptiling.so` specified by `lib_path` is incorrect, or the file does not exist.
- The operator is not correctly deployed in the CANN environment.

**Solution**

1. Confirm that the `op_type` parameter exactly matches the operator type in the tiling function implementation (the match is case-sensitive):

    ```python
    tiling_output = mskl.tiling_func(
        op_type="AddCustom",  # Must match the implementation exactly
        ...
    )
    ```

2. Use the `find` command to confirm that the `liboptiling.so` file exists:

    ```shell
    find . -name 'liboptiling.so'
    ```

3. If the operator was previously deployed and you modified the tiling function, redeploy the operator in the CANN environment.

### 3.4 get_kernel_from_binary Cannot Find the .o File

**Symptom**

```text
[ERROR] Kernel binary file not found: xxx.o
```

**Cause Analysis**

- The specified `.o` file path is incorrect.
- The name of the compiled `.o` file differs depending on the hardware or operating system.

**Solution**

1. Use the `find` command to locate the actual `.o` file:

    ```shell
    find $ASCEND_HOME_PATH -name "*.o" | grep -i addcustom
    ```

2. Fill the absolute path you find into the `KERNEL_BINARY_PATH` variable.

3. If you use the `kernel_type` parameter, ensure that you set it to the correct type (`vec`, `cube`, or `mix`):

    ```python
    kernel = mskl.get_kernel_from_binary(KERNEL_BINARY_PATH, kernel_type='vec')
    ```

---

## 4. Tuning Issues

### 4.1 Autotuning Runs Very Slowly. What Should I Do?

**Symptom**

When you run `autotune` or `autotune_v2`, the entire search process takes too long.

**Cause Analysis**

- The `configs` search space is too large, and the number of parameter combinations is too high.
- The `warmup` warm-up time or the `repeat` count is set too high.
- Other tasks are running in parallel on the device.

**Solution**

1. Narrow the search space: first run a coarse tuning with 3 to 5 parameter combinations to find a better range, and then refine the search:

    ```python
    @mskl.autotune(configs=[
        {'L1TileShape': 'GemmShape<64, 128, 256>', 'L0TileShape': 'GemmShape<64, 128, 64>'},
        {'L1TileShape': 'GemmShape<128, 128, 256>', 'L0TileShape': 'GemmShape<128, 128, 64>'},
        {'L1TileShape': 'GemmShape<128, 256, 256>', 'L0TileShape': 'GemmShape<128, 256, 64>'},
    ], warmup=500, repeat=3, device_ids=[0])
    ```

2. Lower the values of `warmup` (default: 300 μs) and `repeat` (default: 1).

3. Ensure that only one msKL autotuning task runs on a single device, and do not run it in parallel with other operator programs.

4. Set the debug log level to view the detailed time consumption distribution:

    ```shell
    export MSKL_LOG_LEVEL=0
    ```

### 4.2 All Parameter Combinations in Autotuning Results Take Similar Time, Making It Impossible to Select the Best

**Symptom**

The time consumption of each parameter group output by autotune is almost identical, and the difference between `Best config` and the other combinations is extremely small.

**Cause Analysis**

The parameter variation range in the search space is too small, or the performance bottleneck does not lie in the parameters currently being tuned.

**Solution**

1. Expand the parameter variation range in the search space and try more extreme values.
2. Confirm that the parameters currently being tuned are indeed the performance bottleneck (you can use the Profiling tool to help locate it).
3. Increase the `warmup` warm-up time to make the performance data more stable:

    ```python
    @mskl.autotune(configs=[...], warmup=2000, repeat=5)
    ```

### 4.3 Compilation Error During Autotuning

**Symptom**

```text
[ERROR] Compilation failed for config: {...}
```

**Cause Analysis**

Some parameter combinations cause the generated code to fail compilation (for example, unreasonable template parameter values).

**Solution**

1. Check whether the parameter values in the `config` combination that reports the error are valid (for example, whether the values fall within the range allowed by the hardware).
2. The `autotune` interface automatically skips combinations that fail to compile and continues trying the remaining combinations, without affecting the overall process. You can remove the `config` entries that cause compilation failures from the output.
3. Refer to the "Parameter Replacement Principle" in the documentation to confirm that the marking method is correct (`// tunable` vs `// tunable: alias`).

---

## 5. Compilation Issues

### 5.1 Compilation Failure When Running build.py

**Symptom**

```text
$ python3 build.py
[ERROR] build failed: ...
```

**Cause Analysis**

- Compilation dependencies are missing (for example, the compiler or the CANN development package is not installed).
- The Python version does not meet the requirements (Python ≥ 3.7.5 is required).

**Solution**

1. Check the Python version:

    ```shell
    python3 --version
    ```

2. Complete the full environment configuration by following the [Operator Tool Development Environment Installation Guide](https://gitcode.com/Ascend/msot/blob/master/docs/en/common/dev_env_setup.md).

3. Confirm that the CANN environment variables are correctly set:

    ```shell
    source $ASCEND_HOME_PATH/set_env.sh
    ```

### 5.2 The Compiled .o File Name Differs from the Documentation Example

**Symptom**

After compilation, the name of the generated `.o` file differs from the example in the documentation, and the script reports an error because it cannot find the file.

**Cause Analysis**

The names of `.o` files generated on different hardware platforms and operating systems may differ (the file name contains information such as the hardware architecture identifier).

**Solution**

Use the `find` command to locate the actual generated file name, and then fill the actual path into the script:

```shell
find . -name "*.o"
```

Replace the `KERNEL_BINARY_PATH` value in the script with the actual file name you find. The file name in the documentation example is for reference only.

---

## 6. Compatibility Issues

### 6.1 CANN Version Does Not Match the msKL Version

**Symptom**

Errors similar to the following occur during runtime:

```text
ImportError: libascend_hal.so: cannot open shared object file
```

or

```text
[ERROR] ASCEND_HOME_PATH is invalid
```

**Cause Analysis**

- The installed CANN version is incompatible with the msKL version.
- The environment variable `ASCEND_HOME_PATH` points to an incorrect or nonexistent path.

**Solution**

1. Check the current CANN version:

    ```shell
    cat $ASCEND_HOME_PATH/version.cfg
    ```

2. Check the compatibility table in the [release notes](../release_notes/release_notes.md) to confirm that the CANN version matches the msKL version:
    - msKL 26.0.0: CANN 9.0.0 or later recommended
    - msKL 8.3.0: CANN 8.2.RC1 or later required

3. If the versions do not match, upgrade CANN or downgrade the msKL version.

4. Confirm that the environment variables are correct:

    ```shell
    echo $ASCEND_HOME_PATH
    ls $ASCEND_HOME_PATH/set_env.sh
    ```

5. Reload the environment variables and try again:

    ```shell
    source $ASCEND_HOME_PATH/set_env.sh
    ```
