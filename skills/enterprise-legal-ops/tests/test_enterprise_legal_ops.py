#!/usr/bin/env python3
"""Smoke tests for enterprise-legal-ops scripts."""

from __future__ import annotations

import csv
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
INIT = SKILL_DIR / "scripts" / "init_workspace.py"
REMINDERS = SKILL_DIR / "scripts" / "reminders.py"
QUERY = SKILL_DIR / "scripts" / "query_workspace.py"
IMPORT = SKILL_DIR / "scripts" / "import_document.py"
ROSTER = SKILL_DIR / "scripts" / "import_roster.py"
LEDGER = SKILL_DIR / "scripts" / "ledger.py"
ARCHIVE = SKILL_DIR / "scripts" / "archive_record.py"
REDLINE = SKILL_DIR / "scripts" / "contract_redline_review.py"
STRICT = SKILL_DIR / "scripts" / "strict_review_record.py"


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)


def assert_exists(path: Path) -> None:
    if not path.exists():
        raise AssertionError(f"missing: {path}")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> int:
    spec = importlib.util.spec_from_file_location("contract_redline_review", REDLINE)
    if spec is None or spec.loader is None:
        raise AssertionError("unable to load contract_redline_review.py")
    redline = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(redline)
    configured_engine = os.environ.get("LEGAL_CONTRACT_REVIEW_SKILL")
    if configured_engine:
        apply_script, qa_script = redline.find_existing_engine(SKILL_DIR)
        assert_exists(apply_script)
        assert_exists(qa_script)
    else:
        try:
            redline.find_existing_engine(SKILL_DIR)
        except SystemExit as exc:
            assert "LEGAL_CONTRACT_REVIEW_SKILL" in str(exc)
        else:
            raise AssertionError("redline wrapper should require external engine in standalone mode")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        company = "测试公司"
        workspace = root / company

        result = run([sys.executable, str(INIT), "--root", str(root), "--company", company])
        assert "企业法务运营工作区已初始化" in result.stdout

        required = [
            workspace / "_system" / "workspace-config.md",
            workspace / "01-合同管理" / "contracts.csv",
            workspace / "02-人力资源" / "employees.csv",
            workspace / "02-人力资源" / "annual-leave.csv",
            workspace / "02-人力资源" / "policies.csv",
            workspace / "03-公章证照" / "capital-contributions.csv",
            workspace / "04-提醒中心" / "reminders.csv",
            workspace / "05-本地问库" / "qa-log.md",
        ]
        for path in required:
            assert_exists(path)

        contracts_path = workspace / "01-合同管理" / "contracts.csv"
        with contracts_path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=read_csv_headers(contracts_path))
            writer.writerow({
                "contract_id": "服务合同-星河科技-001",
                "contract_name": "技术服务合同",
                "contract_type": "服务合同",
                "counterparty": "星河科技",
                "end_date": "2026-08-01",
                "status": "履行中",
                "original_file_path": "01-合同管理/服务合同-星河科技-001/01-原始文件/技术服务合同.docx",
                "record_md_path": "01-合同管理/服务合同-星河科技-001/03-合同记录/contract-record.md",
            })

        run([
            sys.executable, str(REMINDERS), "add",
            "--workspace", str(workspace),
            "--source-module", "合同",
            "--source-id", "服务合同-星河科技-001",
            "--reminder-type", "合同到期",
            "--title", "服务合同-星河科技-001 到期提醒",
            "--trigger-date", "2026-08-01",
            "--priority", "高",
        ])
        reminder_rows = read_csv(workspace / "04-提醒中心" / "reminders.csv")
        assert len(reminder_rows) == 1
        assert reminder_rows[0]["remind_date"] == "2026-07-02"
        assert reminder_rows[0]["feishu_status"] == "未启用"

        list_result = run([sys.executable, str(REMINDERS), "list", "--workspace", str(workspace), "--days", "999"])
        assert "服务合同-星河科技-001 到期提醒" in list_result.stdout

        reminder_id = reminder_rows[0]["reminder_id"]
        run([
            sys.executable, str(REMINDERS), "postpone",
            "--workspace", str(workspace),
            "--reminder-id", reminder_id,
            "--remind-date", "2026-07-10",
            "--note", "业务负责人要求延期",
        ])
        reminder_rows = read_csv(workspace / "04-提醒中心" / "reminders.csv")
        assert reminder_rows[0]["local_status"] == "已延期"
        assert reminder_rows[0]["remind_date"] == "2026-07-10"

        run([sys.executable, str(REMINDERS), "complete", "--workspace", str(workspace), "--reminder-id", reminder_id])
        reminder_rows = read_csv(workspace / "04-提醒中心" / "reminders.csv")
        assert reminder_rows[0]["local_status"] == "已完成"
        completed_rows = read_csv(workspace / "04-提醒中心" / "completed-reminders.csv")
        assert completed_rows[-1]["reminder_id"] == reminder_id

        run([
            sys.executable, str(REMINDERS), "add",
            "--workspace", str(workspace),
            "--source-module", "证照",
            "--source-id", "LIC-001",
            "--reminder-type", "证照到期",
            "--title", "营业执照到期提醒",
            "--trigger-date", "2026-11-30",
        ])
        license_reminder_id = read_csv(workspace / "04-提醒中心" / "reminders.csv")[-1]["reminder_id"]
        run([
            sys.executable, str(REMINDERS), "cancel",
            "--workspace", str(workspace),
            "--reminder-id", license_reminder_id,
            "--note", "证照已换发，取消旧提醒",
        ])
        reminder_rows = read_csv(workspace / "04-提醒中心" / "reminders.csv")
        assert reminder_rows[-1]["local_status"] == "已取消"

        summary_result = run([sys.executable, str(REMINDERS), "summary", "--workspace", str(workspace), "--days", "999"])
        assert "提醒摘要已生成" in summary_result.stdout
        assert_exists(workspace / "04-提醒中心" / "reminder-summary.md")

        sync_disabled = run([sys.executable, str(REMINDERS), "sync-feishu", "--workspace", str(workspace)])
        assert "飞书提醒未启用" in sync_disabled.stdout

        query_result = run([sys.executable, str(QUERY), "--workspace", str(workspace), "--query", "星河科技"])
        assert "查询结果" in query_result.stdout
        assert "contracts.csv" in query_result.stdout

        strict_result = run([sys.executable, str(QUERY), "--workspace", str(workspace), "--query", "这份合同能不能签"])
        assert "需要进入严审" in strict_result.stdout

        strict_record = run([
            sys.executable, str(STRICT),
            "--workspace", str(workspace),
            "--module", "合同",
            "--matter", "技术服务合同审查",
            "--goal", "判断是否可以签署并生成内部修订稿",
            "--stance", "我方为服务购买方",
            "--materials", str(contracts_path),
            "--verified-rules", "待联网核验",
            "--missing", "合同原文尚未进入正式严审",
            "--risks", "待审查",
            "--next-action", "读取合同并生成 Word 修订稿",
        ])
        assert "严审记录已创建" in strict_record.stdout
        strict_dir_line = [line for line in strict_record.stdout.splitlines() if line.startswith("严审目录：")][0]
        strict_dir = Path(strict_dir_line.split("：", 1)[1])
        assert_exists(strict_dir / "user-confirmation.md")
        assert_exists(strict_dir / "legal-verification-summary.md")
        assert_exists(strict_dir / "source-boundary.md")
        assert_exists(strict_dir / "risk-record.md")

        source_doc = root / "sample-contract.txt"
        source_doc.write_text("技术服务合同\n甲方：测试公司\n乙方：星河科技\n合同到期日：2026-08-01\n", encoding="utf-8")
        import_result = run([
            sys.executable, str(IMPORT),
            "--workspace", str(workspace),
            "--file", str(source_doc),
            "--module", "合同",
            "--object-id", "服务合同-星河科技-001",
        ])
        assert "文件已导入" in import_result.stdout
        assert "读取状态：成功" in import_result.stdout
        assert "读取复查摘要" in import_result.stdout
        assert "来源边界记录" in import_result.stdout
        imported_rows = read_csv(workspace / "_system" / "import-log.csv")
        assert imported_rows[-1]["module"] == "合同"
        text_index_rows = read_csv(workspace / "05-本地问库" / "extracted-text-index.csv")
        assert text_index_rows[-1]["read_status"] == "成功"
        assert "日期=" in text_index_rows[-1]["key_fields"]
        assert_exists(workspace / "_system" / "read-reviews" / f"{imported_rows[-1]['import_id']}-read-review-summary.md")

        image_doc = root / "scan.png"
        image_doc.write_bytes(b"not really an image")
        image_import = run([
            sys.executable, str(IMPORT),
            "--workspace", str(workspace),
            "--file", str(image_doc),
            "--module", "合同",
            "--object-id", "IMG-001",
        ])
        assert "读取状态：需处理" in image_import.stdout or "读取状态：失败" in image_import.stdout

        roster_csv = root / "roster.csv"
        roster_csv.write_text(
            "姓名,部门,岗位,入职日期,试用期结束日期,合同到期日,未休年假\n"
            "赵六,研发部,工程师,2026-01-01,2026-03-31,2026-12-31,3\n",
            encoding="utf-8",
        )
        roster_result = run([
            sys.executable, str(ROSTER),
            "--workspace", str(workspace),
            "--file", str(roster_csv),
            "--year", "2026",
        ])
        assert "员工花名册导入完成" in roster_result.stdout
        employee_rows = read_csv(workspace / "02-人力资源" / "employees.csv")
        zhao = [row for row in employee_rows if row["name"] == "赵六"][0]
        assert zhao["employee_id"].startswith("EMP-")
        assert_exists(Path(zhao["record_md_path"]))
        leave_rows = read_csv(workspace / "02-人力资源" / "annual-leave.csv")
        assert any(row["employee_name"] == "赵六" and row["remaining_annual_leave_days"] == "3" for row in leave_rows)
        reminder_rows = read_csv(workspace / "04-提醒中心" / "reminders.csv")
        assert any(row["source_id"] == zhao["employee_id"] and row["reminder_type"] == "劳动合同到期" for row in reminder_rows)

        archive_contract = run([
            sys.executable, str(ARCHIVE),
            "--workspace", str(workspace),
            "--kind", "contract",
            "--file", str(source_doc),
            "--set", "contract_id=服务合同-星河科技-002",
            "--set", "contract_name=技术服务合同",
            "--set", "contract_type=服务合同",
            "--set", "counterparty=星河科技",
            "--set", "end_date=2026-08-01",
            "--set", "status=履行中",
            "--reminder", "合同到期|2026-08-01|技术服务合同到期提醒|高",
        ])
        assert "业务记录已归档" in archive_contract.stdout
        contract_rows = read_csv(workspace / "01-合同管理" / "contracts.csv")
        archived_contract = [row for row in contract_rows if row["contract_id"] == "服务合同-星河科技-002"][0]
        assert archived_contract["record_md_path"].endswith("contract-record.md")
        assert_exists(Path(archived_contract["record_md_path"]))

        template_doc = root / "service-template.txt"
        template_doc.write_text("技术服务合同模板\n付款：待确认\n", encoding="utf-8")
        run([
            sys.executable, str(ARCHIVE),
            "--workspace", str(workspace),
            "--kind", "template",
            "--file", str(template_doc),
            "--set", "template_id=TPL-001",
            "--set", "template_name=技术服务合同模板",
            "--set", "contract_type=服务合同",
            "--set", "preferred_role=采购方",
            "--set", "applicable_scene=技术服务采购",
            "--set", "status=启用",
        ])
        template_rows = read_csv(workspace / "01-合同管理" / "模板库" / "template-index.csv")
        assert any(row["template_id"] == "TPL-001" for row in template_rows)

        policy_doc = root / "attendance-policy.txt"
        policy_doc.write_text("考勤制度\n迟到扣款规则待审查\n", encoding="utf-8")
        run([
            sys.executable, str(ARCHIVE),
            "--workspace", str(workspace),
            "--kind", "policy",
            "--file", str(policy_doc),
            "--set", "policy_id=POL-001",
            "--set", "policy_name=考勤制度",
            "--set", "policy_type=考勤制度",
            "--set", "effective_date=2026-01-01",
            "--set", "scope=全体员工",
            "--set", "legality_review_status=待完成",
            "--set", "conflict_check_status=待完成",
            "--reminder", "旧制度合法性审查待完成||考勤制度合法性审查待完成|高",
        ])
        policy_rows = read_csv(workspace / "02-人力资源" / "policies.csv")
        assert any(row["policy_id"] == "POL-001" for row in policy_rows)
        assert_exists(workspace / "02-人力资源" / "制度文件" / "制度冲突检查记录" / "POL-001-conflict-check.md")
        assert_exists(workspace / "02-人力资源" / "制度文件" / "制度合法性审查记录" / "POL-001-legality-review.md")

        license_doc = root / "license.txt"
        license_doc.write_text("营业执照\n主体：测试公司\n有效期至：2026-11-30\n", encoding="utf-8")
        archive_license = run([
            sys.executable, str(ARCHIVE),
            "--workspace", str(workspace),
            "--kind", "license",
            "--file", str(license_doc),
            "--set", "license_id=LIC-001",
            "--set", "license_name=营业执照",
            "--set", "license_type=营业执照",
            "--set", "holder=测试公司",
            "--set", "expiry_date=2026-11-30",
            "--set", "status=有效",
            "--reminder", "证照到期|2026-11-30|营业执照到期提醒|高",
        ])
        assert "业务记录已归档" in archive_license.stdout
        license_rows = read_csv(workspace / "03-公章证照" / "licenses.csv")
        assert any(row["license_id"] == "LIC-001" for row in license_rows)

        articles_doc = root / "articles.txt"
        articles_doc.write_text("公司章程\n对外担保由股东会决议。\n", encoding="utf-8")
        run([
            sys.executable, str(ARCHIVE),
            "--workspace", str(workspace),
            "--kind", "governance",
            "--file", str(articles_doc),
            "--set", "governance_doc_id=GOV-001",
            "--set", "doc_name=公司章程",
            "--set", "doc_type=公司章程",
            "--set", "company_name=测试公司",
            "--set", "status=现行有效待复核",
        ])
        governance_rows = read_csv(workspace / "03-公章证照" / "governance-documents.csv")
        governance_record = [row for row in governance_rows if row["governance_doc_id"] == "GOV-001"][0]
        assert_exists(Path(governance_record["record_md_path"]).parent / "authority-summary.md")

        run([
            sys.executable, str(ARCHIVE),
            "--workspace", str(workspace),
            "--kind", "capital",
            "--set", "contribution_id=CAP-002",
            "--set", "shareholder_name=王五",
            "--set", "shareholder_type=自然人",
            "--set", "subscribed_amount=500000",
            "--set", "paid_amount=0",
            "--set", "subscription_deadline=2026-09-30",
            "--set", "status=临近到期",
            "--reminder", "股东出资到期|2026-09-30|王五认缴出资到期提醒|高",
        ])
        capital_rows = read_csv(workspace / "03-公章证照" / "capital-contributions.csv")
        assert any(row["contribution_id"] == "CAP-002" for row in capital_rows)
        assert_exists(workspace / "03-公章证照" / "章程合伙协议" / "出资信息比对记录.md")

        source_map_rows = read_csv(workspace / "05-本地问库" / "source-map.csv")
        assert any(row["object_id"] == "服务合同-星河科技-002" for row in source_map_rows)

        run([
            sys.executable, str(LEDGER), "upsert",
            "--workspace", str(workspace),
            "--ledger", "employee",
            "--set", "employee_id=EMP-001",
            "--set", "name=张三",
            "--set", "contract_end_date=2026-12-31",
        ])
        employee_rows = read_csv(workspace / "02-人力资源" / "employees.csv")
        assert any(row["employee_id"] == "EMP-001" for row in employee_rows)

        run([
            sys.executable, str(LEDGER), "upsert",
            "--workspace", str(workspace),
            "--ledger", "annual_leave",
            "--set", "leave_record_id=AL-001",
            "--set", "employee_id=EMP-001",
            "--set", "employee_name=张三",
            "--set", "year=2026",
            "--set", "remaining_annual_leave_days=5",
        ])
        leave_rows = read_csv(workspace / "02-人力资源" / "annual-leave.csv")
        assert leave_rows[-1]["remaining_annual_leave_days"] == "5"

        run([
            sys.executable, str(LEDGER), "upsert",
            "--workspace", str(workspace),
            "--ledger", "capital",
            "--set", "contribution_id=CAP-001",
            "--set", "shareholder_name=李四",
            "--set", "subscribed_amount=1000000",
            "--set", "subscription_deadline=2026-09-30",
            "--set", "status=临近到期",
        ])
        capital_rows = read_csv(workspace / "03-公章证照" / "capital-contributions.csv")
        assert capital_rows[-1]["shareholder_name"] == "李四"

        ledger_list = run([
            sys.executable, str(LEDGER), "list",
            "--workspace", str(workspace),
            "--ledger", "capital",
            "--query", "李四",
        ])
        assert "CAP-001" in ledger_list.stdout

        if shutil.which("lark-cli"):
            # Dry-run proves the command path without writing to Feishu.
            config = workspace / "04-提醒中心" / "feishu-config.md"
            config.write_text("# 飞书提醒配置\n\n- 是否启用飞书提醒：是\n- 默认日历：primary\n", encoding="utf-8")
            dry_run = run([
                sys.executable, str(REMINDERS), "sync-feishu",
                "--workspace", str(workspace),
                "--force",
                "--dry-run",
            ])
            assert "飞书提醒同步处理完成" in dry_run.stdout

    print("enterprise-legal-ops smoke tests passed")
    return 0


def read_csv_headers(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        return next(reader)


if __name__ == "__main__":
    raise SystemExit(main())
