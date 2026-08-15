# Review Rubric

Use this rubric for human, independent, or user-confirmed visual review.

## Release Threshold

- `9.5/10` or higher: releasable only with P0 = 0 and P1 = 0.
- `9.0-9.4`: promising proof, not final.
- `<9.0`: redesign, not polish.

Do not average away a P1. One bad cover or one dashboard-looking core page can block release.
If a formal visual review was performed and the score is below 9.5, write `FINAL_VISUAL_REVIEW: FAIL`, not a vague pass-like note. Keep the same evidence fields so the failure is auditable.

## Score Axes

| Axis | What 9.5 Looks Like |
| --- | --- |
| Book identity | Cover and title pages feel like a real textbook, not a web hero or worksheet pack. |
| Cover brand | `Eric Teaching Studio` appears as a restrained, readable bottom-right mark with photo contrast protection; course stage/level metadata is not used as a top-right cover badge. |
| Cover concept | Cover/hero image is generated or selected from the actual book/lesson content, with a distinct visual idea rather than a generic reusable study image. |
| Asset interpretability | Final cover/opener/photo/context visuals are immediately understandable real-world imagery. Prefer nature, landscape, wildlife, and realistic animal photographs when suitable; campus/classroom/library/study scenes and modern human learning/life scenes are the second family and need a manifest rationale when chosen. They do not drift into abstract paper sculptures, symbolic boards, token maps, floating strips, or concept-art contraptions. |
| Asset uniqueness | Cover, unit opener, photo passage, and context visuals are distinct one-use assets; the cover image never reappears inside the book. |
| Canon match | Page roles visibly inherit the golden sample rhythm without copying assets/text. |
| Page-role contrast | Contact sheet shows cover, navigation, opener, method, workbook, review, and back matter as distinct roles. |
| Student-book form | When the task absorbs student-book form, the proof shows article/concept opener, comprehension/check, skill/method, grammar/vocabulary practice, diagram/review, and back-matter lookup rhythms rather than a flat exercise packet. |
| Topic/template fidelity | Reused page templates carry the current unit's real teaching semantics. Listening, reading, vocab, handbook, and transfer pages must not retain generic starter rows or row language from another skill/topic. |
| Typography | Chinese and English fonts have stable weight, hierarchy, and professional texture. |
| Title lockup | Cover/title text keeps Chinese words, student names, and mixed-language phrases intact; any line break is deliberate; suffix/name text inside the same H1 is not demoted to a smaller scale. Chinese single-lesson covers use a modern heavy sans lockup with enough optical weight to read as a book cover at contact-sheet size. Long Chinese lesson concepts with colon/list/underscore structure share explicit editorial title lines between cover and title page, and use a long-title optical scale that avoids overflow or squeezed H1 drift. |
| Component restraint | Tables, labels, bands, and boxes behave like textbook components, not app widgets; UI control styling is isolated to explicit marker classes and never leaks onto content spans/blanks. |
| Editorial page feel | Activity, planner, and record pages feel like printed workbook pages, not diagnostic forms, progress dashboards, or tool screens. |
| Writing affordance | Activity/workbook pages use cohesive record surfaces, not loose Q&A tails; fill-in blanks and writing lines sit where a student would naturally write, near the lower writing baseline/lower line-box edge, with no floating/centered underlines and no literal underscore glyphs in any visible exercise text. Model-note cloze blanks sit optically with the paragraph text instead of dangling into the line gap; workbook-record prompt blanks sit with prompt text instead of dropping like answer lines; activity instructions/items, table cells, planner prompts, checklist labels, handbook rows, and answer tables use inline cloze alignment rather than answer-line alignment. Word-box choices, mini-rule cards, captions, sidebars, and narrow lookup cells use compact no-wrap phrase blanks so the underline never becomes a lonely line. ASCII and Chinese punctuation after blanks must stay attached. The older global `-0.64em/-0.68em` blank CSS is not acceptable for release. |
| Density | Pages feel used and useful without becoming cramped or sparse. |
| A4 adaptation density | `lesson-a4` pages use the taller sheet for real learner action. Reading/article pages should add compact evidence/check/record surfaces when the book-trim layout leaves excessive bottom air. |
| Planner/back matter | Planner and final-check pages feel like workbook writing surfaces; handbook and answer-key pages have compact lookup rhythm, not sparse worksheet/table drift. |
| Teacher-book operability | A teacher edition is runnable during class: relevant student-equivalent pages carry teacher notes and answer references, while backmatter guide/key pages are compact lookup/reference surfaces. A student book with only appended teacher tables is not a Teacher's Book release. |
| Rendered surface variation | Repeated writing-planner/final-check pages show real surface variation at full-page and contact-sheet scale. The reviewer must reject metadata-only variants where page titles differ but the rendered surface remains the same. |
| Rendered text fidelity | Digits, punctuation, apostrophes, and mixed Chinese/English text look clean in rendered PNGs. |
| Instructional function | Every component helps teaching, practice, review, or lookup. |
| Deterministic text | Exercises, answers, captions, and tables are selectable/searchable; text-heavy pages are not rasterized even when a reference PDF was image-only. |
| Leak safety | No local paths, internal labels, teacher-only tactics, or process wording. |
| Visible language | Student-facing copy sounds like a real teacher giving tasks, not an internal workflow or AI plan. Premium 中高考 workbook pages use English-first role headings, reading article titles, reading set titles, question prompts, and checkpoint labels unless Eric explicitly asks for Chinese workbook labels. Chinese remains only where it carries exam terminology, local explanation, or original source content. |
| Source hygiene | Custom projects contain only the requested book identity, not starter sample titles, renderer labels, or sample assets. |
| Print readiness | Lines, captions, footers, and tables survive PDF export cleanly. |

## Required Visual Review Fields

`_qa/visual-review-<profile>.md` must include:

```text
FINAL_VISUAL_REVIEW: PASS
Reviewer: user-confirmed or independent-review
Score: 9.5/10
P0: 0
P1: 0
Checked: cover, navigation, opener, dense method, workbook, handbook
Contact sheet: _qa/contact-sheet-<profile>.png
Key pages: _qa/rendered-pages/<profile>-page-001.png, _qa/rendered-pages/<profile>-page-002.png, _qa/rendered-pages/<profile>-page-004.png, _qa/rendered-pages/<profile>-page-006.png
Canon comparison: compared against golden p1 cover, p3 opener, p4 elements, p6 paragraph practice, p9 handbook.
Reject patterns checked: thin-cover-type, title-wrap-break, single-lesson-cover-title-flat, single-lesson-cover-title-weight-weak, single-lesson-long-title-overflow, single-lesson-title-page-wrap-drift, cover-brand-missing, cover-brand-low-contrast, cover-stage-badge, generic-cover-art, abstract-asset-drift, nature-first-rationale-missing, cover-image-reuse, mixed-title-scale-drift, dashboard-panel, ui-number-block, control-selector-leak, component-collage, validation-gallery-sparsity, patch-drift, form-repeat, loose-workbook-tail, plain-planner-table, plain-final-check, thin-lesson-close-surface, same-close-surface-repeat, writing-run-surface-repeat, weak-backmatter, teacher-book-appendix-only-drift, floating-blank-line, orphan-slot-line, question-line-double-blank, planner-label-blank-weak, rendered-text-glitch, student-process-language, visible-title-ai-language, reading-title-language-drift, renderer-ui-label-language-drift, student-prompt-language-drift, manifest-unused-asset-drift, long-chart-row-overflow, raster-book-drift, article-form-missing, skill-ribbon-missing, exercise-taxonomy-flat, backmatter-index-weak.
Font decision: B modern sans primary; C system clean fallback; A rejected if title appears thin.
Visual diagnosis: ...
Weak pages: ...
Remaining risk: ...
```

The validator treats missing canon comparison, reject-pattern check, or font decision as pending/failed human review when formal review is required.

For a formal failed review, use the same structure but replace the sentinel and score:

```text
FINAL_VISUAL_REVIEW: FAIL
Reviewer: formal-human-visual-review
Score: 9.1/10
P0: 0
P1: 1
P2: 2
Checked: cover, navigation, opener, dense method, workbook, planner, handbook
Contact sheet: _qa/contact-sheet-<profile>.png
Key pages: _qa/rendered-pages/<profile>-page-001.png, _qa/rendered-pages/<profile>-page-002.png, _qa/rendered-pages/<profile>-page-005.png, _qa/rendered-pages/<profile>-page-006.png
Canon comparison: compared against golden p1 cover, p3 opener, p5/p6 workbook pages, p8 planner, p9 handbook.
Reject patterns checked: thin-cover-type, title-wrap-break, single-lesson-cover-title-flat, single-lesson-cover-title-weight-weak, single-lesson-long-title-overflow, single-lesson-title-page-wrap-drift, cover-brand-missing, cover-brand-low-contrast, cover-stage-badge, generic-cover-art, abstract-asset-drift, nature-first-rationale-missing, cover-image-reuse, mixed-title-scale-drift, dashboard-panel, ui-number-block, control-selector-leak, component-collage, validation-gallery-sparsity, diagnostic-form-drift, patch-drift, form-repeat, loose-workbook-tail, plain-planner-table, plain-final-check, thin-lesson-close-surface, same-close-surface-repeat, writing-run-surface-repeat, weak-backmatter, teacher-book-appendix-only-drift, floating-blank-line, orphan-slot-line, question-line-double-blank, planner-label-blank-weak, rendered-text-glitch, student-process-language, visible-title-ai-language, reading-title-language-drift, renderer-ui-label-language-drift, student-prompt-language-drift, manifest-unused-asset-drift, long-chart-row-overflow, raster-book-drift, article-form-missing, skill-ribbon-missing, exercise-taxonomy-flat, backmatter-index-weak.
Font decision: ...
Visual diagnosis: ...
Weak pages: ...
Remaining risk: ...
```

Use `FINAL_VISUAL_REVIEW: PENDING` only when the review has not been performed or needs user/independent confirmation. Use `FAIL` when the reviewer has looked at the rendered evidence and found P1 issues or a score below release threshold.

## Reviewer Rules

- Same-agent review is not formal release evidence.
- A user rejection overrides any previous visual PASS.
- When Eric asks to "review", "搜一下 review", "把所有问题搞定", or "沉淀到 skill", named P2/Weak pages in existing review files are active work items. Do not leave them as "remaining risk" unless Eric explicitly accepts that risk after seeing the rendered evidence.
- A cover missing `Eric Teaching Studio`, showing a low-contrast Studio mark, showing a top-right stage/level badge, using generic cover art, drifting into abstract generated imagery, or reusing the cover image inside the book cannot receive a release PASS.
- If a page is repaired, regenerate all contact sheets and update the review.
- If Eric flags a title wrap or AI/backstage wording, treat the previous score as superseded even when machine QA passed.
- If Eric flags Chinese reading titles, AI-flavored headings, Chinese workflow prompt shells, renderer-injected Chinese UI furniture, or too little English in workbook pages, treat it as `visible-title-ai-language` / `reading-title-language-drift` / `student-prompt-language-drift` / `renderer-ui-label-language-drift` and repair the generator or renderer language layer before another visual score.
- If Eric rejects a Teacher's Book because it looks like "student book + appendix", treat it as `teacher-book-appendix-only-drift` and redesign the teacher profile contract. Do not claim it is fixed until rendered teacher pages show integrated notes/answer strips and real guide pages.
- If Eric says the proof "feels different" from the sample, check `diagnostic-form-drift` before doing small CSS fixes.
- If QA flags `STARTER_RESIDUE_FOUND`, treat the build as not release-ready even when the contact sheet looks acceptable.
- Keep weak pages named even when the score is high; "none" is allowed only after checking rendered pages.
