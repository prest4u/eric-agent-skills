#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import hashlib
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = SKILL_DIR / "scripts" / "validate_skill_gates.py"
PDF_VALIDATOR_PATH = SKILL_DIR / "scripts" / "validate_vocab_pdf.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("vocab_skill_gate", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load validate_skill_gates.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_pdf_validator():
    spec = importlib.util.spec_from_file_location("vocab_pdf_gate", PDF_VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load validate_vocab_pdf.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class VocabularySkillGateTest(unittest.TestCase):
    def test_current_skill_package_passes_maintenance_gate(self) -> None:
        module = load_validator()

        report = module.validate_package(SKILL_DIR)

        self.assertEqual(report["status"], "pass", report)
        self.assertEqual(report["counts"]["P0"], 0, report)
        self.assertEqual(report["counts"]["P1"], 0, report)
        self.assertGreaterEqual(report["evidence"]["test_prompt_count"], 3)
        self.assertTrue(report["evidence"]["validate_vocab_pdf_help_ok"])
        self.assertEqual(report["evidence"]["forbidden_skill_tokens"], [])

    def test_runtime_neutrality_scan_flags_legacy_claude_references(self) -> None:
        module = load_validator()

        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = Path(temp_dir)
            (skill_dir / "SKILL.md").write_text("Use Claude Code and ~/.claude/skills here.\n", encoding="utf-8")

            hits = module.runtime_red_hits(skill_dir)

        self.assertEqual([hit["code"] for hit in hits], ["RUNTIME_RED_REFERENCE", "RUNTIME_RED_REFERENCE"])

    def test_formal_review_is_bound_to_exact_pdf_sha256(self) -> None:
        module = load_pdf_validator()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            qa = root / "_qa"
            qa.mkdir()
            pdf = root / "candidate.pdf"
            pdf.write_bytes(b"frozen candidate")
            digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
            (qa / "visual-review-student-lesson-a4.md").write_text(
                "\n".join(
                    [
                        "FINAL_VISUAL_REVIEW: PASS",
                        "Reviewer: independent-review:vocab-release",
                        "Skills used: $eric-review, eric-pdf-vocabulary",
                        "Review method: sub-agent read-only review",
                        "Tone coordination: cover, opener, and body checked",
                        "Score: 9.5/10",
                        "P0: 0",
                        "P1: 0",
                        f"Artifact PDF SHA-256: {digest}",
                    ]
                ),
                encoding="utf-8",
            )
            issues: list[dict[str, str]] = []
            module.check_visual_review(root, "student-lesson-a4", issues, True, pdf)
            self.assertNotIn("FORMAL_REVIEW_PDF_IDENTITY_MISSING", [issue["code"] for issue in issues], issues)
            self.assertNotIn("FORMAL_REVIEW_PDF_IDENTITY_MISMATCH", [issue["code"] for issue in issues], issues)

    def test_formal_review_rejects_sha256_from_another_pdf(self) -> None:
        module = load_pdf_validator()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            qa = root / "_qa"
            qa.mkdir()
            pdf = root / "candidate.pdf"
            pdf.write_bytes(b"current candidate")
            (qa / "visual-review-student-lesson-a4.md").write_text(
                "\n".join(
                    [
                        "FINAL_VISUAL_REVIEW: PASS",
                        "Reviewer: independent-review:vocab-release",
                        "Skills used: $eric-review, eric-pdf-vocabulary",
                        "Review method: sub-agent read-only review",
                        "Tone coordination: checked",
                        "Score: 9.5/10",
                        "P0: 0",
                        "P1: 0",
                        f"Artifact PDF SHA-256: {'0' * 64}",
                    ]
                ),
                encoding="utf-8",
            )
            issues: list[dict[str, str]] = []
            module.check_visual_review(root, "student-lesson-a4", issues, True, pdf)
            self.assertIn("FORMAL_REVIEW_PDF_IDENTITY_MISMATCH", [issue["code"] for issue in issues], issues)


if __name__ == "__main__":
    unittest.main()
