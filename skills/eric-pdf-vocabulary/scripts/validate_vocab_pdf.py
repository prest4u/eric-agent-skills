#!/usr/bin/env python3
"""Vocabulary PDF release checks for Eric's Gaokao vocabulary lessons."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


FORBIDDEN_VISIBLE = [
    "sample",
    "Sample Lesson",
    "Template System Sample",
    "Eric Vocabulary Studio",
]

REQUIRED_IDENTITY = [
    "Vocabulary Learning",
    "Memory Chain Lesson",
]

REQUIRED_LINE_CLASSES = [
    "memory-sentence-line",
    "glossary-record-line",
    "grammar-map-check-line",
    "red-review-line",
    "final-record-line",
    "next-plan-line",
    "no-row-rule-record",
    "grammar-bridge-title",
    "grammar-bridge-compact",
]

REQUIRED_SOURCE_PATTERNS = [
    (
        "VOCAB_RECORD_ROW_RULE_DISABLED",
        re.compile(r"\.vocab-record\s+article\s*\{[^}]*border-bottom:\s*0", re.S),
        "Vocabulary record rows must disable ordinary row separators so they do not collide with handwriting lines.",
    ),
    (
        "RED_LEDGER_ROW_RULE_DISABLED",
        re.compile(r"\.red-word-ledger\s+article\s*\{[^}]*border-bottom:\s*0", re.S),
        "Red-word ledger rows must disable ordinary row separators so they do not collide with handwriting lines.",
    ),
    (
        "SENTENCE_MAP_USES_MARKED_INLINE_TEXT",
        re.compile(
            r"def\s+sentence_map_cards\b[\s\S]+?marked_inline_text\(cells\[0\][\s\S]+?marked_inline_text\(cells\[1\][\s\S]+?marked_inline_text\(cells\[2\]",
            re.S,
        ),
        "Sentence-map cards must render vocabulary markers with marked_inline_text so [[A:...]] never leaks to students.",
    ),
]

VISIBLE_MARKER_RE = re.compile(r"\[\[[ABC]:[^\]]+\]\]")
PATCH_DRIFT_PATTERNS = [
    (
        "GRAMMAR_TITLE_COORDINATION_DRIFT",
        re.compile(r"grammar-bridge-title[\s\S]{0,520}#1f2f32", re.I),
        "Grammar Bridge title must coordinate with deep teal/blue-ink, not a standalone black patch.",
    ),
    (
        "FRONTMATTER_BLACK_OVERLAY_DRIFT",
        re.compile(r"rgba\(0,\s*0,\s*0,\s*\.50\)", re.I),
        "Cover/opener overlays should use coordinated light teal-tinted scrims, not heavy black masks.",
    ),
]

FRONTMATTER_DARK_THRESHOLDS = {
    "student-lesson-a4-page-001.png": 0.90,
    "student-lesson-a4-page-003.png": 0.78,
}

ALLOWED_FORMAL_REVIEWER_RE = re.compile(
    r"^(user-confirmed|independent-review|external-review:[A-Za-z0-9_.:-]+|sub-agent-review:[A-Za-z0-9_.:-]+)\b",
    re.I,
)
SELF_REVIEWER_RE = re.compile(r"\b(agent-self|same-agent|self-review|self)\b", re.I)


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except Exception:
        return {}
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def profile_outputs(root: Path, profile: str) -> tuple[Path | None, Path | None]:
    data = load_yaml(root / "book.yaml")
    profiles = data.get("profiles", {}) if data else {}
    info = profiles.get(profile, {}) if isinstance(profiles, dict) else {}
    html = info.get("output_html") if isinstance(info, dict) else None
    pdf = info.get("output_pdf") if isinstance(info, dict) else None
    return (
        root / html if isinstance(html, str) else None,
        root / pdf if isinstance(pdf, str) else None,
    )


def read_text(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def active_source_paths(root: Path, html: Path | None) -> list[Path]:
    paths: list[Path] = [
        root / "book.yaml",
        root / "tools" / "build.py",
        root / "assets" / "manifest.json",
    ]
    pages = root / "pages"
    if pages.exists():
        paths.extend(sorted(pages.glob("*.md")))
    if html is not None:
        paths.append(html)
    extracted = root / "_qa" / "extracted-student-lesson-a4.txt"
    if extracted.exists():
        paths.append(extracted)
    return [p for p in paths if p.exists()]


def normalize_for_identity(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def add_issue(issues: list[dict[str, str]], severity: str, code: str, detail: str) -> None:
    issues.append({"severity": severity, "code": code, "detail": detail})


def first_match(pattern: str, text: str) -> str:
    match = re.search(pattern, text, re.I | re.M)
    return match.group(1).strip() if match else ""


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def command_output(*command: str) -> str:
    completed = subprocess.run(
        command,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return completed.stdout


def validate_standalone(root: Path, profile: str) -> tuple[dict[str, Any], int]:
    """Validate the self-contained Typst starter without another Eric skill."""
    source = root / "lesson.typ"
    pdf = root / "lesson.pdf"
    issues: list[dict[str, str]] = []
    source_text = read_text(source)
    if not source.is_file():
        add_issue(issues, "P0", "STANDALONE_SOURCE_MISSING", "Missing lesson.typ")
    if not pdf.is_file():
        add_issue(issues, "P1", "STANDALONE_PDF_MISSING", "Compile lesson.typ to lesson.pdf first.")
    source_lower = source_text.lower()
    for term in FORBIDDEN_VISIBLE:
        if term.lower() in source_lower:
            add_issue(issues, "P1", "VISIBLE_SAMPLE_RESIDUE", f"Forbidden visible term found: {term}")
    for term in REQUIRED_IDENTITY:
        if term.lower() not in source_lower:
            add_issue(issues, "P1", "BOOK_IDENTITY_MISSING", f"Missing required identity text: {term}")

    evidence: dict[str, Any] = {"source": str(source), "pdf": str(pdf)}
    required_tools = ("pdfinfo", "pdffonts", "pdftotext", "qpdf")
    missing_tools = [tool for tool in required_tools if shutil.which(tool) is None]
    if missing_tools:
        add_issue(issues, "P0", "REQUIRED_TOOL_MISSING", ", ".join(missing_tools))
    elif pdf.is_file():
        try:
            info = command_output("pdfinfo", str(pdf))
            page_match = re.search(r"^Pages:\s+(\d+)\s*$", info, re.MULTILINE)
            size_match = re.search(r"^Page size:\s+(.+)$", info, re.MULTILINE)
            pages = int(page_match.group(1)) if page_match else 0
            page_size = size_match.group(1).strip() if size_match else ""
            evidence.update({"pages": pages, "page_size": page_size})
            if pages < 2:
                add_issue(issues, "P1", "PAGE_COUNT_TOO_LOW", f"Expected at least 2 pages, found {pages}")
            if "A4" not in page_size:
                add_issue(issues, "P1", "NON_A4_PAGE", page_size or "unknown page size")
            command_output("qpdf", "--check", str(pdf))
            extracted = command_output("pdftotext", str(pdf), "-")
            evidence["text_characters"] = len(extracted.strip())
            if len(extracted.strip()) < 100:
                add_issue(issues, "P1", "TEXT_LAYER_TOO_SHORT", "Selectable text is unexpectedly short.")
            compact_extracted = re.sub(r"\s+", "", extracted).lower()
            for term in REQUIRED_IDENTITY:
                if re.sub(r"\s+", "", term).lower() not in compact_extracted:
                    add_issue(issues, "P1", "PDF_IDENTITY_MISSING", f"PDF text is missing: {term}")
            fonts = command_output("pdffonts", str(pdf))
            font_rows = []
            for line in fonts.splitlines():
                match = re.search(r"\s+(yes|no)\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+\s*$", line)
                if match:
                    font_rows.append(match.groups())
            evidence["font_rows"] = len(font_rows)
            if not font_rows:
                add_issue(issues, "P1", "FONT_STATUS_UNREADABLE", "Could not parse embedded font status.")
            elif any(embedded != "yes" or unicode_map != "yes" for embedded, _, unicode_map in font_rows):
                add_issue(issues, "P1", "FONT_NOT_EMBEDDED", "All fonts need embedding and Unicode maps.")
        except subprocess.CalledProcessError as exc:
            add_issue(issues, "P1", "PDF_TOOL_FAILURE", exc.stdout[-500:])

    counts = {severity: sum(item["severity"] == severity for item in issues) for severity in ("P0", "P1", "P2")}
    status = "fail" if counts["P0"] or counts["P1"] else "pass"
    report = {
        "status": status,
        "mode": "standalone-typst",
        "profile": profile,
        "root": str(root),
        "counts": counts,
        "issues": issues,
        "evidence": evidence,
    }
    return report, 1 if status == "fail" else 0


def check_visual_review(
    root: Path,
    profile: str,
    issues: list[dict[str, str]],
    require_formal: bool,
    pdf: Path | None,
) -> None:
    review_path = root / "_qa" / f"visual-review-{profile}.md"
    if not review_path.exists():
        add_issue(
            issues,
            "P1" if require_formal else "P2",
            "VISUAL_REVIEW_MISSING",
            f"Missing visual review file: {review_path.relative_to(root)}",
        )
        return

    text = read_text(review_path)
    status = first_match(r"FINAL_VISUAL_REVIEW:\s*([A-Z_]+)", text)
    reviewer = first_match(r"Reviewer:\s*(.+)", text)
    score_text = first_match(r"Score:\s*([0-9]+(?:\.[0-9]+)?)\s*/\s*10", text)
    p0_text = first_match(r"P0:\s*(\d+)", text)
    p1_text = first_match(r"P1:\s*(\d+)", text)
    reviewed_pdf_sha256 = first_match(r"Artifact PDF SHA-256:\s*([a-fA-F0-9]{64})", text).lower()
    lower = text.lower()
    uses_eric_review = "eric-review" in lower or "$eric-review" in lower
    mentions_subagent = (
        "sub-agent" in lower
        or "subagent" in lower
        or "sub-agent-review:" in lower
        or "independent-review:" in lower
    )
    has_tone_review = "tone coordination:" in text or "Tone coordination:" in text

    formal_pass = status == "PASS"
    if require_formal or formal_pass:
        if not reviewed_pdf_sha256:
            add_issue(
                issues,
                "P1",
                "FORMAL_REVIEW_PDF_IDENTITY_MISSING",
                "Formal visual review must record 'Artifact PDF SHA-256:' for the exact reviewed PDF.",
            )
        elif pdf is None or not pdf.exists():
            add_issue(
                issues,
                "P1",
                "FORMAL_REVIEW_PDF_IDENTITY_UNVERIFIABLE",
                "The reviewed PDF is missing, so its recorded SHA-256 cannot be verified.",
            )
        elif reviewed_pdf_sha256 != file_sha256(pdf):
            add_issue(
                issues,
                "P1",
                "FORMAL_REVIEW_PDF_IDENTITY_MISMATCH",
                "Visual review SHA-256 does not match the current profile PDF; the review belongs to a different artifact.",
            )
    if not status:
        add_issue(
            issues,
            "P1" if require_formal else "P2",
            "VISUAL_REVIEW_STATUS_MISSING",
            "Visual review file must include FINAL_VISUAL_REVIEW.",
        )
    elif status == "FAIL":
        add_issue(
            issues,
            "P1",
            "VISUAL_REVIEW_FAILED",
            "Visual review explicitly failed; do not treat this PDF as release-ready.",
        )
    elif status != "PASS":
        add_issue(
            issues,
            "P1" if require_formal else "P2",
            "VISUAL_REVIEW_NOT_PASS",
            f"Visual review status is {status}; formal visual review remains pending.",
        )

    if formal_pass:
        try:
            score = float(score_text)
        except Exception:
            score = 0.0
        if score < 9.5:
            add_issue(
                issues,
                "P1",
                "FORMAL_REVIEW_SCORE_TOO_LOW",
                "Formal visual PASS requires Score >= 9.5/10.",
            )
        if p0_text != "0" or p1_text != "0":
            add_issue(
                issues,
                "P1",
                "FORMAL_REVIEW_HAS_P0_OR_P1",
                "Formal visual PASS requires P0: 0 and P1: 0.",
            )

    if formal_pass and (not reviewer or SELF_REVIEWER_RE.search(reviewer)):
        add_issue(
            issues,
            "P1",
            "SELF_SIGNED_VISUAL_PASS",
            "A formal visual PASS cannot be signed by the same agent/self reviewer.",
        )
    elif not reviewer or not ALLOWED_FORMAL_REVIEWER_RE.search(reviewer):
        add_issue(
            issues,
            "P1" if require_formal else "P2",
            "INDEPENDENT_VISUAL_REVIEW_REQUIRED",
            "Visual review is not signed by user-confirmed, independent-review, external-review, or sub-agent-review provenance.",
        )

    if formal_pass and not uses_eric_review:
        add_issue(
            issues,
            "P1",
            "FORMAL_REVIEW_WITHOUT_ERIC_REVIEW",
            "Formal visual PASS must state that $eric-review was used.",
        )
    elif not uses_eric_review:
        add_issue(
            issues,
            "P1" if require_formal else "P2",
            "ERIC_REVIEW_SKILL_NOT_RECORDED",
            "Visual review file should record that $eric-review was used.",
        )

    if formal_pass and not mentions_subagent and not reviewer.lower().startswith("user-confirmed"):
        add_issue(
            issues,
            "P1",
            "FORMAL_REVIEW_WITHOUT_SUBAGENT_PROVENANCE",
            "Formal visual PASS needs user confirmation or sub-agent/independent reviewer provenance.",
        )
    elif not mentions_subagent and not reviewer.lower().startswith("user-confirmed"):
        add_issue(
            issues,
            "P1" if require_formal else "P2",
            "SUBAGENT_REVIEW_NOT_RECORDED",
            "Visual review should identify the sub-agent or independent reviewer used.",
        )

    if not has_tone_review:
        add_issue(
            issues,
            "P1" if require_formal else "P2",
            "TONE_COORDINATION_REVIEW_MISSING",
            "Visual review should include 'Tone coordination:' covering cover/opener/body-page color harmony and dark-tone drift.",
        )

    contact_sheet = root / "_qa" / f"contact-sheet-{profile}.png"
    rendered = root / "_qa" / "rendered-pages"
    freshness_paths = [
        contact_sheet,
        rendered / "student-lesson-a4-page-001.png",
        rendered / "student-lesson-a4-page-003.png",
        rendered / "student-lesson-a4-page-009.png",
        rendered / "student-lesson-a4-page-014.png",
        rendered / "student-lesson-a4-page-015.png",
    ]
    existing_mtimes = [p.stat().st_mtime for p in freshness_paths if p.exists()]
    if existing_mtimes and review_path.stat().st_mtime < max(existing_mtimes):
        add_issue(
            issues,
            "P1" if require_formal else "P2",
            "VISUAL_REVIEW_STALE_AFTER_RENDER",
            "Visual review is older than current contact sheet or key rendered pages.",
        )


def image_dark_ratio(path: Path) -> float | None:
    if not path.exists():
        return None
    try:
        from PIL import Image  # type: ignore
    except Exception:
        return None
    try:
        with Image.open(path) as image:
            image = image.convert("RGB")
            image.thumbnail((240, 340))
            pixel_reader = getattr(image, "get_flattened_data", None)
            pixels = list(pixel_reader() if pixel_reader else image.getdata())
    except Exception:
        return None
    if not pixels:
        return None
    dark = 0
    for red, green, blue in pixels:
        luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue
        if luminance < 92:
            dark += 1
    return dark / len(pixels)


def check_frontmatter_tone(root: Path, profile: str, issues: list[dict[str, str]]) -> None:
    rendered = root / "_qa" / "rendered-pages"
    for name, threshold in FRONTMATTER_DARK_THRESHOLDS.items():
        ratio = image_dark_ratio(rendered / name)
        if ratio is None:
            continue
        if ratio > threshold:
            add_issue(
                issues,
                "P1",
                "FRONTMATTER_DARK_TONE_DRIFT",
                f"{name} dark-pixel ratio {ratio:.2%} exceeds {threshold:.0%}; cover/opener should match a lighter premium workbook tone.",
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--profile", default="student-lesson-a4")
    parser.add_argument(
        "--require-formal-review",
        action="store_true",
        help="Treat missing/pending/stale/non-independent visual review as P1 release blockers.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not (root / "book.yaml").exists() and (root / "lesson.typ").exists():
        report, exit_code = validate_standalone(root, args.profile)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return exit_code
    html, pdf = profile_outputs(root, args.profile)
    issues: list[dict[str, str]] = []

    if not (root / "book.yaml").exists():
        add_issue(issues, "P0", "BOOK_YAML_MISSING", f"Missing {root / 'book.yaml'}")

    if html is None or not html.exists():
        add_issue(issues, "P1", "OUTPUT_HTML_MISSING", "Generated HTML output is missing.")
    if pdf is None or not pdf.exists():
        add_issue(issues, "P1", "OUTPUT_PDF_MISSING", "Generated PDF output is missing.")

    sources = active_source_paths(root, html)
    source_blob = "\n".join(read_text(p) for p in sources)
    source_lower = source_blob.lower()

    for term in FORBIDDEN_VISIBLE:
        if term.lower() in source_lower:
            add_issue(issues, "P1", "VISIBLE_SAMPLE_RESIDUE", f"Forbidden visible term found: {term}")

    identity_blob = normalize_for_identity(source_blob)
    for term in REQUIRED_IDENTITY:
        if term.lower() not in identity_blob:
            add_issue(issues, "P1", "BOOK_IDENTITY_MISSING", f"Missing required identity text: {term}")

    build_source = read_text(root / "tools" / "build.py")
    html_source = read_text(html) if html is not None else ""
    extracted_text = read_text(root / "_qa" / "extracted-student-lesson-a4.txt")
    visible_blob = "\n".join(part for part in [html_source, extracted_text] if part)
    marker_hit = VISIBLE_MARKER_RE.search(visible_blob)
    if marker_hit:
        add_issue(
            issues,
            "P1",
            "VISIBLE_VOCAB_MARKER_LEAK",
            f"Vocabulary source marker leaked into visible output: {marker_hit.group(0)}",
        )

    for class_name in REQUIRED_LINE_CLASSES:
        if class_name not in build_source:
            add_issue(issues, "P1", "LINE_CLASS_SOURCE_MISSING", f"Missing renderer/CSS class: {class_name}")
        if html_source and class_name not in html_source:
            add_issue(issues, "P1", "LINE_CLASS_RENDER_MISSING", f"Missing rendered HTML class: {class_name}")

    for code, pattern, detail in REQUIRED_SOURCE_PATTERNS:
        if not pattern.search(build_source):
            add_issue(issues, "P1", code, detail)

    for code, pattern, detail in PATCH_DRIFT_PATTERNS:
        if pattern.search(build_source):
            add_issue(issues, "P1", code, detail)

    check_visual_review(root, args.profile, issues, args.require_formal_review, pdf)
    check_frontmatter_tone(root, args.profile, issues)

    contact_sheet = root / "_qa" / f"contact-sheet-{args.profile}.png"
    if not contact_sheet.exists():
        add_issue(issues, "P2", "CONTACT_SHEET_MISSING", f"Missing {contact_sheet}")

    rendered = root / "_qa" / "rendered-pages"
    key_pages = [
        "student-lesson-a4-page-001.png",
        "student-lesson-a4-page-002.png",
        "student-lesson-a4-page-005.png",
        "student-lesson-a4-page-006.png",
        "student-lesson-a4-page-009.png",
        "student-lesson-a4-page-014.png",
        "student-lesson-a4-page-015.png",
    ]
    missing_key_pages = [name for name in key_pages if not (rendered / name).exists()]
    if missing_key_pages:
        add_issue(issues, "P2", "KEY_PAGE_PNG_MISSING", ", ".join(missing_key_pages))

    counts = {"P0": 0, "P1": 0, "P2": 0}
    for issue in issues:
        sev = issue["severity"]
        counts[sev] = counts.get(sev, 0) + 1

    status = "pass"
    if counts["P0"] or counts["P1"]:
        status = "fail"
    elif counts["P2"]:
        status = "warn"

    report = {
        "status": status,
        "profile": args.profile,
        "root": str(root),
        "counts": counts,
        "issues": issues,
        "checked_files": [str(p.relative_to(root)) for p in sources if p.is_relative_to(root)],
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if counts["P0"] or counts["P1"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
