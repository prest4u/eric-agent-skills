# Optional RELEASE record

Use this record only when an explicit formal delivery contract requires a machine-readable release record. BUILD and PROOF do not create one. It documents release evidence; it is not another approval workflow.

The current `scripts/validate_quality_packet.py` accepts this shape:

- `schema_version`: integer `1`.
- `mode`: exactly `RELEASE`.
- `artifact`: non-empty string `target` and non-empty string `identity`.
- `authority`: `status` granted/approved/authorized, non-empty `by`, and non-empty `scope` for the intended action.
- `recovery`: `available: true`, non-empty `method`, and non-empty `evidence`.
- `checks`: a non-empty list of objects with non-empty `name`, passing `status`, and non-empty `evidence`. Include the checks required for this release.
- `review`: non-empty distinct `producer` and `reviewer`, `independent: true`, and `verdict` READY or READY WITH MINOR FOLLOW-UPS.
- `findings`: optional list with `severity` P0/P1/P2/P3 and `status` open/closed. Open P0/P1 findings prevent a ready record.

Example of the field structure (illustrative locators must be replaced with actual evidence):

```json
{
  "schema_version": 1,
  "mode": "RELEASE",
  "artifact": {"target": "release/package", "identity": "candidate-version"},
  "authority": {"status": "granted", "by": "Eric", "scope": "specified delivery action"},
  "recovery": {"available": true, "method": "restore previous version", "evidence": "recovery-evidence"},
  "checks": [{"name": "required acceptance", "status": "PASS", "evidence": "current-evidence"}],
  "review": {"producer": "implementer", "reviewer": "independent-reviewer", "independent": true, "verdict": "READY"},
  "findings": []
}
```

Earlier documentation used a different field structure with the same schema number. Existing consumers must use the executable contract above; do not infer compatibility from the number alone. Historical records remain historical evidence and must not be relabeled as current release approval.

When a record is explicitly required, run `python3 scripts/validate_quality_packet.py RECORD --json` from this Skill directory. Exit 0 means structurally valid, 1 means findings, and 2 means unreadable/invalid JSON. Structural validity cannot prove the evidence is true, the product is correct, or the reviewer was actually independent.

Missing authority, recovery, passing checks, or independent review must remain visible as a pending or blocked release. Never invent them to make the validator pass. Ordinary local delivery is not dependent on this record.
