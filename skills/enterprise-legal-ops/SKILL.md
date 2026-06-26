---
name: enterprise-legal-ops
description: 中小企业本地法务运营管理 Skill。用于企业内部管理合同、员工/劳动合同/年假/制度、公章证照、章程权限、股东出资、提醒和本地自然语言问库。用户要初始化企业法务工作区、上传历史合同/员工花名册/劳动制度/证照/章程/授权/用印记录、生成本地台账、查询到期提醒、做企业内部合同审查 Word 修订稿、合同起草、HR 风险预判、制度冲突检查、旧制度合法性审查、公章用印权限校验、股东出资提醒、飞书日历提醒配置时触发。
---

# Enterprise Legal Ops

## Core Identity

Use this Skill for one company's internal legal operations workspace. It is not a lawyer work-product Skill.

Never output:

- lawyer-advisor versions
- formal legal opinions
- court/arbitration/administrative filings
- lawyer or law-firm signature blocks
- Feishu contract-review documents
- contract flowcharts, mind maps, or negotiation bottom lines

Allowed outputs are internal company records, risk notes, source-boundary records, reminders, tables, Markdown records, and internal Word tracked-change contract review drafts.

## First-Run Guidance

When a company workspace is not configured, tell the user this Skill can:

1. Manage contracts: upload contracts, generate contract ledgers, review internally, and track expiry/renewal.
2. Manage HR legal operations: import rosters and labor contracts, track probation/renewal/annual leave, review policies.
3. Manage seals, licenses, articles, authorizations, shareholder contributions, and authority checks.
4. Manage reminders locally, with optional Feishu calendar sync.
5. Answer local natural-language questions from CSV ledgers, Markdown records, and extracted text.

Ask the user to choose a local workspace root and company name, or run `scripts/init_workspace.py`.

## Workflow Router

Before doing substantive work, classify the request:

- **Workspace/data setup**: read `references/workspace-data-standard.md`; use `scripts/init_workspace.py`.
- **Upload/archive business records**: read the relevant module reference; use `scripts/import_document.py` for intake and `scripts/archive_record.py` for ledger/Markdown/source-map archival.
- **Contracts**: read `references/contracts.md`; use `scripts/archive_record.py --kind contract` for local archival and `scripts/contract_redline_review.py` for Word tracked-change drafts.
- **HR**: read `references/hr.md`; use `scripts/import_roster.py` for employee rosters, and `scripts/archive_record.py` for employee, labor-contract, annual-leave, and policy source records.
- **Seals/licenses/articles/capital contribution**: read `references/seals-licenses-governance.md`; use `scripts/archive_record.py` for license, seal, authorization, seal-use, governance, authority-check, and capital records.
- **Reminders or Feishu calendar reminders**: read `references/reminders.md`; use `scripts/reminders.py` when possible.
- **Local natural-language query**: read `references/local-query.md`; use `scripts/query_workspace.py` for CSV/Markdown search.
- **Any substantive legal/risk judgment**: read `references/strict-review.md`; use `scripts/strict_review_record.py` to create local strict-review records before generating risk recommendations.

Load only the needed reference files.

## Hard Gates

### Internal-only output

All outputs are company-internal. If the user asks for a lawyer opinion, court filing, or external legal document, refuse that output form and offer an internal draft/risk note instead.

### Full reading before legal judgment

For legal/risk judgments, read all user-provided relevant files. Record reading method, key fields, doubts, and completeness. If reading fails, disclose the failed file and impact.

### Verification before legal/rule citations

If citing statutes, local labor rules, corporate governance rules, license requirements, or mandatory rules, verify current applicability. Do not rely on model memory as authority.

### Contract review deliverable

Contract review's only review deliverable is an internal Word tracked-change review draft. Do not create Feishu review docs, flowcharts, mind maps, or negotiation-bottom-line documents.

### Feishu scope

Feishu is only for optional calendar reminders. If Feishu sync fails, keep local reminders intact and report the real sync failure.

## User-Facing Completion

Every task must end with a completion note that includes:

- what was completed
- generated or updated files
- ledger paths
- reminder status
- risks or missing information
- next steps

Do not end with only “done”.

## Key Resources

- Product requirements: `../../docs/prd/`
- Workspace/data standard: `references/workspace-data-standard.md`
- Strict review: `references/strict-review.md`
- Contract module: `references/contracts.md`
- HR module: `references/hr.md`
- Seals/licenses/governance module: `references/seals-licenses-governance.md`
- Reminders module: `references/reminders.md`
- Local query module: `references/local-query.md`
- Scripts:
  - `scripts/init_workspace.py`
  - `scripts/import_document.py`
  - `scripts/import_roster.py`
  - `scripts/archive_record.py`
  - `scripts/ledger.py`
  - `scripts/reminders.py`
  - `scripts/query_workspace.py`
  - `scripts/contract_redline_review.py`
  - `scripts/strict_review_record.py`
