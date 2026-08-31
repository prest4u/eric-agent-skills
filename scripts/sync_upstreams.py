#!/usr/bin/env python3
"""Check or update pinned upstream reference snapshots.

Only references/upstream/<id>/ is machine-owned. Local skill policy is never
rewritten by this script.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


IDENTIFIER_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LICENSE_FILE_NAMES = {
    "license",
    "license.md",
    "licence",
    "licence.md",
    "copying",
}
LICENSE_HEADING_RE = re.compile(r"^#{1,3}\s+license\s*$", re.IGNORECASE)
NEXT_HEADING_RE = re.compile(r"^#{1,3}\s+\S")


def license_evidence_bytes(raw: bytes, evidence_path: str) -> bytes:
    """Hash a LICENSE file whole; for README evidence, pin only the License section."""
    name = Path(evidence_path).name.lower()
    if name in LICENSE_FILE_NAMES:
        return raw
    text = raw.decode("utf-8", errors="replace")
    lines = text.splitlines()
    start = next((index for index, line in enumerate(lines) if LICENSE_HEADING_RE.fullmatch(line)), None)
    if start is None:
        return raw
    end = next(
        (index for index in range(start + 1, len(lines)) if NEXT_HEADING_RE.match(lines[index])),
        len(lines),
    )
    return ("\n".join(lines[start:end]).strip() + "\n").encode("utf-8")


def repository_key(url: str) -> str:
    value = url.removesuffix(".git").rstrip("/")
    return "/".join(value.split("/")[-2:])


def tree_hash(root: Path, *, exclude_source_note: bool = False) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        relative = path.relative_to(root).as_posix()
        if exclude_source_note and relative == "_SOURCE.md":
            continue
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def snapshot_destination(repo: Path, entry_id: str, target: str) -> Path:
    """Resolve one machine-managed destination without trusting lock values."""
    if not IDENTIFIER_RE.fullmatch(entry_id):
        raise ValueError(f"invalid upstream id: {entry_id}")
    if not IDENTIFIER_RE.fullmatch(target):
        raise ValueError(f"invalid upstream target: {target}")
    skill_root = (repo / "skills" / target).resolve()
    skills_root = (repo / "skills").resolve()
    try:
        skill_root.relative_to(skills_root)
    except ValueError as exc:
        raise ValueError(f"upstream target escapes skills root: {target}") from exc
    if not skill_root.is_dir():
        raise ValueError(f"unknown upstream target skill: {target}")
    managed_root = (skill_root / "references" / "upstream").resolve()
    destination = (managed_root / entry_id).resolve()
    try:
        destination.relative_to(managed_root)
    except ValueError as exc:
        raise ValueError(f"upstream destination escapes managed root: {entry_id}") from exc
    return destination


def assert_safe_tree(root: Path) -> None:
    if not root.is_dir():
        raise ValueError(f"missing upstream path: {root}")
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"upstream symlink is not allowed: {path}")
        if path.is_file() and path.stat().st_size > 25 * 1024 * 1024:
            raise ValueError(f"upstream file exceeds 25 MiB: {path}")


def remove_identical_finder_duplicates(root: Path) -> None:
    """Remove only Finder-style copies whose canonical sibling is identical."""
    for duplicate in sorted(root.rglob("* 2.*")):
        canonical = duplicate.with_name(duplicate.name.replace(" 2.", "."))
        if not duplicate.is_file() or not canonical.is_file():
            raise ValueError(f"unresolved Finder duplicate: {duplicate}")
        if hashlib.sha256(duplicate.read_bytes()).digest() != hashlib.sha256(canonical.read_bytes()).digest():
            raise ValueError(f"divergent Finder duplicate requires review: {duplicate}")
        duplicate.unlink()


def clone_repository(url: str, destination: Path) -> Path:
    subprocess.run(["git", "clone", "--depth", "1", url, str(destination)], check=True)
    return destination


def head(path: Path) -> str:
    return subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()


def verify_license(checkout: Path, entry: dict) -> str | None:
    evidence = entry.get("license_evidence_path")
    if not evidence:
        return None
    evidence_path = (checkout / evidence).resolve()
    try:
        evidence_path.relative_to(checkout.resolve())
    except ValueError as exc:
        raise ValueError(f"license evidence escapes checkout: {evidence_path}") from exc
    if not evidence_path.is_file():
        raise ValueError(f"license evidence is missing: {evidence_path}")
    license_bytes = license_evidence_bytes(evidence_path.read_bytes(), evidence)
    license_text = license_bytes.decode("utf-8", errors="replace")
    if entry["license"].split("-")[0].lower() not in license_text.lower():
        raise ValueError(f"configured license is not present in evidence: {entry['id']}")
    digest = hashlib.sha256(license_bytes).hexdigest()
    expected = entry.get("license_sha256")
    if expected and expected != digest:
        raise ValueError(
            f"license evidence changed for {entry['id']}; review and update the lock manually"
        )
    return digest


def copy_snapshot(source: Path, destination: Path, entry: dict, commit: str) -> None:
    assert_safe_tree(source)
    if destination.exists():
        expected = entry.get("tree_sha256")
        if expected and tree_hash(destination, exclude_source_note=True) != expected:
            raise ValueError(
                f"local modification conflict in machine-owned snapshot: {destination}"
            )
        shutil.rmtree(destination)
    shutil.copytree(source, destination)
    source_note = (
        "# Managed upstream snapshot\n\n"
        f"- Repository: {entry['repository']}\n"
        f"- Source path: `{entry['source_path']}`\n"
        f"- Commit: `{commit}`\n"
        f"- License: {entry['license']}\n"
        "- Update policy: replace this directory only through `scripts/sync_upstreams.py`.\n"
    )
    (destination / "_SOURCE.md").write_text(source_note, encoding="utf-8")
    remove_identical_finder_duplicates(destination)


def parse_cache(values: list[str]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ValueError("--cache requires owner/repo=/path")
        key, raw_path = value.split("=", 1)
        result[key] = Path(raw_path).expanduser().resolve()
    return result


def do_update(repo: Path, lock: dict, caches: dict[str, Path]) -> bool:
    changed = False
    with tempfile.TemporaryDirectory(prefix="eric-upstreams-") as temp_raw:
        temp = Path(temp_raw)
        checkouts: dict[str, Path] = {}
        for entry in lock["upstreams"]:
            if entry["mode"] != "vendored-reference":
                continue
            key = repository_key(entry["repository"])
            checkout = checkouts.get(key)
            if checkout is None:
                checkout = caches.get(key)
                if checkout is None:
                    checkout = clone_repository(entry["repository"], temp / key.replace("/", "--"))
                checkouts[key] = checkout
            commit = head(checkout)
            license_digest = verify_license(checkout, entry)
            source = (checkout / entry["source_path"]).resolve()
            try:
                source.relative_to(checkout.resolve())
            except ValueError as exc:
                raise ValueError(f"source path escapes checkout: {source}") from exc
            digest = tree_hash(source)
            for target in entry["targets"]:
                destination = snapshot_destination(repo, entry["id"], target)
                copy_snapshot(source, destination, entry, commit)
            if (
                entry.get("commit") != commit
                or entry.get("tree_sha256") != digest
                or (license_digest and entry.get("license_sha256") != license_digest)
            ):
                changed = True
            entry["commit"] = commit
            entry["tree_sha256"] = digest
            if license_digest:
                entry["license_sha256"] = license_digest
    return changed


def do_check(lock: dict) -> int:
    current: dict[str, str] = {}
    updates: list[dict[str, str]] = []
    for entry in lock["upstreams"]:
        url = entry["repository"]
        if url not in current:
            output = subprocess.check_output(["git", "ls-remote", url, "HEAD"], text=True).strip()
            current[url] = output.split()[0]
        if current[url] != entry["commit"]:
            updates.append({"id": entry["id"], "pinned": entry["commit"], "available": current[url]})
    print(json.dumps({"updates": updates}, indent=2))
    return 2 if updates else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("check", "update"))
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--all", action="store_true", help="Required acknowledgement for update")
    parser.add_argument("--cache", action="append", default=[], metavar="OWNER/REPO=PATH")
    args = parser.parse_args()
    lock_path = args.repo / "catalog" / "upstreams.lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    if args.command == "check":
        return do_check(lock)
    if not args.all:
        parser.error("update requires --all")
    changed = do_update(args.repo.resolve(), lock, parse_cache(args.cache))
    lock_path.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"changed": changed, "lock": str(lock_path)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
