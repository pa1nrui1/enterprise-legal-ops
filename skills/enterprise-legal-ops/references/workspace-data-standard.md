# Workspace And Data Standard

Use placeholders in docs and examples:

- `<workspace_root>`: user-chosen local storage root
- `<company_name>`: company name or confirmed short name
- `<company_workspace>`: `<workspace_root>/<company_name>`

Do not hardcode personal absolute paths.

## Directory Tree

```text
<company_workspace>/
├── 00-企业基础档案/
├── 01-合同管理/
│   ├── contracts.csv
│   ├── contract-reminders.csv
│   └── 模板库/template-index.csv
├── 02-人力资源/
│   ├── employees.csv
│   ├── employment-contracts.csv
│   ├── annual-leave.csv
│   └── hr-reminders.csv
├── 03-公章证照/
│   ├── licenses.csv
│   ├── seals.csv
│   ├── authorizations.csv
│   ├── seal-use.csv
│   ├── governance-documents.csv
│   ├── authority-checks.csv
│   └── capital-contributions.csv
├── 04-提醒中心/
│   ├── reminders.csv
│   ├── reminder-summary.md
│   ├── feishu-config.md
│   ├── feishu-sync-log.md
│   └── completed-reminders.csv
├── 05-本地问库/
│   ├── search-index.md
│   ├── qa-log.md
│   ├── source-map.csv
│   ├── extracted-text-index.csv
│   ├── query-routing-log.md
│   └── unresolved-queries.md
├── 06-导入暂存/
│   ├── 待识别/
│   ├── 读取失败/
│   ├── 待用户确认/
│   └── 已归档记录/
├── 07-输出文件/
└── _system/
    ├── current-company.md
    ├── workspace-config.md
    ├── import-log.csv
    ├── read-review-log.md
    ├── legal-verification-log.md
    ├── source-boundary-log.md
    ├── user-confirmation-log.md
    └── error-log.md
```

## Import Rule

For any upload:

```text
save to 06-导入暂存/待识别
→ detect file type
→ read fully
→ extract key fields
→ classify module
→ create read-review summary
→ ask user when ownership or key fields are unclear
→ move/copy into target module
→ update CSV
→ create Markdown record
→ create reminders
→ output completion note
```

Never overwrite old source files or historical versions.

Use `scripts/import_document.py` for temporary intake and text extraction. After module and key fields are known, use `scripts/archive_record.py` to archive the item into its business folder, upsert the CSV ledger, create the Markdown record, update `source-map.csv`, and create local reminders.

## Completion Note

Always tell the user:

- processed files
- ledgers created/updated
- Markdown records created/updated
- reminders created
- uncertain or missing information
- suggested next steps
