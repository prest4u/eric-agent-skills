# Eric PDF Document Type Grammar

Use this reference when an Eric PDF task needs richer visual effects or multiple classroom file types. Keep the Eric/Anthropic-light style: quiet A4 paper, PingFang, warm black text, muted taupe metadata, clay functional emphasis, warm ivory fills, thin tables.

## Shared Page DNA

Every file type should still feel like the same classroom system:

- Cover: upper-third centered title, clay subtitle, short clay line, muted date/version. Do not show a header on the cover. Cover page numbers are normally omitted; when preserving the handbook view, a quiet centered cover number is acceptable. Wrap body pages with `eric-body(title: ...)[...]` so the first body page displays page 1 unless the chosen reference uses continuous quiet numbering.
- Body: 11pt text for student materials, 10.5pt allowed for dense teacher guides.
- Tables: warm hairline borders, cream header fill, very light warm row fill, compact insets.
- Color: clay = action/emphasis, taupe = metadata, pale cream/peach = rule/action and quick-reference boxes.
- Components: use boxes only for rules, timed tasks, checklists, teacher-only notes, or student tracking.
- Avoid: cold gray-white cards, cool-tinted note boxes, dark slabs, decorative cards, heavy backgrounds, icons, gradients, stock images, watermarks, and unrelated layout changes.

## File Types

| Type | Primary Use | Best Components | Density |
|---|---|---|---|
| 课堂练习 | Student does work during class | timed strip, passage, exam-style option rows, answer grid, clue table, error table | High |
| 课上笔记 | Student reviews rules quickly | rule box, quick-reference table, compact checklist, memory cue | Medium |
| 课后作业 | Student executes routine after class | daily task block, checkbox, tracker table, short drill, completion target | Medium-high |
| 教师教案 | Teacher controls pacing and feedback | teacher-only strip, minute flow, answer/evidence table, observation checks, fallback note | High |
| 复习/词库手册 | Student looks up and retrieves | method page, scene/category directory, action strip, lookup table, retrieval drill | Medium |
| 表达手册 | Student produces language | phrase bank, sentence frames, transformation pairs, paragraph skeleton, ruled writing area | Medium-low |
| 数学专题教材 | Student reasons, calculates, and corrects | formula box, diagram panel, example steps, workspace, answer grid, error log | Mixed |

## 课堂练习

Purpose: make the student act under class pressure.

Recommended rhythm:

1. Brief metadata: student, date, version, objective.
2. Section heading with time or task count.
3. Long passage or problem set as plain readable prose.
4. Answer grid or clue/evidence table immediately after the task.
5. Error summary table after a round or section.

Use `eric-timed-strip` before timed tasks and `hermes-table` for answer/clue grids. Keep writing blanks visible. Do not break every paragraph into a card.

For 完形填空, use `eric-choice-row(no, a, b, c, d)` for the ABCD options. Do not put options in a bordered table unless the task is an answer sheet. Formal exam feel matters here: rows should read like `(1) A. story  B. secret  C. lesson  D. subject`.

## 课上笔记

Purpose: compress the lesson into retrievable rules.

Recommended rhythm:

1. Rule box for the central pattern.
2. Quick-reference table for cases or signals.
3. Small checklist for exam-time self-check.
4. Personal record area if the note is tied to a class exercise.

Use `eric-rule-box` for rules, `eric-note-box` for memory cues, and thin tables for cases. Avoid long passages unless they are annotated examples.

## 课后作业

Purpose: turn class work into repeatable action.

Recommended rhythm:

1. Explain why the homework is shaped this way.
2. Daily task block: what to do, how long, how to check.
3. Short practice item or passage.
4. Tracker table with dates and checkboxes.
5. Completion target.

Use `eric-task-card`, `checkbox`, and tracker tables. Homework should feel doable, not like a new textbook chapter.

## 教师教案

Purpose: let the teacher run the class without improvising missing structure.

Recommended rhythm:

1. Teacher-only strip at the top of the first body page.
2. Lesson goal and design logic.
3. Minute-by-minute flow.
4. Full tasks with answers and evidence.
5. Observation checkboxes and fallback notes.

Use 10.5pt text when needed. Teacher-facing PDFs may include internal operational language, but student-facing PDFs must not.

## 复习/词库手册

Purpose: support lookup, retrieval, and repeated review.

Recommended rhythm:

1. Quiet cover with one clear identity: what this manual helps the student retrieve.
2. "How to use this" page or section: usually 3 steps, such as scene -> function -> word form.
3. Directory page: categories/scenes in restrained cards or an index table, each with a short description and count.
4. Repeated chapter/scene pages: opener, action entry strip, core lookup table, extended candidates, common expression patterns.
5. Short retrieval drill: a few blanks with "my answer" and "evidence" columns so lookup turns into practice.
6. Mistake pattern summary if the manual is tied to recent exercises.

Use chapter breaks more often than classroom handouts. A manual can breathe more; it is not constrained by one lesson's timing.

For scene vocabulary or 首字母填空 manuals, read `handbook-view.md`: the richness comes from information architecture, not decoration. Use `eric-method-steps` for the usage guide, `eric-directory-card` for the scene index, `eric-lookup-strip` for the 调用入口, `eric-vocab-table` for the core/expanded word bank, and `eric-initial-drill-table` for the short drill.

## 表达手册

Purpose: help students produce better English.

Recommended rhythm:

1. Topic or function heading.
2. Phrase bank.
3. Sentence frame table.
4. Transformation pair: basic sentence -> upgraded sentence.
5. Writing lines or paragraph skeleton.

Use more whitespace than drills. Output pages need room for handwriting, not maximum content density.

Use `eric-writing-area(lines: ..., label: ...)` for writing areas. Avoid loose `line()` loops for student writing: they can crowd, float, or look unlike printable answer paper.

## 数学专题教材

Purpose: help students move from concept to worked example to independent calculation.

Recommended rhythm:

1. Concept entry: formula, condition, method boundary.
2. Worked example: problem stem, diagram if needed, key observation.
3. Step chain: teacher version shows full solution; student version shows hints or partial structure only.
4. Student workspace: ruled, grid, or blank area sized for real handwritten calculations.
5. Variation set: same method across related problems.
6. Answer grid and error log.

Read `math-materials.md` before creating math PDFs. Use Typst native math for formulas, `eric-math-diagram-panel` for graphs/geometry/source images, `eric-math-workspace` for calculation space, and explicit `version: "student" | "teacher"` switching for solution visibility.
