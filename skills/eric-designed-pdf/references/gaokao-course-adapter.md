# Gaokao Full-Course Adapter

Use this reference when Eric asks to turn a 中高考 / 高二升高三 / full-course exam program into an Eric-designed student book, teacher book, and A4 lesson pack.

This is not a visual reskin route. Treat the existing DOCX/PDF as prior delivery evidence only. The production source should be structured lesson data when available: `lesson_plan.json`, `question_bank.json`, `passage_bank.json`, `writing_bank.json`, and any source audit reports.

## Scope Lock

Before generation, name:

- source course folder and structured data files
- output delivery folder, never the original course folder
- profiles: for independent lesson-pack delivery, default to A4-only `student-lesson-a4` and `teacher-lesson-a4`; for full books, ask Eric whether the release should be `A4`, `book-trim`, or both before generating `student-book-trim` / `teacher-book-trim`
- student answer policy: clean student profile by default
- teacher-only pages: guide notes, answer ledgers, teaching prompts, and solution notes
- asset mode: `proof-placeholder` for layout proofs, `final-assets` for delivery
- `qa.source_inputs`: every upstream `lesson_plan.json` plus question, passage, and writing bank JSON files, so stale PDFs fail when original course data changes

## Source-To-Role Mapping

Map source block semantics before CSS work.

| Source block | Student-book role | Teacher-book role |
| --- | --- | --- |
| lesson overview / route / timeline | `contents-route`, `scope-map`, or module opener | same page plus optional teacher guide |
| concept explanation / method text | `skill-method`, `grammar-rule`, or `handbook` | add teacher notes only in teacher profile |
| sentence analysis / structure diagram | `sentence-map` or `model-annotation` | add expected answer / explanation rows |
| think-aloud / reading strategy | `article-evidence`, `evidence-annotation`, or `long-sentence-transfer` | add teacher-side cue notes |
| classified practice | `activity`, `categorizing-chart`, or `sentence-transformation` | student page plus teacher key |
| exam MCQ set | `exam-mini-set` with answer record | `teacher-answer-key` chunks |
| passage + questions | split deterministic `article-opener` / `article-evidence` pages, then `exam-mini-set` chunks | same plus answer/evidence key |
| writing task | `writing-planner`, `paragraph-practice`, `correction-rewrite`, `final-check` | model answer notes and rubric key |
| reflection / review | `final-check`, `reflection-record`, or handbook lookup | teacher close / key ledger |

Teacher-book routing update: for independent `teacher-lesson-a4` packs, do not stop at `teacher-answer-key` chunks. The teacher edition should keep the student-equivalent pages in order, but add integrated `teacher-page-note` and `teacher-answer-strip` components where the teacher needs answers or correction cues during class. Add separate `teacher-guide-page` pages for the lesson overview, page-by-page notes, likely errors, board notes, and close checks. If the desired output is only a backmatter key, label it appendix-only; otherwise `student book + appended key` is `TEACHER_BOOK_APPENDIX_ONLY_DRIFT`.

## Lesson-By-Lesson First

For a 20+ lesson real course, do not make the 800+ page full book the first proof. Produce in this order:

1. one independent lesson pack for a representative lesson
2. the remaining independent lesson packs after the first proof is visually accepted
3. the compiled full book only after lesson-level identity, page rhythm, and QA gates are stable

Each lesson pack is its own small project with `book.yaml`, `pages/`, `assets/manifest.json`, `theme/`, `tools/`, `outputs/`, and `_qa/`. For the default delivery route, it exposes two A4 profiles:

- `student-lesson-a4`
- `teacher-lesson-a4`

Do not generate book-trim profiles for single lessons unless Eric asks for them. If `qa.output_mode: a4-only` is set, the source and visible output must not contain `book-trim`, `Student workbook and A4 lesson pack`, `22讲`, or `天津高考英语一轮复习`; use the public course title `高考英语复习`. Single-lesson packs should not use `page_family_mode: v2-full`; that gate belongs to full-book/gallery coverage. Instead, keep strict profile separation, source freshness, asset policy, local validation, student language, contact sheets, and human visual review.

Clean A4-only residue at the correct layer. Student objectives and teacher ledgers may need a visible rewrite such as `回看本课证据方法`, but lesson titles and output slugs must remove `第XX讲`, `第 XX 讲`, and `第-XX-讲` with title-prefix rules, not by globally replacing `22讲`. Broken artifacts such as `第本课程` or independent lesson covers that still show `第N讲` prove the sanitizer leaked across layers and must fail review.

Normalize teacher-visible answer notes before rendering. Teacher keys often combine Chinese explanation with English source phrases; insert CJK/Latin spacing in the generator so `定位第一段planned...` becomes readable source text before it reaches the PDF. Do not patch only the single page where the fusion was first noticed.

The single-lesson cover/title must use the lesson concept as the first signal, not the full-course title. For example, use `高考破局挑战` on Lesson 01 and keep `天津卷英语一轮复习 · Lesson 01` as metadata. A cover title such as `天津高考英语一轮复习` on every single lesson is too generic and weakens the premium feeling.

For Chinese single-lesson covers, do not rely on accidental browser wrapping to create hierarchy. If the lesson concept has a natural editorial hinge, set explicit title-line metadata such as `cover_title_lines: ["高考破局", "挑战"]`; otherwise keep a deliberate single-line lockup. This prevents `single-lesson-cover-title-flat` while still avoiding broken Chinese title wrapping.

Chinese single-lesson title typography should use a modern heavy sans route by default. A deliberate two-line title is still weak if it uses a thin/default CJK serif or sits like ordinary overlay text. At contact-sheet size the title should carry the page like a real cover: strong weight, large optical scale, clean shadow/contrast, and quiet course metadata. Record this as `single-lesson-cover-title-weight-weak` when the words are correct but the title does not feel like a book cover.

Long Chinese lesson concepts need a different title contract from short covers. Titles with colon/list/underscore structures, such as `天津卷单选综合：语境、搭配、结构、排除` or `阅读V_组合限时`, must be split by the generator into explicit `cover_title_lines` before rendering. Normalize list tails into a clean editorial second line, such as `语境 · 搭配 · 结构 · 排除`; use the same title-line metadata on both the cover and the title page; and switch to a long-title optical scale instead of reusing the oversized short-title second line. If p1/p2 disagree, overflow, or squeeze the whole concept into one H1, mark `single-lesson-long-title-overflow` or `single-lesson-title-page-wrap-drift`.

Single-lesson front matter should feel like a book chapter, not a cropped full-book index:

- cover: lesson title, concise subtitle, Studio mark
- title: lesson navigation and profile edition signal
- visual lesson opener: photo-led opener with lesson goals/objectives band
- lesson map: optional compact route surface only when the lesson itself needs it; do not add a global course table of contents or explain that the course has 22 lessons inside a standalone A4 lesson pack. If used, make it a classroom route surface with numbered anchors, a soft paper field, and compact task/scope rows, not a cropped full-book contents page.
- start record: student focus, evidence expectation, next-practice habit
- close/review pages: every independent lesson should end with a real workbook close, not a thin final checklist. Use a thinking/check strip, evidence note, and `next practice` / exit-ticket surface with 2-3 concise prompts and stable writing lines. Do not let adjacent close pages share one grid with different headings only: an anonymous heat/error bank should render as a heat-card surface, while a course-planning close should render as a lesson-review surface. Avoid self-check/card language in student-visible pages.

Single-lesson visible language has its own gate:

- The title page may say `Eric Teaching Studio · 天津卷英语一轮复习`, but it must not expose production status such as `before full-book compilation`, `independent proof`, `student workbook and A4 lesson pack`, or similar build notes.
- A lesson map should use lesson-facing labels such as `Lesson 01 Roadmap`, `LESSON MAP`, `Main Work`, and `Today Leaves`; do not leave full-book footer labels such as `BOOK MAP` or a dense page-index grid unless the page is actually a whole-book map.
- For premium Chinese 中高考 student-book/workbook outputs, use English-first component and exercise labels unless Eric explicitly asks for Chinese workbook labels. Good fixed labels include `In This Lesson`, `Before You Begin`, `Evidence Check`, `Method Focus`, `Model Practice`, `Practice Set`, `Writing Moves`, `Writing Practice`, `Review Check`, `Opening Notes`, `Evidence Notes`, and `Before You Leave`. Avoid English-but-AI or tool-surface labels such as `Today On The Page`, `Evidence Pause`, `Practice Review`, `Method Model`, `Demo Practice`, `Tool Practice`, `Lesson Route`, `Lesson Rhythm`, `Practice Rhythm`, `Micro Skills`, `Practice Log`, `Start Record`, `Personal Check`, `Self Check`, `score moves`, `scorecard`, `action card`, or `self-check card`. Chinese can remain inside explanation text, exam terms, source quotations, and local grammar terminology, but page-role headings should not read like Chinese production notes, generated workflow labels, or student-facing tool names.
- Close/review pages need workbook titles, not internal analysis labels. `Anonymous Error Hotspots` and `Personal Check And Course Plan` should become printable headings such as `Error Pattern Check` and `Next Practice Plan`.
- Inner workbook page headings should default to English even when the source lesson block title is Chinese. Keep necessary Chinese for the cover/course identity and real exam explanations, but map activity, paragraph-practice, reading, writing, final-check, handbook, and vocab-bank headings to clean English role/topic titles before rendering.
- Writing prompts may keep the authentic Chinese Gaokao task stem when it is the source question, but the visible writing task title and key-point labels should use English workbook language. Map titles such as `校园博物馆日活动介绍` to `Campus Museum Day Article`, and labels such as `身份 / 对象 / 目的 / 要点` to `role / audience / purpose / point`.
- Check the renderer, not only page source. In English-first workbook mode, the HTML/PDF renderer must not translate UI furniture back into Chinese labels such as `本讲路线`, `课前记录`, `第10讲`, timing-strip `时间`, or repeated frontmatter footers like `Lesson Map • 天津高考英语一轮复习`. Use `Lesson Map`, `Before You Begin`, `Lesson 10`, and `Time` in folios, badges, ribbons, and timing strips. For books whose cover/title page keeps a Chinese course identity, set an English `footer_title` and make the renderer prefer it. If this regresses, fix the shared renderer label map; do not hand-edit generated pages.
- Reading passage/article titles must be English in student-visible pages. If the source passage title is Chinese or too utilitarian, create a neutral English editorial title from the passage topic; never show Chinese reading article titles in the rendered `article-opener` heading or reading `exam-mini-set` heading. Pair question sets with English prefixes such as `Source Reading`, `Guided Reading`, `Timed Reading`, and `Extra Reading`.
- Student-visible questions, answer records, checkpoints, and planner prompts should prefer English in workbook mode: `Answer + evidence: ____`, `Mark the clue before choosing`, `Before You Continue`, `The problem I just found is ____.` Avoid Chinese shells such as `接下来我们`, `本页回收`, `复盘记录`, `微技能训练`, `作业说明`, `今日记录`, `完成前检查`, `进入下一页前`, `下次先改哪一类题`, or `路线`. Cloze and MCQ stems such as `完形填空第N空`, `第N空`, `根据全文选择`, and `选择最符合` must also become English workbook prompts. Machine QA reports `STUDENT_PROMPT_LANGUAGE_DRIFT` when those shells appear in known workbook prompt bodies.
- Teacher answer explanations should normalize cloze labels to `Blank N` rather than `第N空`; teacher-only Chinese explanation can remain, but exam-label language should not regress.
- Strip source-type prefixes such as `完形填空`, `阅读理解`, `阅读表达`, and `任务型阅读` from the start of article body text before `text_chunks`; also strip trailing source section markers such as `三、` that come from copied exam sections. Render the type as English title/notes such as `Cloze Practice` or `Text type: cloze`.
- Normalize cloze article bodies before rendering. OCR/source patterns such as `17 _ side`, `whenI__18`, `my __19 onthe`, `He __ 24 _`, `30___ flights`, `a_31__`, `ev- ery`, `basket- ball`, `Covid-____ related`, `person— something`, `to bea leader`, or `Situation ,is` must be converted into clean prose with deterministic inline `.blank` spans and normal spacing. Real hyphen-number terms such as `Covid-19 related` must be protected before cloze-slot conversion so the number is not mistaken for a blank. Letter-em-dash-letter phrases should use no-break word joiners around the em dash so `person—something` does not split visually at either side of the dash. The reading passage page should show the passage, not raw answer-sheet/OCR residue; question numbers belong in the following question set and answer key.
- MCQ and cloze question stems are a separate blank system. Inside `exam-mini-set` / `.guided-mcq-set`, author `____` placeholders must become `.exam-stem-slot`, not generic `.blank`; punctuation after the slot must be bound by `.exam-stem-keep`. Generic `.blank` in a guided MCQ stem fails `EXAM_STEM_SLOT_DRIFT`, even if the page otherwise looks acceptable.
- A4 sentence analysis is also a separate surface. A `sentence-map` page in `student-lesson-a4` / `teacher-lesson-a4` must render long sentence / analysis / check content as a stacked paper surface (`.sentence-map-card-stack` with `data-surface-family="sentence-map"` and `data-surface`), not as a cramped wide three-column table. Wide table output fails `A4_SENTENCE_MAP_TABLE_CRAMP`.
- Avoid internal/procedural words in student-visible Chinese such as `路径` when it means a hidden method route. Use `判断依据`, `步骤`, `理由`, or `证据` instead, then rerun `eric-teaching-polish --strict`.
- Cover metadata such as `天津卷英语一轮复习 · Lesson 01` may sit quietly inside the title lockup or title page, but stage labels must not become top-right cover badges.

## Pagination Rules

Long exam courses fail visually when the generator tries to keep the old worksheet density. Use these defaults unless the source page is unusually short:

- exam MCQ: at most two long questions per book-trim page
- passage text: split to readable deterministic chunks before question pages; do not rasterize passages
- teacher answer key: about five answer rows per teacher-key page
- writing/planner prompts: short visible labels plus dedicated write lines; do not put long label-prefixed blanks inline
- categorizing charts: page by real rendered density, not only row count. For book-trim, use about six short rows, five rows for reading/writing or rows above 105 visible characters, four rows above 125 characters, and three rows above 155 characters. Rebuild and check `layout-overflow-<profile>.json`; a 5-row writing micro-skill table with long examples can still overflow.
- A4 profiles: preserve the same content order, but add compact record/check surfaces when the taller page would otherwise feel airy
- 999+ page teacher books: rendered key-page evidence may use four-digit page numbers; validators must accept `profile-page-1000.png` style evidence

## Student / Teacher Separation

Clean student profiles must not contain:

- answers, answer-key pages, teacher-only prompts, teaching tactics, or expected responses
- local paths, QA labels, validator text, source ids, starter sample identity
- internal production language such as `Route`, `主动作`, `维修`, `后台`, `闭环`, `卡片`, `动作卡`, `自检卡`, `得分动作`, `教师话术`, `预期回应`, or generic English production prompts
- Chinese reading passage titles, Chinese workbook-role headings, Chinese production-shell question/prompt labels, or renderer-injected Chinese UI labels when the output is meant to feel like a premium English workbook; use a visible-title map in the generator, keep renderer UI labels English-first, and run source/HTML scans for CJK in `article-opener` / reading `exam-mini-set` headings plus prompt/UI drift strings like `接下来我们`, `本页回收`, `复盘记录`, `本讲路线`, `课前记录`, `第xx讲`, `时间`, and repeated frontmatter footers that pair `Lesson Map` with a Chinese course title

For the default independent A4 route, set explicit profile QA:

- `student-lesson-a4`: `answer_visibility: student`
- `teacher-lesson-a4`: `answer_visibility: teacher`

For an explicitly requested full book, also set `student-book-trim` and `teacher-book-trim` with matching student/teacher answer visibility.

The validator also infers student/teacher mode from those profile names so a missing profile block cannot turn leak scanning off, but explicit config remains part of release source hygiene.

Teacher profiles may contain keys and teaching notes, but they should still look like compact reference pages, not spreadsheets. Use pale reference fields, grouped answer blocks, and five-row chunks instead of one long table.

Teacher profiles also need classroom-operability. For `teacher-lesson-a4`, place concise notes and answer strips close to the matching activity page. Backmatter keys remain useful as lookup, but they cannot be the only teacher affordance in a file called Teacher's Book.

## Visual Rhythm

A 20+ lesson book needs module-level rhythm, not only lesson repetition.

- Insert module openers for grammar, cloze, reading, writing, and final review blocks when the source course has those shifts.
- Rotate unit/module opener accent, layout, and image while keeping the same book identity.
- Break long practice runs with article/evidence, handbook, final-check, or module reset pages.
- Use nature, landscape, wildlife, or realistic animal ImageGen assets first when suitable; use school/study/modern-life scenes only with manifest rationale.
- Cover image is cover-only. Every opener/context image needs a separate asset id and file.
- For independent lesson packs, filter `assets/manifest.json` to only the images actually referenced by that lesson pack, usually the lesson cover and that lesson's opener/context image. Do not leave unused full-course images in the manifest; validators should treat missing manifest paths as real failures.

## QA Requirements

Run project-local build/validate for every generated profile. For the default A4-only independent lesson route:

```bash
python3 tools/build.py --profile student-lesson-a4
python3 tools/render_pdf.py --profile student-lesson-a4
python3 tools/validate.py --profile student-lesson-a4
python3 tools/build.py --profile teacher-lesson-a4
python3 tools/render_pdf.py --profile teacher-lesson-a4
python3 tools/validate.py --profile teacher-lesson-a4
pdftotext outputs/lesson-XX-student-a4.pdf _qa/extracted-student-lesson-a4.txt
python3 <eric-teaching-polish-dir>/scripts/validate_teaching_polish.py --strict _qa/extracted-student-lesson-a4.txt
python3 ./scripts/qa_textbook_pdf.py --root . --profile student-lesson-a4 --asset-mode final-assets
python3 ./scripts/qa_textbook_pdf.py --root . --profile teacher-lesson-a4 --asset-mode final-assets
```

For an explicitly requested full-book route, run the same fresh build/validate loop for `student-book-trim` and `teacher-book-trim`. If using the Typst adapter route, additionally run `eric-pdf` QA.

Freshness is part of source authenticity. The generated project `book.yaml` should declare the upstream structured files:

```yaml
qa:
  source_inputs:
    - /absolute/path/to/01_逐讲交付区/第01讲.../lesson_plan.json
    - /absolute/path/to/data/question_bank.json
    - /absolute/path/to/data/passage_bank.json
    - /absolute/path/to/data/writing_bank.json
```

`qa_textbook_pdf.py` must then require HTML/PDF outputs to be newer than those upstream files as well as local pages, assets, theme, and tools.

## Skill Feedback Loop

When a real course exposes a new failure, update the skill, not only the course project:

- add a failure label if the issue is visual or pedagogical
- add validator logic or tests if the issue can be detected
- add starter examples if the issue came from missing template coverage
- add visible-language replacements when internal wording leaked into student pages
- add evidence freshness rules when a stale screenshot/review could pass
