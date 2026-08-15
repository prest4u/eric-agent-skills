from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class VocabularyOutputFirstContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        cls.agent = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")

    def test_skill_is_standalone_with_optional_integrations(self):
        self.assertIn("includes a standalone Typst starter", self.text)
        self.assertIn("they are never required", self.text)
        self.assertIn("standalone lesson", self.agent)

    def test_build_produces_before_expanding_qa(self):
        self.assertIn("Produce the visible lesson/PDF", self.text)
        self.assertIn("cheapest check that can falsify", self.text)

    def test_draft_does_not_wait_for_independent_review(self):
        self.assertIn("Draft and proof work must not use that flag or wait for an independent reviewer", self.text)

    def test_formal_review_is_release_only_and_single(self):
        review = self.text.split("## Review protocol", 1)[1].split("Known release blockers", 1)[0]
        self.assertIn("explicit RELEASE or formal visual sign-off", review)
        self.assertIn("at most one independent reviewer", review)


if __name__ == "__main__":
    unittest.main()
