#!/usr/bin/env python3
"""Append common Enterprise Legal Ops ledger records."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path


LEDGERS = {
    "contract": {
        "path": "01-合同管理/contracts.csv",
        "id": "contract_id",
        "fields": {
            "contract_id", "contract_name", "contract_type", "our_party", "our_role",
            "counterparty", "review_position", "amount", "effective_date", "end_date",
            "auto_renewal", "notice_days", "latest_notice_date", "status",
            "original_file_path", "record_md_path", "latest_review_date", "risk_level",
            "next_action", "created_at", "updated_at",
        },
    },
    "employee": {
        "path": "02-人力资源/employees.csv",
        "id": "employee_id",
        "fields": {
            "employee_id", "name", "department", "position", "employment_status",
            "entry_date", "probation_end_date", "contract_start_date", "contract_end_date",
            "work_location", "working_hours_system", "salary_structure",
            "social_insurance_status", "contract_file_path", "record_md_path",
            "risk_flags", "next_action", "created_at", "updated_at",
        },
    },
    "annual_leave": {
        "path": "02-人力资源/annual-leave.csv",
        "id": "leave_record_id",
        "fields": {
            "leave_record_id", "employee_id", "employee_name", "year", "entry_date",
            "continuous_work_years", "statutory_annual_leave_days",
            "company_annual_leave_days", "used_annual_leave_days",
            "remaining_annual_leave_days", "carryover_rule", "expiry_date",
            "compensation_required", "compensation_amount", "calculation_basis",
            "source_file_path", "record_md_path", "risk_flags", "created_at", "updated_at",
        },
    },
    "license": {
        "path": "03-公章证照/licenses.csv",
        "id": "license_id",
        "fields": {
            "license_id", "license_name", "license_type", "holder", "license_number",
            "issue_authority", "issue_date", "expiry_date", "annual_check_required",
            "annual_check_deadline", "file_path", "record_md_path", "status",
            "risk_flags", "next_action", "created_at", "updated_at",
        },
    },
    "seal": {
        "path": "03-公章证照/seals.csv",
        "id": "seal_id",
        "fields": {
            "seal_id", "seal_name", "seal_type", "custodian", "authorized_scope",
            "approval_rule", "storage_location", "status", "record_md_path",
            "created_at", "updated_at",
        },
    },
    "authorization": {
        "path": "03-公章证照/authorizations.csv",
        "id": "authorization_id",
        "fields": {
            "authorization_id", "authorization_name", "grantor", "grantee", "scope",
            "start_date", "end_date", "revocation_status", "file_path", "record_md_path",
            "risk_flags", "created_at", "updated_at",
        },
    },
    "capital": {
        "path": "03-公章证照/capital-contributions.csv",
        "id": "contribution_id",
        "fields": {
            "contribution_id", "shareholder_name", "shareholder_type", "subscribed_amount",
            "paid_amount", "unpaid_amount", "contribution_method", "subscription_deadline",
            "paid_date", "equity_ratio", "source_document", "source_file_path",
            "proof_file_path", "status", "risk_flags", "next_action", "created_at",
            "updated_at",
        },
    },
}


def read_headers(path: Path) -> list[str]:
    if not path.exists():
        raise SystemExit(f"ledger not found; initialize workspace first: {path}")
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        return next(reader)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_rows(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def parse_values(values: list[str], allowed: set[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for item in values:
        if "=" not in item:
            raise SystemExit(f"invalid --set value, expected key=value: {item}")
        key, value = item.split("=", 1)
        key = key.strip()
        if key not in allowed:
            raise SystemExit(f"field {key!r} is not allowed for this ledger")
        parsed[key] = value
    return parsed


def upsert(args: argparse.Namespace) -> int:
    spec = LEDGERS[args.ledger]
    workspace = Path(args.workspace).expanduser().resolve()
    path = workspace / spec["path"]
    headers = read_headers(path)
    rows = read_rows(path)
    now = datetime.now().isoformat(timespec="seconds")
    data = parse_values(args.set, spec["fields"])
    id_field = spec["id"]
    record_id = data.get(id_field)
    if not record_id:
        raise SystemExit(f"missing required field: {id_field}")
    data.setdefault("created_at", now)
    data["updated_at"] = now

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
    print("台账已更新。")
    print(f"台账类型：{args.ledger}")
    print(f"记录编号：{record_id}")
    print(f"台账位置：{path}")
    print("下一步：如涉及日期、风险或法律判断，请生成提醒并进入严审流程。")
    return 0


def list_cmd(args: argparse.Namespace) -> int:
    spec = LEDGERS[args.ledger]
    path = Path(args.workspace).expanduser().resolve() / spec["path"]
    rows = read_rows(path)
    if args.query:
        q = args.query.lower()
        rows = [row for row in rows if q in " ".join(row.values()).lower()]
    print(f"台账位置：{path}")
    print(f"匹配数量：{len(rows)}")
    for row in rows[: args.limit]:
        record_id = row.get(spec["id"], "")
        name = row.get("contract_name") or row.get("name") or row.get("license_name") or row.get("seal_name") or row.get("authorization_name") or row.get("shareholder_name") or ""
        status = row.get("status") or row.get("employment_status") or row.get("risk_flags") or ""
        print(f"- {record_id} | {name} | {status}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Append or update Enterprise Legal Ops ledgers.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    upsert_parser = sub.add_parser("upsert")
    upsert_parser.add_argument("--workspace", required=True)
    upsert_parser.add_argument("--ledger", required=True, choices=sorted(LEDGERS))
    upsert_parser.add_argument("--set", action="append", default=[], help="field=value; repeatable")
    upsert_parser.set_defaults(func=upsert)

    list_parser = sub.add_parser("list")
    list_parser.add_argument("--workspace", required=True)
    list_parser.add_argument("--ledger", required=True, choices=sorted(LEDGERS))
    list_parser.add_argument("--query")
    list_parser.add_argument("--limit", type=int, default=20)
    list_parser.set_defaults(func=list_cmd)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
