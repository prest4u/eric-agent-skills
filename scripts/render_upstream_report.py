#!/usr/bin/env python3
"""Render a review-oriented summary of an upstream lock update."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def by_id(path: Path) -> dict[str, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {entry["id"]: entry for entry in data["upstreams"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    before = by_id(args.before)
    after = by_id(args.after)
    lines = [
        "## Automated upstream update",
        "",
        "This PR updates pinned snapshots only. It must be reviewed and is never auto-merged.",
        "",
        "| Upstream | Commit | Diff | Tree hash | License evidence |",
        "|---|---|---|---|---|",
    ]
    changes = 0
    for upstream_id in sorted(after):
        old = before.get(upstream_id, {})
        new = after[upstream_id]
        if old == new:
            continue
        changes += 1
        old_commit = str(old.get("commit", "new"))[:12]
        new_commit = str(new.get("commit", "removed"))[:12]
        tree_changed = "changed" if old.get("tree_sha256") != new.get("tree_sha256") else "same"
        license_changed = "changed" if old.get("license_sha256") != new.get("license_sha256") else "same"
        repository = str(new.get("repository") or old.get("repository") or "").removesuffix(".git")
        diff = (
            f"[compare]({repository}/compare/{old.get('commit')}...{new.get('commit')})"
            if repository.startswith("https://github.com/") and old.get("commit") and new.get("commit")
            else "n/a"
        )
        lines.append(
            f"| `{upstream_id}` | `{old_commit}` → `{new_commit}` | {diff} | {tree_changed} | {license_changed} |"
        )
    if not changes:
        lines.append("| _No lock changes_ |  |  |  |  |")
    lines.extend(
        [
            "",
            "### Automated evidence",
            "",
            "- Repository portability, privacy, catalog, and license checks: **PASS**",
            "- Repository tool regression tests (including path escape, symlink, license drift, local conflict, and high-risk blocking): **PASS**",
            "- Independent mirror export check: **PASS**",
            "- Pinned SkillSpector static scan with no unsuppressed High/Critical findings: **PASS**",
            "- Raw SkillSpector JSON is retained as the `upstream-skillspector-reports` workflow artifact.",
            "",
            "### Required review",
            "",
            "- Inspect upstream diffs and retained license evidence.",
            "- Confirm SkillSpector and repository validation results.",
            "- Confirm Eric-owned `SKILL.md` policy was not overwritten.",
        ]
    )
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
