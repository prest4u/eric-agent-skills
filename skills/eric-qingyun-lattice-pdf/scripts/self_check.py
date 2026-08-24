#!/usr/bin/env python3
"""Self-check for the 青云藤紫点阵 skill: paper, FangSong, dots, pages, banned words."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "theme.typ"
DOCUMENT = ROOT / "samples" / "document.typ"
DEFAULT_PDF = ROOT / "samples" / "document.pdf"

PAPER = (0xB7, 0xA8, 0xC8)
BANNED_PAPERS = {
    "near-white": (0xF4, 0xF5, 0xF3),
    "#E6E4DE": (0xE6, 0xE4, 0xDE),
    "#D2CBB8": (0xD2, 0xCB, 0xB8),
    "#C9C6BF": (0xC9, 0xC6, 0xBF),
    "#DDE8E4": (0xDD, 0xE8, 0xE4),
    "#F3F3F1": (0xF3, 0xF3, 0xF1),
}

REQUIRED_THEME_SNIPPETS = (
    'rgb("#B7A8C8")',
    "STFangsong",
    "5mm",
    "lattice",
    "circle",
)

FORBIDDEN_THEME_SNIPPETS = (
    'rgb("#E6E4DE")',
    'rgb("#D2CBB8")',
    'rgb("#C9C6BF")',
    'rgb("#DDE8E4")',
    'rgb("#F3F3F1")',
    "band-h",
    'display("一")',
    "left: 28mm",
    "right: 28mm",
    "columns-n = 6",
    "punch",
    "binder-holes",
    "Kaiti",
    "Xingkai",
    "news-six",
)

FORBIDDEN_DOC_SNIPPETS = (
    'rgb("#E6E4DE")',
    'rgb("#D2CBB8")',
    "band-h",
    'display("一")',
    "left: 28mm",
    "right: 28mm",
    "news-six",
    "columns-n",
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
    "青云纪录",
    "藤紫点阵",
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


def check_theme() -> None:
    text = THEME.read_text(encoding="utf-8")
    missing = [s for s in REQUIRED_THEME_SNIPPETS if s not in text]
    if missing:
        raise SystemExit("theme.typ missing lattice tokens: " + ", ".join(missing))
    leaked = [s for s in FORBIDDEN_THEME_SNIPPETS if s in text]
    if leaked:
        raise SystemExit("theme.typ leaked E/J/I chrome: " + ", ".join(leaked))
    if DOCUMENT.is_file():
        doc = DOCUMENT.read_text(encoding="utf-8")
        leaked_doc = [s for s in FORBIDDEN_DOC_SNIPPETS if s in doc]
        if leaked_doc:
            raise SystemExit("document.typ leaked forbidden chrome: " + ", ".join(leaked_doc))
        if "news-six" in doc or "columns(" in doc:
            raise SystemExit("document.typ uses columns — lattice is single-column")


def check_pdf_text(pdf: Path, expect_pages: int) -> tuple[int, str]:
    for tool in ("pdfinfo", "pdftotext", "pdffonts"):
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

    footer_ok = ("非正式官方文件" in extracted) and ("不保证录取" in extracted) and ("青云" in extracted)
    if not footer_ok:
        raise SystemExit("Footer phrases missing")

    fonts = run("pdffonts", str(pdf))
    font_blob = fonts.lower()
    if "fang" not in font_blob and "仿宋" not in fonts:
        raise SystemExit(f"Expected FangSong/STFangsong in pdffonts, got:\n{fonts}")
    if re.search(r"kaiti|kai\b", font_blob) and "fang" not in font_blob:
        raise SystemExit("Kai font present without FangSong — lattice is FangSong throughout")
    if re.search(r"heiti|sthei", font_blob):
        raise SystemExit("Heiti present — lattice bans black Heiti headlines")

    layout = run("pdftotext", "-layout", "-f", "1", "-l", "1", str(pdf), "-")
    lines = [ln.rstrip() for ln in layout.splitlines() if ln.strip()]
    title_lines = [ln for ln in lines if "选科指导报告" in ln]
    if not title_lines:
        raise SystemExit("Cover missing 选科指导报告")
    title = title_lines[0]
    lead_spaces = len(title) - len(title.lstrip(" "))
    if lead_spaces > 18:
        raise SystemExit(f"Cover title does not look left-aligned (leading spaces={lead_spaces})")
    # 青云 should appear on the cover page near the title, not only in a far-right masthead.
    if "青云" not in layout:
        raise SystemExit("Cover page missing 青云")

    return pages, extracted


def render_pages(pdf: Path, tmp: Path, dpi: int = 150) -> list[Path]:
    require_tool("pdftoppm")
    prefix = tmp / "page"
    subprocess.run(
        ["pdftoppm", "-png", "-r", str(dpi), str(pdf), str(prefix)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    pages = sorted(tmp.glob("page-*.png"))
    if not pages:
        raise SystemExit("pdftoppm produced no page images")
    return pages


def _luma(p) -> float:
    return 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]


def sample_paper(img: Image.Image) -> tuple[tuple[int, int, int], str]:
    rgb = img.convert("RGB")
    w, h = rgb.size
    # Corners are paper (dots sit 5mm inward from 0,0). Sample a few near-corner pixels.
    corners = [
        rgb.getpixel((18, 18)),
        rgb.getpixel((w - 19, 18)),
        rgb.getpixel((18, h - 19)),
        rgb.getpixel((w - 19, h - 19)),
    ]
    sample = corners[0]
    d_paper = dist(sample, PAPER)
    if d_paper > 22:
        raise SystemExit(
            f"Paper sample {sample} is not close to #B7A8C8 (dist={d_paper:.1f}); corners={corners}"
        )
    luma = _luma(sample)
    if luma > 220:
        raise SystemExit(f"Paper looks near-white (luma={luma:.1f}, sample={sample})")
    for name, banned in BANNED_PAPERS.items():
        if dist(sample, banned) < 22 and dist(sample, PAPER) > dist(sample, banned):
            raise SystemExit(f"Paper sample {sample} collided with banned paper {name} {banned}")
    return sample, f"paper_sample={sample} dist_to_#B7A8C8={d_paper:.1f}"


def check_lattice(img: Image.Image, dpi: int = 150) -> str:
    rgb = img.convert("RGB")
    w, h = rgb.size
    px_mm = dpi / 25.4
    step = 5 * px_mm
    # Circles are placed by top-left of the bbox, radius ~0.48mm, so the centre
    # sits ~0.48mm in from each 5mm lattice node.
    r_px = 0.48 * px_mm
    paper_luma = _luma(PAPER)

    hits = 0
    misses = 0
    off_grid = 0
    # Probe expected centres in the top-left margin (avoid body type).
    for j in range(1, 6):
        for i in range(2, 14):
            x = int(round(i * step + r_px))
            y = int(round(j * step + r_px))
            if x >= w - 4 or y >= h - 4:
                continue
            p = rgb.getpixel((x, y))
            if _luma(p) < paper_luma - 5:
                hits += 1
            else:
                misses += 1
            # Midway between nodes should stay close to paper (not a line grid).
            mx = int(round((i + 0.5) * step + r_px))
            my = int(round((j + 0.5) * step + r_px))
            if mx < w - 4 and my < h - 4:
                if _luma(rgb.getpixel((mx, my))) < paper_luma - 8:
                    off_grid += 1

    total = hits + misses
    if total < 12:
        raise SystemExit("Lattice probe region too small")
    hit_rate = hits / total
    if hit_rate < 0.55:
        raise SystemExit(
            f"Dot lattice not visible on 5mm grid (hit_rate={hit_rate:.2f} hits={hits} misses={misses})"
        )
    if off_grid > max(3, total * 0.2):
        raise SystemExit(
            f"Looks like a line grid, not circular dots (off-grid dark={off_grid})"
        )

    # Frame heuristic: a 6mm inset frame is a continuous dark band.
    def edge_dark_ratio(box):
        e = rgb.crop(box)
        pix = e.load()
        ew, eh = e.size
        vals = [_luma(pix[x, y]) for y in range(eh) for x in range(ew)]
        m = sum(vals) / len(vals)
        return sum(1 for v in vals if v < m - 18) / len(vals)

    def mm(n: float) -> int:
        return int(n * px_mm)

    frame_hits = [
        edge_dark_ratio((mm(5.5), mm(40), mm(6.7), h - mm(40))),
        edge_dark_ratio((w - mm(6.7), mm(40), w - mm(5.5), h - mm(40))),
        edge_dark_ratio((mm(40), mm(5.5), w - mm(40), mm(6.7))),
        edge_dark_ratio((mm(40), h - mm(6.7), w - mm(40), h - mm(5.5))),
    ]
    if sum(1 for r in frame_hits if r > 0.35) >= 3:
        raise SystemExit(f"Looks like a page frame (edge dark ratios={frame_hits})")

    return f"lattice hit_rate={hit_rate:.2f} off_grid={off_grid}"


def check_visual(pdf: Path) -> str:
    require_tool("pdftoppm")
    notes = []
    with tempfile.TemporaryDirectory(prefix="qingyun-lattice-") as td:
        tmp = Path(td)
        pages = render_pages(pdf, tmp, dpi=150)
        if len(pages) < 1:
            raise SystemExit("No rendered pages")
        cover = Image.open(pages[0])
        sample, paper_note = sample_paper(cover)
        notes.append(paper_note)
        notes.append(check_lattice(cover))
        # Interior pages should be the same paper, not a different stock.
        if len(pages) >= 2:
            interior = Image.open(pages[1])
            sample2, _ = sample_paper(interior)
            if dist(sample, sample2) > 24:
                raise SystemExit(f"Cover paper {sample} differs from interior {sample2}")
    return " | ".join(notes)


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

    pages, _ = check_pdf_text(pdf, args.expect_pages)
    visual = check_visual(pdf)
    print(
        f"PASS: {pdf} | pages={pages} | A4 | "
        f"theme_tokens=lattice-N | paper=#B7A8C8 | fonts=FangSong | "
        f"banned_brands=none | {visual}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
