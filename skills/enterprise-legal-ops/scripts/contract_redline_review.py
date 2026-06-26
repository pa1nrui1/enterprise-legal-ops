#!/usr/bin/env python3
"""Create an internal contract tracked-change review draft.

This is a thin wrapper around the existing legal contract review redline engine.
It keeps enterprise-legal-ops simple while preserving the proven DOCX redline path.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def find_existing_engine(skill_dir: Path) -> tuple[Path, Path]:
    configured = os.environ.get("LEGAL_CONTRACT_REVIEW_SKILL", "").strip()
    if configured:
        legal_review = Path(configured).expanduser().resolve()
    else:
        skills_root = skill_dir.parent
        legal_review = skills_root / "legal" / "合同审查"
    apply_script = legal_review / "scripts" / "redline" / "apply_redline_plan.py"
    qa_script = legal_review / "scripts" / "redline" / "qa_redline.py"
    if not apply_script.exists():
        raise SystemExit(
            "missing redline engine. Set LEGAL_CONTRACT_REVIEW_SKILL to an existing "
            f"合同审查 Skill path, expected script: {apply_script}"
        )
    if not qa_script.exists():
        raise SystemExit(f"missing redline QA: {qa_script}")
    return apply_script, qa_script


def run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise SystemExit(
            "command failed:\n"
            + " ".join(cmd)
            + "\nSTDOUT:\n"
            + proc.stdout
            + "\nSTDERR:\n"
            + proc.stderr
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a contract tracked-change review draft.")
    parser.add_argument("--input", required=True, help="Original DOCX contract; preserved read-only.")
    parser.add_argument("--plan", required=True, help="redline-plan.json")
    parser.add_argument("--output", required=True, help="Output DOCX review draft.")
    parser.add_argument("--log", required=True, help="Execution log JSON.")
    parser.add_argument("--qa-report", required=True, help="QA report JSON.")
    parser.add_argument("--author", default="Enterprise Legal Ops")
    parser.add_argument("--organization", default="Internal Company Review")
    args = parser.parse_args()

    skill_dir = Path(__file__).resolve().parents[1]
    apply_script, qa_script = find_existing_engine(skill_dir)
    input_path = Path(args.input).expanduser().resolve()
    plan_path = Path(args.plan).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    log_path = Path(args.log).expanduser().resolve()
    qa_path = Path(args.qa_report).expanduser().resolve()

    if not input_path.exists():
        raise SystemExit(f"input not found: {input_path}")
    if not plan_path.exists():
        raise SystemExit(f"plan not found: {plan_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    qa_path.parent.mkdir(parents=True, exist_ok=True)

    # Guard against accidental overwrite of the original contract.
    if output_path == input_path:
        raise SystemExit("output must not be the same as input")
    backup = output_path.with_suffix(output_path.suffix + ".source-copy")
    if not backup.exists():
        shutil.copy2(input_path, backup)

    run([
        sys.executable, str(apply_script),
        "--input", str(input_path),
        "--plan", str(plan_path),
        "--output", str(output_path),
        "--log", str(log_path),
        "--author", args.author,
        "--organization", args.organization,
    ])
    run([
        sys.executable, str(qa_script),
        "--docx", str(output_path),
        "--report", str(qa_path),
    ])

    print("合同 Word 修订格式审核稿已生成。")
    print(f"原合同：{input_path}")
    print(f"审核修订稿：{output_path}")
    print(f"执行日志：{log_path}")
    print(f"QA 报告：{qa_path}")
    print("下一步：打开修订稿逐页检查，并确认所有需企业判断事项已用批注提示。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
