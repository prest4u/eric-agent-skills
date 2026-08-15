import json
import unittest
from pathlib import Path

import yaml


SKILL_DIR = Path(__file__).resolve().parents[1]


class PromptRouteContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = json.loads((SKILL_DIR / "tests" / "test-prompts.json").read_text(encoding="utf-8"))
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        _, frontmatter, cls.body = skill_text.split("---", 2)
        cls.metadata = yaml.safe_load(frontmatter)
        cls.openai = yaml.safe_load((SKILL_DIR / "agents" / "openai.yaml").read_text(encoding="utf-8"))

    def test_prompt_matrix_has_current_routes(self):
        self.assertEqual(8, len(self.cases))
        self.assertEqual(8, len({case["id"] for case in self.cases}))
        self.assertEqual(
            {"production_create", "prototype", "repair", "review_and_fix", "release", "out_of_scope"},
            {case["expected_route"] for case in self.cases},
        )

    def test_every_case_has_portable_route_metadata(self):
        fields = {"id", "prompt", "expected_route", "invocation", "expected_owner"}
        for case in self.cases:
            self.assertEqual(fields, set(case))
            self.assertIn(case["invocation"], {"implicit", "explicit"})

    def test_implicit_build_routes_and_negative_boundaries(self):
        owned = {
            case["id"]
            for case in self.cases
            if case["invocation"] == "implicit" and case["expected_owner"] == "eric-frontend-delivery"
        }
        self.assertEqual(
            {"react-dashboard-final", "static-html-prototype", "repair-mobile-state"}, owned
        )
        rejected = {
            case["id"]
            for case in self.cases
            if case["invocation"] == "implicit" and case["expected_owner"] == "other"
        }
        self.assertEqual(
            {"backend-only", "content-only-release-notes", "unrendered-data-analysis"}, rejected
        )

    def test_explicit_review_and_release_keep_authority_separate(self):
        by_id = {case["id"]: case for case in self.cases}
        self.assertEqual(
            "eric-review+eric-frontend-delivery",
            by_id["explicit-review-and-fix"]["expected_owner"],
        )
        self.assertIn("Keep sign-off separate from deploy", self.body)
        self.assertIn("at most one independent `$eric-review`", self.body)

    def test_description_supports_implicit_creation_without_audit_claims(self):
        description = self.metadata["description"].lower()
        self.assertTrue(self.openai["policy"]["allow_implicit_invocation"])
        for phrase in ("create", "prototype", "repair"):
            self.assertIn(phrase, description)
        for forbidden in ("audit", "auditing", "score"):
            self.assertNotIn(forbidden, description)


if __name__ == "__main__":
    unittest.main()
