#!/usr/bin/env python3
"""Self-check for the 青云票根 skill: O tokens, pages, paper hue, banned words."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "theme.typ"
DOCUMENT = ROOT / "samples" / "document.typ"
DEFAULT_PDF = ROOT / "samples" / "document.pdf"

REQUIRED_THEME_SNIPPETS = (
    'rgb("#D08A72")',
    'rgb("#111111")',
    "Heiti SC",
    "Xingkai SC",
    "stub-h = 22mm",
    "ticket-chrome",
)

FORBIDDEN_THEME_SNIPPETS = (
    'rgb("#C4A882")',
    'rgb("#EFE4D0")',
    'rgb("#D2CBB8")',
    'rgb("#DDE8E4")',
    'rgb("#F4F5F3")',
    'rgb("#FFFFFF")',
    'rgb("#FAFAFA")',
    "band-h",
    "columns-n",
    "punch-gutter",
    "frame-inset",
    "vermilion",
    "rail-head",
    'display("一")',
    "left: 28mm",
    "right: 28mm",
)

FORBIDDEN_DOC_SNIPPETS = (
    'rgb("#C4A882")',
    'rgb("#EFE4D0")',
    'rgb("#D2CBB8")',
    "band-h",
    "columns-n",
    "punch-gutter",
    "frame-inset",
    "vermilion",
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
    "砖红票根",
    "青云纪录",
    "DOCUMENT",
    "STATUS",
    "客户可见",
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
    "案例合成-TJ2026-0042",
)

TARGET_PAPER = (0xD0, 0x8A, 0x72)


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
        raise SystemExit("theme.typ missing O tokens: " + ", ".join(missing))
    leaked = [s for s in FORBIDDEN_THEME_SNIPPETS if s in text]
    if leaked:
        raise SystemExit("theme.typ leaked J/I/D/F chrome: " + ", ".join(leaked))
    if "Xingkai" not in text or "Heiti" not in text:
        raise SystemExit("theme.typ missing Heiti / Xingkai font stack")
    if DOCUMENT.is_file():
        doc = DOCUMENT.read_text(encoding="utf-8")
        leaked_doc = [s for s in FORBIDDEN_DOC_SNIPPETS if s in doc]
        if leaked_doc:
            raise SystemExit("document.typ leaked forbidden chrome: " + ", ".join(leaked_doc))
        if "砖红票根" in doc:
            raise SystemExit("document.typ prints internal skin name")


def rgb_is_brick_red(r: int, g: int, b: int) -> bool:
    if r < 170 or r > 230:
        return False
    if g > 165:
        return False
    if b > 150:
        return False
    if (r - g) < 40:
        return False
    if (g - b) > 50:
        return False
    return True


def median_rgb(pixels: list[tuple[int, int, int]]) -> tuple[int, int, int]:
    rs = sorted(p[0] for p in pixels)
    gs = sorted(p[1] for p in pixels)
    bs = sorted(p[2] for p in pixels)
    mid = len(pixels) // 2
    return rs[mid], gs[mid], bs[mid]


def sample_patch(im: Image.Image, x: int, y: int, radius: int = 2) -> tuple[int, int, int]:
    w, h = im.size
    pix = []
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            xx = min(max(x + dx, 0), w - 1)
            yy = min(max(y + dy, 0), h - 1)
            pix.append(im.getpixel((xx, yy)))
    return median_rgb(pix)


def check_paper_color(pdf: Path) -> str:
    require_tool("pdftoppm")
    with tempfile.TemporaryDirectory() as tmp:
        prefix = Path(tmp) / "p"
        run("pdftoppm", "-png", "-r", "72", "-f", "1", "-l", "1", str(pdf), str(prefix))
        pngs = list(Path(tmp).glob("*.png"))
        if not pngs:
            raise SystemExit("pdftoppm produced no page-1 PNG")
        im = Image.open(pngs[0]).convert("RGB")
        w, h = im.size
        # Upper-right body field: away from left title, above the 22mm stub.
        points = [
            (int(w * 0.82), int(h * 0.10)),
            (int(w * 0.78), int(h * 0.16)),
            (int(w * 0.88), int(h * 0.20)),
        ]
        samples = [sample_patch(im, x, y) for x, y in points]
        r, g, b = median_rgb(samples)
        if not rgb_is_brick_red(r, g, b):
            raise SystemExit(
                f"Paper sample not brick-red (got #{r:02X}{g:02X}{b:02X}; "
                "need hue toward red, not sand/yellow-brown)"
            )
        # Also reject if the sample is far from the locked token.
        tr, tg, tb = TARGET_PAPER
        if abs(r - tr) > 28 or abs(g - tg) > 28 or abs(b - tb) > 28:
            raise SystemExit(
                f"Paper sample #{r:02X}{g:02X}{b:02X} too far from locked #D08A72"
            )
        return f"#{r:02X}{g:02X}{b:02X}"


def check_pdf(pdf: Path, expect_pages: int) -> tuple[int, str]:
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
        raise SystemExit("Looks like a volunteer 冲稳保 table, not a 选科指导报告")

    paper_hex = check_paper_color(pdf)
    return pages, paper_hex


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

    pages, paper_hex = check_pdf(pdf, args.expect_pages)
    print(
        f"PASS: {pdf} | pages={pages} | A4 | "
        f"theme_tokens=O | paper=#D08A72 sample={paper_hex} | "
        f"fonts=Heiti+Xingkai | banned_brands=none | stub=22mm"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
