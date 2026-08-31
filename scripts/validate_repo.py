#!/usr/bin/env python3
"""Validate the public Eric Agent Skills repository without executing skills."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import yaml


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
SECRET_RE = re.compile(
    r"(?i)(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|client[_-]?secret)"
    r"[ \t]*[:=][ \t]*['\"](?!\$|<|example|test|fake|redacted)[^'\"\r\n]{8,}['\"]"
)
PRIVATE_MARKERS = (
    "/Users/eric",
    "C:/Users/eric",
    "李梓硕",
)
PORTABILITY_MARKERS = (
    "~/.codex/skills",
    "~/.agents/skills",
    "/Users/eric",
    "C:/Users/eric",
)
TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".py",
    ".js",
    ".mjs",
    ".ts",
    ".tsx",
    ".html",
    ".css",
    ".typ",
    ".toml",
}
SKIP_TEXT_PARTS = {"references/upstream", "editor/neo-ppt/assets"}


@dataclass(frozen=True)
class Issue:
    code: str
    path: str
    message: str


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected YAML mapping: {path}")
    return data


def parse_skill_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing opening frontmatter delimiter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("missing closing frontmatter delimiter")
    metadata = yaml.safe_load(text[4:end])
    if not isinstance(metadata, dict):
        raise ValueError("frontmatter must be a mapping")
    return metadata, text[end + 5 :]


def iter_text_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        relative = path.relative_to(root).as_posix()
        if any(part in relative for part in SKIP_TEXT_PARTS):
            continue
        yield path


def validate_markdown_links(path: Path, repo: Path) -> list[Issue]:
    issues: list[Issue] = []
    text = path.read_text(encoding="utf-8")
    for raw_target in MARKDOWN_LINK_RE.findall(text):
        target = raw_target.strip().split("#", 1)[0]
        if not target or target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = target.split(" ", 1)[0].strip("<>")
        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(repo.resolve())
        except ValueError:
            issues.append(Issue("LINK_ESCAPE", str(path.relative_to(repo)), raw_target))
            continue
        if not resolved.exists():
            issues.append(Issue("BROKEN_LINK", str(path.relative_to(repo)), raw_target))
    return issues


def git_tracked_relative_paths(repo: Path) -> set[str] | None:
    if not (repo / ".git").exists():
        return None
    try:
        output = subprocess.check_output(
            ["git", "-C", str(repo), "ls-files", "-z"],
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return {item.decode() for item in output.split(b"\0") if item}


def is_published_bytecode(relative: str, tracked: set[str] | None) -> bool:
    if tracked is None:
        return True
    if relative in tracked:
        return True
    prefix = relative.rstrip("/") + "/"
    return any(item.startswith(prefix) for item in tracked)


def snapshot_tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file()):
        relative = path.relative_to(root).as_posix()
        if relative == "_SOURCE.md":
            continue
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def validate_upstream_snapshots(repo: Path, upstream_entries: list, names: list[str]) -> list[Issue]:
    repo = repo.resolve()
    issues: list[Issue] = []
    expected_snapshots: set[Path] = set()
    vendored_targets: set[str] = set()
    for entry in upstream_entries:
        if not isinstance(entry, dict):
            issues.append(Issue("UPSTREAM_ENTRY", "catalog/upstreams.lock.json", "entry must be an object"))
            continue
        entry_id = entry.get("id")
        if not isinstance(entry_id, str) or not NAME_RE.fullmatch(entry_id):
            issues.append(Issue("UPSTREAM_ID", "catalog/upstreams.lock.json", str(entry_id)))
            continue
        targets = entry.get("targets")
        if not isinstance(targets, list) or any(not isinstance(target, str) for target in targets):
            issues.append(Issue("UPSTREAM_TARGETS", "catalog/upstreams.lock.json", entry_id))
            continue
        for target in targets:
            if target not in names:
                issues.append(Issue("UPSTREAM_TARGET", "catalog/upstreams.lock.json", f"{entry_id}: {target}"))
        if entry.get("mode") != "vendored-reference":
            continue
        expected_hash = entry.get("tree_sha256")
        if not isinstance(expected_hash, str) or not re.fullmatch(r"[a-f0-9]{64}", expected_hash):
            issues.append(Issue("UPSTREAM_TREE_HASH", "catalog/upstreams.lock.json", entry_id))
            continue
        for target in targets:
            if target not in names:
                continue
            vendored_targets.add(target)
            managed_root = (repo / "skills" / target / "references" / "upstream").resolve()
            snapshot = (managed_root / entry_id).resolve()
            try:
                snapshot.relative_to(managed_root)
            except ValueError:
                issues.append(Issue("UPSTREAM_PATH_ESCAPE", "catalog/upstreams.lock.json", f"{entry_id}: {target}"))
                continue
            expected_snapshots.add(snapshot)
            relative = snapshot.relative_to(repo).as_posix()
            if not snapshot.is_dir():
                issues.append(Issue("UPSTREAM_SNAPSHOT_MISSING", relative, entry_id))
                continue
            if any(path.is_symlink() for path in snapshot.rglob("*")):
                issues.append(Issue("UPSTREAM_SNAPSHOT_SYMLINK", relative, entry_id))
                continue
            actual_hash = snapshot_tree_hash(snapshot)
            if actual_hash != expected_hash:
                issues.append(Issue("UPSTREAM_SNAPSHOT_DRIFT", relative, f"expected {expected_hash}, found {actual_hash}"))
            source_note = snapshot / "_SOURCE.md"
            note = source_note.read_text(encoding="utf-8") if source_note.is_file() else ""
            for required in (entry.get("repository"), entry.get("commit"), entry.get("license")):
                if not isinstance(required, str) or required not in note:
                    issues.append(Issue("UPSTREAM_SOURCE_NOTE", relative, f"missing {required!r}"))

    for skill_name in names:
        managed_root = repo / "skills" / skill_name / "references" / "upstream"
        if not managed_root.is_dir():
            continue
        for child in managed_root.iterdir():
            if child.is_dir() and child.resolve() not in expected_snapshots:
                issues.append(Issue("UPSTREAM_ORPHAN_SNAPSHOT", child.relative_to(repo).as_posix(), "not declared in lock"))
    for target in sorted(vendored_targets):
        notice = repo / "skills" / target / "THIRD_PARTY_NOTICES.md"
        text = notice.read_text(encoding="utf-8") if notice.is_file() else ""
        if "MIT License" not in text or "Permission is hereby granted" not in text:
            issues.append(
                Issue(
                    "UPSTREAM_LICENSE_NOTICE",
                    notice.relative_to(repo).as_posix(),
                    "vendored Skill must carry the applicable license text",
                )
            )
    return issues


def validate(repo: Path, only_skill: str | None = None) -> list[Issue]:
    issues: list[Issue] = []
    skills_catalog = load_yaml(repo / "catalog" / "skills.yaml")
    collections = load_yaml(repo / "catalog" / "collections.yaml")
    lock = json.loads((repo / "catalog" / "upstreams.lock.json").read_text(encoding="utf-8"))

    records = skills_catalog.get("skills", [])
    if not isinstance(records, list):
        return [Issue("CATALOG_SHAPE", "catalog/skills.yaml", "skills must be a list")]
    names = [record.get("name") for record in records if isinstance(record, dict)]
    if len(names) != 64 or len(set(names)) != 64:
        issues.append(Issue("CORE_COUNT", "catalog/skills.yaml", f"expected 64 unique skills, found {len(set(names))}"))

    actual_names = sorted(path.name for path in (repo / "skills").iterdir() if path.is_dir())
    if sorted(names) != actual_names:
        issues.append(Issue("CATALOG_DIRECTORY_DRIFT", "skills", "catalog names and skill directories differ"))
    for record in records:
        if not isinstance(record, dict):
            continue
        version = record.get("version")
        if not isinstance(version, str) or not SEMVER_RE.fullmatch(version):
            issues.append(Issue("CATALOG_VERSION", "catalog/skills.yaml", f"{record.get('name')}: {version}"))

    collection_names: list[str] = []
    for value in collections.get("collections", {}).values():
        if isinstance(value, dict):
            collection_names.extend(value.get("skills", []))
    if sorted(collection_names) != sorted(names):
        issues.append(Issue("COLLECTION_COVERAGE", "catalog/collections.yaml", "each core skill must appear in exactly one collection"))

    mirror_records = [record for record in records if record.get("mirror")]
    mirrors = [record["mirror"] for record in mirror_records]
    if len(mirrors) != 18 or len(set(mirrors)) != 18:
        issues.append(Issue("MIRROR_COUNT", "catalog/skills.yaml", f"expected 18 unique mirrors, found {len(set(mirrors))}"))

    upstream_entries = lock.get("upstreams", [])
    if not isinstance(upstream_entries, list):
        issues.append(Issue("UPSTREAM_LOCK_SHAPE", "catalog/upstreams.lock.json", "upstreams must be a list"))
        upstream_entries = []
    upstream_ids = {entry.get("id") for entry in upstream_entries if isinstance(entry, dict)}
    for record in records:
        for upstream in record.get("upstreams", []):
            if upstream not in upstream_ids:
                issues.append(Issue("UNKNOWN_UPSTREAM", "catalog/skills.yaml", f"{record['name']}: {upstream}"))

    issues.extend(validate_upstream_snapshots(repo, upstream_entries, names))

    selected = [only_skill] if only_skill else names
    tracked = git_tracked_relative_paths(repo)
    for name in selected:
        if name not in names:
            issues.append(Issue("UNKNOWN_SKILL", "catalog/skills.yaml", str(name)))
            continue
        skill_dir = repo / "skills" / name
        skill_md = skill_dir / "SKILL.md"
        try:
            metadata, body = parse_skill_frontmatter(skill_md)
        except (OSError, ValueError, yaml.YAMLError) as exc:
            issues.append(Issue("FRONTMATTER", str(skill_md.relative_to(repo)), str(exc)))
            continue
        if set(metadata) != {"name", "description"}:
            issues.append(Issue("FRONTMATTER_KEYS", str(skill_md.relative_to(repo)), f"found {sorted(metadata)}"))
        if metadata.get("name") != name or not NAME_RE.fullmatch(str(metadata.get("name", ""))):
            issues.append(Issue("SKILL_NAME", str(skill_md.relative_to(repo)), str(metadata.get("name"))))
        description = metadata.get("description")
        if not isinstance(description, str) or not description.strip() or len(description) > 1024:
            issues.append(Issue("DESCRIPTION", str(skill_md.relative_to(repo)), "description must contain 1-1024 characters"))
        elif name.startswith("eric-") and not re.match(r"^[【\u4e00-\u9fff]", description.lstrip()):
            issues.append(Issue("ERIC_CHINESE_ENTRY", str(skill_md.relative_to(repo)), "Eric Skill descriptions must begin with a Chinese label or Chinese text"))
        if len(skill_md.read_text(encoding="utf-8").splitlines()) > 500:
            issues.append(Issue("SKILL_LENGTH", str(skill_md.relative_to(repo)), "SKILL.md exceeds 500 lines"))
        if (skill_dir / "README.md").exists():
            issues.append(Issue("EXTRANEOUS_README", str((skill_dir / "README.md").relative_to(repo)), "move user documentation to docs/skills"))
        for path in skill_dir.rglob("*"):
            relative = path.relative_to(repo).as_posix()
            if path.is_symlink():
                issues.append(Issue("SYMLINK", relative, "published skills must be copy-safe"))
            if path.is_dir() and path.name == ".git":
                issues.append(Issue("NESTED_GIT", relative, "nested repository"))
            if path.is_dir() and path.name == "__pycache__" and is_published_bytecode(relative, tracked):
                issues.append(Issue("PYTHON_BYTECODE", relative, "generated Python cache directory"))
            if path.is_file():
                if path.suffix.lower() in {".pyc", ".pyo"} and is_published_bytecode(relative, tracked):
                    issues.append(Issue("PYTHON_BYTECODE", relative, "generated Python bytecode"))
                if " 2." in path.name:
                    issues.append(Issue("FINDER_DUPLICATE", relative, "duplicate filename"))
                if path.stat().st_size > 25 * 1024 * 1024:
                    issues.append(Issue("LARGE_FILE", relative, f"{path.stat().st_size} bytes"))
        for path in iter_text_files(skill_dir):
            relative = path.relative_to(repo).as_posix()
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for marker in PRIVATE_MARKERS:
                if marker in text:
                    issues.append(Issue("PRIVATE_MARKER", relative, marker))
            if path.suffix.lower() == ".md":
                for marker in PORTABILITY_MARKERS:
                    if marker in text:
                        issues.append(Issue("NONPORTABLE_PATH", relative, marker))
                issues.extend(validate_markdown_links(path, repo))
            if SECRET_RE.search(text):
                issues.append(Issue("POSSIBLE_SECRET", relative, "credential-like assignment"))

    baseline_dir = repo / "security" / "skillspector-baselines"
    for baseline in sorted(baseline_dir.glob("*.yaml")):
        relative = baseline.relative_to(repo).as_posix()
        if baseline.stem not in names:
            issues.append(Issue("BASELINE_UNKNOWN_SKILL", relative, baseline.stem))
        try:
            data = load_yaml(baseline)
        except (OSError, ValueError, yaml.YAMLError) as exc:
            issues.append(Issue("BASELINE_FORMAT", relative, str(exc)))
            continue
        if data.get("version") != 2 or data.get("scanner_version") != "2.9.4":
            issues.append(Issue("BASELINE_VERSION", relative, "expected SkillSpector baseline v2 from scanner 2.9.4"))
        if data.get("rules") != []:
            issues.append(Issue("BASELINE_GLOB_RULE", relative, "only exact content-bound fingerprints are permitted"))
        fingerprints = data.get("fingerprints")
        if not isinstance(fingerprints, list) or not fingerprints:
            issues.append(Issue("BASELINE_FINGERPRINTS", relative, "non-empty fingerprint list required"))
            continue
        seen: set[tuple[str, str, str]] = set()
        for item in fingerprints:
            if not isinstance(item, dict):
                issues.append(Issue("BASELINE_FINGERPRINT", relative, "fingerprint entry must be a mapping"))
                continue
            key = (str(item.get("hash", "")), str(item.get("rule_id", "")), str(item.get("file", "")))
            if not key[0].startswith("sha256:") or not key[1] or not key[2]:
                issues.append(Issue("BASELINE_FINGERPRINT", relative, f"invalid fingerprint {key}"))
            if key in seen:
                issues.append(Issue("BASELINE_DUPLICATE", relative, f"duplicate fingerprint {key}"))
            seen.add(key)
            candidate = (repo / "skills" / baseline.stem / key[2]).resolve()
            try:
                candidate.relative_to((repo / "skills" / baseline.stem).resolve())
            except ValueError:
                issues.append(Issue("BASELINE_PATH_ESCAPE", relative, key[2]))

    manifest_data: dict[Path, dict] = {}
    for manifest in (
        repo / ".codex-plugin" / "plugin.json",
        repo / ".claude-plugin" / "marketplace.json",
        repo / "kimi.plugin.json",
    ):
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("manifest root must be an object")
            manifest_data[manifest] = data
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            issues.append(Issue("MANIFEST_JSON", str(manifest.relative_to(repo)), str(exc)))

    if len(manifest_data) == 3:
        versions = {data.get("version") for data in manifest_data.values()}
        if len(versions) != 1 or not all(isinstance(version, str) and SEMVER_RE.fullmatch(version) for version in versions):
            issues.append(Issue("MANIFEST_VERSION_DRIFT", "plugin manifests", f"found {sorted(str(version) for version in versions)}"))
        marketplace = manifest_data[repo / ".claude-plugin" / "marketplace.json"]
        marketplace_names: list[str] = []
        for plugin in marketplace.get("plugins", []):
            if not isinstance(plugin, dict):
                continue
            for skill_path in plugin.get("skills", []):
                if isinstance(skill_path, str):
                    marketplace_names.append(Path(skill_path).name)
        if sorted(marketplace_names) != sorted(names):
            issues.append(Issue("MARKETPLACE_COVERAGE", ".claude-plugin/marketplace.json", "each catalog Skill must appear exactly once"))

    public_docs = [
        repo / "README.md",
        repo / "README.zh-CN.md",
        repo / "THIRD_PARTY_NOTICES.md",
        repo / "security" / "README.md",
        *sorted((repo / "docs").rglob("*.md")),
    ]
    for path in public_docs:
        if path.is_file():
            issues.extend(validate_markdown_links(path, repo))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--skill")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    issues = validate(args.repo.resolve(), args.skill)
    if args.json:
        print(json.dumps({"ok": not issues, "issues": [asdict(issue) for issue in issues]}, ensure_ascii=False, indent=2))
    elif issues:
        for issue in issues:
            print(f"{issue.code}: {issue.path}: {issue.message}")
    else:
        print("Repository validation passed.")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
