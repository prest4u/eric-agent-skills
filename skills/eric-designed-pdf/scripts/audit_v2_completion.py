#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_FAMILIES = [
    "Front Matter",
    "Unit Opening",
    "Teaching Core",
    "Practice",
    "Reading / Transfer",
    "Writing / Output",
    "Back Matter",
]
REQUIRED_V2_TEMPLATES = [
    "cover",
    "title",
    "contents-route",
    "diagnostic-entry",
    "unit-opener",
    "article-opener",
    "article-evidence",
    "skill-method",
    "sentence-map",
    "activity",
    "categorizing-chart",
    "exam-mini-set",
    "paragraph-practice",
    "photo-passage",
    "writing-planner",
    "correction-rewrite",
    "final-check",
    "handbook",
    "vocab-bank",
    "connector-index",
    "teacher-guide-page",
]
DISALLOWED_INDEX_PARTS = {
    "node_modules",
    "__pycache__",
    ".cache",
    "browser-cache",
    "chrome-cache",
    "Library",
    "playwright-report",
    "test-results",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def git_output(root: Path, *args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), *args],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception:
        return ""


def make_item(
    item_id: str,
    requirement: str,
    state: str,
    evidence: dict[str, Any] | None = None,
    gaps: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "id": item_id,
        "requirement": requirement,
        "state": state,
        "evidence": evidence or {},
        "gaps": gaps or [],
    }


def item_by_id(audit: dict[str, Any], item_id: str) -> dict[str, Any]:
    for item in audit.get("items", []):
        if item.get("id") == item_id:
            return item
    raise KeyError(item_id)


def existing(paths: list[Path]) -> list[str]:
    return [str(path) for path in paths if path.exists()]


def missing(paths: list[Path]) -> list[str]:
    return [str(path) for path in paths if not path.exists()]


def frontmatter_template(path: Path) -> str:
    text = read_text(path)
    match = re.search(r"(?m)^template:\s*['\"]?([^'\"\n]+)", text)
    return match.group(1).strip() if match else ""


def validation_corpus_evidence(skill_dir: Path, corpus: dict[str, Any]) -> dict[str, Any]:
    scripts_dir = skill_dir / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    try:
        import validate_skill_gates as gate_module  # type: ignore

        return gate_module.validation_corpus_evidence_contract(corpus)
    except Exception as exc:
        return {
            "ok": False,
            "machine_clean_real_cases_from_reports": [],
            "qa_mismatches": [f"validation corpus evidence check unavailable: {exc}"],
        }


def visual_review_score_min(score: Any) -> float | None:
    if isinstance(score, dict):
        values: list[float] = []
        for raw in score.values():
            try:
                values.append(float(raw))
            except (TypeError, ValueError):
                continue
        return min(values) if values else None
    try:
        return float(score)
    except (TypeError, ValueError):
        return None


def is_superseded_archive_case(case: dict[str, Any]) -> bool:
    return case.get("evidence_policy") == "superseded_archive" and case.get("status") == "superseded_archive"


def mirror_content_digest(skill_dir: Path) -> str:
    """Bind an exported package to its exact files, excluding the self-referential provenance record."""
    excluded = {"reports/export-provenance.json"}
    records: list[bytes] = []
    for path in sorted(skill_dir.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(skill_dir).as_posix()
        if relative in excluded or ".git" in Path(relative).parts:
            continue
        file_digest = hashlib.sha256(path.read_bytes()).hexdigest()
        records.append(f"{relative}\0{file_digest}\n".encode("utf-8"))
    return hashlib.sha256(b"".join(records)).hexdigest()


def audit_git_repo(skill_dir: Path) -> dict[str, Any]:
    independent_repo = (skill_dir / ".git").exists()
    provenance_path = skill_dir / "reports/export-provenance.json"
    provenance = load_json(provenance_path) if not independent_repo else {}
    source_commit = ""
    if independent_repo:
        mode = "independent_repo"
        branch = git_output(skill_dir, "rev-parse", "--abbrev-ref", "HEAD")
        count_raw = git_output(skill_dir, "rev-list", "--count", "HEAD")
        commit_count = int(count_raw) if count_raw.isdigit() else 0
        tracked = git_output(skill_dir, "ls-files").splitlines()
    else:
        mode = "export_mirror"
        branch = str(provenance.get("source_branch", ""))
        source_commit = str(provenance.get("source_baseline_commit", ""))
        commit_count = 0
        tracked = [
            str(path.relative_to(skill_dir))
            for path in skill_dir.rglob("*")
            if path.is_file()
        ]
    disallowed = [
        path
        for path in tracked
        if any(part in DISALLOWED_INDEX_PARTS for part in Path(path).parts)
        or path.endswith((".pyc", ".pyo"))
    ]
    gaps = []
    symlinks = [
        str(path.relative_to(skill_dir))
        for path in skill_dir.rglob("*")
        if path.is_symlink()
    ]
    content_digest = ""
    expected_content_digest = ""
    content_digest_verified = False
    if not independent_repo:
        if provenance.get("schema") != "eric-designed-pdf-export-v1":
            gaps.append("Export mirror provenance is missing or has an unsupported schema.")
        if provenance.get("export_repo") != "codex-skills-sync":
            gaps.append("Export mirror is not attributed to codex-skills-sync.")
        if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
            gaps.append("Export mirror source baseline commit is not a 40-character Git object ID.")
        expected_content_digest = str(provenance.get("content_sha256", ""))
        content_digest = mirror_content_digest(skill_dir)
        content_digest_verified = bool(
            re.fullmatch(r"[0-9a-f]{64}", expected_content_digest)
            and content_digest == expected_content_digest
        )
        if not content_digest_verified:
            gaps.append("Export mirror content digest does not match its provenance record.")
    if branch != "v2-full-coverage":
        gaps.append("Expected branch v2-full-coverage.")
    if independent_repo and commit_count < 1:
        gaps.append("No baseline commit exists.")
    if disallowed:
        gaps.append("Disallowed cache/dependency paths are tracked.")
    if symlinks:
        gaps.append("Exported Skill package contains symlinks.")
    return make_item(
        "isolated_git_repo",
        "Create isolated v2 repo/branch area and do not track caches or dependency folders.",
        "proven" if not gaps else "incomplete",
        {
            "mode": mode,
            "branch": branch,
            "commit_count": commit_count,
            "source_commit": provenance.get("source_commit", "") if provenance else "",
            "source_baseline_commit": source_commit,
            "content_sha256": content_digest,
            "content_digest_verified": content_digest_verified,
            "disallowed_tracked": disallowed,
            "symlinks": symlinks,
        },
        gaps,
    )


def audit_matrix(skill_dir: Path) -> dict[str, Any]:
    skill_text = read_text(skill_dir / "SKILL.md")
    matrix_text = read_text(skill_dir / "references/page-role-matrix-v2.md")
    required = REQUIRED_FAMILIES + REQUIRED_V2_TEMPLATES + ["page_family_mode: v2-full"]
    misses = [token for token in required if token not in matrix_text]
    gaps = []
    if not matrix_text:
        gaps.append("references/page-role-matrix-v2.md is missing.")
    if "page-role-matrix-v2.md" not in skill_text:
        gaps.append("SKILL.md does not route to page-role-matrix-v2.md.")
    if misses:
        gaps.append("Page-role matrix is missing required families/templates.")
    return make_item(
        "page_role_matrix",
        "V2 page-role matrix exists, is referenced by SKILL.md, and covers the required families/templates.",
        "proven" if not gaps else "missing",
        {"missing_tokens": misses},
        gaps,
    )


def audit_starter_v2(skill_dir: Path) -> dict[str, Any]:
    starter = skill_dir / "assets/starter-project-v2"
    book = read_text(starter / "book.yaml")
    page_paths = sorted((starter / "pages").glob("*.md"))
    templates = sorted({frontmatter_template(path) for path in page_paths if frontmatter_template(path)})
    missing_templates = [template for template in REQUIRED_V2_TEMPLATES if template not in templates]
    gaps = []
    if not starter.exists():
        gaps.append("assets/starter-project-v2 is missing.")
    if "page_family_mode: v2-full" not in book:
        gaps.append("starter-project-v2/book.yaml does not set page_family_mode: v2-full.")
    if "book-trim:" not in book or "lesson-a4:" not in book:
        gaps.append("book-trim and lesson-a4 profiles are not both declared.")
    if len(page_paths) < 24:
        gaps.append("Starter v2 has fewer than 24 page source files.")
    if missing_templates:
        gaps.append("Starter v2 is missing required page templates.")
    return make_item(
        "starter_v2_full_matrix",
        "Starter v2 can express the full matrix from book.yaml + pages/*.md for book-trim and lesson-a4.",
        "proven" if not gaps else "incomplete",
        {"page_count": len(page_paths), "templates": templates, "missing_templates": missing_templates},
        gaps,
    )


def audit_golden_v2(skill_dir: Path) -> dict[str, Any]:
    golden = skill_dir / "assets/golden-sample-v2"
    required = [
        golden / "full-coverage-v2-book-trim.pdf",
        golden / "full-coverage-v2-lesson-a4.pdf",
        golden / "contact-sheet-book-trim.png",
        golden / "contact-sheet-lesson-a4.png",
        golden / "visual-review-book-trim.md",
        golden / "visual-review-lesson-a4.md",
    ]
    book_pages = sorted((golden / "rendered-pages").glob("book-trim-page-*.png"))
    a4_pages = sorted((golden / "rendered-pages").glob("lesson-a4-page-*.png"))
    gaps = missing(required)
    if len(book_pages) < 24:
        gaps.append("Golden v2 book-trim rendered pages are fewer than 24.")
    if len(a4_pages) < 24:
        gaps.append("Golden v2 lesson-a4 rendered pages are fewer than 24.")
    return make_item(
        "golden_sample_v2_artifacts",
        "Golden v2 sample has PDFs, contact sheets, rendered pages, and review files.",
        "proven" if not gaps else "incomplete",
        {"existing_required": existing(required), "book_trim_pages": len(book_pages), "lesson_a4_pages": len(a4_pages)},
        gaps,
    )


def audit_validation_corpus(skill_dir: Path, corpus: dict[str, Any]) -> dict[str, Any]:
    evidence = validation_corpus_evidence(skill_dir, corpus)
    clean = evidence.get("machine_clean_real_cases_from_reports") or []
    required = set(corpus.get("required_real_case_ids") or [])
    present = {case.get("id") for case in corpus.get("cases", []) if case.get("real_material")}
    gaps = []
    if len(clean) < int(corpus.get("minimum_machine_clean_real_cases") or 3):
        gaps.append("Fewer than three real validation projects are P0/P1-clean from QA reports.")
    if missing_required := sorted(required - present):
        gaps.append(f"Missing required real validation case ids: {', '.join(missing_required)}")
    if not evidence.get("ok"):
        gaps.append("Validation corpus evidence cross-check is not clean.")
    return make_item(
        "real_validation_machine_clean",
        "At least three real validation projects have fresh P0/P1-clean machine evidence.",
        "proven" if not gaps else "incomplete",
        {
            "machine_clean_real_cases": clean,
            "evidence_ok": evidence.get("ok"),
            "qa_mismatches": evidence.get("qa_mismatches", []),
        },
        gaps,
    )


def audit_final_assets(corpus: dict[str, Any]) -> dict[str, Any]:
    final_cases = [
        case.get("id")
        for case in corpus.get("cases", [])
        if case.get("asset_mode") == "final-assets"
        and not is_superseded_archive_case(case)
        and case.get("machine_gate", {}).get("P0") == 0
        and case.get("machine_gate", {}).get("P1") == 0
    ]
    gaps = []
    if not final_cases:
        gaps.append("No P0/P1-clean final-assets case is recorded.")
    return make_item(
        "final_assets_behavior",
        "Final-assets mode is tested with content-aware one-use registered visual assets.",
        "proven" if not gaps else "incomplete",
        {"final_assets_machine_clean_cases": final_cases},
        gaps,
    )


def audit_release(corpus: dict[str, Any]) -> dict[str, Any]:
    eligible = []
    for case in corpus.get("cases", []):
        if is_superseded_archive_case(case):
            continue
        review = case.get("visual_review") or {}
        reviewer = str(review.get("reviewer") or "")
        score = visual_review_score_min(review.get("score")) or 0.0
        if (
            review.get("status") == "PASS"
            and review.get("release_eligible") is True
            and score >= 9.5
            and not re.search(r"same-agent|self|internal", reviewer, re.I)
        ):
            eligible.append(case.get("id"))
    gaps = []
    if not eligible:
        gaps.append("No release-eligible 9.5+ independent/user-confirmed visual review is recorded in validation-corpus-v2.json.")
    return make_item(
        "formal_visual_release",
        "Formal visual release exists with 9.5/10+, P0/P1 = 0, contact sheet evidence, and independent/user confirmation.",
        "proven" if not gaps else "incomplete",
        {"release_eligible_cases": eligible},
        gaps,
    )


def audit_gates_and_prompts(skill_dir: Path) -> list[dict[str, Any]]:
    skill_text = read_text(skill_dir / "SKILL.md")
    qa_text = read_text(skill_dir / "scripts/qa_textbook_pdf.py")
    test_text = read_text(skill_dir / "scripts/test_qa_textbook_pdf.py")
    gate_text = read_text(skill_dir / "scripts/validate_skill_gates.py")
    prompt_text = read_text(skill_dir / "test-prompts.json")
    report_text = read_text(skill_dir / "reports/v2-completion-evidence.md")

    blank_tokens = [
        "LITERAL_UNDERSCORE_BLANKS",
        "BLANK_BASELINE_CSS_WEAK",
        "QUESTION_INLINE_BLANK_WITH_WRITE_LINE",
        "orphan-slot-line",
        "planner-label-blank-weak",
    ]
    answer_tokens = ["STUDENT_ANSWER_VISIBILITY_LEAK", "teacher-answer-key", "answer_visibility"]
    polish_tokens = ["eric-teaching-polish", "validate_teaching_polish.py", "student-process-language"]
    prompt_tokens = ["v2", "full", "final-assets", "ImageGen", "QA repair"]

    items: list[dict[str, Any]] = []
    for item_id, requirement, tokens, haystack in [
        ("blank_line_contract", "Blank-line regressions are represented as machine-detectable gates and tests.", blank_tokens, qa_text + test_text + skill_text),
        ("student_teacher_separation", "Student/teacher answer separation is represented in renderer, QA, and tests.", answer_tokens, qa_text + test_text + gate_text + skill_text),
        ("teaching_polish_contract", "Student-visible language must pass Eric teaching polish strict scan.", polish_tokens, skill_text + gate_text + prompt_text),
        ("forward_test_prompts", "test-prompts.json includes v2 full coverage, real grammar conversion, final asset behavior, and QA repair prompts.", prompt_tokens, prompt_text),
    ]:
        misses = [token for token in tokens if token not in haystack]
        items.append(make_item(item_id, requirement, "proven" if not misses else "weak", {"missing_tokens": misses}, [] if not misses else ["Required contract tokens are missing."]))

    maintenance_tokens = ["quick_validate.py", "test_qa_textbook_pdf.py", "validate_skill_gates.py --json"]
    misses = [token for token in maintenance_tokens if token not in read_text(skill_dir / "references/v2-full-coverage-goal.md")]
    report_misses = [f"{token}: PASS" for token in maintenance_tokens if f"{token}: PASS" not in report_text]
    items.append(
        make_item(
            "maintenance_gate_commands",
            "Skill package commands are documented; latest execution evidence still must be supplied in final reports.",
            "proven" if not misses and not report_misses else ("weak" if not misses else "missing"),
            {"missing_tokens": misses, "missing_report_pass_lines": report_misses},
            [] if not misses and not report_misses else ["This audit does not prove the commands were just run; use command output as delivery evidence."],
        )
    )
    return items


def audit_reference_boundary(skill_dir: Path) -> dict[str, Any]:
    protected_hits = []
    for path in skill_dir.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        rel = path.relative_to(skill_dir).as_posix()
        if re.search(r"Level 1 SB_PDF|L1 SB|Great Writing|National Geographic", rel, re.I):
            protected_hits.append(rel)
    text = read_text(skill_dir / "references/page-role-matrix-v2.md") + read_text(skill_dir / "references/student-book-form-dna.md")
    gaps = []
    if protected_hits:
        gaps.append("Potential protected reference files are inside the skill package.")
    if "without copying protected" not in text and "不复制" not in text:
        gaps.append("Reference-form abstraction boundary is not documented.")
    return make_item(
        "reference_form_boundary",
        "Reference form absorption is documented as abstraction only; no protected reference pages/assets are packaged.",
        "proven" if not gaps else "incomplete",
        {"protected_name_hits": protected_hits},
        gaps,
    )


def audit_final_report(skill_dir: Path) -> dict[str, Any]:
    report = skill_dir / "reports/v2-completion-evidence.md"
    text = read_text(report)
    required_tokens = [
        "Source paths",
        "PDF paths",
        "Commands run",
        "Validator status",
        "Contact sheets",
        "Remaining risks",
        "Git status",
        "gaokao-grammar-final-assets-candidate",
        "validate_skill_gates.py --json: PASS",
        "qa_textbook_pdf.py --require-human-review: PASS",
    ]
    missing_tokens = [token for token in required_tokens if token not in text]
    gaps = []
    if not report.exists():
        gaps.append("reports/v2-completion-evidence.md is missing.")
    if missing_tokens:
        gaps.append("Final report is missing required delivery evidence tokens.")
    return make_item(
        "final_report_evidence",
        "Final response/report names source paths, PDFs, commands, validator status, screenshots/contact sheets, fixes, risks, and git status.",
        "proven" if not gaps else "incomplete",
        {"path": str(report), "missing_tokens": missing_tokens},
        gaps,
    )


def audit_skill(skill_dir: Path) -> dict[str, Any]:
    skill_dir = skill_dir.resolve()
    corpus = load_json(skill_dir / "references/validation-corpus-v2.json")
    items = [
        audit_git_repo(skill_dir),
        audit_matrix(skill_dir),
        audit_starter_v2(skill_dir),
        audit_golden_v2(skill_dir),
        audit_reference_boundary(skill_dir),
        audit_validation_corpus(skill_dir, corpus),
        audit_final_assets(corpus),
        audit_release(corpus),
        *audit_gates_and_prompts(skill_dir),
        audit_final_report(skill_dir),
    ]
    complete = all(item["state"] == "proven" for item in items)
    summary = {
        "complete": complete,
        "proven": sum(1 for item in items if item["state"] == "proven"),
        "weak": sum(1 for item in items if item["state"] == "weak"),
        "incomplete": sum(1 for item in items if item["state"] == "incomplete"),
        "missing": sum(1 for item in items if item["state"] == "missing"),
        "real_machine_clean_cases": len(item_by_id({"items": items}, "real_validation_machine_clean")["evidence"].get("machine_clean_real_cases") or []),
    }
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "skill_dir": str(skill_dir),
        "status": "complete" if complete else "incomplete",
        "summary": summary,
        "items": items,
        "next_action": "Complete weak/incomplete items before calling Eric-designed-pdf v2 done.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict-complete", action="store_true")
    args = parser.parse_args()

    audit = audit_skill(args.root)
    if args.json:
        print(json.dumps(audit, ensure_ascii=False, indent=2))
    else:
        print(f"Status: {audit['status']}")
        print(f"Summary: {audit['summary']}")
        for item in audit["items"]:
            if item["state"] != "proven":
                print(f"- {item['id']}: {item['state']} :: {'; '.join(item['gaps'])}")
    if args.strict_complete and audit["status"] != "complete":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
