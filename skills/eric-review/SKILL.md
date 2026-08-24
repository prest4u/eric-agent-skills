---
name: eric-review
description: 【独立评审】Use only when Eric explicitly asks to review, critique, check, audit, review-and-fix, or formally sign off an existing artifact. Supports QUICK_REVIEW, REVIEW_AND_FIX, and FORMAL_SIGNOFF. Do not invoke before an artifact exists and do not use as a default completion gate.
---

# Eric Review

Inspect the actual artifact and answer the decision Eric asked for. Review should shorten the path to a usable result.

## Choose one mode

| Mode | Use | Mutation |
| --- | --- | --- |
| `QUICK_REVIEW` | Default for check, critique, or review | Read-only unless Eric also asks for fixes. |
| `REVIEW_AND_FIX` | Eric asks to review and deliver/fix | The same agent may inspect, edit the named surface, and run one recheck. |
| `FORMAL_SIGNOFF` | Eric explicitly asks for approval, release readiness, or the action is high-impact | Read-only review of a frozen identity by an independent reviewer. |

If no inspectable artifact exists, stop the review and build or request the missing artifact. Do not review a plan as a substitute for the requested product.

## QUICK_REVIEW

1. Identify the exact artifact and the decision being requested.
2. Inspect the source, render, runtime, or other evidence that the acceptance criterion actually requires.
3. Lead with correctness, security, regression, usability, and missing-test issues.
4. Return a concise verdict, blocking findings, important non-blocking risks, and what was not checked.

Use exact file and line locators when available. Do not require a preflight form, artifact-by-lens matrix, seven-section report, persistent packet, or independent reviewer.

## REVIEW_AND_FIX

1. Inspect the named artifact and identify the smallest set of blocking or high-value changes.
2. Apply only the edits Eric authorized; preserve unrelated work.
3. Run one targeted recheck against the changed surface and adjacent boundary.
4. Deliver the repaired artifact with the check evidence and remaining non-blocking issues.

Do not pause between audit and repair unless the fix expands scope, changes product intent, creates material cost, or requires external authority.

## FORMAL_SIGNOFF

1. Freeze the exact artifact, commit, build, or checksum.
2. Confirm authoritative requirements, required evidence, inspect authority, and reviewer independence.
3. Inspect every mandatory source, render, runtime, browser, playback, or current-source gate.
4. Block on open P0/P1 issues or missing mandatory evidence.
5. Report verdict and sign-off separately. Sign-off never authorizes publish, deploy, send, upload, migration, or destructive action.

The producer cannot grant formal READY to its own artifact. Use one independent reviewer or return `PENDING INDEPENDENT REVIEW`; never create a review-of-review chain. Load a matching file from `references/` only when a formal domain lens is genuinely required.

## Verdicts

- `NOT READY`: a known P0/P1 or stop-ship defect exists.
- `INSUFFICIENT EVIDENCE`: no known blocker, but a mandatory gate was not checked.
- `PENDING INDEPENDENT REVIEW`: the artifact otherwise passes but lacks required independent sign-off.
- `READY WITH MINOR FOLLOW-UPS`: mandatory evidence passes and only P2/P3 work remains.
- `READY`: all required evidence passes with no open finding.

For QUICK_REVIEW and REVIEW_AND_FIX, plain-language equivalents are acceptable. Never manufacture findings to fill a template.
