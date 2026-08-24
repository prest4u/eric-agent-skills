#!/usr/bin/env python3
"""Structural and ethics checks for Qingyun advisory PDFs."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path

FORBIDDEN = (
    "上岸率",
    "录取概率",
    "青云知路",
    "青云志愿",
    "fixture",
    "SaaS",
    "tenant",
    "闭环",
    "主动作",
    "localhost",
    "公章",
    "国徽",
    "保证上岸",
    "一定录取",
)

REQUIRED = (
    "非正式官方文件",
    "不保证录取",
    "本文件不是教育考试院或高校官方文件",
    "本文件不构成录取、就业或薪资承诺",
    "最终以当年官方系统、招生计划和高校招生章程为准",
    "过期、缺失或相互冲突的数据，不得当作已核实事实",
)

SCENE_REQUIRED = {
    "service-brief": ("含什么", "不含什么"),
    "consent": ("待专业审查", "签字"),
    "profile": ("硬约束", "待补"),
    "plan": ("判断类型", "待核验"),
    "checklist": ("服从调剂", "志愿"),
    "signoff": ("签发", "不得覆盖"),
    "briefing": ("今晚", "不保证录取"),
    "subject": ("选科", "待观察"),
    "early-bird": ("早鸟", "不保证录取"),
    "teacher": ("不承诺录取", "转介"),
}

PAGE_BANDS = {
    "service-brief": (2, 4),
    "consent": (4, 6),
    "profile": (2, 4),
    "plan": (8, 16),
    "checklist": (2, 6),
    "signoff": (1, 2),
    "briefing": (2, 2),
    "subject": (4, 8),
    "early-bird": (1, 2),
    "teacher": (1, 2),
}


def run(*command: str) -> str:
    completed = subprocess.run(
        command,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return completed.stdout


def require_tool(name: str) -> None:
    if shutil.which(name) is None:
        raise SystemExit(f"Missing required local tool: {name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--scene", choices=sorted(SCENE_REQUIRED))
    parser.add_argument("--expect-pages", type=int)
    parser.add_argument("--allow-non-a4", action="store_true")
    args = parser.parse_args()

    pdf = Path(args.pdf).expanduser().resolve()
    if not pdf.is_file():
        raise SystemExit(f"PDF not found: {pdf}")

    for tool in ("pdfinfo", "pdffonts", "pdftotext", "qpdf"):
        require_tool(tool)

    info = run("pdfinfo", str(pdf))
    page_match = re.search(r"^Pages:\s+(\d+)\s*$", info, re.MULTILINE)
    size_match = re.search(r"^Page size:\s+(.+)$", info, re.MULTILINE)
    if not page_match or not size_match:
        raise SystemExit("Could not read page count or page size")

    pages = int(page_match.group(1))
    if args.expect_pages is not None and pages != args.expect_pages:
        raise SystemExit(f"Expected {args.expect_pages} pages, found {pages}")
    if args.scene and args.scene in PAGE_BANDS:
        low, high = PAGE_BANDS[args.scene]
        if pages < low or pages > high:
            raise SystemExit(
                f"Scene {args.scene} expected {low}-{high} pages, found {pages}"
            )
    if not args.allow_non_a4 and "A4" not in size_match.group(1):
        raise SystemExit(f"Expected A4 pages, found: {size_match.group(1)}")

    run("qpdf", "--check", str(pdf))
    extracted = run("pdftotext", str(pdf), "-")
    if len(extracted.strip()) < 20:
        raise SystemExit("Selectable text layer is empty or unexpectedly short")

    blank_pages = []
    for page_number in range(1, pages + 1):
        page_text = run(
            "pdftotext",
            "-f",
            str(page_number),
            "-l",
            str(page_number),
            str(pdf),
            "-",
        )
        if len(page_text.strip()) < 8:
            blank_pages.append(page_number)
    if blank_pages:
        raise SystemExit(
            "Pages with empty or unexpectedly short selectable text: "
            + ", ".join(map(str, blank_pages))
        )

    lowered = extracted
    for term in FORBIDDEN:
        if term.lower() in lowered.lower() if term.isascii() else term in lowered:
            raise SystemExit(f"Forbidden visible term: {term}")

    for phrase in REQUIRED:
        if phrase not in extracted:
            raise SystemExit(f"Missing required disclaimer or footer phrase: {phrase}")

    if args.scene:
        for phrase in SCENE_REQUIRED[args.scene]:
            if phrase not in extracted:
                raise SystemExit(f"Scene {args.scene} missing phrase: {phrase}")

    if re.search(r"\d{15,18}", extracted):
        raise SystemExit("Possible real ID-number-like digit run in visible text")

    fonts = run("pdffonts", str(pdf))
    font_rows = []
    for line in fonts.splitlines():
        match = re.search(
            r"\s+(yes|no)\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+\s*$", line
        )
        if match:
            font_rows.append(match.groups())
    if not font_rows:
        raise SystemExit("Could not parse embedded font status")
    if any(
        embedded != "yes" or unicode_map != "yes"
        for embedded, _, unicode_map in font_rows
    ):
        raise SystemExit("All fonts must be embedded and have Unicode mappings")

    print(
        f"PASS: {pdf.name} | scene={args.scene or '-'} | pages={pages} | "
        f"size=A4 | fonts={len(font_rows)} embedded | ethics=yes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
