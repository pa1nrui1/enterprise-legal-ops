#!/usr/bin/env python3
"""Lightweight local CSV/Markdown query for Enterprise Legal Ops workspaces."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


CSV_TARGETS = [
    "01-合同管理/contracts.csv",
    "02-人力资源/employees.csv",
    "02-人力资源/employment-contracts.csv",
    "02-人力资源/annual-leave.csv",
    "03-公章证照/licenses.csv",
    "03-公章证照/seals.csv",
    "03-公章证照/authorizations.csv",
    "03-公章证照/seal-use.csv",
    "03-公章证照/governance-documents.csv",
    "03-公章证照/authority-checks.csv",
    "03-公章证照/capital-contributions.csv",
    "04-提醒中心/reminders.csv",
    "05-本地问库/source-map.csv",
    "05-本地问库/extracted-text-index.csv",
]


LEGAL_JUDGMENT_HINTS = [
    "能不能", "是否合法", "风险", "辞退", "解除", "调岗", "降薪", "处分",
    "盖章", "担保", "借款", "融资", "有效", "补偿", "违约", "怎么改",
]


def search_csv(path: Path, query: str) -> list[tuple[Path, dict[str, str]]]:
    if not path.exists():
        return []
    hits = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            haystack = " ".join(str(v) for v in row.values())
            if query.lower() in haystack.lower():
                hits.append((path, row))
    return hits


def search_markdown(workspace: Path, query: str, limit: int) -> list[tuple[Path, str]]:
    hits = []
    for path in workspace.rglob("*.md"):
        if len(hits) >= limit:
            break
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        idx = text.lower().find(query.lower())
        if idx >= 0:
            start = max(0, idx - 80)
            end = min(len(text), idx + 180)
            snippet = text[start:end].replace("\n", " ")
            hits.append((path, snippet))
    return hits


def classify_query(query: str) -> str:
    if any(hint in query for hint in LEGAL_JUDGMENT_HINTS):
        return "法律判断型问题"
    if any(word in query for word in ["以前", "上次", "历史", "审查过", "变更", "记录"]):
        return "历史记录查询"
    return "管理型查询"


def append_log(workspace: Path, question: str, csv_hits: int, md_hits: int, strict: bool) -> None:
    log = workspace / "05-本地问库" / "qa-log.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as f:
        f.write("\n## 查询记录\n")
        f.write(f"- 查询问题：{question}\n")
        f.write(f"- CSV 命中：{csv_hits}\n")
        f.write(f"- Markdown 命中：{md_hits}\n")
        f.write(f"- 是否需要严审：{'是' if strict else '否'}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Search local Enterprise Legal Ops ledgers and records.")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    query = args.query.strip()
    if not query:
        raise SystemExit("--query cannot be empty")

    strict = any(hint in query for hint in LEGAL_JUDGMENT_HINTS)
    query_type = classify_query(query)
    csv_hits = []
    for rel in CSV_TARGETS:
        csv_hits.extend(search_csv(workspace / rel, query))
        if len(csv_hits) >= args.limit:
            csv_hits = csv_hits[: args.limit]
            break
    md_hits = search_markdown(workspace, query, args.limit)
    append_log(workspace, query, len(csv_hits), len(md_hits), strict)

    if strict:
        print("## 需要进入严审")
        print()
        print("这个问题涉及实质法律判断，不能仅根据台账直接回答。")
        print()
    elif query_type == "历史记录查询":
        print("## 历史记录查询结果")
        print()
    else:
        print("## 查询结果")
        print()

    print(f"- 查询问题：{query}")
    print(f"- 查询类型：{query_type}")
    print("- 查询范围：CSV 台账、Markdown 记录")
    print()
    if csv_hits:
        print("### CSV 命中")
        for path, row in csv_hits:
            summary = "; ".join(f"{k}={v}" for k, v in row.items() if v)
            print(f"- 来源：{path}")
            print(f"  摘要：{summary[:500]}")
    if md_hits:
        print("\n### Markdown 命中")
        for path, snippet in md_hits:
            print(f"- 来源：{path}")
            print(f"  摘要：{snippet[:500]}")
    if not csv_hits and not md_hits:
        unresolved = workspace / "05-本地问库" / "unresolved-queries.md"
        unresolved.parent.mkdir(parents=True, exist_ok=True)
        with unresolved.open("a", encoding="utf-8") as f:
            f.write(f"\n- 未查询到：{query}\n")
        print("未查询到结果。")
        print(f"已记录：{unresolved}")
    print()
    print(f"- 是否需要进入严审：{'是' if strict else '否'}")
    if strict:
        module = "合同/HR/公章证照模块"
        if any(word in query for word in ["合同", "签", "违约", "续约", "解除"]):
            module = "合同管理模块"
        elif any(word in query for word in ["员工", "辞退", "调岗", "降薪", "处分", "年假", "工资", "制度"]):
            module = "人力资源法务管理模块"
        elif any(word in query for word in ["盖章", "担保", "借款", "融资", "章程", "授权", "出资", "证照"]):
            module = "公章证照与章程权限模块"
        print(f"- 建议进入模块：{module}")
    print("- 下一步建议：如涉及法律判断，请进入对应模块严审；如只是管理查询，可打开上述来源文件核对。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
