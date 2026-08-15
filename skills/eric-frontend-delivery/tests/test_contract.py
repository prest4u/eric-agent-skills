import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")


class FrontendOutputFirstContractTests(unittest.TestCase):
    def test_three_modes_match_global_quality_timing(self):
        for mode in ("BUILD", "PROOF", "RELEASE"):
            self.assertIn(f"## {mode}", SKILL)
        for old in ("CREATE_EDIT", "AUDIT_ONLY", "FINAL_REVIEW", "RECHECK"):
            self.assertNotIn(old, SKILL)

    def test_build_produces_working_surface_and_one_check(self):
        build = SKILL.split("## BUILD", 1)[1].split("## PROOF", 1)[0]
        self.assertIn("Build or repair the visible primary flow first", build)
        self.assertIn("Run one combined check", build)
        self.assertIn("same agent may fix ordinary findings", build)

    def test_no_parallel_control_plane_or_scoring(self):
        self.assertIn("Do not create a second maturity, writer/reviewer, scoring, or verdict control plane", SKILL)
        self.assertNotIn("coverage matrix", SKILL)
        self.assertNotRegex(SKILL, r"dimensions? `?0`?–`?4`?")

    def test_proof_has_no_reviewer(self):
        proof = SKILL.split("## PROOF", 1)[1].split("## RELEASE", 1)[0]
        self.assertIn("A proof needs no independent reviewer", proof)

    def test_release_review_is_single_and_separate_from_deploy(self):
        release = SKILL.split("## RELEASE", 1)[1].split("## Runtime evidence", 1)[0]
        self.assertIn("at most one independent `$eric-review`", release)
        self.assertIn("Keep sign-off separate from deploy", release)

    def test_main_agent_is_default(self):
        self.assertIn("Use the main agent by default", SKILL)
        self.assertIn("At most one child agent", SKILL)
        self.assertIn("ordinary visual inspection never requires one", SKILL)

    def test_references_resolve(self):
        for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", SKILL):
            self.assertTrue((ROOT / target).is_file(), target)

    def test_prompts_cover_output_first_routes(self):
        prompts = json.loads((ROOT / "tests" / "test-prompts.json").read_text(encoding="utf-8"))
        self.assertEqual(len(prompts), 8)
        rendered = json.dumps(prompts)
        self.assertNotIn("CREATE_EDIT", rendered)
        self.assertNotIn("FINAL_REVIEW", rendered)


if __name__ == "__main__":
    unittest.main()
