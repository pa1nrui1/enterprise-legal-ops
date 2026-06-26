# HR Module

Use for employee roster, labor contracts, annual leave, policies, policy conflicts, policy legality, salary/attendance questions, and internal HR risk prediction.

## Scope

Include:

- roster import and `employees.csv`
- labor contract import/matching and `employment-contracts.csv`
- employee `employee-record.md`
- probation/contract expiry/renewal reminders
- annual leave management and `annual-leave.csv`
- policy file management
- new-old policy conflict checks
- old policy legality review
- policy procedure reminders
- attendance/salary questions
- transfer, salary reduction, discipline, termination, resignation risk prediction

Exclude:

- labor arbitration representation
- litigation case management
- formal legal opinions
- external legal documents
- lawyer/law-firm signature blocks

## Roster Import

Support `.xlsx`, `.xls`, `.csv`; try OCR/read for PDF/Word/images with accuracy boundary.

Extract employee id, name, department, position, entry date, contract dates, probation end, work location, employment status, working-hours system, salary structure, social insurance status, annual leave fields if present.

Create/update:

- `employees.csv`
- employee records
- probation/contract/renewal reminders
- annual leave records if data exists

Use `scripts/import_roster.py` for `.csv`, `.xlsx`, and `.xls` rosters. It creates employee ids when missing, updates `employees.csv`, writes employee records, creates probation/contract reminders, and writes `annual-leave.csv` when leave fields exist.

## Labor Contract Matching

Read labor contracts fully, extract name/ID and match roster:

- name + ID match: auto-match
- name only with duplicates: ask user
- not in roster: ask whether to create employee
- conflicting contract dates: mark `待复核`
- OCR dates, amounts, ID numbers: mark review status

## Annual Leave

Maintain:

```text
<company_workspace>/02-人力资源/annual-leave.csv
```

Fields:

```text
leave_record_id,employee_id,employee_name,year,entry_date,continuous_work_years,statutory_annual_leave_days,company_annual_leave_days,used_annual_leave_days,remaining_annual_leave_days,carryover_rule,expiry_date,compensation_required,compensation_amount,calculation_basis,source_file_path,record_md_path,risk_flags,created_at,updated_at
```

Never assert used/unused leave without attendance/leave records. For compensation, verify law/local rules and show formula/source.

## Policy Management

Policy files include employee handbook, labor contract templates, salary, attendance, performance, discipline/reward, overtime approval, leave, annual leave, resignation handover, transfer, and HR-related approval policies.

On import:

- read fully
- identify name, version date, effective date, scope
- extract salary, hours, attendance, performance, discipline, termination, annual leave clauses
- update policy index
- mark publicity, democratic procedure, employee receipt materials
- trigger old-policy legality review
- if similar policy exists, trigger conflict check

Use `scripts/archive_record.py --kind policy` to archive policy files, update `policies.csv`, append `制度索引.md`, and create legality/conflict review placeholder records. Complete substantive legality or conflict conclusions only through strict review.

## Policy Conflict Check

Trigger when uploading/drafting/modifying policies or when user asks about conflict.

Compare at least current handbook, labor contract template, salary, attendance, performance, discipline, overtime approval, leave, annual leave, resignation handover, transfer.

Detect conflicts in effective date, scope, salary, payday, overtime approval/calculation, leave/annual leave, performance, discipline, termination, transfer/salary reduction, delivery/receipt, and labor contract terms.

Output must identify exact clauses and concrete impact.

## Policy Procedure Reminder

If a policy touches wages, working hours, rest/leave, social insurance/welfare, labor safety, discipline, assessment/reward, or termination, remind HR about:

- employee/representative discussion
- union or employee representative consultation
- final text
- publication/training
- employee receipt
- preserving meeting notice, attendance, discussion records, feedback, consultation records, screenshots, signed receipts, training records

Do not equate text legality with procedural validity.

## Old Policy Legality Review

Review at least wage deductions, overtime approval/pay, lateness/absence penalties, fines/deductions, performance elimination, transfer/salary reduction, probation/hiring conditions, non-compete/confidentiality, annual/sick/marriage/maternity leave, termination grounds, unilateral final interpretation, democratic procedure/publication/receipt.

Point to exact clauses, source text, risk, suggested fix, replacement text when possible, and verification status.

## HR Risk Prediction

For termination, transfer, salary reduction, discipline, resignation disputes, read employee contract, roster, handbook, salary/attendance/performance/discipline/annual leave policies, facts, notices, interviews, defenses, delivery, union/employee representative materials if any.

Confirm protected status, work injury/medical period/disability, near-retirement status, recent complaints/reporting/labor inspection/arbitration threats, intended action, evidence, procedure, outstanding annual leave/wages/bonus/commission/reimbursement.

Do not draft external termination/discipline/arbitration documents.

## Completion Note

Include employee ledger, employee record, annual leave ledger, policy files, conflict/legality records, reminders, risks/gaps, next steps.
