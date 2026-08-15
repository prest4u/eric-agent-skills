# Production Workflow

Use this reference for the operational path from source material to final PDFs.

## Default Book Identity

The default Eric-designed book is a generic no-student-name edition: a course book, prep plan, workbook, handbook, or teacher/student package that can stand on its own without a specific learner name. Personalized editions are allowed only when the user explicitly asks for one.

For no-student-name editions, do not leave student/test names in:

- `book.yaml` title/subtitle/output paths
- `pages/*.md`
- generator scripts and renderer labels
- `assets/manifest.json` ids, paths, `content_brief`, `visual_direction`, or `uniqueness_note`
- generated HTML
- extracted PDF text
- output filenames
- rendered cover/title/key pages

Sample Learner is a regression/test case for validating the system, not the default identity of the skill. If a generic edition is derived from a personalized test project, remove the name at the generator/source layer first, regenerate pages and manifest, rebuild both profiles, and scan all layers before delivery.

Generic editions also need a positive identity pass. Removing the name is not enough. For final delivery, `book.yaml` should include:

```yaml
identity:
  cover_title: "Evidence Before Score"
  positioning: "A generic IELTS workbook that turns score anxiety into visible daily proof."
  audience: "IELTS Academic students"
  front_matter_role: "Cover, title page, and map establish the book promise, scope, and practice rhythm."
```

Avoid using a bare functional label such as `备考计划`, `学习计划`, `student workbook`, or `A4 lesson pack` as the whole visible identity. Those phrases can appear as subtitle/meta, but the cover/title should carry a stronger book name or series lockup. Machine QA reports `GENERIC_BOOK_IDENTITY_WEAK` when a final generic book lacks this identity layer.

For long books, page-family coverage is not the same as book rhythm. A 100+ page build must still alternate visible page roles across the contact sheet. Do not allow long stretches of planner/final-check/exam/practice forms without editorial anchors such as unit openers, article/evidence pages, photo passages, handbook/reference pages, or answer-key back matter. Machine QA reports `PAGE_ROLE_RHYTHM_WEAK` as a review queue.

## Source Interfaces

- `book.yaml`: book title, subtitle, level, unit metadata, output profiles, and page order.
- `pages/*.md`: one page per source file; YAML frontmatter controls template and component data.
- `assets/manifest.json`: image registry with id, path, use role, source/generation status, dimensions, and cover concept fields.
- `theme/tokens.json`: color, typography, and line-system tokens.

For large structured exam courses, prefer source-data generation over document reskinning. Read `lesson_plan.json`, `question_bank.json`, `passage_bank.json`, and `writing_bank.json`; map each block to page roles before writing `pages/*.md`; and write the generated/adaptation review into the delivery folder. Keep the original DOCX/PDF untouched and use a new delivery directory.

## Asset Modes

Set the project asset mode in `book.yaml` before QA:

```yaml
qa:
  asset_mode: proof-placeholder   # layout/design-transfer proof only
```

Use `proof-placeholder` only while checking page grammar, typography, blanks, and component rhythm. The final pass must switch to:

```yaml
qa:
  asset_mode: final-assets
```

In `final-assets` mode, every cover, unit-opener, photo-passage, context, or hero visual must be either `kind: imagegen` or a licensed/owned original. ImageGen assets must be generated as bitmap context only, copied into the project, and registered with `status: approved_final`, `prompt` or `generation_prompt`, `source_note`, `focus`, dimensions when known, `allowed_templates`, and `text_policy` stating no visible text and no questions/answers/teaching body. Final generated visuals must also be immediately understandable real-world imagery. Prefer nature, landscape, wildlife, and realistic animal photographs when the content can support that mood; use campus/classroom/library/study scenes or modern human learning/life scenes as the second family. Do not use abstract paper sculptures, symbolic decision boards, token maps, floating strips, concept-art contraptions, procedural rasters, starter/sample/proof images, drafts, placeholders, or temporary mocks as final visuals.

One image may be used once only. Do not reuse the cover image as the unit opener or photo-passage image, even if the image is beautiful or thematically close. Use separate asset ids, separate image files, and separate manifest records:

```json
[
  {"id": "unit-cover", "role": "cover_hero", "allowed_templates": ["cover"]},
  {"id": "unit-opener", "role": "unit_opener", "allowed_templates": ["unit-opener"]},
  {"id": "unit-passage", "role": "photo_passage", "allowed_templates": ["photo-passage"]}
]
```

The validator blocks repeated asset ids across pages, multiple asset ids pointing to the same image path, cover assets used inside the book, and page templates outside `allowed_templates`.

Cover/hero assets need three additional fields before final delivery:

```json
{
  "content_brief": "What this book/lesson is actually about.",
  "visual_direction": "The specific cover idea as a real scene: nature/landscape/wildlife/animal first when suitable, otherwise campus/classroom/library/study or modern human learning/life setting, mood, and composition.",
  "uniqueness_note": "How this cover differs from prior/course-generic covers."
}
```

Write these fields before calling ImageGen. A grammar transition, IELTS writing plan, reading unit, and vocabulary workbook should not all receive the same generic desk, abstract gradient, or textbook-stack image. The cover prompt should grow out of the source material while staying in a real-world visual family Eric can immediately understand. If the written brief uses terms such as abstract, symbolic, conceptual, paper sculpture, decision map, token board, floating strips, or evidence board, rewrite it before generation unless Eric explicitly asked for that direction; otherwise `FINAL_ASSET_UNINTERPRETABLE_SCENE` should block final QA.

## Output Profiles

- `book-trim`: custom textbook trim, about `594.96 x 761.133 pt`.
- `lesson-a4`: A4 adaptation of the same HTML content layer.
- `student-lesson-a4` / `teacher-lesson-a4`: default independent lesson-pack delivery route. Use these two profiles when Eric asks for one lesson at a time or an A4-only course delivery.
- `student-book-trim` / `teacher-book-trim`: full-book route only when Eric explicitly wants book-trim or both A4 and book-trim.
- `typst-adapter`: A4 proof route for classroom handouts, checked through explicit `$eric-pdf` invocation when Eric requests that adapter/QA step.

If Eric asks for a full book / 教材全书 / book-like course without naming the output profile, ask whether the delivery should be `A4`, `book-trim`, or both before scaffolding. If `qa.output_mode: a4-only` is set, `book.yaml`, profile names, output paths, and visible PDF text must not contain `book-trim` residue.

Custom A4 profiles that do not contain `lesson-a4` in the profile name, such as `practice-companion-a4`, need an explicit optical pass. Do not assume they inherit all `.profile-lesson-a4` cover/body/opener proportions. Either add a shared A4 profile class in the renderer or add profile-specific CSS for body inset, cover title scale, opener band height, and photo-passage height, then inspect p1, p3, and one dense workbook page at full rendered PNG size.

## Custom Project QA Config

When a project changes page count, output names, or template names, keep the skill validator in the loop by adding `qa` and output paths to `book.yaml`:

```yaml
qa:
  asset_mode: final-assets
  answer_visibility: student   # student | student-with-answer-key | teacher
  min_pages: 14
  max_pages: 14
  required_templates:
    - cover
    - title-route
    - contents-route
    - unit-opener
    - method-card
    - workbook-practice
    - handbook-page
  required_components:
    - cover
    - unit-opener
    - objectives-band
    - method-card
    - workbook-practice
    - handbook-page
profiles:
  book-trim:
    output_html: outputs/IELTS_Prep_Plan_Unit01_book-trim.html
    output_pdf: outputs/IELTS_Prep_Plan_Unit01_book-trim.pdf
    qa:
      answer_visibility: student
```

Use `answer_visibility: student` for clean student PDFs; it blocks both `answer-key` and `teacher-answer-key` pages. Use `student-with-answer-key` only for an intentional student answer-key edition; it still blocks teacher-only pages. Use `teacher` for teacher profiles or teacher-only answer packages.

Page frontmatter can also route a page before rendering:

```yaml
---
template: teacher-answer-key
section: backmatter
audience: teacher
include_profiles: [teacher-book-trim]
exclude_profiles: [book-trim, lesson-a4]
---
```

Use `audience: teacher` for teacher-only notes, answer keys, and internal checking pages. Use `include_profiles` or `exclude_profiles` only when one page truly belongs to a named edition. The starter v2 builder applies this filter before HTML rendering, so clean student profiles do not get teacher pages and visible page numbers remain consecutive.

Do not create a project-local validator that omits component coverage, leak scans, asset checks, rendered-page evidence, or visual-review parsing.

## Starter Project

Create a new project:

```bash
python3 ./scripts/new_project.py --out <project-dir> --title "<book title>" --profiles book-trim,lesson-a4 --include-typst
```

For independent A4 lesson packs, scaffold:

```bash
python3 ./scripts/new_project.py --starter v2 --out <project-dir> --title "<lesson title>" --profiles student-lesson-a4,teacher-lesson-a4
```

For student/teacher edition testing, pass named profiles:

```bash
python3 ./scripts/new_project.py --starter v2 --out <project-dir> --title "<book title>" --profiles student-book-trim,teacher-book-trim --include-typst
```

Names containing `student` receive `answer_visibility: student` and student QA requirements without teacher-key pages. Names containing `teacher` receive `answer_visibility: teacher`. Names containing `lesson-a4` or ending in `-a4` inherit A4 dimensions; other names inherit book-trim dimensions.

Then edit:

1. `book.yaml` for metadata and page order.
2. `pages/*.md` for content and template data.
3. `assets/manifest.json` for image governance.
4. `theme/tokens.json` only when the visual system needs a deliberate variant.
5. `tools/build.py` and `typst-adapter/` labels when the default starter wording would leak into the custom book.

Before first build, remove starter identity from custom projects. The skill validator flags `STARTER_RESIDUE_FOUND` when non-starter projects still contain `Pathways to Better Writing`, `English Writing System`, `Sentences, Paragraphs, and Writing Practice`, starter canyon assets, or starter paragraph titles in active source or rendered output. Set `qa.allow_starter_residue: true` only for the original starter sample.

Before final delivery, run an asset generation pass. Generate or source the cover/opener/context visuals from content-specific real-world briefs, one image per page role, inspect that they contain no fake typography, watermarks, or hard-to-explain abstract symbols, record their manifest metadata, then rebuild from source. Start briefs from landscape, nature, wildlife, or realistic animal photography when the content can support that mood; use campus/classroom/library/study or modern-life scenes only when those fit the material better, and record `family_rationale` or `nature_first_rationale` for that second-family choice. If this pass has not happened, label the output as a proof rather than a final book.

## Build Loop

For each profile:

```bash
python3 tools/build.py --profile <profile>
python3 tools/render_pdf.py --profile <profile>
python3 tools/validate.py --profile <profile>
pdftotext outputs/<profile-output>.pdf _qa/extracted-<profile>.txt
python3 <eric-teaching-polish-dir>/scripts/validate_teaching_polish.py --strict _qa/extracted-<profile>.txt
python3 ./scripts/qa_textbook_pdf.py --root . --profile <profile>
```

Formal delivery uses `--require-human-review` after a visual review file exists.
The report files are intentionally separate: the normal executable QA report is `_qa/textbook-qa-<profile>.md/json`, while the formal visual-release gate is `_qa/textbook-qa-<profile>-release.md/json`. Run both when preparing handoff evidence. A failed release gate should not overwrite the P0/P1-clean machine QA evidence; it should sit beside it and explain why visual release is still blocked.
For student-visible Chinese or mixed-language teaching materials, the extracted-text polish scan is mandatory. Visible `Route`, `主动作`, `Repair`, `维修`, `路由`, `后台`, or `闭环` is a release blocker. For custom projects, `STARTER_RESIDUE_FOUND` is also a release blocker.

## Human Review Sentinel

When machine checks pass, inspect the contact sheet and representative rendered pages. Write `_qa/visual-review-<profile>.md` with:

```text
FINAL_VISUAL_REVIEW: PASS
Reviewer: user-confirmed or independent-review
Score: 9.5/10
P0: 0
P1: 0
Checked: cover, unit opener, dense rules page, activity page, writing page, handbook/answer key
Contact sheet: _qa/contact-sheet-<profile>.png
Key pages: _qa/rendered-pages/<profile>-page-001.png, _qa/rendered-pages/<profile>-page-002.png, _qa/rendered-pages/<profile>-page-006.png, _qa/rendered-pages/<profile>-page-010.png
Canon comparison: compared against golden p1 cover, p3 opener, p4 elements, p6 paragraph practice, p9 handbook.
Reject patterns checked: thin-cover-type, title-wrap-break, dashboard-panel, ui-number-block, component-collage, patch-drift, form-repeat, student-process-language.
Font decision: B modern sans primary; C system clean fallback; A rejected if title appears thin.
Visual diagnosis: state why the page set now reads as a book, not a repeated form template.
Weak pages: name the weakest page(s), or write none only after checking the rendered page image.
Remaining risk: none
```

The validator rejects missing reviewer provenance, same-agent/self review labels, fewer than four checked page roles, missing render evidence, missing canon comparison, missing reject-pattern check, missing font decision, or missing diagnosis fields when `--require-human-review` is used. Do not fabricate user confirmation.

## Typst Adapter

Compile:

```bash
typst compile typst-adapter/lesson-a4-template.typ outputs/textbook-template-lesson-a4-typst-adapter.pdf
```

When Eric separately requests the adapter/QA step, invoke `$eric-pdf` and run its current `qa_typst_a4.py` workflow with `--require-visual-checks`. Treat this as a separate A4 proof route, not a replacement for the HTML book engine.
