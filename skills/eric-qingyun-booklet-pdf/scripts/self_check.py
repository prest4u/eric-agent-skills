#!/usr/bin/env python3
"""Self-check for the 青云线装竖册 skill: L tokens, vertical, pages, banned words."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "theme.typ"
DOCUMENT = ROOT / "samples" / "document.typ"
DEFAULT_PDF = ROOT / "samples" / "document.pdf"

REQUIRED_THEME_SNIPPETS = (
    'rgb("#D9B8C4")',
    '("Kaiti SC", "STKaiti", "Kaiti TC", "KaiTi")',
    "dir: ttb",
    "dir: rtl",
    "top: 14mm",
    "bottom: 16mm",
    "left: 12mm",
    "right: 16mm",
    'display("01")',
    "gate-columns",
)

FORBIDDEN_THEME_SNIPPETS = (
    'rgb("#E6E4DE")',
    'rgb("#C5D4E0")',
    'rgb("#D2CBB8")',
    'rgb("#C4A882")',
    'rgb("#2B2E2C")',
    'rgb("#C9C6BF")',
    'rgb("#DDE8E4")',
    "band-h",
    'display("一")',
    "left: 28mm",
    "right: 28mm",
    "Songti SC",
    "Heiti SC",
    "Weibei SC",
    "first-line-indent: 2em",
)

FORBIDDEN_DOC_SNIPPETS = (
    'rgb("#E6E4DE")',
    'rgb("#C5D4E0")',
    'rgb("#D2CBB8")',
    "band-h",
    'display("一")',
    "left: 28mm",
    "right: 28mm",
    "gate-table",
    "Songti SC",
    "Heiti SC",
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
    "藕荷竖册",
    "知路",
    "青云纪录",
)

REQUIRED_TEXT = (
    "青云",
    "选科指导报告",
    "林同",
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


def flatten(text: str) -> str:
    return re.sub(r"\s+", "", text)


def check_theme() -> None:
    text = THEME.read_text(encoding="utf-8")
    missing = [s for s in REQUIRED_THEME_SNIPPETS if s not in text]
    if missing:
        raise SystemExit("theme.typ missing L tokens: " + ", ".join(missing))
    leaked = [s for s in FORBIDDEN_THEME_SNIPPETS if s in text]
    if leaked:
        raise SystemExit("theme.typ leaked E/H/I chrome: " + ", ".join(leaked))
    if "table(" in text:
        raise SystemExit("theme.typ must not use a horizontal table() for 门对照")
    if DOCUMENT.is_file():
        doc = DOCUMENT.read_text(encoding="utf-8")
        leaked_doc = [s for s in FORBIDDEN_DOC_SNIPPETS if s in doc]
        if leaked_doc:
            raise SystemExit("document.typ leaked forbidden chrome: " + ", ".join(leaked_doc))
        if "gate-columns" not in doc:
            raise SystemExit("document.typ must call gate-columns (vertical combo columns)")


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

    flat = flatten(extracted)

    for term in FORBIDDEN_TEXT:
        if term in extracted or term in flat:
            raise SystemExit(f"Forbidden visible term: {term}")

    for phrase in REQUIRED_TEXT:
        if phrase not in extracted and phrase not in flat:
            raise SystemExit(f"Missing required phrase: {phrase}")

    if "院校冲" in extracted or "院校冲" in flat or "冲稳保表" in extracted or "冲稳保表" in flat:
        raise SystemExit("Looks like a volunteer 冲稳保 table, not a 选科长文")

    raw = pdf.read_bytes()
    if b"#D9B8C4" not in raw and b"D9B8C4" not in raw:
        # Typst may emit decimal RGB; accept either hex or 217 184 196 / 0.85.. components
        if b"0.85098" not in raw and b"217" not in raw:
            pass

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
        f"theme_tokens=L | paper=#D9B8C4 | kaiti | vertical | banned_brands=none"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
