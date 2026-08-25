from __future__ import annotations

import importlib.util
import json
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

REGISTER_SPEC = importlib.util.spec_from_file_location(
    "register_tool_surface",
    REPO / "skills/eric-catalog/scripts/register_tool_surface.py",
)
assert REGISTER_SPEC and REGISTER_SPEC.loader
REGISTER = importlib.util.module_from_spec(REGISTER_SPEC)
sys.modules[REGISTER_SPEC.name] = REGISTER
REGISTER_SPEC.loader.exec_module(REGISTER)


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
                home / ".config/opencode/skills/alpha-skill",
                home / ".roo/skills/alpha-skill",
                home / ".claude/skills/alpha-skill",
                home / ".cline/skills/alpha-skill",
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
            self.assertFalse((home / ".config/opencode/skills/alpha-skill").exists())
            self.assertFalse((home / ".roo/skills/alpha-skill").exists())
            self.assertEqual((shared / "alpha-skill").resolve(), (home / ".claude/skills/alpha-skill").resolve())
            self.assertEqual((shared / "alpha-skill").resolve(), (home / ".cline/skills/alpha-skill").resolve())
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

    def test_custom_tool_registry_reconciles_link_and_shadow_modes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            home = root / "home"
            repo = self.make_repo(root)
            backup = root / "backups"
            registry = home / ".config/eric-agent-skills/tool-surfaces.json"
            linked = root / "custom-linked-skills"
            shadowed = root / "custom-native-skills"

            for skills_root in (linked, shadowed):
                stale = skills_root / "alpha-skill"
                stale.mkdir(parents=True)
                (stale / "SKILL.md").write_text(
                    "---\nname: alpha-skill\ndescription: stale\n---\n",
                    encoding="utf-8",
                )

            REGISTER.register_surface(
                registry=registry,
                name="future-agent",
                mode="links",
                skills_root=str(linked),
                home=home,
                repo=repo,
            )
            REGISTER.register_surface(
                registry=registry,
                name="native-agent",
                mode="shadows",
                skills_root=str(shadowed),
                home=home,
                repo=repo,
            )

            SYNC.reconcile_install(repo, home, apply=True, backup_root=backup)
            shared = home / ".agents/skills"
            self.assertEqual(
                (shared / "alpha-skill").resolve(),
                (linked / "alpha-skill").resolve(),
            )
            self.assertFalse((shadowed / "alpha-skill").exists())
            self.assertTrue(any(backup.rglob("alpha-skill/SKILL.md")))

            checked = SYNC.reconcile_install(
                repo, home, apply=False, backup_root=backup
            )
            self.assertEqual([], checked.drift)

    def test_invalid_custom_registry_fails_before_shared_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            home = root / "home"
            repo = self.make_repo(root)
            backup = root / "backups"
            shared = home / ".agents/skills/alpha-skill"
            shared.mkdir(parents=True)
            (shared / "SKILL.md").write_text("old", encoding="utf-8")
            registry = home / ".config/eric-agent-skills/tool-surfaces.json"
            registry.parent.mkdir(parents=True)
            registry.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "surfaces": [
                            {
                                "name": "unsafe",
                                "mode": "shadows",
                                "skills_root": str(repo / "skills"),
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "unsafe custom tool skills_root"):
                SYNC.reconcile_install(repo, home, apply=True, backup_root=backup)

            self.assertEqual("old", (shared / "SKILL.md").read_text(encoding="utf-8"))
            self.assertFalse(backup.exists())

    def test_registration_rejects_authority_and_overlapping_roots(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            home = root / "home"
            repo = self.make_repo(root)
            registry = home / ".config/eric-agent-skills/tool-surfaces.json"

            with self.assertRaisesRegex(ValueError, "unsafe"):
                REGISTER.register_surface(
                    registry=registry,
                    name="authority-copy",
                    mode="links",
                    skills_root=str(repo / "skills"),
                    home=home,
                    repo=repo,
                )
            self.assertFalse(registry.exists())

            first = root / "tool-a/skills"
            REGISTER.register_surface(
                registry=registry,
                name="tool-a",
                mode="links",
                skills_root=str(first),
                home=home,
                repo=repo,
            )
            before = registry.read_bytes()
            with self.assertRaisesRegex(ValueError, "overlaps"):
                REGISTER.register_surface(
                    registry=registry,
                    name="tool-b",
                    mode="shadows",
                    skills_root=str(first / "nested-skills"),
                    home=home,
                    repo=repo,
                )
            self.assertEqual(before, registry.read_bytes())

            with self.assertRaisesRegex(ValueError, "absolute"):
                REGISTER.register_surface(
                    registry=registry,
                    name="relative-tool",
                    mode="links",
                    skills_root="relative-skills",
                    home=home,
                    repo=repo,
                )
            self.assertEqual(before, registry.read_bytes())

    def test_custom_root_cannot_overlap_kimi_desktop(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            home = root / "home"
            repo = self.make_repo(root)
            backup = root / "backups"
            shared = home / ".agents/skills/alpha-skill"
            shared.mkdir(parents=True)
            (shared / "SKILL.md").write_text("old", encoding="utf-8")
            kimi_skills = (
                home
                / "Library/Application Support/kimi-desktop/daimon-share/daimon/skills"
            )
            registry = home / ".config/eric-agent-skills/tool-surfaces.json"
            REGISTER.register_surface(
                registry=registry,
                name="kimi-overlap",
                mode="links",
                skills_root=str(kimi_skills),
                home=home,
                repo=repo,
            )

            with self.assertRaisesRegex(ValueError, "built-in adapter"):
                SYNC.reconcile_install(repo, home, apply=True, backup_root=backup)

            self.assertEqual("old", (shared / "SKILL.md").read_text(encoding="utf-8"))
            self.assertFalse(backup.exists())

    def test_custom_root_cannot_overlap_hermes_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            home = root / "home"
            repo = self.make_repo(root)
            backup = root / "backups"
            shared = home / ".agents/skills/alpha-skill"
            shared.mkdir(parents=True)
            (shared / "SKILL.md").write_text("old", encoding="utf-8")
            profile = home / ".hermes/profiles/reviewer"
            profile.mkdir(parents=True)
            profile_skills = profile / "skills"
            registry = home / ".config/eric-agent-skills/tool-surfaces.json"
            REGISTER.register_surface(
                registry=registry,
                name="profile-overlap",
                mode="links",
                skills_root=str(profile_skills),
                home=home,
                repo=repo,
            )

            with self.assertRaisesRegex(ValueError, "built-in adapter"):
                SYNC.reconcile_install(repo, home, apply=True, backup_root=backup)

            self.assertEqual("old", (shared / "SKILL.md").read_text(encoding="utf-8"))
            self.assertFalse(backup.exists())

    def test_shadow_root_linked_to_authority_is_not_traversed_or_removed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            home = root / "home"
            repo = self.make_repo(root)
            backup = root / "backups"
            shared = home / ".agents/skills"
            shared.mkdir(parents=True)
            product_root = home / ".codex/skills"
            product_root.parent.mkdir(parents=True)
            product_root.symlink_to(shared, target_is_directory=True)

            result = SYNC.reconcile_install(
                repo, home, apply=True, backup_root=backup
            )

            self.assertTrue(product_root.is_symlink())
            self.assertEqual(
                (repo / "skills/alpha-skill").resolve(),
                (shared / "alpha-skill").resolve(),
            )
            self.assertTrue(
                any(
                    item == "codex: root already links to the shared authority"
                    for item in result.ok
                )
            )
            self.assertFalse(any(backup.rglob("alpha-skill/SKILL.md")))

    def test_unverified_product_root_symlink_fails_before_shared_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            home = root / "home"
            repo = self.make_repo(root)
            backup = root / "backups"
            shared = home / ".agents/skills/alpha-skill"
            shared.mkdir(parents=True)
            (shared / "SKILL.md").write_text("old", encoding="utf-8")
            external = root / "external-skills"
            external.mkdir()
            product_root = home / ".claude/skills"
            product_root.parent.mkdir(parents=True)
            product_root.symlink_to(external, target_is_directory=True)

            with self.assertRaisesRegex(ValueError, "unverified target"):
                SYNC.reconcile_install(repo, home, apply=True, backup_root=backup)

            self.assertEqual("old", (shared / "SKILL.md").read_text(encoding="utf-8"))
            self.assertTrue(product_root.is_symlink())
            self.assertFalse(backup.exists())

    def test_symlinked_hermes_profile_fails_before_external_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            home = root / "home"
            repo = self.make_repo(root)
            backup = root / "backups"
            shared = home / ".agents/skills/alpha-skill"
            shared.mkdir(parents=True)
            (shared / "SKILL.md").write_text("old-shared", encoding="utf-8")
            external_skill = root / "external-profile/skills/alpha-skill"
            external_skill.mkdir(parents=True)
            manifest = external_skill / "SKILL.md"
            manifest.write_text(
                "---\nname: alpha-skill\ndescription: external\n---\n",
                encoding="utf-8",
            )
            profile = home / ".hermes/profiles/reviewer"
            profile.parent.mkdir(parents=True)
            profile.symlink_to(external_skill.parents[1], target_is_directory=True)

            with self.assertRaisesRegex(ValueError, "profile directory is a symlink"):
                SYNC.reconcile_install(repo, home, apply=True, backup_root=backup)

            self.assertEqual(
                "old-shared", (shared / "SKILL.md").read_text(encoding="utf-8")
            )
            self.assertTrue(manifest.is_file())
            self.assertTrue(profile.is_symlink())
            self.assertFalse(backup.exists())

    def test_symlinked_shared_root_fails_without_touching_authority(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            home = root / "home"
            repo = self.make_repo(root)
            backup = root / "backups"
            shared = home / ".agents/skills"
            shared.parent.mkdir(parents=True)
            shared.symlink_to(repo / "skills", target_is_directory=True)

            with self.assertRaisesRegex(ValueError, "shared Skill root"):
                SYNC.reconcile_install(repo, home, apply=True, backup_root=backup)

            for name in ("alpha-skill", "beta-skill"):
                self.assertTrue((repo / "skills" / name / "SKILL.md").is_file())
            self.assertTrue(shared.is_symlink())
            self.assertFalse(backup.exists())

    def test_symlinked_agents_ancestor_fails_without_external_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            home = root / "home"
            home.mkdir()
            repo = self.make_repo(root)
            backup = root / "backups"
            external_skill = root / "external-agents/skills/alpha-skill"
            external_skill.mkdir(parents=True)
            manifest = external_skill / "SKILL.md"
            manifest.write_text("external", encoding="utf-8")
            (home / ".agents").symlink_to(
                root / "external-agents", target_is_directory=True
            )

            with self.assertRaisesRegex(ValueError, "shared Skill root"):
                SYNC.reconcile_install(repo, home, apply=True, backup_root=backup)

            self.assertEqual("external", manifest.read_text(encoding="utf-8"))
            self.assertFalse(backup.exists())

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
            shared = home / ".agents/skills/alpha-skill"
            shared.mkdir(parents=True)
            (shared / "SKILL.md").write_text("old-shared", encoding="utf-8")
            daimon = home / "Library/Application Support/kimi-desktop/daimon-share/daimon"
            stale = daimon / "skills/alpha-skill"
            stale.mkdir(parents=True)
            (stale / "SKILL.md").write_text("old", encoding="utf-8")
            config = daimon / "runtime/kimi-code/config.toml"
            config.parent.mkdir(parents=True)
            invalid = 'extra_skill_dirs = [ "/keep",\n'
            config.write_text(invalid, encoding="utf-8")

            with self.assertRaises(SYNC.tomllib.TOMLDecodeError):
                SYNC.reconcile_install(repo, home, apply=True, backup_root=backup)

            self.assertTrue(stale.is_dir())
            self.assertEqual(invalid, config.read_text(encoding="utf-8"))
            self.assertEqual(
                "old-shared", (shared / "SKILL.md").read_text(encoding="utf-8")
            )
            self.assertFalse(backup.exists())

    def test_linked_skill_collection_blocks_before_out_of_root_mutation(self) -> None:
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

            with self.assertRaisesRegex(ValueError, "collection link"):
                SYNC.reconcile_install(repo, home, apply=True, backup_root=backup)

            self.assertTrue(external_shadow.exists())
            self.assertTrue((skills / "linked-category").is_symlink())
            self.assertTrue(archived.is_dir())
            self.assertTrue(reference.is_dir())
            self.assertFalse(backup.exists())
            self.assertFalse((home / ".agents/skills/alpha-skill").exists())

    def test_direct_skill_symlink_is_backed_up_without_moving_its_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            home = root / "home"
            repo = self.make_repo(root)
            backup = root / "backups"
            external = root / "external/alpha-skill"
            external.mkdir(parents=True)
            manifest = external / "SKILL.md"
            manifest.write_text(
                "---\nname: alpha-skill\ndescription: external\n---\n",
                encoding="utf-8",
            )
            product_skill = home / ".codex/skills/alpha-skill"
            product_skill.parent.mkdir(parents=True)
            product_skill.symlink_to(external, target_is_directory=True)

            SYNC.reconcile_install(repo, home, apply=True, backup_root=backup)

            self.assertFalse(product_skill.exists())
            self.assertTrue(manifest.is_file())
            self.assertTrue(any(path.is_symlink() for path in backup.rglob("alpha-skill")))

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
