# Strict Review Protocol

Use this for any substantive risk/legal judgment.

## Triggers

Contracts:

- review, revision, Word tracked-change review draft
- drafting, termination, renewal, supplement
- whether to sign, terminate, breach, seal, authorize

HR:

- termination, transfer, salary reduction, discipline, resignation dispute
- overtime, wage deduction, annual leave compensation
- policy legality, policy conflict, policy procedure

Seals/licenses/governance:

- whether to seal
- authorization validity
- guarantee, borrowing, financing, major contract authority
- articles change impact
- shareholder contribution overdue risk
- license coverage for business

## Required Steps

```text
classify task
→ confirm user goal and stance/context
→ read all relevant materials
→ extract key facts
→ create read-review summary
→ verify statutes/rules when cited
→ identify risks
→ generate internal recommendation
→ write source boundary
→ write user confirmation record where needed
→ tell user file locations and next steps
```

## Read-Review Summary

```markdown
# 读取复查摘要

## 文件
-

## 读取方式
-

## 关键字段
-

## 存疑项
-

## 完整性评估
-

## 是否需要用户确认
-
```

## Rule Verification Summary

```markdown
# 法规/规则核验摘要

## 核验事项
-

## 核验来源
-

## 核验结果
-

## 适用地区
-

## 现行有效状态
-

## 对本事项的影响
-
```

## Source Boundary

```markdown
# 来源边界

## 已读取材料
-

## 已核验内容
-

## 未读取或缺失材料
-

## 存疑项
-

## 输出边界
-
```

## Prohibitions

Do not:

- output a legal/risk conclusion without reading relevant materials
- cite law or local rules without verification
- review a contract without confirmed review position
- assess HR discipline/termination/wage deduction without policies and employee materials
- approve sealing/guarantee/borrowing without articles/authorization review
- create lawyer-advisor versions, formal legal opinions, or external filings
- use lawyer or law-firm signature blocks
- overwrite source files
- delete historical versions or reminders
- invent unfound information

Use `scripts/strict_review_record.py` to create the local strict-review folder and log user confirmation, rule verification, source boundary, and risk records before producing any substantive internal recommendation.
