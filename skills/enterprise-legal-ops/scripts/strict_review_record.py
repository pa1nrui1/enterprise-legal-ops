#!/usr/bin/env python3
"""Create strict-review records for substantive Enterprise Legal Ops tasks."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from uuid import uuid4


def append_log(path: Path, title: str, record: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(f"# {title}\n\n", encoding="utf-8")
    with path.open("a", encoding="utf-8") as f:
        f.write(f"- {datetime.now().isoformat(timespec='seconds')}：{record}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create strict-review records.")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--module", required=True, choices=["合同", "HR", "公章证照"])
    parser.add_argument("--matter", required=True)
    parser.add_argument("--goal", required=True)
    parser.add_argument("--stance", default="")
    parser.add_argument("--materials", action="append", default=[])
    parser.add_argument("--verified-rules", default="待核验")
    parser.add_argument("--missing", default="")
    parser.add_argument("--risks", default="")
    parser.add_argument("--next-action", default="")
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    review_id = f"SR-{uuid4().hex[:8]}"
    out_dir = workspace / "07-输出文件" / "严审记录" / review_id
    out_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now().isoformat(timespec="seconds")

    user_confirmation = out_dir / "user-confirmation.md"
    user_confirmation.write_text(
        "\n".join([
            "# 用户确认记录",
            "",
            "## 确认时间",
            f"- {now}",
            "",
            "## 确认事项",
            f"- 模块：{args.module}",
            f"- 事项：{args.matter}",
            f"- 用户目标：{args.goal}",
            f"- 关键立场/适用场景：{args.stance or '待确认'}",
            "",
            "## 用户选择",
            "- 以上信息来自本次命令参数或用户确认。",
            "",
            "## 对输出的影响",
            "- 未确认事项不得作为确定结论。",
            "",
        ]),
        encoding="utf-8",
    )

    legal_verification = out_dir / "legal-verification-summary.md"
    legal_verification.write_text(
        "\n".join([
            "# 法规/规则核验摘要",
            "",
            "## 核验事项",
            f"- {args.matter}",
            "",
            "## 核验来源",
            f"- {args.verified_rules}",
            "",
            "## 核验结果",
            "- 待在具体严审中补充检索结果和现行有效状态。",
            "",
            "## 适用地区",
            "- 待确认/按用户确认地区。",
            "",
            "## 现行有效状态",
            "- 待核验。",
            "",
            "## 对本事项的影响",
            "- 未完成核验前不得引用为确定法律依据。",
            "",
        ]),
        encoding="utf-8",
    )

    source_boundary = out_dir / "source-boundary.md"
    material_lines = [f"- {Path(item).expanduser().resolve()}" for item in args.materials] or ["- 待上传/待读取"]
    source_boundary.write_text(
        "\n".join([
            "# 来源边界",
            "",
            "## 已读取材料",
            *material_lines,
            "",
            "## 已核验内容",
            f"- {args.verified_rules}",
            "",
            "## 未读取或缺失材料",
            f"- {args.missing or '待结合具体材料确认'}",
            "",
            "## 存疑项",
            "- 所有未读取、未核验、未确认内容均为存疑项。",
            "",
            "## 输出边界",
            "- 本记录仅用于企业内部严审过程管理，不是律师顾问意见或正式法律意见。",
            "",
        ]),
        encoding="utf-8",
    )

    risk_record = out_dir / "risk-record.md"
    risk_record.write_text(
        "\n".join([
            "# 风险判断记录",
            "",
            f"- 严审编号：{review_id}",
            f"- 模块：{args.module}",
            f"- 事项：{args.matter}",
            f"- 用户目标：{args.goal}",
            f"- 风险记录：{args.risks or '待完成材料读取和规则核验后补充'}",
            f"- 下一步：{args.next_action or '继续读取材料、核验规则并生成内部处理建议'}",
            "",
        ]),
        encoding="utf-8",
    )

    append_log(workspace / "_system" / "user-confirmation-log.md", "用户确认记录", user_confirmation)
    append_log(workspace / "_system" / "legal-verification-log.md", "法规/规则核验记录", legal_verification)
    append_log(workspace / "_system" / "source-boundary-log.md", "来源边界记录", source_boundary)

    print("严审记录已创建。")
    print(f"严审编号：{review_id}")
    print(f"严审目录：{out_dir}")
    print(f"用户确认记录：{user_confirmation}")
    print(f"法规/规则核验摘要：{legal_verification}")
    print(f"来源边界：{source_boundary}")
    print(f"风险判断记录：{risk_record}")
    print("下一步：完成材料读取和规则核验后，再输出内部风险提示或 Word 修订稿。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
