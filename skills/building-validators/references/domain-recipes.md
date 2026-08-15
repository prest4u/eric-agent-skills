# Domain Recipes

Pick the closest recipe, then adapt it to the actual project artifacts. Do not load every recipe into a prompt when only one domain is relevant.

## Teaching And Course Packs

Core gates:

- Source authenticity: real source inventory, no reused AI-produced questions when true papers are required.
- Lesson capacity: time segments sum to target duration; no overlaps/gaps; classroom volume fits the student level.
- Student/teacher separation: student-facing files have no answer keys, teacher tactics, internal labels, source IDs, or private paths.
- Cross-file alignment: lesson plan, materials JSON, student sheets, teacher guide, homework, and answer keys reference the same item IDs.
- Public feedback format: enforce the exact required sections when a project has a feedback contract.
- Final delivery: DOCX/PDF counts, rendered pages, no blanks, visual sample review, package manifest.

Useful negative fixtures:

- Student file containing an answer key.
- Materials JSON ID referenced in a handout but missing from source inventory.
- 120-minute plan with a five-minute gap.
- Formal feedback with an extra section.

## PDF And Document Delivery

Core gates:

- Fresh compile evidence, not stale output timestamps.
- Text extraction succeeds for each PDF.
- Page count, page size, blank/low-text pages, qpdf/pdfinfo checks.
- Full-page renders or contact sheets exist for visual inspection.
- Required visual roles sampled: cover, first body page, dense page, final page.
- Public output has no local paths, process markers, or internal review language.

Human bridge:

- Require a review report sentinel such as `FINAL_VISUAL_REVIEW: PASS` before formal handoff.

## Content, Book, And Novel Projects

Core gates:

- Manifest coverage, chapter count, unique titles/numbers, locked table of contents.
- Source/provenance ledgers for high-risk chapters.
- Continuity probes and known leak phrases.
- Style radar for cliches, meta-outline language, excessive abstraction, overclaiming.
- Machine score only unlocks human reading review; it does not certify literary quality.

Useful negative fixtures:

- Missing chapter in a locked range.
- Duplicate title.
- Backstage phrase like "this chapter mainly".
- Known future-name leak before the character enters.

## Webapps And Product Tools

Core gates:

- Runtime validators for profile, answers, archived records, exported reports, and API boundaries.
- Invalid records are filtered or explained without breaking legal paths.
- Report/export copy counts completed inputs, not full banks.
- Default exports omit raw localStorage or diagnostic snapshots.
- Mobile QA blocks page-level horizontal overflow.
- Lint, typecheck, unit tests, build, audit, and E2E/QA scripts are wired into the release gate.

Useful negative fixtures:

- Archived report object that is shaped like data but cannot render.
- Export payload containing raw diagnostics.
- Mobile viewport with overflowing report section.

## Skills And Plugins

Core gates:

- `SKILL.md` frontmatter has valid `name` and useful `description`.
- Directory name matches skill name.
- No template TODOs or stale platform-specific runtime references.
- Referenced scripts/references/assets exist.
- Scripts have self-tests or representative tests.
- Skill body is concise; heavy detail lives one level deep in `references/`.

Useful negative fixtures:

- Missing `SKILL.md`.
- Literal block scalar description that breaks list renderers.
- `TODO` marker left in a public skill.
- Script referenced in instructions but missing on disk.

## Data And Analytics

Core gates:

- Schema validity before instance validation.
- Required fields, types, row counts, null thresholds, uniqueness, and freshness.
- Metric denominators and filters preserved in reports.
- Exceptions live in dated allowlists with owner and expiry.
- Validation result is machine-readable and can be diffed between runs.

Useful negative fixtures:

- Invalid schema accepted as if it were a data failure.
- Row count drift outside threshold.
- Metric report missing denominator.
- Accepted warning with no owner or expiry.
