<div align="center">

# Enterprise Legal Ops

面向中小企业内部管理的 AI Agent Skill，把合同、员工、制度、公章证照、章程权限、股东出资、提醒和本地问库组织成可复核、可追踪、可本地化改造的企业法务运营工作流。

兼容 Codex、Claude Code、Qoder、OpenCode、OpenAI Skills 以及其他支持本地 Markdown Skill 的 Agent 平台。

[![Enterprise Legal Ops](https://img.shields.io/badge/Enterprise%20Legal%20Ops-SME%20Legal%20Ops-0F766E)](https://github.com/pa1nrui1/enterprise-legal-ops)
[![Skill](https://img.shields.io/badge/Skill-enterprise--legal--ops-2E7D32)](#skill-列表)
[![Language](https://img.shields.io/badge/Language-%E4%B8%AD%E6%96%87%E4%BC%98%E5%85%88-B91C1C)](#)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

</div>

## 关于项目

**Enterprise Legal Ops** 是一个面向中小企业内部使用的本地法务运营 Skill。它不是律师顾问版，也不输出正式法律意见书，而是帮助企业把分散的合同、员工、制度、公章、证照、章程、授权、股东出资和提醒事项，整理为本地台账、Markdown 记录、来源边界和可追踪提醒。

Agent 在本项目中不会被鼓励直接给出结论，而是被要求按企业内部管理习惯推进：

- 先初始化企业本地工作区，再接收历史资料；
- 先读取文件、生成读取复查摘要，再写入台账或进入严审；
- 涉及合同审查、制度合法性、章程权限、用印、出资逾期等判断时，必须进入严审流程；
- 合同审查唯一交付物是企业内部 Word 修订格式审核稿；
- 飞书只作为可选日历提醒，不用于合同审查交付；
- 所有输出均为企业内部工作文件，不生成律师顾问版、正式法律意见书或律师/律所落款文件。

> **重要提示：本项目不提供法律意见。**
> 本项目输出的任何内容均应视为企业内部管理记录或供人工复核的工作草稿。真实签署、解除、担保、借款、融资、出资、用印或劳动处理事项，应由企业负责人或专业人士基于完整事实、现行规则和具体语境独立判断。

<details open>
<summary>最近更新</summary>

| 日期 | 类型 | 模块 | 更新要点 |
| :--- | :--- | :--- | :--- |
| 2026-06-26 | 新增 | 企业法务运营 | 首次开源 `enterprise-legal-ops` Skill，覆盖合同、HR、公章证照、章程权限、股东出资、本地问库、提醒和飞书日历提醒 |

</details>

## 项目概述

中小企业的日常法务需求，很多时候不是诉讼，而是资料、台账、权限、期限和内部处理流程：

1. 合同分散，找不到原件、版本和到期节点。
2. 员工花名册、劳动合同、年假、制度文件缺少统一记录。
3. 证照、公章、授权文件、用印事项缺少可追溯台账。
4. 章程或合伙协议中的担保、借款、重大合同、用印权限没有结构化记录。
5. 股东认缴出资期限临近或逾期时容易遗漏。
6. 企业希望用自然语言查询本地资料，但系统必须区分管理查询和法律判断。

### 核心特点

- **本地优先**：所有企业资料保存到用户选择的 `<workspace_root>/<company_name>`。
- **台账与记录并重**：CSV 台账用于检索，Markdown 记录用于阅读和追踪。
- **历史资料导入**：支持合同、员工花名册、劳动合同、制度、证照、章程、授权、用印记录和出资资料。
- **严审边界**：法律、风险、权限、金额、地方规则判断必须先读取材料、核验规则、记录来源边界。
- **提醒独立模块**：本地提醒永远可用；飞书仅作为可选日历提醒。
- **企业内部身份**：不输出律师顾问版、正式法律意见书、法院/仲裁/行政提交材料或律师/律所落款。

## 架构

```text
企业资料
  │
  ▼
导入与读取
  - 暂存原始文件
  - 提取文本
  - 读取复查摘要
  - 来源边界记录
  │
  ▼
业务模块
  - 合同管理
  - 人力资源法务
  - 公章证照
  - 章程权限
  - 股东出资
  - 提醒中心
  - 本地问库
  │
  ▼
严审流程
  - 用户目标确认
  - 材料读取
  - 法规/规则核验
  - 风险识别
  - 内部建议
  - 文件位置和下一步
```

## Skill 列表

| Skill | 标签 | 说明 | 状态 |
| :--- | :--- | :--- | :--- |
| [enterprise-legal-ops](skills/enterprise-legal-ops/) | 企业法务 | 面向中小企业内部管理合同、员工花名册、劳动合同、未休年假、制度文件、公章证照、章程权限、股东出资、提醒和本地问库 | 核心 |

## 典型工作流

#### 初始化企业工作区

```text
企业选择本地资料保存根目录
  │
  ▼
运行工作区初始化
  │
  ▼
生成合同、HR、公章证照、提醒、问库和系统记录目录
  │
  ▼
告诉用户企业档案目录、台账位置和下一步可上传资料
```

#### 合同管理

```text
上传合同
  │
  ▼
导入暂存并读取文本
  │
  ▼
归档原件、生成合同台账和 Markdown 记录
  │
  ▼
提取到期、续约和提前通知提醒
  │
  ▼
如需审查：进入严审并生成企业内部 Word 修订稿
```

#### HR 管理

```text
上传员工花名册
  │
  ▼
识别姓名、部门、岗位、入职日期、合同期限和年假字段
  │
  ▼
生成 employees.csv、employee-record.md 和 annual-leave.csv
  │
  ▼
写入试用期、劳动合同到期、续签和年假提醒
```

#### 公章证照与章程权限

```text
上传证照、章程、授权或用印文件
  │
  ▼
生成证照、印章、授权、治理文件或出资台账
  │
  ▼
涉及担保、借款、融资、重大合同或对外承诺时
  │
  ▼
进入章程权限严审，生成内部权限校验记录
```

## 快速开始

#### 安装项目

```bash
git clone https://github.com/pa1nrui1/enterprise-legal-ops.git
cd enterprise-legal-ops
```

#### 初始化企业工作区

```bash
python skills/enterprise-legal-ops/scripts/init_workspace.py \
  --root "<workspace_root>" \
  --company "<company_name>"
```

#### 导入员工花名册

```bash
python skills/enterprise-legal-ops/scripts/import_roster.py \
  --workspace "<company_workspace>" \
  --file "员工花名册.xlsx"
```

#### 本地提醒查询

```bash
python skills/enterprise-legal-ops/scripts/reminders.py list \
  --workspace "<company_workspace>" \
  --days 30
```

#### 本地自然语言问库

```bash
python skills/enterprise-legal-ops/scripts/query_workspace.py \
  --workspace "<company_workspace>" \
  --query "哪些合同下个月到期"
```

## 目录结构

```text
.
├── SKILL.md
├── skills/
│   └── enterprise-legal-ops/
│       ├── SKILL.md
│       ├── agents/
│       ├── references/
│       ├── scripts/
│       └── tests/
├── .codex-plugin/
│   └── plugin.json
├── README.md
└── LICENSE
```

## 本地配置

本仓库不包含企业真实资料、作者本机路径、客户材料或外部服务凭证。真实使用前，建议配置：

- 企业名称、统一社会信用代码、所在地和主要经营地区；
- 本地资料保存根目录；
- 是否启用飞书日历提醒；
- OCR、PDF、DOCX、XLSX 读取环境；
- 如需合同 Word 修订稿，配置外部合同审查红线引擎路径：`LEGAL_CONTRACT_REVIEW_SKILL`。

## 安全边界

Enterprise Legal Ops 默认强调以下边界：

- 不把模型记忆包装成文件事实、现行法规或已核验规则。
- 不在未读取材料、未完成复查、未核验规则时输出确定法律判断。
- 不因飞书同步失败而丢失本地提醒。
- 不覆盖原始文件，不删除历史版本和历史提醒。
- 不把内部风险判断包装为律师顾问意见或正式法律意见。
- 不把真实企业资料、API key、飞书凭证或本机私有路径提交到公开仓库。

## 开源范围

本仓库发布的是企业法务运营 Skill 规则、参考流程和本地脚本，不包含：

- 真实企业资料；
- 真实员工信息；
- 合同原件；
- 公章证照原件；
- 飞书文档或日历数据；
- 私有数据库凭证；
- 作者本机业务路径。

## 贡献

欢迎通过 issue 或 pull request 改进：

- 更清晰的企业法务运营工作流；
- 更稳健的导入、读取复查和来源边界记录；
- 更通用的合同、HR、公章证照和章程权限台账；
- 更好的飞书日历提醒适配；
- 更严格的开源脱敏和安全检查。

提交贡献前，请不要包含真实企业信息、员工资料、合同原件、证照文件、本机路径、飞书凭证或任何未获授权公开的数据。

## 免责声明

本项目仅提供 AI Agent 工作流、提示规则和本地脚本示例。它不构成法律意见、律师服务、法律代理关系或对任何事项处理结果的承诺。任何真实法律或经营事项均应由企业负责人或具备相应资格的专业人士基于完整事实、有效授权、现行规则和可核验来源进行独立判断。

## License

MIT
