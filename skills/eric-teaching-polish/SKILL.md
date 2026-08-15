---
name: eric-teaching-polish
description: Use when polishing Eric's teaching materials, lesson plans, worksheets, student-facing handouts, parent-facing notes, class summaries, PDFs/DOCX/slides text, or generated teaching drafts to remove AI flavor and internal production wording. Trigger for 教学材料去 AI 味, 去后台腔, 去内部词, 入口/回收/卡片/路由/动作链/维修层 cleanup, student-facing polish, parent-facing polish, and making teaching content sound like a real teacher rather than an AI workflow.
---

# Eric Teaching Polish

Polish teaching materials so the final visible text sounds like Eric teaching real students, not an AI system describing its own workflow.

This skill is broader than `eric-parent-feedback`: use it for lesson packs, worksheets, student books, teacher notes being converted to visible materials, slides, handouts, and mixed teaching deliverables. For pure parent post-class feedback, prefer `eric-parent-feedback`.

## First Move

Classify the target audience before editing:

| Audience | What to do |
|---|---|
| Student-facing | remove internal planning words; keep instructions simple, exam-grounded, and executable |
| Parent-facing | if it is post-class feedback, switch to `eric-parent-feedback`; otherwise keep calm, specific, non-anxious |
| Teacher-internal | internal terms may remain only if user explicitly wants internal planning; still remove AI filler |
| Public/招生-facing | use student/parent-safe language; no hidden tactics, no overclaiming |

If files are available, inspect the real artifact before polishing. Do not polish from a summary when the actual DOCX/MD/TXT/PDF text is accessible.

## Teacher Guide Answer Design

For teacher editions that mirror a student worksheet, prefer an in-place answer layer:

- Keep the full student-facing question surface in the teacher edition.
- Write the concise answer directly in the original question/table/blank position, using a clearly teacher-only visual treatment.
- Use the explanation block below the task for `为什么 / 依据`, `易错`, `讲法`, and optional `加讲`; do not dump a long answer list there unless the task has no stable question position.
- For open writing or annotation tasks, place a short teacher reference/sample near the task, then use the support block to explain scoring or evidence.
- A teacher edition that makes the teacher mentally map a distant answer appendix back to the student task is not considered class-ready.
- For single-lesson and full-book packages, the teacher edition should be a teaching master, not a thin answer supplement: it must carry the student task surface plus answers, evidence, common errors, and repair notes in the same lesson order.

## Dual-Course Packaging

When the same lesson content is packaged as two outward courses, treat each package as a separate student-visible product:

- Student PDFs may show only the current course identity, not the sibling course title, master-course name, old package name, source folder, or build label.
- Teacher PDFs may mention the teacher role, but should still use the same course identity as the matching student package.
- Filenames, total-book covers, body headers, index workbooks, course说明, and manifest summaries must all use the same outward course name.
- Student-facing package scans must include both ordinary leak terms and cross-package residue such as the other course title, `Vocabulary Hacking` when it is no longer the visible brand, `Soft Signal`, `student_total_a4`, `teacher_total_a4`, `outputs/`, `src/`, `qa/`, local paths, and stale `archive` names.
- Workbook and homework packages must make the classroom pairing visible with a reader-facing title label such as `配套课堂：动词形式判断` or a total-book `对应课堂` column. Do not solve this with internal labels such as `第03讲`, `B轨/B册`, source IDs, build order, or teacher schedule language.

## Core Workflow

1. **Lock visibility**
   - Decide whether the text is visible to students/parents/public or internal only.
   - Visible text must not expose teacher tactics, memory/project labels, route decisions, or production scaffolding.

2. **Protect real teaching content**
   - Keep true question text, answer choices, grammar terms, exam names, page numbers, source IDs, and concrete homework.
   - Do not delete a technical term just because it is formal.

3. **Translate internal wording**
   - Read `references/visible-language-guide.md`.
   - Replace backstage words with student/parent-facing language.
   - Avoid inventing new activities, scores, student behavior, or exam facts.

4. **Run the de-AI stack as roles**
   - `shuorenhua`: protect facts, register, and audience before rewriting.
   - `deslop-zh`: final subtraction; remove empty summaries, fake uplift, and neat template transitions.
   - `remove-ai-flavor` / `de-AI-writing`: patch repeated shells such as `本节课围绕...展开`, `先...再...`, `真正重要的是`.
   - `qu-ai-wei`: avoid sterilizing Eric's real teacher voice.
   - `humanizer-zh`: broad audit only; do not add dramatic personality or unsupported anecdotes.

5. **Validate**
   - For TXT/MD extracted text or any file you edit, run:

```bash
python3 ./scripts/validate_teaching_polish.py path/to/file
```

   - For delivery-bound visible materials, use strict mode:

```bash
python3 ./scripts/validate_teaching_polish.py --strict path/to/file
```

## Output Contract

For a rewrite request, return:

```text
[polished visible text]

修改说明：
- 去掉/改写的后台词
- 保留的教学事实
- 仍需 Eric 确认的信息
```

If the user asks for direct final text only, output only the polished text and necessary fact warnings.

For file edits, report:

- file path edited
- validator result
- any remaining WARN terms and why they are acceptable

## Hard Gates

Visible student/parent/public materials must not contain:

- MBTI, Hermes, memory, hidden project labels, cross-project context
- `挖坑`, `让学生先错`, `教师动作`, `预期回应`
- `心法`, `出招`, `拆招`, `定招`
- `后台`, `路由`, `维修层`, `validator`, `production`, `agent`
- raw route/source/bank codes such as `T1`, `A38`, `B01`, `B41`, `C01`, `D01`, unless they are actual exam labels in the source
- raw source/question codes in visible teaching text such as `TJGK-*`, `SIM-*`, `CLOZE-*`, `READ-*`, `L12-EC03`, or short cloze labels like `T16/B16/G16`. Student materials should hide them; teacher guides should convert them to teachable labels such as `Cloze Blank 16`, `Reading Q36`, `Exam-style writing task`, or `Lesson 12 response item 3`
- teacher timing tables or execution labels such as `0-10`, `10-27`, `课堂安排`, `课堂动作`, `学生产出`, `教师节奏`
- student-visible identity and route labels such as `学生版`, `教师版`, `教师用`, `22讲`, or `第N讲`
- student-visible lesson ranges or route references such as `第07-08讲`, `第10-13讲`, `02-06`, `07-09`, `前四讲`, or `本阶段分钟`; rewrite as `前面几次训练`, `前一阶段`, a stage name, or a direct student task
- standalone course-map labels such as `课程地图`, `22讲路线`, or `Course Map` in ordinary student lesson packs, unless Eric explicitly asks for a visible course overview; fold usage notes into lesson 1 and stage review into the relevant unit instead
- source-management labels such as `source_id`, `TJGK-PAPER`, `SIM-...`, `复用材料`, or `回看材料`; keep them in manifests/internal source notes, while visible pages use quiet labels like `Review Passage`, `Additional Practice`, `Optional Practice`, or `Exam-style Practice`
- production/source sequence fields such as `source_unit_no`, `reader_order`, `build_order`, `canonical_id`, `golden sample`, `thick unit`, or `quality gate`; keep mapping fields in manifests and show students only the final unit title, page number, and learning task
- source-type metadata such as `2025 · cloze`, `2025 · reading`, `2022 · reading_expression`, `reading_expression · 原创天津高考仿真`, `cloze · 原创天津高考仿真`, or a standalone `reading_expression` line; student pages and release teacher guides should use natural task/provenance labels like `Reading Practice`, `Cloze Practice`, `Reading Response Practice`, `Exam Source`, or `Exam-style Practice`
- Chinese cloze/reading item labels such as `博物馆导览与灵活执行 第16空` in later exam practice; use English-forward labels like `Museum Tour and Flexible Guiding, Blank 16`
- internal taxonomy labels such as `SOLO` / `solo`, unless they are part of an authentic source text
- teacher-control wording such as `讲评` in ordinary student worksheets; use `核对`, `订正`, or a concrete student task instead
- teacher-control schedule wording such as `时间安排`, `课堂中必须保留`, `不可被课堂核对占用`, or `样文只能展示`; rewrite as what the student should do now
- student-visible tool-routing language such as `工具调用`, `阅读工具`, `工具选择`, `Tool to use`, or `tool selection`; rewrite as `策略使用`, `阅读策略`, `卡题处理`, or the concrete action students should take
- student-visible backstop wording such as `Backup Passage`, `Backup Full Passage`, `备用阅读`, `备用任务`, or `备用补测`; rewrite as `Optional Passage`, `Additional Practice`, `加练阅读`, or a concrete follow-up task
- student-visible tiering or teacher scheduling language such as `快班`, `慢班`, `补测`, `分层补测`, `剩余20分钟`, `Record the homework requirement`, or `No Immediate Review`; rewrite as a direct optional practice/homework/review task
- student-visible internal track labels such as `A轨`, `B轨`, `C轨`, `Track A`, `Foundation Track`, `Core Track`, `Advanced Track`, `基础差`, or `差生版`; use positive outward course identities such as `稳基线课堂练习`, `标准提升课堂练习`, or `高分冲刺课堂练习`
- reused materials disguised as new/unseen practice, such as `Unseen Full Practice` for a passage already used earlier; mark reuse honestly in the source manifest and give students a review/timed-recovery task label
- answer leakage in student-facing materials, such as `参考答案`, `答案解析`, `答案：`, `解析：`
- production markers such as `prototype`, `draft`, `drafts`, local paths like `/Users/...`, or stale build labels, unless they are part of an authentic source passage and Eric explicitly accepts them
- student-facing writing workflow labels that use standalone `Draft` as a method step; use classroom language such as `First version`, `complete first version`, `write the first version`, or `Revise`
- student-facing writing page titles such as `Low-Error Draft Plan`; use `Low-Error Writing Plan`, `First-Version Plan`, or another classroom-facing writing label
- production/style packaging wording in student-facing front matter, such as `Soft Signal`, `publication edition`, `lesson pack`, `combined book`, or `generated from`; rewrite as natural classroom wording like `本册`, `课堂练习`, `目录页码`, or `本讲页码`
- student-facing production-quality labels such as `English-forward`, `exam-style reading`, or table headers like `Learning object`; rewrite as the actual student instruction or a neutral reader label such as `Topic`
- cross-package residue in a student-facing course, such as the sibling course title, master-course title, old outward package name, raw PDF build name (`student_total_a4`, `lesson01_student_a4`), source folders (`outputs/`, `src/`, `qa/`, `validator/`), or `archive` labels
- OCR/build artifacts in official exam text, including split words (`ev- ery`, `a- gainshe`), glued tokens (`whenI__18`, `onthe`), corrupted options (`confusio`, `expectationoi`), fused PDF words (`fourweek`), and punctuation artifacts (`of*Pirates`)
- fake-complete cloze content: passage blanks and question `Blank N` labels do not match, a 10+ item cloze uses one repeated option set, all answers are the same letter, or the teacher basis repeats a generic line such as `备用题要求先写证据再选答案`
- cramped multiple-choice layout: student-facing grammar, reading, cloze, or integrated workbook items that put the question stem and `A. ... B. ... C. ... D. ...` on the same visual line. Put the stem/question first, then move the options to the next line or a dedicated option block; cloze options should sit in an `Options` cell or option row rather than being glued to the blank/question text.
- fake-complete objective practice: grammar, single-choice, or reading sets where all answer letters fall in the same position or expose a visible answer-position pattern such as `AAABBB`, `ABCDABC`, `ABCDABCD`, repeated cycles, or three same letters in a row; tasks that ask students to revise/read/respond but omit the source text; or integrated lessons that only contain a title/originality marker instead of the promised exercise surface
- fake-complete high-weight homework: a high-difficulty cloze/reading/reading-response/integrated workbook lesson that promises 35-45 minutes but only gives one very short passage, 3-5 items, a thin response surface, or generic evidence/repair rows. Add enough original task surface and make the repair rows item-specific.
- fake-complete later-course homework: main-idea, timed-reading, reading-response, integrated, or final-review homework that keeps the lesson title but does not practise the real move. Main-idea work needs paragraph job/title scope/structure repair; timed reading needs easy-first/return-mark/proof-count practice; reading response needs answer form/text support/boundary repair; integrated work needs grammar, cloze, reading, and next-action switching; final review needs one repeated error, proof place, and next first step.
- anonymous workbook pairing: a lesson homework PDF or merged workbook body that only says `课后练习`/`Topic` and makes the teacher or student infer which classroom lesson it belongs to. Add the outward classroom title on the single-lesson cover/body header/target page and use a total-book `对应课堂` index, without exposing `第N讲`, track labels, or source codes.
- teacher writing-answer gaps: a writing teacher book must provide task-specific reference output, acceptable-outline/point coverage, common return reasons, and one repair standard; a generic task boundary plus three reusable marking rows is not a class-ready answer guide
- teacher-guide boilerplate repeated across many blocks, such as `先给学生 30 至 60 秒独立观察`, `学生回答后，把依据写在题目旁边`, or `请两名学生复述方法`; keep concrete task-specific teaching moves, but consolidate or remove generic repeated control notes
- low-utilization repair residue in teacher guides, especially bilingual template glue such as `先让学生口头说出 Use subject + verb language` or repeated Chinese wrappers around English reference cells; rewrite as natural teacher actions tied to the misconception, such as `先收 subject + finite verb 这一组依据` or `先括出修饰部分`
- low-utilization repair residue in teacher extension pages, especially generic fallback lines such as `顺利学生做；若低错不稳，退回 core。` or `顺利学生做；若证据不稳，退回 line band。`; rewrite with the actual lesson rescue move, e.g. relation check, passive check, line evidence, answer-form repair, or writing risk transfer
- visible layout-repair rationale in finished PDFs, such as `This page breaks the answer-key rhythm` or `打断表格节奏`; rewrite as the classroom decision or student action that the page supports
- vocabulary/tone lesson residue that treats attitude questions as generic evidence lookup, such as only saying `找证据` or `退回 line band`; rewrite with the actual tone move: mood direction, turn word, option mood, too-strong wording, wrong-direction choice, or memory-only translation repair
- main-idea/structure lesson residue that treats paragraph structure as generic line locating, such as `Line-Band Rescue`, `line band + evidence word`, or a main-idea page that only says `找证据`; rewrite with the actual structure move: paragraph job, title scope, ending result, wrong-title rejection, and safer-title repair
- reading-set/timed-combination lesson residue that treats timing control as generic line locating, such as `Line-Band Rescue`, `line band + evidence word`, or a reading-set page that only says `找证据`; rewrite with the actual timed-set move: easy first, skip-return, proof count, return point, and hard-first repair
- integrated objective-reading lesson residue that treats mixed objective questions as generic line locating, such as `Line-Band Rescue`, `line band + evidence word`, or an objective-reading page that only says `找证据`; rewrite with the actual mixed-objective move: question type, evidence, boundary, review/next action, and one concrete repair
- reading-response locate/rewrite lesson residue that treats short answers as generic line locating, such as `Line-Band Rescue`, `Line Bank only`, or a reading-response page that only says `找证据`; rewrite with the actual answer-form move: question form, needed words, answer starter, cut words, subject match, and tense check
- open reading-response lesson residue that treats open answers as generic line locating, retelling, or personal reflection, such as `Line-Band Rescue`, `Line Bank only`, `copy facts`, `retell the whole story`, or `personal opinion first`; rewrite with the actual open-response move: answer position, text fact, because link, boundary, retelling cut, slogan-only rejection, and safe personal link
- paragraph-expansion writing lesson residue that treats paragraph development as generic prompt reading, such as `reader/purpose only`, `Prompt card + rescue + repeat`, or `若句子不稳，退回简单句`; rewrite with the actual writing move: point, support detail, because/link, low-error sentence check, and vague-word repair
- sentence-upgrade writing lesson residue that treats upgrade work as generic prompt reading, such as `reader/purpose only`, `Prompt card + rescue + repeat`, or `顺利学生做；若句子不稳，退回简单句`; rewrite with the actual upgrade move: safe base, connector meaning, one upgrade, added-verb check, and stop/return-to-base
- timed-writing lesson residue that treats timed completion as generic prompt reading, such as `reader/purpose only`, `Prompt card + rescue + repeat`, or `顺利学生做；若句子不稳，退回简单句`; rewrite with the actual timed-writing move: reader/purpose, topic-time-place-reason outline, opening/small text, missing-point check, and plan-write-check
- final-review lesson residue that treats review as a generic writing prompt, such as `Plan Before Writing`, `Tiny Prompt Repeat`, `Low-Risk Writing Extension`, `reader/purpose/required points only`, `全卷讲评`, or a review page that only says `be careful`; rewrite with the actual review move: one repeated error, proof place, next first step, transfer check, and vague-review repair
- numeric teacher route residue such as `Start + 01-07 + 09-10` or `01 + 05 one row + 07 first item + 09`; rewrite as natural classroom path labels rather than generator section math
- release teacher surface residue such as `Line-band`, `Line Bands`, `Line-Band Rescue`, `教师版`, or generic `讲评` in teacher total books and class-ready teacher PDFs; rewrite as natural classroom product and method language such as `Evidence Map`, `Where to Look`, `Teaching Guide`, `课堂讲解`, `core path`, or a concrete teacher decision
- total-book tail-page residue after individual lesson covers are skipped: a final lesson body page that only contains a three-row exit table or one short note may pass single-lesson density but fail as a combined-book sequence ending; repair the lesson source with a next-task transfer, review check, or mini-application before rebuilding the total book
- isolated teacher cue residue such as `Review cue After the key table...` or a one-sentence `Teaching cue` that could sit on its own page; merge it into the relevant answer/evidence/control table or rewrite as a real classroom decision layer
- overstrong inference wording in student reading lessons, such as `What must be true?` when the method is about evidence-bounded inference; use `What is directly true in the text?`, `text fact`, or `what follows without adding a new reason?`
- AI-detection promises or "去 AI 检测率" language
- repeated collection metadata in ordinary student handouts, such as `姓名/日期` printed in every body-page header when it should appear only on the cover or first identity area
- table blanks or answer lines that visually sit through the middle of writable cells; student-facing PDFs should use lower-edge writing lines that feel printable and hand-writable
- machine replacement residue in leveled or rebuilt course packs, such as duplicated heading labels (`Sprint High-Score Sprint Setup`), duplicate cleanup words (`加练加练`), partial replacements (`第本课程`), or production-navigation wording (`内部翻找`)

High-risk terms such as `入口`, `回收`, `卡片`, `动作链`, `得分动作`, `私人自检`, `优先动作卡`, `班级动作热区`, `得分场景`, `能力场景`, `短程维修`, `课堂路线`, `闭环`, `抓手`, `沉淀`, `赋能` should be rewritten in visible materials unless there is a clear non-internal meaning.

## References

- `references/visible-language-guide.md`: internal-to-visible language replacements and anti-AI patterns.
- `scripts/validate_teaching_polish.py`: scan files or stdin for hard forbidden terms and high-risk AI/internal wording.
