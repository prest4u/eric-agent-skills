#!/usr/bin/env python3
"""Apply a generated mirror tree after verifying the remote managed state."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_target(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"managed path escapes mirror root: {relative}") from exc
    return path


def worktree_files(root: Path) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for path in root.rglob("*"):
        relative_path = path.relative_to(root)
        if relative_path.parts and relative_path.parts[0] == ".git":
            continue
        if path.is_symlink():
            raise ValueError(f"mirror symlink is not allowed: {relative_path.as_posix()}")
        if path.is_file():
            files[relative_path.as_posix()] = path
    return files


def verify_existing(checkout: Path) -> dict | None:
    manifest_path = checkout / ".mirror-manifest.json"
    if not manifest_path.exists():
        return None
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    managed = manifest.get("managed_files")
    if not isinstance(managed, dict):
        raise ValueError("mirror manifest managed_files must be an object")
    actual_files = worktree_files(checkout)
    expected_files = set(managed) | {".mirror-manifest.json"}
    actual_names = set(actual_files)
    unmanaged = sorted(actual_names - expected_files)
    missing = sorted(expected_files - actual_names)
    if unmanaged:
        raise ValueError(f"unmanaged mirror files detected: {', '.join(unmanaged)}")
    if missing:
        raise ValueError(f"managed mirror files missing: {', '.join(missing)}")
    for relative, expected in managed.items():
        path = safe_target(checkout, relative)
        if not path.is_file() or sha256(path) != expected:
            raise ValueError(f"mirror drift detected: {relative}")
    return manifest


def apply(generated: Path, checkout: Path, *, bootstrap: bool = False) -> None:
    generated_manifest = verify_existing(generated)
    if generated_manifest is None:
        raise ValueError("generated mirror is missing .mirror-manifest.json")
    current = verify_existing(checkout)
    if current is None and not bootstrap:
        raise ValueError("mirror is not bootstrapped; rerun with --bootstrap after reviewing the diff")
    if current and current.get("skill") != generated_manifest.get("skill"):
        raise ValueError("mirror skill identity mismatch")
    if current or bootstrap:
        for path in worktree_files(checkout).values():
            path.unlink()
    for source in sorted(path for path in generated.rglob("*") if path.is_file()):
        relative = source.relative_to(generated)
        target = safe_target(checkout, relative.as_posix())
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    for directory in sorted(
        (path for path in checkout.rglob("*") if path.is_dir() and path.name != ".git"),
        key=lambda item: len(item.parts),
        reverse=True,
    ):
        try:
            directory.rmdir()
        except OSError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", type=Path, required=True)
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--bootstrap", action="store_true")
    args = parser.parse_args()
    apply(args.generated.resolve(), args.checkout.resolve(), bootstrap=args.bootstrap)
    print(f"Applied {args.generated} to {args.checkout}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
