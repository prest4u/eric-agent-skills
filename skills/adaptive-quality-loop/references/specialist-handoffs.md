# Specialist handoffs

Pass explicit unknowns; never invent missing fields.

## data-analytics:validate-data

Validation question; audience/decision; exact artifacts/version; sources/as-of; population/grain/filters/exclusions; formulas/denominators/units/timezone; windows/baseline; claims/recommendations; SQL/notebook/sheet/dashboard evidence; recomputed values/traced records; rendered evidence; caveats/unavailable checks; requested share verdict.

Use for analysis, metric, chart, recommendation, or decision-claim review—not merely because a CSV exists.

## building-validators

Project root and existing validator inventory; finding IDs to make durable; artifact/release contract; captured bad behavior; one good and bad fixture per gate family; project-native language/test/CI; strict severities/release boundary; machine fields/human next action; no-write/path safety; acceptance commands.

Use only when the check must be repeatable, executable, and reusable. Prefer native frameworks; use the Python scaffold only when none is usable.

## eric-review

Mode/question; allowlist/exclusions/identities; authoritative requirements; audience/channel/stage/deadline; evidence matrix; finding IDs/fix claims; separate permissions; privacy/redaction; reviewer provenance; required decision/sign-off.

An implementer returns `PENDING INDEPENDENT REVIEW` when other gates pass but the changed artifact lacks independent or Eric approval.

## Missing specialist

Resolve availability from the current runtime inventory, not filesystem cache presence. Record the requested Skill and availability result.

For Q0/Q1, use the strongest native evidence and state the missing route. For Q2/Q3, return `INSUFFICIENT EVIDENCE` or the stronger blocker—never silently claim equivalence. Never copy a plugin Skill into a local fallback.
