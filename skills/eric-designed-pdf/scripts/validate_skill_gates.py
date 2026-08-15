#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from qa_textbook_pdf import rendered_page_filename_checks


STRICT = {"P0", "P1"}
REQUIRED_FILES = [
    "SKILL.md",
    "agents/openai.yaml",
    "references/visual-dna.md",
    "references/visual-canon.md",
    "references/page-role-matrix-v2.md",
    "references/student-book-form-dna.md",
    "references/failure-taxonomy.md",
    "references/review-rubric.md",
    "references/component-grammar.md",
    "references/production-workflow.md",
    "references/qa-gates.md",
    "assets/starter-project/book.yaml",
    "assets/starter-project/pages/01-cover.md",
    "assets/starter-project/assets/manifest.json",
    "assets/starter-project/theme/tokens.json",
    "assets/starter-project/tools/build.py",
    "assets/starter-project/tools/render_pdf.py",
    "assets/starter-project/tools/validate.py",
    "assets/starter-project/typst-adapter/lesson-a4-template.typ",
    "assets/starter-project-v2/book.yaml",
    "assets/starter-project-v2/pages/01-cover.md",
    "assets/starter-project-v2/pages/24-teacher-guide.md",
    "assets/starter-project-v2/pages/25-reading-close.md",
    "assets/starter-project-v2/assets/manifest.json",
    "assets/starter-project-v2/theme/tokens.json",
    "assets/starter-project-v2/tools/build.py",
    "assets/starter-project-v2/tools/render_pdf.py",
    "assets/starter-project-v2/tools/validate.py",
    "assets/starter-project-v2/typst-adapter/lesson-a4-template.typ",
    "scripts/new_project.py",
    "scripts/audit_v2_completion.py",
    "scripts/qa_textbook_pdf.py",
    "scripts/test_qa_textbook_pdf.py",
    "scripts/validate_skill_gates.py",
    "test-prompts.json",
]
REQUIRED_SKILL_TOKENS = [
    "## Hard Completion Gates",
    "G0 Scope lock",
    "G1 Legal/design boundary",
    "G2 Fresh build",
    "G3 PDF structure",
    "G4 Component coverage",
    "G5 Asset policy",
    "G6 Leak safety",
    "G7 Visual QA",
    "G8 Evidence report",
    "Gate Evidence Ledger",
    "Asset Generation Pass Lock",
    "asset_mode: final-assets",
    "proof-placeholder",
    "final-assets",
    "qa_textbook_pdf.py",
    "eric-pdf",
    "student book",
    "workbook",
    "## Failure Modes",
    "Custom project cannot pass starter",
    "Contact sheet looks like repeated forms",
    "Do not self-certify visual quality",
    "FINAL_VISUAL_REVIEW: FAIL",
    "diagnostic-form-drift",
    "CHECKPOINT",
    "Contact sheet:",
    "Key pages:",
    "Canon comparison:",
    "Reject patterns checked:",
    "Font decision:",
    "Design Transfer Reset",
    "Cover Title Lock",
    "Cover Brand Lock",
    "Student Language Lock",
    "Blank Line Baseline Lock",
    "LITERAL_UNDERSCORE_BLANKS",
    "question-line-double-blank",
    "QUESTION_INLINE_BLANK_WITH_WRITE_LINE",
    "Exam Stem Slot Lock",
    "EXAM_STEM_SLOT_DRIFT",
    "exam-stem-slot",
    "A4 Sentence Map Surface Lock",
    "A4_SENTENCE_MAP_TABLE_CRAMP",
    "A4_ONLY_PROFILE_RESIDUE",
    "visible-sanitizer-scope-leak",
    "第本课程",
    "第N讲",
    "final whole-delivery conflict scan",
    "stale `lesson-*` directory",
    "teacher-key-cjk-latin-fusion",
    "Planner And Backmatter Lock",
    "Workbook Record Lock",
    "Rendered Text Fidelity Lock",
    "Starter Residue Lock",
    "STARTER_RESIDUE_FOUND",
    "WORKBOOK_RECORD_SURFACE_MISSING",
    "eric-teaching-polish",
    "answer_visibility",
    "STUDENT_ANSWER_VISIBILITY_LEAK",
    "STUDENT_PROMPT_LANGUAGE_DRIFT",
    "Negative regression",
    "orphan-slot-line",
    "Eric Teaching Studio",
    "one image file and one asset id are used once only",
    "allowed_templates",
    "ASSET_REUSED_ACROSS_PAGES",
    "ASSET_PATH_REUSED_IN_MANIFEST",
    "COVER_ASSET_REUSED_INSIDE_BOOK",
    "ASSET_ALLOWED_TEMPLATE_MISMATCH",
    "cover-image-reuse",
    "abstract-asset-drift",
    "FINAL_ASSET_UNINTERPRETABLE_SCENE",
    "FINAL_ASSET_NATURE_FIRST_RATIONALE_MISSING",
    "nature_first_rationale",
    "nature",
    "wildlife",
    "mascot",
    "textbook-qa-<profile>-release",
    "release_gate",
    "page-role-matrix-v2.md",
    "page_family_mode",
    "v2-full",
    "V2_PAGE_FAMILY_COVERAGE_MISSING",
    "starter-project-v2",
    "--starter v2",
    "Generic Edition Lock",
    "no-student-name edition",
    "Sample Learner is a regression/test case",
    "Personalized editions",
]
REQUIRED_VALIDATION_CASE_IDS = {
    "level1-form-abstraction",
    "gaokao-summer-grammar",
    "sample-student-clause-linker",
    "sample-learner-ielts-regression",
    "tianjin-gaokao-22-lessons-four-profile",
}
REQUIRED_REFERENCE_TOKENS = {
    "references/page-role-matrix-v2.md": [
        "Front Matter",
        "Unit Opening",
        "Teaching Core",
        "Practice",
        "Reading / Transfer",
        "Writing / Output",
        "Back Matter",
        "contents-route",
        "diagnostic-entry",
        "article-opener",
        "article-evidence",
        "skill-method",
        "sentence-map",
        "categorizing-chart",
        "exam-mini-set",
        "correction-rewrite",
        "vocab-bank",
        "connector-index",
        "teacher-answer-key",
        "page_family_mode: v2-full",
        "V2_PAGE_FAMILY_COVERAGE_MISSING",
    ],
    "references/production-workflow.md": [
        "Default Book Identity",
        "no-student-name",
        "only when the user explicitly asks",
        "Asset Modes",
        "asset_mode: proof-placeholder",
        "asset_mode: final-assets",
        "status: approved_final",
        "prompt",
        "no visible text",
        "content_brief",
        "visual_direction",
        "uniqueness_note",
        "allowed_templates",
        "One image may be used once only",
        "cover assets used inside the book",
    ],
        "references/qa-gates.md": [
        "asset_mode",
        "final-assets",
        "proof-placeholder",
        "procedural/proof/placeholder/starter/sample",
        "prompt",
        "no-text policy",
        "QUESTION_INLINE_BLANK_WITH_WRITE_LINE",
        "EXAM_STEM_SLOT_DRIFT",
        "A4_SENTENCE_MAP_TABLE_CRAMP",
        "A4_ONLY_PROFILE_RESIDUE",
        "STUDENT_PROMPT_LANGUAGE_DRIFT",
        "COVER_CONTENT_CONCEPT_MISSING",
        "COVER_BRAND_MARK_MISSING",
        "COVER_BRAND_CONTRAST_WEAK",
        "one-image-one-use",
        "ASSET_REUSED_ACROSS_PAGES",
        "ASSET_PATH_REUSED_IN_MANIFEST",
        "COVER_ASSET_REUSED_INSIDE_BOOK",
        "ASSET_ALLOWED_TEMPLATE_MISMATCH",
    ],
    "references/component-grammar.md": [
        "question-line-double-blank",
        "QUESTION_INLINE_BLANK_WITH_WRITE_LINE",
        "prompt_text_before_write_lines",
        "exam-stem-slot",
        "sentence-map-card-stack",
        "Eric Teaching Studio",
        "content_brief",
        "allowed_templates",
        "Cover image reused inside",
    ],
    "references/visual-canon.md": [
        "Source Of Truth",
        "Page-Role Anchors",
        "Typography Canon",
        "Transfer Workflow",
        "title-wrap",
        "Canon comparison:",
        "distinct opener asset",
        "not the cover bitmap",
    ],
    "references/failure-taxonomy.md": [
        "thin-cover-type",
        "title-wrap-break",
        "cover-brand-missing",
        "cover-brand-low-contrast",
        "cover-stage-badge",
        "generic-cover-art",
        "cover-image-reuse",
        "abstract-asset-drift",
        "dashboard-panel",
        "ui-number-block",
        "component-collage",
        "diagnostic-form-drift",
        "patch-drift",
        "floating-blank-line",
        "orphan-slot-line",
        "question-line-double-blank",
        "QUESTION_INLINE_BLANK_WITH_WRITE_LINE",
        "exam-stem-slot-drift",
        "a4-sentence-map-table-cramp",
        "a4-only-profile-residue",
        "loose-workbook-tail",
        "plain-planner-table",
        "plain-final-check",
        "weak-backmatter",
        "rendered-text-glitch",
        "student-process-language",
        "starter-residue",
        "STARTER_RESIDUE_FOUND",
        "WORKBOOK_RECORD_SURFACE_MISSING",
    ],
    "references/review-rubric.md": [
        "Release Threshold",
        "Score Axes",
        "Title lockup",
        "Cover brand",
        "cover-brand-low-contrast",
        "Cover concept",
        "Asset uniqueness",
        "cover-image-reuse",
        "Writing affordance",
        "orphan-slot-line",
        "question-line-double-blank",
        "loose-workbook-tail",
        "Rendered text fidelity",
        "Source hygiene",
        "Required Visual Review Fields",
        "Reject patterns checked:",
        "FINAL_VISUAL_REVIEW: FAIL",
        "diagnostic-form-drift",
    ],
}
RUNTIME_RED_RE = re.compile(r"(Claude Code|~/\.claude/skills|TODO|\[TODO)", re.I)


def issue(severity: str, code: str, detail: str, file: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"severity": severity, "code": code, "detail": detail}
    if file:
        payload["file"] = file
    return payload


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 120) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
        )
        return proc.returncode, proc.stdout
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        detail = f"Timed out after {timeout}s: {' '.join(cmd)}"
        return 124, (output + "\n" + detail).strip() + "\n"


def find_eric_pdf_qa(skill_dir: Path) -> tuple[Path | None, bool]:
    """Find the optional Eric PDF adapter without creating a package dependency."""
    env_dir = os.environ.get("ERIC_PDF_SKILL_DIR")
    if env_dir:
        candidate = Path(env_dir).expanduser() / "scripts" / "qa_typst_a4.py"
        return (candidate if candidate.is_file() else None), True
    sibling = skill_dir.parent / "eric-pdf" / "scripts" / "qa_typst_a4.py"
    return (sibling if sibling.is_file() else None), False


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    fields: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"')
    return fields


def load_validation_corpus(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def visual_review_score_min(score: Any) -> float | None:
    """Return the release score, accepting either one score or per-profile scores."""
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


FOUR_PROFILE_SET = {"student-book-trim", "teacher-book-trim", "student-lesson-a4", "teacher-lesson-a4"}


PROFILE_EVIDENCE_KEYS = {
    "book-trim": {
        "qa": "book_trim_qa",
        "release_qa": "book_trim_release_qa",
        "pdf": "book_trim_pdf",
        "contact_sheet": "book_trim_contact_sheet",
        "visual_review": "book_trim_visual_review",
    },
    "lesson-a4": {
        "qa": "lesson_a4_qa",
        "release_qa": "lesson_a4_release_qa",
        "pdf": "lesson_a4_pdf",
        "contact_sheet": "lesson_a4_contact_sheet",
        "visual_review": "lesson_a4_visual_review",
    },
    "student-book-trim": {
        "qa": "student_book_trim_qa",
        "release_qa": "student_book_trim_release_qa",
        "pdf": "student_book_trim_pdf",
        "contact_sheet": "student_book_trim_contact_sheet",
        "visual_review": "student_book_trim_visual_review",
    },
    "teacher-book-trim": {
        "qa": "teacher_book_trim_qa",
        "release_qa": "teacher_book_trim_release_qa",
        "pdf": "teacher_book_trim_pdf",
        "contact_sheet": "teacher_book_trim_contact_sheet",
        "visual_review": "teacher_book_trim_visual_review",
    },
    "student-lesson-a4": {
        "qa": "student_lesson_a4_qa",
        "release_qa": "student_lesson_a4_release_qa",
        "pdf": "student_lesson_a4_pdf",
        "contact_sheet": "student_lesson_a4_contact_sheet",
        "visual_review": "student_lesson_a4_visual_review",
    },
    "teacher-lesson-a4": {
        "qa": "teacher_lesson_a4_qa",
        "release_qa": "teacher_lesson_a4_release_qa",
        "pdf": "teacher_lesson_a4_pdf",
        "contact_sheet": "teacher_lesson_a4_contact_sheet",
        "visual_review": "teacher_lesson_a4_visual_review",
    },
}


def has_book_and_a4_profiles(profiles: list[Any]) -> bool:
    profile_set = {str(profile) for profile in profiles}
    return {"book-trim", "lesson-a4"}.issubset(profile_set) or FOUR_PROFILE_SET.issubset(profile_set)


def required_evidence_fields_for_profiles(profiles: list[Any], *, release: bool) -> list[str]:
    fields: list[str] = []
    for profile in profiles:
        keys = PROFILE_EVIDENCE_KEYS.get(str(profile))
        if not keys:
            continue
        fields.extend([keys["pdf"], keys["contact_sheet"], keys["qa"], keys["visual_review"]])
        if release:
            fields.append(keys["release_qa"])
    return fields


def is_superseded_archive_case(case: dict[str, Any]) -> bool:
    return case.get("evidence_policy") == "superseded_archive" and case.get("status") == "superseded_archive"


def validation_corpus_contract(corpus: dict[str, Any]) -> dict[str, Any]:
    cases = corpus.get("cases", [])
    case_ids = [str(case.get("id", "")) for case in cases]
    required_ids = set(corpus.get("required_real_case_ids") or set()) | REQUIRED_VALIDATION_CASE_IDS
    minimum_raw = corpus.get("minimum_machine_clean_real_cases")
    minimum_machine_clean = int(minimum_raw) if minimum_raw is not None else 3
    machine_clean_real_cases = []
    release_pass_cases = []
    incorrect_release_pass_cases = []
    skipped_superseded_cases = []
    missing_required_fields: dict[str, list[str]] = {}

    required_case_fields = [
        "id",
        "family",
        "real_material",
        "status",
        "release_status",
        "project_path",
        "profiles",
        "asset_mode",
        "machine_gate",
        "visual_review",
        "source_boundary",
        "evidence",
        "known_gaps",
        "next_action",
    ]
    for case in cases:
        case_id = str(case.get("id", ""))
        missing = [field for field in required_case_fields if field not in case]
        evidence = case.get("evidence") if isinstance(case.get("evidence"), dict) else {}
        profiles = case.get("profiles") if isinstance(case.get("profiles"), list) else []
        required_evidence_fields = required_evidence_fields_for_profiles(
            profiles,
            release=case.get("release_status") == "pass",
        )
        missing.extend([f"evidence.{field}" for field in required_evidence_fields if field not in evidence])
        if missing:
            missing_required_fields[case_id or "<missing-id>"] = missing

        if is_superseded_archive_case(case):
            skipped_superseded_cases.append(case_id)
            continue

        gate = case.get("machine_gate") if isinstance(case.get("machine_gate"), dict) else {}
        is_machine_clean = gate.get("P0") == 0 and gate.get("P1") == 0
        has_both_profiles = has_book_and_a4_profiles(profiles)
        if case.get("real_material") is True and is_machine_clean and has_both_profiles:
            machine_clean_real_cases.append(case_id)

        if case.get("release_status") == "pass":
            release_pass_cases.append(case_id)
            visual_review = case.get("visual_review") if isinstance(case.get("visual_review"), dict) else {}
            reviewer = str(visual_review.get("reviewer", ""))
            reviewer_ok = reviewer in {"independent-review", "user-confirmed"}
            score = visual_review_score_min(visual_review.get("score"))
            score_ok = score is not None and score >= 9.5
            p0 = visual_review.get("P0", visual_review.get("p0", gate.get("P0")))
            p1 = visual_review.get("P1", visual_review.get("p1", gate.get("P1")))
            visual_ok = visual_review.get("status") == "PASS" and p0 == 0 and p1 == 0
            if not (reviewer_ok and score_ok and visual_ok and visual_review.get("release_eligible") is True):
                incorrect_release_pass_cases.append(case_id)

    checks = {
        "required_cases_present": required_ids.issubset(set(case_ids)),
        "minimum_machine_clean_real_cases": len(machine_clean_real_cases) >= minimum_machine_clean,
        "incorrect_final_release_pass": bool(incorrect_release_pass_cases),
        "required_fields_present": not missing_required_fields,
    }
    ok = (
        checks["required_cases_present"]
        and checks["minimum_machine_clean_real_cases"]
        and not checks["incorrect_final_release_pass"]
        and checks["required_fields_present"]
    )
    return {
        "ok": ok,
        "case_ids": case_ids,
        "required_case_ids": sorted(required_ids),
        "machine_clean_real_cases": machine_clean_real_cases,
        "release_pass_cases": release_pass_cases,
        "incorrect_release_pass_cases": incorrect_release_pass_cases,
        "skipped_superseded_cases": skipped_superseded_cases,
        "missing_required_fields": missing_required_fields,
        "checks": checks,
    }


def resolve_case_path(project_path: Path, candidate: str) -> Path:
    path = Path(candidate)
    if path.is_absolute():
        return path
    return (project_path / path).resolve()


def current_rendered_page_count(project_path: Path, profile: str) -> int:
    rendered_dir = project_path / "_qa" / "rendered-pages"
    return len(sorted(rendered_dir.glob(f"{profile}-page-*.png"))) if rendered_dir.exists() else 0


def current_rendered_page_inventory(project_path: Path, profile: str, expected_count: int | None) -> dict[str, Any]:
    rendered_dir = project_path / "_qa" / "rendered-pages"
    names = [path.name for path in sorted(rendered_dir.glob(f"{profile}-page-*.png"))] if rendered_dir.exists() else []
    return rendered_page_filename_checks(names, profile, expected_count)


def expected_page_family_mode_for(case: dict[str, Any], profile: str) -> str:
    expected = case.get("page_family_mode", "off")
    if isinstance(expected, dict):
        return str(expected.get(profile) or expected.get("*") or "off")
    return str(expected)


def validation_corpus_evidence_contract(corpus: dict[str, Any]) -> dict[str, Any]:
    cases = corpus.get("cases", [])
    missing_project_paths: list[dict[str, str]] = []
    missing_source_materials: list[dict[str, str]] = []
    missing_evidence_files: list[dict[str, str]] = []
    qa_load_failures: list[dict[str, str]] = []
    qa_mismatches: list[dict[str, Any]] = []
    stale_rendered_page_files: list[dict[str, Any]] = []
    machine_clean_real_cases_from_reports: list[str] = []
    skipped_superseded_cases: list[str] = []

    for case in cases:
        case_id = str(case.get("id", ""))
        if is_superseded_archive_case(case):
            skipped_superseded_cases.append(case_id)
            continue
        project = Path(str(case.get("project_path", ""))).expanduser()
        if not project.exists():
            missing_project_paths.append({"case": case_id, "path": str(project)})
            continue

        for source in case.get("source_materials", []) or []:
            source_path = Path(str(source)).expanduser()
            if not source_path.exists():
                missing_source_materials.append({"case": case_id, "path": str(source_path)})

        evidence = case.get("evidence") if isinstance(case.get("evidence"), dict) else {}
        for key, rel_path in evidence.items():
            if not isinstance(rel_path, str):
                continue
            path = resolve_case_path(project, rel_path)
            if not path.exists():
                missing_evidence_files.append({"case": case_id, "key": key, "path": str(path)})

        gate_counts = case.get("machine_gate") if isinstance(case.get("machine_gate"), dict) else {}
        profiles = case.get("profiles") if isinstance(case.get("profiles"), list) else []
        profile_reports: dict[str, Any] = {}
        all_profiles_p0p1_clean = True
        for profile in profiles:
            keys = PROFILE_EVIDENCE_KEYS.get(str(profile))
            if not keys:
                continue
            qa_rel = evidence.get(keys["qa"])
            if not isinstance(qa_rel, str):
                qa_mismatches.append({"case": case_id, "profile": profile, "reason": "qa_evidence_missing"})
                all_profiles_p0p1_clean = False
                continue
            qa_path = resolve_case_path(project, qa_rel)
            try:
                qa_report = json.loads(qa_path.read_text(encoding="utf-8"))
            except Exception as exc:
                qa_load_failures.append({"case": case_id, "profile": profile, "path": str(qa_path), "error": str(exc)})
                all_profiles_p0p1_clean = False
                continue

            profile_reports[str(profile)] = qa_report
            counts = (qa_report.get("summary") or {}).get("counts") or {}
            for severity in ("P0", "P1"):
                if counts.get(severity) != gate_counts.get(severity):
                    qa_mismatches.append(
                        {
                            "case": case_id,
                            "profile": profile,
                            "field": f"machine_gate.{severity}",
                            "ledger": gate_counts.get(severity),
                            "qa_report": counts.get(severity),
                        }
                    )
            if counts.get("P0") != 0 or counts.get("P1") != 0:
                all_profiles_p0p1_clean = False

            qa_evidence = qa_report.get("evidence") if isinstance(qa_report.get("evidence"), dict) else {}
            qa_config = qa_evidence.get("qa_config") if isinstance(qa_evidence.get("qa_config"), dict) else {}
            rendered_evidence = qa_evidence.get("rendered_pages") if isinstance(qa_evidence.get("rendered_pages"), dict) else {}
            expected_rendered = rendered_evidence.get("expected") or qa_evidence.get("page_count")
            recorded_rendered = rendered_evidence.get("count")
            rendered_inventory = current_rendered_page_inventory(
                project,
                str(profile),
                int(expected_rendered) if expected_rendered else None,
            )
            actual_rendered = int(rendered_inventory.get("actual") or 0)
            if expected_rendered and (actual_rendered != int(expected_rendered) or not rendered_inventory.get("ok", True)):
                stale_rendered_page_files.append(
                    {
                        "case": case_id,
                        "profile": profile,
                        "expected": int(expected_rendered),
                        "recorded": recorded_rendered,
                        "actual": actual_rendered,
                        "filename_checks": rendered_inventory,
                    }
                )
                all_profiles_p0p1_clean = False
            if qa_config.get("asset_mode") != case.get("asset_mode"):
                qa_mismatches.append(
                    {
                        "case": case_id,
                        "profile": profile,
                        "field": "asset_mode",
                        "ledger": case.get("asset_mode"),
                        "qa_report": qa_config.get("asset_mode"),
                    }
                )
            expected_page_family_mode = expected_page_family_mode_for(case, str(profile))
            qa_page_family_mode = qa_config.get("page_family_mode", "off")
            if qa_page_family_mode != expected_page_family_mode:
                qa_mismatches.append(
                    {
                        "case": case_id,
                        "profile": profile,
                        "field": "page_family_mode",
                        "ledger": expected_page_family_mode,
                        "qa_report": qa_page_family_mode,
                    }
                )

            for evidence_field, qa_field in [(keys["pdf"], "pdf"), (keys["contact_sheet"], "contact_sheet")]:
                expected = evidence.get(evidence_field)
                actual = qa_evidence.get(qa_field)
                if expected and actual and expected != actual:
                    qa_mismatches.append(
                        {
                            "case": case_id,
                            "profile": profile,
                            "field": qa_field,
                            "ledger": expected,
                            "qa_report": actual,
                        }
                    )

            if case.get("release_status") == "pass":
                release_rel = evidence.get(keys["release_qa"])
                if not isinstance(release_rel, str):
                    qa_mismatches.append({"case": case_id, "profile": profile, "reason": "release_qa_evidence_missing"})
                    all_profiles_p0p1_clean = False
                    continue
                release_path = resolve_case_path(project, release_rel)
                try:
                    release_report = json.loads(release_path.read_text(encoding="utf-8"))
                except Exception as exc:
                    qa_load_failures.append({"case": case_id, "profile": profile, "path": str(release_path), "error": str(exc)})
                    all_profiles_p0p1_clean = False
                    continue
                release_counts = (release_report.get("summary") or {}).get("counts") or {}
                release_evidence = release_report.get("evidence") if isinstance(release_report.get("evidence"), dict) else {}
                human_review = release_evidence.get("human_visual_review") if isinstance(release_evidence.get("human_visual_review"), dict) else {}
                release_reviewer = str(human_review.get("reviewer", ""))
                release_score = visual_review_score_min(human_review.get("score"))
                release_ok = (
                    release_report.get("status") == "pass"
                    and release_counts.get("P0") == 0
                    and release_counts.get("P1") == 0
                    and human_review.get("ok") is True
                    and human_review.get("status") == "PASS"
                    and release_score is not None
                    and release_score >= 9.5
                    and not re.search(r"same-agent|self|internal", release_reviewer, re.I)
                )
                if not release_ok:
                    qa_mismatches.append(
                        {
                            "case": case_id,
                            "profile": profile,
                            "field": "release_gate",
                            "ledger": "release_status=pass",
                            "qa_report": {
                                "status": release_report.get("status"),
                                "counts": release_counts,
                                "human_visual_review": human_review,
                            },
                        }
                    )
                    all_profiles_p0p1_clean = False

        has_both_profiles = has_book_and_a4_profiles(list(profile_reports))
        if case.get("real_material") is True and has_both_profiles and all_profiles_p0p1_clean:
            machine_clean_real_cases_from_reports.append(case_id)

    minimum_raw = corpus.get("minimum_machine_clean_real_cases")
    minimum_machine_clean = int(minimum_raw) if minimum_raw is not None else 3
    checks = {
        "project_paths_exist": not missing_project_paths,
        "source_materials_exist": not missing_source_materials,
        "evidence_files_exist": not missing_evidence_files,
        "qa_json_loads": not qa_load_failures,
        "qa_reports_match_ledger": not qa_mismatches,
        "rendered_pages_match_current_filesystem": not stale_rendered_page_files,
        "minimum_machine_clean_real_cases_from_reports": len(machine_clean_real_cases_from_reports) >= minimum_machine_clean,
    }
    return {
        "ok": all(checks.values()),
        "missing_project_paths": missing_project_paths,
        "missing_source_materials": missing_source_materials,
        "missing_evidence_files": missing_evidence_files,
        "qa_load_failures": qa_load_failures,
        "qa_mismatches": qa_mismatches,
        "stale_rendered_page_files": stale_rendered_page_files,
        "skipped_superseded_cases": skipped_superseded_cases,
        "machine_clean_real_cases_from_reports": machine_clean_real_cases_from_reports,
        "checks": checks,
    }


def validate_static(skill_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    evidence: dict[str, Any] = {}
    missing = [path for path in REQUIRED_FILES if not (skill_dir / path).exists()]
    evidence["required_files_checked"] = len(REQUIRED_FILES)
    if missing:
        issues.append(issue("P1", "REQUIRED_FILES_MISSING", ", ".join(missing)))

    audit_script = skill_dir / "scripts" / "audit_v2_completion.py"
    if audit_script.exists():
        try:
            spec = importlib.util.spec_from_file_location("audit_v2_completion_for_gate", audit_script)
            if spec is None or spec.loader is None:
                raise RuntimeError("could not load audit_v2_completion.py")
            audit_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(audit_module)
            audit = audit_module.audit_skill(skill_dir)
            evidence["v2_completion_audit"] = {
                "status": audit.get("status"),
                "summary": audit.get("summary"),
                "non_proven_items": [
                    {"id": row.get("id"), "state": row.get("state"), "gaps": row.get("gaps")}
                    for row in audit.get("items", [])
                    if row.get("state") != "proven"
                ],
            }
        except Exception as exc:
            issues.append(issue("P1", "V2_COMPLETION_AUDIT_FAILED", str(exc), "scripts/audit_v2_completion.py"))
    else:
        issues.append(issue("P1", "V2_COMPLETION_AUDIT_SCRIPT_MISSING", "scripts/audit_v2_completion.py is required.", "scripts/audit_v2_completion.py"))

    skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8") if (skill_dir / "SKILL.md").exists() else ""
    frontmatter = parse_frontmatter(skill_text)
    description = frontmatter.get("description", "")
    evidence["frontmatter"] = {"name": frontmatter.get("name"), "description_length": len(description)}
    if frontmatter.get("name") != "eric-designed-pdf":
        issues.append(issue("P1", "FRONTMATTER_NAME", str(frontmatter.get("name")), "SKILL.md"))
    trigger_terms = ["textbook", "student book", "workbook", "教材级 PDF", "Eric-designed-pdf"]
    missing_triggers = [term for term in trigger_terms if term.lower() not in description.lower()]
    if missing_triggers:
        issues.append(issue("P1", "FRONTMATTER_TRIGGER_WEAK", ", ".join(missing_triggers), "SKILL.md"))
    missing_tokens = [token for token in REQUIRED_SKILL_TOKENS if token not in skill_text]
    if missing_tokens:
        issues.append(issue("P1", "SKILL_GATE_TOKENS_MISSING", ", ".join(missing_tokens), "SKILL.md"))

    reference_token_misses: dict[str, list[str]] = {}
    for rel_path, tokens in REQUIRED_REFERENCE_TOKENS.items():
        path = skill_dir / rel_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        missing_for_file = [token for token in tokens if token not in text]
        if missing_for_file:
            reference_token_misses[rel_path] = missing_for_file
    evidence["reference_token_misses"] = reference_token_misses
    if reference_token_misses:
        issues.append(issue("P1", "REFERENCE_CONTRACT_TOKENS_MISSING", json.dumps(reference_token_misses, ensure_ascii=False)))

    validation_corpus_path = skill_dir / "references" / "validation-corpus-v2.json"
    if validation_corpus_path.exists():
        try:
            validation_corpus = load_validation_corpus(validation_corpus_path)
            validation_corpus_result = validation_corpus_contract(validation_corpus)
            validation_corpus_evidence_result = validation_corpus_evidence_contract(validation_corpus)
            evidence["validation_corpus_v2"] = validation_corpus_result
            evidence["validation_corpus_v2_evidence"] = validation_corpus_evidence_result
            if not validation_corpus_result["ok"]:
                issues.append(issue("P1", "VALIDATION_CORPUS_V2_WEAK", json.dumps(validation_corpus_result, ensure_ascii=False), str(validation_corpus_path.relative_to(skill_dir))))
            if not validation_corpus_evidence_result["ok"]:
                issues.append(issue("P1", "VALIDATION_CORPUS_V2_EVIDENCE_WEAK", json.dumps(validation_corpus_evidence_result, ensure_ascii=False), str(validation_corpus_path.relative_to(skill_dir))))
        except Exception as exc:
            issues.append(issue("P1", "VALIDATION_CORPUS_V2_INVALID", str(exc), str(validation_corpus_path.relative_to(skill_dir))))
    else:
        evidence["validation_corpus_v2"] = {
            "status": "skipped",
            "reason": "optional authorized private regression corpus is not installed",
        }

    scan_files = [skill_dir / "SKILL.md", *sorted((skill_dir / "references").glob("*.md"))]
    runtime_hits = []
    for path in scan_files:
        if not path.exists():
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if RUNTIME_RED_RE.search(line):
                runtime_hits.append({"file": str(path.relative_to(skill_dir)), "line": number, "text": line.strip()})
    evidence["runtime_scan_hits"] = runtime_hits
    if runtime_hits:
        issues.append(issue("P1", "RUNTIME_OR_TODO_HITS", json.dumps(runtime_hits[:5], ensure_ascii=False)))

    try:
        prompts = json.loads((skill_dir / "test-prompts.json").read_text(encoding="utf-8"))
        bad = [i for i, row in enumerate(prompts, 1) if not row.get("prompt") or not row.get("expected")]
        evidence["test_prompts"] = {"count": len(prompts), "bad": bad}
        if len(prompts) < 4 or bad:
            issues.append(issue("P1", "TEST_PROMPTS_WEAK", str(evidence["test_prompts"]), "test-prompts.json"))
        prompt_contract = json.dumps(prompts, ensure_ascii=False)
        prompt_terms = [
            "one image",
            "cover image",
            "allowed_templates",
            "ASSET_REUSED_ACROSS_PAGES",
            "COVER_ASSET_REUSED_INSIDE_BOOK",
        ]
        missing_prompt_terms = [term for term in prompt_terms if term not in prompt_contract]
        evidence["test_prompt_asset_contract"] = {"missing": missing_prompt_terms}
        if missing_prompt_terms:
            issues.append(issue("P1", "TEST_PROMPTS_ASSET_CONTRACT_WEAK", ", ".join(missing_prompt_terms), "test-prompts.json"))
    except Exception as exc:
        issues.append(issue("P1", "TEST_PROMPTS_INVALID", str(exc), "test-prompts.json"))

    golden_specs = (
        ("golden_rendered_pages", "assets/golden-sample/rendered-pages", 20),
        ("golden_rendered_pages_v2", "assets/golden-sample-v2/rendered-pages", 48),
    )
    for evidence_key, relative_dir, minimum in golden_specs:
        golden_dir = skill_dir / relative_dir
        if golden_dir.exists():
            rendered_pages = list(golden_dir.glob("*.png"))
            evidence[evidence_key] = {
                "status": "checked",
                "count": len(rendered_pages),
                "minimum": minimum,
            }
            if len(rendered_pages) < minimum:
                issues.append(
                    issue(
                        "P1",
                        "GOLDEN_RENDERED_PAGES_TOO_FEW" if minimum == 20 else "GOLDEN_V2_RENDERED_PAGES_TOO_FEW",
                        str(len(rendered_pages)),
                        relative_dir,
                    )
                )
        else:
            evidence[evidence_key] = {
                "status": "skipped",
                "reason": "optional authorized private golden regression fixture is not installed",
            }

    new_project = skill_dir / "scripts" / "new_project.py"
    if new_project.exists():
        new_project_text = new_project.read_text(encoding="utf-8")
        v2_scaffold_gate = "STARTER_V2" in new_project_text and "--starter" in new_project_text and "v2" in new_project_text
        evidence["v2_scaffold_entry"] = v2_scaffold_gate
        if not v2_scaffold_gate:
            issues.append(issue("P1", "V2_SCAFFOLD_ENTRY_MISSING", "new_project.py must support `--starter v2` and copy assets/starter-project-v2.", str(new_project.relative_to(skill_dir))))
        new_project_dynamic_profiles = {
            "safe_profile_name_parser": "PROFILE_NAME_RE" in new_project_text and "invalid profile names" in new_project_text,
            "no_fixed_profile_allowlist": "VALID_PROFILES" not in new_project_text,
            "profile_spec_derivation": "def derived_profile_spec" in new_project_text,
            "student_teacher_visibility_derivation": "def answer_visibility_for_profile" in new_project_text
            and '"teacher"' in new_project_text
            and '"student"' in new_project_text,
            "student_profile_removes_teacher_key": "def qa_without_teacher_key" in new_project_text
            and '"teacher-answer-key"' in new_project_text
            and '"answer-key-page"' in new_project_text,
        }
        evidence["new_project_dynamic_profiles"] = {
            "ok": all(new_project_dynamic_profiles.values()),
            "checks": new_project_dynamic_profiles,
        }
        if not all(new_project_dynamic_profiles.values()):
            issues.append(issue("P1", "NEW_PROJECT_DYNAMIC_PROFILES_MISSING", json.dumps(new_project_dynamic_profiles, ensure_ascii=False), str(new_project.relative_to(skill_dir))))

    starter_v2 = skill_dir / "assets" / "starter-project-v2"
    starter_v2_build = starter_v2 / "tools" / "build.py"
    starter_v2_render = starter_v2 / "tools" / "render_pdf.py"
    starter_v2_validate = starter_v2 / "tools" / "validate.py"
    starter_v2_teacher_page = starter_v2 / "pages" / "24-teacher-guide.md"
    if starter_v2_build.exists() and starter_v2_render.exists() and starter_v2_validate.exists() and starter_v2_teacher_page.exists():
        starter_v2_build_text = starter_v2_build.read_text(encoding="utf-8")
        starter_v2_render_text = starter_v2_render.read_text(encoding="utf-8")
        starter_v2_validate_text = starter_v2_validate.read_text(encoding="utf-8")
        starter_v2_teacher_text = starter_v2_teacher_page.read_text(encoding="utf-8")
        fixed_profile_choices = 'choices=["book-trim", "lesson-a4"]'
        starter_v2_profile_filtering = {
            "page_filter_helper": "def page_in_profile" in starter_v2_build_text,
            "build_loop_skips_excluded_pages": "if not page_in_profile(meta, profile, book):" in starter_v2_build_text,
            "visible_pages_renumbered": "page_no = 0" in starter_v2_build_text,
            "teacher_key_declares_audience": "audience: teacher" in starter_v2_teacher_text
            and "template: teacher-guide-page" in starter_v2_teacher_text,
            "build_accepts_dynamic_profiles": fixed_profile_choices not in starter_v2_build_text,
            "render_accepts_dynamic_profiles": fixed_profile_choices not in starter_v2_render_text,
            "validate_accepts_dynamic_profiles": fixed_profile_choices not in starter_v2_validate_text,
        }
        evidence["starter_v2_profile_filtering"] = {
            "ok": all(starter_v2_profile_filtering.values()),
            "checks": starter_v2_profile_filtering,
        }
        if not all(starter_v2_profile_filtering.values()):
            issues.append(issue("P1", "STARTER_V2_PROFILE_FILTERING_MISSING", json.dumps(starter_v2_profile_filtering, ensure_ascii=False), str(starter_v2.relative_to(skill_dir))))
        starter_v2_pages = sorted((starter_v2 / "pages").glob("*.md"))
        starter_v2_page_text = "\n".join(path.read_text(encoding="utf-8") for path in starter_v2_pages)
        starter_v2_repeat_templates = {
            "activity",
            "article-evidence",
            "article-opener",
            "categorizing-chart",
            "correction-rewrite",
            "exam-mini-set",
            "handbook",
            "sentence-map",
            "skill-method",
            "vocab-bank",
            "writing-planner",
        }
        starter_v2_missing_repeat_variants = []
        for page_path in starter_v2_pages:
            page_text = page_path.read_text(encoding="utf-8")
            frontmatter = page_text.split("---", 2)[1] if page_text.startswith("---") and page_text.count("---") >= 2 else page_text
            template_match = re.search(r"^template:\s*(.+)$", frontmatter, re.M)
            template = template_match.group(1).strip() if template_match else ""
            if template in starter_v2_repeat_templates and not re.search(r"^variant:\s*.+$", frontmatter, re.M):
                starter_v2_missing_repeat_variants.append(page_path.name)
        starter_v2_structure_metadata = {
            "page_shell_emits_variant": "data-variant" in starter_v2_build_text and "variant_slug" in starter_v2_build_text,
            "renderer_emits_surface_markers": "data-surface" in starter_v2_build_text and "data-surface-family" in starter_v2_build_text,
            "page_shell_emits_opener_layout": "data-opener-layout" in starter_v2_build_text and "opener_layout" in starter_v2_build_text,
            "page_shell_emits_opener_accent": "data-opener-accent" in starter_v2_build_text and "opener_accent" in starter_v2_build_text,
            "starter_pages_declare_opener_layouts": starter_v2_page_text.count("opener_layout:") >= 1,
            "starter_pages_declare_opener_accents": starter_v2_page_text.count("opener_accent:") >= 1,
            "starter_pages_declare_semantic_variants": starter_v2_page_text.count("variant:") >= 4,
            "starter_pages_include_task2_surface_variant": "variant: task2-agree-disagree-answer-ladder" in starter_v2_page_text,
            "starter_pages_include_listening_surface_variant": "variant: listening-part3-speaker-opinion-matrix" in starter_v2_page_text,
            "starter_pages_include_reading_surface_variant": "variant: reading-transfer-ticket-close" in starter_v2_page_text,
            "starter_pages_declare_split_band_opener": "opener_layout: split-band" in starter_v2_page_text,
            "starter_repeat_families_declare_variants": not starter_v2_missing_repeat_variants,
            "starter_css_has_opener_layout_variants": 'data-opener-layout="side-panel"' in starter_v2_build_text
            and 'data-opener-layout="split-band"' in starter_v2_build_text,
        }
        evidence["starter_v2_structure_metadata"] = {
            "ok": all(starter_v2_structure_metadata.values()),
            "checks": starter_v2_structure_metadata,
            "missing_repeat_variant_pages": starter_v2_missing_repeat_variants,
        }
        if not all(starter_v2_structure_metadata.values()):
            issues.append(issue("P1", "STARTER_V2_STRUCTURE_METADATA_MISSING", json.dumps(starter_v2_structure_metadata, ensure_ascii=False), str(starter_v2.relative_to(skill_dir))))

    starter_build = skill_dir / "assets" / "starter-project" / "tools" / "build.py"
    if starter_build.exists():
        starter_build_text = starter_build.read_text(encoding="utf-8")
        inline_cloze_selectors = (
            ".activity-block p .blank",
            ".activity-block li .blank",
            ".word-box .blank",
            ".words-to-know .blank",
            ".textbook-table td .blank",
            ".review-rules .blank",
            ".planner-prompt .blank",
            ".editing-checklist label .blank",
            ".handbook-page .blank",
            ".answer-table .blank",
        )
        blank_checks = {
            "underscore_runs_parse_to_blank": "def inline_text" in starter_build_text
            and "(?P<blank>_{3,})" in starter_build_text,
            "activity_items_parse_to_blank": "{inline_text(item)}</li>" in starter_build_text,
            "word_box_items_parse_to_blank": "word-box-item" in starter_build_text and "blank_mode='wordbox'" in starter_build_text,
            "activity_instructions_parse_to_blank": "{inline_text(meta['activity_instructions'])}</b>" in starter_build_text,
            "activity_instruction_fields_parse_to_blank": "{inline_text(meta['instructions'])}</b>" in starter_build_text,
            "table_cells_parse_to_blank": "f\"<td>{inline_text(cell)}</td>\"" in starter_build_text,
            "planner_prompts_parse_to_blank": "{inline_text(item['prompt'])}</p>" in starter_build_text,
            "blank_punctuation_kept_unbroken": "&#8288;" in starter_build_text
            and "，。；：！？、" in starter_build_text
            and "if punct or (prefix and blank_mode" in starter_build_text,
            "zero_height_blank_box": "height: 0" in starter_build_text,
            "lower_edge_baseline_align": "vertical-align: -0.82em" in starter_build_text,
            "question_blank_lower_edge_adjustment": ".question-lines .blank" in starter_build_text and "vertical-align: -0.88em" in starter_build_text,
            "model_paragraph_cloze_adjustment": ".paragraph-practice p .blank" in starter_build_text and "vertical-align: -0.22em" in starter_build_text,
            "record_prompt_cloze_adjustment": ".record-prompt .blank" in starter_build_text and "vertical-align: -0.32em" in starter_build_text,
            "inline_cloze_context_adjustments": all(selector in starter_build_text for selector in inline_cloze_selectors)
            and "vertical-align: -0.30em" in starter_build_text,
            "compact_phrase_blank_adjustments": ".cloze-keep" in starter_build_text
            and "white-space: nowrap" in starter_build_text
            and "vertical-align: -0.26em" in starter_build_text
            and "vertical-align: -0.24em" in starter_build_text
            and "repeat(4, 1fr)" not in starter_build_text,
            "question_prompts_strip_blanks_before_write_lines": "def prompt_text_before_write_lines" in starter_build_text
            and "prompt_text_before_write_lines(q)" in starter_build_text
            and r"_{3,}" in starter_build_text,
            "exam_stem_slot_contract": "def exam_stem_text" in starter_build_text
            and ".exam-stem-slot" in starter_build_text
            and "exam_stem_text(prompt)" in starter_build_text
            and ".exam-stem-keep" in starter_build_text,
            "sentence_map_card_stack_contract": "def sentence_map_cards" in starter_build_text
            and "sentence-map-card-stack" in starter_build_text
            and 'data-surface-family="sentence-map"' in starter_build_text
            and 'data-surface="a4-card-stack"' in starter_build_text,
            "editing_checklist_control_isolated": "check-mark" in starter_build_text
            and ".editing-checklist .check-mark" in starter_build_text
            and ".editing-checklist label span" not in starter_build_text,
            "editing_checklist_compact_blank_adjustment": ".editing-checklist label .blank" in starter_build_text
            and "vertical-align: -0.24em" in starter_build_text,
            "old_centered_blank_rejected": all(
                value not in starter_build_text
                for value in ("height: 0.16em", "vertical-align: -0.42em", "vertical-align: -0.44em", "vertical-align: -0.64em", "vertical-align: -0.68em")
            ),
            "no_old_upward_transform": "translateY(-2pt)" not in starter_build_text,
        }
        blank_css_ok = all(blank_checks.values())
        evidence["blank_baseline_css"] = {"ok": blank_css_ok, "checks": blank_checks}
        if not blank_css_ok:
            issues.append(issue("P1", "BLANK_BASELINE_CSS_WEAK", "Starter must convert underscore runs to contextual .blank rules, bind ASCII/CJK punctuation, use -0.82em / -0.88em for writing lines, use -0.22em for paragraph cloze blanks, use -0.32em for record-prompt cloze blanks, use -0.30em for inline cloze containers, use compact no-wrap word-box/mini-rule blanks, and reject legacy centered values.", str(starter_build.relative_to(skill_dir))))
        starter_component_tokens = {
            "title_single_lockup": "title-single" in starter_build_text and "white-space: nowrap" in starter_build_text,
            "mixed_title_same_scale": ".title-page h1.title-single .title-for" in starter_build_text
            and "font-size: 1em" in starter_build_text
            and "font-size: .86em" not in starter_build_text
            and "font-size: 0.86em" not in starter_build_text,
            "cover_brand_bottom_right": "Eric Teaching Studio" in starter_build_text
            and "cover-brand" in starter_build_text
            and "right: 39pt" in starter_build_text
            and "bottom: 40pt" in starter_build_text
            and "cover-top b" not in starter_build_text,
            "planner_rule_strip": "planner-note" in starter_build_text and "planner-prompt" in starter_build_text,
            "planner_row_cards": "planner-rows" in starter_build_text and "planner-row" in starter_build_text and "planner-key" in starter_build_text,
            "no_plain_planner_table": "planner-table" not in starter_build_text,
            "workbook_record_surface": "workbook-record" in starter_build_text and "workbook-practice" in starter_build_text,
            "handbook_mini_rules": "handbook-rules" in starter_build_text,
            "unit_opener_prompt_integrated": "opener-prompt" in starter_build_text
            and "objectives-intro" in starter_build_text
            and "objectives-list" in starter_build_text
            and "photo-caption" not in starter_build_text,
        }
        evidence["starter_component_locks"] = starter_component_tokens
        for name, ok in starter_component_tokens.items():
            if not ok:
                issues.append(issue("P1", "STARTER_COMPONENT_LOCK_MISSING", f"Starter build missing {name}.", str(starter_build.relative_to(skill_dir))))

    starter_manifest = skill_dir / "assets" / "starter-project" / "assets" / "manifest.json"
    starter_pages = skill_dir / "assets" / "starter-project" / "pages"
    if starter_manifest.exists() and starter_pages.exists():
        try:
            manifest = json.loads(starter_manifest.read_text(encoding="utf-8"))
            assets = manifest.get("assets", [])
            assets_by_id = {str(asset.get("id")): asset for asset in assets}
            paths = [str(asset.get("path", "")) for asset in assets if asset.get("path")]
            page_refs: list[dict[str, str]] = []
            for page in sorted(starter_pages.glob("*.md")):
                frontmatter = parse_frontmatter(page.read_text(encoding="utf-8"))
                if frontmatter.get("asset"):
                    page_refs.append(
                        {
                            "page": page.name,
                            "template": frontmatter.get("template", ""),
                            "asset": frontmatter.get("asset", ""),
                        }
                    )
            refs_by_template = {ref["template"]: ref["asset"] for ref in page_refs}
            expected_role_assets = {
                "cover": "canyon-cover",
                "unit-opener": "sentence-basics-unit-opener",
                "photo-passage": "place-observation-passage",
            }
            starter_asset_checks = {
                "has_three_visual_assets": all(asset_id in assets_by_id for asset_id in expected_role_assets.values()),
                "manifest_paths_unique": len(paths) == len(set(paths)),
                "all_visual_assets_declare_allowed_templates": all(asset.get("allowed_templates") for asset in assets),
                "cover_asset_cover_only": assets_by_id.get("canyon-cover", {}).get("allowed_templates") == ["cover"],
                "pages_use_expected_distinct_assets": refs_by_template == expected_role_assets,
                "page_asset_refs_unique": len([ref["asset"] for ref in page_refs]) == len(set(ref["asset"] for ref in page_refs)),
            }
            evidence["starter_asset_uniqueness"] = {
                "ok": all(starter_asset_checks.values()),
                "checks": starter_asset_checks,
                "page_refs": page_refs,
            }
            if not all(starter_asset_checks.values()):
                issues.append(issue("P1", "STARTER_ASSET_UNIQUENESS_WEAK", json.dumps(evidence["starter_asset_uniqueness"], ensure_ascii=False), "assets/starter-project/assets/manifest.json"))
        except Exception as exc:
            issues.append(issue("P1", "STARTER_ASSET_CONTRACT_INVALID", str(exc), "assets/starter-project/assets/manifest.json"))

    skill_qa = skill_dir / "scripts" / "qa_textbook_pdf.py"
    if skill_qa.exists():
        skill_qa_text = skill_qa.read_text(encoding="utf-8")
        literal_blank_gate = "LITERAL_UNDERSCORE_BLANKS" in skill_qa_text and "literal_underscore_runs" in skill_qa_text
        evidence["literal_underscore_blank_gate"] = literal_blank_gate
        if not literal_blank_gate:
            issues.append(issue("P1", "LITERAL_UNDERSCORE_GATE_MISSING", "Skill QA must block generated HTML/PDF text that still contains 3+ underscore runs.", str(skill_qa.relative_to(skill_dir))))
        workbook_record_gate = "WORKBOOK_RECORD_SURFACE_MISSING" in skill_qa_text and "workbook_record_checks" in skill_qa_text
        evidence["workbook_record_gate"] = workbook_record_gate
        if not workbook_record_gate:
            issues.append(issue("P1", "WORKBOOK_RECORD_GATE_MISSING", "Skill QA must block loose activity/workbook tails without a cohesive record surface.", str(skill_qa.relative_to(skill_dir))))
        title_lockup_gate = "MIXED_TITLE_SCALE_DRIFT" in skill_qa_text and "title_lockup_css_checks" in skill_qa_text
        evidence["title_lockup_gate"] = title_lockup_gate
        if not title_lockup_gate:
            issues.append(issue("P1", "TITLE_LOCKUP_GATE_MISSING", "Skill QA must block mixed title-page lockups that shrink name/suffix text inside the same H1.", str(skill_qa.relative_to(skill_dir))))
        cover_brand_gate = "COVER_BRAND_MARK_MISSING" in skill_qa_text and "COVER_BRAND_CONTRAST_WEAK" in skill_qa_text and "COVER_TOP_LEVEL_BADGE" in skill_qa_text and "cover_brand_checks" in skill_qa_text
        evidence["cover_brand_gate"] = cover_brand_gate
        if not cover_brand_gate:
            issues.append(issue("P1", "COVER_BRAND_GATE_MISSING", "Skill QA must require Eric Teaching Studio as a readable bottom-right cover brand and block level/stage badges in cover-top.", str(skill_qa.relative_to(skill_dir))))
        checklist_control_gate = "CHECKLIST_CONTROL_SELECTOR_LEAK" in skill_qa_text and "checklist_control_css_checks" in skill_qa_text
        evidence["checklist_control_gate"] = checklist_control_gate
        if not checklist_control_gate:
            issues.append(issue("P1", "CHECKLIST_CONTROL_GATE_MISSING", "Skill QA must block generic checklist control selectors that can style content blanks as checkbox rectangles.", str(skill_qa.relative_to(skill_dir))))
        duplicated_question_gate = "QUESTION_INLINE_BLANK_WITH_WRITE_LINE" in skill_qa_text and "duplicated_question_blank_hits" in skill_qa_text
        evidence["duplicated_question_blank_gate"] = duplicated_question_gate
        if not duplicated_question_gate:
            issues.append(issue("P1", "QUESTION_LINE_DOUBLE_BLANK_GATE_MISSING", "Skill QA must block question-line prompts that render both inline .blank and dedicated .write-line answer space.", str(skill_qa.relative_to(skill_dir))))
        exam_stem_slot_gate = "EXAM_STEM_SLOT_DRIFT" in skill_qa_text and "exam_stem_slot_policy" in skill_qa_text
        evidence["exam_stem_slot_gate"] = exam_stem_slot_gate
        if not exam_stem_slot_gate:
            issues.append(issue("P1", "EXAM_STEM_SLOT_GATE_MISSING", "Skill QA must block guided MCQ/cloze stems that use generic .blank, literal underscores, or detached punctuation instead of .exam-stem-slot.", str(skill_qa.relative_to(skill_dir))))
        a4_sentence_map_gate = "A4_SENTENCE_MAP_TABLE_CRAMP" in skill_qa_text and "a4_sentence_map_surface_policy" in skill_qa_text
        evidence["a4_sentence_map_gate"] = a4_sentence_map_gate
        if not a4_sentence_map_gate:
            issues.append(issue("P1", "A4_SENTENCE_MAP_GATE_MISSING", "Skill QA must block A4 sentence-map pages that still use wide cramped tables instead of card-stack surfaces.", str(skill_qa.relative_to(skill_dir))))
        a4_only_profile_gate = "A4_ONLY_PROFILE_RESIDUE" in skill_qa_text and "a4_only_profile_policy" in skill_qa_text
        evidence["a4_only_profile_gate"] = a4_only_profile_gate
        if not a4_only_profile_gate:
            issues.append(issue("P1", "A4_ONLY_PROFILE_GATE_MISSING", "Skill QA must block book-trim/profile residue when a project declares qa.output_mode: a4-only.", str(skill_qa.relative_to(skill_dir))))
        answer_visibility_gate = (
            "answer_visibility_policy" in skill_qa_text
            and "ANSWER_VISIBILITY_MODES" in skill_qa_text
            and "STUDENT_ANSWER_VISIBILITY_LEAK" in skill_qa_text
            and "student-with-answer-key" in skill_qa_text
        )
        evidence["answer_visibility_gate"] = answer_visibility_gate
        if not answer_visibility_gate:
            issues.append(issue("P1", "ANSWER_VISIBILITY_GATE_MISSING", "Skill QA must block answer-key or teacher-only pages in clean student profiles and support explicit student/teacher answer visibility modes.", str(skill_qa.relative_to(skill_dir))))
        generic_identity_gate = "GENERIC_BOOK_IDENTITY_WEAK" in skill_qa_text and "generic_book_identity_policy" in skill_qa_text
        evidence["generic_identity_gate"] = generic_identity_gate
        if not generic_identity_gate:
            issues.append(issue("P1", "GENERIC_IDENTITY_GATE_MISSING", "Skill QA must block final generic books that only remove a student name without adding a publishable identity.", str(skill_qa.relative_to(skill_dir))))
        page_role_rhythm_gate = "PAGE_ROLE_RHYTHM_WEAK" in skill_qa_text and "page_role_rhythm_policy" in skill_qa_text
        evidence["page_role_rhythm_gate"] = page_role_rhythm_gate
        if not page_role_rhythm_gate:
            issues.append(issue("P1", "PAGE_ROLE_RHYTHM_GATE_MISSING", "Skill QA must flag long v2 books that pass family coverage but still read as repeated form runs.", str(skill_qa.relative_to(skill_dir))))
        page_role_variant_gate = "PAGE_ROLE_VARIANT_RHYTHM_WEAK" in skill_qa_text and "page_role_variant_policy" in skill_qa_text
        evidence["page_role_variant_gate"] = page_role_variant_gate
        if not page_role_variant_gate:
            issues.append(issue("P1", "PAGE_ROLE_VARIANT_GATE_MISSING", "Skill QA must require semantic variants for long-book planner/final-check pages so repeated forms become distinct page roles.", str(skill_qa.relative_to(skill_dir))))
        page_structure_variant_gate = (
            "PAGE_STRUCTURE_VARIANT_LIBRARY_WEAK" in skill_qa_text
            and "page_structure_variant_library_policy" in skill_qa_text
            and "rendered_page_records" in skill_qa_text
            and "metadata_only_surface_pages" in skill_qa_text
            and "missing_surface_family_pages" in skill_qa_text
            and "page_rendered_surface_key" in skill_qa_text
        )
        evidence["page_structure_variant_gate"] = page_structure_variant_gate
        if not page_structure_variant_gate:
            issues.append(issue("P1", "PAGE_STRUCTURE_VARIANT_GATE_MISSING", "Skill QA must flag repeated long-book template families that lack semantic structure variants beyond planner/final-check.", str(skill_qa.relative_to(skill_dir))))
        unit_opener_variation_gate = "UNIT_OPENER_VARIATION_WEAK" in skill_qa_text and "unit_opener_variation_checks" in skill_qa_text
        evidence["unit_opener_variation_gate"] = unit_opener_variation_gate
        if not unit_opener_variation_gate:
            issues.append(issue("P1", "UNIT_OPENER_VARIATION_GATE_MISSING", "Skill QA must flag long books whose unit openers reuse one accent and one layout across every unit.", str(skill_qa.relative_to(skill_dir))))
        rendered_freshness_gate = "RENDERED_ARTIFACTS_STALE" in skill_qa_text and "rendered_artifact_freshness_checks" in skill_qa_text
        evidence["rendered_freshness_gate"] = rendered_freshness_gate
        if not rendered_freshness_gate:
            issues.append(issue("P1", "RENDERED_FRESHNESS_GATE_MISSING", "Skill QA must block stale rendered PNG/contact-sheet evidence that is older than the current HTML/PDF.", str(skill_qa.relative_to(skill_dir))))
        source_output_freshness_gate = "SOURCE_OUTPUTS_STALE" in skill_qa_text and "source_output_freshness_checks" in skill_qa_text
        evidence["source_output_freshness_gate"] = source_output_freshness_gate
        if not source_output_freshness_gate:
            issues.append(issue("P1", "SOURCE_OUTPUT_FRESHNESS_GATE_MISSING", "Skill QA must block HTML/PDF outputs that are older than current source pages, manifest, theme, assets, or renderer inputs.", str(skill_qa.relative_to(skill_dir))))
        review_path_gate = "review_paths_ok" in skill_qa_text and "review_artifact_evidence" in skill_qa_text
        evidence["review_path_gate"] = review_path_gate
        if not review_path_gate:
            issues.append(issue("P1", "VISUAL_REVIEW_PATH_GATE_MISSING", "Skill QA must verify visual-review contact sheet and key-page paths exist and match the active profile.", str(skill_qa.relative_to(skill_dir))))
        review_freshness_gate = "review_fresh_after_artifacts" in skill_qa_text and "max_reviewed_artifact_mtime" in skill_qa_text
        evidence["review_freshness_gate"] = review_freshness_gate
        if not review_freshness_gate:
            issues.append(issue("P1", "VISUAL_REVIEW_FRESHNESS_GATE_MISSING", "Skill QA must reject stale human review files that predate their referenced contact sheet or rendered key pages.", str(skill_qa.relative_to(skill_dir))))
        final_asset_gate = (
            "ASSET_MODE_FINAL" in skill_qa_text
            and "FINAL_ASSET_SOURCE_NOT_APPROVED" in skill_qa_text
            and "FINAL_ASSET_PLACEHOLDER_OR_PROOF" in skill_qa_text
            and "IMAGEGEN_PROMPT_MISSING" in skill_qa_text
            and "COVER_CONTENT_CONCEPT_MISSING" in skill_qa_text
            and "COVER_UNIQUENESS_NOTE_MISSING" in skill_qa_text
            and "FINAL_ASSET_UNINTERPRETABLE_SCENE" in skill_qa_text
            and "asset_interpretable_scene_policy" in skill_qa_text
            and "asset_nature_first_policy" in skill_qa_text
            and "FINAL_ASSET_NATURE_FIRST_RATIONALE_MISSING" in skill_qa_text
            and "ANIMAL_STYLE_DRIFT_TERMS" in skill_qa_text
            and "asset_metadata_policy" in skill_qa_text
            and "NATURE_ASSET_ANCHORS" in skill_qa_text
            and "wildlife" in skill_qa_text
            and "mascot" in skill_qa_text
        )
        evidence["final_asset_gate"] = final_asset_gate
        if not final_asset_gate:
            issues.append(issue("P1", "FINAL_ASSET_GATE_MISSING", "Skill QA must block proof/procedural/starter/uninterpretable visual assets in final-assets mode and require ImageGen prompt/source/focus/no-text/real-world-scene manifest evidence, including nature/wildlife anchors and a P2 rationale gate when second-family school/study/modern-life visuals are chosen.", str(skill_qa.relative_to(skill_dir))))
        asset_usage_gate = (
            "asset_usage_policy" in skill_qa_text
            and "ASSET_REUSED_ACROSS_PAGES" in skill_qa_text
            and "ASSET_PATH_REUSED_IN_MANIFEST" in skill_qa_text
            and "COVER_ASSET_REUSED_INSIDE_BOOK" in skill_qa_text
            and "ASSET_ALLOWED_TEMPLATE_MISMATCH" in skill_qa_text
            and "asset_refs_match_allowed_templates" in skill_qa_text
        )
        evidence["asset_usage_gate"] = asset_usage_gate
        if not asset_usage_gate:
            issues.append(issue("P1", "ASSET_USAGE_GATE_MISSING", "Skill QA must enforce one-image-one-use, unique manifest paths, cover-only cover assets, and allowed_templates matches.", str(skill_qa.relative_to(skill_dir))))
        v2_page_family_gate = (
            "page_family_coverage_policy" in skill_qa_text
            and "V2_PAGE_FAMILY_COVERAGE_MISSING" in skill_qa_text
            and "page_family_mode" in skill_qa_text
            and "v2-full" in skill_qa_text
        )
        evidence["v2_page_family_gate"] = v2_page_family_gate
        if not v2_page_family_gate:
            issues.append(issue("P1", "V2_PAGE_FAMILY_GATE_MISSING", "Skill QA must enforce full v2 page-family coverage when page_family_mode is v2-full.", str(skill_qa.relative_to(skill_dir))))

    new_project = skill_dir / "scripts" / "new_project.py"
    if new_project.exists():
        new_project_text = new_project.read_text(encoding="utf-8")
        scaffold_ignore_gate = all(
            token in new_project_text
            for token in ("shutil.ignore_patterns", "__pycache__", "*.pyc", "_qa", "outputs", "node_modules")
        )
        evidence["scaffold_generated_artifact_ignore_gate"] = scaffold_ignore_gate
        if not scaffold_ignore_gate:
            issues.append(issue("P1", "SCAFFOLD_GENERATED_ARTIFACT_IGNORE_MISSING", "new_project.py must ignore generated outputs, QA evidence, caches, and pyc files when copying starter projects.", str(new_project.relative_to(skill_dir))))

    starter_validate = skill_dir / "assets" / "starter-project" / "tools" / "validate.py"
    if starter_validate.exists():
        starter_validate_text = starter_validate.read_text(encoding="utf-8")
        self_noise_terms = [
            "Pathways to Better Writing",
            "English Writing System",
            "Sentences, Paragraphs, and Writing Practice",
            "A Good Place to Observe",
            "The Best Place to Think",
            "canyon-cover",
        ]
        self_noise_hits = [term for term in self_noise_terms if term in starter_validate_text]
        evidence["starter_validator_self_noise_hits"] = self_noise_hits
        if self_noise_hits:
            issues.append(issue("P1", "STARTER_VALIDATOR_SELF_NOISE", ", ".join(self_noise_hits), str(starter_validate.relative_to(skill_dir))))
        duplicated_question_validator_gate = "duplicated_question_blanks" in starter_validate_text and "question prompt has inline blank plus writing line" in starter_validate_text
        evidence["starter_duplicated_question_blank_gate"] = duplicated_question_validator_gate
        if not duplicated_question_validator_gate:
            issues.append(issue("P1", "STARTER_QUESTION_LINE_DOUBLE_BLANK_GATE_MISSING", "Starter validator must fail if a question-line item contains both inline blanks and write lines.", str(starter_validate.relative_to(skill_dir))))
        starter_asset_usage_gate = (
            "asset_usage_checks" in starter_validate_text
            and "asset_refs_single_use" in starter_validate_text
            and "cover_assets_not_used_inside" in starter_validate_text
            and "asset_refs_match_allowed_templates" in starter_validate_text
        )
        evidence["starter_asset_usage_gate"] = starter_asset_usage_gate
        if not starter_asset_usage_gate:
            issues.append(issue("P1", "STARTER_ASSET_USAGE_GATE_MISSING", "Starter validator must enforce one-image-one-use and cover-only asset references.", str(starter_validate.relative_to(skill_dir))))

    return issues, evidence


def validate_scripts(skill_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    evidence: dict[str, Any] = {}
    commands = {
        "new_project_help": ["python3", str(skill_dir / "scripts" / "new_project.py"), "--help"],
        "qa_self_test": ["python3", str(skill_dir / "scripts" / "qa_textbook_pdf.py"), "--self-test", "--json"],
        "qa_contract_tests": ["python3", str(skill_dir / "scripts" / "test_qa_textbook_pdf.py")],
    }
    for name, cmd in commands.items():
        code, out = run(cmd)
        evidence[name] = {"returncode": code, "output_tail": out[-800:]}
        if code != 0:
            issues.append(issue("P1", "SCRIPT_CHECK_FAILED", name))
    return issues, evidence


def validate_smoke(skill_dir: Path, skip_typst: bool = False) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    evidence: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="eric-designed-pdf-smoke-") as tmp:
        tmp_root = Path(tmp)
        project = tmp_root / "project"
        scaffold_cmd = [
            "python3",
            str(skill_dir / "scripts" / "new_project.py"),
            "--out",
            str(project),
            "--profiles",
            "book-trim,lesson-a4",
            "--include-typst",
        ]
        code, out = run(scaffold_cmd)
        evidence["scaffold"] = {"returncode": code, "output_tail": out[-800:]}
        if code != 0:
            issues.append(issue("P1", "SMOKE_SCAFFOLD_FAILED", out[-1000:]))
            return issues, evidence

        profile_results: dict[str, Any] = {}
        for profile in ["book-trim", "lesson-a4"]:
            result: dict[str, Any] = {}
            for step, cmd in [
                ("build", ["python3", "tools/build.py", "--profile", profile]),
                ("render", ["python3", "tools/render_pdf.py", "--profile", profile]),
                ("starter_validate", ["python3", "tools/validate.py", "--profile", profile]),
                ("skill_qa", ["python3", str(skill_dir / "scripts" / "qa_textbook_pdf.py"), "--root", str(project), "--profile", profile, "--json"]),
            ]:
                code, out = run(cmd, cwd=project)
                result[step] = {"returncode": code, "output_tail": out[-1200:]}
                if code != 0:
                    issues.append(issue("P1", "SMOKE_STEP_FAILED", f"{profile}:{step}: {out[-1000:]}"))
                    break
            profile_results[profile] = result
        evidence["profiles"] = profile_results

        if not skip_typst:
            typst = shutil.which("typst")
            if not typst:
                issues.append(issue("P1", "TYPST_MISSING", "typst executable not found"))
            else:
                pdf_path = project / "outputs" / "textbook-template-lesson-a4-typst-adapter.pdf"
                code, out = run([typst, "compile", "typst-adapter/lesson-a4-template.typ", str(pdf_path)], cwd=project)
                evidence["typst_compile"] = {"returncode": code, "output_tail": out[-1200:]}
                if code != 0:
                    issues.append(issue("P1", "TYPST_COMPILE_FAILED", out[-1000:]))
                else:
                    eric_pdf_qa, explicitly_configured = find_eric_pdf_qa(skill_dir)
                    if not eric_pdf_qa:
                        evidence["typst_eric_pdf_qa"] = {
                            "status": "missing" if explicitly_configured else "skipped",
                            "reason": (
                                "ERIC_PDF_SKILL_DIR does not contain scripts/qa_typst_a4.py"
                                if explicitly_configured
                                else "optional eric-pdf adapter is not installed beside this independent Skill"
                            ),
                        }
                        if explicitly_configured:
                            issues.append(issue("P1", "ERIC_PDF_QA_CONFIG_INVALID", evidence["typst_eric_pdf_qa"]["reason"]))
                    else:
                        cmd = [
                            "python3",
                            str(eric_pdf_qa),
                            "typst-adapter/lesson-a4-template.typ",
                            str(pdf_path),
                            "--out-dir",
                            "_qa/typst-smoke-pages",
                            "--profile",
                            "student",
                            "--overwrite",
                            "--require-visual-checks",
                            "--visual-check",
                            "cover,first-body,final,table",
                            "--json",
                        ]
                        code, out = run(cmd, cwd=project)
                        evidence["typst_eric_pdf_qa"] = {"returncode": code, "output_tail": out[-2000:]}
                        if code != 0:
                            issues.append(issue("P1", "TYPST_ERIC_PDF_QA_FAILED", out[-1500:]))

        project_v2 = tmp_root / "project-v2"
        scaffold_v2_cmd = [
            "python3",
            str(skill_dir / "scripts" / "new_project.py"),
            "--starter",
            "v2",
            "--out",
            str(project_v2),
            "--profiles",
            "book-trim,lesson-a4",
            "--include-typst",
        ]
        code, out = run(scaffold_v2_cmd)
        evidence["v2_scaffold"] = {"returncode": code, "output_tail": out[-800:]}
        if code != 0:
            issues.append(issue("P1", "SMOKE_V2_SCAFFOLD_FAILED", out[-1000:]))
            return issues, evidence
        v2_profile_results: dict[str, Any] = {}
        for profile in ["book-trim", "lesson-a4"]:
            result: dict[str, Any] = {}
            for step, cmd in [
                ("build", ["python3", "tools/build.py", "--profile", profile]),
                ("render", ["python3", "tools/render_pdf.py", "--profile", profile]),
                ("starter_validate", ["python3", "tools/validate.py", "--profile", profile]),
                ("skill_qa", ["python3", str(skill_dir / "scripts" / "qa_textbook_pdf.py"), "--root", str(project_v2), "--profile", profile, "--json"]),
            ]:
                code, out = run(cmd, cwd=project_v2)
                result[step] = {"returncode": code, "output_tail": out[-1200:]}
                if code != 0:
                    issues.append(issue("P1", "SMOKE_V2_STEP_FAILED", f"{profile}:{step}: {out[-1000:]}"))
                    break
            v2_profile_results[profile] = result
        evidence["v2_profiles"] = v2_profile_results

        project_dynamic = tmp_root / "project-v2-dynamic-profiles"
        scaffold_dynamic_cmd = [
            "python3",
            str(skill_dir / "scripts" / "new_project.py"),
            "--starter",
            "v2",
            "--out",
            str(project_dynamic),
            "--profiles",
            "student-book-trim,teacher-book-trim",
            "--include-typst",
        ]
        code, out = run(scaffold_dynamic_cmd)
        dynamic_profile_pdf_smoke: dict[str, Any] = {
            "scaffold": {"returncode": code, "output_tail": out[-800:]},
            "profiles": {},
            "checks": {},
        }
        evidence["dynamic_profile_pdf_smoke"] = dynamic_profile_pdf_smoke
        if code != 0:
            issues.append(issue("P1", "SMOKE_DYNAMIC_PROFILE_SCAFFOLD_FAILED", out[-1000:]))
            return issues, evidence

        for profile in ["student-book-trim", "teacher-book-trim"]:
            result: dict[str, Any] = {}
            failed = False
            for step, cmd, timeout in [
                ("build", ["python3", "tools/build.py", "--profile", profile], 60),
                ("render", ["python3", "tools/render_pdf.py", "--profile", profile], 180),
                ("starter_validate", ["python3", "tools/validate.py", "--profile", profile], 60),
                ("skill_qa", ["python3", str(skill_dir / "scripts" / "qa_textbook_pdf.py"), "--root", str(project_dynamic), "--profile", profile, "--json"], 120),
                ("pdftotext", ["pdftotext", str(project_dynamic / "outputs" / f"full-coverage-v2-{profile}.pdf"), "-"], 60),
            ]:
                code, out = run(cmd, cwd=project_dynamic, timeout=timeout)
                result[step] = {"returncode": code, "output_tail": out[-1200:]}
                if step == "pdftotext":
                    result["pdf_text_has_teacher_answer_key"] = (
                        "Teacher Answer Key" in out
                        or "Teacher Guide" in out
                        or "TEACHER GUIDE" in out
                    )
                if code != 0:
                    issues.append(issue("P1", "SMOKE_DYNAMIC_PROFILE_STEP_FAILED", f"{profile}:{step}: {out[-1000:]}"))
                    failed = True
                    break
            html_path = project_dynamic / "outputs" / f"full-coverage-v2-{profile}.html"
            rendered_pages = sorted((project_dynamic / "_qa" / "rendered-pages").glob(f"{profile}-page-*.png"))
            contact_sheet = project_dynamic / "_qa" / f"contact-sheet-{profile}.png"
            if html_path.exists():
                html_text = html_path.read_text(encoding="utf-8")
                result["html_has_teacher_key_template"] = (
                    'data-template="teacher-answer-key"' in html_text
                    or 'data-template="teacher-guide-page"' in html_text
                )
                result["html_has_teacher_answer_key"] = (
                    "Teacher Answer Key" in html_text
                    or "Teacher Guide" in html_text
                    or "TEACHER GUIDE" in html_text
                )
            result["rendered_pages"] = len(rendered_pages)
            result["contact_sheet_exists"] = contact_sheet.exists()
            result["failed"] = failed
            dynamic_profile_pdf_smoke["profiles"][profile] = result

        student_result = dynamic_profile_pdf_smoke["profiles"].get("student-book-trim", {})
        teacher_result = dynamic_profile_pdf_smoke["profiles"].get("teacher-book-trim", {})
        checks = {
            "student_pdf_excludes_teacher_key": not student_result.get("pdf_text_has_teacher_answer_key", True),
            "student_html_excludes_teacher_key": not student_result.get("html_has_teacher_answer_key", True)
            and not student_result.get("html_has_teacher_key_template", True),
            "teacher_pdf_includes_teacher_key": bool(teacher_result.get("pdf_text_has_teacher_answer_key")),
            "teacher_html_includes_teacher_key": bool(teacher_result.get("html_has_teacher_answer_key"))
            and bool(teacher_result.get("html_has_teacher_key_template")),
            "student_rendered_pages_exact": student_result.get("rendered_pages") == 24,
            "teacher_rendered_pages_exact": teacher_result.get("rendered_pages") == 25,
            "student_contact_sheet_exists": bool(student_result.get("contact_sheet_exists")),
            "teacher_contact_sheet_exists": bool(teacher_result.get("contact_sheet_exists")),
        }
        dynamic_profile_pdf_smoke["checks"] = checks
        dynamic_profile_pdf_smoke["ok"] = all(checks.values())
        if not dynamic_profile_pdf_smoke["ok"]:
            issues.append(issue("P1", "DYNAMIC_PROFILE_PDF_SMOKE_FAILED", json.dumps(checks, ensure_ascii=False), str(project_dynamic)))
    return issues, evidence


def make_report(skill_dir: Path, issues: list[dict[str, Any]], evidence: dict[str, Any]) -> dict[str, Any]:
    counts = {sev: sum(1 for item in issues if item["severity"] == sev) for sev in ["P0", "P1", "P2", "P3"]}
    status = "fail" if counts["P0"] or counts["P1"] else ("warn" if counts["P2"] or counts["P3"] else "pass")
    return {
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(skill_dir),
        "summary": {"counts": counts, "strict_fail_severities": sorted(STRICT)},
        "issues": issues,
        "evidence": evidence,
        "next_action": "Fix blocking issues and rerun." if status == "fail" else "Skill gates passed.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the eric-designed-pdf skill package.")
    parser.add_argument("skill_dir", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--skip-smoke", action="store_true")
    parser.add_argument("--skip-typst", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    skill_dir = args.skill_dir.expanduser().resolve()
    issues: list[dict[str, Any]] = []
    evidence: dict[str, Any] = {}
    for name, validator in [("static", validate_static), ("scripts", validate_scripts)]:
        sub_issues, sub_evidence = validator(skill_dir)
        issues.extend(sub_issues)
        evidence[name] = sub_evidence
    if not args.skip_smoke:
        sub_issues, sub_evidence = validate_smoke(skill_dir, skip_typst=args.skip_typst)
        issues.extend(sub_issues)
        evidence["smoke"] = sub_evidence
    report = make_report(skill_dir, issues, evidence)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Status: {report['status']}")
        print(f"Counts: {report['summary']['counts']}")
        for item in issues:
            print(f"[{item['severity']}] {item['code']}: {item['detail']}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
