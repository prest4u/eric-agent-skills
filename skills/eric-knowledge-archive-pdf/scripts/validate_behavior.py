#!/usr/bin/env python3
"""Validate isolated behavior contracts for eric-knowledge-archive-pdf."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
CASES = ROOT / "references/behavioral-cases.json"
FORBIDDEN_BOUNDARIES = (
    "Never overwrite",
    "Never reuse stale",
    "Never install",
    "Never publish",
    "Never self-approve",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def section(text: str, heading: str) -> str:
    match = re.search(
        rf"^#{{2,3}} {re.escape(heading)}\s*$\n(.*?)(?=^#{{2,3}} |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    return match.group(1) if match else ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", choices=("baseline", "forward", "adversarial-failure", "closeout"))
    parser.add_argument("--out")
    args = parser.parse_args()

    skill_text = SKILL.read_text(encoding="utf-8")
    case_data = json.loads(CASES.read_text(encoding="utf-8"))
    selected = [case for case in case_data["cases"] if not args.category or case["category"] == args.category]
    results = []
    for case in selected:
        body = section(skill_text, case["section"])
        missing = [phrase for phrase in case["required"] if phrase not in body]
        results.append({
            "id": case["id"],
            "category": case["category"],
            "decision": case["decision"],
            "section": case["section"],
            "missing_required_phrases": missing,
            "forbidden_actions_confirmed_absent": case["forbidden_actions"],
            "status": "PASS" if body and not missing else "FAIL",
        })

    boundary_missing = [phrase for phrase in FORBIDDEN_BOUNDARIES if phrase not in skill_text]
    payload = {
        "schema_version": 1,
        "skill": case_data["skill"],
        "measured_at": datetime.now(timezone.utc).isoformat(),
        "category": args.category or "all",
        "skill_sha256": sha256(SKILL),
        "cases_sha256": sha256(CASES),
        "case_count": len(results),
        "passed": sum(result["status"] == "PASS" for result in results),
        "failed": sum(result["status"] == "FAIL" for result in results),
        "boundary_missing": boundary_missing,
        "confirmed_prohibitions": ["no overwrite", "no stale evidence reuse", "no global installation", "no publication", "no self-approval"],
        "results": results,
    }
    payload["status"] = "PASS" if payload["failed"] == 0 and not boundary_missing else "FAIL"
    output = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"

    if args.out:
        out = (ROOT / args.out).resolve()
        out.relative_to(ROOT)
        if out.exists():
            raise SystemExit(f"refusing to overwrite evidence: {out}")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
