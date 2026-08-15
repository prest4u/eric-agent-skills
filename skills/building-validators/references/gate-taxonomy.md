# Gate Taxonomy

Use this taxonomy when deciding what a validator should block, warn, or hand to human review.

## Gate Layers

1. **Artifact contract**: required files, counts, naming, sizes, IDs, manifests, folder boundaries, no symlinks where release artifacts are expected.
2. **Parseability**: JSON/YAML/CSV/schema validity, DOCX/PDF readable, Markdown headings, package manifests, config shape.
3. **Cross-reference integrity**: IDs used in documents exist in source lists; manifest paths exist; answer keys align; chapter numbers and titles are unique.
4. **Boundary safety**: public/student/customer-facing artifacts do not leak internal markers, answer keys, raw diagnostics, personal paths, secrets, or process language.
5. **Domain truth**: source-backed claims, exam-paper provenance, data denominators, continuity facts, scoring normalization, policy dates.
6. **Render/visual evidence**: PDFs rendered, pages counted, blank/low-text pages detected, screenshots/contact sheets archived, mobile overflow tested.
7. **Human-review bridge**: independent review sentinel, human score, dated exception, or next-action queue when machine checks cannot judge quality.
8. **Release action**: explicit status and next allowed action.

## Severity

- `P0`: must block. Trust loss, privacy/internal leak, broken deliverable, missing required artifact, invalid source contract.
- `P1`: normally blocks. Likely user-visible issue, unsupported claim, incomplete required QA evidence, report/export boundary bug.
- `P2`: focused review. Quality risk, density radar, style issue, weak evidence, incomplete warning policy.
- `P3`: sampling radar. Does not imply a change by itself.

## Promotion Rules

Promote a warning to a blocker when:

- It affects public/student/customer-visible output.
- It changes scoring, counts, answer correctness, or provenance.
- It hides behind generated polish or post-hoc explanation.
- The same warning repeats across releases without an allowlist.
- The only evidence is "manual check looked fine" with no artifact.

## Non-Negotiables

- A validator must have at least one negative fixture or self-test for each major gate family.
- A release validator must exit non-zero for strict failures.
- A report must say what is allowed next and what remains outside machine judgment.
