#!/usr/bin/env python3
"""Validate structure and flag register risks in parent feedback TXT files."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_HEADINGS = [
    "①课上内容",
    "②课上反馈",
    "③课后作业",
]

FORBIDDEN_PATTERNS: list[tuple[str, str]] = [
    (r"^#{1,6}\s+", "Markdown headings are not allowed"),
    (
        r"下节课(会|将|继续|重点|安排|计划|检查)|"
        r"下一节课(会|将|继续|重点|安排|计划|检查)|"
        r"下一步(会|将|继续|安排|计划|路线|方向)",
        "next-lesson or route preview is not allowed",
    ),
    (
        r"MBTI|内部(?:后台|路由|生产|MBTI|Hermes|validator|T1|B01|B02)|维修层|"
        r"^(?:后台|路由|生产|MBTI|Hermes|validator|T1|B01|B02)"
        r"(?:标签|编号|代码|状态|备注|版本|稿|层)?[：:]|"
        r"(?:反馈|教学|系统|生产|工作流)\s*(?:的\s*)?(?:路由|route)"
        r"(?:标签|编号|代码|状态|备注|版本|工作流)?[：:]|"
        r"内部.{0,6}(?:路由|route)|"
        r"(?:路由|route|后台|生产)(?:标签|编号|代码|状态|备注|版本|稿|层)[：:]?|"
        r"(?:本反馈|该反馈|反馈文本|本文|输出|结果).{0,8}validator|"
        r"(?:通过|经由?)\s*validator\s*(?:检查|验证|校验|审查)|"
        r"validator\s*(?:检查|验证|校验|审查|通过|状态|结果|报告|版本|标签|编号|代码)[：:]?|"
        r"(?:内部(?:项目|系统|记忆)?|记忆系统|后台项目|生产系统).{0,3}Hermes|"
        r"(?:系统|项目|记忆系统)\s*[：:]\s*Hermes|"
        r"Hermes\s*(?:系统|记忆|项目|标签|编号|状态|备注|版本|路由)",
        "internal planning labels are not allowed",
    ),
    (
        r"挖坑|让学生先错|教师动作|预期回应|心法|出招|拆招|定招",
        "teacher-tactic labels are not allowed",
    ),
    (
        r"AI检测|检测率|绕过检测|规避检测",
        "AI-detection claims are not allowed",
    ),
]

STYLE_PATTERNS: list[tuple[str, str, str]] = [
    ("状态还行", r"状态还行", "replace conversational assessment with a precise classroom result"),
    ("挺好", r"挺好|挺不错", "replace conversational praise with a supported result"),
    ("抓紧", r"抓紧", "state the exact deadline or completion action neutrally"),
    ("小磕碰", r"小磕碰", "use a calibrated formal description of the actual slip"),
    ("下手更顺", r"下手(?:比[^，。\n]{0,12})?更?顺", "state what became more independent or stable"),
    ("问题不大", r"问题不大", "prefer 整体影响不大 when that severity is supported"),
    (
        "训话式条件句（不能……就……）",
        r"不能[^。；\n]{0,24}就(?:不|别|没)",
        "replace scolding with a neutral verified requirement",
    ),
    ("课堂投入度", r"课堂投入度", "describe observable participation instead of an administrative metric"),
    ("任务完成度", r"任务完成度", "state the exact unfinished task"),
    ("提升空间", r"提升空间", "name the exact unstable action"),
    ("切实下功夫", r"切实下功夫", "name the concrete practice need without inflating severity"),
    (
        "各方面才能……",
        r"各方面[^。；\n]{0,20}(?:才|才能)[^。；\n]{0,20}(?:提升|提高|往上走)",
        "avoid broad causal claims unsupported by one lesson",
    ),
    ("具有较强的学习能力", r"具有较强的学习能力", "replace the label with an independent classroom result"),
    (
        "打下坚实基础",
        r"为[^。；\n]{0,20}打下(?:了)?坚实基础",
        "delete the stock conclusion or name a concrete consequence",
    ),
    ("本节课围绕……展开", r"本节课围绕[^。；\n]{0,30}(?:展开|进行了)", "state what was actually practiced"),
    ("系统梳理", r"系统(?:地|性)?梳理", "list the concrete content instead"),
    ("整体表现良好", r"整体表现良好", "replace generic praise with a supported result"),
    ("望继续努力", r"望(?:再接再厉|继续努力)", "replace motivational closure with an executable task"),
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

EXTRA_SECTION_RE = re.compile(
    r"^(?:"
    r"(?:④|四|4)\s*[、.．)）:：]?\s*"
    r"(?:家长配合|家长建议|家长提醒|补充说明|补充建议|老师建议|老师提醒|"
    r"温馨提示|后续安排|下节课安排|下节课计划|下一步安排)[：:]?|"
    r"(?:家长配合|家长建议|家长提醒|补充说明|补充建议|老师建议|老师提醒|"
    r"温馨提示|后续安排|下节课安排|下节课计划|下一步安排)[：:]?"
    r")\s*$",
    flags=re.MULTILINE,
)


def section(text: str, heading: str, next_heading: str | None = None) -> str:
    if heading not in text:
        return ""
    body = text.split(heading, maxsplit=1)[1]
    if next_heading and next_heading in body:
        body = body.split(next_heading, maxsplit=1)[0]
    return body.strip()


def validate(text: str) -> list[str]:
    """Return hard structural or forbidden-content errors."""

    errors: list[str] = []
    headings = re.findall(
        r"^(?:①课上内容|②课上反馈|③课后作业)$",
        text,
        flags=re.MULTILINE,
    )
    if headings != REQUIRED_HEADINGS:
        found = " | ".join(headings) if headings else "(none)"
        errors.append(
            "Visible plain-text section headings must be exactly: "
            + " | ".join(REQUIRED_HEADINGS)
            + f" ; found: {found}"
        )

    for heading in OLD_HEADINGS:
        if heading in text and heading not in REQUIRED_HEADINGS:
            errors.append(f"Old heading style is not allowed: {heading}")

    extra = EXTRA_SECTION_RE.search(text)
    if extra:
        errors.append(f"A fourth or supplemental visible section is not allowed: {extra.group(0)}")

    for pattern, message in FORBIDDEN_PATTERNS:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            errors.append(
                f"Forbidden parent-facing content matched /{pattern}/: {match.group(0)} ({message})"
            )

    metadata = text.split("①课上内容", maxsplit=1)[0]
    if not re.search(r"^学生[：:]", metadata, flags=re.MULTILINE):
        errors.append("Missing or misplaced metadata before section ①: 学生：")
    if not re.search(r"^日期[：:]", metadata, flags=re.MULTILINE):
        errors.append("Missing or misplaced metadata before section ①: 日期：")
    if not re.search(r"^(?:课次 / 主题|主题)[：:]", metadata, flags=re.MULTILINE):
        errors.append(
            "Missing or misplaced metadata before section ①: 课次 / 主题： or 主题："
        )

    if CLASS_COURSE_MARKERS.search(metadata) and not re.search(
        r"^班级[：:]", metadata, flags=re.MULTILINE
    ):
        errors.append(
            "Class-course marker found in metadata, but 班级： is missing. "
            "Course type—not student count—determines the format."
        )

    section_pairs = (
        ("①课上内容", "②课上反馈"),
        ("②课上反馈", "③课后作业"),
        ("③课后作业", None),
    )
    for heading, next_heading in section_pairs:
        if heading in headings and not section(text, heading, next_heading):
            errors.append(f"Visible section must not be empty: {heading}")

    return errors


def lint_style(text: str) -> list[str]:
    """Return non-structural warnings that require editorial review."""

    warnings: list[str] = []
    for label, pattern, repair in STYLE_PATTERNS:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            warnings.append(
                f"Style warning [{label}]: {repair}; matched: {match.group(0)}"
            )

    feedback = section(text, "②课上反馈", "③课后作业")
    need_count = len(re.findall(r"(?:仍|还)?需要|仍需|还需", feedback))
    practice_count = len(re.findall(r"练习", feedback))
    if need_count >= 3 or (need_count >= 2 and practice_count >= 2):
        warnings.append(
            "Style warning [重复使用需要类句式]: section ② uses 需要/仍需/还需 "
            f"{need_count} times and 练习 {practice_count} times; "
            "consolidate repeated judgments"
        )

    generic_praise_count = len(
        re.findall(
            r"(?:表现|状态|掌握)(?:也)?(?:很|挺|比较|较为)?(?:好|不错|良好)",
            feedback,
        )
    )
    if generic_praise_count >= 2:
        warnings.append(
            "Style warning [重复泛化表扬]: section ② repeats generic praise; "
            "state shared mastery once and keep only verified individual differences"
        )

    return warnings


def read_input(raw_path: str) -> str:
    if raw_path == "-":
        return sys.stdin.read()
    path = Path(raw_path)
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate parent-feedback structure and flag register risks."
    )
    parser.add_argument(
        "--strict-style",
        action="store_true",
        help="return a failing exit code when style warnings remain",
    )
    parser.add_argument("path", help="feedback TXT path or - for stdin")
    args = parser.parse_args(argv)

    try:
        text = read_input(args.path)
    except FileNotFoundError as exc:
        print(f"ERROR: file not found: {exc}", file=sys.stderr)
        return 2

    errors = validate(text)
    warnings = lint_style(text)

    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        for warning in warnings:
            print(f"- {warning}")
        return 1

    if warnings:
        print("FAIL STYLE" if args.strict_style else "PASS WITH WARNINGS")
        for warning in warnings:
            print(f"- {warning}")
        return 1 if args.strict_style else 0

    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
