from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
METADATA = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
PROMPTS = ROOT / "test-prompts.json"


class EricReviewContractTests(unittest.TestCase):
    def test_review_is_explicit_only(self):
        self.assertIn("Use only when Eric explicitly asks", SKILL.split("---", 2)[1])
        self.assertIn("allow_implicit_invocation: false", METADATA)

    def test_three_modes_are_public(self):
        for mode in ("QUICK_REVIEW", "REVIEW_AND_FIX", "FORMAL_SIGNOFF"):
            self.assertIn(mode, SKILL)

    def test_quick_review_is_default(self):
        self.assertIn("Default for check, critique, or review", SKILL)

    def test_review_requires_an_existing_artifact(self):
        self.assertIn("If no inspectable artifact exists", SKILL)
        self.assertIn("Do not review a plan as a substitute", SKILL)

    def test_quick_review_is_concise(self):
        quick = SKILL.split("## QUICK_REVIEW", 1)[1].split("## REVIEW_AND_FIX", 1)[0]
        self.assertIn("concise verdict", quick)
        self.assertIn("blocking findings", quick)
        self.assertIn("what was not checked", quick)

    def test_quick_review_has_no_formal_ceremony(self):
        quick = SKILL.split("## QUICK_REVIEW", 1)[1].split("## REVIEW_AND_FIX", 1)[0]
        for phrase in ("preflight form", "artifact-by-lens matrix", "seven-section report", "persistent packet"):
            self.assertIn(phrase, quick)

    def test_review_and_fix_allows_same_agent(self):
        repair = SKILL.split("## REVIEW_AND_FIX", 1)[1].split("## FORMAL_SIGNOFF", 1)[0]
        self.assertIn("same agent", SKILL)
        self.assertIn("one targeted recheck", repair)

    def test_review_and_fix_does_not_pause_normally(self):
        repair = SKILL.split("## REVIEW_AND_FIX", 1)[1].split("## FORMAL_SIGNOFF", 1)[0]
        self.assertIn("Do not pause between audit and repair", repair)

    def test_formal_signoff_freezes_identity(self):
        formal = SKILL.split("## FORMAL_SIGNOFF", 1)[1].split("## Verdicts", 1)[0]
        self.assertIn("Freeze the exact artifact", formal)
        self.assertIn("independent reviewer", formal)

    def test_producer_cannot_self_sign(self):
        self.assertIn("producer cannot grant formal READY", SKILL)

    def test_formal_signoff_is_not_publish_authority(self):
        formal = SKILL.split("## FORMAL_SIGNOFF", 1)[1].split("## Verdicts", 1)[0]
        for action in ("publish", "deploy", "send", "upload", "migration", "destructive action"):
            self.assertIn(action, formal)

    def test_open_p0_p1_blocks_formal_signoff(self):
        self.assertIn("Block on open P0/P1", SKILL)

    def test_missing_mandatory_evidence_has_specific_verdict(self):
        self.assertIn("INSUFFICIENT EVIDENCE", SKILL)

    def test_no_review_of_review_chain(self):
        self.assertIn("never create a review-of-review chain", SKILL)

    def test_metadata_defaults_to_quick_review(self):
        self.assertIn("QUICK_REVIEW mode", METADATA)

    def test_forward_prompts_use_only_current_review_modes(self):
        prompts = json.loads(PROMPTS.read_text(encoding="utf-8"))
        self.assertEqual(len(prompts), 6)
        rendered = json.dumps(prompts)
        self.assertNotIn("AUDIT_THEN_REPAIR", rendered)
        self.assertNotIn("AUDIT_ONLY", rendered)

    def test_references_do_not_restore_archived_control_plane(self):
        references = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted((ROOT / "references").glob("*.md"))
        )
        self.assertNotIn("eric-visual-delivery-review", references)
        self.assertNotIn("Artifact × Lens Plan", references)
        self.assertNotIn("Handoff Packet", references)

    def test_router_keeps_ordinary_review_single_pass(self):
        router = (ROOT / "references" / "review-router.md").read_text(encoding="utf-8")
        self.assertIn("QUICK_REVIEW normally uses one lens", router)
        self.assertIn("REVIEW_AND_FIX uses the same agent and one recheck", router)

    def test_router_does_not_implicitly_invoke_eric_research(self):
        router = (ROOT / "references" / "review-router.md").read_text(encoding="utf-8")
        self.assertIn("use `$eric-research` only when Eric separately invokes it", router)


if __name__ == "__main__":
    unittest.main()
