# Frontend delivery evidence contract

Use this machine-readable packet only for `production_create` and `repair`. Store it in the target project's existing QA directory. It records evidence shape; it does not score design, UX, accessibility compliance, or visual quality.

## Required shape

- `schema_version`: `1`.
- `delivery_id`: stable non-empty identifier.
- `route`: `production_create` or `repair`.
- `artifact`: non-empty relative `targets`, `source_identity`, `build_identity`, and a strict `http`/`https` runtime URL whose host is `localhost`, an IPv4 address in `127.0.0.0/8`, or `::1`. Raw C0 controls (`U+0000`–`U+001F`) and DEL (`U+007F`) are rejected before URL parsing. Userinfo, external hosts, ambiguous shorthand addresses, malformed URLs, and other schemes are invalid.
- `q0`: outcome, primary flow, source of truth, non-goals, product surface, framework, design system, asset/dependency policies, explicit design direction, declared viewports/states/accessibility, and acceptance evidence.
- `stages.q1`: owner `frontend-design`, status, and source evidence.
- `stages.q2`: status and exact commands with status and evidence locator.
- `q0.viewports`: unique exact objects `{id, width, height}` with non-empty string IDs and positive integer dimensions; `desktop` and `mobile` are mandatory.
- `q0.states`: unique exact objects `{id, required}` with non-empty string IDs and Boolean required flags.
- `stages.q3`: owner `eric-review`, mode `RECHECK`, matching build identity, runtime evidence, observed viewport/state evidence, and reviewer provenance.
- `stages.q3.viewports` and `stages.q3.states`: unique exact objects `{id, evidence}` with declared IDs and contained relative evidence paths. All declared viewports and all states marked `required: true` must be observed.
- `stages.q3.reviewer_provenance`: `same_agent`, `independent_agent`, or `eric`. This records who performed the rendered visual recheck; it never substitutes for Q4 fresh-independent sign-off.
- `stages.q4`: owner `eric-review`, documented status, reviewer provenance, and verdict. Every verdict requires all three fields.
- `permissions`: explicit booleans for inspect, edit, external mutation, and publish/send.
- `verdict` and `next_action`: strongest honest current state and concrete next step.

Use this Q4 compatibility matrix:

| Verdict | Status | Allowed reviewer provenance |
| --- | --- | --- |
| `READY`, `READY WITH MINOR FOLLOW-UPS` | `pass` | `fresh_independent`, `eric` |
| `PENDING INDEPENDENT REVIEW` | `pending` | `fresh_independent_required` |
| `NOT READY` | `fail` | `same_agent`, `fresh_independent`, `eric` |
| `INSUFFICIENT EVIDENCE`, `BLOCKED_REPAIR_BUDGET` | `blocked` | `same_agent`, `fresh_independent`, `eric` |

Same-agent provenance may record a negative verdict but can never self-sign the READY family. Missing provenance invalidates negative verdicts too.

Every source target and evidence locator must be one canonical, portable, contained project-relative POSIX path. Reject every percent sign (encoded or literal), any raw string that differs from its NFKC normalization, Unicode control category `Cc` (including NUL, C0, and DEL), URI/scheme-like prefixes, POSIX or Windows absolute paths, drive-qualified or drive-relative forms (`C:/`, `C:\\`, `C:relative`), UNC, backslashes, home-relative forms, empty/dot/parent segments, repeated separators, and trailing separators. Apply these rules through the same helper to artifact targets plus every Q1/Q2/Q3 locator. NFKC-stable Unicode segments, including ordinary Chinese, remain valid. Locator findings name only the field and a safe reason; they never echo the submitted value. URLs belong only in `artifact.runtime`.

## Frozen release boundary

Treat every JSON string as malformed/untrusted input. The executable URL contract is limited to raw C0/DEL rejection, strict scheme/authority/host/port parsing, and the explicit loopback allowlist above. The locator contract is exactly the canonical path policy above. Dynamic Codex Skill selection is outside this repository's executable surface and remains `NOT VERIFIED/UNAVAILABLE`. After these contracts are met, only a frozen-contract violation, crash, path escape, privacy leak, or provenance/self-sign bypass is a release blocker; do not expand unclaimed theoretical transformations into new requirements.

## Validator

From the installed Skill directory, invoke the validator through its portable relative path:

```bash
python3 ./scripts/validate_delivery_evidence.py PACKET.json --json --no-write
```

Exit `0` means contract-valid, `1` means findings, and `2` means invalid/unreadable input. JSON output includes `status`, `findings`, and `next_action`; human output includes the same decision. `--no-write` is explicit documentation of the validator's read-only behavior; the script never writes deliverables or reports.

Treat validator `PASS` as “the evidence packet is structurally coherent.” Q3 and Q4 remain human evidence gates.

For an uninstalled repository candidate, run the same command from `skills/eric-frontend-delivery`. Do not copy into or modify a live installation merely to validate a candidate.
