# Local Natural-Language Query

Use for local questions over CSV ledgers, Markdown records, extracted text, and original file paths.

Do not answer legal/risk judgments directly. Route them to strict review.

## Query Types

Management query: answer from local ledgers/records.

Historical query: answer from previous records.

Legal/risk judgment: locate sources, then route to the proper module and strict review.

## Files

```text
<company_workspace>/05-本地问库/
├── search-index.md
├── qa-log.md
├── source-map.csv
├── extracted-text-index.csv
├── query-routing-log.md
└── unresolved-queries.md
```

`source-map.csv`:

```text
source_id,module,object_id,object_name,csv_path,md_path,extracted_text_path,original_file_path,last_updated_at
```

`extracted-text-index.csv`:

```text
text_id,module,object_id,source_file_path,extracted_text_path,read_method,read_status,ocr_status,key_fields,created_at,updated_at
```

## Query Order

```text
understand question
→ classify query type
→ classify module
→ query matching CSV
→ query Markdown record
→ query extracted text if needed
→ locate original file if needed
→ decide whether strict review is needed
→ answer with sources
→ log query
```

## Routing

Contracts: contracts, agreements, orders, supplements, termination, renewal, expiry, review, tracked-change draft, signed version.

HR: employee, labor contract, probation, renewal, annual leave, attendance, wage, social insurance, transfer, salary reduction, discipline, termination, policy.

Governance: license, qualification, seal, authorization, articles, partnership agreement, shareholder meeting, board, guarantee, borrowing, capital contribution.

Reminder: reminder, expiry, overdue, annual check, renewal, pending, today, this week, next month, Feishu.

## Answer Formats

Management query:

```markdown
## 查询结果

- 查询问题：
- 查询范围：
- 找到结果：
- 来源：
- 下一步建议：
```

Historical query:

```markdown
## 历史记录查询结果

- 查询问题：
- 已找到记录：
- 关键摘要：
- 来源文件：
- 下一步建议：
```

Legal/risk judgment:

```markdown
## 需要进入严审

这个问题涉及实质法律判断，不能仅根据台账直接回答。

已找到资料：
-

还需要补充或确认：
-

建议进入模块：
-

下一步：
-
```

No result:

```markdown
## 未查询到结果

- 查询问题：
- 已查询范围：
- 未找到内容：
- 可能原因：
- 建议下一步：
```

Write unresolved queries to `unresolved-queries.md`.
