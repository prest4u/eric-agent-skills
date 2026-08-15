# Fresh independent closeout

Send a fresh `$eric-review` task this exact packet:

```text
Mode: FORMAL_SIGNOFF
Question: Is this exact frontend build ready for the stated formal delivery?
Targets and source/build identity:
Authoritative requirements and Q0 acceptance IDs:
Audience, product surface, primary flow, channel, and stage:
Explicit exclusions and non-goals:
Permissions: inspect / edit / external mutation / publish-send
Q2 commands, exits, and evidence locators:
Q3 runtime URL, viewports, states, accessibility checks, visual report, and evidence locators:
Known findings, accepted risks, missing evidence, and reviewer conflicts:
Privacy/redaction boundary:
Requested verdict and sign-off:
```

Require the reviewer to inspect the actual current artifact, run or verify the mandatory evidence, cite exact route × viewport × state locators, state coverage and unreviewed surfaces, and report verdict separately from sign-off. The review is read-only and grants no deploy, publish, send, upload, merge, or external-mutation authority.

Accept `READY` or `READY WITH MINOR FOLLOW-UPS` only from a fresh independent reviewer using `eric-review` or from Eric. Same-agent, stale-build, source-only, validator-only, or partial-runtime approval is invalid. When all other gates pass without that provenance, use `PENDING INDEPENDENT REVIEW`.

Require documented Q4 status and reviewer provenance for every verdict, including negative or blocked outcomes. Same-agent provenance may report `NOT READY`, `INSUFFICIENT EVIDENCE`, or `BLOCKED_REPAIR_BUDGET`; it may not sign either READY-family verdict.
