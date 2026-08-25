#!/usr/bin/env python3
"""Register an additional agent product Skill root for the shared sync."""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from pathlib import Path


SCHEMA_VERSION = 1
LABEL_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MODES = ("links", "shadows")
MAX_SURFACES = 64


def default_registry(home: Path) -> Path:
    return home / ".config/eric-agent-skills/tool-surfaces.json"


def is_authority_repo(path: Path) -> bool:
    return all(
        candidate.is_file()
        for candidate in (
            path / "catalog/skills.yaml",
            path / "scripts/sync_user_install.py",
            path / "skills/eric-catalog/SKILL.md",
        )
    )


def discover_authority_repo(home: Path, explicit: Path | None = None) -> Path:
    if explicit is not None:
        candidate = explicit.expanduser().resolve(strict=False)
        if not is_authority_repo(candidate):
            raise ValueError(f"not an Eric Skill authority checkout: {candidate}")
        return candidate

    state = home / ".local/state/eric-agent-skills/status.json"
    if state.is_file():
        data = json.loads(state.read_text(encoding="utf-8"))
        repository = data.get("repository") if isinstance(data, dict) else None
        if isinstance(repository, str):
            candidate = Path(repository).expanduser().resolve(strict=False)
            if is_authority_repo(candidate):
                return candidate

    packaged = Path(__file__).resolve().parents[3]
    if is_authority_repo(packaged):
        return packaged
    raise ValueError(
        "cannot locate the Eric Skill authority checkout; pass --repo explicitly"
    )


def paths_overlap(left: Path, right: Path) -> bool:
    left = left.expanduser().resolve(strict=False)
    right = right.expanduser().resolve(strict=False)
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


def contains_path(container: Path, candidate: Path) -> bool:
    try:
        candidate.expanduser().resolve(strict=False).relative_to(
            container.expanduser().resolve(strict=False)
        )
        return True
    except ValueError:
        return False


def normalize_root(raw: str, home: Path, repo: Path) -> Path:
    if raw == "~":
        path = home
    elif raw.startswith("~/"):
        path = home / raw[2:]
    else:
        path = Path(raw)
    if not path.is_absolute():
        raise ValueError("skills root must be absolute or start with ~/")
    root = path.expanduser().resolve(strict=False)
    if (
        not root.name.lower().endswith("skills")
        or contains_path(root, home)
        or paths_overlap(root, home / ".agents/skills")
        or paths_overlap(root, repo)
    ):
        raise ValueError(
            "refusing an unsafe, non-Skill, or already-managed skills root"
        )
    return root


def load_registry(path: Path) -> dict:
    if not path.exists():
        return {"schema_version": SCHEMA_VERSION, "surfaces": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported tool-surface registry schema")
    surfaces = data.get("surfaces")
    if not isinstance(surfaces, list) or len(surfaces) > MAX_SURFACES:
        raise ValueError(
            f"tool-surface registry must contain at most {MAX_SURFACES} entries"
        )
    names: set[str] = set()
    roots: set[str] = set()
    for item in surfaces:
        if not isinstance(item, dict) or set(item) != {
            "name",
            "mode",
            "skills_root",
        }:
            raise ValueError(
                "each tool surface requires name, mode, and skills_root"
            )
        name = item["name"]
        mode = item["mode"]
        root = item["skills_root"]
        if not isinstance(name, str) or not LABEL_RE.fullmatch(name):
            raise ValueError(f"invalid registered tool name: {name}")
        if mode not in MODES:
            raise ValueError(f"invalid registered mode for {name}: {mode}")
        if not isinstance(root, str) or not root:
            raise ValueError(f"invalid registered skills root for {name}")
        if name in names or root in roots:
            raise ValueError("duplicate registered tool name or skills root")
        names.add(name)
        roots.add(root)
    return data


def save_registry(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        handle.write(payload)
        temporary = Path(handle.name)
    os.chmod(temporary, 0o600)
    os.replace(temporary, path)


def register_surface(
    *,
    registry: Path,
    name: str,
    mode: str,
    skills_root: str,
    home: Path,
    repo: Path,
) -> dict:
    if not LABEL_RE.fullmatch(name):
        raise ValueError("tool name must be lowercase kebab-case")
    if mode not in MODES:
        raise ValueError(f"mode must be one of: {', '.join(MODES)}")
    root = normalize_root(skills_root, home, repo)
    data = load_registry(registry)
    surfaces = [item for item in data["surfaces"] if item["name"] != name]
    for item in surfaces:
        existing = Path(item["skills_root"])
        if paths_overlap(root, existing):
            raise ValueError(
                f"skills root overlaps registered tool {item['name']}: {existing}"
            )
    surfaces.append({"name": name, "mode": mode, "skills_root": str(root)})
    if len(surfaces) > MAX_SURFACES:
        raise ValueError(f"at most {MAX_SURFACES} tool surfaces may be registered")
    data["surfaces"] = sorted(surfaces, key=lambda item: item["name"])
    save_registry(registry, data)
    return data


def remove_surface(*, registry: Path, name: str) -> dict:
    if not LABEL_RE.fullmatch(name):
        raise ValueError("tool name must be lowercase kebab-case")
    data = load_registry(registry)
    data["surfaces"] = [
        item
        for item in data["surfaces"]
        if isinstance(item, dict) and item.get("name") != name
    ]
    save_registry(registry, data)
    return data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="Stable lowercase tool label")
    parser.add_argument("--mode", choices=MODES)
    parser.add_argument("--skills-root")
    parser.add_argument("--remove", action="store_true")
    parser.add_argument("--registry", type=Path)
    parser.add_argument("--repo", type=Path, help="Eric Skill authority checkout")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    home = Path.home().resolve()
    repo = discover_authority_repo(home, args.repo)
    registry = (args.registry or default_registry(home)).expanduser().resolve()
    if args.remove:
        data = remove_surface(registry=registry, name=args.name)
    else:
        if not args.mode or not args.skills_root:
            raise ValueError("--mode and --skills-root are required unless --remove is used")
        data = register_surface(
            registry=registry,
            name=args.name,
            mode=args.mode,
            skills_root=args.skills_root,
            home=home,
            repo=repo,
        )
    print(json.dumps({"registry": str(registry), **data}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"registration failed: {exc}")
        raise SystemExit(2)
