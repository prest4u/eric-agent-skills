# Report Contract

A validator report is evidence, not decoration. Design JSON first, Markdown second.

## JSON Shape

Recommended top-level fields:

```json
{
  "status": "pass|warn|fail",
  "generated_at": "ISO-8601 timestamp",
  "root": "absolute or project-relative root",
  "summary": {
    "counts": {"P0": 0, "P1": 0, "P2": 0, "P3": 0},
    "strict_fail_severities": ["P0", "P1"]
  },
  "issues": [
    {
      "severity": "P1",
      "code": "PUBLIC_FORBIDDEN_TERM",
      "file": "path/to/file.md",
      "line": 42,
      "detail": "why this matters"
    }
  ],
  "next_action": "what the agent or human may do next"
}
```

## Markdown Shape

Include:

- Status and strict threshold.
- Counts by severity.
- Blocking issues first.
- Warning queue second.
- Evidence inventory.
- Human-review requirements.
- Next allowed action.

Avoid:

- "Validated" when the script only scanned a sample.
- "Ready for delivery" when visual, source, or human review gates are missing.
- Hiding warnings below a celebratory summary.

## Status Language

Use precise language:

- Good: "No executable blockers were found; proceed to human visual review."
- Bad: "Final quality is 10/10."
- Good: "PDF text and page-count checks passed; manual contact-sheet review remains required."
- Bad: "PDF QA passed" when only compilation ran.

## Evidence

For formal delivery, reports should point to stable evidence paths:

- Raw machine JSON.
- Human-readable report.
- Rendered screenshots/contact sheets when visual QA matters.
- Independent review sentinel when machine judgment is insufficient.
- Dated warning allowlist when warnings are accepted.
