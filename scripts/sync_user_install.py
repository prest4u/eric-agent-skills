#!/usr/bin/env python3
"""Keep Eric Agent Skills on one Git checkout across local agent products.

The repository checkout is the physical source. ``~/.agents/skills`` exposes
catalog skills as links to that checkout. Product-specific locations either
link to the shared root or have same-name duplicates removed so precedence can
never select an older copy. Every replaced entry is moved to a timestamped
backup before mutation.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import plistlib
import re
import shutil
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class Result:
    changed: list[str]
    drift: list[str]
    ok: list[str]

    @classmethod
    def empty(cls) -> "Result":
        return cls(changed=[], drift=[], ok=[])


def lexists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def resolved(path: Path) -> Path:
    return path.expanduser().resolve(strict=False)


def catalog_names(repo: Path) -> list[str]:
    data = yaml.safe_load((repo / "catalog" / "skills.yaml").read_text(encoding="utf-8"))
    records = data.get("skills", []) if isinstance(data, dict) else []
    names = [record.get("name") for record in records if isinstance(record, dict)]
    if not names or any(not isinstance(name, str) or not name for name in names):
        raise ValueError("catalog/skills.yaml has invalid skill records")
    if len(names) != len(set(names)):
        raise ValueError("catalog/skills.yaml contains duplicate skill names")
    for name in names:
        if not (repo / "skills" / name / "SKILL.md").is_file():
            raise FileNotFoundError(f"missing skills/{name}/SKILL.md")
    return names


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=repo, text=True, capture_output=True, check=False
    )
    if completed.returncode:
        message = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {message}")
    return completed.stdout.strip()


def update_checkout(repo: Path) -> None:
    if git(repo, "status", "--porcelain"):
        raise RuntimeError("checkout has local changes; refusing to overwrite them from GitHub")
    git(repo, "fetch", "origin", "main")
    git(repo, "merge", "--ff-only", "origin/main")


def validate_checkout(repo: Path) -> None:
    completed = subprocess.run(
        [sys.executable, str(repo / "scripts" / "validate_repo.py")],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        message = completed.stdout.strip() or completed.stderr.strip()
        raise RuntimeError(f"repository validation failed:\n{message}")


class Reconciler:
    def __init__(self, *, apply: bool, backup_root: Path, result: Result) -> None:
        self.apply = apply
        self.backup_root = backup_root
        self.result = result
        self._stamp = dt.datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")

    def _backup(self, path: Path, label: str) -> None:
        if not lexists(path):
            return
        target = self.backup_root / self._stamp / label / path.name
        target.parent.mkdir(parents=True, exist_ok=True)
        counter = 1
        while lexists(target):
            target = target.with_name(f"{path.name}.{counter}")
            counter += 1
        shutil.move(str(path), str(target))

    def ensure_link(self, path: Path, target: Path, label: str) -> None:
        target = resolved(target)
        if path.is_symlink() and resolved(path) == target:
            self.result.ok.append(f"{label}: {path}")
            return
        self.result.drift.append(f"{label}: {path} should link to {target}")
        if not self.apply:
            return
        self._backup(path, label)
        path.parent.mkdir(parents=True, exist_ok=True)
        relative = os.path.relpath(target, start=resolved(path.parent))
        path.symlink_to(relative, target_is_directory=True)
        self.result.changed.append(f"{label}: linked {path} -> {relative}")

    def ensure_absent(self, path: Path, label: str) -> None:
        if not lexists(path):
            self.result.ok.append(f"{label}: no duplicate {path}")
            return
        self.result.drift.append(f"{label}: higher-priority duplicate exists at {path}")
        if not self.apply:
            return
        self._backup(path, label)
        self.result.changed.append(f"{label}: backed up duplicate {path}")


def replace_toml_string_list(text: str, key: str, values: list[str]) -> str:
    rendered = key + " = [ " + ", ".join(json.dumps(value) for value in values) + " ]"
    match = re.search(rf"(?m)^{re.escape(key)}\s*=", text)
    if not match:
        return rendered + "\n" + text
    bracket = text.find("[", match.end())
    if bracket < 0:
        raise ValueError(f"{key} is not a TOML array")
    in_string = False
    escaped = False
    depth = 0
    for index in range(bracket, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return text[: match.start()] + rendered + text[index + 1 :]
    raise ValueError(f"unterminated TOML array for {key}")


def skill_name_from_manifest(manifest: Path) -> str | None:
    """Return a Skill's declared name without trusting its directory layout."""
    try:
        text = manifest.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end < 0:
        return None
    try:
        frontmatter = yaml.safe_load(text[4:end])
    except yaml.YAMLError:
        return None
    name = frontmatter.get("name") if isinstance(frontmatter, dict) else None
    return name if isinstance(name, str) and name else None


def discovered_skill_dirs(root: Path) -> list[tuple[Path, str]]:
    """Find the same active Skill manifests that Hermes recursively indexes."""
    if not root.is_dir():
        return []
    excluded = {
        ".git", ".github", ".hub", ".archive", ".venv", "venv",
        "node_modules", "site-packages", "__pycache__", ".tox", ".nox",
        ".pytest_cache", ".mypy_cache", ".ruff_cache",
    }
    support = {"references", "templates", "assets", "scripts"}
    manifests: set[Path] = set()
    for current, directories, files in os.walk(root, followlinks=True):
        has_skill_manifest = "SKILL.md" in files
        directories[:] = [
            directory
            for directory in directories
            if directory not in excluded
            and not (has_skill_manifest and directory in support)
        ]
        if has_skill_manifest:
            manifests.add(Path(current) / "SKILL.md")
    found: list[tuple[Path, str]] = []
    for manifest in manifests:
        name = skill_name_from_manifest(manifest) or manifest.parent.name
        found.append((manifest.parent, name))
    return sorted(set(found), key=lambda item: (len(item[0].parts), str(item[0])))


def remove_catalog_shadows(
    *, root: Path, names: list[str], reconciler: Reconciler, label: str,
    allowed_root_links: bool = False,
) -> None:
    """Remove catalog Skills hidden at arbitrary depths in a product tree."""
    managed = set(names)
    for skill_dir, name in discovered_skill_dirs(root):
        if name not in managed:
            continue
        if allowed_root_links and skill_dir == root / name:
            continue
        reconciler.ensure_absent(skill_dir, label)


def reconcile_kimi_desktop(
    *, home: Path, shared_root: Path, names: list[str], reconciler: Reconciler
) -> None:
    daimon = home / "Library/Application Support/kimi-desktop/daimon-share/daimon"
    config = daimon / "runtime/kimi-code/config.toml"
    skills_root = daimon / "skills"
    if not config.is_file() or not skills_root.is_dir():
        reconciler.result.ok.append("kimi-desktop: not installed or no local agent runtime")
        return

    # Parse the whole file before making any Kimi Desktop mutation. A malformed
    # configuration must leave both the config and its local Skill copies intact.
    text = config.read_text(encoding="utf-8")
    parsed = tomllib.loads(text)
    current_value = parsed.get("extra_skill_dirs", [])
    if not isinstance(current_value, list) or not all(
        isinstance(item, str) for item in current_value
    ):
        raise ValueError("Kimi Desktop extra_skill_dirs must be an array of strings")
    current: list[str] = current_value

    for name in names:
        reconciler.ensure_absent(skills_root / name, "kimi-desktop")

    shared = str(resolved(shared_root))
    daimon_skills = str(resolved(skills_root))
    desired = [shared] + [item for item in current if item not in {shared, daimon_skills}]
    desired.append(daimon_skills)
    if current == desired:
        reconciler.result.ok.append("kimi-desktop: shared skills root is first")
        return
    reconciler.result.drift.append("kimi-desktop: extra_skill_dirs does not prefer the shared root")
    if not reconciler.apply:
        return
    backup = reconciler.backup_root / reconciler._stamp / "kimi-desktop-config" / "config.toml"
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(config, backup)
    config.write_text(replace_toml_string_list(text, "extra_skill_dirs", desired), encoding="utf-8")
    reconciler.result.changed.append("kimi-desktop: configured shared skills root first")


def reconcile_install(repo: Path, home: Path, *, apply: bool, backup_root: Path) -> Result:
    names = catalog_names(repo)
    result = Result.empty()
    reconciler = Reconciler(apply=apply, backup_root=backup_root, result=result)
    shared = home / ".agents/skills"

    for name in names:
        reconciler.ensure_link(shared / name, repo / "skills" / name, "shared")

    # These products discover ~/.agents/skills natively. Removing same-name
    # copies prevents their precedence rules from selecting an older package.
    for label, root in (
        ("codex", home / ".codex/skills"),
        ("cursor", home / ".cursor/skills"),
        ("kimi-code", home / ".kimi-code/skills"),
        ("kimi-legacy", home / ".kimi/skills"),
    ):
        for name in names:
            reconciler.ensure_absent(root / name, label)

    # Claude Code does not currently scan ~/.agents/skills, so keep lightweight
    # links in its documented personal Skill directory.
    for name in names:
        reconciler.ensure_link(home / ".claude/skills" / name, shared / name, "claude-code")

    # Hermes recursively scans Skill roots. Remove catalog Skills hidden at any
    # depth before wiring the documented default root to the shared source.
    hermes_root = home / ".hermes/skills"
    remove_catalog_shadows(
        root=hermes_root,
        names=names,
        reconciler=reconciler,
        label="hermes-nested",
        allowed_root_links=True,
    )
    for name in names:
        reconciler.ensure_link(hermes_root / name, shared / name, "hermes")
    profiles = home / ".hermes/profiles"
    if profiles.is_dir():
        for profile in profiles.iterdir():
            if not profile.is_dir():
                continue
            remove_catalog_shadows(
                root=profile / "skills",
                names=names,
                reconciler=reconciler,
                label=f"hermes-profile-{profile.name}",
            )

    reconcile_kimi_desktop(home=home, shared_root=shared, names=names, reconciler=reconciler)
    return result


def install_launch_agent(repo: Path, home: Path, backup_root: Path) -> Path:
    label = "com.eric.agent-skills-sync"
    path = home / "Library/LaunchAgents" / f"{label}.plist"
    log_dir = home / "Library/Logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "Label": label,
        "ProgramArguments": [
            sys.executable,
            str(repo / "scripts" / "sync_user_install.py"),
            "--repo",
            str(repo),
            "--update",
            "--apply",
            "--quiet",
        ],
        "RunAtLoad": True,
        "StartInterval": 900,
        "StandardOutPath": str(log_dir / "EricAgentSkillsSync.log"),
        "StandardErrorPath": str(log_dir / "EricAgentSkillsSync.error.log"),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    if lexists(path):
        stamp = dt.datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")
        backup = backup_root / stamp / "launch-agent" / path.name
        backup.parent.mkdir(parents=True, exist_ok=True)
        counter = 1
        while lexists(backup):
            backup = backup.with_name(f"{path.name}.{counter}")
            counter += 1
        shutil.move(str(path), str(backup))
    with path.open("wb") as handle:
        plistlib.dump(payload, handle, sort_keys=True)
    return path


def write_state(repo: Path, home: Path, names: list[str], result: Result) -> Path:
    state = home / ".local/state/eric-agent-skills/status.json"
    state.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "repository": str(repo),
        "remote": git(repo, "remote", "get-url", "origin"),
        "commit": git(repo, "rev-parse", "HEAD"),
        "skill_count": len(names),
        "updated_at": dt.datetime.now().astimezone().isoformat(),
        "changed": result.changed,
        "remaining_drift": result.drift if not result.changed else [],
    }
    state.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--backup-root", type=Path)
    parser.add_argument("--apply", action="store_true", help="Back up conflicts and reconcile every agent surface")
    parser.add_argument("--check", action="store_true", help="Check only (the default when --apply is absent)")
    parser.add_argument("--update", action="store_true", help="Fast-forward this clean checkout from origin/main first")
    parser.add_argument("--install-launch-agent", action="store_true", help="Install a 15-minute macOS update-and-reconcile job")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = resolved(args.repo)
    home = resolved(args.home)
    backup_root = resolved(
        args.backup_root or home / ".local/state/eric-agent-skills/backups"
    )
    if args.update:
        update_checkout(repo)
    validate_checkout(repo)
    result = reconcile_install(repo, home, apply=args.apply, backup_root=backup_root)
    names = catalog_names(repo)
    launch_agent = None
    if args.install_launch_agent:
        if not args.apply:
            raise RuntimeError("--install-launch-agent requires --apply")
        launch_agent = install_launch_agent(repo, home, backup_root)
    state = write_state(repo, home, names, result) if args.apply else None
    payload = {
        "ok": not result.drift or args.apply,
        "mode": "apply" if args.apply else "check",
        "skill_count": len(names),
        "changed": result.changed,
        "drift": result.drift,
        "state": str(state) if state else None,
        "launch_agent": str(launch_agent) if launch_agent else None,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif not args.quiet:
        print(f"{payload['mode']}: {len(names)} skills")
        print(f"changed: {len(result.changed)}")
        print(f"drift: {len(result.drift)}")
        if result.drift and not args.apply:
            for item in result.drift:
                print(f"- {item}")
        if state:
            print(f"state: {state}")
        if launch_agent:
            print(f"launch agent: {launch_agent}")
    return 0 if args.apply or not result.drift else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"sync failed: {exc}", file=sys.stderr)
        raise SystemExit(2)
