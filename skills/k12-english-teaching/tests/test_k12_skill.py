"""Small maintenance checks for the K12 runtime contract."""

from __future__ import annotations

import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (SKILL_DIR / relative).read_text(encoding="utf-8")


class K12RuntimeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = read("SKILL.md")
        cls.skill_lower = cls.skill.lower()
        cls.formal = read("references/formal-teaching-contract.md")
        cls.surface = read("references/student-source-contract.md")
        cls.metadata = read("agents/openai.yaml")

    def test_runtime_is_thin_and_uses_only_two_direct_references(self) -> None:
        self.assertLess(len(self.skill.splitlines()), 120)
        frontmatter = self.skill.split("---", 2)[1].strip().splitlines()
        self.assertEqual({"name", "description"}, {line.split(":", 1)[0] for line in frontmatter})
        self.assertIn("references/formal-teaching-contract.md", self.skill)
        self.assertIn("references/student-source-contract.md", self.skill)
        self.assertEqual(2, self.skill.count("references/"))
        self.assertTrue("For package maintenance only" in self.skill)
        self.assertNotIn("validate_k12_skill.py", self.skill)

    def test_implicit_owner_first_routing(self) -> None:
        self.assertIn("even when the user does not name this Skill", self.skill)
        self.assertIn("allow_implicit_invocation: true", self.metadata)
        self.assertIn("Keep `k12-english-teaching`", self.skill)
        for owner in (
            "eric-teaching-polish",
            "eric-parent-feedback",
            "eric-soft-signal",
            "eric-pdf-vocabulary",
        ):
            self.assertIn(owner, self.skill)

    def test_unknown_level_45_minute_reading_proceeds_with_diagnosis(self) -> None:
        self.assertIn("missing current level", self.skill)
        self.assertIn("embedded diagnostic", self.skill)
        self.assertIn("45-minute reading lesson with unknown level", self.formal)
        self.assertIn("complete runnable plan in the same response", self.formal)
        self.assertNotIn("explicit invocation remains", self.skill_lower)

    def test_pure_polish_routes_to_teaching_polish(self) -> None:
        self.assertRegex(
            self.skill,
            r"Language polish or de-AI editing of already-written teaching content only \| Route to `eric-teaching-polish`",
        )

    def test_parent_feedback_routes_to_parent_owner(self) -> None:
        self.assertRegex(self.skill, r"Parent feedback \| Route to `eric-parent-feedback`")

    def test_student_teacher_editions_have_parity_without_leakage(self) -> None:
        self.assertIn("same ordered task set", self.surface)
        self.assertIn("complete student wording and inputs in the same order", self.surface)
        for leak in ("answers", "teacher-only material", "internal task/target labels"):
            self.assertIn(leak, self.surface)
        self.assertIn("Keep answers", self.surface)

    def test_unverified_latest_tianjin_source_never_invents_provenance(self) -> None:
        self.assertIn("latest Tianjin Gaokao paper", self.surface)
        self.assertIn("must not produce invented question numbers or provenance", self.surface)
        self.assertIn("continue with original practice", self.surface)

    def test_draft_delivers_without_independent_review(self) -> None:
        self.assertIn("deliver the visible product directly", self.skill)
        self.assertIn("same-agent repair is sufficient", self.skill)
        self.assertNotIn("PENDING INDEPENDENT REVIEW", self.skill)

    def test_pdf_draft_hands_off_format_without_final_visual_gate(self) -> None:
        self.assertIn("use `eric-soft-signal` for the document/PDF surface", self.skill)
        self.assertIn("Use generic `pdf` only for narrow file operations", self.skill)
        self.assertIn("Do not trigger formal visual review for an ordinary classroom draft", self.skill)

    def test_minimum_teaching_contract_and_privacy_are_present(self) -> None:
        for term in (
            "one scoring or performance bottleneck",
            "one observable signal",
            "Fit a runnable sequence",
            "needed to answer each exercise",
            "minimum necessary, authorized learner information",
        ):
            self.assertIn(term, self.skill)

    def test_only_final_or_formal_student_delivery_freezes_identity(self) -> None:
        self.assertIn("formally handed to students, published, or explicitly signed off", self.skill)
        self.assertIn("freeze its identity", self.skill)
        self.assertIn("at most one fresh independent review", self.skill)


if __name__ == "__main__":
    unittest.main()
