#!/usr/bin/env python3
"""Freshly compile a Typst source, validate A4 PDF gates, and render key pages."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

try:
    import fitz  # type: ignore
except ImportError:  # pragma: no cover - exercised through dependency probe
    fitz = None


SKILL_ROOT = Path(__file__).resolve().parents[1]
A4_WIDTH = 595.276
A4_HEIGHT = 841.89
CORE_VISUAL_CHECKS = {"cover", "first-body", "final"}
DENSE_VISUAL_CHECKS = {"dense", "table", "workspace", "diagram", "formula"}
SOURCE_LEAK_TERMS = (
    "挖坑", "心法", "出招", "拆招", "定招", "教师动作", "话术", "source ID", "source_id"
)
STUDENT_FORBIDDEN_TERMS = (
    "教师版", "教师解析", "教师用", "教师提示", "教师讲评", "评分点", "评分标准",
    "板书", "完整解答", "完整解析", "teacher-only",
)


class DependencyError(RuntimeError):
    """Raised when a required local dependency is unavailable."""


def result(ok: bool, **details: Any) -> dict[str, Any]:
    return {"ok": ok, **details}


def require_dependencies(typst_command: str) -> str:
    if fitz is None:
        raise DependencyError(
            "PyMuPDF is required for PDF structure checks and PNG rendering; "
            "the Python module 'fitz' is unavailable."
        )
    executable = shutil.which(typst_command)
    if executable is None:
        raise DependencyError(
            f"Typst executable not found: {typst_command!r}. A fresh compile requires Typst."
        )
    return executable


def parse_visual_checks(values: list[str]) -> set[str]:
    checks: set[str] = set()
    aliases = {"body": "first-body", "first_body": "first-body", "last": "final", "math": "formula"}
    for value in values:
        for token in re.split(r"[\s,]+", value):
            normalized = token.strip().lower().replace("_", "-")
            if normalized:
                checks.add(aliases.get(normalized, normalized))
    return checks


def visual_gate(confirmed: set[str], required: bool) -> dict[str, Any]:
    if not required:
        return result(True, skipped=True, confirmed=sorted(confirmed))
    missing = sorted(CORE_VISUAL_CHECKS - confirmed)
    dense_ok = bool(DENSE_VISUAL_CHECKS & confirmed)
    return result(
        not missing and dense_ok,
        confirmed=sorted(confirmed),
        missing=missing,
        required_any=sorted(DENSE_VISUAL_CHECKS),
        dense_category_confirmed=dense_ok,
    )


def validate_paths(source: Path, pdf: Path, out_dir: Path, overwrite: bool) -> tuple[Path, Path, Path]:
    source = source.expanduser().resolve()
    pdf = pdf.expanduser().resolve()
    out_dir = out_dir.expanduser().resolve()
    if not source.is_file() or source.suffix.lower() != ".typ":
        raise ValueError(f"source must be an existing .typ file: {source}")
    if pdf.suffix.lower() != ".pdf":
        raise ValueError("PDF output must end with .pdf")
    if pdf == source or pdf.is_symlink():
        raise ValueError(f"unsafe PDF output path: {pdf}")
    if pdf.exists() and not overwrite:
        raise FileExistsError(f"refusing to overwrite existing PDF without --overwrite: {pdf}")
    for candidate in (pdf, out_dir):
        try:
            candidate.relative_to(SKILL_ROOT)
        except ValueError:
            continue
        raise ValueError(f"refusing to write QA output inside the Skill package: {candidate}")
    return source, pdf, out_dir


def prepare_render_dir(out_dir: Path, overwrite: bool) -> None:
    if not out_dir.exists():
        out_dir.mkdir(parents=True, exist_ok=False)
        return
    if out_dir.is_symlink() or not out_dir.is_dir():
        raise ValueError(f"render output is not a normal directory: {out_dir}")
    entries = sorted(out_dir.iterdir())
    invalid = [path for path in entries if not re.fullmatch(r"page-\d+\.png", path.name)]
    if invalid:
        raise ValueError(f"render directory contains non-page files: {invalid[0].name}")
    if entries and not overwrite:
        raise FileExistsError(
            "render directory already contains page PNGs; use a fresh --out-dir or explicit "
            "--overwrite-rendered-pages authority"
        )
    for path in entries:
        path.unlink()


def is_a4(page: Any, tolerance: float = 2.0) -> bool:
    pairs = ((page.rect.width, page.rect.height), (page.rect.height, page.rect.width))
    return any(abs(w - A4_WIDTH) <= tolerance and abs(h - A4_HEIGHT) <= tolerance for w, h in pairs)


def structurally_blank_pages(doc: Any) -> list[int]:
    blank: list[int] = []
    for index, page in enumerate(doc):
        if not page.get_text("text").strip() and not page.get_drawings() and not page.get_images(full=True):
            blank.append(index + 1)
    return blank


def source_leaks(source: Path) -> dict[str, Any]:
    text = source.read_text(encoding="utf-8", errors="replace")
    hits = [term for term in SOURCE_LEAK_TERMS if term in text]
    return result(not hits, terms=hits)


def profile_leaks(doc: Any, profile: str) -> dict[str, Any]:
    if profile != "student":
        return result(True, skipped=True, profile=profile)
    compact = re.sub(r"\s+", "", "\n".join(page.get_text("text") for page in doc))
    hits = [term for term in STUDENT_FORBIDDEN_TERMS if term in compact]
    return result(not hits, profile=profile, terms=hits)


def render_key_pages(doc: Any, out_dir: Path, overwrite: bool) -> list[dict[str, Any]]:
    prepare_render_dir(out_dir, overwrite)
    indexes = sorted({0, 1, len(doc) // 2, len(doc) - 1})
    rendered: list[dict[str, Any]] = []
    for index in indexes:
        if 0 <= index < len(doc):
            path = out_dir / f"page-{index + 1:02d}.png"
            doc[index].get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(path)
            rendered.append({"page": index + 1, "path": str(path)})
    return rendered


def run_qa(
    source: Path,
    pdf: Path,
    out_dir: Path,
    *,
    profile: str = "general",
    typst_command: str = "typst",
    overwrite: bool = False,
    overwrite_rendered_pages: bool = False,
    visual_checks: set[str] | None = None,
    require_visual_checks: bool = False,
) -> dict[str, Any]:
    source, pdf, out_dir = validate_paths(source, pdf, out_dir, overwrite)
    typst = require_dependencies(typst_command)
    pdf.parent.mkdir(parents=True, exist_ok=True)
    compile_run = subprocess.run(
        [typst, "compile", str(source), str(pdf)],
        cwd=source.parent,
        text=True,
        capture_output=True,
        check=False,
    )
    payload: dict[str, Any] = {
        "status": "fail", "source": str(source), "pdf": str(pdf), "checks": {}, "rendered_pages": []
    }
    payload["checks"]["fresh_compile"] = result(
        compile_run.returncode == 0,
        returncode=compile_run.returncode,
        stderr=compile_run.stderr.strip(),
    )
    if compile_run.returncode != 0:
        return payload

    try:
        doc = fitz.open(pdf)
    except Exception as exc:
        payload["checks"]["open_pdf"] = result(False, error=str(exc))
        return payload
    with doc:
        metadata = doc.metadata or {}
        creator = " ".join(str(metadata.get(key) or "") for key in ("creator", "producer"))
        checks = payload["checks"]
        checks["open_pdf"] = result(True, pages=len(doc))
        checks["page_count"] = result(len(doc) > 0, pages=len(doc))
        checks["typst_metadata"] = result("typst" in creator.lower(), creator=creator.strip())
        bad_a4 = [index + 1 for index, page in enumerate(doc) if not is_a4(page)]
        checks["a4_pages"] = result(not bad_a4, bad_pages=bad_a4)
        blank = structurally_blank_pages(doc)
        checks["no_blank_pages"] = result(not blank, pages=blank)
        checks["source_leak_scan"] = source_leaks(source)
        checks["profile_scan"] = profile_leaks(doc, profile)
        checks["visual_review_evidence"] = visual_gate(visual_checks or set(), require_visual_checks)
        if len(doc):
            try:
                payload["rendered_pages"] = render_key_pages(doc, out_dir, overwrite_rendered_pages)
                checks["render_key_pages"] = result(True, count=len(payload["rendered_pages"]))
            except (FileExistsError, ValueError) as exc:
                checks["render_key_pages"] = result(False, error=str(exc))
    if all(item["ok"] for item in payload["checks"].values()):
        payload["status"] = "pass"
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--profile", choices=("general", "student", "teacher"), default="general")
    parser.add_argument("--typst", default="typst")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--overwrite-rendered-pages", action="store_true")
    parser.add_argument("--visual-check", action="append", default=[])
    parser.add_argument("--require-visual-checks", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        payload = run_qa(
            args.source,
            args.pdf,
            args.out_dir,
            profile=args.profile,
            typst_command=args.typst,
            overwrite=args.overwrite,
            overwrite_rendered_pages=args.overwrite_rendered_pages,
            visual_checks=parse_visual_checks(args.visual_check),
            require_visual_checks=args.require_visual_checks,
        )
    except (DependencyError, FileExistsError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Status: {payload['status']}")
        for name, check in payload["checks"].items():
            print(f"{'PASS' if check['ok'] else 'FAIL'} {name}: {check}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
