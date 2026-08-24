from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "sync_user_install", REPO / "scripts" / "sync_user_install.py"
)
assert SPEC and SPEC.loader
SYNC = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SYNC
SPEC.loader.exec_module(SYNC)


class SyncUserInstallTest(unittest.TestCase):
    def make_repo(self, root: Path) -> Path:
        repo = root / "repo"
        (repo / "catalog").mkdir(parents=True)
        (repo / "catalog/skills.yaml").write_text(
            "schema_version: 1\nskills:\n"
            "  - name: alpha-skill\n"
            "  - name: beta-skill\n",
            encoding="utf-8",
        )
        for name in ("alpha-skill", "beta-skill"):
            skill = repo / "skills" / name
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                f"---\nname: {name}\ndescription: test\n---\n", encoding="utf-8"
            )
        return repo

    def test_apply_replaces_duplicates_and_wires_every_surface(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            home = root / "home"
            repo = self.make_repo(root)
            backup = root / "backups"

            for path in (
                home / ".agents/skills/alpha-skill",
                home / ".codex/skills/alpha-skill",
                home / ".claude/skills/alpha-skill",
                home / ".hermes/skills/alpha-skill",
                home / ".hermes/profiles/reviewer/skills/teaching/k12/alpha-skill",
            ):
                path.mkdir(parents=True)
                (path / "SKILL.md").write_text("old", encoding="utf-8")

            daimon = home / "Library/Application Support/kimi-desktop/daimon-share/daimon"
            (daimon / "skills/alpha-skill").mkdir(parents=True)
            (daimon / "skills/alpha-skill/SKILL.md").write_text("old", encoding="utf-8")
            (daimon / "runtime/kimi-code").mkdir(parents=True)
            daimon_root = str((daimon / "skills").resolve())
            (daimon / "runtime/kimi-code/config.toml").write_text(
                'theme = "dark"\n'
                'extra_skill_dirs = [\n'
                '  "/keep-team-skills",\n'
                f'  "{daimon_root}",\n'
                ']\n',
                encoding="utf-8",
            )

            result = SYNC.reconcile_install(
                repo, home, apply=True, backup_root=backup
            )
            self.assertTrue(result.changed)
            shared = home / ".agents/skills"
            self.assertEqual((repo / "skills/alpha-skill").resolve(), (shared / "alpha-skill").resolve())
            self.assertFalse((home / ".codex/skills/alpha-skill").exists())
            self.assertEqual((shared / "alpha-skill").resolve(), (home / ".claude/skills/alpha-skill").resolve())
            self.assertEqual((shared / "alpha-skill").resolve(), (home / ".hermes/skills/alpha-skill").resolve())
            self.assertFalse((home / ".hermes/profiles/reviewer/skills/teaching/k12/alpha-skill").exists())
            self.assertFalse((daimon / "skills/alpha-skill").exists())
            config = (daimon / "runtime/kimi-code/config.toml").read_text(encoding="utf-8")
            self.assertLess(config.index(str(shared.resolve())), config.index(daimon_root))
            self.assertIn("/keep-team-skills", config)
            self.assertTrue(any(backup.rglob("SKILL.md")))

            checked = SYNC.reconcile_install(
                repo, home, apply=False, backup_root=backup
            )
            self.assertEqual([], checked.drift)

    def test_toml_list_replacement_preserves_other_settings(self) -> None:
        original = 'theme = "dark"\nextra_skill_dirs = [ "/old" ]\n[models]\n'
        updated = SYNC.replace_toml_string_list(
            original, "extra_skill_dirs", ["/shared", "/old"]
        )
        self.assertIn('theme = "dark"', updated)
        self.assertIn('extra_skill_dirs = [ "/shared", "/old" ]', updated)
        self.assertTrue(updated.endswith("[models]\n"))

    def test_malformed_kimi_config_fails_before_any_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            home = root / "home"
            repo = self.make_repo(root)
            backup = root / "backups"
            daimon = home / "Library/Application Support/kimi-desktop/daimon-share/daimon"
            stale = daimon / "skills/alpha-skill"
            stale.mkdir(parents=True)
            (stale / "SKILL.md").write_text("old", encoding="utf-8")
            config = daimon / "runtime/kimi-code/config.toml"
            config.parent.mkdir(parents=True)
            invalid = 'extra_skill_dirs = [ "/keep",\n'
            config.write_text(invalid, encoding="utf-8")

            reconciler = SYNC.Reconciler(
                apply=True, backup_root=backup, result=SYNC.Result.empty()
            )
            with self.assertRaises(SYNC.tomllib.TOMLDecodeError):
                SYNC.reconcile_kimi_desktop(
                    home=home,
                    shared_root=home / ".agents/skills",
                    names=SYNC.catalog_names(repo),
                    reconciler=reconciler,
                )

            self.assertTrue(stale.is_dir())
            self.assertEqual(invalid, config.read_text(encoding="utf-8"))
            self.assertFalse(backup.exists())

    def test_hermes_follows_linked_categories_but_skips_inactive_packages(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            home = root / "home"
            repo = self.make_repo(root)
            backup = root / "backups"
            profile = home / ".hermes/profiles/reviewer"
            skills = profile / "skills"

            external_shadow = profile / "linked-source/alpha-skill"
            external_shadow.mkdir(parents=True)
            (external_shadow / "SKILL.md").write_text(
                "---\nname: alpha-skill\ndescription: linked shadow\n---\n",
                encoding="utf-8",
            )
            skills.mkdir(parents=True)
            (skills / "linked-category").symlink_to(
                "../linked-source", target_is_directory=True
            )

            archived = skills / ".archive/alpha-skill"
            archived.mkdir(parents=True)
            (archived / "SKILL.md").write_text(
                "---\nname: alpha-skill\ndescription: archive\n---\n",
                encoding="utf-8",
            )
            host = skills / "host-skill"
            reference = host / "references/alpha-skill"
            reference.mkdir(parents=True)
            (host / "SKILL.md").write_text(
                "---\nname: unrelated-host\ndescription: host\n---\n",
                encoding="utf-8",
            )
            (reference / "SKILL.md").write_text(
                "---\nname: alpha-skill\ndescription: reference\n---\n",
                encoding="utf-8",
            )

            SYNC.reconcile_install(repo, home, apply=True, backup_root=backup)

            self.assertFalse(external_shadow.exists())
            self.assertTrue((skills / "linked-category").is_symlink())
            self.assertTrue(archived.is_dir())
            self.assertTrue(reference.is_dir())
            self.assertTrue(any(backup.rglob("alpha-skill/SKILL.md")))

            checked = SYNC.reconcile_install(
                repo, home, apply=False, backup_root=backup
            )
            self.assertEqual([], checked.drift)

    def test_launch_agent_replacement_is_backed_up(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            home = root / "home"
            repo = self.make_repo(root)
            backup = root / "backups"
            launch_agent = home / "Library/LaunchAgents/com.eric.agent-skills-sync.plist"
            launch_agent.parent.mkdir(parents=True)
            launch_agent.write_text("previous launch agent", encoding="utf-8")

            installed = SYNC.install_launch_agent(repo, home, backup)

            self.assertEqual(launch_agent, installed)
            self.assertEqual("previous launch agent", next(backup.rglob(launch_agent.name)).read_text())
            with installed.open("rb") as handle:
                payload = SYNC.plistlib.load(handle)
            self.assertEqual("com.eric.agent-skills-sync", payload["Label"])
            self.assertEqual(900, payload["StartInterval"])


if __name__ == "__main__":
    unittest.main()
