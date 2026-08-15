#!/usr/bin/env python3
"""Fail when SkillSpector JSON reports unsuppressed high/critical findings."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


BLOCKING = {"critical", "high", "p0", "p1"}


def findings(value):
    if isinstance(value, dict):
        severity = str(value.get("severity", "")).lower()
        suppressed = bool(value.get("suppressed", False))
        if severity in BLOCKING and not suppressed:
            yield value
        for child in value.values():
            yield from findings(child)
    elif isinstance(value, list):
        for child in value:
            yield from findings(child)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report_dir", type=Path)
    args = parser.parse_args()
    blocking = []
    incomplete = []
    for path in sorted(args.report_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        completeness = data.get("analysis_completeness", {})
        analyzer_failures = [
            status.get("analyzer_id")
            for status in completeness.get("analyzer_statuses", [])
            if status.get("failed", 0) or status.get("unaccounted", 0)
        ]
        exceptions = completeness.get("ledger_exceptions", [])
        fatal_exceptions = [item for item in exceptions if item.get("fatal")]
        unexpected_exceptions = [
            item
            for item in exceptions
            if item.get("reason_code") not in {"binary_content", "size_limit"}
        ]
        if (
            data.get("execution_successful") is not True
            or analyzer_failures
            or fatal_exceptions
            or unexpected_exceptions
        ):
            incomplete.append(
                {
                    "report": path.name,
                    "execution_successful": data.get("execution_successful"),
                    "coverage_percent": completeness.get("coverage_percent"),
                    "entirely_uninspected_files": completeness.get("entirely_uninspected_files"),
                    "analyzer_failures": analyzer_failures,
                    "fatal_exceptions": fatal_exceptions,
                    "unexpected_exceptions": unexpected_exceptions,
                }
            )
        for finding in findings(data):
            location = finding.get("location") if isinstance(finding.get("location"), dict) else {}
            blocking.append(
                {
                    "report": path.name,
                    "id": finding.get("id", "risk_assessment"),
                    "severity": finding.get("severity"),
                    "category": finding.get("category"),
                    "file": location.get("file"),
                    "line": location.get("start_line"),
                    "finding": str(finding.get("finding", ""))[:240],
                }
            )
    if blocking or incomplete:
        print(json.dumps({"blocking": blocking, "incomplete": incomplete}, indent=2))
        return 1
    print(f"No unsuppressed high/critical findings in {args.report_dir}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
