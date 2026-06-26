# Seals, Licenses, Governance, And Capital Contributions

Use for licenses, seals, authorization, seal use, articles/partnership agreement, resolutions, authority checks, shareholder capital contribution, and related reminders.

## Scope

Include:

- licenses and qualifications
- seal ledger
- seal-use records
- authorizations
- articles/partnership agreement/resolutions
- authority summaries
- articles changes
- authority checks for sealing/signing/guarantee/borrowing/major commitments
- shareholder capital contribution ledger and reminders

Exclude external filings, license application agency, formal legal opinions, litigation/arbitration materials.

## Licenses

On upload:

- save original
- read fully
- extract license name/type, holder, number, issuing authority, issue date, expiry date, annual check
- compare holder with company
- update `licenses.csv`
- create Markdown record
- create expiry/annual-check reminders

Risk flags:

- expired or near expiry
- holder mismatch
- business scope mismatch
- annual check date missing
- authenticity/effectiveness cannot be confirmed
- OCR date/number doubt

## Seals

Maintain `seals.csv`:

```text
seal_id,seal_name,seal_type,custodian,authorized_scope,approval_rule,storage_location,status,record_md_path,created_at,updated_at
```

Record each seal's custodian, scope, storage, approval rule. Do not delete lost/stopped/recarved seals; change status.

## Seal Use

Maintain `seal-use.csv`:

```text
seal_use_id,seal_id,document_name,document_type,purpose,applicant,approver,use_date,counterparty,amount,high_risk_type,authority_check_status,governance_basis,file_path,record_md_path,next_action,created_at,updated_at
```

High-risk seal use includes external commitment, guarantee, borrowing, financing, equity transfer, major asset disposal, long-term contract, large contract, labor termination, authorization to sign for company.

High-risk use must read target document, extract amount/counterparty/obligations, check articles/partnership agreement, check resolutions/authorization, create authority-check record, and recommend pause or supplemental approval if basis is insufficient.

## Authorizations

Maintain `authorizations.csv`:

```text
authorization_id,authorization_name,grantor,grantee,scope,start_date,end_date,revocation_status,file_path,record_md_path,risk_flags,created_at,updated_at
```

Always record grantor, grantee, scope, period. Expiring authorizations create reminders. Revoked/expired authorizations are not deleted.

## Governance Documents

Documents include articles, amendments, partnership agreement, supplemental partnership agreement, shareholder meeting resolution, board resolution, executive director decision, partner meeting resolution, guarantee policy, finance approval policy, seal policy, major contract approval policy.

Maintain `governance-documents.csv`:

```text
governance_doc_id,doc_name,doc_type,version_date,effective_date,company_name,key_authority_summary,file_path,record_md_path,status,created_at,updated_at
```

Extract company, shareholders/partners, legal representative/executive partner, meeting/board/executive authority, investment, guarantee, borrowing/financing, major contract, seal approval, voting ratio, version/effective date, amendments.

Create `authority-summary.md` for every articles/partnership agreement.

## Capital Contributions

Maintain:

```text
<company_workspace>/03-公章证照/capital-contributions.csv
```

Fields:

```text
contribution_id,shareholder_name,shareholder_type,subscribed_amount,paid_amount,unpaid_amount,contribution_method,subscription_deadline,paid_date,equity_ratio,source_document,source_file_path,proof_file_path,status,risk_flags,next_action,created_at,updated_at
```

Status values:

```text
未到期
临近到期
已实缴
部分实缴
逾期未缴
待复核
```

Use articles, amendments, shareholder agreement, resolutions, registration information, contribution certificate, capital verification report, bank receipt, financial voucher, equity transfer agreement.

Do not assert paid-in contribution without proof. If articles, registration, and shareholder agreement conflict, mark `待复核`. If deadline passed without proof, mark high risk.

Create reminders for contribution due soon, overdue, partially paid, proof missing, and contribution data mismatch.

When multiple source documents exist, compare shareholder name, subscribed amount, equity ratio, deadline, method, proof, partial/overdue status. Save comparison to:

```text
<company_workspace>/03-公章证照/章程合伙协议/出资信息比对记录.md
```

## Authority Check

Triggers:

- external commitment
- guarantee
- borrowing
- financing
- equity transfer
- major asset disposal
- long-term or large contract
- labor termination or group employee matter
- authorization to sign for company
- user asks whether a document can be sealed

Process:

```text
read target document
→ identify type and obligations
→ extract amount, term, counterparty, commitment
→ read current articles/partnership/governance documents
→ check approval authority
→ check resolutions/authorization
→ create authority-check record
→ give internal next action
```

Conclusion values only:

```text
已通过
待补充审批
章程无明确依据
建议暂停用印
待人工确认
```

## Completion Note

Include ledgers, governance record, authority check record, capital contribution status, reminders, risks/gaps, next steps.
