# QA Gates

Use this reference before claiming any Eric-designed PDF is ready.

## Gate Matrix

| Gate | Machine evidence | Human evidence |
| --- | --- | --- |
| Scope lock | named profile, paths, source list | user intent matched |
| Legal/design boundary | no reference assets in project, no forbidden visible terms | design language is original |
| Fresh build | source-to-output freshness, rendered-page/contact-sheet freshness, current reports, plus starter-residue scan | no stale artifact or starter identity used |
| PDF structure | page count, trim size, text extraction, blank-page scan | page order makes sense |
| Component coverage | template/component counters plus planner/final-check variant and opener-variation gates | page rhythm feels complete |
| Student-book form coverage | required student-book roles/components when enabled | contact sheet shows article/opener, skill/method, practice, diagram/review, and handbook contrast |
| Asset policy | manifest paths, dimensions, `asset_mode`, final source kind/status/prompt/text policy, source-note/status license consistency, real-world scene anchors, `allowed_templates`, one-image-one-use checks, cover `content_brief` / `visual_direction` / `uniqueness_note`, second-family `family_rationale` / `nature_first_rationale`, cover-brand contrast CSS | images are clear, appropriate, immediately understandable real-world scenes, prefer nature/landscape/wildlife/animal directions when suitable, not proof placeholders, not abstract-symbolic contraptions, content-specific, not reused across page roles, and the Studio mark remains readable over the photo |
| Leak safety | visible text scan + extracted PDF text scan | student/teacher separation and natural teaching language reviewed |
| Visual QA | rendered pages, contact sheet, and review-file freshness | 9.5/10 target, P0/P1 = 0 |
| Evidence report | JSON/Markdown report | final response names remaining risk |

## Commands

Project profile:

```bash
python3 tools/build.py --profile book-trim
python3 tools/render_pdf.py --profile book-trim
python3 tools/validate.py --profile book-trim
pdftotext outputs/<profile-output>.pdf _qa/extracted-book-trim.txt
python3 <eric-teaching-polish-dir>/scripts/validate_teaching_polish.py --strict _qa/extracted-book-trim.txt
python3 ./scripts/qa_textbook_pdf.py --root . --profile book-trim --require-human-review
```

For final delivery, set `qa.asset_mode: final-assets` in `book.yaml` or pass:

```bash
python3 ./scripts/qa_textbook_pdf.py --root . --profile book-trim --asset-mode final-assets
```

Custom profile example:

```bash
python3 ./scripts/qa_textbook_pdf.py \
  --root . \
  --profile book-trim \
  --min-pages 14 \
  --max-pages 14 \
  --required-template cover \
  --required-template unit-opener \
  --required-component unit-opener \
  --require-human-review
```

Skill maintenance:

```bash
python3 <skill-creator-dir>/scripts/quick_validate.py .
python3 ./scripts/validate_skill_gates.py --json
```

## Severity Rules

- `P0`: trust-breaking issue, visible leak, missing required artifact, broken PDF, or copied protected source material.
- `P1`: likely user-visible defect, accidental cover/title wrapping, starter-sample residue in a custom project, missing required QA evidence, bad page size, answer leak risk, or failed build.
- `P2`: quality risk needing focused review, such as density imbalance or missing human visual sentinel when not required.
- `P3`: sampling radar only.

`PASS` means executable gates found no blocking issue. It does not mean visual excellence unless the visual review sentinel is present and parsed.
`FAIL` in a formal visual review is valid evidence of inspection, but it is not release evidence. Keep it in `_qa/visual-review-<profile>.md` and let `--require-human-review` fail until the proof is repaired and reviewed again.
Normal machine QA and formal release QA must remain separate files. The normal run writes `_qa/textbook-qa-<profile>.md/json`; `--require-human-review` writes `_qa/textbook-qa-<profile>-release.md/json`. Do not overwrite the normal report with release-gate failure evidence.

## Negative Regression

Run these checks whenever the validator or visual review contract changes:

```bash
python3 ./scripts/qa_textbook_pdf.py --self-test --json
python3 ./scripts/test_qa_textbook_pdf.py
```

Required behavior:

- A self-signed `FINAL_VISUAL_REVIEW: PASS` fails.
- A `.question-lines li` item containing both `.blank` and `.write-line` fails as `QUESTION_INLINE_BLANK_WITH_WRITE_LINE`; question prompts with dedicated answer lines must use `prompt_text_before_write_lines()` to strip author placeholders.
- A `.guided-mcq-set p` / `exam-mini-set` question stem containing generic `.blank` or literal `____` fails as `EXAM_STEM_SLOT_DRIFT`; MCQ/cloze stems must render through `.exam-stem-slot`, and slot punctuation must be wrapped with `.exam-stem-keep`.
- An A4 `sentence-map` page using `.textbook-table` / wide three-column long-text layout fails as `A4_SENTENCE_MAP_TABLE_CRAMP`; A4 lesson packs must use `.sentence-map-card-stack` with `data-surface-family="sentence-map"` and a real `data-surface`.
- A project with `qa.output_mode: a4-only` that still declares book-trim profiles/output filenames or visible labels such as `Student workbook and A4 lesson pack`, `22讲`, `天津高考英语一轮复习`, `book-trim`, source-lesson prefixes such as `第N讲`, or broken sanitizer output such as `第本课程` fails as `A4_ONLY_PROFILE_RESIDUE`.
- A clean `student-*` profile without explicit `answer_visibility` still runs student leak gates by profile-name inference; if teacher-answer-key pages or `data-teacher-only="true"` appear, it fails as `STUDENT_ANSWER_VISIBILITY_LEAK` instead of falling back to off.
- A `teacher-*` profile that contains many student-equivalent pages and only appends `teacher-answer-key` pages at the end fails as `TEACHER_BOOK_APPENDIX_ONLY_DRIFT` unless the project is explicitly named appendix-only. True teacher editions must include `teacher-page-note` and `teacher-answer-strip` components on relevant student-equivalent pages and at least one real `teacher-guide-page` for lesson flow and page-by-page teacher use. A `Teacher Guide` page rendered with `teacher-answer-key` is a failure, not a visual variation.
- A final visual asset set using procedural/proof/placeholder/starter/sample images fails.
- A final ImageGen asset without `prompt` / `generation_prompt`, approved final status, focus, source note, and no-text policy fails.
- A final visual asset that lacks real-world scene anchors, uses unnegated abstract/symbolic/paper-token drift terms, or turns the preferred animal/nature direction into cartoon mascot, sticker, chibi, anime, toy-like, or childish character art fails as `FINAL_ASSET_UNINTERPRETABLE_SCENE`.
- A final visual asset that uses campus/classroom/library/study or modern-life imagery without explaining why nature/landscape/wildlife/animal imagery was not the better fit reports P2 `FINAL_ASSET_NATURE_FIRST_RATIONALE_MISSING`.
- A manifest asset whose `source_note` says Public domain while `status` says CC BY, or whose `source_note` says CC BY/CC BY-SA while `status` says Public domain or omits the CC family, fails as `ASSET_LICENSE_STATUS_SOURCE_MISMATCH`.
- A final cover/hero asset without `content_brief`, `visual_direction`, and `uniqueness_note` fails as `COVER_CONTENT_CONCEPT_MISSING` / `COVER_UNIQUENESS_NOTE_MISSING`.
- Reusing the same asset id across pages fails as `ASSET_REUSED_ACROSS_PAGES`.
- Two asset ids pointing to the same image file fails as `ASSET_PATH_REUSED_IN_MANIFEST`.
- A cover/hero asset used on a unit opener, photo passage, or inner content page fails as `COVER_ASSET_REUSED_INSIDE_BOOK`.
- A page that uses an asset outside its `allowed_templates` fails as `ASSET_ALLOWED_TEMPLATE_MISMATCH`.
- A clean student profile with `answer_visibility: student` fails as `STUDENT_ANSWER_VISIBILITY_LEAK` if `answer-key`, `teacher-answer-key`, `answer-key-page`, or `data-teacher-only="true"` content appears. `student-with-answer-key` allows a normal student answer-key page but still blocks teacher-only pages.
- The starter v2 HTML builder must filter profile-specific pages before rendering. Teacher-only pages should declare `audience: teacher`; use `include_profiles` / `exclude_profiles` for named editions. Leak QA is the backstop, not the first place where student/teacher separation happens.
- Premium 中高考 workbook outputs must scan generated `pages/*.md` for student-visible headings. `article-opener` pages that are reading passages and reading `exam-mini-set` headings must not contain CJK; page-role headings such as map/writing-move/paragraph diagnosis/homework/checkpoint should pass through a generator-level visible-title map before render. English-but-AI or tool-surface headings such as `Lesson Route`, `Lesson Rhythm`, `Practice Rhythm`, `Micro Skills`, `Practice Log`, `Start Record`, `Personal Check`, `Self Check`, `score moves`, `scorecard`, and `self-check card` must be rejected in favor of printed workbook language such as `In This Lesson`, `Before You Begin`, `Evidence Check`, `Method Focus`, `Practice Set`, `Writing Moves`, `Opening Notes`, `Evidence Notes`, and `Before You Leave`.
- Premium 中高考 workbook outputs must scan student-visible prompt bodies, not only headings. Question lines, record prompts, planner prompts, checkpoint/review labels, and workbook record surfaces must not expose Chinese production-shell language such as `接下来我们`, `本页回收`, `复盘记录`, `微技能训练`, `作业说明`, `今日记录`, or `完成前检查`; failures report `STUDENT_PROMPT_LANGUAGE_DRIFT`.
- Article opener bodies must not preserve source-type prefixes such as `完形填空 Life is...`, `阅读理解...`, `阅读表达...`, or `任务型阅读...`, nor trailing copied source section markers such as `三、`; move source type into English title/notes and strip the prefix/marker before chunking passage text. This is checked as `STUDENT_PROMPT_LANGUAGE_DRIFT`.
- Cloze article bodies must not preserve OCR blank damage such as `17 _ side`, `whenI__18`, `my __19 onthe`, `He __ 24 _`, `30___ flights`, `a_31__`, split words like `ev- ery`, fused article phrases like `to bea leader`, hyphen-number damage like `Covid-____ related`, broken dash phrases like `person— something`, or punctuation spacing like `Situation ,is`; normalize these to clean prose with deterministic inline `.blank` spans before rendering. Protect real hyphen-number terms such as `Covid-19 related` before converting cloze numbers, and keep letter-em-dash-letter phrases together with word joiners on both sides of the dash so they do not break across lines before or after the dash. This is checked as `STUDENT_PROMPT_LANGUAGE_DRIFT` and as a visual `rendered-text-glitch` when caught in screenshots.
- If a Chinese course identity is kept on the cover/title page, the renderer still needs an English `footer_title` for frontmatter folios. Repeated labels such as `Lesson Map • 天津高考英语一轮复习` are renderer UI drift, not acceptable workbook identity; failures report `RENDERER_UI_LABEL_LANGUAGE_DRIFT`.
- Premium 中高考 workbook outputs must reject Chinese cloze/choice stems in rendered student text, including `完形填空第N空`, `第N空`, `根据全文选择`, and `选择最符合`. These belong in the generator's visible-language map as English workbook prompts, not as post-render hand edits.
- Teacher-only answer keys may keep Chinese explanations, but cloze blank references should still use `Blank N` instead of `第N空` so all release PDFs share the same exam-label language.
- Shared renderer defaults for workbook prompts must be English-first and student-facing. Defaults such as `进入下一页前，先确认这一页能直接使用。` and `下次先改哪一类题？` fail `STUDENT_PROMPT_LANGUAGE_DRIFT`; English defaults such as `Which question type should I repair next?` also fail if they use backstage terms. Fix the renderer default, not one generated page.
- Premium 中高考 workbook inner page headings must be English-first. Cover/course identity may keep necessary Chinese, but inner workbook surfaces such as activity, paragraph practice, reading, writing, final-check, handbook, and vocab-bank pages must not expose Chinese production-style headings; failures report `WORKBOOK_TITLE_LANGUAGE_DRIFT`.
- English-first is not enough if the title still sounds like a generator/workflow label. Student workbook headings such as `Today On The Page`, `Evidence Pause`, `Practice Review`, `Method Model`, `Demo Practice`, `Tool Practice`, `Lesson Route`, `Lesson Rhythm`, `Practice Rhythm`, and `Micro Skills` must be rewritten into printable workbook language such as `Practice Plan`, `Evidence Check`, `Review Check`, `Method Focus`, `Model Practice`, or `Strategy Practice`; failures report `WORKBOOK_TITLE_LANGUAGE_DRIFT`.
- Premium 中高考 workbook outputs must also scan rendered HTML/PDF UI furniture. A renderer that injects `本讲路线`, `课前记录`, `第10讲`, or timing-strip `时间` into folios, badges, ribbons, or timing strips fails `RENDERER_UI_LABEL_LANGUAGE_DRIFT`; the fix belongs in the shared renderer label map.
- Student-visible front matter must not expose production/design-system wording such as `surface family`, `page rhythm`, `design system`, `Lesson Route`, `Lesson Rhythm`, `Practice Rhythm`, or `Micro Skills`; failures are student-visible language leaks and belong in `STUDENT_FORBIDDEN_VISIBLE`.
- Lesson-pack final-assets validation must not depend on unused full-course manifest entries. A manifest path that does not exist is a failure; if the asset is unused by this lesson pack, remove it from that lesson's manifest instead of suppressing the validator.
- Categorizing charts need density-aware pagination. Add regression fixtures or representative lessons where rows above 125 visible characters split to four rows per book-trim page and rows above 155 split to three. The absence of `layout_overflows` across both book-trim and A4 is the proof.
- A cover without bottom-right `Eric Teaching Studio`, with a low-contrast Studio mark over the photo, or with level/stage metadata in the cover top-right, fails as `COVER_BRAND_MARK_MISSING` / `COVER_BRAND_CONTRAST_WEAK` / `COVER_TOP_LEVEL_BADGE`.
- A 9.5+ review with no `Contact sheet:` and no 4+ `Key pages:` fails.
- Key-page evidence must accept large-book screenshot names such as `_qa/rendered-pages/teacher-book-trim-page-1000.png`; four-digit rendered pages are valid for 999+ page teacher books and should not be rejected as a profile mismatch.
- A 9.5+ review with no `Canon comparison:`, `Reject patterns checked:`, or `Font decision:` fails.
- A valid independent review with screenshot evidence, canon comparison, reject-pattern check, and font decision passes.
- A formal failed review with `FINAL_VISUAL_REVIEW: FAIL`, evidence fields, and named weak pages remains a validator failure when `--require-human-review` is used; do not silently downgrade it to pending or pass.

## Visual Review Contract

`_qa/visual-review-<profile>.md` must include:

```text
FINAL_VISUAL_REVIEW: PASS
Reviewer: user-confirmed or independent-review
Score: 9.5/10
P0: 0
P1: 0
Checked: cover, unit opener, dense method/practice, workbook page, handbook/checkpoint
Contact sheet: _qa/contact-sheet-<profile>.png
Key pages: _qa/rendered-pages/<profile>-page-001.png, _qa/rendered-pages/<profile>-page-002.png, _qa/rendered-pages/<profile>-page-006.png, _qa/rendered-pages/<profile>-page-010.png
Canon comparison: compared against golden p1 cover, p3 opener, p4 elements, p6 paragraph practice, p9 handbook.
Reject patterns checked: thin-cover-type, title-wrap-break, cover-brand-missing, cover-brand-low-contrast, cover-stage-badge, generic-cover-art, abstract-asset-drift, nature-first-rationale-missing, mixed-title-scale-drift, dashboard-panel, ui-number-block, control-selector-leak, component-collage, diagnostic-form-drift, patch-drift, form-repeat, page-role-variant-rhythm-weak, unit-opener-variation-weak, loose-workbook-tail, plain-planner-table, plain-final-check, weak-backmatter, floating-blank-line, orphan-slot-line, question-line-double-blank, planner-label-blank-weak, rendered-text-glitch, student-process-language, visible-title-ai-language, workbook-title-language-drift, reading-title-language-drift, renderer-ui-label-language-drift, student-prompt-language-drift, raster-book-drift, article-form-missing, skill-ribbon-missing, exercise-taxonomy-flat, backmatter-index-weak.
Font decision: B modern sans primary; C system clean fallback; A rejected if title appears thin.
Visual diagnosis: ...
Weak pages: ...
Remaining risk: ...
```

Rules:

- Same-agent or self-signed review is not formal evidence.
- Formal delivery requires `qa.asset_mode: final-assets`; `proof-placeholder` means the output is only a layout/design-transfer proof.
- Cover/opener/photo/context assets cannot be procedural rasters, starter/sample/proof images, drafts, placeholders, or temporary mocks in final delivery. ImageGen assets need prompt/source/focus/no-text manifest evidence and must not contain fake text, watermarks, questions, answers, or teaching body.
- One image may be used once only. Cover/hero assets are cover-only; unit opener, photo passage, and inner context visuals require separate asset ids, separate image paths, and matching `allowed_templates`.
- In `final-assets` mode, cover/hero assets must be content-aware. The manifest must record `content_brief`, `visual_direction`, and `uniqueness_note`; a generic study desk, abstract gradient, or reused template image cannot receive 9.5 just because it is visually clean.
- In `final-assets` mode, all generated cover/opener/photo/context visuals must be immediately understandable real-world imagery. Prefer nature, landscape, wildlife, or realistic animal scenes when suitable; use campus/classroom/library/study or modern human learning/life scenes as the second family. If the second family is chosen, the manifest should record `family_rationale` or `nature_first_rationale`; otherwise QA reports P2 `FINAL_ASSET_NATURE_FIRST_RATIONALE_MISSING`. Abstract paper sculptures, symbolic decision maps, token boards, floating strips, concept-art contraptions, cartoon mascots, sticker animals, chibi/anime animals, toy-like animals, or childish character art are `abstract-asset-drift` / style drift and cannot receive 9.5 unless Eric explicitly asked for that exception.
- The cover must include `Eric Teaching Studio` as a bottom-right brand mark with enough contrast to read over the selected photo. Course stage/level metadata such as `高二升高三` must not appear as a top-right cover badge.
- A formal review below 9.5 must use `FINAL_VISUAL_REVIEW: FAIL`; `PENDING` is only for evidence not yet reviewed or user/independent confirmation not yet obtained.
- Missing contact sheet or fewer than four key page references means the visual review is pending, even if the score says 9.5+.
- Missing `Canon comparison:`, `Reject patterns checked:`, or `Font decision:` means the visual review is pending.
- A contact sheet with repeated sparse form pages cannot receive 9.5.
- A long book where planner/final-check pages omit semantic variants or reuse the same template+variant densely cannot receive 9.5; label it `page-role-variant-rhythm-weak`.
- A long book where repeated activity, skill-method, categorizing-chart, exam-mini-set, handbook, vocab-bank, article/evidence, or sentence-map pages have no declared structure variants cannot receive 9.5 as a reusable system; label it `page-structure-variant-library-weak`.
- Numbered variants such as `practice-1/2/3` count as one structure unless the rendered surface changes; metadata-only numbering cannot clear `page-structure-variant-library-weak`.
- For repeated `writing-planner` and `final-check` pages, rendered HTML needs both `data-surface-family` and `data-surface` on the actual paper/workbook surface. If the source declares different variants but the renderer emits the same surface, no surface marker, or a surface marker without a family marker, label it `metadata-only-variant`; machine QA keeps `PAGE_STRUCTURE_VARIANT_LIBRARY_WEAK`.
- A multi-unit book whose openers reuse one accent and one layout cannot receive 9.5; label it `unit-opener-variation-weak`.
- A student-book conversion cannot receive 9.5 if it is only a numbered exercise packet. It must show article/opener, skill/method, practice, diagram/review, and handbook/back-matter rhythms, or the review must name `exercise-taxonomy-flat`, `article-form-missing`, or `backmatter-index-weak`.
- A teacher book cannot receive 9.5 if pages 1-N are just the student book and all teacher material appears only as sparse backmatter tables. It must be runnable during class: teacher notes and answer references need to be close to the matching student page, while backmatter should function as compact lookup.
- A reference PDF being image-only is not permission to rasterize. If text-heavy pages are full-page images or body text is hidden inside visual assets, apply `raster-book-drift` and fail the gate until deterministic text is restored.
- Skill/practice pages that should inherit professional student-book form but lack section ribbons or cognitive side labels should be labeled `skill-ribbon-missing` before visual scoring.
- A contact sheet where activity, planner, or record pages use the right components but still read as diagnostic forms or workflow tools cannot receive 9.5; label this `diagnostic-form-drift`.
- A cover/title page with accidental Chinese/name/title wrapping cannot receive 9.5.
- A cover/title page where one phrase of the same H1 title is secretly demoted in size or weight, such as a smaller `for Sample Learner`, cannot receive 9.5; label this `mixed-title-scale-drift`.
- A checklist/table/sidebar component whose generic selectors style all descendant spans and turn blanks or text fragments into UI controls cannot receive 9.5; label this `control-selector-leak`.
- An activity/workbook page that ends as scattered questions or loose writing lines cannot receive 9.5; it needs a cohesive `workbook-record` / `workbook-practice` surface with header, numbered rows, and stable writing lines. Machine QA should report `WORKBOOK_RECORD_SURFACE_MISSING` when that structure is absent.
- A planner/review page that still reads as a spreadsheet cannot receive 9.5.
- A handbook/reference page without lookup density cannot receive 9.5.
- Fill-in-the-blank underlines floating near the middle of any visible exercise text, model-note cloze blanks dangling below the paragraph line, record-prompt blanks dropping like answer lines, word-box / mini-rule / caption / sidebar blanks becoming lonely horizontal rules, or literal underscore glyphs used as blanks, cannot receive 9.5; starter blanks must use a zero-height bottom-rule model with `.blank { vertical-align: -0.82em; }`, `.question-lines .blank { vertical-align: -0.88em; }`, `.paragraph-practice p .blank { vertical-align: -0.22em; }`, `.record-prompt .blank { vertical-align: -0.32em; }`, `.word-box .blank { vertical-align: -0.26em; }`, `.handbook-rules .blank { vertical-align: -0.24em; }`, `.word-box-item { white-space: nowrap; }`, and `.cloze-keep { white-space: nowrap; }`. Machine QA should report `LITERAL_UNDERSCORE_BLANKS` when generated HTML/PDF text still contains 3+ underscore runs and `BLANK_BASELINE_CSS_WEAK` when generated CSS keeps the older centered alignment or omits the paragraph / record-prompt / compact phrase cloze override.
- MCQ/cloze stem underlines are a separate system from `.blank`; `.guided-mcq-set p .blank`, detached punctuation after an exam stem slot, or literal underscores in exam stems cannot receive 9.5 and should fail `EXAM_STEM_SLOT_DRIFT`.
- A4 long sentence analysis squeezed into a wide table cannot receive 9.5; use a stacked sentence-map card surface and fail `A4_SENTENCE_MAP_TABLE_CRAMP` when A4 keeps the cramped table.
- An A4-only independent lesson pack with book-trim residue, full-course `22讲` labels, or visible `天津高考英语一轮复习` cannot receive 9.5; fail `A4_ONLY_PROFILE_RESIDUE` and regenerate from A4-only profiles.
- A period, comma, colon, semicolon, question mark, or exclamation mark after a blank cannot orphan onto its own line. Render `____.` and similar author text as a nonbreaking blank-plus-punctuation unit.
- Rendered PNG text with ambiguous digits, broken apostrophes, or mixed-script glyph glitches cannot receive 9.5 even when `pdftotext` is correct.
- Student-visible text with backstage terms such as `Route`, `主动作`, `Repair`, `维修`, `路由`, `后台`, or `闭环` cannot receive 9.5.
- Student-visible reading articles or reading question sets with Chinese headings cannot receive 9.5 in English workbook mode. Use neutral English article titles and English set prefixes; keep Chinese only where it is actual explanatory/exam content.
- Student-visible page-role headings that read like generated Chinese workflow labels, even if not forbidden by the strict scanner, should be labeled `visible-title-ai-language` and repaired before scoring.
- Student-visible renderer UI labels that are Chinese only because the template layer translated them back, such as `本讲路线`, `课前记录`, `第10讲`, `时间`, or a repeated frontmatter footer like `Lesson Map • 天津高考英语一轮复习`, should be labeled `renderer-ui-label-language-drift` and repaired in the renderer before scoring.
- Student-visible workbook prompt bodies that still use Chinese workflow shells such as `接下来我们`, `本页回收`, `复盘记录`, `微技能训练`, `作业说明`, `今日记录`, or `完成前检查` should be labeled `student-prompt-language-drift` and repaired in the generator before scoring.
- Fresh evidence is chronological: source inputs must be older than HTML/PDF, rendered pages/contact sheets must be newer than HTML/PDF, and the visual-review file must be newer than the screenshots it cites.
- Generated `pages/` folders must not contain stale duplicate files such as `pages/0002-title 2.md`; even when `book.yaml` does not reference them, they pollute source scans and future reviews. Machine QA reports `STALE_DUPLICATE_PAGE_FILES`.
- Every generated `pages/*.md` file must be referenced by `book.yaml`. Unreferenced active-looking pages, old lesson variants, or Finder/iCloud copies preserve rejected language and can mislead review even when the current PDF is clean. Machine QA reports `INACTIVE_PAGE_SOURCE_FILES`.
- Generated `_qa/rendered-pages/` folders must not contain Finder/iCloud-style conflict screenshots such as `<profile>-page-252 2.png` or `<profile>-page-1074 3.png`. The validator must check the canonical rendered-page sequence and report `RENDERED_PAGE_CONFLICT_FILES`, `RENDERED_PAGE_SEQUENCE_MISSING`, or `RENDERED_PAGE_FILENAME_DRIFT` before accepting contact sheets or release reviews.
- Generated `_qa/` evidence files must not contain Finder/iCloud-style duplicate contact sheets, review sheets, visual reviews, or QA reports such as `contact-sheet-student-book-trim 2.png` or `review-sheet-book-trim-key-pages 3.png`. These can mislead human review even when the PDF is clean; machine QA reports `QA_EVIDENCE_CONFLICT_FILES`.
- Independent lesson-pack delivery roots must also run a final whole-folder conflict scan after the last lesson builds. Files such as `book 2.yaml` or `LESSON_ADAPTATION_REVIEW 2.md` can appear after per-lesson checks and must be deleted before evidence is accepted. A complete 22-lesson delivery must also have no stale `lesson-*` directory outside the manifest; a manifest with 22 lessons beside 39 lesson folders is not a clean handoff.
- For 500+ page / four-profile projects in iCloud-backed or synced folders, do not run all long `render_pdf.py` jobs in parallel. Render profiles sequentially, then wait for the filesystem to settle and run a conflict scan before `qa_textbook_pdf.py --require-human-review`; otherwise stale `... 2.png` screenshots and `... 3.md` page copies can appear after a clean render and correctly fail release gates.
- A custom project with `STARTER_RESIDUE_FOUND` cannot receive 9.5, even if the residue is hidden in source files rather than visible on the rendered page.
- If the user flags a visual issue after PASS, revoke the sentinel, repair the issue, regenerate screenshots, and rerun the gate.
- If the user asks to search review or fix all issues, named P2/Weak pages are a repair list. They may remain only when the final response explicitly says Eric accepted that risk after seeing updated screenshots.
- If a project uses custom validators, they must preserve this visual review contract.

## Evidence Template

```text
PDF: /absolute/path/to/output.pdf
Source: /absolute/path/to/project
Build: build.py + render_pdf.py succeeded for <profile>
Validator: pass, machine report at _qa/textbook-qa-<profile>.md; release report at _qa/textbook-qa-<profile>-release.md when `--require-human-review` is used
Assets: asset_mode final-assets; cover/opener/context visuals are ImageGen or licensed originals with manifest prompt/source/focus/no-text policy and real-world scene anchors, preferring nature/landscape/wildlife/animal directions when suitable; second-family school/study/modern-life visuals include family_rationale / nature_first_rationale; cover/hero assets include content_brief, visual_direction, and uniqueness_note; every visual has a unique asset id/path and matching allowed_templates; cover brand contrast passed
Visible text: answer_visibility is correct for the profile; extracted PDF text passed teaching-polish strict scan / not applicable
Visual QA: contact sheet and key pages checked; FINAL_VISUAL_REVIEW PASS at _qa/visual-review-<profile>.md
Fixes made: none / named fixes
Remaining risk: none / exact page or component
```
