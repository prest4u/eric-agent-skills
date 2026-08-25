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


@dataclass(frozen=True)
class ToolSurface:
    label: str
    mode: str
    skills_root: Path


TOOL_SURFACE_SCHEMA = 1
TOOL_LABEL_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DISCOVERY_EXCLUDED = {
    ".git", ".github", ".hub", ".archive", ".venv", "venv",
    "node_modules", "site-packages", "__pycache__", ".tox", ".nox",
    ".pytest_cache", ".mypy_cache", ".ruff_cache",
}
DISCOVERY_SUPPORT = {"references", "templates", "assets", "scripts"}
MAX_LINK_SCAN_DIRECTORIES = 10_000


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


def paths_overlap(left: Path, right: Path) -> bool:
    left = resolved(left)
    right = resolved(right)
    try:
        left.relative_to(right)
        return True
    except ValueError:
        pass
    try:
        right.relative_to(left)
        return True
    except ValueError:
        return False


def expand_registered_root(raw: str, home: Path) -> Path:
    if raw == "~":
        path = home
    elif raw.startswith("~/"):
        path = home / raw[2:]
    else:
        path = Path(raw)
    if not path.is_absolute():
        raise ValueError("custom tool skills_root must be absolute or start with ~/")
    return resolved(path)


def load_custom_tool_surfaces(repo: Path, home: Path, shared: Path) -> list[ToolSurface]:
    registry = home / ".config/eric-agent-skills/tool-surfaces.json"
    if not registry.is_file():
        return []
    data = json.loads(registry.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != TOOL_SURFACE_SCHEMA:
        raise ValueError("unsupported custom tool-surface registry schema")
    records = data.get("surfaces")
    if not isinstance(records, list) or len(records) > 64:
        raise ValueError("custom tool-surface registry must contain at most 64 entries")

    surfaces: list[ToolSurface] = []
    labels: set[str] = set()
    roots: list[Path] = []
    protected = {Path("/"), resolved(home), resolved(shared)}
    for record in records:
        if not isinstance(record, dict) or set(record) != {"name", "mode", "skills_root"}:
            raise ValueError("each custom tool surface requires name, mode, and skills_root")
        label = record["name"]
        mode = record["mode"]
        raw_root = record["skills_root"]
        if not isinstance(label, str) or not TOOL_LABEL_RE.fullmatch(label):
            raise ValueError(f"invalid custom tool label: {label}")
        if label in labels:
            raise ValueError(f"duplicate custom tool label: {label}")
        if mode not in {"links", "shadows"}:
            raise ValueError(f"invalid custom tool mode for {label}: {mode}")
        if not isinstance(raw_root, str) or not raw_root.strip():
            raise ValueError(f"invalid custom tool skills_root for {label}")
        root = expand_registered_root(raw_root, home)
        if (
            not root.name.lower().endswith("skills")
            or root in protected
            or paths_overlap(root, repo)
        ):
            raise ValueError(f"unsafe custom tool skills_root for {label}: {root}")
        for existing in roots:
            if paths_overlap(root, existing):
                raise ValueError(
                    f"overlapping custom tool skills_root values: {root} and {existing}"
                )
        labels.add(label)
        roots.append(root)
        surfaces.append(ToolSurface(label=label, mode=mode, skills_root=root))
    return surfaces


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


def visible_directories(
    current: Path, directories: list[str], *, has_skill_manifest: bool
) -> tuple[list[str], list[Path]]:
    regular: list[str] = []
    links: list[Path] = []
    for directory in directories:
        if directory in DISCOVERY_EXCLUDED:
            continue
        if has_skill_manifest and directory in DISCOVERY_SUPPORT:
            continue
        candidate = current / directory
        if candidate.is_symlink():
            links.append(candidate)
        else:
            regular.append(directory)
    return regular, links


def discovered_skill_dirs(root: Path) -> list[tuple[Path, str]]:
    """Find active Skills without following directory symlinks outside root."""
    if not root.is_dir():
        return []
    manifests: set[Path] = set()
    for current_raw, directories, files in os.walk(root, followlinks=False):
        current = Path(current_raw)
        has_skill_manifest = "SKILL.md" in files
        regular, links = visible_directories(
            current, directories, has_skill_manifest=has_skill_manifest
        )
        directories[:] = regular
        for link in links:
            manifest = link / "SKILL.md"
            if manifest.is_file():
                manifests.add(manifest)
        if has_skill_manifest:
            manifests.add(current / "SKILL.md")
    found: list[tuple[Path, str]] = []
    for manifest in manifests:
        name = skill_name_from_manifest(manifest) or manifest.parent.name
        found.append((manifest.parent, name))
    return sorted(set(found), key=lambda item: (len(item[0].parts), str(item[0])))


def tree_contains_catalog_skill(
    root: Path, managed: set[str], *, visited: set[Path], budget: list[int]
) -> bool:
    target = resolved(root)
    if target in visited or not target.is_dir():
        return False
    visited.add(target)
    for current_raw, directories, files in os.walk(target, followlinks=False):
        budget[0] -= 1
        if budget[0] < 0:
            raise ValueError(
                "linked Skill collection exceeds the safe inspection limit"
            )
        current = Path(current_raw)
        has_skill_manifest = "SKILL.md" in files
        if has_skill_manifest:
            name = skill_name_from_manifest(current / "SKILL.md") or current.name
            if name in managed:
                return True
        regular, links = visible_directories(
            current, directories, has_skill_manifest=has_skill_manifest
        )
        directories[:] = regular
        for link in links:
            manifest = link / "SKILL.md"
            if manifest.is_file():
                name = skill_name_from_manifest(manifest) or link.name
                if name in managed:
                    return True
            elif tree_contains_catalog_skill(
                link, managed, visited=visited, budget=budget
            ):
                return True
    return False


def preflight_linked_collections(root: Path, names: list[str], label: str) -> None:
    """Stop before mutation if a collection link exposes a managed Skill."""
    if not root.is_dir() or root.is_symlink():
        return
    managed = set(names)
    for current_raw, directories, files in os.walk(root, followlinks=False):
        current = Path(current_raw)
        has_skill_manifest = "SKILL.md" in files
        regular, links = visible_directories(
            current, directories, has_skill_manifest=has_skill_manifest
        )
        directories[:] = regular
        for link in links:
            if (link / "SKILL.md").is_file():
                continue
            if tree_contains_catalog_skill(
                link,
                managed,
                visited=set(),
                budget=[MAX_LINK_SCAN_DIRECTORIES],
            ):
                raise ValueError(
                    f"{label} collection link exposes a managed Skill; "
                    f"manual review required: {link} -> {resolved(link)}"
                )


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

    shared_resolved = resolved(shared_root)
    skills_linked_to_authority = skills_root.is_symlink()
    if skills_linked_to_authority and resolved(skills_root) != shared_resolved:
        raise ValueError(
            "Kimi Desktop skills root is a symlink to an unverified target: "
            f"{skills_root} -> {resolved(skills_root)}"
        )

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

    if not skills_linked_to_authority:
        for name in names:
            reconciler.ensure_absent(skills_root / name, "kimi-desktop")
    else:
        reconciler.result.ok.append(
            "kimi-desktop: local skills root already links to the shared authority"
        )

    shared = str(shared_resolved)
    daimon_skills = str(resolved(skills_root))
    desired = [shared] + [item for item in current if item not in {shared, daimon_skills}]
    if daimon_skills != shared:
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

    # Parse and validate machine-local adapters before any filesystem mutation.
    custom_surfaces = load_custom_tool_surfaces(repo, home, shared)

    shadow_surfaces = (
        ToolSurface("codex", "shadows", home / ".codex/skills"),
        ToolSurface("cursor", "shadows", home / ".cursor/skills"),
        ToolSurface("kimi-code", "shadows", home / ".kimi-code/skills"),
        ToolSurface("kimi-legacy", "shadows", home / ".kimi/skills"),
        ToolSurface("opencode", "shadows", home / ".config/opencode/skills"),
        ToolSurface("roo-code", "shadows", home / ".roo/skills"),
    )
    link_surfaces = (
        ToolSurface("claude-code", "links", home / ".claude/skills"),
        ToolSurface("cline", "links", home / ".cline/skills"),
    )
    profiles_root = home / ".hermes/profiles"
    profile_surfaces = (
        tuple(
            ToolSurface(
                f"hermes-profile-{profile.name}", "shadows", profile / "skills"
            )
            for profile in profiles_root.iterdir()
            if profile.is_dir()
        )
        if profiles_root.is_dir()
        else ()
    )
    kimi_desktop_skills = (
        home
        / "Library/Application Support/kimi-desktop/daimon-share/daimon/skills"
    )
    built_in_roots = [
        resolved(surface.skills_root) for surface in (*shadow_surfaces, *link_surfaces)
    ]
    built_in_roots.extend(
        (
            resolved(shared),
            resolved(home / ".hermes/skills"),
            resolved(kimi_desktop_skills),
            *(resolved(surface.skills_root) for surface in profile_surfaces),
        )
    )
    for surface in custom_surfaces:
        for built_in in built_in_roots:
            if paths_overlap(surface.skills_root, built_in):
                raise ValueError(
                    "custom tool surface overlaps a built-in adapter: "
                    f"{surface.skills_root} and {built_in}"
                )

    authority_roots = {resolved(shared), resolved(repo / "skills")}
    authority_linked_roots: set[Path] = set()
    root_surfaces = (
        *shadow_surfaces,
        *link_surfaces,
        *profile_surfaces,
        ToolSurface("hermes", "links", home / ".hermes/skills"),
        ToolSurface("kimi-desktop", "shadows", kimi_desktop_skills),
    )
    for surface in root_surfaces:
        if not surface.skills_root.is_symlink():
            continue
        target = resolved(surface.skills_root)
        if target not in authority_roots:
            raise ValueError(
                "a built-in Skill root is a symlink to an unverified target: "
                f"{surface.skills_root} -> {target}"
            )
        authority_linked_roots.add(surface.skills_root)

    # Parse and inspect Kimi Desktop before any shared or product mutation so a
    # malformed local config cannot leave the global reconciliation half-applied.
    reconcile_kimi_desktop(
        home=home,
        shared_root=shared,
        names=names,
        reconciler=Reconciler(
            apply=False, backup_root=backup_root, result=Result.empty()
        ),
    )

    cleanup_surfaces = (
        *shadow_surfaces,
        *profile_surfaces,
        ToolSurface("hermes-nested", "shadows", home / ".hermes/skills"),
        *(surface for surface in custom_surfaces if surface.mode == "shadows"),
    )
    for surface in cleanup_surfaces:
        if surface.skills_root in authority_linked_roots:
            continue
        preflight_linked_collections(
            surface.skills_root, names, surface.label
        )

    for name in names:
        reconciler.ensure_link(shared / name, repo / "skills" / name, "shared")

    # Codex, Cursor, Kimi Code, OpenCode, Zed, and Roo Code discover the shared
    # Agent Skills root. Remove same-name higher-priority product copies.
    for surface in shadow_surfaces:
        if surface.skills_root in authority_linked_roots:
            result.ok.append(
                f"{surface.label}: root already links to the shared authority"
            )
            continue
        remove_catalog_shadows(
            root=surface.skills_root,
            names=names,
            reconciler=reconciler,
            label=surface.label,
        )

    # Products without native ~/.agents/skills discovery receive lightweight
    # per-Skill links. Cline is provisioned now so a later installation starts
    # on the same authority instead of creating a second library.
    for surface in link_surfaces:
        for name in names:
            reconciler.ensure_link(
                surface.skills_root / name, shared / name, surface.label
            )

    # Hermes recursively scans Skill roots. Remove catalog Skills hidden at any
    # depth before wiring the documented default root to the shared source.
    hermes_root = home / ".hermes/skills"
    if hermes_root not in authority_linked_roots:
        remove_catalog_shadows(
            root=hermes_root,
            names=names,
            reconciler=reconciler,
            label="hermes-nested",
            allowed_root_links=True,
        )
    for name in names:
        reconciler.ensure_link(hermes_root / name, shared / name, "hermes")
    for surface in profile_surfaces:
        if surface.skills_root not in authority_linked_roots:
            remove_catalog_shadows(
                root=surface.skills_root,
                names=names,
                reconciler=reconciler,
                label=surface.label,
            )

    for surface in custom_surfaces:
        if surface.mode == "links":
            for name in names:
                reconciler.ensure_link(
                    surface.skills_root / name, shared / name, surface.label
                )
        else:
            remove_catalog_shadows(
                root=surface.skills_root,
                names=names,
                reconciler=reconciler,
                label=surface.label,
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
    registry = home / ".config/eric-agent-skills/tool-surfaces.json"
    payload = {
        "schema_version": 1,
        "repository": str(repo),
        "remote": git(repo, "remote", "get-url", "origin"),
        "commit": git(repo, "rev-parse", "HEAD"),
        "shared_skill_root": str(resolved(home / ".agents/skills")),
        "managed_products": [
            "codex",
            "cursor",
            "kimi-code",
            "kimi-desktop",
            "claude-code",
            "hermes-agent",
            "opencode",
            "zed",
            "roo-code",
            "cline",
        ],
        "custom_tool_registry": str(registry) if registry.is_file() else None,
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
        "authority": str(repo),
        "shared_skill_root": str(resolved(home / ".agents/skills")),
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
