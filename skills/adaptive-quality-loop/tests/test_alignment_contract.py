from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class OptionalReferenceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        cls.metadata = (ROOT / "agents/openai.yaml").read_text(encoding="utf-8")

    def test_entry_is_explicit_and_host_controls_workflow(self):
        self.assertIn("Use only when Eric explicitly requests", self.skill)
        self.assertIn("allow_implicit_invocation: false", self.metadata)
        self.assertIn("Host and task policy governs", self.skill)

    def test_methods_do_not_become_required_stages(self):
        self.assertIn("Do not classify every task", self.skill)
        self.assertIn("They are not mandatory task stages", self.skill)
        self.assertNotIn("## Choose one mode", self.skill)

    def test_formal_record_api_remains_optional(self):
        self.assertIn("only when an explicit formal release record is required", self.skill)
        self.assertIn("schema_version: 1", self.skill)
        validator = (ROOT / "scripts/validate_quality_packet.py").read_text(encoding="utf-8")
        self.assertIn("FORMAL_RECORD_RELEASE_ONLY", validator)

    def test_missing_review_does_not_authorize_release(self):
        self.assertIn("Missing review is never approval", self.skill)
        self.assertIn("keeping dependent release or high-impact actions blocked", self.skill)

    def test_optional_polish_does_not_reopen_completion(self):
        self.assertIn("Optional polish does not create another round", self.skill)
        self.assertIn("smallest sufficient evidence set", self.skill)

    def test_legacy_record_labels_are_not_runtime_modes(self):
        for label in ("`BUILD`", "`PROOF`", "`RELEASE`"):
            self.assertIn(label, self.skill.split("## Compatibility", 1)[1])
        for old in ("ALIGN_DIRECT", "ALIGN_FOCUSED", "ALIGN_DISCOVERY", "Q0", "Q1", "Q2", "Q3"):
            self.assertNotIn(old, self.skill)

    def test_existing_forward_fixture_ids_remain_available(self):
        cases = json.loads((ROOT / "test-prompts.json").read_text(encoding="utf-8"))
        self.assertEqual(12, len(cases))
        self.assertEqual(12, len({case["id"] for case in cases}))
        self.assertTrue(any("$adaptive-quality-loop" in case["prompt"] for case in cases))
        for case in cases:
            if "$adaptive-quality-loop" not in case["prompt"]:
                self.assertIn("automatically invoke adaptive-quality-loop", case["fail_if"])


if __name__ == "__main__":
    unittest.main()
