# MindStudio Kernel Launcher Release Notes

## Version Mapping

### Product Version Information

| Product Name | Product Version | Version Type |
|------|-------|------|
| msKL | 26.0.0 | Beta Version |
| msKL | 8.3.0 | Official Version |

### Related Product Version Mapping

| msKL | CANN Version | Python Version |
|----------|-----------------|----------|
| 26.0.0 | 9.0.0 or later recommended | Python 3.11 or later recommended |
| 8.3.0 | 8.2.RC1 or later | Python 3.11 or later recommended |

## Version Compatibility Notes

No compatibility changes.

## Feature Change Notes

### 26.0.0

No new features.

### 8.3.0

First release, with the following features:

1. Provides the tiling_func and get_kernel_from_binary interfaces, supporting calls to tiling functions in the msOpGen project and user-defined Kernel functions for quick debugging.

2. Provides a series of autotune interfaces, supporting code replacement, compilation, execution, and performance comparison for template library operators, facilitating efficient tuning.
