# Permission Error When Running Kernel

## Problem Symptom

The following error occurs when running the Kernel:

```text
raise PermissionError(f'Path {path} cannot have write permission of group.')
PermissionError: Path /any_path/_gen_module.so cannot have write permission of group.
```

## Root Cause

The default permissions for files created by the current user are too permissive (with group write permission).

## Solution

First, use the `umask -S` command to query the permission configuration, then use the `umask 0022` command to adjust the permission configuration.

```sh
$ umask -S
$ umask 0022
u=rwx,g=rx,o=rx
```
