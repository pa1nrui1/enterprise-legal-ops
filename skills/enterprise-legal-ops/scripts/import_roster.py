#!/usr/bin/env python3
"""Import employee rosters into Enterprise Legal Ops."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


EMPLOYEE_HEADERS = [
    "employee_id", "name", "department", "position", "employment_status",
    "entry_date", "probation_end_date", "contract_start_date", "contract_end_date",
    "work_location", "working_hours_system", "salary_structure",
    "social_insurance_status", "contract_file_path", "record_md_path",
    "risk_flags", "next_action", "created_at", "updated_at",
]

LEAVE_HEADERS = [
    "leave_record_id", "employee_id", "employee_name", "year", "entry_date",
    "continuous_work_years", "statutory_annual_leave_days",
    "company_annual_leave_days", "used_annual_leave_days",
    "remaining_annual_leave_days", "carryover_rule", "expiry_date",
    "compensation_required", "compensation_amount", "calculation_basis",
    "source_file_path", "record_md_path", "risk_flags", "created_at", "updated_at",
]

FIELD_ALIASES = {
    "employee_id": ["员工编号", "工号", "编号", "employee_id"],
    "name": ["姓名", "员工姓名", "name"],
    "department": ["部门", "所属部门", "department"],
    "position": ["岗位", "职位", "职务", "position"],
    "employment_status": ["状态", "在职状态", "employment_status"],
    "entry_date": ["入职日期", "入职时间", "entry_date"],
    "probation_end_date": ["试用期结束", "试用期结束日期", "probation_end_date"],
    "contract_start_date": ["合同开始", "合同起始日期", "劳动合同开始日期", "contract_start_date"],
    "contract_end_date": ["合同结束", "合同到期日", "劳动合同结束日期", "contract_end_date"],
    "work_location": ["工作地点", "履行地", "work_location"],
    "working_hours_system": ["工时制度", "working_hours_system"],
    "salary_structure": ["工资结构", "薪酬结构", "salary_structure"],
    "social_insurance_status": ["社保", "社保状态", "social_insurance_status"],
    "used_annual_leave_days": ["已休年假", "已休年休假", "used_annual_leave_days"],
    "remaining_annual_leave_days": ["剩余年假", "未休年假", "remaining_annual_leave_days"],
}


def normalize_header(value: str) -> str:
    return re.sub(r"\s+", "", value.strip().lower())


def map_headers(headers: list[str]) -> dict[str, int]:
    normalized = {normalize_header(header): idx for idx, header in enumerate(headers)}
    mapping: dict[str, int] = {}
    for field, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            key = normalize_header(alias)
            if key in normalized:
                mapping[field] = normalized[key]
                break
    return mapping


def read_roster(path: Path) -> list[dict[str, str]]:
    suffix = path.suffix.lower()
    rows: list[list[str]] = []
    if suffix == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as f:
            rows = [[cell.strip() for cell in row] for row in csv.reader(f)]
    elif suffix == ".xlsx":
        try:
            import openpyxl  # type: ignore
        except Exception as exc:
            raise SystemExit(f"openpyxl unavailable: {exc}")
        wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
        ws = wb.worksheets[0]
        for row in ws.iter_rows(values_only=True):
            values = ["" if value is None else str(value).strip() for value in row]
            if any(values):
                rows.append(values)
    elif suffix == ".xls":
        try:
            import xlrd  # type: ignore
        except Exception:
            raise SystemExit("legacy .xls requires xlrd; convert to .xlsx or install xlrd")
        book = xlrd.open_workbook(str(path))
        sheet = book.sheet_by_index(0)
        for r in range(sheet.nrows):
            values = [str(sheet.cell_value(r, c)).strip() for c in range(sheet.ncols)]
            if any(values):
                rows.append(values)
    else:
        raise SystemExit("roster import supports .csv, .xlsx, .xls")
    if not rows:
        return []
    headers = rows[0]
    mapping = map_headers(headers)
    if "name" not in mapping:
        raise SystemExit("roster must contain a name column")
    result = []
    for raw in rows[1:]:
        item = {}
        for field, idx in mapping.items():
            item[field] = raw[idx].strip() if idx < len(raw) else ""
        if item.get("name"):
            result.append(item)
    return result


def read_csv_rows(path: Path, headers: list[str]) -> list[dict[str, str]]:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open("w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=headers).writeheader()
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv_rows(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def employee_id_for(name: str, existing: set[str]) -> str:
    base = "EMP-" + hashlib.sha1(name.encode("utf-8")).hexdigest()[:6].upper()
    if base not in existing:
        return base
    idx = 2
    while f"{base}-{idx}" in existing:
        idx += 1
    return f"{base}-{idx}"


def safe_segment(value: str) -> str:
    return re.sub(r'[<>:"/\\|?*\n\r\t]+', "-", value.strip())[:80] or "未命名"


def make_employee_record(row: dict[str, str], source: Path) -> str:
    lines = [
        "# 员工个人记录",
        "",
        "## 基础信息",
    ]
    for field in EMPLOYEE_HEADERS:
        if row.get(field):
            lines.append(f"- {field}：{row[field]}")
    lines.extend([
        "",
        "## 劳动合同",
        f"- 合同文件：{row.get('contract_file_path') or '待上传/待匹配'}",
        "",
        "## 薪酬工时",
        f"- 工时制度：{row.get('working_hours_system') or '待确认'}",
        f"- 薪酬结构：{row.get('salary_structure') or '待确认'}",
        "",
        "## 未休年假",
        "- 年假数据来自花名册；无考勤或请休假记录时不得断言已休或未休。",
        "",
        "## 来源边界",
        f"- 来源花名册：{source}",
        "- 本记录为企业内部管理记录。",
        "",
        "## 下一步动作",
        "- 上传或匹配劳动合同。",
        "- 核对合同期限、试用期和年假字段。",
        "",
    ])
    return "\n".join(lines)


def upsert(rows: list[dict[str, str]], id_field: str, data: dict[str, str], headers: list[str]) -> None:
    for row in rows:
        if row.get(id_field) == data[id_field]:
            row.update(data)
            return
    full = {header: "" for header in headers}
    full.update(data)
    rows.append(full)


def create_reminder(workspace: Path, employee_id: str, reminder_type: str, trigger_date: str, title: str, record: Path, source: Path) -> None:
    if not trigger_date:
        return
    subprocess.run([
        sys.executable,
        str(Path(__file__).resolve().with_name("reminders.py")),
        "add",
        "--workspace", str(workspace),
        "--source-module", "HR",
        "--source-id", employee_id,
        "--reminder-type", reminder_type,
        "--title", title,
        "--trigger-date", trigger_date,
        "--record-md-path", str(record),
        "--source-file-path", str(source),
    ], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Import an employee roster.")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--file", required=True)
    parser.add_argument("--year", default=str(datetime.now().year))
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    src = Path(args.file).expanduser().resolve()
    if not src.exists():
        raise SystemExit(f"file not found: {src}")
    imported = workspace / "02-人力资源" / "导入记录" / src.name
    imported.parent.mkdir(parents=True, exist_ok=True)
    if not imported.exists():
        shutil.copy2(src, imported)

    roster = read_roster(src)
    employee_path = workspace / "02-人力资源" / "employees.csv"
    leave_path = workspace / "02-人力资源" / "annual-leave.csv"
    employees = read_csv_rows(employee_path, EMPLOYEE_HEADERS)
    leaves = read_csv_rows(leave_path, LEAVE_HEADERS)
    existing_ids = {row.get("employee_id", "") for row in employees if row.get("employee_id")}
    now = datetime.now().isoformat(timespec="seconds")
    created = 0
    updated = 0
    reminders = 0

    for item in roster:
        employee_id = item.get("employee_id") or employee_id_for(item["name"], existing_ids)
        existing_ids.add(employee_id)
        record_dir = workspace / "02-人力资源" / "员工记录" / f"{safe_segment(employee_id)}-{safe_segment(item['name'])}"
        record_dir.mkdir(parents=True, exist_ok=True)
        record_path = record_dir / "employee-record.md"
        data = {header: "" for header in EMPLOYEE_HEADERS}
        data.update({key: value for key, value in item.items() if key in EMPLOYEE_HEADERS})
        data["employee_id"] = employee_id
        data.setdefault("employment_status", "在职")
        data["record_md_path"] = str(record_path)
        data.setdefault("created_at", now)
        data["updated_at"] = now
        before = any(row.get("employee_id") == employee_id for row in employees)
        upsert(employees, "employee_id", data, EMPLOYEE_HEADERS)
        if before:
            updated += 1
        else:
            created += 1
        record_path.write_text(make_employee_record(data, imported), encoding="utf-8")
        if data.get("probation_end_date"):
            create_reminder(workspace, employee_id, "试用期结束", data["probation_end_date"], f"{data['name']} 试用期结束提醒", record_path, imported)
            reminders += 1
        if data.get("contract_end_date"):
            create_reminder(workspace, employee_id, "劳动合同到期", data["contract_end_date"], f"{data['name']} 劳动合同到期提醒", record_path, imported)
            reminders += 1
            create_reminder(workspace, employee_id, "劳动合同续签", data["contract_end_date"], f"{data['name']} 劳动合同续签提醒", record_path, imported)
            reminders += 1
        if item.get("used_annual_leave_days") or item.get("remaining_annual_leave_days"):
            leave_id = f"AL-{employee_id}-{args.year}"
            leave_record = {
                "leave_record_id": leave_id,
                "employee_id": employee_id,
                "employee_name": data["name"],
                "year": args.year,
                "entry_date": data.get("entry_date", ""),
                "used_annual_leave_days": item.get("used_annual_leave_days", ""),
                "remaining_annual_leave_days": item.get("remaining_annual_leave_days", ""),
                "source_file_path": str(imported),
                "record_md_path": str(record_path),
                "risk_flags": "年假字段来自花名册，需结合考勤请假记录复核",
                "created_at": now,
                "updated_at": now,
            }
            upsert(leaves, "leave_record_id", leave_record, LEAVE_HEADERS)

    write_csv_rows(employee_path, EMPLOYEE_HEADERS, employees)
    write_csv_rows(leave_path, LEAVE_HEADERS, leaves)
    print("员工花名册导入完成。")
    print(f"已新增员工：{created}")
    print(f"已更新员工：{updated}")
    print(f"员工台账：{employee_path}")
    print(f"年假台账：{leave_path}")
    print(f"本次新增提醒：{reminders}")
    print(f"导入文件保存位置：{imported}")
    print("下一步：上传劳动合同并核对试用期、合同期限和未休年假数据。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
