#!/usr/bin/env python3
"""Layout health checker for eric-soft-signal A4 PDF renders.

Calibration (170 dpi PNGs, BG_TOLERANCE=28):
- Known near-empty / fragment bad pages:
  - student-final p.8:  content_height_ratio ≈ 0.211, ink_coverage ≈ 0.0091
  - student-final2 p.17: content_height_ratio ≈ 0.242, ink_coverage ≈ 0.0069
- Known blank-ruled lower-half bad page:
  - student-complete p.18: content_height_ratio ≈ 0.746, ink_coverage ≈ 0.0189
    (ruled writing lines push the last foreground row down, so a simple height
    check misses it; the low-density heuristic catches it.)
- Known good pages (excluding covers / blank last pages):
  - student-release min content_height_ratio ≈ 0.329 (p.16, intentional writing
    page), min ink_coverage ≈ 0.0135
  - grammar-book/student min content_height_ratio ≈ 0.162 (p.12 blank last page,
    should be --ignore), min ink_coverage otherwise ≈ 0.036

Default thresholds chosen to catch the known bad pages without erroring on good
pages:
  near_empty          0.25   # p.8 / p.17 → error
  sparse              0.30   # avoids false warnings on release p.16 (0.329)
  low_density_height  0.70   # catches tall-but-thin pages like complete p.18
  low_density_ink     0.0190
  dense_height        0.95   # over-compression check, deliberately conservative
  dense_ink           0.08   # because pixel density did not cleanly separate
                             # the 9-page student-final from good releases
  pagebreak_threshold 3
  v_threshold         30
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterable

from PIL import Image


SOFT_PAPER = (255, 253, 248)
BG_TOLERANCE = 28

NEAR_EMPTY = 0.25
SPARSE = 0.30
LOW_DENSITY_HEIGHT = 0.70
LOW_DENSITY_INK = 0.0190
DENSE_HEIGHT = 0.95
DENSE_INK = 0.08

PAGEBREAK_THRESHOLD = 3
V_THRESHOLD = 30

PAGE_NAME = re.compile(r"page-(\d+)\.png$")
LEAK_PATTERN = re.compile(r"TEACHER|教师版|correct-index|/Users/")
SOURCE_PAGEBREAK = re.compile(r"#pagebreak\(\)")
SOURCE_V = re.compile(r"#v\(")
TEACHER_OPENER = re.compile(r"(?:#(?:tnote|twarn|show-ans)\(|teacher-note\s*:)")
INLINE_MCQ_SKIP = re.compile(r"soft-choice\(")
# Same-line run-on choice lists. Requires A. + B. + C. with option text
# after each letter. Lone "A." table cells and 2x2 four-box rows (A+B only)
# do not match.
INLINE_MCQ_RUNON = re.compile(
    r"(?<![A-Za-z0-9])A[.．]\s+\S.{0,70}?\s+B[.．]\s+\S.{0,70}?\s+C[.．]"
)
INLINE_MCQ_PAREN = re.compile(
    r"[（(]\s*A[.．]\s+\S.{0,70}?\s+B[.．]\s+\S.{0,70}?\s+C[.．]"
)


def page_number(path: Path) -> int:
    match = PAGE_NAME.fullmatch(path.name)
    if match is None:
        raise ValueError(f"Unexpected render name: {path.name}")
    return int(match.group(1))


def is_foreground(pixel: tuple[int, int, int]) -> bool:
    """Return True if a pixel is not the soft-paper background.

    BG_TOLERANCE=28 keeps soft-clay-pale #f8e9df (channel diffs 7,20,25) as
    content while rejecting anti-aliased background pixels.
    """
    r, g, b = pixel
    return (
        abs(r - SOFT_PAPER[0]) > BG_TOLERANCE
        or abs(g - SOFT_PAPER[1]) > BG_TOLERANCE
        or abs(b - SOFT_PAPER[2]) > BG_TOLERANCE
    )


def page_metrics(image_path: Path) -> dict:
    """Compute layout metrics for a single rendered page.

    Returns a dict with keys:
      - width, height
      - content_height_ratio: last foreground row / height
      - ink_coverage: fraction of foreground pixels
    """
    with Image.open(image_path) as rendered:
        rendered = rendered.convert("RGB")
        width, height = rendered.size
        pixels = rendered.load()

        foreground_pixels = 0
        last_foreground_row = 0
        for y in range(height):
            for x in range(width):
                if is_foreground(pixels[x, y]):
                    foreground_pixels += 1
                    last_foreground_row = y

        total_pixels = width * height
        return {
            "width": width,
            "height": height,
            "content_height_ratio": round((last_foreground_row + 1) / height, 4),
            "ink_coverage": round(foreground_pixels / total_pixels, 4),
        }


def render_pdf(pdf: Path, dpi: int) -> Path:
    """Render a PDF to a temporary directory of page-*.png files."""
    if shutil.which("pdftoppm") is None:
        raise RuntimeError("pdftoppm is required to render PDF input")

    temp_dir = Path(tempfile.mkdtemp(prefix="check_layout_"))
    prefix = temp_dir / "page"
    result = subprocess.run(
        ["pdftoppm", "-png", "-r", str(dpi), str(pdf), str(prefix)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"pdftoppm failed: {result.stderr}")
    return temp_dir


def collect_pages(input_path: Path, dpi: int) -> tuple[list[Path], Path | None]:
    """Return (sorted page image paths, optional temporary render directory)."""
    if input_path.is_dir():
        pages = sorted(input_path.glob("page-*.png"), key=page_number)
        if not pages:
            raise ValueError(f"No page-*.png renders found in {input_path}")
        return pages, None

    if input_path.is_file():
        temp_dir = render_pdf(input_path, dpi)
        pages = sorted(temp_dir.glob("page-*.png"), key=page_number)
        if not pages:
            raise ValueError(f"pdftoppm produced no pages for {input_path}")
        return pages, temp_dir

    raise ValueError(f"Input is not a file or directory: {input_path}")


def parse_ignore(raw: str | None) -> set[int]:
    if not raw:
        return set()
    return {int(part.strip()) for part in raw.split(",") if part.strip()}


def analyze_pages(
    pages: Iterable[Path],
    ignore: set[int],
    near_empty: float,
    sparse: float,
    low_density_height: float,
    low_density_ink: float,
    dense_height: float,
    dense_ink: float,
) -> tuple[list[dict], list[dict], dict]:
    """Classify each page and return (metrics, findings, summary)."""
    metrics: list[dict] = []
    findings: list[dict] = []
    ignored_count = 0

    for page in pages:
        number = page_number(page)
        if number in ignore:
            ignored_count += 1
            continue

        m = page_metrics(page)
        entry = {
            "page": number,
            "file": page.name,
            **m,
        }
        metrics.append(entry)

        ch = m["content_height_ratio"]
        ink = m["ink_coverage"]

        if ch < near_empty:
            findings.append(
                {
                    "page": number,
                    "severity": "error",
                    "category": "near-empty",
                    "message": f"页面利用率极低：内容仅占高度 {ch:.1%}",
                    "content_height_ratio": ch,
                    "ink_coverage": ink,
                }
            )
        elif ch < sparse:
            findings.append(
                {
                    "page": number,
                    "severity": "warning",
                    "category": "sparse",
                    "message": f"页面较空：内容占高度 {ch:.1%}",
                    "content_height_ratio": ch,
                    "ink_coverage": ink,
                }
            )

        if ch > low_density_height and ink < low_density_ink:
            findings.append(
                {
                    "page": number,
                    "severity": "warning",
                    "category": "low-density-tall-page",
                    "message": (
                        f"页面下部疑似空白（横线/浅色块撑满但墨量低）："
                        f"高度 {ch:.1%}，墨量 {ink:.2%}"
                    ),
                    "content_height_ratio": ch,
                    "ink_coverage": ink,
                }
            )

        if ch > dense_height and ink > dense_ink:
            findings.append(
                {
                    "page": number,
                    "severity": "warning",
                    "category": "over-compressed",
                    "message": f"页面可能过挤：高度 {ch:.1%}，墨量 {ink:.2%}",
                    "content_height_ratio": ch,
                    "ink_coverage": ink,
                }
            )

    errors = sum(1 for f in findings if f["severity"] == "error")
    warnings = sum(1 for f in findings if f["severity"] == "warning")
    summary = {
        "pages_checked": len(metrics),
        "pages_ignored": ignored_count,
        "errors": errors,
        "warnings": warnings,
        "clean": errors == 0 and warnings == 0,
    }
    return metrics, findings, summary


def iter_student_facing_lines(text: str) -> Iterable[tuple[int, str]]:
    """Yield (line_no, line) skipping comments and teacher-only blocks."""
    in_teacher = False
    depth = 0
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("//"):
            continue
        if in_teacher:
            depth += line.count("[") - line.count("]")
            if depth <= 0:
                in_teacher = False
                depth = 0
            continue
        if TEACHER_OPENER.search(line):
            depth = line.count("[") - line.count("]")
            if depth > 0:
                in_teacher = True
            continue
        if INLINE_MCQ_SKIP.search(line):
            continue
        yield line_no, line


def find_inline_mcq(text: str) -> list[dict]:
    """Flag run-on A. B. C. choice lists on one student-facing line."""
    findings: list[dict] = []
    for line_no, line in iter_student_facing_lines(text):
        if INLINE_MCQ_PAREN.search(line) or INLINE_MCQ_RUNON.search(line):
            preview = line.strip()
            if len(preview) > 80:
                preview = preview[:77] + "..."
            findings.append(
                {
                    "severity": "error",
                    "category": "inline-mcq",
                    "message": (
                        "单项选择写成了行内 A. B. C.，应改为 "
                        "#soft-question 的 A–D 四框（恰好 4 个选项）"
                    ),
                    "line": line_no,
                    "match": preview,
                }
            )
    return findings


def source_lint(path: Path, pagebreak_threshold: int, v_threshold: int) -> dict:
    """Count manual density-tuning markers and flag inline MCQ runs."""
    text = path.read_text(encoding="utf-8")
    pagebreak_count = len(SOURCE_PAGEBREAK.findall(text))
    v_count = len(SOURCE_V.findall(text))

    findings: list[dict] = []
    if pagebreak_count > pagebreak_threshold or v_count > v_threshold:
        findings.append(
            {
                "severity": "warning",
                "category": "suspected-manual-density-tuning",
                "message": (
                    f"检测到大量手动排版调整：pagebreak={pagebreak_count}，"
                    f"#v(={v_count}"
                ),
                "pagebreak_count": pagebreak_count,
                "v_count": v_count,
            }
        )
    findings.extend(find_inline_mcq(text))

    return {
        "file": path.name,
        "pagebreak_count": pagebreak_count,
        "v_count": v_count,
        "inline_mcq_count": sum(1 for f in findings if f["category"] == "inline-mcq"),
        "findings": findings,
        "clean": not findings,
    }


def leak_scan(pdf: Path) -> dict:
    """Scan a PDF for leaked teacher-edition markers."""
    if shutil.which("pdftotext") is None:
        raise RuntimeError("pdftotext is required for leak scan")

    result = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"pdftotext failed: {result.stderr}")

    findings: list[dict] = []
    for line_no, line in enumerate(result.stdout.splitlines(), start=1):
        for match in LEAK_PATTERN.finditer(line):
            findings.append(
                {
                    "severity": "error",
                    "category": "student-leak",
                    "message": f"学生版疑似泄漏教师内容：{match.group()!r}",
                    "line": line_no,
                    "match": match.group(),
                }
            )
    findings.extend(find_inline_mcq(result.stdout))

    return {
        "file": pdf.name,
        "findings": findings,
        "clean": not findings,
    }


def orphan_titles(pdf: Path, title_size: float, bottom_ratio: float) -> dict:
    """Detect title-sized text blocks stranded in the bottom of a page."""
    if shutil.which("pdftohtml") is None:
        return {
            "file": pdf.name,
            "findings": [],
            "clean": True,
            "note": "pdftohtml not available; orphan-title check skipped",
        }

    result = subprocess.run(
        ["pdftohtml", "-xml", "-stdout", str(pdf)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"pdftohtml failed: {result.stderr}")

    root = ET.fromstring(result.stdout)
    findings: list[dict] = []

    for page in root.findall("page"):
        page_width = int(page.get("width", 0))
        page_height = int(page.get("height", 0))
        if page_height == 0:
            continue

        fontspecs = {
            fs.get("id"): float(fs.get("size", 0))
            for fs in page.findall("fontspec")
        }
        blocks: list[dict] = []
        for text in page.findall("text"):
            top = float(text.get("top", 0))
            left = float(text.get("left", 0))
            font_id = text.get("font")
            size = fontspecs.get(font_id, 0.0)
            content = "".join(text.itertext()).strip()
            if not content:
                continue
            blocks.append(
                {
                    "top": top,
                    "left": left,
                    "size": size,
                    "text": content,
                }
            )

        threshold_y = page_height * (1 - bottom_ratio)
        for block in blocks:
            if block["size"] >= title_size and block["top"] >= threshold_y:
                # Stranded if no smaller body block appears below it.
                has_body_below = any(
                    other["size"] < block["size"] and other["top"] > block["top"]
                    for other in blocks
                )
                if not has_body_below:
                    findings.append(
                        {
                            "severity": "error",
                            "category": "stranded-heading",
                            "message": (
                                f"页面底部出现孤立标题（字号 {block['size']:.1f}pt）："
                                f"{block['text'][:40]!r}"
                            ),
                            "page": int(page.get("number", 0)),
                            "size": block["size"],
                            "text": block["text"],
                        }
                    )

    return {
        "file": pdf.name,
        "findings": findings,
        "clean": not findings,
    }


def human_summary(kind: str, payload: dict) -> str:
    """Return a short Chinese summary for stderr."""
    if "summary" in payload:
        errors = payload["summary"].get("errors", 0)
        warnings = payload["summary"].get("warnings", 0)
    else:
        findings = payload.get("findings", [])
        errors = sum(1 for f in findings if f.get("severity") == "error")
        warnings = sum(1 for f in findings if f.get("severity") == "warning")
    clean = payload.get("clean", True)

    if kind == "pages":
        checked = payload.get("summary", {}).get("pages_checked", 0)
        ignored = payload.get("summary", {}).get("pages_ignored", 0)
        return (
            f"体检 {checked} 页（忽略 {ignored} 页）："
            f"错误 {errors}，警告 {warnings}"
        )
    if kind == "source":
        return (
            f"源码检查：pagebreak={payload.get('pagebreak_count')}, "
            f"#v(={payload.get('v_count')}, "
            f"inline-mcq={payload.get('inline_mcq_count', 0)}；"
            f"错误 {errors}，警告 {warnings}"
        )
    if kind == "leak":
        return f"泄漏扫描：错误 {errors}，警告 {warnings}"
    if kind == "orphans":
        return f"孤立标题扫描：错误 {errors}，警告 {warnings}"
    return ""


def build_pages_parser(sub: argparse._SubParsersAction) -> None:
    parser = sub.add_parser("pages", help="Check rendered page layout metrics")
    parser.add_argument("input", type=Path, help="Directory of page-*.png or a PDF")
    parser.add_argument("--ignore", default="", help="Comma-separated page numbers to skip")
    parser.add_argument("--dpi", type=int, default=170, help="Rendering DPI for PDF input")
    parser.add_argument("--near-empty", type=float, default=NEAR_EMPTY)
    parser.add_argument("--sparse", type=float, default=SPARSE)
    parser.add_argument("--low-density-height", type=float, default=LOW_DENSITY_HEIGHT)
    parser.add_argument("--low-density-ink", type=float, default=LOW_DENSITY_INK)
    parser.add_argument("--dense-height", type=float, default=DENSE_HEIGHT)
    parser.add_argument("--dense-ink", type=float, default=DENSE_INK)


def build_source_parser(sub: argparse._SubParsersAction) -> None:
    parser = sub.add_parser(
        "source",
        help="Lint Typst source for manual density tuning and inline A.B.C. MCQs",
    )
    parser.add_argument("typ", type=Path)
    parser.add_argument("--pagebreak-threshold", type=int, default=PAGEBREAK_THRESHOLD)
    parser.add_argument("--v-threshold", type=int, default=V_THRESHOLD)


def build_leak_parser(sub: argparse._SubParsersAction) -> None:
    parser = sub.add_parser("leak", help="Scan a student PDF for teacher-edition leaks")
    parser.add_argument("pdf", type=Path)


def build_orphans_parser(sub: argparse._SubParsersAction) -> None:
    parser = sub.add_parser("orphans", help="Detect stranded headings near page bottoms")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--title-size", type=float, default=12.4)
    parser.add_argument("--bottom-ratio", type=float, default=0.12)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Layout health checker for eric-soft-signal PDF renders"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    build_pages_parser(sub)
    build_source_parser(sub)
    build_leak_parser(sub)
    build_orphans_parser(sub)
    args = parser.parse_args()

    result: dict = {}
    has_error = False

    if args.command == "pages":
        pages, temp_dir = collect_pages(args.input, args.dpi)
        try:
            metrics, findings, summary = analyze_pages(
                pages,
                parse_ignore(args.ignore),
                args.near_empty,
                args.sparse,
                args.low_density_height,
                args.low_density_ink,
                args.dense_height,
                args.dense_ink,
            )
        finally:
            if temp_dir is not None:
                shutil.rmtree(temp_dir, ignore_errors=True)

        result = {
            "command": "pages",
            "pages": metrics,
            "findings": findings,
            "summary": summary,
        }
        has_error = summary.get("errors", 0) > 0
        sys.stderr.write(human_summary("pages", result) + "\n")

    elif args.command == "source":
        result = source_lint(args.typ, args.pagebreak_threshold, args.v_threshold)
        result["command"] = "source"
        has_error = any(f["severity"] == "error" for f in result.get("findings", []))
        sys.stderr.write(human_summary("source", result) + "\n")

    elif args.command == "leak":
        result = leak_scan(args.pdf)
        result["command"] = "leak"
        has_error = any(f["severity"] == "error" for f in result.get("findings", []))
        sys.stderr.write(human_summary("leak", result) + "\n")

    elif args.command == "orphans":
        result = orphan_titles(args.pdf, args.title_size, args.bottom_ratio)
        result["command"] = "orphans"
        has_error = any(f["severity"] == "error" for f in result.get("findings", []))
        sys.stderr.write(human_summary("orphans", result) + "\n")

    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 1 if has_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
