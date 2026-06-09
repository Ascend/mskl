<h1 align="center">MindStudio Kernel Launcher</h1>

<div align="center">
<p><b><span style="font-size:24px;">昇腾 AI 算子轻量化调用工具</span></b></p>

 [![License](https://badgen.net/badge/快速入门/QuickStart/blue)](docs/zh/quick_start/mskl_quick_start.md) 
 [![License](https://badgen.net/badge/精确搜索/ReadTheDocs/blue)](https://mindstudio-operator-tools-docs.readthedocs.io/zh-cn/latest/) 
 [![License](https://badgen.net/badge/AI问答/DeepWiki/blue)](https://deepwiki.com/mindstudio-docs/master) 
 [![License](https://badgen.net/badge/AI问答/ZRead/blue)](https://zread.ai/mindstudio-docs/master) 
 [![License](https://badgen.net/badge/昇腾社区/Community/blue)](https://www.hiascend.com/cn/developer/software/mindstudio) 
 [![License](https://badgen.net/badge/报告问题/Issues/blue)](https://gitcode.com/Ascend/mskl/issues) 

</div>

## ✨ 最新消息

<span style="font-size:14px;">

🔹 **[2025.12.31]**：MindStudio Kernel Launcher 项目全面开源

</span>

## ℹ️ 简介

MindStudio Kernel Launcher（算子调用，msKL）具有Kernel轻量化调用的功能。使用msKL工具可以利用提供的接口在Python脚本中快速实现Kernel下发代码生成、编译及运行Kernel。

## ⚙️ 功能介绍

msKL具有调用msOpGen算子工程和基于Ascend C模板库进行自动调优的功能，具体介绍如下：

| 功能名称 | 功能描述  |
|---------|--------|
| **调用msOpGen算子工程** | 提供tiling_func和get_kernel_from_binary接口，可以直接调用msOpGen算子工程。 |
| **自动调优** | 提供模板库Kernel下发代码生成、编译、运行的能力，支持Kernel内代码替换并自动调优。 |

## 🚀 快速入门

以简易加法算子为例，快速体验核心功能，请参见《[msKL 快速入门](./docs/zh/quick_start/mskl_quick_start.md)》。

## 📦 安装指南

介绍工具的环境依赖与安装方法，请参见《[msKL 安装指南](docs/zh/install_guide/mskl_install_guide.md)》。

## 📘 使用指南

工具的详细使用方法，请参见《[msKL 使用指南](docs/zh/user_guide/mskl_user_guide.md)》。

## 📚 API参考

请参见《[msKL 对外接口使用说明](docs/zh/api_reference/mskl_api_reference.md)》。

## ❓ FAQ

常见问题及解决方案，请参见《[msKL FAQ](docs/zh/support/faq.md)》。

## 🌌 智能检索

为提升文档查阅效率，我们提供多种高效检索方式：

- **[精确搜索（ReadTheDocs）](https://mindstudio-operator-tools-docs.readthedocs.io/zh-cn/latest/)**：全量文档毫秒级结构化检索，精准触达底层配置与 API 细节
- **[AI 智能问答（DeepWiki）](https://deepwiki.com/mindstudio-docs/master)**：基于上下文的 AI 研发助手，自然语言提问，秒级获取答复

## 🛠️ 贡献指南

欢迎参与项目贡献，请参见《[贡献指南](./docs/zh/contributing/contributing_guide.md)》。  

## ⚖️ 相关说明

🔹《[版本说明](./docs/zh/release_notes/release_notes.md)》  
🔹《[许可证声明](./docs/zh/legal/license_notice.md)》  
🔹《[安全声明](./docs/zh/legal/security_statement.md)》  
🔹《[免责声明](./docs/zh/legal/disclaimer.md)》   

## 🤝 建议与交流

欢迎大家为社区做贡献。如果有任何疑问或建议，请提交[Issues](https://gitcode.com/Ascend/mskl/issues)，我们会尽快回复。感谢您的支持。

|                                                                            即时互动（微信群）                                                                             |                                                                                  官方资讯（公众号）                                                                                   | 深度支持（助手/论坛）                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|:------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| <img src="https://raw.gitcode.com/mengguangxin/docs/files/dev_0526/common/Writing_Template/figures/qr_code_wechat_work.png" width="120"><br><sub>*扫码加入技术交流群*</sub> | <img src="https://raw.gitcode.com/mengguangxin/docs/files/dev_0526/common/Writing_Template/figures/qr_code_wechat_official_account.png" width="120"><br><sub>*扫码关注官方公众号*</sub> | 扫码入群并关注公众号，直达 MindStudio 用户与开发者最快捷的交流平台：<br> **快速提问：** 与社区小伙伴即时探讨技术问题<br>**掌握动态：** 第一时间获取版本发布与功能更新通知<br> **经验共享：** 与广大开发者交流最佳实践与实战心得  <br> <br> **更多支持渠道**：👉 昇腾助手：[![WeChat](https://img.shields.io/badge/WeChat-07C160?style=flat-square&logo=wechat&logoColor=white)](https://gitcode.com/Ascend/msit/blob/master/docs/zh/figures/readme/xiaozhushou.png) 👉 昇腾论坛：[![Website](https://img.shields.io/badge/Website-%231e37ff?style=flat-square&logo=RSS&logoColor=white)](https://www.hiascend.com/forum/) |

## 🙏 致谢

本工具由华为公司的下列部门联合贡献：    
🔹 昇腾计算MindStudio开发部  
🔹 昇腾计算生态使能部  
🔹 华为云昇腾云服务  
🔹 2012编译器实验室  
🔹 2012马尔科夫实验室  
感谢来自社区的每一个 PR，欢迎贡献！
