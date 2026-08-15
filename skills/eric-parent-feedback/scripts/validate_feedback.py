#!/usr/bin/env python3
"""Validate Eric parent-facing post-class feedback files."""

from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_HEADINGS = [
    "①课上内容",
    "②课上反馈",
    "③课后作业",
]

FORBIDDEN_PATTERNS = [
    r"^##\s+",
    r"##\s*(四|4|④|补充|下节课|下一步|内部|路由)",
    r"下节课(会|将|继续|重点|安排|计划|检查)",
    r"下一节课(会|将|继续|重点|安排|计划|检查)",
    r"下一步(会|将|继续|安排|计划|路线|方向)",
    r"MBTI|Hermes|T1|B01|B02|后台|路由|维修层|validator|生产",
    r"挖坑|让学生先错|教师动作|预期回应",
    r"心法|出招|拆招|定招",
    r"AI检测|检测率|绕过检测|规避检测",
]

OLD_HEADINGS = [
    "## 一、课程内容",
    "## 二、学生表现",
    "## 三、课后作业",
    "## 一、课上内容",
    "## 二、课上反馈",
    "## ①课上内容",
    "## ②课上反馈",
    "## ③课后作业",
    "一、课程内容",
    "二、学生表现",
    "三、课后作业",
    "一、课上内容",
    "二、课上反馈",
]

CLASS_COURSE_MARKERS = re.compile(
    r"班课|暑假班|寒假班|春季班|秋季班|预科班|小班|集体课"
)


def validate(text: str) -> list[str]:
    errors: list[str] = []

    headings = re.findall(r"^(?:①课上内容|②课上反馈|③课后作业)$", text, flags=re.MULTILINE)
    if headings != REQUIRED_HEADINGS:
        errors.append(
            "Visible plain-text section headings must be exactly: "
            + " | ".join(REQUIRED_HEADINGS)
            + f" ; found: {' | '.join(headings) if headings else '(none)'}"
        )

    for heading in OLD_HEADINGS:
        if heading in text and heading not in REQUIRED_HEADINGS:
            errors.append(f"Old heading style is not allowed: {heading}")

    for pattern in FORBIDDEN_PATTERNS:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            excerpt = match.group(0)
            errors.append(f"Forbidden parent-facing content matched /{pattern}/: {excerpt}")

    if not re.search(r"学生[：:]", text):
        errors.append("Missing metadata field: 学生：")
    metadata = text.split("①课上内容", maxsplit=1)[0]
    if CLASS_COURSE_MARKERS.search(metadata) and not re.search(r"^班级[：:]", metadata, flags=re.MULTILINE):
        errors.append(
            "Class-course marker found in metadata, but 班级： is missing. "
            "Course type—not student count—determines the format."
        )
    if not re.search(r"日期[：:]", text):
        errors.append("Missing metadata field: 日期：")
    if not re.search(r"(课次 / 主题|主题)[：:]", text):
        errors.append("Missing metadata field: 课次 / 主题： or 主题：")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: validate_feedback.py path/to/feedback.txt or -", file=sys.stderr)
        return 2

    if argv[1] == "-":
        text = sys.stdin.read()
    else:
        path = Path(argv[1])
        if not path.exists():
            print(f"ERROR: file not found: {path}", file=sys.stderr)
            return 2
        text = path.read_text(encoding="utf-8")
    errors = validate(text)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
