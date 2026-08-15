# Code Review Lens

Use this for code changes, PRs, diffs, APIs, scripts, dependencies, config, and tests.

## Required Checks

- Requirements/spec alignment: implemented behavior matches the request; no missing or extra risky behavior.
- Correctness: edge cases, error paths, async/race behavior, state transitions, data loss.
- Security: authz/authn, user input, path traversal, injection, secrets, SSRF, unsafe deserialization, dependency risk.
- Tests: real behavior covered; regression tests for fixes; mocks do not replace meaningful behavior; relevant checks pass.
- Interactive release behavior: unit tests, source inspection, and snapshot hashes do not replace build-matched browser/runtime evidence; route the visible journey to `ui-ux-review.md`.
- Maintainability: clear boundaries, local conventions, types, error handling, simple design, no unrelated refactors.
- Production readiness: migrations, compatibility, observability, performance, rollback risk where relevant.

## Evidence Requirements

- Cite file and line when possible.
- For diffs, inspect both changed code and nearby call sites.
- For security findings, show the exploit path or trust boundary.
- For test findings, name the missing scenario and the command/check that should cover it.

## Severity Calibration

- P0: exploitable security issue, data loss, broken core behavior, secret exposure, destructive migration, release blocker.
- P1: missing required behavior, meaningful regression risk, inadequate tests for risky code, poor error handling.
- P2: maintainability, performance, or observability improvement that does not block delivery.
- P3: style or naming polish.

## Reviewer Non-Scope

Do not review teaching quality, visual aesthetics, product-flow usability, or video retention unless the code directly generates those artifacts. Route interactive UI/UX separately even when its source code is in the same diff.
