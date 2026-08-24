from __future__ import annotations

import importlib.util
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml


REPO = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = REPO / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


SYNC = load_script("sync_upstreams.py")
MIRRORS = load_script("export_mirrors.py")
APPLY_MIRROR = load_script("apply_mirror.py")
SECURITY_GATE = load_script("check_skillspector_report.py")
VALIDATOR = load_script("validate_repo.py")
PUSH_MIRRORS = load_script("push_mirrors.py")


class UpstreamSafetyTest(unittest.TestCase):
    def test_tree_hash_changes_with_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "a.txt").write_text("one", encoding="utf-8")
            first = SYNC.tree_hash(root)
            (root / "a.txt").write_text("two", encoding="utf-8")
            self.assertNotEqual(first, SYNC.tree_hash(root))

    def test_source_note_can_be_excluded_from_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "a.txt").write_text("content", encoding="utf-8")
            expected = SYNC.tree_hash(root)
            (root / "_SOURCE.md").write_text("metadata", encoding="utf-8")
            self.assertEqual(expected, SYNC.tree_hash(root, exclude_source_note=True))

    def test_rejects_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "target.txt").write_text("content", encoding="utf-8")
            link = root / "link.txt"
            try:
                link.symlink_to(root / "target.txt")
            except OSError:
                self.skipTest("symlinks unavailable")
            with self.assertRaises(ValueError):
                SYNC.assert_safe_tree(root)

    def test_finder_duplicate_requires_identical_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "guide.md").write_text("canonical", encoding="utf-8")
            (root / "guide 2.md").write_text("different", encoding="utf-8")
            with self.assertRaises(ValueError):
                SYNC.remove_identical_finder_duplicates(root)

    def test_finder_duplicate_is_removed_when_identical(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "guide.md").write_text("same", encoding="utf-8")
            (root / "guide 2.md").write_text("same", encoding="utf-8")
            SYNC.remove_identical_finder_duplicates(root)
            self.assertFalse((root / "guide 2.md").exists())

    def test_license_change_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            checkout = Path(temp)
            (checkout / "LICENSE").write_text("MIT License", encoding="utf-8")
            entry = {
                "id": "sample",
                "license": "MIT",
                "license_evidence_path": "LICENSE",
                "license_sha256": "0" * 64,
            }
            with self.assertRaises(ValueError):
                SYNC.verify_license(checkout, entry)

    def _update_fixture(self, root: Path, *, commit: str = "new-commit"):
        repo = root / "repo"
        checkout = root / "checkout"
        source = checkout / "skill"
        destination_parent = repo / "skills" / "target" / "references" / "upstream"
        source.mkdir(parents=True)
        destination_parent.mkdir(parents=True)
        (source / "SKILL.md").write_text("reviewed content\n", encoding="utf-8")
        license_bytes = b"MIT License\n"
        (checkout / "LICENSE").write_bytes(license_bytes)
        entry = {
            "id": "sample",
            "repository": "https://github.com/example/upstream.git",
            "source_path": "skill",
            "commit": commit,
            "tree_sha256": SYNC.tree_hash(source),
            "license": "MIT",
            "license_evidence_path": "LICENSE",
            "license_sha256": hashlib.sha256(license_bytes).hexdigest(),
            "mode": "vendored-reference",
            "targets": ["target"],
        }
        return repo, checkout, source, {"upstreams": [entry]}, entry

    def test_no_change_update_is_stable(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo, checkout, _source, lock, entry = self._update_fixture(Path(temp))
            with patch.object(SYNC, "head", return_value=entry["commit"]):
                changed = SYNC.do_update(repo, lock, {"example/upstream": checkout})
            self.assertFalse(changed)
            snapshot = repo / "skills" / "target" / "references" / "upstream" / "sample"
            self.assertEqual("reviewed content\n", (snapshot / "SKILL.md").read_text(encoding="utf-8"))
            self.assertTrue((snapshot / "_SOURCE.md").is_file())

    def test_normal_upgrade_updates_lock_and_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo, checkout, source, lock, entry = self._update_fixture(Path(temp), commit="old-commit")
            (source / "SKILL.md").write_text("upgraded content\n", encoding="utf-8")
            with patch.object(SYNC, "head", return_value="new-commit"):
                changed = SYNC.do_update(repo, lock, {"example/upstream": checkout})
            self.assertTrue(changed)
            self.assertEqual("new-commit", entry["commit"])
            self.assertEqual(SYNC.tree_hash(source), entry["tree_sha256"])
            snapshot = repo / "skills" / "target" / "references" / "upstream" / "sample"
            self.assertEqual("upgraded content\n", (snapshot / "SKILL.md").read_text(encoding="utf-8"))

    def test_source_path_traversal_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo, checkout, _source, lock, entry = self._update_fixture(Path(temp))
            outside = checkout.parent / "outside"
            outside.mkdir()
            (outside / "SKILL.md").write_text("escape", encoding="utf-8")
            entry["source_path"] = "../outside"
            with patch.object(SYNC, "head", return_value=entry["commit"]):
                with self.assertRaisesRegex(ValueError, "source path escapes checkout"):
                    SYNC.do_update(repo, lock, {"example/upstream": checkout})

    def test_target_path_traversal_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo, checkout, _source, lock, entry = self._update_fixture(Path(temp))
            entry["targets"] = ["../../../escaped-skill"]
            with patch.object(SYNC, "head", return_value=entry["commit"]):
                with self.assertRaisesRegex(ValueError, "invalid upstream target"):
                    SYNC.do_update(repo, lock, {"example/upstream": checkout})

    def test_upstream_id_path_traversal_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo, checkout, _source, lock, entry = self._update_fixture(Path(temp))
            entry["id"] = "../../escaped-snapshot"
            with patch.object(SYNC, "head", return_value=entry["commit"]):
                with self.assertRaisesRegex(ValueError, "invalid upstream id"):
                    SYNC.do_update(repo, lock, {"example/upstream": checkout})

    def test_repository_validator_detects_snapshot_tree_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            snapshot = repo / "skills" / "target" / "references" / "upstream" / "sample"
            snapshot.mkdir(parents=True)
            (snapshot / "SKILL.md").write_text("locked\n", encoding="utf-8")
            entry = {
                "id": "sample",
                "repository": "https://github.com/example/upstream.git",
                "commit": "a" * 40,
                "tree_sha256": VALIDATOR.snapshot_tree_hash(snapshot),
                "license": "MIT",
                "mode": "vendored-reference",
                "targets": ["target"],
            }
            (snapshot / "_SOURCE.md").write_text(
                f"{entry['repository']}\n{entry['commit']}\n{entry['license']}\n",
                encoding="utf-8",
            )
            (repo / "skills" / "target" / "THIRD_PARTY_NOTICES.md").write_text(
                "MIT License\n\nPermission is hereby granted\n",
                encoding="utf-8",
            )
            self.assertEqual([], VALIDATOR.validate_upstream_snapshots(repo, [entry], ["target"]))
            (snapshot / "SKILL.md").write_text("tampered\n", encoding="utf-8")
            issues = VALIDATOR.validate_upstream_snapshots(repo, [entry], ["target"])
            self.assertIn("UPSTREAM_SNAPSHOT_DRIFT", {item.code for item in issues})

    def test_local_machine_owned_conflict_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source"
            destination = root / "destination"
            source.mkdir()
            destination.mkdir()
            (source / "SKILL.md").write_text("upstream", encoding="utf-8")
            (destination / "SKILL.md").write_text("manual drift", encoding="utf-8")
            entry = {
                "tree_sha256": "0" * 64,
                "repository": "https://github.com/example/upstream.git",
                "source_path": "skill",
                "license": "MIT",
            }
            with self.assertRaisesRegex(ValueError, "local modification conflict"):
                SYNC.copy_snapshot(source, destination, entry, "new-commit")


class SecurityGateTest(unittest.TestCase):
    def test_unsuppressed_high_finding_blocks_release(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            report = {
                "execution_successful": True,
                "analysis_completeness": {
                    "coverage_percent": 100,
                    "analyzer_statuses": [],
                    "ledger_exceptions": [],
                },
                "issues": [
                    {
                        "id": "TEST-HIGH",
                        "severity": "HIGH",
                        "category": "Supply Chain",
                        "location": {"file": "SKILL.md", "start_line": 1},
                        "finding": "synthetic blocker",
                    }
                ],
            }
            (root / "sample.json").write_text(json.dumps(report), encoding="utf-8")
            with patch("sys.argv", ["check_skillspector_report.py", str(root)]):
                self.assertEqual(1, SECURITY_GATE.main())


class MirrorExportTest(unittest.TestCase):
    def test_exports_all_guarded_mirrors(self) -> None:
        records = MIRRORS.mirror_records(REPO)
        self.assertEqual(18, len(records))
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "mirror"
            MIRRORS.export_one(REPO, records[0], output)
            manifest = json.loads((output / ".mirror-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(records[0]["name"], manifest["skill"])
            self.assertIn("SKILL.md", manifest["managed_files"])
            self.assertTrue((output / "README.md").is_file())
            self.assertTrue((output / "THIRD_PARTY_NOTICES.md").is_file())

    def test_apply_requires_bootstrap_and_then_detects_drift(self) -> None:
        records = MIRRORS.mirror_records(REPO)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            generated = root / "generated"
            checkout = root / "checkout"
            checkout.mkdir()
            MIRRORS.export_one(REPO, records[0], generated)
            with self.assertRaises(ValueError):
                APPLY_MIRROR.apply(generated, checkout)
            APPLY_MIRROR.apply(generated, checkout, bootstrap=True)
            (checkout / "SKILL.md").write_text("manual drift", encoding="utf-8")
            with self.assertRaises(ValueError):
                APPLY_MIRROR.apply(generated, checkout)

    def test_apply_rejects_unmanaged_file_and_bootstrap_replaces_old_tree(self) -> None:
        records = MIRRORS.mirror_records(REPO)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            generated = root / "generated"
            checkout = root / "checkout"
            checkout.mkdir()
            (checkout / "legacy.txt").write_text("reviewed bootstrap removal", encoding="utf-8")
            MIRRORS.export_one(REPO, records[0], generated)
            APPLY_MIRROR.apply(generated, checkout, bootstrap=True)
            self.assertFalse((checkout / "legacy.txt").exists())
            (checkout / "manual-note.md").write_text("human fork", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unmanaged mirror files"):
                APPLY_MIRROR.apply(generated, checkout)

    def test_existing_mirror_tag_must_match_candidate_commit(self) -> None:
        tag = "v1.0.0"
        expected = "a" * 40
        self.assertTrue(
            PUSH_MIRRORS.assert_remote_tag_matches(
                f"{'b' * 40}\trefs/tags/{tag}\n{expected}\trefs/tags/{tag}^{{}}\n",
                tag,
                expected,
            )
        )
        with self.assertRaisesRegex(ValueError, "refusing to move it"):
            PUSH_MIRRORS.assert_remote_tag_matches(
                f"{'b' * 40}\trefs/tags/{tag}\n",
                tag,
                expected,
            )

    def test_conflicting_tag_is_checked_before_any_remote_write(self) -> None:
        record = {
            "name": "eric-pdf",
            "version": "1.0.0",
            "mirror": "prest4u/eric-pdf",
        }
        expected = "a" * 40
        commands: list[list[str]] = []

        def fake_run(command, cwd=None, *, capture=False):
            commands.append(command)
            if command[:3] == ["git", "status", "--porcelain"]:
                return " M SKILL.md"
            if command[:3] == ["git", "rev-parse", "HEAD"]:
                return expected
            if command[:3] == ["git", "ls-remote", "--tags"]:
                return f"{'b' * 40}\trefs/tags/v1.0.0\n"
            return ""

        with tempfile.TemporaryDirectory() as temp, patch.object(
            PUSH_MIRRORS.EXPORT, "export_one"
        ), patch.object(PUSH_MIRRORS.APPLY, "apply"), patch.object(
            PUSH_MIRRORS, "run", side_effect=fake_run
        ):
            with self.assertRaisesRegex(ValueError, "refusing to move it"):
                PUSH_MIRRORS.push_one(REPO, record, Path(temp), dry_run=False)

        self.assertFalse(
            any(command[:2] == ["git", "push"] for command in commands),
            commands,
        )

    def test_new_tag_and_main_are_pushed_atomically(self) -> None:
        record = {
            "name": "eric-pdf",
            "version": "1.0.0",
            "mirror": "prest4u/eric-pdf",
        }
        expected = "a" * 40
        commands: list[list[str]] = []

        def fake_run(command, cwd=None, *, capture=False):
            commands.append(command)
            if command[:3] == ["git", "status", "--porcelain"]:
                return " M SKILL.md"
            if command[:3] == ["git", "rev-parse", "HEAD"]:
                return expected
            if command[:3] == ["git", "ls-remote", "--tags"]:
                return ""
            return ""

        with tempfile.TemporaryDirectory() as temp, patch.object(
            PUSH_MIRRORS.EXPORT, "export_one"
        ), patch.object(PUSH_MIRRORS.APPLY, "apply"), patch.object(
            PUSH_MIRRORS, "run", side_effect=fake_run
        ):
            PUSH_MIRRORS.push_one(REPO, record, Path(temp), dry_run=False)

        pushes = [command for command in commands if command[:2] == ["git", "push"]]
        self.assertEqual(
            [[
                "git",
                "push",
                "--atomic",
                "origin",
                "HEAD:main",
                "refs/tags/v1.0.0:refs/tags/v1.0.0",
            ]],
            pushes,
        )


class IndependentInstallTest(unittest.TestCase):
    def test_all_64_skills_copy_as_self_contained_directories(self) -> None:
        catalog = yaml.safe_load(
            (REPO / "catalog" / "skills.yaml").read_text(encoding="utf-8")
        )
        records = catalog["skills"]
        self.assertEqual(64, len(records))
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for record in records:
                source = REPO / "skills" / record["name"]
                target = root / record["name"]
                shutil.copytree(source, target)
                self.assertTrue((target / "SKILL.md").is_file())
                self.assertFalse(any(path.is_symlink() for path in target.rglob("*")))
                source_files = {
                    path.relative_to(source): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in source.rglob("*")
                    if path.is_file()
                }
                target_files = {
                    path.relative_to(target): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in target.rglob("*")
                    if path.is_file()
                }
                self.assertEqual(source_files, target_files, record["name"])


if __name__ == "__main__":
    unittest.main()
