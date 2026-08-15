#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run deterministic QA gates for Eric-style Typst PDFs."""

from __future__ import annotations

import argparse
import json
import re
from os import remove
from pathlib import Path
from typing import Any

import fitz


LEAK_TERMS = [
    "挖坑",
    "心法",
    "出招",
    "拆招",
    "定招",
    "教师动作",
    "话术",
    "source ID",
    "source_id",
]
A4_WIDTH = 595.276
A4_HEIGHT = 841.89
CORE_VISUAL_CHECKS = {"cover", "first-body", "final"}
DENSE_VISUAL_CHECKS = {"dense", "table", "workspace", "diagram", "formula"}
VISUAL_CHECK_ALIASES = {
    "body": "first-body",
    "first_body": "first-body",
    "firstbody": "first-body",
    "last": "final",
    "end": "final",
    "math": "formula",
}
STUDENT_FORBIDDEN_TERMS = [
    "教师版",
    "教师解析",
    "教师用",
    "教师提示",
    "教师讲评",
    "评分点",
    "评分标准",
    "讲评",
    "板书",
    "完整解答",
    "完整解析",
    "teacher-only",
]


def check(ok: bool, **details: Any) -> dict[str, Any]:
    return {"ok": ok, **details}


def parse_visual_checks(values: list[str] | None) -> set[str]:
    checks: set[str] = set()
    for value in values or []:
        for token in re.split(r"[\s,]+", value):
            normalized = token.strip().lower().replace("_", "-")
            if not normalized:
                continue
            checks.add(VISUAL_CHECK_ALIASES.get(normalized, normalized))
    return checks


def manual_visual_review_check(confirmed: set[str], require: bool = False) -> dict[str, Any]:
    if not require:
        return check(True, skipped=True, confirmed=sorted(confirmed))
    missing_core = sorted(CORE_VISUAL_CHECKS - confirmed)
    has_dense_evidence = bool(DENSE_VISUAL_CHECKS & confirmed)
    missing_any_group = [] if has_dense_evidence else [sorted(DENSE_VISUAL_CHECKS)]
    return check(
        not missing_core and not missing_any_group,
        confirmed=sorted(confirmed),
        required_all=sorted(CORE_VISUAL_CHECKS),
        required_any_group=missing_any_group,
        missing_any_group=missing_any_group,
        missing=missing_core,
    )


def semantic_profile_hits(text: str, profile: str) -> list[str]:
    if profile != "student":
        return []
    compact = re.sub(r"\s+", "", text)
    return [term for term in STUDENT_FORBIDDEN_TERMS if term in compact]


def is_a4(page: fitz.Page, tolerance: float = 2.0) -> bool:
    rect = page.rect
    pairs = [(rect.width, rect.height), (rect.height, rect.width)]
    return any(
        abs(width - A4_WIDTH) <= tolerance and abs(height - A4_HEIGHT) <= tolerance
        for width, height in pairs
    )


def blank_pages(doc: fitz.Document) -> list[int]:
    blanks: list[int] = []
    for index, page in enumerate(doc):
        text = page.get_text("text").strip()
        drawings = page.get_drawings()
        images = page.get_images(full=True)
        if not text and not drawings and not images:
            blanks.append(index + 1)
    return blanks


def is_rendered_page_name(path: Path) -> bool:
    return bool(re.fullmatch(r"page-\d+\.png", path.name))


def prepare_render_dir(out_dir: Path, overwrite_rendered_pages: bool = False) -> None:
    if out_dir.exists():
        if out_dir.is_symlink() or not out_dir.is_dir():
            raise RuntimeError(f"render output path is not a normal directory: {out_dir}")
        entries = sorted(out_dir.iterdir())
        if entries:
            non_render = [path for path in entries if not is_rendered_page_name(path)]
            if non_render:
                sample = ", ".join(path.name for path in non_render[:5])
                raise RuntimeError(f"render output directory contains non-render files: {sample}")
            if not overwrite_rendered_pages:
                sample = ", ".join(path.name for path in entries[:5])
                raise RuntimeError(
                    "render output directory already contains page PNGs; use a fresh "
                    f"--out-dir or pass --overwrite-rendered-pages after approval. Found: {sample}"
                )
            for path in entries:
                remove(path)
    else:
        out_dir.mkdir(parents=True, exist_ok=False)


def render_key_pages(doc: fitz.Document, out_dir: Path, overwrite_rendered_pages: bool = False) -> list[dict[str, Any]]:
    prepare_render_dir(out_dir, overwrite_rendered_pages=overwrite_rendered_pages)
    indexes = sorted({0, 1, len(doc) // 2, len(doc) - 1})
    rendered: list[dict[str, Any]] = []
    for index in indexes:
        if 0 <= index < len(doc):
            page = doc[index]
            path = out_dir / f"page-{index + 1:02d}.png"
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            pixmap.save(path)
            rendered.append({"page": index + 1, "path": str(path)})
    return rendered


def scan_leaks(source: Path | None, allow_missing_source: bool = False) -> dict[str, Any]:
    if source is None:
        return check(
            allow_missing_source,
            skipped=allow_missing_source,
            delivery_gate_eligible=False,
            reason="no source file supplied; delivery QA requires --source",
        )
    if not source.exists():
        return check(False, path=str(source), reason="source file missing")

    text = source.read_text(encoding="utf-8", errors="replace")
    terms = [term for term in LEAK_TERMS if term in text]
    lines = []
    if terms:
        for number, line in enumerate(text.splitlines(), start=1):
            matched = [term for term in terms if term in line]
            if matched:
                lines.append({"line": number, "terms": matched})
    return check(not terms, path=str(source), terms=terms, lines=lines)


def scan_profile(doc: fitz.Document, profile: str) -> dict[str, Any]:
    if profile == "general":
        return check(True, skipped=True, profile=profile)
    text = "\n".join(page.get_text("text") for page in doc)
    terms = semantic_profile_hits(text, profile)
    return check(not terms, profile=profile, terms=terms)


def qa(
    pdf_path: Path,
    source: Path | None,
    out_dir: Path,
    profile: str = "general",
    visual_checks: set[str] | None = None,
    require_visual_checks: bool = False,
    allow_missing_source: bool = False,
    overwrite_rendered_pages: bool = False,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "pdf": str(pdf_path),
        "source": str(source) if source else None,
        "status": "fail",
        "delivery_gate_eligible": True,
        "checks": {},
        "rendered_pages": [],
    }

    checks = payload["checks"]
    checks["pdf_exists"] = check(pdf_path.exists(), path=str(pdf_path))
    if not pdf_path.exists():
        return payload

    try:
        doc = fitz.open(pdf_path)
    except Exception as exc:  # pragma: no cover - defensive path
        checks["open_pdf"] = check(False, error=str(exc))
        return payload

    with doc:
        metadata = doc.metadata or {}
        creator = metadata.get("creator") or metadata.get("producer") or ""
        checks["open_pdf"] = check(True, pages=len(doc))
        checks["page_count"] = check(len(doc) > 0, pages=len(doc))
        checks["typst_creator"] = check("Typst" in creator, creator=creator)
        bad_a4 = [index + 1 for index, page in enumerate(doc) if not is_a4(page)]
        checks["a4_pages"] = check(not bad_a4, bad_pages=bad_a4)
        blanks = blank_pages(doc)
        checks["no_blank_pages"] = check(not blanks, pages=blanks)
        checks["leak_scan"] = scan_leaks(source, allow_missing_source=allow_missing_source)
        checks["profile_scan"] = scan_profile(doc, profile)
        checks["manual_visual_review"] = manual_visual_review_check(
            visual_checks or set(),
            require=require_visual_checks,
        )
        if len(doc) > 0:
            try:
                payload["rendered_pages"] = render_key_pages(
                    doc,
                    out_dir,
                    overwrite_rendered_pages=overwrite_rendered_pages,
                )
            except Exception as exc:
                checks["render_key_pages"] = check(False, error=str(exc), out_dir=str(out_dir))

    all_checks_ok = all(item["ok"] for item in checks.values())
    delivery_gate_eligible = all(item.get("delivery_gate_eligible", True) for item in checks.values())
    payload["delivery_gate_eligible"] = delivery_gate_eligible
    if all_checks_ok and delivery_gate_eligible:
        payload["status"] = "pass"
    elif all_checks_ok:
        payload["status"] = "smoke-pass"
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Eric PDF QA gates and render key pages.")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--out-dir", type=Path, default=Path("_qa_pages"))
    parser.add_argument("--profile", choices=["general", "student", "teacher"], default="general")
    parser.add_argument(
        "--visual-check",
        action="append",
        default=[],
        help="Manual visual review categories confirmed, comma or space separated.",
    )
    parser.add_argument("--require-visual-checks", action="store_true")
    parser.add_argument(
        "--allow-missing-source",
        action="store_true",
        help="Allow PDF-only smoke checks. Runs with this flag are not delivery-gate evidence.",
    )
    parser.add_argument(
        "--overwrite-rendered-pages",
        action="store_true",
        help="Overwrite page-*.png files in --out-dir after explicit approval.",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload = qa(
        args.pdf,
        args.source,
        args.out_dir,
        profile=args.profile,
        visual_checks=parse_visual_checks(args.visual_check),
        require_visual_checks=args.require_visual_checks,
        allow_missing_source=args.allow_missing_source,
        overwrite_rendered_pages=args.overwrite_rendered_pages,
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Status: {payload['status']}")
        for name, result in payload["checks"].items():
            marker = "PASS" if result["ok"] else "FAIL"
            print(f"{marker} {name}: {result}")
        if payload["rendered_pages"]:
            print("Rendered:")
            for item in payload["rendered_pages"]:
                print(f"- page {item['page']}: {item['path']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
