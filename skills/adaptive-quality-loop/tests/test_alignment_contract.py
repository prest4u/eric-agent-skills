from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
METADATA = ROOT / "agents" / "openai.yaml"
VALIDATOR = ROOT / "scripts" / "validate_quality_packet.py"
PROMPTS = ROOT / "test-prompts.json"


class OutputFirstContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.metadata = METADATA.read_text(encoding="utf-8")
        cls.validator = VALIDATOR.read_text(encoding="utf-8")

    def test_public_modes_are_build_proof_release(self):
        for mode in ("`BUILD`", "`PROOF`", "`RELEASE`"):
            self.assertIn(mode, self.skill)

    def test_build_is_the_default(self):
        self.assertIn("`BUILD` | Default", self.skill)
        self.assertIn("Default to BUILD", self.skill.split("---", 2)[1])

    def test_visible_artifact_precedes_process(self):
        self.assertIn("Build the requested thing before expanding the process", self.skill)
        self.assertIn("Create or modify the actual artifact", self.skill)

    def test_build_has_one_targeted_check(self):
        build = self.skill.split("## BUILD", 1)[1].split("## PROOF", 1)[0]
        self.assertIn("cheapest check", build)
        self.assertIn("one targeted check", self.skill)

    def test_build_forbids_packet_approval_and_reviewer(self):
        build = self.skill.split("## BUILD", 1)[1].split("## PROOF", 1)[0]
        for phrase in ("Do not create a quality packet", "ask for routine approval", "dispatch a reviewer"):
            self.assertIn(phrase, build)

    def test_proof_is_reversible_and_visible(self):
        proof = self.skill.split("## PROOF", 1)[1].split("## RELEASE", 1)[0]
        self.assertIn("smallest representative result", proof)
        self.assertIn("locally reversible", proof)

    def test_proof_asks_only_for_material_boundary(self):
        proof = self.skill.split("## PROOF", 1)[1].split("## RELEASE", 1)[0]
        for phrase in ("material product choice", "expense", "lock-in", "irreversible action", "external impact"):
            self.assertIn(phrase, proof)

    def test_proof_forbids_packet_and_independent_review(self):
        proof = self.skill.split("## PROOF", 1)[1].split("## RELEASE", 1)[0]
        self.assertIn("Do not create a persistent QA record", proof)
        self.assertIn("independent reviewer", proof)

    def test_release_triggers_are_high_impact(self):
        release = self.skill.split("## RELEASE", 1)[1].split("## Agent budget", 1)[0]
        for phrase in ("publish", "external delivery", "security/privacy", "destructive action", "migration", "deployment"):
            self.assertIn(phrase, self.skill)
        self.assertIn("Confirm current authority", release)

    def test_release_uses_one_independent_review(self):
        release = self.skill.split("## RELEASE", 1)[1].split("## Agent budget", 1)[0]
        self.assertIn("one fresh independent review", release)
        self.assertIn("Stop mutation", release)

    def test_formal_validator_is_release_only(self):
        self.assertIn("only when an explicit formal release record is required", self.skill)
        self.assertIn("FORMAL_RECORD_RELEASE_ONLY", self.validator)

    def test_single_agent_is_default(self):
        budget = self.skill.split("## Agent budget", 1)[1].split("## Failure loop", 1)[0]
        self.assertIn("one main agent by default", budget)
        self.assertIn("at most one child agent", budget)
        self.assertIn("never a full-history fork", budget)

    def test_same_agent_checking_is_ordinary_default(self):
        self.assertIn("Same-agent checking is sufficient outside RELEASE", self.skill)

    def test_failure_loop_has_two_bounded_repairs(self):
        failure = self.skill.split("## Failure loop", 1)[1].split("## Done", 1)[0]
        self.assertIn("one targeted repair", failure)
        self.assertIn("before a second repair", failure)
        self.assertIn("change approach or return the concrete blocker", failure)

    def test_failure_loop_forbids_json_fingerprints(self):
        self.assertIn("Do not encode JSON fingerprints", self.skill)

    def test_legacy_runtime_labels_are_absent(self):
        for phrase in ("ALIGN_DIRECT", "ALIGN_FOCUSED", "ALIGN_DISCOVERY", "Q0", "Q1", "Q2", "Q3"):
            self.assertNotIn(phrase, self.skill)

    def test_metadata_describes_build_first_behavior(self):
        self.assertIn("Build first", self.metadata)
        self.assertIn("BUILD mode", self.metadata)
        self.assertIn("allow_implicit_invocation: true", self.metadata)

    def test_description_excludes_advice_and_status(self):
        frontmatter = self.skill.split("---", 2)[1]
        for phrase in ("ordinary advice", "explanations", "status checks", "inspect-only"):
            self.assertIn(phrase, frontmatter)

    def test_forward_prompts_cover_current_modes_without_legacy_routes(self):
        prompts = json.loads(PROMPTS.read_text(encoding="utf-8"))
        self.assertEqual(len(prompts), 12)
        ids = [item["id"] for item in prompts]
        self.assertTrue(any(value.startswith("BUILD-") for value in ids))
        self.assertTrue(any(value.startswith("PROOF-") for value in ids))
        self.assertTrue(any(value.startswith("RELEASE-") for value in ids))
        rendered = json.dumps(prompts)
        self.assertNotIn("ALIGN_", rendered)
        self.assertNotIn("Q2", rendered)


if __name__ == "__main__":
    unittest.main()
