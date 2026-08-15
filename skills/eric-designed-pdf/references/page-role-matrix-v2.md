# Page Role Matrix V2

Use this reference when a project must move beyond the v1 8-12 page proof and cover the recurring page forms of a 100+ page student book, workbook, handbook, answer-key package, or lesson-a4 adaptation.

This matrix is an abstraction layer. It absorbs form grammar from Eric's reference books and validation projects without copying protected logos, passages, images, exercises, or whole-page layouts. All instructional text, exercises, answers, tables, captions, and blanks stay deterministic HTML/Typst text.

## Coverage Contract

For full-coverage validation, set:

```yaml
qa:
  page_family_mode: v2-full
```

`qa_textbook_pdf.py` then enforces `V2_PAGE_FAMILY_COVERAGE_MISSING` when the rendered HTML does not contain the required page families. A v2 gallery should normally be 24-32 pages; a shorter project may use selected v2 templates but should not claim full coverage.

## Front Matter

| Template | Required Components | Visual Role | Asset Rule | Failure Labels | QA Checks |
| --- | --- | --- | --- | --- | --- |
| `cover` | `cover`, `cover-brand` | Full-bleed book identity, heavy title lockup, bottom-right Eric Teaching Studio | one-use `cover_hero`, `allowed_templates: ["cover"]` | `thin-cover-type`, `title-wrap-break`, `mixed-title-scale-drift`, `cover-brand-missing`, `cover-stage-badge`, `generic-cover-art`, `cover-image-reuse` | cover brand, title lockup, final asset metadata |
| `title` | `title-page`, `title-navigation` | Quiet editorial title and scope positioning | no required image | `mixed-title-scale-drift`, `empty-title-page`, `student-process-language` | title scale, starter residue, visible language |
| `contents-route` | `title-navigation`, `scope-map`, `unit-folio` | Useful table of contents / unit route without dashboard panels; should include a visible second layer such as scope proof, page-family map, or next-step strip | no image | `dashboard-panel`, `ui-number-block`, `validation-gallery-sparsity`, `starter-residue` | component coverage, visible language |
| `scope-map` | `diagram-callout`, `unit-folio` | Compact map of course scope, units, or exam modules | diagram is deterministic CSS/HTML unless a licensed context visual is registered | `component-collage`, `exercise-taxonomy-flat` | layout overflow, component coverage |
| `diagnostic-entry` | `section-ribbon`, `guided-mcq-set`, `workbook-record` | Opening check that sends students into the unit | no decorative image unless one-use context asset is justified | `diagnostic-form-drift`, `loose-workbook-tail` | workbook record, student-book form coverage |

Full v2 front-matter coverage requires at least `contents-route` and `diagnostic-entry` in addition to normal cover/title pages.

## Unit Opening

| Template | Required Components | Visual Role | Asset Rule | Failure Labels | QA Checks |
| --- | --- | --- | --- | --- | --- |
| `unit-opener` | `unit-opener`, `objectives-band` | Photo-led unit start with objectives band | one-use `unit_opener`, not the cover image | `stacked-opener`, `cover-image-reuse` | asset usage, rendered contact sheet |
| `article-opener` | `article-title-lockup`, `lettered-paragraph`, `vocab-highlight` | Concept/article opener with real reading or problem texture | optional one-use context visual | `article-form-missing`, `raster-book-drift`, `a4-reading-airiness` | deterministic text, page family coverage, A4 density review |
| `article-evidence` | `definition-footnote`, `diagram-callout` or evidence field, optional evidence/check record | White article / inset evidence page for long-sentence or grammar transfer; should not stop at diagram + notes when the source has learner evidence rows | one-use evidence/context visual if used | `article-form-missing`, `validation-gallery-sparsity`, `cover-image-reuse`, `rendered-text-glitch` | asset uniqueness, text extraction |

Full v2 unit-opening coverage requires `unit-opener`, `article-opener`, and `article-evidence`. In multi-unit books, `unit-opener` pages also need per-unit `opener_accent`, `opener_band`, and `opener_layout` metadata so the contact sheet does not show cloned openers; six-unit books should show at least two opener structures and three accent families.

## Teaching Core

| Template | Required Components | Visual Role | Asset Rule | Failure Labels | QA Checks |
| --- | --- | --- | --- | --- | --- |
| `skill-method` | `section-ribbon`, `skill-side-label`, `mechanics-table`, optional `guided-discovery` / method application strip | Compact method page: rule, model, application, transfer strip | no image by default | `skill-ribbon-missing`, `validation-gallery-sparsity`, `student-process-language` | component coverage, polish scan |
| `grammar-rule` | `mechanics-table`, `definition-footnote` | Rule explanation with examples and decision cues | no image by default | `weak-backmatter`, `rendered-text-glitch` | table overflow, text extraction |
| `model-annotation` | `lettered-paragraph`, `vocab-highlight`, `workbook-record` | Worked sentence/paragraph annotation | no image by default | `diagnostic-form-drift`, `floating-blank-line` | blank baseline, workbook record |
| `sentence-map` | `diagram-callout`, `categorizing-chart` | Clause map / relationship chart / sentence skeleton | deterministic CSS/HTML diagram | `component-collage`, `exercise-taxonomy-flat` | layout overflow, rendered PNG check |
| `guided-discovery` | `guided-mcq-set`, `critical-thinking-strip` | Example -> question -> learner inference | no image by default | `skill-ribbon-missing`, `question-line-double-blank` | question-line gate, component coverage |

Full v2 teaching-core coverage requires `skill-method` and `sentence-map`; projects should add `grammar-rule`, `model-annotation`, or `guided-discovery` when the source lesson needs them.

## Practice

| Template | Required Components | Visual Role | Asset Rule | Failure Labels | QA Checks |
| --- | --- | --- | --- | --- | --- |
| `activity` | `activity-block`, `word-box`, `workbook-practice` | Core workbook practice page | no image by default | `loose-workbook-tail`, `orphan-slot-line` | workbook record, blank baseline |
| `workbook-record` | `workbook-record`, `unit-folio` | Dedicated practice evidence record | no image | `diagnostic-form-drift`, `floating-blank-line` | record prompt blank rules |
| `connector-bank` | `practice-word-box`, `categorizing-chart` | Compact choice bank / collocation / connector practice | no image | `orphan-slot-line`, `exercise-taxonomy-flat` | compact no-wrap blanks |
| `categorizing-chart` | `categorizing-chart`, `skill-side-label` | Error/evidence grouping table; row language must match the current skill/topic, not a rotated starter table | no image | `exercise-taxonomy-flat`, `plain-planner-table`, `topic-template-drift` | table overflow, component coverage, topic-specific row review |
| `sentence-transformation` | `workbook-record`, `mechanics-table` | Rewrite/merge/transform sentences | no image | `question-line-double-blank`, `floating-blank-line` | question-line and blank gates |
| `mixed-timed-drill` | `guided-mcq-set`, `critical-thinking-strip` | Timed mixed practice | no image | `diagnostic-form-drift`, `ui-number-block` | visible language, component rhythm |
| `exam-mini-set` | `guided-mcq-set`, `workbook-record` | Exam-style mini set with answer separation | no image | `answer-leakage`, `exercise-taxonomy-flat` | leak scan, teacher/student profile |

Full v2 practice coverage requires `activity`, `categorizing-chart`, and `exam-mini-set`.

## Reading / Transfer

| Template | Required Components | Visual Role | Asset Rule | Failure Labels | QA Checks |
| --- | --- | --- | --- | --- | --- |
| `photo-passage` | `photo-passage`, `activity-block` | Context visual plus short deterministic response prompts | one-use `photo_passage` / context image, not cover/opener | `cover-image-reuse`, `question-line-double-blank` | asset uniqueness, question-line gate |
| `long-sentence-transfer` | `lettered-paragraph`, `diagram-callout` | Long-sentence reading-to-grammar transfer | optional one-use context/evidence visual | `article-form-missing`, `rendered-text-glitch` | text extraction, layout overflow |
| `comprehension-check` | `guided-mcq-set`, `skill-side-label` | Main idea/detail/inference or grammar equivalent | no image | `skill-ribbon-missing`, `exercise-taxonomy-flat` | component coverage |
| `evidence-annotation` | `vocab-highlight`, `definition-footnote`, `workbook-record` | Deterministic annotation of evidence | no image by default | `raster-book-drift`, `student-process-language` | text extraction, polish scan |
| `critical-thinking` | `critical-thinking-strip`, `workbook-record` | Reflection/transfer strip with short output | no image | `loose-workbook-tail` | workbook record |

Full v2 reading-transfer coverage requires `photo-passage` and `article-evidence`; longer books should add `long-sentence-transfer` or `evidence-annotation`.

## Writing / Output

| Template | Required Components | Visual Role | Asset Rule | Failure Labels | QA Checks |
| --- | --- | --- | --- | --- | --- |
| `writing-planner` | `writing-planner`, `editing-checklist` | Tactile planner rows, not spreadsheet table | no image | `plain-planner-table`, `planner-label-blank-weak` | planner surface, checklist selector |
| `paragraph-practice` | `paragraph-practice`, `activity-block` | Model passage and stable answer lines | no image | `floating-blank-line`, `rendered-text-glitch` | paragraph cloze blank override |
| `correction-rewrite` | `workbook-record`, `editing-checklist` | Error correction -> rewrite output | no image | `control-selector-leak`, `loose-workbook-tail` | checklist selector, workbook record |
| `final-check` | `editing-checklist`, `critical-thinking-strip` | End-of-unit final check | no image | `control-selector-leak`, `student-process-language` | checklist selector, polish scan |
| `reflection-record` | `workbook-record`, `unit-folio` | Next-step record / practice log | no image | `diagnostic-form-drift`, `floating-blank-line` | record prompt blank rules |

Full v2 writing-output coverage requires `writing-planner`, `correction-rewrite`, and `final-check`. In long books, `writing-planner` and `final-check` must carry semantic variants such as monthly route map, daily schedule, answer sheet, visual planner, speaking cue card, listening replay, and reading evidence close; do not rely on one generic form surface under different page titles.

## Back Matter

| Template | Required Components | Visual Role | Asset Rule | Failure Labels | QA Checks |
| --- | --- | --- | --- | --- | --- |
| `handbook` | `handbook-page`, `handbook-table` | Pale lookup/reference rhythm with topic-specific mini rules and transfer examples | no image | `weak-backmatter`, `backmatter-index-weak`, `topic-template-drift` | component coverage, table overflow, lookup density |
| `grammar-lookup-index` | `handbook-page`, `mechanics-table` | Grammar lookup rows and quick examples | no image | `backmatter-index-weak`, `rendered-text-glitch` | lookup density, text extraction |
| `connector-index` | `practice-word-box`, `handbook-page` | Connector bank index with enough lookup rows to read as reference back matter | no image | `orphan-slot-line`, `backmatter-index-weak`, `validation-gallery-sparsity` | compact no-wrap blanks |
| `vocab-bank` | `words-to-know`, `handbook-page` | Vocabulary bank with compact topic-specific rows, examples, and action lookup density | no image | `backmatter-index-weak`, `validation-gallery-sparsity`, `exercise-taxonomy-flat`, `topic-template-drift` | component coverage, topic-specific word/example review |
| `answer-key` | `answer-key-page` | Compact grouped answer lookup for back matter | no image | `answer-leakage`, `weak-backmatter` | profile separation, leak scan |
| `teacher-answer-key` | `answer-key-page` | Teacher-only grouped key / notes profile | no image | `answer-leakage`, `student-process-language`, `weak-backmatter` | teacher/student output separation |
| `teacher-guide-page` | `teacher-guide-page`, `answer-key-page` | Teacher edition guide with timing, page notes, answer focus, and board notes | no image | `teacher-book-appendix-only-drift`, `weak-backmatter` | integrated teacher notes plus guide-page presence |
| `lesson-a4-adapter` | profile-level output, not a page template | A4 classroom version preserving book language and adding real learner action when the taller page would otherwise feel airy | follows source pages | `raster-book-drift`, `starter-residue`, `a4-reading-airiness` | lesson-a4 build, explicit `$eric-pdf` QA when requested for the Typst adapter, A4 contact-sheet review |

Full v2 back-matter coverage requires `handbook`, `vocab-bank`, and one answer-family page: `answer-key` for an intentional student-with-answer-key/public-notes edition, `teacher-answer-key` for a compact teacher-only key, or `teacher-guide-page` for a true teacher edition with integrated teaching notes and answer focus.

## Source Mapping

| Source material | Preferred v2 route |
| --- | --- |
| Level 1 reference form | abstract article-opener, evidence page, skill/method, practice, review, and back-matter rhythm only |
| 高二升高三暑假语法课 | contents-route, diagnostic-entry, skill-method, sentence-map, activity, exam-mini-set, handbook |
| 高二升高三 / 中高考 20+ lesson full course | module openers, contents-route, skill-method, sentence-map, article/evidence, exam-mini-set chunks, writing-planner/correction pages, teacher-answer-key chunks, handbook |
| 示例学生从句衔接课 | skill-method, model-annotation, sentence-transformation, correction-rewrite, final-check, lesson-a4 |
| Sample Learner IELTS regression | cover/title lockup, workbook-record, writing-planner, paragraph-practice, handbook, rendered text checks |

## Optional Structure Library

The system may not use every structure in every book, but it must have them available. When a long book repeats one template family, choose the structure from the lesson role instead of recycling the same shell with new text.

Declare the choice in page frontmatter as `variant:`. The renderer should expose it as `data-variant` and a `variant-*` class so CSS, QA, and visual review can see the structure decision. For repeated workbook/student-book roles, the rendered HTML must also expose a real surface marker such as `data-surface-family="task2-writing"` and `data-surface="task2-agree-disagree-answer-ladder"` on the main surface. Metadata-only variants do not count when the visual surface stays the same.

| Template family | Available structure variants |
| --- | --- |
| `unit-opener` | `bottom-band`, `side-panel`, `split-band`, `quiet-field-opener`, `photo-led-objectives`, `text-led-proof-opener` |
| `skill-method` | `rule-table-method`, `worked-example-method`, `guided-discovery-method`, `contrast-cue-method`, `micro-handbook-method`, `error-pattern-method` |
| `activity` | `word-box-controlled-practice`, `evidence-choice-practice`, `sentence-repair-practice`, `timed-transfer-practice`, `classification-practice`, `short-output-practice` |
| `categorizing-chart` | `error-bank-chart`, `logic-map-chart`, `evidence-sort-chart`, `verb-pattern-chart`, `paraphrase-pair-chart` |
| `exam-mini-set` | `mcq-evidence-set`, `cloze-repair-set`, `rewrite-transfer-set`, `listening-trap-set`, `reading-proof-set` |
| `writing-planner` | `book-roadmap-planner`, `daily-practice-schedule`, `task2-agree-disagree-answer-ladder`, `task2-discussion-two-view-bridge`, `task2-problem-solution-matrix`, `task2-advantage-balance-scale`, `task2-full-mock-answer-booklet`, `task1-visual-planner`, `speaking-cue-card`, `reading-evidence-record` |
| `final-check` | `weekend-mock-review`, `listening-part1-form-ledger`, `listening-part2-map-path-surface`, `listening-part3-speaker-opinion-matrix`, `listening-part4-lecture-note-columns`, `reading-line-evidence-close`, `reading-paraphrase-pair-close`, `reading-transfer-ticket-close`, `connector-final-check`, `exit-ticket-review`, `mistake-bank-close` |
| `sentence-map` | `clause-boundary-map`, `connector-logic-map`, `sentence-skeleton-map`, `modifier-attachment-map`, `parallel-structure-map` |
| `article-opener` / `article-evidence` | `concept-story-opener`, `source-evidence-page`, `model-paragraph-annotation`, `problem-solution-reading`, `long-sentence-transfer` |
| `handbook` / `vocab-bank` | `lookup-index`, `mini-rule-bank`, `contrast-table`, `example-ladder`, `error-to-fix-reference`, `topic-word-bank` |

Minimum rule for 50+ page `v2-full` books: if a repeated template family appears four or more times in final-assets mode, it should declare semantic variants and normally show at least two rendered surface variants. If it appears eight or more times, three rendered surface variants are expected unless the human review explicitly accepts the repetition as an exam answer-booklet convention. For `writing-planner` and `final-check`, QA reads the rendered `data-surface`; a page with only a new `variant:` name is `metadata-only-variant`.

Failure label: `page-structure-variant-library-weak`. Machine QA reports `PAGE_STRUCTURE_VARIANT_LIBRARY_WEAK`.

## Release Notes

- A v2 project can use selected templates without setting `page_family_mode: v2-full`.
- A project that claims full matrix coverage must pass `V2_PAGE_FAMILY_COVERAGE_MISSING` with all seven families complete.
- `qa.asset_mode: final-assets` remains separate from family coverage: a proof can pass v2 family coverage but still be labeled a layout proof until final ImageGen/licensed visual assets are registered and validated.
