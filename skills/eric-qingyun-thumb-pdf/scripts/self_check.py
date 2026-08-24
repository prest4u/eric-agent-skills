#!/usr/bin/env python3
"""Self-check for the 青云军绿指索 skill: paper, clerical fonts, thumb tabs, bans."""

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

PAPER = (0x8B, 0x91, 0x70)
FORBIDDEN_PAPERS = {
    "sand-F": (0xC4, 0xA8, 0x82),
    "frost-H": (0xC5, 0xD4, 0xE0),
    "night-G": (0x2B, 0x2E, 0x2C),
    "binder-J": (0xC9, 0xC6, 0xBF),
    "news-I": (0xD2, 0xCB, 0xB8),
    "white": (0xF7, 0xF7, 0xF4),
}

REQUIRED_THEME_SNIPPETS = (
    "#8B9170",
    "Baoli",
    "Libian",
    "tab-centers",
    "thumb-index",
    "15.2mm",
)

FORBIDDEN_THEME_SNIPPETS = (
    "#C4A882",
    "#C5D4E0",
    "#2B2E2C",
    "#C9C6BF",
    "#D2CBB8",
    "vermilion",
    "page-frame",
    "studio-seal",
    "binder-holes",
    "punch-gutter",
    "strip-w",
    "right-strip",
    "Kaiti",
    "Heiti",
    "Songti",
    "Xingkai",
    "Weibei",
    "rail-head",
)

FORBIDDEN_TEXT = (
    "军绿指索",
    "青云知路",
    "青云志愿",
    "知路",
    "未来教育",
    "志愿填报",
    "冲稳保",
    "上岸率",
    "录取概率",
    "保证上岸",
    "一定录取",
    "公章",
    "国徽",
    "朱印砂卷",
    "霜蓝通缘",
    "活页齿孔",
    "DOCUMENT",
    "STATUS",
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

CLERICAL_RE = re.compile(r"Baoli|Libian|LiBian|Lishu|\u96b6", re.I)
BANNED_FONT_RE = re.compile(
    r"Kaiti|STKaiti|Heiti|STHeiti|Songti|STSong|Xingkai|Weibei|PingFang",
    re.I,
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


def dist(a, b) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5


def lum(c) -> float:
    return 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]


def check_theme() -> None:
    text = THEME.read_text(encoding="utf-8")
    missing = [s for s in REQUIRED_THEME_SNIPPETS if s not in text]
    if missing:
        raise SystemExit("theme.typ missing thumb tokens: " + ", ".join(missing))
    leaked = [s for s in FORBIDDEN_THEME_SNIPPETS if s in text]
    if leaked:
        raise SystemExit("theme.typ leaked H/F/J chrome: " + ", ".join(leaked))
    if "Kaiti" in text or "Heiti" in text or "Songti" in text:
        raise SystemExit("theme.typ must not use Kai/Hei/Song")
    print("PASS: theme tokens paper=#8B9170 clerical=Baoli/Libian thumb-index")


def check_pdf_text(pdf: Path, expect_pages: int) -> str:
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
    print(f"PASS: pages={pages} A4")

    extracted = run("pdftotext", str(pdf), "-")
    if len(extracted.strip()) < 20:
        raise SystemExit("Selectable text layer is empty or unexpectedly short")

    for term in FORBIDDEN_TEXT:
        if term in extracted:
            raise SystemExit(f"Forbidden visible term: {term}")
    print("PASS: banned strings absent (军绿指索/知路/冲稳保/朱印...)")

    for phrase in REQUIRED_TEXT:
        if phrase not in extracted:
            raise SystemExit(f"Missing required phrase: {phrase}")
    print("PASS: required phrases present (青云/非正式官方文件/不保证录取)")
    return extracted


def check_fonts(pdf: Path) -> None:
    require_tool("pdffonts")
    out = run("pdffonts", str(pdf))
    if not CLERICAL_RE.search(out):
        raise SystemExit("pdffonts: expected clerical face (Baoli/Libian/隶), got:\n" + out)
    banned = []
    for line in out.splitlines()[2:]:
        if BANNED_FONT_RE.search(line):
            banned.append(line.strip())
    if banned:
        raise SystemExit("pdffonts leaked Kai/Hei/Song/etc: " + " | ".join(banned))
    print("PASS: fonts clerical (Baoli/Libian), no Kai/Hei/Song")


def sample_paper_color(im: Image.Image) -> tuple[int, int, int]:
    w, h = im.size
    px = im.load()
    samples = []
    for y in range(int(h * 0.10), int(h * 0.78), 7):
        for x in range(int(w * 0.10), int(w * 0.68), 7):
            c = px[x, y][:3]
            L = lum(c)
            if 85 <= L <= 175:
                samples.append(c)
    if len(samples) < 30:
        raise SystemExit("Could not sample enough paper pixels")
    samples.sort(key=lum)
    mid = samples[len(samples) // 2]
    return mid


def tab_run_count(im: Image.Image, paper_rgb) -> tuple[int, float]:
    w, h = im.size
    px = im.load()
    px_per_mm = w / 210.0
    xs = [int(w - mm * px_per_mm) for mm in (1.4, 2.2)]
    xs = [max(0, min(w - 1, x)) for x in xs]
    paper_l = lum(paper_rgb)

    def is_tab_row(y: int) -> bool:
        for x in xs:
            c = px[x, y][:3]
            if dist(c, paper_rgb) <= 16:
                continue
            L = lum(c)
            dark_olive = L < paper_l - 8 and 30 < L < 135
            cream_label = L > paper_l + 12 and c[0] > 180
            if dark_olive or cream_label:
                return True
        return False

    flags = [is_tab_row(y) for y in range(h)]
    raw = []
    y = 0
    while y < h:
        if not flags[y]:
            y += 1
            continue
        start = y
        while y < h and flags[y]:
            y += 1
        raw.append([start, y])

    merged = []
    gap_px = 6.0 * px_per_mm
    for run in raw:
        if not merged or run[0] - merged[-1][1] > gap_px:
            merged.append(run)
        else:
            merged[-1][1] = run[1]

    n = 0
    for a, b in merged:
        height_mm = (b - a) / px_per_mm
        if 10.0 <= height_mm <= 24.0:
            n += 1
    dark_frac = sum(1 for v in flags if v) / float(h)
    return n, dark_frac


def check_visual(pdf: Path) -> None:
    require_tool("pdftoppm")
    with tempfile.TemporaryDirectory(prefix="qingyun-thumb-") as tmp:
        prefix = str(Path(tmp) / "page")
        subprocess.run(
            ["pdftoppm", "-png", "-r", "120", str(pdf), prefix],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        pages = sorted(Path(tmp).glob("page*.png"))
        if len(pages) != 4:
            raise SystemExit(f"pdftoppm produced {len(pages)} images, expected 4")

        fracs = []
        counts = []
        papers = []
        for i, path in enumerate(pages):
            im = Image.open(path).convert("RGB")
            paper_rgb = sample_paper_color(im)
            papers.append(paper_rgb)
            d_paper = dist(paper_rgb, PAPER)
            if d_paper > 42:
                raise SystemExit(
                    f"page {i+1} paper {paper_rgb} too far from #8B9170 (d={d_paper:.1f})"
                )
            for name, rgb in FORBIDDEN_PAPERS.items():
                if dist(paper_rgb, rgb) < d_paper:
                    raise SystemExit(
                        f"page {i+1} paper {paper_rgb} closer to {name} {rgb} than #8B9170"
                    )
            n, frac = tab_run_count(im, paper_rgb)
            counts.append(n)
            fracs.append(frac)

        mean_paper = tuple(sum(p[k] for p in papers) // 4 for k in range(3))
        print(
            f"PASS: paper ~#{mean_paper[0]:02X}{mean_paper[1]:02X}{mean_paper[2]:02X} "
            f"(target #8B9170, not sand/frost/night/white)"
        )

        if counts[0] != 1:
            raise SystemExit(f"cover should have 1 thumb tab, found {counts[0]}")
        print("PASS: cover has 1 right-edge thumb tab")

        for i, n in enumerate(counts[1:], start=2):
            if n != 4:
                raise SystemExit(f"page {i} should have 4 thumb tabs, found {n}")
        print("PASS: inner pages have 4 right-edge thumb tabs")

        if any(f > 0.45 for f in fracs):
            raise SystemExit(
                f"right edge looks like a full-height bar (dark fractions={fracs})"
            )
        print("PASS: right edge is teeth, not a full-height H strip")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", default=str(DEFAULT_PDF))
    parser.add_argument("--expect-pages", type=int, default=4)
    parser.add_argument("--skip-theme", action="store_true")
    parser.add_argument("--skip-visual", action="store_true")
    args = parser.parse_args()

    if not args.skip_theme:
        if not THEME.is_file():
            raise SystemExit(f"theme.typ missing: {THEME}")
        check_theme()

    pdf = Path(args.pdf).expanduser().resolve()
    if not pdf.is_file():
        raise SystemExit(f"PDF not found: {pdf}")

    check_pdf_text(pdf, args.expect_pages)
    check_fonts(pdf)
    if not args.skip_visual:
        check_visual(pdf)

    print(
        f"PASS: {pdf} | pages={args.expect_pages} | A4 | "
        f"theme_tokens=thumb-M | paper=#8B9170 | clerical | tabs=1/4/4/4 | banned_brands=none"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
