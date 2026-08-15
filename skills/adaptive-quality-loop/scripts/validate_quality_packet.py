#!/usr/bin/env python3
"""Validate the small formal record used only for RELEASE mode."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


READY_VERDICTS = {"READY", "READY WITH MINOR FOLLOW-UPS"}
VALID_SEVERITIES = {"P0", "P1", "P2", "P3"}


def finding(code: str, field: str, detail: str, severity: str = "P1") -> dict[str, str]:
    return {"severity": severity, "code": code, "field": field, "detail": detail}


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_release_record(record: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []

    if record.get("schema_version") != 1:
        findings.append(finding("SCHEMA_VERSION_INVALID", "schema_version", "schema_version must equal 1"))
    if record.get("mode") != "RELEASE":
        findings.append(finding(
            "FORMAL_RECORD_RELEASE_ONLY",
            "mode",
            "BUILD and PROOF must not create a formal record; mode must be RELEASE",
        ))

    artifact = record.get("artifact")
    if not isinstance(artifact, dict):
        findings.append(finding("ARTIFACT_MISSING", "artifact", "artifact must be an object"))
        artifact = {}
    if not nonempty(artifact.get("target")):
        findings.append(finding("ARTIFACT_TARGET_MISSING", "artifact.target", "an exact target is required"))
    if not nonempty(artifact.get("identity")):
        findings.append(finding("ARTIFACT_IDENTITY_MISSING", "artifact.identity", "a frozen identity is required"))

    authority = record.get("authority")
    if not isinstance(authority, dict):
        findings.append(finding("AUTHORITY_MISSING", "authority", "release authority must be recorded", "P0"))
        authority = {}
    if str(authority.get("status", "")).strip().lower() not in {"granted", "approved", "authorized"}:
        findings.append(finding("AUTHORITY_NOT_GRANTED", "authority.status", "release authority is not granted", "P0"))
    if not nonempty(authority.get("by")):
        findings.append(finding("AUTHORITY_GRANTOR_MISSING", "authority.by", "the authority grantor is required", "P0"))
    if not nonempty(authority.get("scope")):
        findings.append(finding("AUTHORITY_SCOPE_MISSING", "authority.scope", "the authorized action scope is required", "P0"))

    recovery = record.get("recovery")
    if not isinstance(recovery, dict):
        findings.append(finding("RECOVERY_MISSING", "recovery", "a recovery record is required", "P0"))
        recovery = {}
    if recovery.get("available") is not True:
        findings.append(finding("RECOVERY_UNAVAILABLE", "recovery.available", "recovery must be available", "P0"))
    if not nonempty(recovery.get("method")):
        findings.append(finding("RECOVERY_METHOD_MISSING", "recovery.method", "a usable recovery method is required", "P0"))
    if not nonempty(recovery.get("evidence")):
        findings.append(finding("RECOVERY_EVIDENCE_MISSING", "recovery.evidence", "current recovery evidence is required", "P0"))

    checks = record.get("checks")
    if not isinstance(checks, list) or not checks:
        findings.append(finding("CHECKS_MISSING", "checks", "at least one release check is required"))
        checks = []
    for index, check in enumerate(checks):
        prefix = f"checks[{index}]"
        if not isinstance(check, dict):
            findings.append(finding("CHECK_INVALID", prefix, "each check must be an object"))
            continue
        if not nonempty(check.get("name")):
            findings.append(finding("CHECK_NAME_MISSING", f"{prefix}.name", "check name is required"))
        if str(check.get("status", "")).strip().upper() != "PASS":
            findings.append(finding("CHECK_NOT_PASSING", f"{prefix}.status", "every required release check must pass"))
        if not nonempty(check.get("evidence")):
            findings.append(finding("CHECK_EVIDENCE_MISSING", f"{prefix}.evidence", "current evidence is required"))

    review = record.get("review")
    if not isinstance(review, dict):
        findings.append(finding("REVIEW_MISSING", "review", "an independent release review is required", "P0"))
        review = {}
    producer = review.get("producer")
    reviewer = review.get("reviewer")
    if not nonempty(producer):
        findings.append(finding("PRODUCER_MISSING", "review.producer", "producer identity is required"))
    if not nonempty(reviewer):
        findings.append(finding("REVIEWER_MISSING", "review.reviewer", "reviewer identity is required", "P0"))
    if review.get("independent") is not True:
        findings.append(finding("INDEPENDENCE_REQUIRED", "review.independent", "formal release review must be independent", "P0"))
    if nonempty(producer) and nonempty(reviewer) and producer.strip().casefold() == reviewer.strip().casefold():
        findings.append(finding("SAME_AGENT_SIGNOFF_FORBIDDEN", "review.reviewer", "producer and reviewer must differ", "P0"))
    if review.get("verdict") not in READY_VERDICTS:
        findings.append(finding("REVIEW_NOT_READY", "review.verdict", "review verdict must be READY or READY WITH MINOR FOLLOW-UPS", "P0"))

    recorded_findings = record.get("findings", [])
    if not isinstance(recorded_findings, list):
        findings.append(finding("FINDINGS_INVALID", "findings", "findings must be a list"))
        recorded_findings = []
    for index, item in enumerate(recorded_findings):
        prefix = f"findings[{index}]"
        if not isinstance(item, dict):
            findings.append(finding("FINDING_INVALID", prefix, "each finding must be an object"))
            continue
        severity = item.get("severity")
        status = str(item.get("status", "open")).strip().lower()
        if severity not in VALID_SEVERITIES:
            findings.append(finding("FINDING_SEVERITY_INVALID", f"{prefix}.severity", "severity must be P0, P1, P2, or P3"))
        if status not in {"open", "closed"}:
            findings.append(finding("FINDING_STATUS_INVALID", f"{prefix}.status", "status must be open or closed"))
        if severity in {"P0", "P1"} and status == "open":
            findings.append(finding("OPEN_RELEASE_BLOCKER", prefix, "open P0/P1 findings block release", "P0"))

    return findings


def load_record(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("record root must be a JSON object")
    return value


def self_test_record() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "mode": "RELEASE",
        "artifact": {"target": "dist/example", "identity": "sha256:example"},
        "authority": {"status": "granted", "by": "Eric", "scope": "install the frozen profile"},
        "recovery": {"available": True, "method": "rollback manifest", "evidence": "manifest.json"},
        "checks": [{"name": "tests", "status": "PASS", "evidence": "tests: pass"}],
        "review": {"producer": "writer", "reviewer": "reviewer", "independent": True, "verdict": "READY"},
        "findings": [],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", nargs="?", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    try:
        if args.self_test:
            record = self_test_record()
        elif args.record is not None:
            record = load_record(args.record)
        else:
            parser.error("record is required unless --self-test is used")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    findings = validate_release_record(record)
    result = {"valid": not findings, "mode": record.get("mode"), "findings": findings}
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    elif findings:
        for item in findings:
            print(f"{item['severity']} {item['code']} {item['field']}: {item['detail']}")
    else:
        print("VALID RELEASE RECORD")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
