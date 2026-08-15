#!/usr/bin/env python3
"""Validate a Fusion Visual System bundle without mutating deliverables."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STRICT_SEVERITIES = {"P0", "P1"}
DNA_KEYS = {
    "visual_style",
    "component_structure",
    "composition",
    "shot_and_lens",
    "lighting",
    "color_science",
    "medium_texture",
    "mood",
    "rendering_feel",
    "era_culture",
    "spatial_logic",
    "density_blank_space",
    "dynamic_state",
    "post_processing",
    "signature_traits",
}
DOCUMENT_KEYS = {
    "information_hierarchy",
    "pagination",
    "data_visualization",
    "iconography",
    "accessibility",
    "medium_translation",
}
EXCLUSION_KEYS = {"logos", "copy", "imagery", "full_composition"}


@dataclass
class Issue:
    severity: str
    code: str
    file: str
    detail: str
    line: int | None = None


class Validator:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.issues: list[Issue] = []
        self.evidence: dict[str, Any] = {}

    def issue(self, severity: str, code: str, file: Path | str, detail: str, line: int | None = None) -> None:
        try:
            shown = str(Path(file).resolve().relative_to(self.root))
        except (ValueError, OSError):
            shown = str(file)
        self.issues.append(Issue(severity, code, shown, detail, line))

    def safe_path(self, value: Any, label: str) -> Path | None:
        if not isinstance(value, str) or not value.strip():
            self.issue("P0", "INVALID_PATH", label, "Path must be a non-empty relative string.")
            return None
        raw = Path(value)
        if raw.is_absolute() or ".." in raw.parts:
            self.issue("P0", "UNSAFE_PATH", label, f"Absolute or escaping path rejected: {value}")
            return None
        path = (self.root / raw).resolve()
        try:
            path.relative_to(self.root)
        except ValueError:
            self.issue("P0", "PATH_ESCAPE", label, f"Path escapes bundle root: {value}")
            return None
        return path

    def require_file(self, path: Path | None, code: str) -> bool:
        if path is None:
            return False
        if path.is_symlink():
            self.issue("P0", "SYMLINK_ARTIFACT", path, "Required bundle artifacts may not be symlinks.")
            return False
        if not path.is_file():
            self.issue("P0", code, path, "Required file is missing.")
            return False
        return True

    def read_text(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            self.issue("P0", "UNREADABLE_TEXT", path, str(exc))
            return ""

    def read_json(self, path: Path) -> dict[str, Any] | None:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            self.issue("P0", "INVALID_JSON", path, str(exc))
            return None
        if not isinstance(value, dict):
            self.issue("P0", "JSON_OBJECT_REQUIRED", path, "Top level must be a JSON object.")
            return None
        return value

    def validate_brief(self, path: Path) -> None:
        brief = self.read_json(path)
        if brief is None:
            return
        if brief.get("schema_version") != 1:
            self.issue("P1", "BRIEF_SCHEMA", path, "schema_version must equal 1.")

        dna = brief.get("visual_dna")
        if not isinstance(dna, dict):
            self.issue("P0", "DNA_MISSING", path, "visual_dna object is required.")
        else:
            missing = sorted(key for key in DNA_KEYS if not str(dna.get(key, "")).strip())
            if missing:
                self.issue("P1", "DNA_INCOMPLETE", path, "Missing visual DNA values: " + ", ".join(missing))

        extension = brief.get("document_extension")
        if not isinstance(extension, dict):
            self.issue("P1", "DOCUMENT_EXTENSION_MISSING", path, "document_extension object is required.")
        else:
            missing = sorted(key for key in DOCUMENT_KEYS if not str(extension.get(key, "")).strip())
            if missing:
                self.issue("P1", "DOCUMENT_EXTENSION_INCOMPLETE", path, "Missing values: " + ", ".join(missing))

        references = brief.get("references")
        adopted = 0
        if not isinstance(references, list) or len(references) < 2:
            self.issue("P1", "REFERENCE_COUNT", path, "At least two inspected references are required.")
        else:
            for index, reference in enumerate(references, 1):
                if not isinstance(reference, dict):
                    self.issue("P1", "REFERENCE_SHAPE", path, f"Reference {index} must be an object.")
                    continue
                if reference.get("adopted") is True:
                    adopted += 1
                    status = reference.get("license_status")
                    if status not in {"verified", "user-owned"}:
                        self.issue("P0", "UNVERIFIED_ADOPTION", path, f"Adopted reference {index} has license_status={status!r}.")
                if not reference.get("inspected_evidence"):
                    self.issue("P1", "UNINSPECTED_REFERENCE", path, f"Reference {index} lacks inspected_evidence.")
        if adopted < 2:
            self.issue("P1", "ADOPTED_REFERENCE_COUNT", path, "At least two inspected, rights-cleared references must be adopted.")

        originality = brief.get("originality")
        if not isinstance(originality, dict):
            self.issue("P0", "ORIGINALITY_MISSING", path, "originality object is required.")
        else:
            transformations = originality.get("transformations")
            if not isinstance(transformations, list) or len([x for x in transformations if str(x).strip()]) < 5:
                self.issue("P1", "TRANSFORMATIONS_INSUFFICIENT", path, "Record at least five concrete transformations.")
            excluded = {str(x) for x in originality.get("excluded", [])}
            missing = sorted(EXCLUSION_KEYS - excluded)
            if missing:
                self.issue("P1", "EXCLUSIONS_INCOMPLETE", path, "Missing exclusion classes: " + ", ".join(missing))

        banned_keys = {"artist_name", "studio_name", "brand_name", "source_copy"}
        serialized = json.dumps(brief, ensure_ascii=False)
        for key in banned_keys:
            if f'"{key}"' in serialized:
                self.issue("P1", "SOURCE_IDENTITY_FIELD", path, f"Remove source identity field: {key}")

    def validate_ledger(self, path: Path) -> None:
        text = self.read_text(path)
        required = {
            "ref_id",
            "source",
            "author",
            "source_class",
            "license",
            "license_status",
            "attribution",
            "adopted_rules",
            "excluded_elements",
            "verified_at",
        }
        header = next((line for line in text.splitlines() if line.startswith("|") and "ref_id" in line), "")
        missing = sorted(key for key in required if key not in header)
        if missing:
            self.issue("P1", "LEDGER_COLUMNS", path, "Missing ledger columns: " + ", ".join(missing))
        if "unverified" in text.lower() and re.search(r"\|\s*unverified\s*\|[^\n]*\|\s*(?!none|not adopted)", text, re.I):
            self.issue("P2", "UNVERIFIED_LEDGER_ITEM", path, "Review unverified entries and ensure nothing was adopted.")

    def validate_css(self, path: Path, required_tokens: list[str]) -> None:
        text = self.read_text(path)
        if not re.search(r"@page\s*{[^}]*size\s*:\s*A4", text, re.I | re.S):
            self.issue("P1", "A4_RULE_MISSING", path, "CSS must declare @page size: A4.")
        for token in required_tokens:
            if not re.search(rf"{re.escape(token)}\s*:", text):
                self.issue("P1", "TOKEN_MISSING", path, f"Required semantic token is missing: {token}")
        if "print-color-adjust: exact" not in text:
            self.issue("P2", "PRINT_COLOR_RULE", path, "Add print-color-adjust: exact for deterministic color output.")

    def validate_public_source(self, path: Path, forbidden_terms: list[str]) -> None:
        text = self.read_text(path)
        for match in re.finditer(r"https?://", text, re.I):
            line = text.count("\n", 0, match.start()) + 1
            self.issue("P1", "EXTERNAL_RUNTIME_URL", path, "Public source must use local assets only.", line)
        for marker in ("/Users/", "file://", "TODO", "待 Research", "内部审查"):
            if marker in text:
                self.issue("P1", "PUBLIC_PROCESS_LEAK", path, f"Public source contains forbidden marker: {marker}")
        for term in forbidden_terms:
            if term and term in text:
                self.issue("P1", "PUBLIC_FORBIDDEN_TERM", path, f"Public source contains forbidden term: {term}")

    def run_command(self, command: list[str], file: Path, code: str) -> subprocess.CompletedProcess[str] | None:
        if shutil.which(command[0]) is None:
            self.issue("P1", "TOOL_MISSING", file, f"Required local tool is missing: {command[0]}")
            return None
        result = subprocess.run(command, text=True, capture_output=True, check=False)
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()[-800:]
            self.issue("P1", code, file, detail or f"Command failed: {' '.join(command)}")
        return result

    def validate_pdf(self, path: Path, expected_pages: int) -> None:
        info = self.run_command(["pdfinfo", str(path)], path, "PDFINFO_FAILED")
        if info and info.returncode == 0:
            pages = re.search(r"^Pages:\s+(\d+)", info.stdout, re.M)
            size = re.search(r"^Page size:\s+([\d.]+) x ([\d.]+) pts", info.stdout, re.M)
            if not pages or int(pages.group(1)) != expected_pages:
                self.issue("P1", "PDF_PAGE_COUNT", path, f"Expected {expected_pages} pages.")
            if not size or abs(float(size.group(1)) - 595.28) > 1 or abs(float(size.group(2)) - 841.89) > 1:
                self.issue("P1", "PDF_NOT_A4", path, "PDF page size is not A4 portrait.")
            self.evidence["pdfinfo"] = {"pages": pages.group(1) if pages else None, "size": size.groups() if size else None}

        text = self.run_command(["pdftotext", str(path), "-"], path, "PDF_TEXT_FAILED")
        if text and text.returncode == 0:
            length = len(text.stdout.strip())
            self.evidence["extracted_text_characters"] = length
            if length < 120:
                self.issue("P1", "PDF_LOW_TEXT", path, "Extracted PDF text is unexpectedly sparse.")
        self.run_command(["qpdf", "--check", str(path)], path, "QPDF_CHECK_FAILED")

    def validate_renders(self, pdf: Path, renders: list[Path], expected_pages: int) -> None:
        if len(renders) < expected_pages:
            self.issue("P1", "RENDER_COUNT", str(self.root), f"Expected at least {expected_pages} page renders.")
        fresh = 0
        for render in renders:
            if not self.require_file(render, "RENDER_MISSING"):
                continue
            if render.stat().st_size < 10_000:
                self.issue("P1", "RENDER_TOO_SMALL", render, "Rendered page file is unexpectedly small.")
            if render.stat().st_mtime + 1 >= pdf.stat().st_mtime:
                fresh += 1
            else:
                self.issue("P1", "STALE_RENDER", render, "Render is older than the PDF artifact.")
        self.evidence["fresh_renders"] = fresh


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Fusion validation report",
        "",
        f"- Status: **{report['status']}**",
        f"- Strict threshold: P0, P1",
        f"- Counts: {json.dumps(report['summary']['counts'], ensure_ascii=False)}",
        "",
        "## Issues",
        "",
    ]
    if not report["issues"]:
        lines.append("No executable blockers or warnings were found.")
    for issue in report["issues"]:
        location = f"{issue['file']}:{issue['line']}" if issue.get("line") else issue["file"]
        lines.append(f"- [{issue['severity']}] `{issue['code']}` — {location}: {issue['detail']}")
    lines.extend(["", "## Evidence", "", "```json", json.dumps(report["evidence"], ensure_ascii=False, indent=2), "```", "", "## Human review", "", report["human_review"], "", "## Next action", "", report["next_action"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", help="Fusion bundle root")
    parser.add_argument("--manifest", default="fusion-manifest.json")
    parser.add_argument("--out-dir", default="qa/fusion-validation")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--structure-only", action="store_true", help="Skip PDF/render checks for skill self-tests")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    validator = Validator(root)
    if not root.is_dir():
        print(json.dumps({"status": "fail", "issues": [{"severity": "P0", "code": "ROOT_MISSING", "file": str(root), "detail": "Bundle root is missing."}]}, ensure_ascii=False, indent=2))
        return 2

    manifest_path = validator.safe_path(args.manifest, "manifest")
    manifest: dict[str, Any] | None = None
    if validator.require_file(manifest_path, "MANIFEST_MISSING"):
        manifest = validator.read_json(manifest_path)

    if manifest:
        files = manifest.get("files")
        if not isinstance(files, dict):
            validator.issue("P0", "FILES_MAP_MISSING", manifest_path or "manifest", "Manifest files object is required.")
            files = {}

        resolved: dict[str, Path] = {}
        for key in ("brief", "tokens", "reference_ledger", "third_party_notices", "source_html", "source_css"):
            path = validator.safe_path(files.get(key), f"files.{key}")
            if validator.require_file(path, f"{key.upper()}_MISSING") and path is not None:
                resolved[key] = path

        if "brief" in resolved:
            validator.validate_brief(resolved["brief"])
        if "reference_ledger" in resolved:
            validator.validate_ledger(resolved["reference_ledger"])

        required_tokens = manifest.get("required_tokens", [])
        if not isinstance(required_tokens, list) or not all(isinstance(x, str) for x in required_tokens):
            validator.issue("P1", "TOKEN_CONTRACT", manifest_path or "manifest", "required_tokens must be a string array.")
            required_tokens = []
        css_paths = [resolved[key] for key in ("tokens", "source_css") if key in resolved]
        if css_paths:
            merged_css = "\n".join(validator.read_text(path) for path in css_paths)
            synthetic = validator.root / ".fusion-combined-css"
            if not re.search(r"@page\s*{[^}]*size\s*:\s*A4", merged_css, re.I | re.S):
                validator.issue("P1", "A4_RULE_MISSING", css_paths[-1], "Combined CSS must declare @page size: A4.")
            for token in required_tokens:
                if not re.search(rf"{re.escape(token)}\s*:", merged_css):
                    validator.issue("P1", "TOKEN_MISSING", synthetic, f"Required semantic token is missing: {token}")
            if "print-color-adjust: exact" not in merged_css:
                validator.issue("P2", "PRINT_COLOR_RULE", css_paths[-1], "Add print-color-adjust: exact.")

        forbidden_terms = manifest.get("forbidden_public_terms", [])
        if not isinstance(forbidden_terms, list):
            forbidden_terms = []
        for key in ("source_html", "source_css"):
            if key in resolved:
                validator.validate_public_source(resolved[key], [str(x) for x in forbidden_terms])

        expected_pages = manifest.get("expected_pages")
        if not isinstance(expected_pages, int) or expected_pages < 1:
            validator.issue("P1", "EXPECTED_PAGES", manifest_path or "manifest", "expected_pages must be a positive integer.")
            expected_pages = 1

        if not args.structure_only:
            pdf = validator.safe_path(files.get("pdf"), "files.pdf")
            if validator.require_file(pdf, "PDF_MISSING") and pdf is not None:
                validator.validate_pdf(pdf, expected_pages)
                render_values = files.get("rendered_pages", [])
                if not isinstance(render_values, list):
                    validator.issue("P1", "RENDER_LIST", manifest_path or "manifest", "rendered_pages must be an array.")
                    render_values = []
                renders = [path for value in render_values if (path := validator.safe_path(value, "files.rendered_pages")) is not None]
                validator.validate_renders(pdf, renders, expected_pages)

            review = validator.safe_path(files.get("visual_review"), "files.visual_review")
            if validator.require_file(review, "VISUAL_REVIEW_MISSING") and review is not None:
                text = validator.read_text(review)
                if "FINAL_VISUAL_REVIEW: PASS" not in text:
                    validator.issue("P1", "VISUAL_REVIEW_PENDING", review, "Required visual review sentinel is missing.")

    counts = {severity: sum(1 for issue in validator.issues if issue.severity == severity) for severity in ("P0", "P1", "P2", "P3")}
    has_blocker = bool(any(counts[x] for x in STRICT_SEVERITIES))
    status = "fail" if has_blocker else ("warn" if counts["P2"] or counts["P3"] else "pass")
    next_action = "Repair P0/P1 issues and rerun the validator." if has_blocker else ("Review warnings, then proceed to human visual review." if status == "warn" else "No executable blockers were found; preserve the evidence and proceed to delivery.")
    report = {
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "summary": {"counts": counts, "strict_fail_severities": sorted(STRICT_SEVERITIES)},
        "issues": [asdict(issue) for issue in validator.issues],
        "evidence": validator.evidence,
        "human_review": "Originality, visual quality, density, and page-role judgment remain human-reviewed even when this report passes.",
        "next_action": next_action,
    }

    if args.no_write:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        out_dir = validator.safe_path(args.out_dir, "out_dir")
        if out_dir is None:
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 2
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (out_dir / "report.md").write_text(markdown_report(report), encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))

    return 1 if args.strict and has_blocker else 0


if __name__ == "__main__":
    raise SystemExit(main())
