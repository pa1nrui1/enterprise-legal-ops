#!/usr/bin/env python3
"""Initialize an Enterprise Legal Ops company workspace."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path


CSV_HEADERS = {
    "01-合同管理/contracts.csv": [
        "contract_id", "contract_name", "contract_type", "our_party", "our_role",
        "counterparty", "review_position", "amount", "effective_date", "end_date",
        "auto_renewal", "notice_days", "latest_notice_date", "status",
        "original_file_path", "record_md_path", "latest_review_date", "risk_level",
        "next_action", "created_at", "updated_at",
    ],
    "01-合同管理/contract-reminders.csv": [
        "reminder_id", "source_module", "source_id", "reminder_type", "title",
        "trigger_date", "remind_date", "status", "created_at", "updated_at",
    ],
    "01-合同管理/模板库/template-index.csv": [
        "template_id", "template_name", "contract_type", "preferred_role",
        "applicable_scene", "source_file_path", "record_md_path", "last_used_at",
        "status", "created_at", "updated_at",
    ],
    "02-人力资源/employees.csv": [
        "employee_id", "name", "department", "position", "employment_status",
        "entry_date", "probation_end_date", "contract_start_date", "contract_end_date",
        "work_location", "working_hours_system", "salary_structure",
        "social_insurance_status", "contract_file_path", "record_md_path",
        "risk_flags", "next_action", "created_at", "updated_at",
    ],
    "02-人力资源/employment-contracts.csv": [
        "employment_contract_id", "employee_id", "employee_name", "contract_type",
        "contract_start_date", "contract_end_date", "probation_end_date", "position",
        "work_location", "salary_terms", "working_hours_system", "renewal_status",
        "contract_file_path", "record_md_path", "read_status", "risk_flags",
        "created_at", "updated_at",
    ],
    "02-人力资源/annual-leave.csv": [
        "leave_record_id", "employee_id", "employee_name", "year", "entry_date",
        "continuous_work_years", "statutory_annual_leave_days",
        "company_annual_leave_days", "used_annual_leave_days",
        "remaining_annual_leave_days", "carryover_rule", "expiry_date",
        "compensation_required", "compensation_amount", "calculation_basis",
        "source_file_path", "record_md_path", "risk_flags", "created_at", "updated_at",
    ],
    "02-人力资源/policies.csv": [
        "policy_id", "policy_name", "policy_type", "version_date", "effective_date",
        "scope", "source_file_path", "record_md_path", "publicity_status",
        "democratic_procedure_status", "employee_receipt_status",
        "legality_review_status", "conflict_check_status", "risk_flags",
        "next_action", "created_at", "updated_at",
    ],
    "02-人力资源/hr-reminders.csv": [
        "reminder_id", "source_module", "source_id", "reminder_type", "title",
        "trigger_date", "remind_date", "status", "created_at", "updated_at",
    ],
    "03-公章证照/licenses.csv": [
        "license_id", "license_name", "license_type", "holder", "license_number",
        "issue_authority", "issue_date", "expiry_date", "annual_check_required",
        "annual_check_deadline", "file_path", "record_md_path", "status",
        "risk_flags", "next_action", "created_at", "updated_at",
    ],
    "03-公章证照/seals.csv": [
        "seal_id", "seal_name", "seal_type", "custodian", "authorized_scope",
        "approval_rule", "storage_location", "status", "record_md_path",
        "created_at", "updated_at",
    ],
    "03-公章证照/authorizations.csv": [
        "authorization_id", "authorization_name", "grantor", "grantee", "scope",
        "start_date", "end_date", "revocation_status", "file_path", "record_md_path",
        "risk_flags", "created_at", "updated_at",
    ],
    "03-公章证照/seal-use.csv": [
        "seal_use_id", "seal_id", "document_name", "document_type", "purpose",
        "applicant", "approver", "use_date", "counterparty", "amount",
        "high_risk_type", "authority_check_status", "governance_basis", "file_path",
        "record_md_path", "next_action", "created_at", "updated_at",
    ],
    "03-公章证照/governance-documents.csv": [
        "governance_doc_id", "doc_name", "doc_type", "version_date", "effective_date",
        "company_name", "key_authority_summary", "file_path", "record_md_path",
        "status", "created_at", "updated_at",
    ],
    "03-公章证照/authority-checks.csv": [
        "authority_check_id", "matter_name", "matter_type", "related_file_path",
        "amount", "counterparty", "governance_basis", "required_approval",
        "existing_approval", "conclusion", "risk_flags", "record_md_path",
        "created_at", "updated_at",
    ],
    "03-公章证照/capital-contributions.csv": [
        "contribution_id", "shareholder_name", "shareholder_type", "subscribed_amount",
        "paid_amount", "unpaid_amount", "contribution_method", "subscription_deadline",
        "paid_date", "equity_ratio", "source_document", "source_file_path",
        "proof_file_path", "status", "risk_flags", "next_action", "created_at",
        "updated_at",
    ],
    "04-提醒中心/reminders.csv": [
        "reminder_id", "source_module", "source_id", "reminder_type", "title",
        "description", "trigger_date", "advance_days", "remind_date", "priority",
        "local_status", "feishu_enabled", "feishu_status", "feishu_event_id",
        "source_file_path", "record_md_path", "owner", "next_action", "created_at",
        "updated_at",
    ],
    "04-提醒中心/completed-reminders.csv": [
        "reminder_id", "completed_at", "completion_note",
    ],
    "05-本地问库/source-map.csv": [
        "source_id", "module", "object_id", "object_name", "csv_path", "md_path",
        "extracted_text_path", "original_file_path", "last_updated_at",
    ],
    "05-本地问库/extracted-text-index.csv": [
        "text_id", "module", "object_id", "source_file_path", "extracted_text_path",
        "read_method", "read_status", "ocr_status", "key_fields", "created_at",
        "updated_at",
    ],
    "_system/import-log.csv": [
        "import_id", "file_path", "module", "status", "notes", "created_at",
    ],
}


DIRS = [
    "00-企业基础档案",
    "01-合同管理/模板库",
    "02-人力资源/员工记录",
    "02-人力资源/制度文件/员工手册",
    "02-人力资源/制度文件/薪酬制度",
    "02-人力资源/制度文件/考勤制度",
    "02-人力资源/制度文件/绩效制度",
    "02-人力资源/制度文件/奖惩制度",
    "02-人力资源/制度文件/年休假制度",
    "02-人力资源/制度文件/制度冲突检查记录",
    "02-人力资源/制度文件/制度合法性审查记录",
    "02-人力资源/导入记录",
    "02-人力资源/输出文件",
    "03-公章证照/证照文件",
    "03-公章证照/印章资料",
    "03-公章证照/授权文件",
    "03-公章证照/用印记录",
    "03-公章证照/章程合伙协议",
    "03-公章证照/决议文件",
    "03-公章证照/权限校验记录",
    "03-公章证照/输出文件",
    "04-提醒中心/failed-sync",
    "05-本地问库",
    "06-导入暂存/待识别",
    "06-导入暂存/读取失败",
    "06-导入暂存/待用户确认",
    "06-导入暂存/已归档记录",
    "07-输出文件",
    "_system",
]


MD_FILES = {
    "00-企业基础档案/company-profile.md": "# 公司基础信息\n\n- 企业名称：{company}\n- 统一社会信用代码：\n- 企业所在地：\n- 主要经营地区：\n- 创建时间：{now}\n",
    "00-企业基础档案/governance-summary.md": "# 企业治理摘要\n\n- 当前章程：待上传\n- 当前合伙协议：不适用/待确认\n- 权限摘要：待生成\n",
    "00-企业基础档案/articles-change-log.md": "# 章程/合伙协议变更记录\n\n",
    "00-企业基础档案/authority-matrix.md": "# 权限矩阵\n\n- 对外担保：待读取章程\n- 借款融资：待读取章程\n- 重大合同：待读取章程\n- 用印审批：待读取制度\n",
    "02-人力资源/制度文件/制度索引.md": "# 制度索引\n\n",
    "04-提醒中心/reminder-summary.md": "# 提醒摘要\n\n",
    "04-提醒中心/feishu-config.md": "# 飞书提醒配置\n\n- 是否启用飞书提醒：否\n- 默认日历：\n- 默认提醒提前天数：\n- 是否自动创建飞书日历：否\n- 同步失败是否保留本地提醒：是\n- 最近配置时间：{now}\n",
    "04-提醒中心/feishu-sync-log.md": "# 飞书同步记录\n\n",
    "05-本地问库/search-index.md": "# 本地问库索引\n\n",
    "05-本地问库/qa-log.md": "# 问答日志\n\n",
    "05-本地问库/query-routing-log.md": "# 查询路由日志\n\n",
    "05-本地问库/unresolved-queries.md": "# 未解决查询\n\n",
    "_system/current-company.md": "# 当前企业\n\n- 企业名称：{company}\n- 企业工作区：{workspace}\n- 最近更新时间：{now}\n",
    "_system/workspace-config.md": "# 工作区配置\n\n- 企业名称：{company}\n- 工作区根目录：{root}\n- 企业工作区：{workspace}\n- 创建时间：{now}\n- 最后更新时间：{now}\n- 是否启用飞书提醒：否\n",
    "_system/read-review-log.md": "# 读取复查记录\n\n",
    "_system/legal-verification-log.md": "# 法规/规则核验记录\n\n",
    "_system/source-boundary-log.md": "# 来源边界记录\n\n",
    "_system/user-confirmation-log.md": "# 用户确认记录\n\n",
    "_system/error-log.md": "# 错误记录\n\n",
}


def write_csv_if_missing(path: Path, headers: list[str]) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)


def write_text_if_missing(path: Path, text: str) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize an Enterprise Legal Ops workspace.")
    parser.add_argument("--root", required=True, help="Workspace root chosen by the user.")
    parser.add_argument("--company", required=True, help="Company name or confirmed short name.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    company = args.company.strip()
    if not company:
        raise SystemExit("--company cannot be empty")

    workspace = root / company
    now = datetime.now().isoformat(timespec="seconds")

    for rel in DIRS:
        (workspace / rel).mkdir(parents=True, exist_ok=True)

    for rel, headers in CSV_HEADERS.items():
        write_csv_if_missing(workspace / rel, headers)

    for rel, template in MD_FILES.items():
        write_text_if_missing(
            workspace / rel,
            template.format(company=company, root=root, workspace=workspace, now=now),
        )

    print("企业法务运营工作区已初始化。")
    print(f"企业名称：{company}")
    print(f"企业工作区：{workspace}")
    print(f"配置文件：{workspace / '_system' / 'workspace-config.md'}")
    print(f"合同台账：{workspace / '01-合同管理' / 'contracts.csv'}")
    print(f"员工台账：{workspace / '02-人力资源' / 'employees.csv'}")
    print(f"提醒台账：{workspace / '04-提醒中心' / 'reminders.csv'}")
    print("下一步可以上传合同、员工花名册、章程、证照或授权文件。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
