#!/usr/bin/env python3
"""Validate a project-local validator bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


REQUIRED_SCRIPT_TOKENS = (
    "class Issue",
    "def validate(",
    "def render_markdown(",
    "--self-test",
    "--no-write",
    "strict_fail_severities",
    "next_action",
    "RULE_PATH_OUTSIDE_ROOT",
)

PACKAGE_ARTIFACT_SUFFIXES = {".pyc", ".pyo", ".tmp", ".bak", ".orig"}
PACKAGE_ARTIFACT_NAMES = {"__pycache__", ".DS_Store"}
REPORT_REQUIRED_FIELDS = {"status", "generated_at", "root", "summary", "issues", "next_action"}


@dataclass
class Finding:
    severity: str
    code: str
    file: str
    detail: str


def add(findings: list[Finding], severity: str, code: str, file: Path | str, detail: str) -> None:
    findings.append(Finding(severity=severity, code=code, file=str(file), detail=detail))


def run_cmd(args: list[str], cwd: Path, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(args, cwd=cwd, text=True, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return subprocess.CompletedProcess(args, 124, stdout, stderr or f"command timed out after {timeout}s")


def digest_file(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "unreadable"


def digest_symlink_target(path: Path, seen: frozenset[tuple[int, int]] | None = None) -> str:
    seen = seen or frozenset()
    try:
        link_target = os.readlink(path)
        resolved = path.resolve(strict=True)
        target_stat = resolved.stat()
    except (OSError, RuntimeError) as exc:
        return f"broken:{exc}"
    target_id = (target_stat.st_dev, target_stat.st_ino)
    if target_id in seen:
        return f"cycle:{link_target}"
    next_seen = seen | {target_id}

    if resolved.is_file():
        return (
            f"file:{link_target}:{target_stat.st_mode}:{target_stat.st_size}:"
            f"{target_stat.st_mtime_ns}:{target_stat.st_ctime_ns}:{digest_file(resolved)}"
        )

    if resolved.is_dir():
        entries: list[str] = []
        for child in sorted(resolved.rglob("*")):
            try:
                child_stat = child.lstat()
            except OSError:
                continue
            rel_child = child.relative_to(resolved)
            digest = ""
            if child.is_symlink():
                digest = digest_symlink_target(child, next_seen)
            elif child.is_file():
                digest = digest_file(child)
            entries.append(
                f"{rel_child}:{child_stat.st_mode}:{child_stat.st_size}:"
                f"{child_stat.st_mtime_ns}:{child_stat.st_ctime_ns}:"
                f"{stat.S_ISDIR(child_stat.st_mode)}:{digest}"
            )
        metadata = (
            f"{target_stat.st_mode}:{target_stat.st_size}:"
            f"{target_stat.st_mtime_ns}:{target_stat.st_ctime_ns}"
        )
        return f"dir:{link_target}:{metadata}:" + hashlib.sha256("\n".join(entries).encode("utf-8")).hexdigest()

    return f"other:{link_target}"


def snapshot_tree(root: Path) -> dict[str, tuple[int, int, int, int, bool, str]]:
    if not root.exists():
        return {}
    snapshot: dict[str, tuple[int, int, int, int, bool, str]] = {}
    for path in root.rglob("*"):
        try:
            path_stat = path.lstat()
        except OSError:
            continue
        digest = ""
        if path.is_symlink():
            digest = digest_symlink_target(path)
        elif path.is_file():
            digest = digest_file(path)
        snapshot[str(path.relative_to(root))] = (
            path_stat.st_mode,
            path_stat.st_size,
            path_stat.st_mtime_ns,
            path_stat.st_ctime_ns,
            stat.S_ISDIR(path_stat.st_mode),
            digest,
        )
    return snapshot


def no_write_watch_roots(root: Path, validator_dir: Path) -> dict[str, Path]:
    roots: dict[str, Path] = {"root": root}
    if validator_dir.name == "validator" and validator_dir.parent.name == "qa":
        roots["project_root"] = validator_dir.parent.parent
    else:
        roots["validator_parent"] = validator_dir.parent
    return roots


def load_json(path: Path, findings: list[Finding]) -> dict[str, Any] | None:
    if not path.exists():
        add(findings, "P0", "RULES_MISSING", path, "validator_rules.json is missing")
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        add(findings, "P0", "RULES_INVALID_JSON", path, str(exc))
        return None
    if not isinstance(payload, dict):
        add(findings, "P0", "RULES_NOT_OBJECT", path, "rules file must contain a JSON object")
        return None
    return payload


def check_package_artifacts(validator_dir: Path, findings: list[Finding]) -> None:
    if not validator_dir.exists():
        return
    for path in validator_dir.rglob("*"):
        if any(part in PACKAGE_ARTIFACT_NAMES for part in path.parts) or path.suffix in PACKAGE_ARTIFACT_SUFFIXES:
            add(findings, "P1", "PACKAGE_ARTIFACT_FOUND", path, "remove generated cache/temp artifact from validator bundle")


def check_report_contract(script: Path, rules_path: Path, validator_dir: Path, findings: list[Finding]) -> None:
    if not script.exists() or not rules_path.exists():
        return
    with tempfile.TemporaryDirectory(prefix="validator-bundle-contract-") as tmp:
        root = Path(tmp)
        watch_roots = no_write_watch_roots(root, validator_dir)
        before = {name: snapshot_tree(path) for name, path in watch_roots.items()}
        result = run_cmd(
            [
                sys.executable,
                "-B",
                str(script),
                "--root",
                tmp,
                "--rules",
                str(rules_path),
                "--no-write",
                "--json",
            ],
            validator_dir,
        )
        after = {name: snapshot_tree(path) for name, path in watch_roots.items()}
    if after != before:
        add(findings, "P1", "NO_WRITE_CONTRACT_VIOLATED", script, "validator wrote files while invoked with --no-write")
    if result.returncode not in {0, 1}:
        add(findings, "P1", "REPORT_CONTRACT_COMMAND_FAILED", script, result.stderr or result.stdout or "validator report command failed")
        return
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        add(findings, "P1", "REPORT_CONTRACT_INVALID_JSON", script, f"validator --json output is not valid JSON: {exc}")
        return
    if not isinstance(payload, dict):
        add(findings, "P1", "REPORT_CONTRACT_NOT_OBJECT", script, "validator --json output must be a JSON object")
        return
    for field in sorted(REPORT_REQUIRED_FIELDS - set(payload)):
        add(findings, "P1", "REPORT_CONTRACT_MISSING_FIELD", script, f"validator JSON report missing field: {field}")
    if "next_action" in payload and (not isinstance(payload["next_action"], str) or not payload["next_action"].strip()):
        add(findings, "P1", "REPORT_CONTRACT_INVALID_FIELD", script, "next_action must be a non-empty string")
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        add(findings, "P1", "REPORT_CONTRACT_INVALID_FIELD", script, "summary must be an object")
    elif not {"status", "counts", "strict_fail_severities"}.issubset(summary):
        add(findings, "P1", "REPORT_CONTRACT_INVALID_FIELD", script, "summary must include status, counts, and strict_fail_severities")
    if "issues" in payload and not isinstance(payload["issues"], list):
        add(findings, "P1", "REPORT_CONTRACT_INVALID_FIELD", script, "issues must be a list")


def validate_bundle(
    validator_dir: Path,
    script_name: str,
    rules_name: str,
    skip_self_test: bool,
    static_only: bool,
) -> dict[str, Any]:
    validator_dir = validator_dir.expanduser().resolve()
    findings: list[Finding] = []
    script = validator_dir / script_name
    rules_path = validator_dir / rules_name

    if not validator_dir.exists():
        add(findings, "P0", "VALIDATOR_DIR_MISSING", validator_dir, "validator directory does not exist")
    if not script.exists():
        add(findings, "P0", "SCRIPT_MISSING", script, "validator script is missing")
    else:
        text = script.read_text(encoding="utf-8")
        missing = [token for token in REQUIRED_SCRIPT_TOKENS if token not in text]
        for token in missing:
            add(findings, "P1", "SCRIPT_CONTRACT_TOKEN_MISSING", script, f"missing token: {token}")
        if "TODO" in text or "[TODO" in text:
            add(findings, "P1", "SCRIPT_TODO_LEFTOVER", script, "script contains TODO marker")
    check_package_artifacts(validator_dir, findings)

    rules = load_json(rules_path, findings)
    if rules is not None:
        if rules.get("schema_version") != 1:
            add(findings, "P1", "RULES_SCHEMA_VERSION_MISSING", rules_path, "schema_version must be 1")
        strict = rules.get("strict_fail_severities")
        if not isinstance(strict, list) or not {"P0", "P1"}.issubset({str(item) for item in strict}):
            add(findings, "P1", "STRICT_SEVERITIES_WEAK", rules_path, "strict_fail_severities must include P0 and P1")
        for key in ("required_paths", "expected_counts", "json_files", "public_globs", "forbidden_public_terms"):
            if key in rules and not isinstance(rules[key], list):
                add(findings, "P1", "RULES_FIELD_NOT_LIST", rules_path, f"{key} must be a list")

    if script.exists() and not static_only:
        help_result = run_cmd([sys.executable, str(script), "--help"], validator_dir)
        if help_result.returncode != 0:
            add(findings, "P1", "SCRIPT_HELP_FAILED", script, help_result.stderr or help_result.stdout)
        if not skip_self_test:
            self_test = run_cmd([sys.executable, str(script), "--self-test"], validator_dir)
            if self_test.returncode != 0:
                add(findings, "P0", "SCRIPT_SELF_TEST_FAILED", script, self_test.stderr or self_test.stdout)
        check_report_contract(script, rules_path, validator_dir, findings)

    tests_dir = validator_dir / "tests"
    if not tests_dir.exists():
        add(findings, "P2", "TESTS_DIR_MISSING", tests_dir, "bundle has no tests directory")
    else:
        test_files = sorted(tests_dir.glob("test_*.py"))
        if not test_files:
            add(findings, "P2", "TEST_FILES_MISSING", tests_dir, "bundle has no test_*.py files")
        elif not static_only:
            for test_file in test_files:
                test_result = run_cmd([sys.executable, str(test_file)], validator_dir)
                if test_result.returncode != 0:
                    add(
                        findings,
                        "P1",
                        "TEST_COMMAND_FAILED",
                        test_file,
                        (test_result.stderr or test_result.stdout or "test command failed").strip(),
                    )

    counts: dict[str, int] = {}
    for item in findings:
        counts[item.severity] = counts.get(item.severity, 0) + 1
    status = "fail" if any(item.severity in {"P0", "P1"} for item in findings) else ("warn" if findings else "pass")
    return {
        "status": status,
        "validator_dir": str(validator_dir),
        "counts": counts,
        "findings": [asdict(item) for item in findings],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a project-local validator bundle.")
    parser.add_argument("validator_dir", type=Path)
    parser.add_argument("--script", default="validate_project.py")
    parser.add_argument("--rules", default="validator_rules.json")
    parser.add_argument("--skip-self-test", action="store_true")
    parser.add_argument("--static-only", action="store_true", help="inspect bundle files without executing candidate validator code")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    payload = validate_bundle(args.validator_dir, args.script, args.rules, args.skip_self_test, args.static_only)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"status={payload['status']} findings={len(payload['findings'])}")
        for finding in payload["findings"]:
            print(f"- [{finding['severity']}] {finding['code']} {finding['file']}: {finding['detail']}")
    return 1 if payload["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
