#!/usr/bin/env python3
"""Export independently installable, guarded mirror working trees."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import yaml


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_commit(repo: Path) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:
        return "WORKTREE"


def export_one(repo: Path, record: dict, output: Path) -> None:
    skill = repo / "skills" / record["name"]
    if not skill.is_dir():
        raise ValueError(f"missing skill: {record['name']}")
    if output.exists():
        shutil.rmtree(output)
    shutil.copytree(skill, output)
    root_license = repo / "LICENSE"
    if not (output / "LICENSE").exists():
        shutil.copy2(root_license, output / "LICENSE")
    root_notices = repo / "THIRD_PARTY_NOTICES.md"
    if not (output / "THIRD_PARTY_NOTICES.md").exists():
        shutil.copy2(root_notices, output / "THIRD_PARTY_NOTICES.md")
    readme = (
        f"# {record['name']}\n\n"
        "This repository is a generated, independently installable mirror.\n\n"
        "Canonical source: https://github.com/prest4u/eric-agent-skills\n\n"
        "Do not edit generated skill files here. Submit changes to the canonical repository first.\n"
    )
    (output / "README.md").write_text(readme, encoding="utf-8")
    managed = {
        path.relative_to(output).as_posix(): sha256(path)
        for path in sorted(p for p in output.rglob("*") if p.is_file())
        if path.name != ".mirror-manifest.json"
    }
    manifest = {
        "schema_version": 1,
        "canonical_repository": "prest4u/eric-agent-skills",
        "skill": record["name"],
        "version": record["version"],
        "source_commit": source_commit(repo),
        "managed_files": managed,
    }
    (output / ".mirror-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def mirror_records(repo: Path) -> list[dict]:
    catalog = yaml.safe_load((repo / "catalog" / "skills.yaml").read_text(encoding="utf-8"))
    return [record for record in catalog["skills"] if record.get("mirror")]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--skill")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()
    repo = args.repo.resolve()
    records = mirror_records(repo)
    if len(records) != 18 or len({record["mirror"] for record in records}) != 18:
        raise SystemExit("catalog must define exactly 18 unique mirrors")
    if args.skill:
        records = [record for record in records if record["name"] == args.skill]
        if not records:
            raise SystemExit(f"skill has no mirror: {args.skill}")
    if args.list:
        for record in records:
            print(f"{record['name']}\t{record['mirror']}")
        return 0
    if args.check:
        with tempfile.TemporaryDirectory(prefix="eric-mirrors-") as temp:
            for record in records:
                export_one(repo, record, Path(temp) / record["mirror"].split("/")[-1])
        print(f"Mirror export check passed for {len(records)} skills.")
        return 0
    if args.output is None:
        parser.error("--output is required unless --check is used")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    for record in records:
        export_one(repo, record, output / record["mirror"].split("/")[-1])
    print(f"Exported {len(records)} mirrors to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
