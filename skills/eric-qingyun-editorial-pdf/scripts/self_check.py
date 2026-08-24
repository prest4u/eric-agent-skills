#!/usr/bin/env python3
"""Self-check for the 青云编辑纸本 skill: tokens, pages, banned brand words."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "theme.typ"
DEFAULT_PDF = ROOT / "samples" / "document.pdf"

# Paper: Document Master lock #E6E4DE (must leave C #F3F3F1). Other tokens from E-editorial/document.typ.
REQUIRED_THEME_SNIPPETS = (
    'rgb("#E6E4DE")',
    'rgb("#262626")',
    'rgb("#6B6B6B")',
    'rgb("#707070")',
    'rgb("#C8C8C4")',
    '("Songti SC", "STSong")',
    '("PingFang SC", "Hiragino Sans GB")',
    "top: 26mm",
    "bottom: 24mm",
    "left: 28mm",
    "right: 28mm",
    'display("一")',
    "10.5pt",
)

FORBIDDEN_THEME_SNIPPETS = (
    'rgb("#F3F3F1")',  # C near-white / rejected E study paper
    'rgb("#F6F3EA")',  # B warm ivory
    'rgb("#F4F5F3")',  # A slate-white paper
    'rgb("#5D6C75")',  # A primary rail
    'rgb("#4E6866")',  # D teal
    'rgb("#626A56")',  # B moss
    "rail-head",
    "split-rule",
)

FORBIDDEN_TEXT = (
    "青云知路",
    "青云志愿",
    "上岸率",
    "录取概率",
    "保证上岸",
    "一定录取",
    "公章",
    "国徽",
)

REQUIRED_TEXT = (
    "青云",
    "选科指导报告",
    "非正式官方文件",
    "不保证录取",
    "本文件不是教育考试院或高校官方文件",
    "本文件不构成录取、就业或薪资承诺",
    "最终以当年官方系统、招生计划和高校招生章程为准",
    "过期、缺失或相互冲突的数据，不得当作已核实事实",
    "待核验",
)


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


def check_theme() -> None:
    text = THEME.read_text(encoding="utf-8")
    missing = [s for s in REQUIRED_THEME_SNIPPETS if s not in text]
    if missing:
        raise SystemExit("theme.typ missing E tokens: " + ", ".join(missing))
    leaked = [s for s in FORBIDDEN_THEME_SNIPPETS if s in text]
    if leaked:
        raise SystemExit("theme.typ leaked A/B/C/D chrome: " + ", ".join(leaked))


def check_pdf(pdf: Path, expect_pages: int) -> int:
    for tool in ("pdfinfo", "pdftotext"):
        require_tool(tool)

    info = run("pdfinfo", str(pdf))
    page_match = re.search(r"^Pages:\s+(\d+)\s*$", info, re.MULTILINE)
    size_match = re.search(r"^Page size:\s+(.+)$", info, re.MULTILINE)
    if not page_match or not size_match:
        raise SystemExit("Could not read page count or page size")
    pages = int(page_match.group(1))
    if pages != expect_pages:
        raise SystemExit(f"Expected {expect_pages} pages, found {pages}")
    if "A4" not in size_match.group(1):
        raise SystemExit(f"Expected A4 pages, found: {size_match.group(1)}")

    extracted = run("pdftotext", str(pdf), "-")
    if len(extracted.strip()) < 20:
        raise SystemExit("Selectable text layer is empty or unexpectedly short")

    for term in FORBIDDEN_TEXT:
        if term in extracted:
            raise SystemExit(f"Forbidden visible term: {term}")

    for phrase in REQUIRED_TEXT:
        if phrase not in extracted:
            raise SystemExit(f"Missing required phrase: {phrase}")

    if "院校冲" in extracted or "冲稳保表" in extracted:
        raise SystemExit("Looks like a volunteer 冲稳保 table, not a 选科长文")

    return pages


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", default=str(DEFAULT_PDF))
    parser.add_argument("--expect-pages", type=int, default=4)
    parser.add_argument("--skip-theme", action="store_true")
    args = parser.parse_args()

    if not args.skip_theme:
        if not THEME.is_file():
            raise SystemExit(f"theme.typ missing: {THEME}")
        check_theme()

    pdf = Path(args.pdf).expanduser().resolve()
    if not pdf.is_file():
        raise SystemExit(f"PDF not found: {pdf}")

    pages = check_pdf(pdf, args.expect_pages)
    print(
        f"PASS: {pdf} | pages={pages} | A4 | "
        f"theme_tokens=E | banned_brands=none"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
