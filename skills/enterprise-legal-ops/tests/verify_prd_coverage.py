#!/usr/bin/env python3
"""Static PRD coverage checks for enterprise-legal-ops."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SKILL = ROOT / "skills" / "enterprise-legal-ops"
PRD = ROOT / "docs" / "prd"


REQUIRED_PRDS = [
    "企业法务运营Skill_PRD_v0.1.1_第1卷_产品定义与总览.md",
    "企业法务运营Skill_PRD_v0.1.3_第2卷_本地目录结构与数据标准.md",
    "企业法务运营Skill_PRD_v0.1.6_第3卷_合同管理模块.md",
    "企业法务运营Skill_PRD_v0.1.8_第4卷_人力资源法务管理模块.md",
    "企业法务运营Skill_PRD_v0.1.10_第5卷_公章证照与章程权限模块.md",
    "企业法务运营Skill_PRD_v0.1.11_第6卷_提醒模块.md",
    "企业法务运营Skill_PRD_v0.1.12_第7卷_本地自然语言问库模块.md",
    "企业法务运营Skill_PRD_v0.1.13_第8卷_严审流程与用户引导规范.md",
]

REQUIRED_FILES = [
    "SKILL.md",
    "agents/openai.yaml",
    "references/workspace-data-standard.md",
    "references/contracts.md",
    "references/hr.md",
    "references/seals-licenses-governance.md",
    "references/reminders.md",
    "references/local-query.md",
    "references/strict-review.md",
    "scripts/init_workspace.py",
    "scripts/import_document.py",
    "scripts/import_roster.py",
    "scripts/archive_record.py",
    "scripts/reminders.py",
    "scripts/query_workspace.py",
    "scripts/ledger.py",
    "scripts/contract_redline_review.py",
    "scripts/strict_review_record.py",
    "tests/test_enterprise_legal_ops.py",
]

REQUIRED_TERMS = {
    "SKILL.md": [
        "企业内部",
        "formal legal opinions",
        "scripts/import_roster.py",
        "scripts/archive_record.py",
        "scripts/contract_redline_review.py",
        "Feishu is only for optional calendar reminders",
    ],
    "references/contracts.md": [
        "Word 修订格式合同审核稿",
        "Feishu contract review documents",
        "do not model-fill amounts",
    ],
    "references/hr.md": [
        "annual-leave.csv",
        "Policy Conflict Check",
        "Old Policy Legality Review",
        "scripts/import_roster.py",
    ],
    "references/seals-licenses-governance.md": [
        "capital-contributions.csv",
        "authority-summary.md",
        "Authority Check",
    ],
    "references/reminders.md": [
        "sync-feishu",
        "cancel",
        "postpone",
        "summary",
    ],
    "references/strict-review.md": [
        "read-review summary",
        "Rule Verification Summary",
        "source boundary",
        "strict_review_record.py",
    ],
}

FORBIDDEN_PERSONAL_PATHS = [
    "/" + "Users" + "/" + "panrui",
    "/" + "Users" + "/",
    "C:" + "\\Users",
    "/" + "home" + "/",
]


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> int:
    for name in REQUIRED_PRDS:
        path = PRD / name
        if not path.exists():
            fail(f"missing PRD: {path}")
    for rel in REQUIRED_FILES:
        path = SKILL / rel
        if not path.exists():
            fail(f"missing skill file: {path}")

    for rel, terms in REQUIRED_TERMS.items():
        text = (SKILL / rel).read_text(encoding="utf-8")
        for term in terms:
            if term not in text:
                fail(f"{rel} missing term: {term}")

    scanned_roots = [PRD, SKILL]
    for root in scanned_roots:
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for pattern in FORBIDDEN_PERSONAL_PATHS:
                if pattern in text:
                    fail(f"personal absolute path found in {path}: {pattern}")

    tests = (SKILL / "tests" / "test_enterprise_legal_ops.py").read_text(encoding="utf-8")
    for term in [
        "import_roster.py",
        "archive_record.py",
        "sync-feishu",
        "读取复查摘要",
        "authority-summary.md",
        "出资信息比对记录.md",
        "contract_redline_review.py",
        "strict_review_record.py",
    ]:
        if term not in tests:
            fail(f"smoke test missing coverage term: {term}")

    print("enterprise-legal-ops PRD coverage checks passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"PRD coverage check failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
