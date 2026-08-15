#!/usr/bin/env python3
"""Push guarded mirror updates without force-pushing or bootstrapping."""

from __future__ import annotations

import argparse
import importlib.util
import os
import subprocess
import tempfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


def load_script(filename: str):
    path = REPO / "scripts" / filename
    spec = importlib.util.spec_from_file_location(filename.removesuffix(".py"), path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


EXPORT = load_script("export_mirrors.py")
APPLY = load_script("apply_mirror.py")


def run(command: list[str], cwd: Path | None = None, *, capture: bool = False) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
    )
    return result.stdout.strip() if capture else ""


def remote_tag_target(output: str, tag: str) -> str | None:
    refs: dict[str, str] = {}
    for line in output.splitlines():
        fields = line.split()
        if len(fields) == 2:
            refs[fields[1]] = fields[0]
    peeled = refs.get(f"refs/tags/{tag}^{{}}")
    return peeled or refs.get(f"refs/tags/{tag}")


def assert_remote_tag_matches(output: str, tag: str, expected_commit: str) -> bool:
    target = remote_tag_target(output, tag)
    if target is None:
        return False
    if target != expected_commit:
        raise ValueError(
            f"remote tag {tag} points to {target}, expected {expected_commit}; refusing to move it"
        )
    return True


def push_one(repo: Path, record: dict, workspace: Path, *, dry_run: bool) -> None:
    mirror_name = record["mirror"].split("/")[-1]
    generated = workspace / "generated" / mirror_name
    checkout = workspace / "checkout" / mirror_name
    EXPORT.export_one(repo, record, generated)
    run(["gh", "repo", "clone", record["mirror"], str(checkout), "--", "--depth=1", "--branch=main"])
    APPLY.apply(generated, checkout)
    status = run(["git", "status", "--porcelain"], checkout, capture=True)
    if status:
        run(["git", "config", "user.name", "github-actions[bot]"], checkout)
        run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], checkout)
        run(["git", "add", "--all"], checkout)
        run(["git", "commit", "-m", f"sync: {record['name']} {record['version']}"], checkout)
    tag = f"v{record['version']}"
    expected_commit = run(["git", "rev-parse", "HEAD"], checkout, capture=True)
    remote_tag = run(
        [
            "git",
            "ls-remote",
            "--tags",
            "origin",
            f"refs/tags/{tag}",
            f"refs/tags/{tag}^{{}}",
        ],
        checkout,
        capture=True,
    )
    exists = assert_remote_tag_matches(remote_tag, tag, expected_commit)
    if dry_run:
        if status:
            print(f"DRY RUN {record['mirror']}: local candidate created from:\n{status}")
        if not exists:
            print(f"DRY RUN {record['mirror']}: would create {tag} at {expected_commit}")
        else:
            print(f"DRY RUN {record['mirror']}: verified {tag} at {expected_commit}")
        return

    refspecs: list[str] = []
    if status:
        refspecs.append("HEAD:main")
    if not exists:
        run(["git", "tag", tag], checkout)
        refspecs.append(f"refs/tags/{tag}:refs/tags/{tag}")
    if refspecs:
        run(["git", "push", "--atomic", "origin", *refspecs], checkout)
    print(f"Synced {record['mirror']} at verified {tag} ({expected_commit})")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=REPO)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not os.environ.get("GH_TOKEN"):
        parser.error("GH_TOKEN is required")
    repo = args.repo.resolve()
    records = EXPORT.mirror_records(repo)
    if len(records) != 18:
        raise SystemExit("catalog must define exactly 18 mirrors")
    with tempfile.TemporaryDirectory(prefix="eric-mirror-push-") as temp:
        workspace = Path(temp)
        for record in records:
            push_one(repo, record, workspace, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
