#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


REQUIRED_FILES = [
    "SKILL.md",
    "agents/openai.yaml",
    "references/page-role-contracts.md",
    "references/writing-line-standards.md",
    "references/qa-checklist.md",
    "scripts/validate_vocab_pdf.py",
    "scripts/validate_skill_gates.py",
    "scripts/test_validate_skill_gates.py",
    "test-prompts.json",
]

REQUIRED_SKILL_TOKENS = [
    "## Vocabulary PDF boundary",
    "## Failure Branches",
    "## Review protocol",
    "validate_vocab_pdf.py",
    "validate_skill_gates.py",
    "--require-formal-review",
    "FINAL_VISUAL_REVIEW: PENDING",
    "eric-review",
    "Vocabulary Learning",
    "Eric Teaching Studio",
    "Memory Chain Lesson",
    "A words: 12",
    "B words: about 20",
    "C words: about 8",
    "memory-sentence-line",
    "glossary-record-line",
    "grammar-map-check-line",
    "red-review-line",
    "final-record-line",
    "next-plan-line",
    "no-row-rule-record",
    "VISIBLE_VOCAB_MARKER_LEAK",
    "B_WORD_SELECTOR_LEAK",
]

FORBIDDEN_SKILL_TOKENS = [
    "## \U0001f534 CHECKPOINT",
    "CREATE_EDIT",
    "AUDIT_ONLY",
    "FINAL_REVIEW",
    "RECHECK",
    "BLOCKED_REPAIR_BUDGET",
]

REQUIRED_REFERENCE_TOKENS = {
    "references/page-role-contracts.md": [
        "cover",
        "title",
        "unit-opener",
        "reading",
        "glossary",
        "memory-chain",
        "grammar bridge",
        "B/C recognition",
        "red-word challenge",
        "before-you-leave",
    ],
    "references/writing-line-standards.md": [
        "memory-sentence-line",
        "glossary-record-line",
        "grammar-map-check-line",
        "red-review-line",
        "final-record-line",
        "next-plan-line",
        "no-row-rule-record",
    ],
    "references/qa-checklist.md": [
        "FINAL_VISUAL_REVIEW",
        "eric-review",
        "Vocabulary Learning",
        "VISIBLE_VOCAB_MARKER_LEAK",
        "B_WORD_SELECTOR_LEAK",
    ],
}

RUNTIME_RED_TERMS = [
    "Claude" + " Code",
    "~/" + ".claude/skills",
    "TO" + "DO",
    "[" + "TO" + "DO",
]
RUNTIME_RED_RE = re.compile("|".join(re.escape(term) for term in RUNTIME_RED_TERMS), re.I)
SCAN_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".py"}
SKIP_SCAN_PARTS = {"__pycache__"}


def issue(severity: str, code: str, detail: str, file: str | None = None) -> dict[str, str]:
    payload = {"severity": severity, "code": code, "detail": detail}
    if file:
        payload["file"] = file
    return payload


def read_text(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def runtime_red_hits(skill_dir: Path) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for path in sorted(skill_dir.rglob("*")):
        if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
            continue
        if any(part in SKIP_SCAN_PARTS for part in path.parts):
            continue
        if path.name == "test_validate_skill_gates.py":
            continue
        text = read_text(path)
        for match in RUNTIME_RED_RE.finditer(text):
            rel = path.relative_to(skill_dir) if path.is_relative_to(skill_dir) else path
            hits.append(
                issue(
                    "P1",
                    "RUNTIME_RED_REFERENCE",
                    f"Runtime-specific reference found: {match.group(0)}",
                    str(rel),
                )
            )
    return hits


def load_test_prompts(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    if not path.exists():
        return [], ["test-prompts.json is missing."]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [], [f"test-prompts.json is not valid JSON: {exc}"]
    if not isinstance(data, list):
        return [], ["test-prompts.json must be a list."]
    errors: list[str] = []
    cases: list[dict[str, Any]] = []
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            errors.append(f"prompt {index} is not an object.")
            continue
        cases.append(item)
        for field in ("id", "prompt", "expected"):
            if not item.get(field):
                errors.append(f"prompt {index} is missing {field}.")
    if len(cases) < 3:
        errors.append("test-prompts.json must include at least three forward evaluation cases.")
    return cases, errors


def run_help(skill_dir: Path) -> tuple[bool, str]:
    script = skill_dir / "scripts" / "validate_vocab_pdf.py"
    if not script.exists():
        return False, "scripts/validate_vocab_pdf.py is missing."
    proc = subprocess.run(
        ["python3", str(script), "--help"],
        cwd=skill_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=30,
    )
    return proc.returncode == 0 and "--require-formal-review" in proc.stdout, proc.stdout


def validate_package(skill_dir: Path) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    evidence: dict[str, Any] = {}

    missing = [path for path in REQUIRED_FILES if not (skill_dir / path).exists()]
    if missing:
        issues.append(issue("P1", "REQUIRED_FILES_MISSING", ", ".join(missing)))

    skill_text = read_text(skill_dir / "SKILL.md")
    missing_tokens = [token for token in REQUIRED_SKILL_TOKENS if token not in skill_text]
    evidence["missing_skill_tokens"] = missing_tokens
    if missing_tokens:
        issues.append(issue("P1", "SKILL_TOKENS_MISSING", ", ".join(missing_tokens), "SKILL.md"))

    forbidden_tokens = [token for token in FORBIDDEN_SKILL_TOKENS if token in skill_text]
    evidence["forbidden_skill_tokens"] = forbidden_tokens
    if forbidden_tokens:
        issues.append(issue("P1", "LEGACY_CONTROL_TOKENS_PRESENT", ", ".join(forbidden_tokens), "SKILL.md"))

    missing_reference_tokens: dict[str, list[str]] = {}
    for rel_path, tokens in REQUIRED_REFERENCE_TOKENS.items():
        text = read_text(skill_dir / rel_path)
        missing_for_file = [token for token in tokens if token not in text]
        if missing_for_file:
            missing_reference_tokens[rel_path] = missing_for_file
    evidence["missing_reference_tokens"] = missing_reference_tokens
    if missing_reference_tokens:
        issues.append(issue("P1", "REFERENCE_TOKENS_MISSING", json.dumps(missing_reference_tokens, ensure_ascii=False)))

    prompts, prompt_errors = load_test_prompts(skill_dir / "test-prompts.json")
    evidence["test_prompt_count"] = len(prompts)
    if prompt_errors:
        issues.append(issue("P1", "TEST_PROMPTS_INVALID", "; ".join(prompt_errors), "test-prompts.json"))

    help_ok, help_output = run_help(skill_dir)
    evidence["validate_vocab_pdf_help_ok"] = help_ok
    evidence["validate_vocab_pdf_help_excerpt"] = help_output[:500]
    if not help_ok:
        issues.append(issue("P1", "VALIDATE_VOCAB_HELP_FAILED", "validate_vocab_pdf.py --help did not succeed or lacks release flag."))

    red_hits = runtime_red_hits(skill_dir)
    evidence["runtime_red_hits"] = red_hits
    issues.extend(red_hits)

    counts = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
    for row in issues:
        severity = row["severity"]
        counts[severity] = counts.get(severity, 0) + 1

    status = "pass"
    if counts["P0"] or counts["P1"]:
        status = "fail"
    elif counts["P2"] or counts["P3"]:
        status = "warn"

    return {
        "status": status,
        "counts": counts,
        "issues": issues,
        "evidence": evidence,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-dir", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = validate_package(Path(args.skill_dir).resolve())
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Status: {report['status']}")
        print(f"Counts: {report['counts']}")
        for row in report["issues"]:
            file_part = f" [{row['file']}]" if row.get("file") else ""
            print(f"{row['severity']} {row['code']}{file_part}: {row['detail']}")
    return 1 if report["counts"]["P0"] or report["counts"]["P1"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
