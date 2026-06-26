#!/usr/bin/env python3
"""Archive Enterprise Legal Ops business records.

This script handles the deterministic part of the product workflow:
copy source files without overwrite, upsert the right CSV ledger, create a
Markdown record, update source-map, and optionally create local reminders.
Substantive legal judgment remains in the strict-review workflow.
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


KIND_SPECS = {
    "contract": {
        "ledger": "01-合同管理/contracts.csv",
        "id": "contract_id",
        "name": "contract_name",
        "module": "合同",
        "folder": "01-合同管理/{id}-{name}",
        "source_dir": "01-原始文件",
        "record": "03-合同记录/contract-record.md",
        "title": "合同详情记录",
        "ledger_path_field": "original_file_path",
        "record_path_field": "record_md_path",
    },
    "employee": {
        "ledger": "02-人力资源/employees.csv",
        "id": "employee_id",
        "name": "name",
        "module": "HR",
        "folder": "02-人力资源/员工记录/{id}-{name}",
        "source_dir": "来源文件",
        "record": "employee-record.md",
        "title": "员工个人记录",
        "ledger_path_field": "contract_file_path",
        "record_path_field": "record_md_path",
    },
    "employment_contract": {
        "ledger": "02-人力资源/employment-contracts.csv",
        "id": "employment_contract_id",
        "name": "employee_name",
        "module": "HR",
        "folder": "02-人力资源/劳动合同/{id}-{name}",
        "source_dir": "01-原始文件",
        "record": "employment-contract-record.md",
        "title": "劳动合同记录",
        "ledger_path_field": "contract_file_path",
        "record_path_field": "record_md_path",
    },
    "template": {
        "ledger": "01-合同管理/模板库/template-index.csv",
        "id": "template_id",
        "name": "template_name",
        "module": "合同",
        "folder": "01-合同管理/模板库/{id}-{name}",
        "source_dir": "01-原始文件",
        "record": "template-record.md",
        "title": "合同模板记录",
        "ledger_path_field": "source_file_path",
        "record_path_field": "record_md_path",
    },
    "policy": {
        "ledger": "02-人力资源/policies.csv",
        "id": "policy_id",
        "name": "policy_name",
        "module": "HR",
        "folder": "02-人力资源/制度文件/{policy_type}/{id}-{name}",
        "source_dir": "01-原始文件",
        "record": "policy-record.md",
        "title": "劳动制度记录",
        "ledger_path_field": "source_file_path",
        "record_path_field": "record_md_path",
    },
    "annual_leave": {
        "ledger": "02-人力资源/annual-leave.csv",
        "id": "leave_record_id",
        "name": "employee_name",
        "module": "HR",
        "folder": "02-人力资源/员工记录/{employee_id}-{name}/年假记录",
        "source_dir": "来源文件",
        "record": "annual-leave-record.md",
        "title": "未休年假记录",
        "ledger_path_field": "source_file_path",
        "record_path_field": "record_md_path",
    },
    "license": {
        "ledger": "03-公章证照/licenses.csv",
        "id": "license_id",
        "name": "license_name",
        "module": "公章证照",
        "folder": "03-公章证照/证照文件/{id}-{name}",
        "source_dir": "01-原始文件",
        "record": "license-record.md",
        "title": "证照记录",
        "ledger_path_field": "file_path",
        "record_path_field": "record_md_path",
    },
    "seal": {
        "ledger": "03-公章证照/seals.csv",
        "id": "seal_id",
        "name": "seal_name",
        "module": "公章证照",
        "folder": "03-公章证照/印章资料/{id}-{name}",
        "source_dir": "来源文件",
        "record": "seal-record.md",
        "title": "印章记录",
        "ledger_path_field": "",
        "record_path_field": "record_md_path",
    },
    "authorization": {
        "ledger": "03-公章证照/authorizations.csv",
        "id": "authorization_id",
        "name": "authorization_name",
        "module": "公章证照",
        "folder": "03-公章证照/授权文件/{id}-{name}",
        "source_dir": "01-原始文件",
        "record": "authorization-record.md",
        "title": "授权文件记录",
        "ledger_path_field": "file_path",
        "record_path_field": "record_md_path",
    },
    "seal_use": {
        "ledger": "03-公章证照/seal-use.csv",
        "id": "seal_use_id",
        "name": "document_name",
        "module": "公章证照",
        "folder": "03-公章证照/用印记录/{id}-{name}",
        "source_dir": "01-原始文件",
        "record": "seal-use-record.md",
        "title": "用印记录",
        "ledger_path_field": "file_path",
        "record_path_field": "record_md_path",
    },
    "governance": {
        "ledger": "03-公章证照/governance-documents.csv",
        "id": "governance_doc_id",
        "name": "doc_name",
        "module": "公章证照",
        "folder": "03-公章证照/章程合伙协议/{id}-{name}",
        "source_dir": "01-原始文件",
        "record": "governance-record.md",
        "title": "治理文件记录",
        "ledger_path_field": "file_path",
        "record_path_field": "record_md_path",
    },
    "authority_check": {
        "ledger": "03-公章证照/authority-checks.csv",
        "id": "authority_check_id",
        "name": "matter_name",
        "module": "公章证照",
        "folder": "03-公章证照/权限校验记录/{id}-{name}",
        "source_dir": "来源文件",
        "record": "authority-check-record.md",
        "title": "权限校验记录",
        "ledger_path_field": "related_file_path",
        "record_path_field": "record_md_path",
    },
    "capital": {
        "ledger": "03-公章证照/capital-contributions.csv",
        "id": "contribution_id",
        "name": "shareholder_name",
        "module": "公章证照",
        "folder": "03-公章证照/章程合伙协议/股东出资/{id}-{name}",
        "source_dir": "来源文件",
        "record": "capital-contribution-record.md",
        "title": "股东出资记录",
        "ledger_path_field": "source_file_path",
        "record_path_field": "",
    },
}


def safe_segment(value: str) -> str:
    value = value.strip() or "未命名"
    value = re.sub(r'[<>:"/\\|?*\n\r\t]+', "-", value)
    value = re.sub(r"\s+", " ", value)
    return value[:80]


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    idx = 2
    while True:
        candidate = parent / f"{stem}-v{idx}{suffix}"
        if not candidate.exists():
            return candidate
        idx += 1


def parse_values(values: list[str]) -> dict[str, str]:
    data: dict[str, str] = {}
    for item in values:
        if "=" not in item:
            raise SystemExit(f"invalid --set value, expected key=value: {item}")
        key, value = item.split("=", 1)
        data[key.strip()] = value.strip()
    return data


def read_headers(path: Path) -> list[str]:
    if not path.exists():
        raise SystemExit(f"ledger not found; initialize workspace first: {path}")
    with path.open(newline="", encoding="utf-8") as f:
        return next(csv.reader(f))


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_rows(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def append_source_map(workspace: Path, row: dict[str, str]) -> None:
    path = workspace / "05-本地问库" / "source-map.csv"
    headers = [
        "source_id", "module", "object_id", "object_name", "csv_path", "md_path",
        "extracted_text_path", "original_file_path", "last_updated_at",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    if path.exists():
        with path.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    rows = [existing for existing in rows if existing.get("source_id") != row["source_id"]]
    rows.append(row)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def update_ledger(path: Path, data: dict[str, str], id_field: str) -> None:
    headers = read_headers(path)
    unknown = sorted(set(data) - set(headers))
    if unknown:
        raise SystemExit(f"unknown fields for {path.name}: {', '.join(unknown)}")
    rows = read_rows(path)
    record_id = data[id_field]
    matched = False
    for row in rows:
        if row.get(id_field) == record_id:
            row.update(data)
            matched = True
            break
    if not matched:
        row = {header: "" for header in headers}
        row.update(data)
        rows.append(row)
    write_rows(path, headers, rows)


def ensure_policy_ledger(path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = [
        "policy_id", "policy_name", "policy_type", "version_date", "effective_date",
        "scope", "source_file_path", "record_md_path", "publicity_status",
        "democratic_procedure_status", "employee_receipt_status",
        "legality_review_status", "conflict_check_status", "risk_flags",
        "next_action", "created_at", "updated_at",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=headers).writeheader()


def append_policy_index(workspace: Path, data: dict[str, str], record_path: Path) -> None:
    index = workspace / "02-人力资源" / "制度文件" / "制度索引.md"
    index.parent.mkdir(parents=True, exist_ok=True)
    if not index.exists():
        index.write_text("# 制度索引\n\n", encoding="utf-8")
    with index.open("a", encoding="utf-8") as f:
        f.write(f"## {data.get('policy_name', '')}\n\n")
        f.write(f"- 制度编号：{data.get('policy_id', '')}\n")
        f.write(f"- 制度类型：{data.get('policy_type', '')}\n")
        f.write(f"- 版本日期：{data.get('version_date', '待确认')}\n")
        f.write(f"- 生效日期：{data.get('effective_date', '待确认')}\n")
        f.write(f"- 适用范围：{data.get('scope', '待确认')}\n")
        f.write(f"- 原始文件：{data.get('source_file_path', '待上传')}\n")
        f.write(f"- 记录文件：{record_path}\n")
        f.write(f"- 程序事项：{data.get('next_action', '需核对民主程序、公示、签收、培训材料')}\n")
        f.write(f"- 合法性审查：{data.get('legality_review_status', '待完成')}\n")
        f.write(f"- 冲突检查：{data.get('conflict_check_status', '待完成')}\n\n")


def create_policy_review_placeholders(workspace: Path, data: dict[str, str]) -> None:
    policy_id = data.get("policy_id", "POLICY")
    policy_name = data.get("policy_name", "制度")
    conflict_dir = workspace / "02-人力资源" / "制度文件" / "制度冲突检查记录"
    legality_dir = workspace / "02-人力资源" / "制度文件" / "制度合法性审查记录"
    conflict_dir.mkdir(parents=True, exist_ok=True)
    legality_dir.mkdir(parents=True, exist_ok=True)
    (conflict_dir / f"{policy_id}-conflict-check.md").write_text(
        "\n".join([
            "# 制度冲突检查记录",
            "",
            f"- 制度：{policy_name}",
            "- 状态：待完成",
            "- 要求：比对现行员工手册、劳动合同模板、薪酬、考勤、绩效、奖惩、加班、请休假、年休假、离职交接、调岗制度。",
            "- 输出：具体冲突条款、冲突影响、处理建议、需废止或同步修改的旧制度。",
            "",
        ]),
        encoding="utf-8",
    )
    (legality_dir / f"{policy_id}-legality-review.md").write_text(
        "\n".join([
            "# 制度合法性审查记录",
            "",
            f"- 制度：{policy_name}",
            "- 状态：待完成",
            "- 要求：检查工资扣款、加班审批和加班费、罚款扣工资、绩效淘汰、调岗降薪、试用期、竞业限制、休假、解除条件、最终解释权、民主程序、公示签收。",
            "- 注意：引用法律法规或地方规则前必须核验。",
            "",
        ]),
        encoding="utf-8",
    )


def make_record_text(title: str, data: dict[str, str], source_file: str, ledger: Path, reminders: list[str]) -> str:
    now = datetime.now().isoformat(timespec="seconds")
    lines = [
        f"# {title}",
        "",
        "## 基础信息",
        f"- 生成时间：{now}",
    ]
    for key, value in data.items():
        if value:
            lines.append(f"- {key}：{value}")
    lines.extend([
        "",
        "## 文件位置",
        f"- 原始文件：{source_file or '无/待上传'}",
        f"- 台账位置：{ledger}",
        "",
        "## 关键摘要",
        "- 待由严审或人工复核补充。",
        "",
        "## 风险提示",
        "- 本记录为企业内部管理记录；涉及法律、权限、金额或日期判断时必须进入严审。",
        "",
        "## 提醒事项",
    ])
    if reminders:
        lines.extend(f"- {item}" for item in reminders)
    else:
        lines.append("- 暂无新增提醒。")
    lines.extend([
        "",
        "## 来源边界",
        "- 本记录来自用户提供字段和已归档文件路径。",
        "- 未读取或未核验的事实不得作为确定法律结论。",
        "",
        "## 下一步",
        "- 核对关键字段。",
        "- 如涉及合同审查、制度合法性、章程权限或用印判断，进入严审流程。",
        "",
    ])
    return "\n".join(lines)


def create_reminder(workspace: Path, args: argparse.Namespace, record_id: str, record_path: Path, source_file: str) -> list[str]:
    created: list[str] = []
    for item in args.reminder:
        parts = item.split("|")
        if len(parts) < 3:
            raise SystemExit("--reminder must be type|trigger_date|title[|priority]")
        reminder_type, trigger_date, title = parts[:3]
        priority = parts[3] if len(parts) > 3 else "中"
        cmd = [
            sys.executable,
            str(Path(__file__).resolve().with_name("reminders.py")),
            "add",
            "--workspace", str(workspace),
            "--source-module", args.kind,
            "--source-id", record_id,
            "--reminder-type", reminder_type,
            "--title", title,
            "--trigger-date", trigger_date,
            "--priority", priority,
            "--source-file-path", source_file,
            "--record-md-path", str(record_path),
        ]
        if args.feishu_enabled:
            cmd.append("--feishu-enabled")
        proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode != 0:
            raise SystemExit(proc.stderr or proc.stdout)
        created.append(f"{reminder_type}｜{trigger_date}｜{title}")
    return created


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive a business record into an Enterprise Legal Ops workspace.")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--kind", required=True, choices=sorted(KIND_SPECS))
    parser.add_argument("--file", action="append", default=[], help="source file to copy; repeatable")
    parser.add_argument("--set", action="append", default=[], help="ledger field=value; repeatable")
    parser.add_argument("--reminder", action="append", default=[], help="type|trigger_date|title[|priority]; repeatable")
    parser.add_argument("--feishu-enabled", action="store_true")
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    spec = KIND_SPECS[args.kind]
    data = parse_values(args.set)
    id_field = spec["id"]
    name_field = spec["name"]
    if id_field not in data or not data[id_field]:
        raise SystemExit(f"missing required field: {id_field}")
    if name_field not in data or not data[name_field]:
        raise SystemExit(f"missing required field: {name_field}")

    now = datetime.now().isoformat(timespec="seconds")
    data.setdefault("created_at", now)
    data["updated_at"] = now
    record_id = data[id_field]
    record_name = data[name_field]
    folder_rel = spec["folder"].format(
        id=safe_segment(record_id),
        name=safe_segment(record_name),
        employee_id=safe_segment(data.get("employee_id", record_id)),
        policy_type=safe_segment(data.get("policy_type", "其他制度")),
    )
    folder = workspace / folder_rel
    source_dir = folder / spec["source_dir"]
    source_dir.mkdir(parents=True, exist_ok=True)

    copied_files = []
    for raw in args.file:
        src = Path(raw).expanduser().resolve()
        if not src.exists():
            raise SystemExit(f"source file not found: {src}")
        dest = unique_path(source_dir / src.name)
        shutil.copy2(src, dest)
        copied_files.append(dest)

    source_file = str(copied_files[0]) if copied_files else data.get(spec["ledger_path_field"], "")
    if spec["ledger_path_field"] and source_file:
        data[spec["ledger_path_field"]] = source_file

    record_path = folder / spec["record"]
    if spec["record_path_field"]:
        data[spec["record_path_field"]] = str(record_path)

    ledger_path = workspace / spec["ledger"]
    if args.kind == "policy":
        ensure_policy_ledger(ledger_path)
    reminders = create_reminder(workspace, args, record_id, record_path, source_file)
    update_ledger(ledger_path, data, id_field)
    record_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.write_text(make_record_text(spec["title"], data, source_file, ledger_path, reminders), encoding="utf-8")
    append_source_map(workspace, {
        "source_id": f"{args.kind}:{record_id}",
        "module": spec["module"],
        "object_id": record_id,
        "object_name": record_name,
        "csv_path": str(ledger_path),
        "md_path": str(record_path),
        "extracted_text_path": "",
        "original_file_path": source_file,
        "last_updated_at": now,
    })

    if args.kind == "governance":
        authority = folder / "authority-summary.md"
        if not authority.exists():
            authority.write_text("# 权限摘要\n\n- 待读取章程或合伙协议后补充。\n", encoding="utf-8")
    if args.kind == "capital":
        compare = workspace / "03-公章证照" / "章程合伙协议" / "出资信息比对记录.md"
        compare.parent.mkdir(parents=True, exist_ok=True)
        if not compare.exists():
            compare.write_text("# 出资信息比对记录\n\n", encoding="utf-8")
    if args.kind == "policy":
        append_policy_index(workspace, data, record_path)
        create_policy_review_placeholders(workspace, data)

    print("业务记录已归档。")
    print(f"记录类型：{args.kind}")
    print(f"记录编号：{record_id}")
    if copied_files:
        print("原始文件位置：")
        for path in copied_files:
            print(f"- {path}")
    else:
        print("原始文件位置：无/待上传")
    print(f"台账位置：{ledger_path}")
    print(f"Markdown 记录：{record_path}")
    print(f"来源映射：{workspace / '05-本地问库' / 'source-map.csv'}")
    print(f"新增提醒：{len(reminders)}")
    print("下一步：核对关键字段；涉及法律、权限或风险判断时进入严审流程。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
