# Visual DNA

Use this reference when designing or repairing the visual language of an Eric-designed textbook PDF.

## Design Boundary

- Build an original system. Preserve only abstract page grammar: full-photo opener, quiet textbook grids, teal rules, magenta activity labels, writing lines, textured practice blocks, and back-matter pages.
- Never copy source-book logos, original passages, artwork, screenshots, page images, or brand names into student-visible output.
- Keep text deterministic. Photos and generated assets support context; they do not carry exercises, answers, long headings, or instructions.
- Some reference student books are distributed as whole-page images. Do not copy that production route. `raster-book-drift` is a reject pattern whenever selectable/searchable teaching text is replaced by page images.
- For layout proofs, `qa.asset_mode: proof-placeholder` may use stable temporary visuals so typography and page rhythm can be debugged. For final delivery, switch to `qa.asset_mode: final-assets`; cover/opener/context visuals must be ImageGen or licensed/owned originals registered with prompt/source/focus/no-text policy and real-world scene anchors. Default final visuals to immediately understandable real-world scenes, with Eric's preferred order: nature/landscape/wildlife/animal photographs first when suitable, then campus/classroom/library/study scenes or modern human learning/life scenes. If a final asset uses the second family, add `family_rationale` or `nature_first_rationale` to the manifest so QA can see why the content needed a study/life scene instead of nature/wildlife. Animal imagery should read as real nature/wildlife, not childish mascots. Abstract paper sculptures, symbolic boards, token maps, floating strips, and concept-art contraptions are `abstract-asset-drift` unless Eric explicitly asks for that direction. Final cover/hero visuals must also include `content_brief`, `visual_direction`, and `uniqueness_note` so the cover is designed from the actual material and does not become a reusable generic mood image. One image may be used once only: a cover visual cannot reappear as a unit opener or inner photo-passage visual.

## Page Rhythm

- **Cover:** full-bleed photographic signal, condensed title, restrained series metadata, no cards; `Eric Teaching Studio` sits as the bottom-right brand mark; stage/level metadata does not appear as a cover top-right badge.
- **Title page:** quiet editorial page, small mark, rule line, level/edition metadata, and restrained navigation rows when the page needs orientation.
- **Generic front matter:** no-student-name editions need a real book identity, not only a functional course label. p1-p3 should establish cover identity, editorial promise, audience/scope, and route; do not leave them as a stripped personalized cover plus usage notes.
- **Unit opener:** large photo, unit number/title lockup, bottom objectives band.
- **Elements page:** teal top rule, large heading, serif explanatory body, structured rule table.
- **Activity page:** magenta activity label, word box, and cohesive workbook record surface with numbered prompts and bounded writing lines.
- **Paragraph practice:** paper-textured model paragraph block with green label and stable blanks.
- **Photo passage:** photo/caption plus short answer lines; photo is context, not decoration.
- **Writing planner:** paper-surface planning block with generous lines, strong row labels, softened prompts, a small rule strip, and an editing checklist.
- **Handbook/back matter:** pale blue-gray field, denser lookup rhythm, mini rules, compact rows, quiet footers.
- **Answer key:** compact but clean tables; never included in student profile unless explicitly requested.

## Student Book Form Rhythm

When absorbing a Level 1/student-book form, add these page-role rhythms on top of the Eric-designed canon:

- **Article/concept opener:** anchored visual or evidence field, large editorial title, lettered paragraphs, inline keyword highlights, compact support notes.
- **Comprehension/check page:** warm section ribbon, A/B/C tasks, side cognitive labels, MCQ/short answer/chart mix.
- **Skill/method page:** concept box, model sentence or excerpt, guided questions, short transfer strip.
- **Vocabulary/grammar practice:** compact word box, completion/context/collocation or connector-choice sections, margin image/cutout only when useful.
- **Diagram/map page:** sentence tree, clause-boundary map, or logic grid as a thinking surface.
- **Review/task page:** timed check, short reflection, vocabulary/review checklist.
- **Back-matter lookup:** glossary/index rhythm, compact tables, mini rules.

For Chinese exam grammar, the textbook form should make the method visible through page roles: quick diagnostic -> check page, core model -> skill page, 三栏判断 -> diagram/chart, classified drill -> practice page, mixed drill -> review page, and rule summary -> handbook page.

## Tokens

Default starter tokens:

- Paper: `#ffffff`
- Ink: `#161616`
- Muted: `#585858`
- Teal: `#0f7890`
- Teal dark: `#096878`
- Teal light: `#c8e2e4`
- Activity magenta: `#9a3370`
- Green: `#43856f`
- Rust: `#b8642f`
- Back matter blue: `#dbe7ed`
- Table line: `#9fc3c6`
- Hairline: `#cbd5d6`
- Paper texture: `#f6f5f1`

Font stacks:

- Display: `Arial Narrow, Helvetica Neue Condensed, Impact, sans-serif`
- Serif body: `Georgia, Times New Roman, serif`
- Sans: `Arial, Helvetica, PingFang SC, Hiragino Sans GB, sans-serif`
- Chinese: `PingFang SC, Hiragino Sans GB, Arial, sans-serif`

For Chinese-heavy covers or headings, read `visual-canon.md` and prefer the B/C route: `Hiragino Sans GB` or `PingFang SC` with a firm semibold/bold cover lockup. Reject a proof when a missing Source Han/Noto font falls back into thin Songti/PingFang and weakens the cover.
For mixed Chinese/English titles or personalized names, lock the title deliberately. Reject accidental wrapping that splits Chinese words or leaves suffixes such as `for Sample Learner` orphaned.

## Visual QA Targets

- Density feels like a printed textbook page: used, not cramped.
- Repeated components align across pages; footer and rule systems do not jump.
- Writing lines stay stable and visible after PDF export.
- Inline fill-in blanks sit near the lower writing baseline/lower line-box edge, not floated upward toward the middle of the line; author-typed `___` / `______` runs in all visible exercise text, including word-box items, become zero-height bottom-rule blank elements, never visible underscore glyphs. Use the lower-edge alignment contract (`-0.82em`; question lists `-0.88em`) rather than the older `-0.64em/-0.68em` values. For model-note / paragraph-practice cloze blanks, use the separate paragraph-text optical adjustment (`.paragraph-practice p .blank { vertical-align: -0.22em; }`) so short blanks sit precisely with the serif paragraph line. For workbook-record prompt cloze blanks, use `.record-prompt .blank { vertical-align: -0.32em; }` so they remain attached to prompt text.
- Tables have enough row height and do not become spreadsheet dumps.
- Student-facing copy uses real teaching language, not internal workflow terms.
- Rendered text, punctuation, ranges, and mixed CJK/Latin strings read cleanly in PNG screenshots, not only in extracted PDF text.
- Photos are sharp enough for the trim size and do not show fake text or watermarks.
- Final assets do not look like placeholders, procedural test art, or starter/sample images; their manifest status is approved final.
- Final generated assets are easy to understand as real scenes: nature, landscape, wildlife/animal, school/campus/classroom/library/study, or modern human learning/life contexts. Prefer the nature/animal family when it can carry the mood; if choosing school/study/modern-life imagery instead, record the content reason in `family_rationale` or `nature_first_rationale`. Reject hard-to-explain abstract paper/symbol/token compositions.
- Cover art is content-aware: a grammar book, writing planner, reading unit, and vocabulary workbook should not all use the same generic desk/photo direction.
- Cover, unit-opener, photo-passage, and context visuals are distinct at contact-sheet scale. Reusing the same photograph/bitmap across page roles makes the book feel like a template proof, not a real publication.
- Contact sheet should reveal immediate page variety: cover, opener, rules, activity, passage, writing, handbook, answer key.

## Contact Sheet Rejection Rules

Reject the build before writing a visual PASS when the contact sheet shows any of these:

- More than one third of pages look like the same white form/table with only a different heading.
- A generic no-student-name edition has only a bare functional title such as `备考计划`, `学习计划`, `student workbook`, or `A4 lesson pack`, without a publishable `identity.cover_title` and editorial positioning.
- A long v2 book has long form-only runs where planner/final-check/exam/practice pages appear without editorial anchors such as opener, article/evidence, photo passage, handbook, or answer-key rhythm.
- Most pages have a large empty lower half without a deliberate writing-space purpose.
- Cover looks like a website hero or marketing card pasted over a photo instead of a book cover.
- Cover is missing `Eric Teaching Studio` in the bottom-right or shows `高二升高三` / `Level` as a top-right badge.
- Cover art feels generic, reused, or unrelated to the current book/lesson content.
- Final generated visuals look like abstract concept art, paper sculptures, symbolic boards, token maps, or floating strips rather than understandable real-world scenes.
- The same cover/opener/photo image appears on more than one page.
- Cover/title text breaks a Chinese word, student name, or mixed-language title phrase by accident.
- Unit opener is a stack of unrelated bands/cards instead of one controlled opener composition.
- Dense instructional pages do not contain real textbook texture: rule explanation, example, guided practice, margin note, checklist, or review action.
- Activity/workbook page ends as scattered questions or loose writing lines instead of a cohesive record surface.
- Writing planner is a plain spreadsheet-like table instead of a tactile writing surface.
- Fill-in-the-blank underlines float near the middle of visible exercise text, or literal underscore glyphs appear instead of lower-edge writing lines.
- Rendered text shows glyph ambiguity, broken apostrophe spacing, or range/digit shapes that make the page look unpolished.
- Student-facing pages contain backstage words such as `Route`, `主动作`, `Repair`, `维修`, `路由`, `后台`, or `闭环`.
- Handbook/back matter looks like another worksheet page instead of a denser reference surface.
- Student-book conversions remain a long numbered exercise packet without article/opener, skill/method, practice, diagram/review, and handbook contrast.
- Article/concept pages lack anchored visual/evidence fields and read as plain notes.
- Skill/practice pages lack section ribbons and cognitive side labels where needed.
- Text-heavy pages are rasterized or body text is hidden inside images.

If any rejection rule appears, mark the page set as `not ready`, redesign the weakest page roles, and regenerate screenshots before running formal QA.

## Visual Failure Taxonomy

Use these labels in `Visual diagnosis:` and `Weak pages:` so failures become repairable:

| Label | Symptom | Repair |
| --- | --- | --- |
| `landing-cover` | Cover reads like a website hero, with centered marketing copy or card-like title blocks. | Rebuild as a book cover: full-bleed image, editorial title lockup, restrained metadata, no UI cards. |
| `title-wrap-break` | Title breaks a Chinese word, student name, or mixed-language title phrase by accident. | Lock the phrase to one line or create an intentional editorial break; rerender the contact sheet. |
| `cover-brand-missing` | Cover lacks the bottom-right `Eric Teaching Studio` mark. | Add a restrained `.cover-brand` at the lower-right corner and rerender p1. |
| `cover-stage-badge` | Course stage/level appears as a top-right cover badge, making the cover feel like an internal packet. | Move stage/level metadata to title/navigation or subtitle/meta; keep the top cover as series identity only. |
| `generic-cover-art` | Cover image is pretty but not derived from the lesson/book content, or it reuses a template mood across projects. | Generate a content-specific cover concept and record `content_brief`, `visual_direction`, and `uniqueness_note` in the manifest. |
| `generic-book-identity-weak` | A no-student-name final book is only a de-personalized version of a test build, with a functional title such as `备考计划` or `workbook` but no real publication identity. | Create `identity.cover_title`, `identity.positioning`, `identity.audience`, and `identity.front_matter_role`; rebuild p1-p3 as a cover/title/scope system before scaling. |
| `page-role-rhythm-weak` | Full v2 coverage passes, but contact-sheet rhythm is still a long run of planner/final-check/exam/form pages. | Insert or redesign editorial anchors and reduce form-only stretches so the book alternates cover, opener, article/evidence, method, practice, writing, handbook, and answer-key roles. |
| `abstract-asset-drift` | Final generated cover/opener/photo/context imagery is hard to understand: abstract paper sculpture, symbolic board, token map, floating strips, or concept-art composition. | Regenerate first as realistic nature, landscape, wildlife, or animal imagery tied to the content when suitable; otherwise use campus/classroom/library/study or modern human learning/life scenes; rerun asset QA. |
| `cover-image-reuse` | The cover image appears again on a unit opener, photo-passage, or inner context page, or the same bitmap is reused under multiple asset ids. | Generate separate assets for each page role and set `allowed_templates`; rerender the contact sheet. |
| `stacked-opener` | Unit opener is several unrelated strips/cards rather than one controlled opening spread, or a `Before the unit begins...` prompt floats on the photo and visually collides with the Objectives band. | Use one image field, one title lockup, one objectives band, and aligned output blocks; put opener prompts inside the objectives band as `.opener-prompt`, not as a floating photo caption. |
| `form-repeat` | Contact sheet is dominated by the same sparse worksheet/table structure. | Replace at least three pages with distinct roles: method, annotated sample, passage, writing planner, handbook. |
| `loose-workbook-tail` | Activity page has a normal question list or spare lines where a designed workbook record surface should be. | Add `workbook-record` / `workbook-practice`: record header, numbered prompts, and stable writing lines. |
| `plain-planner-table` | Planner is only a basic grid with writing lines. | Add a paper-surface block, rule strip, softer prompts, stronger row labels, and stable writing lines. |
| `floating-blank-line` | Exercise blanks look vertically centered, model-note cloze blanks dangle below the paragraph line, record-prompt blanks drop like answer lines, or visible text shows literal underscore glyphs. | Convert underscore runs in all visible exercise text to `.blank`, use the zero-height bottom-rule model, remove upward transforms, lower true writing blanks to the writing baseline/lower edge (`-0.82em`; question lists `-0.88em`), apply `.paragraph-practice p .blank { vertical-align: -0.22em; }` for model paragraph cloze blanks, and apply `.record-prompt .blank { vertical-align: -0.32em; }` for workbook-record prompt blanks. |
| `question-line-double-blank` | A question prompt shows a short inline blank while the same numbered item also has full writing lines below. | Strip author placeholders from `.question-lines li` with `prompt_text_before_write_lines()` before appending `.write-line`; fail `QUESTION_INLINE_BLANK_WITH_WRITE_LINE` if both elements appear in the same item. |
| `rendered-text-glitch` | Text is extractable but the PNG shows ambiguous digits, punctuation spacing, or mixed-script shaping. | Repair wording, spacing, or font; inspect the rerendered PNG before scoring. |
| `student-process-language` | Visible copy exposes internal workflow or AI-ish planning terms. | Rewrite as concrete learner instructions and scan extracted PDF text. |
| `thin-method` | Teaching page has headings but not enough explanation, examples, margin cues, or guided practice. | Add textbook texture: rule table, model sentence, worked annotation, short check, and practice handoff. |
| `weak-backmatter` | Handbook/answer key looks like another worksheet. | Increase reference density, use quiet blue-gray field, mini rules, compact tables, and lookup-style hierarchy. |
| `raster-book-drift` | Text-heavy pages are full-page images or body text is hidden inside visual assets. | Rebuild text as deterministic HTML/Typst; keep images for context only. |
| `article-form-missing` | Concept/article page has title and text but no visual/evidence anchor or paragraph rhythm. | Add image/inset/diagram anchor, lettered paragraphs, inline highlights, and compact support notes. |
| `skill-ribbon-missing` | Skill/practice page lacks section ribbon and cognitive labels. | Add ribbon and labels before scoring the form. |
| `exercise-taxonomy-flat` | Practice page is only a long numbered list. | Split into A/B/C sections with word boxes, categorizing charts, and task-type contrast. |
| `backmatter-index-weak` | Handbook lacks index/glossary lookup density. | Add compact lookup rows and index tables. |

Any `landing-cover`, `stacked-opener`, or `form-repeat` finding is a P1 visual issue until repaired and rerendered.

## Minimum Page-Role Contrast

For a 10+ page sample, the contact sheet must visibly contain at least five distinct roles:

- identity page: cover or title page
- navigation page: contents, route, or unit map
- opener page: photo-led unit start
- dense teaching page: method, rule, rubric, or annotated sample
- workbook page: practice/planner with writing space
- reference page: handbook, checklist, answer key, or checkpoint

Do not count a page role if it is only a heading swap on the same table/card layout.
