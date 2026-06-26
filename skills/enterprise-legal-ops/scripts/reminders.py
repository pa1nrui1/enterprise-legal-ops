#!/usr/bin/env python3
"""Manage local Enterprise Legal Ops reminders."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from uuid import uuid4


HEADERS = [
    "reminder_id", "source_module", "source_id", "reminder_type", "title",
    "description", "trigger_date", "advance_days", "remind_date", "priority",
    "local_status", "feishu_enabled", "feishu_status", "feishu_event_id",
    "source_file_path", "record_md_path", "owner", "next_action", "created_at",
    "updated_at",
]


DEFAULT_ADVANCE_DAYS = {
    "合同到期": 30,
    "自动续约": 30,
    "提前通知解除": 15,
    "提前通知不续约": 15,
    "劳动合同到期": 30,
    "劳动合同续签": 30,
    "试用期结束": 7,
    "证照到期": 60,
    "证照年检": 30,
    "授权失效": 15,
    "股东出资到期": 60,
    "认缴出资已逾期": 0,
    "离职未休年假结算": 0,
    "年假即将到期": 30,
    "章程变更复核": 0,
    "高风险用印后续跟进": 0,
}

LOCAL_STATUS = {"待提醒", "已提醒", "已完成", "已取消", "已延期", "信息缺失", "待用户确认"}
FEISHU_STATUS = {"未启用", "待同步", "已同步", "同步失败", "已取消", "无需同步"}


def reminders_path(workspace: Path) -> Path:
    return workspace / "04-提醒中心" / "reminders.csv"


def changes_path(workspace: Path) -> Path:
    return workspace / "04-提醒中心" / "reminder-changes.md"


def sync_log_path(workspace: Path) -> Path:
    return workspace / "04-提醒中心" / "feishu-sync-log.md"


def ensure_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open("w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=HEADERS).writeheader()


def read_rows(path: Path) -> list[dict[str, str]]:
    ensure_file(path)
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    ensure_file(path)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def append_change(workspace: Path, reminder_id: str, action: str, note: str = "") -> None:
    path = changes_path(workspace)
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now().isoformat(timespec="seconds")
    if not path.exists():
        path.write_text("# 提醒变更记录\n\n", encoding="utf-8")
    with path.open("a", encoding="utf-8") as f:
        f.write(f"## {now}｜{action}\n\n")
        f.write(f"- 提醒编号：{reminder_id}\n")
        if note:
            f.write(f"- 说明：{note}\n")
        f.write("\n")


def parse_date(value: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def add(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).expanduser().resolve()
    path = reminders_path(workspace)
    rows = read_rows(path)
    now = datetime.now().isoformat(timespec="seconds")
    trigger = parse_date(args.trigger_date)
    advance_days = args.advance_days
    if advance_days is None:
        advance_days = DEFAULT_ADVANCE_DAYS.get(args.reminder_type, 30)
    if trigger:
        remind = trigger - timedelta(days=advance_days)
        local_status = "待提醒"
    else:
        remind = None
        local_status = "信息缺失"

    feishu_enabled = "是" if args.feishu_enabled else "否"
    feishu_status = "待同步" if args.feishu_enabled and trigger else "未启用"
    if args.feishu_enabled and not trigger:
        feishu_status = "无需同步"

    row = {
        "reminder_id": args.reminder_id or f"REM-{uuid4().hex[:8]}",
        "source_module": args.source_module,
        "source_id": args.source_id or "",
        "reminder_type": args.reminder_type,
        "title": args.title,
        "description": args.description or "",
        "trigger_date": args.trigger_date or "",
        "advance_days": str(advance_days),
        "remind_date": remind.isoformat() if remind else "",
        "priority": args.priority,
        "local_status": local_status,
        "feishu_enabled": feishu_enabled,
        "feishu_status": feishu_status,
        "feishu_event_id": "",
        "source_file_path": args.source_file_path or "",
        "record_md_path": args.record_md_path or "",
        "owner": args.owner or "",
        "next_action": args.next_action or "",
        "created_at": now,
        "updated_at": now,
    }
    for existing in rows:
        if (
            existing.get("source_module") == row["source_module"]
            and existing.get("source_id") == row["source_id"]
            and existing.get("reminder_type") == row["reminder_type"]
            and existing.get("trigger_date") == row["trigger_date"]
            and existing.get("local_status") not in {"已取消"}
        ):
            print("已存在相同来源和日期的提醒，未重复创建。")
            print(f"提醒编号：{existing.get('reminder_id')}")
            print(f"提醒台账：{path}")
            return 0
    rows.append(row)
    write_rows(path, rows)
    append_change(workspace, row["reminder_id"], "创建提醒", row["title"])
    print("提醒已写入本地台账。")
    print(f"提醒编号：{row['reminder_id']}")
    print(f"提醒台账：{path}")
    print(f"提醒日期：{row['remind_date'] or '信息缺失，待确认'}")
    print(f"飞书状态：{row['feishu_status']}")
    return 0


def list_cmd(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).expanduser().resolve()
    path = reminders_path(workspace)
    rows = read_rows(path)
    today = date.today()
    filtered = []
    for row in rows:
        if args.status and row.get("local_status") != args.status:
            continue
        if args.type and row.get("reminder_type") != args.type:
            continue
        if args.days is not None:
            remind = parse_date(row.get("remind_date", ""))
            if not remind or remind < today or remind > today + timedelta(days=args.days):
                continue
        filtered.append(row)

    print(f"提醒台账：{path}")
    print(f"匹配数量：{len(filtered)}")
    for row in filtered:
        print(
            f"- {row.get('reminder_id')} | {row.get('reminder_type')} | "
            f"{row.get('title')} | 提醒日 {row.get('remind_date') or '待确认'} | "
            f"状态 {row.get('local_status')} | 飞书 {row.get('feishu_status')}"
        )
    return 0


def complete(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).expanduser().resolve()
    path = reminders_path(workspace)
    rows = read_rows(path)
    now = datetime.now().isoformat(timespec="seconds")
    matched = False
    for row in rows:
        if row.get("reminder_id") == args.reminder_id:
            row["local_status"] = "已完成"
            row["next_action"] = args.note or row.get("next_action", "")
            row["updated_at"] = now
            matched = True
            break
    if not matched:
        raise SystemExit(f"未找到提醒：{args.reminder_id}")
    write_rows(path, rows)
    append_change(workspace, args.reminder_id, "完成提醒", args.note or "")
    append_completion(workspace, args.reminder_id, args.note or "")
    print("提醒已标记完成。")
    print(f"提醒编号：{args.reminder_id}")
    print(f"提醒台账：{path}")
    return 0


def append_completion(workspace: Path, reminder_id: str, note: str) -> None:
    path = workspace / "04-提醒中心" / "completed-reminders.csv"
    headers = ["reminder_id", "completed_at", "completion_note"]
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not exists:
            writer.writeheader()
        writer.writerow({
            "reminder_id": reminder_id,
            "completed_at": datetime.now().isoformat(timespec="seconds"),
            "completion_note": note,
        })


def cancel(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).expanduser().resolve()
    path = reminders_path(workspace)
    rows = read_rows(path)
    now = datetime.now().isoformat(timespec="seconds")
    matched = False
    for row in rows:
        if row.get("reminder_id") == args.reminder_id:
            row["local_status"] = "已取消"
            if row.get("feishu_status") == "已同步":
                row["feishu_status"] = "已取消" if args.feishu_cancelled else row["feishu_status"]
            row["next_action"] = args.note or row.get("next_action", "")
            row["updated_at"] = now
            matched = True
            break
    if not matched:
        raise SystemExit(f"未找到提醒：{args.reminder_id}")
    write_rows(path, rows)
    append_change(workspace, args.reminder_id, "取消提醒", args.note or "")
    print("提醒已标记取消，历史记录已保留。")
    print(f"提醒编号：{args.reminder_id}")
    print(f"提醒台账：{path}")
    return 0


def postpone(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).expanduser().resolve()
    path = reminders_path(workspace)
    rows = read_rows(path)
    new_remind = parse_date(args.remind_date)
    if not new_remind:
        raise SystemExit("--remind-date must be YYYY-MM-DD")
    now = datetime.now().isoformat(timespec="seconds")
    matched = False
    for row in rows:
        if row.get("reminder_id") == args.reminder_id:
            old = row.get("remind_date", "")
            row["remind_date"] = new_remind.isoformat()
            if args.trigger_date:
                trigger = parse_date(args.trigger_date)
                if not trigger:
                    raise SystemExit("--trigger-date must be YYYY-MM-DD")
                row["trigger_date"] = trigger.isoformat()
            row["local_status"] = "已延期"
            if row.get("feishu_status") == "已同步":
                row["feishu_status"] = "待同步"
            row["next_action"] = args.note or row.get("next_action", "")
            row["updated_at"] = now
            matched = True
            append_change(workspace, args.reminder_id, "延期提醒", f"{old} -> {new_remind.isoformat()} {args.note or ''}".strip())
            break
    if not matched:
        raise SystemExit(f"未找到提醒：{args.reminder_id}")
    write_rows(path, rows)
    print("提醒已延期，历史记录已保留。")
    print(f"提醒编号：{args.reminder_id}")
    print(f"新的提醒日期：{new_remind.isoformat()}")
    print(f"提醒台账：{path}")
    return 0


def summary(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).expanduser().resolve()
    path = reminders_path(workspace)
    rows = read_rows(path)
    today = date.today()
    within = today + timedelta(days=args.days)
    buckets = {
        "本期待处理": [],
        "逾期提醒": [],
        "高优先级": [],
        "飞书同步失败": [],
        "信息缺失": [],
        "待用户确认": [],
    }
    for row in rows:
        status = row.get("local_status", "")
        remind = parse_date(row.get("remind_date", ""))
        if status in {"已完成", "已取消"}:
            continue
        if remind and today <= remind <= within:
            buckets["本期待处理"].append(row)
        if remind and remind < today:
            buckets["逾期提醒"].append(row)
        if row.get("priority") in {"高", "紧急"}:
            buckets["高优先级"].append(row)
        if row.get("feishu_status") == "同步失败":
            buckets["飞书同步失败"].append(row)
        if status == "信息缺失":
            buckets["信息缺失"].append(row)
        if status == "待用户确认":
            buckets["待用户确认"].append(row)

    out = workspace / "04-提醒中心" / "reminder-summary.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# 提醒摘要", "", f"- 生成时间：{datetime.now().isoformat(timespec='seconds')}", f"- 统计范围：未来 {args.days} 天", ""]
    for title, items in buckets.items():
        lines.append(f"## {title}")
        if not items:
            lines.append("- 无")
        for row in items:
            lines.append(
                f"- {row.get('reminder_id')}｜{row.get('reminder_type')}｜{row.get('title')}｜"
                f"提醒日：{row.get('remind_date') or '待确认'}｜状态：{row.get('local_status')}｜飞书：{row.get('feishu_status')}"
            )
        lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    print("提醒摘要已生成。")
    print(f"提醒台账：{path}")
    print(f"提醒摘要：{out}")
    return 0


def read_feishu_config(workspace: Path) -> dict[str, str]:
    config = workspace / "04-提醒中心" / "feishu-config.md"
    result = {
        "enabled": "否",
        "calendar_id": "primary",
    }
    if not config.exists():
        return result
    text = config.read_text(encoding="utf-8")
    for raw in text.splitlines():
        line = raw.strip().lstrip("-").strip()
        if "：" not in line:
            continue
        key, value = [part.strip() for part in line.split("：", 1)]
        if key == "是否启用飞书提醒":
            result["enabled"] = value or "否"
        elif key == "默认日历":
            result["calendar_id"] = value or "primary"
    return result


def append_sync_log(workspace: Path, reminder_id: str, status: str, message: str) -> None:
    path = sync_log_path(workspace)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("# 飞书同步记录\n\n", encoding="utf-8")
    with path.open("a", encoding="utf-8") as f:
        f.write(f"## {datetime.now().isoformat(timespec='seconds')}｜{status}\n\n")
        f.write(f"- 提醒编号：{reminder_id}\n")
        f.write(f"- 结果：{message}\n\n")


def event_times(remind_date: str) -> tuple[str, str]:
    day = parse_date(remind_date)
    if not day:
        raise ValueError("missing remind date")
    return f"{day.isoformat()}T09:00+08:00", f"{day.isoformat()}T09:30+08:00"


def parse_event_id(stdout: str) -> str:
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return ""
    stack = [payload]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            for key, value in item.items():
                if key == "event_id" and isinstance(value, str):
                    return value
                if isinstance(value, (dict, list)):
                    stack.append(value)
        elif isinstance(item, list):
            stack.extend(item)
    return ""


def sync_feishu(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).expanduser().resolve()
    path = reminders_path(workspace)
    rows = read_rows(path)
    config = read_feishu_config(workspace)
    if config["enabled"] != "是" and not args.force:
        print("飞书提醒未启用，未执行同步。本地提醒不受影响。")
        print(f"配置文件：{workspace / '04-提醒中心' / 'feishu-config.md'}")
        return 0

    changed = False
    synced = 0
    failed = 0
    for row in rows:
        if args.reminder_id and row.get("reminder_id") != args.reminder_id:
            continue
        if row.get("local_status") in {"已完成", "已取消", "信息缺失", "待用户确认"}:
            continue
        if row.get("feishu_status") == "已同步" and not args.force:
            continue
        if row.get("feishu_enabled") != "是" and not args.force:
            continue
        if not row.get("remind_date"):
            row["feishu_status"] = "无需同步"
            changed = True
            continue
        start, end = event_times(row["remind_date"])
        description = "\n".join([
            f"提醒类型：{row.get('reminder_type', '')}",
            f"事件日期：{row.get('trigger_date', '')}",
            f"提前提醒天数：{row.get('advance_days', '')}",
            f"来源模块：{row.get('source_module', '')}",
            f"来源文件：{row.get('source_file_path', '')}",
            f"本地记录：{row.get('record_md_path', '')}",
            f"下一步建议：{row.get('next_action', '')}",
        ])
        cmd = [
            "lark-cli", "calendar", "+create",
            "--as", "user",
            "--summary", f"[{row.get('source_module', '法务')}] {row.get('title', '提醒事项')}",
            "--start", start,
            "--end", end,
            "--description", description,
            "--calendar-id", config.get("calendar_id") or "primary",
        ]
        if args.dry_run:
            cmd.append("--dry-run")
        proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        now = datetime.now().isoformat(timespec="seconds")
        if proc.returncode == 0 and not args.dry_run:
            event_id = parse_event_id(proc.stdout)
            row["feishu_status"] = "已同步"
            row["feishu_event_id"] = event_id
            row["updated_at"] = now
            append_sync_log(workspace, row["reminder_id"], "已同步", event_id or "已创建飞书日历事件")
            synced += 1
            changed = True
        elif proc.returncode == 0 and args.dry_run:
            append_sync_log(workspace, row["reminder_id"], "预演成功", proc.stdout.strip()[:1000])
            synced += 1
        else:
            row["feishu_status"] = "同步失败"
            row["updated_at"] = now
            append_sync_log(workspace, row["reminder_id"], "同步失败", (proc.stderr or proc.stdout).strip()[:1000])
            failed += 1
            changed = True
    if changed:
        write_rows(path, rows)
    print("飞书提醒同步处理完成。")
    print(f"提醒台账：{path}")
    print(f"同步/预演成功：{synced}")
    print(f"同步失败：{failed}")
    print(f"飞书同步记录：{sync_log_path(workspace)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage Enterprise Legal Ops reminders.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    add_parser = sub.add_parser("add")
    add_parser.add_argument("--workspace", required=True)
    add_parser.add_argument("--reminder-id")
    add_parser.add_argument("--source-module", required=True)
    add_parser.add_argument("--source-id")
    add_parser.add_argument("--reminder-type", required=True)
    add_parser.add_argument("--title", required=True)
    add_parser.add_argument("--description")
    add_parser.add_argument("--trigger-date", default="")
    add_parser.add_argument("--advance-days", type=int)
    add_parser.add_argument("--priority", default="中", choices=["低", "中", "高", "紧急"])
    add_parser.add_argument("--source-file-path")
    add_parser.add_argument("--record-md-path")
    add_parser.add_argument("--owner")
    add_parser.add_argument("--next-action")
    add_parser.add_argument("--feishu-enabled", action="store_true")
    add_parser.set_defaults(func=add)

    list_parser = sub.add_parser("list")
    list_parser.add_argument("--workspace", required=True)
    list_parser.add_argument("--status")
    list_parser.add_argument("--type")
    list_parser.add_argument("--days", type=int)
    list_parser.set_defaults(func=list_cmd)

    complete_parser = sub.add_parser("complete")
    complete_parser.add_argument("--workspace", required=True)
    complete_parser.add_argument("--reminder-id", required=True)
    complete_parser.add_argument("--note")
    complete_parser.set_defaults(func=complete)

    cancel_parser = sub.add_parser("cancel")
    cancel_parser.add_argument("--workspace", required=True)
    cancel_parser.add_argument("--reminder-id", required=True)
    cancel_parser.add_argument("--note")
    cancel_parser.add_argument("--feishu-cancelled", action="store_true")
    cancel_parser.set_defaults(func=cancel)

    postpone_parser = sub.add_parser("postpone")
    postpone_parser.add_argument("--workspace", required=True)
    postpone_parser.add_argument("--reminder-id", required=True)
    postpone_parser.add_argument("--remind-date", required=True)
    postpone_parser.add_argument("--trigger-date")
    postpone_parser.add_argument("--note")
    postpone_parser.set_defaults(func=postpone)

    summary_parser = sub.add_parser("summary")
    summary_parser.add_argument("--workspace", required=True)
    summary_parser.add_argument("--days", type=int, default=30)
    summary_parser.set_defaults(func=summary)

    sync_parser = sub.add_parser("sync-feishu")
    sync_parser.add_argument("--workspace", required=True)
    sync_parser.add_argument("--reminder-id")
    sync_parser.add_argument("--force", action="store_true")
    sync_parser.add_argument("--dry-run", action="store_true")
    sync_parser.set_defaults(func=sync_feishu)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
