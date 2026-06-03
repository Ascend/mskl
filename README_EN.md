<!-- md-trans-meta sourceCommit=unknown translatedAt=2026-05-20T04:13:48.001Z pushedAt=2026-05-20T09:58:07.868Z -->

<h1 align="center">MindStudio Kernel Launcher</h1>

<div align="center">
<h2>A Lightweight Tool for Invoking Ascend AI Operators</h2>

 [![Ascend](https://img.shields.io/badge/Community-MindStudio-blue.svg)](https://www.hiascend.com/developer/software/mindstudio) 
 [![License](https://badgen.net/badge/License/MulanPSL-2.0/blue)](./LICENSE)

</div>

## ✨ Latest News

<span style="font-size:14px;">

🔹 **[2025.12.31]**: The MindStudio Kernel Launcher project is now fully open source

</span>

## ️ ℹ️ Overview

MindStudio Kernel Launcher (msKL) provides lightweight kernel invocation capabilities. Using the msKL tool, you can leverage the provided APIs to quickly generate kernel launch code, compile, and run kernels within Python scripts.

## ⚙️ Feature Introduction

msKL provides the ability to invoke msOpGen Operator Projects and perform automatic tuning based on the Ascend C template library. The specific features are described as follows:

| Feature Name | Feature Description  |
|---------|--------|
| **Invoke msOpGen Operator Project** | Provides the tiling_func and get_kernel_from_binary interfaces, allowing direct invocation of msOpGen Operator Projects. |
| **Automatic Tuning** | Provides the capability to generate, compile, and run Kernel launch code from the template library, supporting in-kernel code replacement and automatic tuning. |

## 🚀 Quick Start

To quickly experience the core features using a simple addition operator as an example, See also [msKL Quick Start](./docs/en/quick_start/mskl_quick_start.md).

## 📦 Installation Guide

Introduces the environmental dependencies and installation methods of the tool. See also [msKL Installation Guide](docs/en/install_guide/mskl_install_guide.md).

## 📘 User Guide

For detailed usage of the tool, See also [msKL User Guide](docs/en/user_guide/mskl_user_guide.md)

## 📚 API Reference

See also [msKL External API Reference](docs/en/api_reference/mskl_api_reference.md).

## ❓ FAQ

For common issues and solutions, See also [msKL FAQ](docs/en/support/faq.md).

## 🛠️ Contribution Guide

Contributions are welcome. See also [Contribution Guide](./docs/en/contributing/contributing_guide.md).

## ⚖️ Related Notes

🔹 [Release Notes](./docs/en/release_notes/release_notes.md)  
🔹 [License Notice](./docs/en/legal/license_notice.md)  
🔹 [Security Statement](./docs/en/legal/security_statement.md)  
🔹 [Disclaimer](./docs/en/legal/disclaimer.md)  

## 🤝 Suggestions and Communication

We welcome everyone to contribute to the community. If you have any questions or suggestions, please submit an [Issue](https://gitcode.com/Ascend/mskl/issues), and we will respond as soon as possible. Thank you for your support.

|                                      📱 Follow MindStudio Official Account                                       | 💬 More Communication and Support                                                                                                                                                                                                                                                                                                                                                                                                                     |
|:-----------------------------------------------------------------------------------------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| <img src="https://gitcode.com/Ascend/msot/blob/master/docs/zh/figures/readme/officialAccount.png" width="120"><br><sub>*Scan to follow for the latest updates*</sub> | 💡 **Join WeChat Group**: <br>Follow the official account and reply "communication group" to get the group QR code.<br><br>🛠️ **Other Channels**: <br>👉 Ascend Assistant: [![WeChat](https://img.shields.io/badge/WeChat-07C160?style=flat-square&logo=wechat&logoColor=white)](https://gitcode.com/Ascend/msot/blob/master/docs/zh/figures/readme/xiaozhushou.png)<br>👉 Ascend Forum: [![Website](https://img.shields.io/badge/Website-%231e37ff?style=flat-square&logo=RSS&logoColor=white)](https://www.hiascend.com/forum/) |

## 🙏 Acknowledgments

This tool is jointly contributed by the following departments of Huawei:  
🔹 Ascend Computing MindStudio Development Department  
🔹 Ascend Computing Ecosystem Enablement Department  
🔹 Huawei Cloud Ascend Cloud Service  
🔹 2012 Compiler Lab  
🔹 2012 Markov Lab  
Thanks for every PR from the community, contributions are welcome.
