#!/usr/bin/env python3
"""Validate Eric PDF skill maintenance gates."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import tempfile
from pathlib import Path
from typing import Any


RUNTIME_RED_RE = re.compile(
    r"(在 Claude Code|Claude Code skill|Claude Code 用户|Cursor only|Codex 中|"
    r"^\[!\[Claude Code|~/\.claude/skills/[a-z]|/plugin install\b)",
    re.M,
)

REQUIRED_FILES = [
    "SKILL.md",
    "agents/openai.yaml",
    "references/document-types.md",
    "references/handbook-view.md",
    "references/math-materials.md",
    "assets/eric-pdf-template.typ",
    "assets/eric-pdf-document-types-demo.typ",
    "assets/eric-pdf-document-types-demo.pdf",
    "assets/eric-pdf-math-demo.typ",
    "assets/eric-pdf-math-demo-student.pdf",
    "assets/eric-pdf-math-demo-teacher.pdf",
    "scripts/build_eric_pdf.py",
    "scripts/qa_eric_pdf.py",
    "scripts/test_qa_eric_pdf.py",
    "scripts/validate_skill_gates.py",
    "test-prompts.json",
    "results.tsv",
]

REQUIRED_TOKENS = [
    "## Hard Completion Gates",
    "GATE 0: Scope lock",
    "GATE 1: Fresh compile",
    "GATE 2: Automated QA",
    "GATE 3: Rendered-page review",
    "GATE 4: Leak and version safety",
    "GATE 5: Evidence report",
    "Gate Evidence Ledger",
    "Do not end",
    "scripts/qa_eric_pdf.py",
    "typst compile",
    "rendered pages",
    "student/teacher",
    "--profile",
    "--require-visual-checks",
    "manual_visual_review",
    "profile_scan",
    "do not omit `--source`",
]

DEMO_QA_TARGETS = [
    (
        "document-types",
        "assets/eric-pdf-document-types-demo.pdf",
        "assets/eric-pdf-document-types-demo.typ",
    ),
    (
        "math-student",
        "assets/eric-pdf-math-demo-student.pdf",
        "assets/eric-pdf-math-demo.typ",
    ),
    (
        "math-teacher",
        "assets/eric-pdf-math-demo-teacher.pdf",
        "assets/eric-pdf-math-demo.typ",
    ),
]


def check(ok: bool, **details: Any) -> dict[str, Any]:
    return {"ok": ok, **details}


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


def load_qa_module(skill_dir: Path):
    path = skill_dir / "scripts" / "qa_eric_pdf.py"
    spec = importlib.util.spec_from_file_location("qa_eric_pdf", path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate(skill_dir: Path, run_demo_qa: bool = True) -> dict[str, Any]:
    skill_dir = skill_dir.expanduser().resolve()
    skill_path = skill_dir / "SKILL.md"
    text = skill_path.read_text(encoding="utf-8") if skill_path.exists() else ""
    frontmatter = parse_frontmatter(text)
    checks: dict[str, Any] = {}

    missing_files = [path for path in REQUIRED_FILES if not (skill_dir / path).exists()]
    checks["required_files"] = check(not missing_files, missing=missing_files)

    description = frontmatter.get("description", "")
    checks["frontmatter"] = check(
        frontmatter.get("name") == "eric-pdf"
        and description.startswith("Create, polish, compile, or QA")
        and len(description) <= 1024,
        name=frontmatter.get("name"),
        description_length=len(description),
    )

    missing_tokens = [token for token in REQUIRED_TOKENS if token not in text]
    checks["hard_gate_tokens"] = check(not missing_tokens, missing=missing_tokens)

    runtime_hits = [
        {"line": number, "text": line}
        for number, line in enumerate(text.splitlines(), start=1)
        if RUNTIME_RED_RE.search(line)
    ]
    checks["runtime_neutrality"] = check(not runtime_hits, hits=runtime_hits)

    try:
        prompts = json.loads((skill_dir / "test-prompts.json").read_text(encoding="utf-8"))
        bad_prompts = [
            index
            for index, item in enumerate(prompts, start=1)
            if not item.get("prompt") or not item.get("expected")
        ]
        checks["test_prompts"] = check(
            isinstance(prompts, list) and len(prompts) >= 3 and not bad_prompts,
            count=len(prompts) if isinstance(prompts, list) else None,
            bad_items=bad_prompts,
        )
    except Exception as exc:
        checks["test_prompts"] = check(False, error=str(exc))

    if run_demo_qa:
        demo_results: dict[str, Any] = {}
        try:
            qa_module = load_qa_module(skill_dir)
            with tempfile.TemporaryDirectory(prefix="eric-pdf-skill-gates-") as tmp:
                tmp_dir = Path(tmp)
                for name, pdf_rel, source_rel in DEMO_QA_TARGETS:
                    result = qa_module.qa(
                        skill_dir / pdf_rel,
                        skill_dir / source_rel,
                        tmp_dir / name,
                        profile="student" if name == "math-student" else ("teacher" if name == "math-teacher" else "general"),
                        visual_checks={"cover", "first-body", "dense", "final"},
                        require_visual_checks=True,
                        overwrite_rendered_pages=True,
                    )
                    demo_results[name] = {
                        "status": result.get("status"),
                        "rendered_pages": result.get("rendered_pages", []),
                        "failed_checks": [
                            key
                            for key, value in (result.get("checks") or {}).items()
                            if not value.get("ok")
                        ],
                    }
        except Exception as exc:
            checks["demo_pdf_qa"] = check(False, error=str(exc), results=demo_results)
        else:
            failed = [name for name, result in demo_results.items() if result["status"] != "pass"]
            checks["demo_pdf_qa"] = check(not failed, failed=failed, results=demo_results)

    status = "pass" if all(item["ok"] for item in checks.values()) else "fail"
    return {"status": status, "skill_dir": str(skill_dir), "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate eric-pdf skill gates.")
    parser.add_argument("skill_dir", nargs="?", default=Path(__file__).resolve().parents[1], type=Path)
    parser.add_argument("--skip-demo-qa", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload = validate(args.skill_dir, run_demo_qa=not args.skip_demo_qa)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Status: {payload['status']}")
        for name, result in payload["checks"].items():
            marker = "PASS" if result["ok"] else "FAIL"
            print(f"{marker} {name}: {result}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
