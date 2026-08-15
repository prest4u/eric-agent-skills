#!/usr/bin/env python3
"""Validate the portable frontend-delivery evidence schema."""
from __future__ import annotations

import argparse
import ipaddress
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


FORMAL_ROUTES = {"production_create", "repair"}
READY = {"READY", "READY WITH MINOR FOLLOW-UPS"}
VALID_VERDICTS = READY | {
    "PENDING INDEPENDENT REVIEW",
    "INSUFFICIENT EVIDENCE",
    "BLOCKED_REPAIR_BUDGET",
    "NOT READY",
}
Q3_REVIEWER_PROVENANCE = {"same_agent", "independent_agent", "eric"}
Q4_COMPATIBILITY = {
    "READY": {("pass", "fresh_independent"), ("pass", "eric")},
    "READY WITH MINOR FOLLOW-UPS": {("pass", "fresh_independent"), ("pass", "eric")},
    "PENDING INDEPENDENT REVIEW": {("pending", "fresh_independent_required")},
    "NOT READY": {("fail", "same_agent"), ("fail", "fresh_independent"), ("fail", "eric")},
    "INSUFFICIENT EVIDENCE": {("blocked", "same_agent"), ("blocked", "fresh_independent"), ("blocked", "eric")},
    "BLOCKED_REPAIR_BUDGET": {("blocked", "same_agent"), ("blocked", "fresh_independent"), ("blocked", "eric")},
}


def finding(code: str, field: str, detail: str, severity: str = "P1") -> dict[str, str]:
    return {"severity": severity, "code": code, "field": field, "detail": detail}


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(nonempty(item) for item in value)


def evidence_locator_reason(value: Any) -> str | None:
    """Return a safe rejection reason for a canonical portable locator."""
    if not isinstance(value, str) or not value.strip():
        return "non-empty string required"
    if value != unicodedata.normalize("NFKC", value):
        return "NFKC-canonical form required"
    if "%" in value:
        return "percent signs and percent encoding are forbidden"
    if any(unicodedata.category(character) == "Cc" for character in value):
        return "control characters are forbidden"
    if "\\" in value:
        return "backslashes and UNC forms are forbidden"
    if value.startswith(("/", "~")):
        return "absolute and home-relative forms are forbidden"
    if re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", value) is not None:
        return "scheme-like and drive-relative prefixes are forbidden"
    segments = value.split("/")
    if any(segment in {"", ".", ".."} for segment in segments):
        return "empty, dot, parent, repeated, or trailing segments are forbidden"
    return None


def relative_path(value: Any) -> bool:
    return evidence_locator_reason(value) is None


def positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def valid_port(value: str) -> bool:
    if re.fullmatch(r"[0-9]{1,5}", value) is None:
        return False
    return 1 <= int(value) <= 65535


def split_authority(authority: str) -> tuple[str, str | None, bool] | None:
    """Return host, optional port, and IPv6-literal flag for a strict authority."""
    if not authority or "@" in authority:
        return None
    if authority.startswith("["):
        closing = authority.find("]")
        if closing <= 1:
            return None
        host = authority[1:closing]
        suffix = authority[closing + 1 :]
        if "]" in suffix:
            return None
        if not suffix:
            return host, None, True
        if not suffix.startswith(":") or not valid_port(suffix[1:]):
            return None
        return host, suffix[1:], True
    if "[" in authority or "]" in authority:
        return None
    if ":" not in authority:
        return authority, None, False
    host, port = authority.rsplit(":", 1)
    if not host or ":" in host or not valid_port(port):
        return None
    return host, port, False


def loopback_runtime_url(value: Any) -> bool:
    if (
        not nonempty(value)
        or any(ord(character) <= 0x1F or ord(character) == 0x7F for character in value)
        or any(character.isspace() for character in value)
        or "\\" in value
        or re.search(r"%(?![0-9A-Fa-f]{2})", value)
    ):
        return False
    try:
        parsed = urlsplit(value)
    except ValueError:
        return False
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False
    authority = split_authority(parsed.netloc)
    if authority is None or parsed.username is not None or parsed.password is not None:
        return False
    hostname, _port, is_ipv6 = authority
    if is_ipv6:
        try:
            return ipaddress.IPv6Address(hostname) == ipaddress.IPv6Address("::1")
        except ipaddress.AddressValueError:
            return False
    if hostname.lower() == "localhost":
        return True
    try:
        address = ipaddress.IPv4Address(hostname)
        return int(address) >> 24 == 127
    except ipaddress.AddressValueError:
        return False


def require_object(parent: dict[str, Any], key: str, findings: list[dict[str, str]]) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        findings.append(finding("OBJECT_MISSING", key, f"{key} must be an object"))
        return {}
    return value


def require_strings(obj: dict[str, Any], fields: tuple[str, ...], prefix: str, findings: list[dict[str, str]]) -> None:
    for field in fields:
        if not nonempty(obj.get(field)):
            findings.append(finding("FIELD_MISSING", f"{prefix}.{field}", "non-empty string required"))


def check_evidence_path(value: Any, field: str, findings: list[dict[str, str]]) -> None:
    reason = evidence_locator_reason(value)
    if reason is not None:
        findings.append(finding("EVIDENCE_PATH_ESCAPE", field, f"canonical project-relative locator required: {reason}"))


def validate(packet: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if packet.get("schema_version") != 1:
        findings.append(finding("SCHEMA_VERSION_INVALID", "schema_version", "schema_version must equal 1"))
    if not nonempty(packet.get("delivery_id")):
        findings.append(finding("DELIVERY_ID_MISSING", "delivery_id", "stable delivery_id required"))
    if packet.get("route") not in FORMAL_ROUTES:
        findings.append(finding("ROUTE_NOT_FORMAL", "route", "validator accepts production_create or repair only"))

    artifact = require_object(packet, "artifact", findings)
    require_strings(artifact, ("source_identity", "build_identity", "runtime"), "artifact", findings)
    if not loopback_runtime_url(artifact.get("runtime")):
        findings.append(
            finding(
                "RUNTIME_URL_INVALID",
                "artifact.runtime",
                "runtime must be a strict http/https URL on localhost, an IPv4 address in 127.0.0.0/8, or ::1, without userinfo",
            )
        )
    targets = artifact.get("targets")
    if not isinstance(targets, list) or not targets:
        findings.append(finding("ARTIFACT_TARGETS_MISSING", "artifact.targets", "non-empty target list required"))
        targets = []
    elif not all(nonempty(target) for target in targets):
        findings.append(finding("ARTIFACT_TARGETS_MISSING", "artifact.targets", "non-empty target strings required"))
    for index, target in enumerate(targets):
        check_evidence_path(target, f"artifact.targets[{index}]", findings)

    q0 = require_object(packet, "q0", findings)
    require_strings(
        q0,
        (
            "outcome", "product_surface", "framework", "design_system", "asset_policy",
            "dependency_policy", "design_direction",
        ),
        "q0",
        findings,
    )
    for field in ("primary_flow", "source_of_truth", "non_goals", "accessibility", "acceptance_evidence"):
        if not string_list(q0.get(field)):
            findings.append(finding("Q0_LIST_MISSING", f"q0.{field}", "non-empty string list required"))

    declared_viewports: set[str] = set()
    viewports = q0.get("viewports")
    if not isinstance(viewports, list) or not viewports:
        findings.append(finding("Q0_VIEWPORTS_MISSING", "q0.viewports", "desktop and mobile viewports required"))
        viewports = []
    for index, viewport in enumerate(viewports):
        field = f"q0.viewports[{index}]"
        if (
            not isinstance(viewport, dict)
            or set(viewport) != {"id", "width", "height"}
            or not nonempty(viewport.get("id"))
            or not positive_int(viewport.get("width"))
            or not positive_int(viewport.get("height"))
        ):
            findings.append(finding("Q0_VIEWPORT_INVALID", field, "exactly id:string, width:positive integer, and height:positive integer required"))
            continue
        if viewport["id"] in declared_viewports:
            findings.append(finding("Q0_VIEWPORT_DUPLICATE", field, f"duplicate viewport id: {viewport['id']}"))
        declared_viewports.add(viewport["id"])
    if "desktop" not in declared_viewports or "mobile" not in declared_viewports:
        findings.append(finding("Q0_RESPONSIVE_BASELINE_MISSING", "q0.viewports", "formal delivery requires desktop and mobile declarations"))

    declared_states: set[str] = set()
    required_states: set[str] = set()
    states = q0.get("states")
    if not isinstance(states, list) or not states:
        findings.append(finding("Q0_STATES_MISSING", "q0.states", "at least one declared state object required"))
        states = []
    for index, state in enumerate(states):
        field = f"q0.states[{index}]"
        if (
            not isinstance(state, dict)
            or set(state) != {"id", "required"}
            or not nonempty(state.get("id"))
            or not isinstance(state.get("required"), bool)
        ):
            findings.append(finding("Q0_STATE_INVALID", field, "exactly id:string and required:boolean required"))
            continue
        if state["id"] in declared_states:
            findings.append(finding("Q0_STATE_DUPLICATE", field, f"duplicate state id: {state['id']}"))
        declared_states.add(state["id"])
        if state["required"]:
            required_states.add(state["id"])

    stages = require_object(packet, "stages", findings)
    q1 = require_object(stages, "q1", findings)
    if q1.get("owner") != "frontend-design" or q1.get("status") != "pass":
        findings.append(finding("Q1_INCOMPLETE", "stages.q1", "frontend-design owner with pass status required"))
    q1_evidence = q1.get("evidence")
    if not isinstance(q1_evidence, list) or not q1_evidence:
        findings.append(finding("Q1_EVIDENCE_MISSING", "stages.q1.evidence", "source evidence required"))
        q1_evidence = []
    elif not all(nonempty(value) for value in q1_evidence):
        findings.append(finding("Q1_EVIDENCE_MISSING", "stages.q1.evidence", "non-empty source evidence strings required"))
    for index, value in enumerate(q1_evidence):
        check_evidence_path(value, f"stages.q1.evidence[{index}]", findings)

    q2 = require_object(stages, "q2", findings)
    if q2.get("status") != "pass":
        findings.append(finding("Q2_INCOMPLETE", "stages.q2.status", "pass status required"))
    commands = q2.get("commands")
    if not isinstance(commands, list) or not commands:
        findings.append(finding("Q2_COMMANDS_MISSING", "stages.q2.commands", "at least one command record required"))
        commands = []
    for index, command in enumerate(commands):
        if not isinstance(command, dict) or not nonempty(command.get("command")) or command.get("status") != "pass":
            findings.append(finding("Q2_COMMAND_INVALID", f"stages.q2.commands[{index}]", "passing exact command required"))
            continue
        check_evidence_path(command.get("evidence"), f"stages.q2.commands[{index}].evidence", findings)

    q3 = require_object(stages, "q3", findings)
    if q3.get("owner") != "eric-review" or q3.get("mode") != "RECHECK" or q3.get("status") != "pass":
        findings.append(finding("Q3_INCOMPLETE", "stages.q3", "visual owner, RECHECK mode, and pass status required"))
    if q3.get("build_identity") != artifact.get("build_identity"):
        findings.append(finding("Q3_BUILD_IDENTITY_MISMATCH", "stages.q3.build_identity", "Q3 must match the artifact build identity"))
    if "runtime_evidence" not in q3:
        findings.append(finding("Q3_RUNTIME_EVIDENCE_MISSING", "stages.q3.runtime_evidence", "build-matched runtime evidence required"))
    else:
        check_evidence_path(q3.get("runtime_evidence"), "stages.q3.runtime_evidence", findings)
    if "reviewer_provenance" not in q3:
        findings.append(
            finding(
                "Q3_REVIEWER_PROVENANCE_MISSING",
                "stages.q3.reviewer_provenance",
                "Q3 rendered visual recheck provenance is required and remains separate from Q4 sign-off",
            )
        )
    elif q3.get("reviewer_provenance") not in Q3_REVIEWER_PROVENANCE:
        findings.append(
            finding(
                "Q3_REVIEWER_PROVENANCE_INVALID",
                "stages.q3.reviewer_provenance",
                f"must be one of {sorted(Q3_REVIEWER_PROVENANCE)}; Q4 fresh-independent values are not Q3 provenance",
            )
        )

    observed_viewports: set[str] = set()
    observed_viewport_items = q3.get("viewports")
    if not isinstance(observed_viewport_items, list) or not observed_viewport_items:
        findings.append(finding("Q3_VIEWPORTS_MISSING", "stages.q3.viewports", "at least one observed viewport object required"))
        observed_viewport_items = []
    for index, item in enumerate(observed_viewport_items):
        field = f"stages.q3.viewports[{index}]"
        evidence_field = f"{field}.evidence"
        if not isinstance(item, dict) or set(item) != {"id", "evidence"} or not nonempty(item.get("id")) or not relative_path(item.get("evidence")):
            findings.append(finding("Q3_VIEWPORT_INVALID", field, "exactly id:string and contained evidence:path required"))
            if isinstance(item, dict) and "evidence" in item:
                check_evidence_path(item.get("evidence"), evidence_field, findings)
            continue
        if item["id"] in observed_viewports:
            findings.append(finding("Q3_VIEWPORT_DUPLICATE", field, f"duplicate observed viewport id: {item['id']}"))
        observed_viewports.add(item["id"])
        if item["id"] not in declared_viewports:
            findings.append(finding("Q3_VIEWPORT_UNDECLARED", field, f"observed viewport was not declared in Q0: {item['id']}"))
    if not declared_viewports.issubset(observed_viewports):
        missing = sorted(declared_viewports - observed_viewports)
        findings.append(finding("Q3_VIEWPORT_COVERAGE_MISSING", "stages.q3.viewports", f"missing declared viewports: {', '.join(missing)}"))

    observed_states: set[str] = set()
    observed_state_items = q3.get("states")
    if not isinstance(observed_state_items, list) or not observed_state_items:
        findings.append(finding("Q3_STATES_MISSING", "stages.q3.states", "at least one observed state object required"))
        observed_state_items = []
    for index, item in enumerate(observed_state_items):
        field = f"stages.q3.states[{index}]"
        evidence_field = f"{field}.evidence"
        if not isinstance(item, dict) or set(item) != {"id", "evidence"} or not nonempty(item.get("id")) or not relative_path(item.get("evidence")):
            findings.append(finding("Q3_STATE_INVALID", field, "exactly id:string and contained evidence:path required"))
            if isinstance(item, dict) and "evidence" in item:
                check_evidence_path(item.get("evidence"), evidence_field, findings)
            continue
        if item["id"] in observed_states:
            findings.append(finding("Q3_STATE_DUPLICATE", field, f"duplicate observed state id: {item['id']}"))
        observed_states.add(item["id"])
        if item["id"] not in declared_states:
            findings.append(finding("Q3_STATE_UNDECLARED", field, f"observed state was not declared in Q0: {item['id']}"))
    if not required_states.issubset(observed_states):
        missing = sorted(required_states - observed_states)
        findings.append(finding("Q3_STATE_COVERAGE_MISSING", "stages.q3.states", f"missing declared states: {', '.join(missing)}"))

    q4 = require_object(stages, "q4", findings)
    if q4.get("owner") != "eric-review":
        findings.append(finding("Q4_OWNER_INVALID", "stages.q4.owner", "eric-review owner required"))
    verdict = packet.get("verdict")
    if verdict not in VALID_VERDICTS:
        findings.append(finding("VERDICT_INVALID", "verdict", "unsupported formal verdict"))
    if q4.get("verdict") != verdict:
        findings.append(finding("Q4_VERDICT_MISMATCH", "stages.q4.verdict", "Q4 and packet verdicts must match"))
    if "status" not in q4:
        findings.append(finding("Q4_STATUS_MISSING", "stages.q4.status", "documented Q4 status is required"))
    if "reviewer_provenance" not in q4:
        findings.append(
            finding(
                "Q4_REVIEWER_PROVENANCE_MISSING",
                "stages.q4.reviewer_provenance",
                "reviewer provenance is required for every supported verdict",
            )
        )
    if verdict in Q4_COMPATIBILITY and (q4.get("status"), q4.get("reviewer_provenance")) not in Q4_COMPATIBILITY[verdict]:
        code = "SAME_AGENT_READY_FORBIDDEN" if verdict in READY and q4.get("reviewer_provenance") == "same_agent" else "Q4_VERDICT_CONTRACT_INVALID"
        severity = "P0" if verdict in READY else "P1"
        findings.append(
            finding(
                code,
                "stages.q4",
                "Q4 verdict, documented status, and reviewer provenance are incompatible",
                severity,
            )
        )

    permissions = require_object(packet, "permissions", findings)
    for field in ("inspect", "edit", "external_mutation", "publish_send"):
        if not isinstance(permissions.get(field), bool):
            findings.append(finding("PERMISSION_INVALID", f"permissions.{field}", "explicit boolean required"))
    if not nonempty(packet.get("next_action")):
        findings.append(finding("NEXT_ACTION_MISSING", "next_action", "concrete next action required"))
    return findings


def report(findings: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "next_action": (
            "Route the exact build and evidence matrix to a fresh eric-review reviewer."
            if not findings
            else "Repair the listed machine-checkable evidence contract findings, then rerun; Q3/Q4 still require human review."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--no-write", action="store_true", help="Explicitly affirm read-only validation (default behavior).")
    args = parser.parse_args()
    try:
        value = json.loads(args.packet.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("packet root must be an object")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc), "next_action": "Provide a readable JSON object."}))
        return 2

    result = report(validate(value))
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"status: {result['status']}")
        for item in result["findings"]:
            print(f"{item['severity']} {item['code']} {item['field']}: {item['detail']}")
        print(f"next_action: {result['next_action']}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
