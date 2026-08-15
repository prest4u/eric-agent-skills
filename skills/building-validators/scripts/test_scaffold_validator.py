#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCAFFOLD = SKILL_DIR / "scripts" / "scaffold_validator.py"
BUNDLE_CHECK = SKILL_DIR / "scripts" / "validate_validator_bundle.py"


class ScaffoldValidatorTests(unittest.TestCase):
    def run_py(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=cwd,
            text=True,
            capture_output=True,
        )

    def scaffold_bundle(self, root: Path, domain: str = "generic") -> Path:
        result = self.run_py(str(SCAFFOLD), str(root), "--domain", domain)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        return root / "qa" / "validator"

    def run_generated_validator(
        self, validator_dir: Path, root: Path, rules_path: Path
    ) -> subprocess.CompletedProcess[str]:
        return self.run_py(
            str(validator_dir / "validate_project.py"),
            "--root",
            str(root),
            "--rules",
            str(rules_path),
            "--no-write",
            "--json",
        )

    def test_skill_description_contains_chinese_trigger_words(self) -> None:
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        description_line = next(line for line in skill_text.splitlines() if line.startswith("description:"))
        for token in ["Validator", "验证", "验收", "门禁", "QA"]:
            self.assertIn(token, description_line)
        self.assertNotIn("/Users/", skill_text)

    def test_scaffold_generates_self_testing_validator_bundle(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            root = Path(tmp)
            validator_dir = self.scaffold_bundle(root, "teaching")
            validate_script = validator_dir / "validate_project.py"
            rules = validator_dir / "validator_rules.json"
            generated_test = validator_dir / "tests" / "test_validate_project.py"

            self.assertTrue(validate_script.exists())
            self.assertTrue(rules.exists())
            self.assertTrue(generated_test.exists())

            self_test = self.run_py(str(validate_script), "--self-test")
            self.assertEqual(self_test.returncode, 0, self_test.stderr + self_test.stdout)

            bundle = self.run_py(str(BUNDLE_CHECK), str(validator_dir), "--json")
            self.assertEqual(bundle.returncode, 0, bundle.stderr + bundle.stdout)
            payload = json.loads(bundle.stdout)
            self.assertEqual(payload["status"], "pass")

    def test_scaffold_rejects_out_dir_escape(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            base = Path(tmp)
            project = base / "project"
            absolute_outside = base / "outside-absolute"
            result = self.run_py(
                str(SCAFFOLD),
                str(project),
                "--out-dir",
                str(absolute_outside),
            )
            self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
            self.assertFalse((absolute_outside / "validate_project.py").exists())

            parent_outside = base / "outside-parent"
            result = self.run_py(
                str(SCAFFOLD),
                str(project),
                "--out-dir",
                "../outside-parent",
            )
            self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
            self.assertFalse((parent_outside / "validate_project.py").exists())

    def test_generated_validator_blocks_contract_and_public_leaks(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            root = Path(tmp)
            validator_dir = self.scaffold_bundle(root)
            rules_path = validator_dir / "validator_rules.json"
            rules = json.loads(rules_path.read_text(encoding="utf-8"))
            rules["required_paths"] = [
                {"path": "public.md", "min_bytes": 20, "severity": "P0"}
            ]
            rules["public_globs"] = ["public.md"]
            rules["forbidden_public_terms"] = [
                {"term": "INTERNAL_ONLY", "severity": "P0", "reason": "internal marker leak"}
            ]
            rules_path.write_text(json.dumps(rules, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            (root / "public.md").write_text("Visible handoff with INTERNAL_ONLY marker.\n", encoding="utf-8")

            result = self.run_generated_validator(validator_dir, root, rules_path)
            self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "fail")
            codes = {issue["code"] for issue in payload["issues"]}
            self.assertIn("PUBLIC_FORBIDDEN_TERM", codes)

    def test_generated_validator_blocks_forbidden_terms_case_insensitively(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            root = Path(tmp)
            validator_dir = self.scaffold_bundle(root)
            rules_path = validator_dir / "validator_rules.json"
            rules = json.loads(rules_path.read_text(encoding="utf-8"))
            rules["public_globs"] = ["public.md"]
            rules["forbidden_public_terms"] = [
                {"term": "INTERNAL_ONLY", "severity": "P0", "reason": "internal marker leak"}
            ]
            rules_path.write_text(json.dumps(rules, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            (root / "public.md").write_text("Visible handoff with internal_only marker.\n", encoding="utf-8")

            result = self.run_generated_validator(validator_dir, root, rules_path)
            self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
            payload = json.loads(result.stdout)
            codes = {issue["code"] for issue in payload["issues"]}
            self.assertIn("PUBLIC_FORBIDDEN_TERM", codes)

    def test_generated_validator_forces_p0_p1_strict_failures(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            root = Path(tmp)
            validator_dir = self.scaffold_bundle(root)
            rules_path = validator_dir / "validator_rules.json"
            rules = json.loads(rules_path.read_text(encoding="utf-8"))
            rules["strict_fail_severities"] = []
            rules["required_paths"] = [{"path": "missing.md", "min_bytes": 1, "severity": "P0"}]
            rules_path.write_text(json.dumps(rules, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            result = self.run_generated_validator(validator_dir, root, rules_path)
            self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "fail")
            self.assertIn("P0", payload["summary"]["strict_fail_severities"])
            self.assertIn("P1", payload["summary"]["strict_fail_severities"])

    def test_generated_validator_rejects_malformed_forbidden_terms(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            root = Path(tmp)
            validator_dir = self.scaffold_bundle(root)
            rules_path = validator_dir / "validator_rules.json"
            rules = json.loads(rules_path.read_text(encoding="utf-8"))
            rules["public_globs"] = ["public.md"]
            rules["forbidden_public_terms"] = ["INTERNAL_ONLY"]
            rules_path.write_text(json.dumps(rules, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            (root / "public.md").write_text("Visible handoff with INTERNAL_ONLY marker.\n", encoding="utf-8")

            result = self.run_generated_validator(validator_dir, root, rules_path)
            self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
            payload = json.loads(result.stdout)
            codes = {issue["code"] for issue in payload["issues"]}
            self.assertIn("RULE_INVALID", codes)

    def test_generated_validator_reports_next_action_and_respects_no_write(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            root = Path(tmp)
            validator_dir = self.scaffold_bundle(root)
            rules_path = validator_dir / "validator_rules.json"
            result = self.run_generated_validator(validator_dir, root, rules_path)
            self.assertIn(result.returncode, {0, 1}, result.stderr + result.stdout)
            payload = json.loads(result.stdout)
            self.assertIn("next_action", payload)
            self.assertIsInstance(payload["next_action"], str)
            self.assertGreater(len(payload["next_action"]), 10)
            self.assertFalse((validator_dir / "reports" / "validator_report.json").exists())

    def test_generated_validator_rejects_report_dir_outside_root_when_writing(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            root = Path(tmp)
            validator_dir = self.scaffold_bundle(root)
            outside = root.parent / "outside-reports"
            result = self.run_py(
                str(validator_dir / "validate_project.py"),
                "--root",
                str(root),
                "--rules",
                str(validator_dir / "validator_rules.json"),
                "--report-dir",
                "../outside-reports",
            )
            self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
            self.assertIn("--report-dir must stay under --root", result.stderr)
            self.assertFalse((outside / "validator_report.json").exists())

    def test_generated_validator_expands_brace_globs(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            root = Path(tmp)
            validator_dir = self.scaffold_bundle(root, "webapp")
            (root / "src").mkdir()
            (root / "src" / "app.ts").write_text("const leak = 'INTERNAL_ONLY';\n", encoding="utf-8")

            result = self.run_generated_validator(validator_dir, root, validator_dir / "validator_rules.json")
            self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
            payload = json.loads(result.stdout)
            codes = {issue["code"] for issue in payload["issues"]}
            self.assertIn("PUBLIC_FORBIDDEN_TERM", codes)

    def test_generated_validator_rejects_rule_paths_outside_root(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            base = Path(tmp)
            root = base / "project"
            root.mkdir()
            validator_dir = self.scaffold_bundle(root)
            rules_path = validator_dir / "validator_rules.json"
            (base / "outside.md").write_text("large enough external file\n", encoding="utf-8")
            (base / "outside_review.md").write_text("FINAL_VISUAL_REVIEW: PASS\n", encoding="utf-8")
            rules = json.loads(rules_path.read_text(encoding="utf-8"))
            rules["required_paths"] = [{"path": "../outside.md", "min_bytes": 1, "severity": "P0"}]
            rules["manual_review_sentinels"] = [
                {"path": "../outside_review.md", "sentinel": "FINAL_VISUAL_REVIEW: PASS", "severity": "P0"}
            ]
            rules_path.write_text(json.dumps(rules, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            result = self.run_generated_validator(validator_dir, root, rules_path)
            self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
            payload = json.loads(result.stdout)
            codes = {issue["code"] for issue in payload["issues"]}
            self.assertIn("RULE_PATH_OUTSIDE_ROOT", codes)

    def test_generated_validator_rejects_parent_public_glob(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            base = Path(tmp)
            root = base / "project"
            root.mkdir()
            validator_dir = self.scaffold_bundle(root)
            rules_path = validator_dir / "validator_rules.json"
            (base / "outside.md").write_text("INTERNAL_ONLY\n", encoding="utf-8")
            rules = json.loads(rules_path.read_text(encoding="utf-8"))
            rules["public_globs"] = ["../*.md"]
            rules["forbidden_public_terms"] = [
                {"term": "INTERNAL_ONLY", "severity": "P0", "reason": "external file must not be scanned"}
            ]
            rules_path.write_text(json.dumps(rules, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            result = self.run_generated_validator(validator_dir, root, rules_path)
            self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
            payload = json.loads(result.stdout)
            codes = {issue["code"] for issue in payload["issues"]}
            self.assertIn("RULE_PATH_OUTSIDE_ROOT", codes)

    def test_generated_validator_rejects_globbed_symlink(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            base = Path(tmp)
            root = base / "project"
            root.mkdir()
            validator_dir = self.scaffold_bundle(root)
            rules_path = validator_dir / "validator_rules.json"
            outside = base / "outside.md"
            outside.write_text("INTERNAL_ONLY\n", encoding="utf-8")
            (root / "linked.md").symlink_to(outside)
            rules = json.loads(rules_path.read_text(encoding="utf-8"))
            rules["public_globs"] = ["*.md"]
            rules["forbidden_public_terms"] = [
                {"term": "INTERNAL_ONLY", "severity": "P0", "reason": "external symlink must not be scanned"}
            ]
            rules_path.write_text(json.dumps(rules, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            result = self.run_generated_validator(validator_dir, root, rules_path)
            self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
            payload = json.loads(result.stdout)
            codes = {issue["code"] for issue in payload["issues"]}
            self.assertTrue({"RULE_PATH_SYMLINK", "RULE_PATH_OUTSIDE_ROOT"} & codes)

    def test_generated_validator_rejects_files_reached_through_symlinked_directory(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            base = Path(tmp)
            root = base / "project"
            root.mkdir()
            validator_dir = self.scaffold_bundle(root)
            rules_path = validator_dir / "validator_rules.json"
            outside_dir = base / "outside"
            outside_dir.mkdir()
            (outside_dir / "leak.md").write_text("INTERNAL_ONLY\n", encoding="utf-8")
            (root / "linked_dir").symlink_to(outside_dir, target_is_directory=True)
            rules = json.loads(rules_path.read_text(encoding="utf-8"))
            rules["public_globs"] = ["linked_dir/*.md"]
            rules["forbidden_public_terms"] = [
                {"term": "INTERNAL_ONLY", "severity": "P0", "reason": "external symlink directory must not be scanned"}
            ]
            rules_path.write_text(json.dumps(rules, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            result = self.run_generated_validator(validator_dir, root, rules_path)
            self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
            payload = json.loads(result.stdout)
            codes = {issue["code"] for issue in payload["issues"]}
            self.assertTrue({"RULE_PATH_SYMLINK", "RULE_PATH_OUTSIDE_ROOT"} & codes)

    def test_generated_validator_rejects_symlinks_that_resolve_inside_root(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            root = Path(tmp)
            validator_dir = self.scaffold_bundle(root)
            target = root / "actual.md"
            target.write_text("clean file\n", encoding="utf-8")
            (root / "alias.md").symlink_to(target)
            rules = {
                "strict_fail_severities": ["P0", "P1"],
                "required_paths": [{"path": "alias.md", "min_bytes": 1, "severity": "P0"}],
                "public_globs": ["alias.md"],
                "forbidden_public_terms": [],
            }
            rules_path = root / "rules.json"
            rules_path.write_text(json.dumps(rules, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            result = self.run_generated_validator(validator_dir, root, rules_path)
            self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
            payload = json.loads(result.stdout)
            codes = {issue["code"] for issue in payload["issues"]}
            self.assertIn("RULE_PATH_SYMLINK", codes)

    def test_generated_validator_rejects_wildcard_symlink_directory_that_resolves_inside_root(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            root = Path(tmp)
            validator_dir = self.scaffold_bundle(root)
            actual_dir = root / "actual"
            actual_dir.mkdir()
            (actual_dir / "public.md").write_text("clean file\n", encoding="utf-8")
            (root / "alias").symlink_to(actual_dir, target_is_directory=True)
            rules = {
                "schema_version": 1,
                "strict_fail_severities": ["P0", "P1"],
                "required_paths": [],
                "expected_counts": [],
                "json_files": [],
                "public_globs": ["*/public.md"],
                "forbidden_public_terms": [],
                "regex_rules": [],
                "manual_review_sentinels": [],
            }
            rules_path = root / "rules.json"
            rules_path.write_text(json.dumps(rules, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            result = self.run_generated_validator(validator_dir, root, rules_path)
            self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
            payload = json.loads(result.stdout)
            codes = {issue["code"] for issue in payload["issues"]}
            self.assertIn("RULE_PATH_SYMLINK", codes)

    def test_generated_validator_rejects_public_globs_not_list(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            root = Path(tmp)
            validator_dir = self.scaffold_bundle(root)
            rules = {
                "schema_version": 1,
                "strict_fail_severities": ["P0", "P1"],
                "required_paths": [],
                "expected_counts": [],
                "json_files": [],
                "public_globs": "*.md",
                "forbidden_public_terms": [],
                "regex_rules": [],
                "manual_review_sentinels": [],
            }
            rules_path = root / "rules.json"
            rules_path.write_text(json.dumps(rules, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            result = self.run_generated_validator(validator_dir, root, rules_path)
            self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
            payload = json.loads(result.stdout)
            codes = {issue["code"] for issue in payload["issues"]}
            self.assertIn("RULE_INVALID", codes)

    def test_generated_validator_missing_root_is_structured_and_no_write(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            root = Path(tmp)
            validator_dir = self.scaffold_bundle(root)
            missing_root = root / "missing-root"
            result = self.run_py(
                str(validator_dir / "validate_project.py"),
                "--root",
                str(missing_root),
                "--rules",
                str(validator_dir / "validator_rules.json"),
                "--json",
            )
            self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
            payload = json.loads(result.stdout)
            codes = {issue["code"] for issue in payload["issues"]}
            self.assertIn("PROJECT_ROOT_MISSING", codes)
            self.assertFalse(missing_root.exists())

    def test_generated_validator_reports_malformed_rules_as_findings(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            root = Path(tmp)
            validator_dir = self.scaffold_bundle(root)
            cases = [
                {"required_paths": [{"path": "public.md", "min_bytes": "large", "severity": "P0"}]},
                {"expected_counts": [{"glob": "*.md", "count": "two", "severity": "P0"}]},
                {"regex_rules": [{"globs": ["*.md"], "regex": "[", "severity": "P0"}]},
            ]
            for index, rules_delta in enumerate(cases):
                with self.subTest(index=index):
                    rules_path = root / f"rules-{index}.json"
                    rules = {
                        "schema_version": 1,
                        "strict_fail_severities": ["P0", "P1"],
                        "required_paths": [],
                        "expected_counts": [],
                        "json_files": [],
                        "public_globs": [],
                        "forbidden_public_terms": [],
                        "regex_rules": [],
                        "manual_review_sentinels": [],
                    }
                    rules.update(rules_delta)
                    rules_path.write_text(json.dumps(rules, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                    result = self.run_generated_validator(validator_dir, root, rules_path)
                    self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
                    payload = json.loads(result.stdout)
                    codes = {issue["code"] for issue in payload["issues"]}
                    self.assertIn("RULE_INVALID", codes)

    def test_generated_validator_reports_non_object_rules_as_json_contract(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            root = Path(tmp)
            validator_dir = self.scaffold_bundle(root)
            rules_path = root / "rules.json"
            rules_path.write_text("[]\n", encoding="utf-8")
            result = self.run_generated_validator(validator_dir, root, rules_path)
            self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "fail")
            codes = {issue["code"] for issue in payload["issues"]}
            self.assertIn("RULES_NOT_OBJECT", codes)

    def test_generated_validator_rejects_regex_globs_not_list(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            root = Path(tmp)
            validator_dir = self.scaffold_bundle(root)
            rules = {
                "strict_fail_severities": ["P0", "P1"],
                "required_paths": [],
                "expected_counts": [],
                "json_files": [],
                "public_globs": [],
                "forbidden_public_terms": [],
                "regex_rules": [{"globs": "public.md", "regex": "INTERNAL", "severity": "P0"}],
                "manual_review_sentinels": [],
            }
            rules_path = root / "rules.json"
            rules_path.write_text(json.dumps(rules, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            result = self.run_generated_validator(validator_dir, root, rules_path)
            self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
            payload = json.loads(result.stdout)
            codes = {issue["code"] for issue in payload["issues"]}
            self.assertIn("RULE_INVALID", codes)

    def test_bundle_validator_runs_generated_test_files(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            root = Path(tmp)
            validator_dir = self.scaffold_bundle(root)
            broken_test = validator_dir / "tests" / "test_validate_project.py"
            broken_test.write_text(
                "import unittest\n\n"
                "class BrokenTests(unittest.TestCase):\n"
                "    def test_breaks(self):\n"
                "        self.fail('bundle validator must run generated tests')\n\n"
                "if __name__ == '__main__':\n"
                "    unittest.main()\n",
                encoding="utf-8",
            )

            bundle = self.run_py(str(BUNDLE_CHECK), str(validator_dir), "--json")
            self.assertEqual(bundle.returncode, 1, bundle.stderr + bundle.stdout)
            payload = json.loads(bundle.stdout)
            codes = {finding["code"] for finding in payload["findings"]}
            self.assertIn("TEST_COMMAND_FAILED", codes)

    def test_bundle_validator_static_only_does_not_execute_candidate_tests(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            root = Path(tmp)
            validator_dir = self.scaffold_bundle(root)
            broken_test = validator_dir / "tests" / "test_validate_project.py"
            broken_test.write_text("raise SystemExit('must not execute in static-only mode')\n", encoding="utf-8")

            bundle = self.run_py(str(BUNDLE_CHECK), str(validator_dir), "--static-only", "--json")
            self.assertEqual(bundle.returncode, 0, bundle.stderr + bundle.stdout)
            payload = json.loads(bundle.stdout)
            codes = {finding["code"] for finding in payload["findings"]}
            self.assertNotIn("TEST_COMMAND_FAILED", codes)

    def test_bundle_validator_checks_report_contract(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            root = Path(tmp)
            validator_dir = self.scaffold_bundle(root)
            script = validator_dir / "validate_project.py"
            script.write_text(
                script.read_text(encoding="utf-8").replace(
                    '        "next_action": next_action_for(summary["status"]),\n',
                    "",
                ),
                encoding="utf-8",
            )

            bundle = self.run_py(str(BUNDLE_CHECK), str(validator_dir), "--json")
            self.assertEqual(bundle.returncode, 1, bundle.stderr + bundle.stdout)
            payload = json.loads(bundle.stdout)
            codes = {finding["code"] for finding in payload["findings"]}
            self.assertIn("REPORT_CONTRACT_MISSING_FIELD", codes)

    def test_bundle_validator_rejects_packaging_artifacts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            root = Path(tmp)
            validator_dir = self.scaffold_bundle(root)
            cache_dir = validator_dir / "__pycache__"
            cache_dir.mkdir()
            (cache_dir / "validate_project.cpython-312.pyc").write_bytes(b"bytecode")

            bundle = self.run_py(str(BUNDLE_CHECK), str(validator_dir), "--static-only", "--json")
            self.assertEqual(bundle.returncode, 1, bundle.stderr + bundle.stdout)
            payload = json.loads(bundle.stdout)
            codes = {finding["code"] for finding in payload["findings"]}
            self.assertIn("PACKAGE_ARTIFACT_FOUND", codes)

    def test_bundle_validator_rejects_no_write_side_effects(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            root = Path(tmp)
            validator_dir = self.scaffold_bundle(root)
            script = validator_dir / "validate_project.py"
            script.write_text(
                script.read_text(encoding="utf-8").replace(
                    "    payload = validate(root, rules)\n",
                    "    (root / 'side_effect.txt').write_text('oops', encoding='utf-8')\n"
                    "    payload = validate(root, rules)\n",
                ),
                encoding="utf-8",
            )

            bundle = self.run_py(str(BUNDLE_CHECK), str(validator_dir), "--json")
            self.assertEqual(bundle.returncode, 1, bundle.stderr + bundle.stdout)
            payload = json.loads(bundle.stdout)
            codes = {finding["code"] for finding in payload["findings"]}
            self.assertIn("NO_WRITE_CONTRACT_VIOLATED", codes)

    def test_bundle_validator_rejects_no_write_side_effects_in_validator_dir(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            root = Path(tmp)
            validator_dir = self.scaffold_bundle(root)
            script = validator_dir / "validate_project.py"
            script.write_text(
                script.read_text(encoding="utf-8").replace(
                    "    payload = validate(root, rules)\n",
                    "    (Path.cwd() / 'reports').mkdir(exist_ok=True)\n"
                    "    (Path.cwd() / 'reports' / 'no_write_leak.txt').write_text('oops', encoding='utf-8')\n"
                    "    payload = validate(root, rules)\n",
                ),
                encoding="utf-8",
            )

            bundle = self.run_py(str(BUNDLE_CHECK), str(validator_dir), "--json")
            self.assertEqual(bundle.returncode, 1, bundle.stderr + bundle.stdout)
            payload = json.loads(bundle.stdout)
            codes = {finding["code"] for finding in payload["findings"]}
            self.assertIn("NO_WRITE_CONTRACT_VIOLATED", codes)

    def test_bundle_validator_rejects_no_write_side_effects_in_project_root(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            root = Path(tmp)
            validator_dir = self.scaffold_bundle(root)
            script = validator_dir / "validate_project.py"
            script.write_text(
                script.read_text(encoding="utf-8").replace(
                    "    payload = validate(root, rules)\n",
                    "    (Path.cwd().parent.parent / 'no_write_project_leak.txt').write_text('oops', encoding='utf-8')\n"
                    "    payload = validate(root, rules)\n",
                ),
                encoding="utf-8",
            )

            bundle = self.run_py(str(BUNDLE_CHECK), str(validator_dir), "--json")
            self.assertEqual(bundle.returncode, 1, bundle.stderr + bundle.stdout)
            payload = json.loads(bundle.stdout)
            codes = {finding["code"] for finding in payload["findings"]}
            self.assertIn("NO_WRITE_CONTRACT_VIOLATED", codes)

    def test_bundle_validator_rejects_no_write_same_size_same_mtime_mutation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            root = Path(tmp)
            validator_dir = self.scaffold_bundle(root)
            watched = root / "watched.txt"
            watched.write_text("alpha\n", encoding="utf-8")
            original_stat = watched.stat()
            script = validator_dir / "validate_project.py"
            script.write_text(
                script.read_text(encoding="utf-8").replace(
                    "    payload = validate(root, rules)\n",
                    "    watched = Path.cwd().parent.parent / 'watched.txt'\n"
                    "    watched.write_text('bravo\\n', encoding='utf-8')\n"
                    f"    os.utime(watched, ns=({original_stat.st_atime_ns}, {original_stat.st_mtime_ns}))\n"
                    "    payload = validate(root, rules)\n",
                ),
                encoding="utf-8",
            )

            bundle = self.run_py(str(BUNDLE_CHECK), str(validator_dir), "--json")
            self.assertEqual(bundle.returncode, 1, bundle.stderr + bundle.stdout)
            payload = json.loads(bundle.stdout)
            codes = {finding["code"] for finding in payload["findings"]}
            self.assertIn("NO_WRITE_CONTRACT_VIOLATED", codes)

    def test_bundle_validator_rejects_no_write_restore_content_ctime_mutation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            root = Path(tmp)
            validator_dir = self.scaffold_bundle(root)
            watched = root / "watched.txt"
            watched.write_text("alpha\n", encoding="utf-8")
            original_stat = watched.stat()
            original_mode = original_stat.st_mode & 0o777
            script = validator_dir / "validate_project.py"
            script.write_text(
                script.read_text(encoding="utf-8").replace(
                    "    payload = validate(root, rules)\n",
                    "    watched = Path.cwd().parent.parent / 'watched.txt'\n"
                    "    watched.write_text('bravo\\n', encoding='utf-8')\n"
                    "    watched.write_text('alpha\\n', encoding='utf-8')\n"
                    f"    watched.chmod({original_mode})\n"
                    f"    os.utime(watched, ns=({original_stat.st_atime_ns}, {original_stat.st_mtime_ns}))\n"
                    "    payload = validate(root, rules)\n",
                ),
                encoding="utf-8",
            )

            bundle = self.run_py(str(BUNDLE_CHECK), str(validator_dir), "--json")
            self.assertEqual(bundle.returncode, 1, bundle.stderr + bundle.stdout)
            payload = json.loads(bundle.stdout)
            codes = {finding["code"] for finding in payload["findings"]}
            self.assertIn("NO_WRITE_CONTRACT_VIOLATED", codes)

    def test_bundle_validator_rejects_no_write_permission_mutation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            root = Path(tmp)
            validator_dir = self.scaffold_bundle(root)
            watched = root / "watched.txt"
            watched.write_text("alpha\n", encoding="utf-8")
            original_mode = watched.stat().st_mode & 0o777
            changed_mode = 0o600 if original_mode != 0o600 else 0o644
            script = validator_dir / "validate_project.py"
            script.write_text(
                script.read_text(encoding="utf-8").replace(
                    "    payload = validate(root, rules)\n",
                    "    watched = Path.cwd().parent.parent / 'watched.txt'\n"
                    f"    watched.chmod({changed_mode})\n"
                    "    payload = validate(root, rules)\n",
                ),
                encoding="utf-8",
            )

            bundle = self.run_py(str(BUNDLE_CHECK), str(validator_dir), "--json")
            self.assertEqual(bundle.returncode, 1, bundle.stderr + bundle.stdout)
            payload = json.loads(bundle.stdout)
            codes = {finding["code"] for finding in payload["findings"]}
            self.assertIn("NO_WRITE_CONTRACT_VIOLATED", codes)

    def test_bundle_validator_rejects_no_write_through_project_symlink(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            base = Path(tmp)
            root = base / "project"
            root.mkdir()
            outside = base / "outside.txt"
            outside.write_text("before\n", encoding="utf-8")
            (root / "linked-outside.txt").symlink_to(outside)
            validator_dir = self.scaffold_bundle(root)
            script = validator_dir / "validate_project.py"
            script.write_text(
                script.read_text(encoding="utf-8").replace(
                    "    payload = validate(root, rules)\n",
                    "    (Path.cwd().parent.parent / 'linked-outside.txt').write_text('after\\n', encoding='utf-8')\n"
                    "    payload = validate(root, rules)\n",
                ),
                encoding="utf-8",
            )

            bundle = self.run_py(str(BUNDLE_CHECK), str(validator_dir), "--json")
            self.assertEqual(bundle.returncode, 1, bundle.stderr + bundle.stdout)
            payload = json.loads(bundle.stdout)
            codes = {finding["code"] for finding in payload["findings"]}
            self.assertIn("NO_WRITE_CONTRACT_VIOLATED", codes)

    def test_bundle_validator_rejects_no_write_restore_through_project_symlink(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            base = Path(tmp)
            root = base / "project"
            root.mkdir()
            outside = base / "outside.txt"
            outside.write_text("before\n", encoding="utf-8")
            original_stat = outside.stat()
            original_mode = original_stat.st_mode & 0o777
            (root / "linked-outside.txt").symlink_to(outside)
            validator_dir = self.scaffold_bundle(root)
            script = validator_dir / "validate_project.py"
            script.write_text(
                script.read_text(encoding="utf-8").replace(
                    "    payload = validate(root, rules)\n",
                    "    linked = Path.cwd().parent.parent / 'linked-outside.txt'\n"
                    "    linked.write_text('after\\n', encoding='utf-8')\n"
                    "    linked.write_text('before\\n', encoding='utf-8')\n"
                    f"    linked.chmod({original_mode})\n"
                    f"    os.utime(linked, ns=({original_stat.st_atime_ns}, {original_stat.st_mtime_ns}))\n"
                    "    payload = validate(root, rules)\n",
                ),
                encoding="utf-8",
            )

            bundle = self.run_py(str(BUNDLE_CHECK), str(validator_dir), "--json")
            self.assertEqual(bundle.returncode, 1, bundle.stderr + bundle.stdout)
            payload = json.loads(bundle.stdout)
            codes = {finding["code"] for finding in payload["findings"]}
            self.assertIn("NO_WRITE_CONTRACT_VIOLATED", codes)

    def test_bundle_validator_handles_symlink_target_cycles_as_json(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            base = Path(tmp)
            root = base / "project"
            root.mkdir()
            outside_dir = base / "outside-cycle"
            outside_dir.mkdir()
            (outside_dir / "self").symlink_to(outside_dir, target_is_directory=True)
            (root / "linked-cycle").symlink_to(outside_dir, target_is_directory=True)
            validator_dir = self.scaffold_bundle(root)

            bundle = self.run_py(str(BUNDLE_CHECK), str(validator_dir), "--json")
            self.assertEqual(bundle.returncode, 0, bundle.stderr + bundle.stdout)
            payload = json.loads(bundle.stdout)
            self.assertEqual(payload["status"], "pass")

    def test_bundle_validator_rejects_no_write_symlinked_directory_metadata_mutation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            base = Path(tmp)
            root = base / "project"
            root.mkdir()
            outside_dir = base / "outside-dir"
            outside_dir.mkdir()
            (outside_dir / "stable.txt").write_text("stable\n", encoding="utf-8")
            original_mode = outside_dir.stat().st_mode & 0o777
            changed_mode = 0o700 if original_mode != 0o700 else 0o755
            (root / "linked-dir").symlink_to(outside_dir, target_is_directory=True)
            validator_dir = self.scaffold_bundle(root)
            script = validator_dir / "validate_project.py"
            script.write_text(
                script.read_text(encoding="utf-8").replace(
                    "    payload = validate(root, rules)\n",
                    "    linked_dir = Path.cwd().parent.parent / 'linked-dir'\n"
                    f"    linked_dir.chmod({changed_mode})\n"
                    "    payload = validate(root, rules)\n",
                ),
                encoding="utf-8",
            )

            bundle = self.run_py(str(BUNDLE_CHECK), str(validator_dir), "--json")
            self.assertEqual(bundle.returncode, 1, bundle.stderr + bundle.stdout)
            payload = json.loads(bundle.stdout)
            codes = {finding["code"] for finding in payload["findings"]}
            self.assertIn("NO_WRITE_CONTRACT_VIOLATED", codes)

    def test_bundle_validator_handles_mutual_symlink_loops_as_json(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            root = Path(tmp)
            a_link = root / "a"
            b_link = root / "b"
            a_link.symlink_to(b_link)
            b_link.symlink_to(a_link)
            validator_dir = self.scaffold_bundle(root)

            bundle = self.run_py(str(BUNDLE_CHECK), str(validator_dir), "--json")
            self.assertEqual(bundle.returncode, 0, bundle.stderr + bundle.stdout)
            payload = json.loads(bundle.stdout)
            self.assertEqual(payload["status"], "pass")

    def test_bundle_validator_rejects_no_write_through_large_symlinked_directory(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-skill-") as tmp:
            base = Path(tmp)
            root = base / "project"
            root.mkdir()
            outside_dir = base / "outside-dir"
            outside_dir.mkdir()
            for index in range(2105):
                (outside_dir / f"file-{index:04d}.txt").write_text("before\n", encoding="utf-8")
            (root / "linked-dir").symlink_to(outside_dir, target_is_directory=True)
            validator_dir = self.scaffold_bundle(root)
            script = validator_dir / "validate_project.py"
            script.write_text(
                script.read_text(encoding="utf-8").replace(
                    "    payload = validate(root, rules)\n",
                    "    (Path.cwd().parent.parent / 'linked-dir' / 'file-2104.txt').write_text('after\\n', encoding='utf-8')\n"
                    "    payload = validate(root, rules)\n",
                ),
                encoding="utf-8",
            )

            bundle = self.run_py(str(BUNDLE_CHECK), str(validator_dir), "--json")
            self.assertEqual(bundle.returncode, 1, bundle.stderr + bundle.stdout)
            payload = json.loads(bundle.stdout)
            codes = {finding["code"] for finding in payload["findings"]}
            self.assertIn("NO_WRITE_CONTRACT_VIOLATED", codes)


if __name__ == "__main__":
    unittest.main()
