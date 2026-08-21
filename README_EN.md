<h1 align="center">MindStudio Kernel Launcher</h1>

<div align="center">
<p><b><span style="font-size:24px;">A Lightweight Tool for Invoking Ascend AI Operators</span></b></p>

 [![License](https://badgen.net/badge/快速入门/QuickStart/blue)](docs/en/quick_start/mskl_quick_start.md)
 [![License](https://badgen.net/badge/精确搜索/ReadTheDocs/blue)](https://mindstudio-operator-tools-docs.readthedocs.io/zh-cn/latest/)
 [![License](https://badgen.net/badge/AI问答/DeepWiki/blue)](https://deepwiki.com/mindstudio-docs/master)
 [![License](https://badgen.net/badge/AI问答/ZRead/blue)](https://zread.ai/mindstudio-docs/master)
 [![License](https://badgen.net/badge/昇腾社区/Community/blue)](https://www.hiascend.com/cn/developer/software/mindstudio)
 [![License](https://badgen.net/badge/报告问题/Issues/blue)](https://gitcode.com/Ascend/mskl/issues)

</div>

English | [简体中文](README.md)

## ✨ Latest News

<span style="font-size:14px;">

🔹 **[Dec 31, 2025]**: The MindStudio Kernel Launcher project is now fully open source

</span>

## ℹ️ Overview

MindStudio Kernel Launcher (msKL) provides lightweight kernel invocation capabilities. Using the msKL tool, you can leverage the provided APIs to quickly generate kernel launch code, compile, and run kernels within Python scripts.

## ⚙️ Feature Introduction

msKL provides the ability to invoke msOpGen Operator Projects and perform automatic tuning based on the Ascend C template library. The specific features are described as follows:

| Feature Name | Feature Description  |
|---------|--------|
| **msOpGen operator project invocation** | Provides the `tiling_func` and `get_kernel_from_binary` interfaces, allowing direct invocation of msOpGen Operator Projects. |
| **Automatic tuning** | Provides the capability to generate, compile, and run Kernel launch code from the template library, supporting in-kernel code replacement and automatic tuning. |

## 🚀 Quick Start

To quickly experience the core features using a simple addition operator as an example, see [msKL Quick Start](./docs/en/quick_start/mskl_quick_start.md).

## 📦 Installation Guide

Introduces the environmental dependencies and installation methods of the tool. See [msKL Installation Guide](docs/en/install_guide/mskl_install_guide.md).

## 📘 User Guide

For detailed usage of the tool, see [msKL User Guide](docs/en/user_guide/mskl_user_guide.md)

## 📚 API Reference

See [msKL External API Reference](docs/en/api_reference/mskl_api_reference.md).

## ❓ FAQ

For common issues and solutions, see [msKL FAQ](docs/en/support/faq.md).

## 🌌 Intelligent Search

To improve document retrieval efficiency, we provide multiple efficient search methods:

- **[Precise Search (ReadTheDocs)](https://mindstudio-operator-tools-docs.readthedocs.io/zh-cn/latest/)**: Provides millisecond-level structured search across the entire documentation, enabling precise access to underlying configuration and API details.
- **[AI-Powered Q&A (DeepWiki)](https://deepwiki.com/mindstudio-docs/master)**: Provides a context-aware AI R&D assistant that answers questions in natural language within seconds.

## 🛠️ Contribution Guide

Contributions are welcome. See [Contribution Guide](./docs/en/contributing/contributing_guide.md).

## ⚖️ Related Notes

🔹 [Release Notes](https://gitcode.com/Ascend/mskl/releases)  
🔹 [License Notice](./docs/en/legal/license_notice.md)  
🔹 [Security Statement](./docs/en/legal/security_statement.md)  
🔹 [Disclaimer](./docs/en/legal/disclaimer.md)

## 🤝 Suggestions and Communication

We welcome everyone to contribute to the community. If you have any questions or suggestions, please submit an [Issue](https://gitcode.com/Ascend/mskl/issues), and we will respond as soon as possible. Thank you for your support.

| Instant Interaction (WeChat Group) | Official Information (Official Account) | In-Depth Support (Assistant/Forum) |
|:------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| <img src="https://raw.gitcode.com/Ascend/docs/files/master/common/Writing_Template/figures/qr_code_wechat_work.png" width="120"><br><sub>*Scan to join the technical group*</sub> | <img src="https://raw.gitcode.com/Ascend/docs/files/master/common/Writing_Template/figures/qr_code_wechat_official_account.png" width="120"><br><sub>*Scan to follow the official account*</sub> | Scan the QR code to join the group and follow the official account, connecting directly with MindStudio users and developers through the most convenient communication platform:<br> **Ask questions quickly:** Discuss technical issues with community members in real time.<br>**Stay up to date:** Receive notifications about version releases and feature updates as soon as they are available.<br> **Share experience:** Exchange best practices and hands-on experience with developers.  <br> <br> **More support channels**: 👉 Ascend Assistant: [![WeChat](https://img.shields.io/badge/WeChat-07C160?style=flat-square&logo=wechat&logoColor=white)](https://gitcode.com/Ascend/msit/blob/master/docs/zh/figures/readme/xiaozhushou.png) 👉 Ascend Forum: [![Website](https://img.shields.io/badge/Website-%231e37ff?style=flat-square&logo=RSS&logoColor=white)](https://www.hiascend.com/forum/) |

## 🙏 Acknowledgments

This tool is jointly contributed by the following departments of Huawei:  
🔹 Ascend Computing MindStudio Development Department  
🔹 Ascend Computing Ecosystem Enablement Department  
🔹 Huawei Cloud Ascend Cloud Service  
🔹 2012 Compiler Lab  
🔹 2012 Markov Lab  
Thanks for every PR from the community, contributions are welcome.
