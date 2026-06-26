# Contract Module

Use for contract upload, ledgering, review, tracked-change review draft, drafting, templates, versions, expiry, and contract queries.

## Scope

Include:

- upload/archive contracts
- generate `contracts.csv`
- create `contract-record.md`
- review contracts
- create internal Word tracked-change review draft
- draft contracts
- manage company template library
- manage versions/final confirmation
- create local reminders
- answer local contract questions
- link to governance authority checks for guarantee, borrowing, financing, major commitment, and sealing

Exclude:

- Feishu contract review documents
- business flowcharts
- mind maps
- negotiation-bottom-line documents
- lawyer-advisor versions
- formal legal opinions
- lawyer/law-firm signature blocks

## Upload Workflow

```text
save source file
→ read fully
→ extract basic fields
→ check duplicate/similar records
→ confirm project/ownership if unclear
→ generate contract_id
→ archive original
→ update contracts.csv
→ create contract-record.md
→ extract expiry/renewal/notice dates
→ create reminders
→ output completion note
```

## Key Fields

Extract where possible:

- contract name/type
- our party and role
- counterparty
- amount
- signing/effective/start/end dates
- renewal and notice terms
- payment, delivery/service, acceptance
- breach, termination, dispute resolution
- attachments/orders/supplements
- sealing, authorization, guarantee, borrowing, financing, major commitment flags

Mark missing fields as `待确认`; mark OCR doubts as `OCR待复核`.

## Review Gate

Before review, confirm:

- review position
- company role
- focus areas
- whether Word tracked-change review draft is needed
- whether guarantee/borrowing/financing/major commitment/sealing is involved
- whether articles/authorization check is needed
- signing deadline

No substantive review before confirmed review position.

## Review Method

Use the existing legal contract review method as reference:

1. transaction structure
2. contract type
3. clause completeness
4. special risk card

At minimum check:

- subject qualification
- signing authority
- subject matter
- price/payment
- term
- delivery/acceptance
- breach
- termination
- dispute resolution
- notices
- attachments/supplements
- sealing/authorization
- expiry/renewal/notice

Risk levels:

```text
低
中
高
签署阻断
```

## Review Issue Format

```markdown
### 问题 001｜问题标题

- 条款位置：
- 原文摘录：
- 问题类型：
- 风险说明：
- 处理建议：必须修改 / 建议修改 / 需企业确认 / 可优化
- 建议修改文本：
- 是否进入 Word 修订稿：
- 来源：
```

Do not include negotiation bottom line or lawyer strategy.

## Only Review Deliverable

The only contract review deliverable is:

```text
Word 修订格式合同审核稿
```

Requirements:

- original contract is read-only
- do not overwrite original
- save new review draft
- use real Word tracked changes
- use comments for major risks, fact gaps, and company decisions
- do not model-fill amounts, dates, contacts, accounts, or business choices
- run structure/QA checks before calling complete

Use `scripts/contract_redline_review.py` after a valid `redline-plan.json` has been produced. The wrapper reuses the existing legal contract review redline engine and QA checker, preserving the original contract and producing a separate internal tracked-change DOCX.

## Drafting

Drafting modes:

```text
company template
→ generic template
→ independent drafting
```

Before drafting confirm contract type, parties, role, background, subject/service, price/payment, term, delivery/acceptance, breach preference, dispute resolution, sealing, guarantee/borrowing/authorization/major commitment, and whether to use company template.

Drafts are internal company drafts only.

## Template Library

Company templates live at:

```text
<company_workspace>/01-合同管理/模板库/
```

Index:

```text
template_id,template_name,contract_type,preferred_role,applicable_scene,source_file_path,record_md_path,last_used_at,status,created_at,updated_at
```

Use `scripts/archive_record.py --kind template` to archive company templates and update `template-index.csv`.

## Version And Final

Never guess final version. Mark final only when user explicitly says:

```text
最终版
定稿
签署版
已签署
归档
```

## Completion Note

Include original contract path, ledger path, detail record path, review/draft output path, reminders, risks/gaps, next steps.
