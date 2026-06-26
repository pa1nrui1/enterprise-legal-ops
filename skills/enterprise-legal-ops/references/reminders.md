# Reminders Module

Use for all local reminders and optional Feishu calendar reminders.

## Scope

Feishu is only for calendar reminders. Do not use Feishu for contract review, HR review, seal/license deliverables, or approval workflows.

All reminders are written locally first.

## Files

```text
<company_workspace>/04-提醒中心/
├── reminders.csv
├── reminder-summary.md
├── feishu-config.md
├── feishu-sync-log.md
├── completed-reminders.csv
└── failed-sync/
```

`reminders.csv` fields:

```text
reminder_id,source_module,source_id,reminder_type,title,description,trigger_date,advance_days,remind_date,priority,local_status,feishu_enabled,feishu_status,feishu_event_id,source_file_path,record_md_path,owner,next_action,created_at,updated_at
```

## Status Values

Local status:

```text
待提醒
已提醒
已完成
已取消
已延期
信息缺失
待用户确认
```

Feishu status:

```text
未启用
待同步
已同步
同步失败
已取消
无需同步
```

Priority:

```text
低
中
高
紧急
```

## Default Advance Days

```text
合同到期：30
自动续约：30
提前通知解除/不续约：15 days before notice deadline
劳动合同到期：30
试用期结束：7
证照到期：60
证照年检：30
授权失效：15
股东出资到期：60
年假即将到期：30
```

If date is unclear or OCR-suspect, create an `信息缺失` or `待用户确认` reminder, not a firm date reminder.

## Feishu Config

`feishu-config.md` should record:

- whether Feishu reminders are enabled
- default calendar
- default advance days
- whether to auto-create events
- whether local reminders are kept when sync fails
- last config time

If Feishu is disabled, set `feishu_status` to `未启用`; other modules remain fully functional.

## Feishu Sync

Only sync when:

- Feishu is enabled
- date is clear
- status is not `信息缺失` or `待用户确认`
- not already synced or date changed
- config allows auto-create or user confirmed

On success:

- update `reminders.csv`
- set `feishu_event_id`
- set `feishu_status=已同步`
- write `feishu-sync-log.md`
- tell user

On failure:

- keep local reminder
- set `feishu_status=同步失败`
- record real error
- tell user retry/local-only options

Use `scripts/reminders.py sync-feishu` only for Feishu calendar reminders. It calls `lark-cli calendar +create` with user identity and leaves local reminders intact when sync fails. Use `--dry-run` for validation without writing to Feishu.

## Query And State Changes

Support queries for future, overdue, high-priority, missing-info, pending-confirmation, and Feishu-failed reminders.

Completing, cancelling, or postponing reminders must preserve history. Never delete records silently.

Use:

```text
scripts/reminders.py complete
scripts/reminders.py cancel
scripts/reminders.py postpone
scripts/reminders.py summary
```
