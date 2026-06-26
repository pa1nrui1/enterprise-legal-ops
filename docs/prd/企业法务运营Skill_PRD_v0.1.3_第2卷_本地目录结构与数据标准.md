# 企业法务运营 Skill PRD

版本：v0.1.3  
卷号：第 2 卷  
状态：已确认基线  
文档主题：本地目录结构、数据表字段、Markdown 记录模板、上传导入规则

## 1. 本卷目标

本卷规定企业法务运营 Skill 的本地数据结构。

它要解决四个问题：

1. 用户上传的资料保存在哪里。
2. 系统生成的台账保存在哪里。
3. 每类台账必须有哪些字段。
4. 上传 Excel、Word、PDF、图片后，如何转成可搜索、可追踪的本地记录。

## 2. 本地根目录

每个企业独立一个本地工作区。系统不得预设固定绝对路径。

首次初始化时，必须由用户选择或确认企业数据保存位置。文档统一使用占位符：

```text
<workspace_root>/<company_name>/
```

其中：

1. `<workspace_root>`：用户选择的本地保存目录
2. `<company_name>`：企业名称或用户确认的企业简称

不得写死任何开发者个人机器路径，不得假设用户使用 macOS、Windows 或 Linux 的特定用户目录。

初始化后，应在企业工作区保存配置文件：

```text
<company_workspace>/_system/workspace-config.md
```

## 3. 顶层目录结构

```text
<company_workspace>/
├── 00-企业基础档案/
├── 01-合同管理/
├── 02-人力资源/
├── 03-公章证照/
├── 04-提醒中心/
├── 05-本地问库/
├── 06-导入暂存/
├── 07-输出文件/
└── _system/
```

## 4. 各目录用途

### 4.1 `00-企业基础档案/`

保存企业基础治理资料，包括营业执照、公司章程、合伙协议、股东会决议、董事会决议、法定代表人身份证明、授权委托书、内部审批制度、印章管理制度、财务审批制度。

系统生成文件：

```text
company-profile.md
governance-summary.md
articles-change-log.md
authority-matrix.md
```

### 4.2 `01-合同管理/`

保存合同原件、合同记录、合同审查文件和版本记录。

```text
01-合同管理/
├── contracts.csv
├── contract-reminders.csv
├── 模板库/
├── <合同编号-合同简称>/
│   ├── 01-原始文件/
│   ├── 02-读取文本/
│   ├── 03-合同记录/
│   ├── 04-审查记录/
│   ├── 05-版本记录/
│   └── 06-输出文件/
```

### 4.3 `02-人力资源/`

保存员工花名册、劳动合同、制度文件、未休年假和员工专项记录。

```text
02-人力资源/
├── employees.csv
├── employment-contracts.csv
├── annual-leave.csv
├── hr-reminders.csv
├── 员工记录/
├── 制度文件/
├── 劳动合同/
├── 考勤薪酬/
└── 离职处分调岗降薪/
```

### 4.4 `03-公章证照/`

保存证照、印章、授权、用印、章程权限和股东出资记录。

```text
03-公章证照/
├── licenses.csv
├── seals.csv
├── authorizations.csv
├── seal-use.csv
├── governance-documents.csv
├── authority-checks.csv
├── capital-contributions.csv
├── 证照文件/
├── 印章资料/
├── 授权文件/
├── 用印记录/
└── 章程合伙协议/
```

### 4.5 `04-提醒中心/`

保存所有提醒，不论是否启用飞书。

```text
04-提醒中心/
├── reminders.csv
├── feishu-config.md
├── feishu-sync-log.md
└── reminder-summary.md
```

### 4.6 `05-本地问库/`

保存问库索引和可搜索摘要。

```text
05-本地问库/
├── search-index.md
├── qa-log.md
├── source-map.csv
└── extracted-text-index.csv
```

### 4.7 `06-导入暂存/`

保存用户刚上传、尚未归档的资料。

```text
06-导入暂存/
├── 待识别/
├── 读取失败/
├── 待用户确认/
└── 已归档记录/
```

### 4.8 `07-输出文件/`

保存企业内部输出文件，包括合同审查记录、合同修改建议、HR 风险提示、用印风险提示、证照缺口清单、内部报告草稿。

禁止保存律师正式意见书、律所落款文件、对外正式法律文书。

### 4.9 `_system/`

保存系统内部记录。

```text
_system/
├── current-company.md
├── workspace-config.md
├── import-log.csv
├── read-review-log.md
├── legal-verification-log.md
├── source-boundary-log.md
├── user-confirmation-log.md
└── error-log.md
```

## 5. 核心 CSV 台账字段

### 5.1 `contracts.csv`

```text
contract_id,contract_name,contract_type,our_party,our_role,counterparty,review_position,amount,effective_date,end_date,auto_renewal,notice_days,latest_notice_date,status,original_file_path,record_md_path,latest_review_date,risk_level,next_action,created_at,updated_at
```

### 5.2 `employees.csv`

```text
employee_id,name,department,position,employment_status,entry_date,probation_end_date,contract_start_date,contract_end_date,work_location,working_hours_system,salary_structure,social_insurance_status,contract_file_path,record_md_path,risk_flags,next_action,created_at,updated_at
```

### 5.3 `employment-contracts.csv`

```text
employment_contract_id,employee_id,employee_name,contract_type,contract_start_date,contract_end_date,probation_end_date,position,work_location,salary_terms,working_hours_system,renewal_status,contract_file_path,record_md_path,read_status,risk_flags,created_at,updated_at
```

### 5.4 `annual-leave.csv`

```text
leave_record_id,employee_id,employee_name,year,entry_date,continuous_work_years,statutory_annual_leave_days,company_annual_leave_days,used_annual_leave_days,remaining_annual_leave_days,carryover_rule,expiry_date,compensation_required,compensation_amount,calculation_basis,source_file_path,record_md_path,risk_flags,created_at,updated_at
```

### 5.5 `licenses.csv`

```text
license_id,license_name,license_type,holder,license_number,issue_authority,issue_date,expiry_date,annual_check_required,annual_check_deadline,file_path,record_md_path,status,risk_flags,next_action,created_at,updated_at
```

### 5.6 `seals.csv`

```text
seal_id,seal_name,seal_type,custodian,authorized_scope,approval_rule,storage_location,status,record_md_path,created_at,updated_at
```

### 5.7 `seal-use.csv`

```text
seal_use_id,seal_id,document_name,document_type,purpose,applicant,approver,use_date,counterparty,amount,high_risk_type,authority_check_status,governance_basis,file_path,record_md_path,next_action,created_at,updated_at
```

### 5.8 `authorizations.csv`

```text
authorization_id,authorization_name,grantor,grantee,scope,start_date,end_date,revocation_status,file_path,record_md_path,risk_flags,created_at,updated_at
```

### 5.9 `governance-documents.csv`

```text
governance_doc_id,doc_name,doc_type,version_date,effective_date,company_name,key_authority_summary,file_path,record_md_path,status,created_at,updated_at
```

### 5.10 `authority-checks.csv`

```text
authority_check_id,matter_name,matter_type,related_file_path,amount,counterparty,governance_basis,required_approval,existing_approval,conclusion,risk_flags,record_md_path,created_at,updated_at
```

### 5.11 `capital-contributions.csv`

```text
contribution_id,shareholder_name,shareholder_type,subscribed_amount,paid_amount,unpaid_amount,contribution_method,subscription_deadline,paid_date,equity_ratio,source_document,source_file_path,proof_file_path,status,risk_flags,next_action,created_at,updated_at
```

### 5.12 `reminders.csv`

```text
reminder_id,source_module,source_id,reminder_type,title,description,trigger_date,advance_days,remind_date,priority,local_status,feishu_enabled,feishu_status,feishu_event_id,source_file_path,record_md_path,owner,next_action,created_at,updated_at
```

## 6. Markdown 记录模板

每类事项必须生成可读 Markdown 记录。模板至少包括：

1. 基础信息
2. 文件位置
3. 关键摘要
4. 风险提示
5. 提醒事项
6. 来源边界
7. 下一步

关键模板包括：

1. `contract-record.md`
2. `employee-record.md`
3. `license-record.md`
4. `authority-summary.md`
5. `seal-use-record.md`
6. `read-review-summary.md`
7. `source-boundary.md`
8. `user-confirmation.md`

## 7. 上传导入规则

用户上传任意文件后，执行：

```text
接收文件
→ 保存到 06-导入暂存/待识别/
→ 判断文件类型
→ 完整读取
→ 提取关键字段
→ 判断所属模块
→ 生成读取复查摘要
→ 用户确认归属或系统自动归档
→ 移动到对应模块目录
→ 更新 CSV 台账
→ 生成 Markdown 记录
→ 写入提醒
→ 如启用飞书，处理飞书提醒
→ 输出完成说明
```

V1 必须支持：

```text
.xlsx
.xls
.csv
.docx
.doc
.pdf
.jpg
.jpeg
.png
.txt
.md
```

## 8. 用户确认触发条件

以下情况必须询问用户：

1. 无法判断文件属于哪个模块。
2. 合同相对方无法识别。
3. 劳动合同无法匹配员工。
4. 证照主体与企业名称不一致。
5. 章程版本顺序不清楚。
6. 用印事项是否属于重大事项无法判断。
7. OCR 结果影响日期、金额、主体、权限。
8. 是否创建飞书提醒需要确认。

## 9. 处理完成说明标准

每次导入完成后，必须输出：

```text
本次导入已完成。

已处理文件：
...

已生成或更新的台账：
...

已生成的记录文件：
...

已写入的提醒：
...

未能确认或需要补充的信息：
...

你下一步可以：
1. ...
2. ...
3. ...
```

不得只说“已完成”。

## 10. 本卷验收标准

1. 能创建完整企业本地目录。
2. 能为合同、员工、证照、印章、授权、提醒建立 CSV 台账。
3. 能为每个重要事项生成 Markdown 详情记录。
4. 能接收历史资料上传并转入对应模块。
5. 能标注读取方式、存疑项和用户确认事项。
6. 能把提醒先写入本地，再按配置决定是否同步飞书。
7. 能在每次处理完成后告诉用户文件和台账位置。
8. 任何旧版本资料不得被覆盖，只能新增版本或变更记录。
