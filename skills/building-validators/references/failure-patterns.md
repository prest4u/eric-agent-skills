# Failure Patterns

Use these patterns when auditing an existing validator.

## Looks Strong But Is Weak

- It writes a long report but always exits 0.
- It has no bad fixture proving the main gate catches real defects.
- It mutates files while validating.
- It scans generated reports instead of source artifacts.
- It catches strings but ignores manifest/path/count contracts.
- It produces only Markdown, so CI or agents cannot consume results.
- It says `PASS` while required review evidence is missing.

Fix:

- Add strict severities and non-zero exit.
- Add negative fixtures before changing logic.
- Split rules from code.
- Write JSON and Markdown reports.
- Make next action explicit.

## Common Drift

- Thresholds live in code and become invisible policy.
- Project-specific phrases get copied into unrelated projects.
- Warning counts grow while release still passes.
- Human review is mentioned in prose but not enforced by sentinel.
- Public-facing leak terms are checked in source docs but not final PDFs.

Fix:

- Move thresholds and forbidden terms to rules JSON.
- Keep domain recipes separate.
- Add dated allowlists for accepted warnings.
- Require sentinel files for non-machine review.
- Validate final rendered artifacts, not only source.

## Adversarial Fixtures To Add

- Missing required file.
- Invalid JSON/YAML/schema.
- Duplicate ID/title/chapter.
- Public artifact with internal marker.
- Correct source path but wrong artifact count.
- PDF with low-text/blank page.
- Report claiming full-bank count when completed count is lower.
- Export payload containing raw diagnostics.
- Warning that should fail once release mode is enabled.
