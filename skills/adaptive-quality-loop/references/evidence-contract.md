# Quality packet contract

Q2/Q3 work requires a JSON quality packet; Q0 must not create one and Q1 uses one only when project convention requires it.

Required top-level fields: `schema_version: 1`, `task_id`, `phase`, `artifact`, `risk`, `acceptance`, `gates`, `failures`, `review`, `permissions`, and `next_action`.

Valid phases are `preflight`, `build`, `verify`, `review`, and `recheck`. Machine findings use `P0`, `P1`, `P2`, or `P3`; P0/P1 are contract blockers.

- `artifact`: type, exact targets, identity/hash/version, delivery channel.
- `risk`: Q0-Q3 tier, observed signals, rationale.
- `acceptance`: non-empty stable IDs, non-empty observable criteria, and a Boolean required flag.
- `gates`: non-empty stable ID and kind, valid status, Boolean required flag, and a meaningful current evidence locator (a non-empty locator string, or a locator-keyed mapping/list).
- `failures`: complete, semantically populated failure fingerprints from `failure-loop.md`; partial, empty-valued, out-of-order, or counter-reset fingerprints are invalid.
- `review`: required flag, provenance (`same_agent`, `independent_agent`, or `eric`), verdict.
- `permissions`: separate inspect, edit, external mutation, and publish/send authority.
- Q3 additionally requires structured `approval_evidence` with status; Q3 readiness accepts only a positive structured status (`granted`, `approved`, or `authorized`) whose approver is Eric. External/destructive work also records recovery evidence.

Gate statuses are `not_run`, `pass`, `fail`, `blocked`, or `not_applicable` with rationale. A pass/fail requires a non-empty current evidence locator. A required gate must pass before READY. Every permission subfield is explicit; missing permission data never implies authority.

Both `READY` and `READY WITH MINOR FOLLOW-UPS` are formal readiness verdicts: Q2/Q3 cannot use same-agent provenance. Q3 readiness requires positively granted approval; merely recording `not_granted` is not approval. Migration, destructive, deploy, publish, upload, and external-mutation readiness also requires recovery evidence.

The repair budget is enforced across normalized fingerprints, not finding IDs. Attempts after one require a stable criterion and complete, contiguous preceding records for that normalized group; omitted history or counter jumps are invalid. Repeating the same failure requires strictly increasing timezone-aware timestamps and counters, plus diagnosis unless the root-cause evidence adds a locator not already recorded for the group. A third implementation attempt requires both that new evidence and structured positive Eric authorization such as `{"status":"granted","by":"Eric"}`; free-form approval text is invalid.

Validate deterministically:

```bash
python3 -B scripts/validate_quality_packet.py PACKET --json
```

Exit 0 means contract-valid, 1 means contract findings, 2 means unreadable/invalid JSON. The validator checks packet consistency only; it cannot judge semantic, visual, source, or business quality.

Store persistent Q2/Q3 packets under the project's existing QA directory or `qa/quality/`. Never create QA files for Q0. Treat installed plugin caches as read-only. If a packet would expose private content, store minimal locators/hashes and redact evidence.

Verdicts: `READY`, `READY WITH MINOR FOLLOW-UPS`, `PENDING INDEPENDENT REVIEW`, `INSUFFICIENT EVIDENCE`, `BLOCKED_REPAIR_BUDGET`, `NOT READY`. Same-agent Q2/Q3 work cannot claim independent sign-off.
