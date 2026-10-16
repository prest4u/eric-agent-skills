---
name: eric-teaching-polish
description: '【教学润色】Revise teaching text for clear classroom language while preserving source meaning, answer accuracy, and the intended audience.'
---

# Eric Teaching Polish

Polish the supplied unit: a sentence, activity, page, deck or full pack. For a local wording correction, preserve facts, authentic terminology, question wording, difficulty and answer logic. For an explicit exercise-quality rebuild, preserve the learning target and appropriate difficulty while revising the prompts, answers and teacher guidance together. Do not invent a lesson, extra activity, new edition or full review for a local wording request. Use the requested register and concrete learner actions; remove internal workflow language from visible teaching text.

For a lesson title, use a short subject label for the main grammar point or skill area, such as “时间状语从句”, “定语从句”, “写作”, or “时态与语态综合练习”. State the desired independent performance, source material, and classroom context in the objective and task descriptions. Keep the same visible title across the student book, teacher copy, notes, homework, and current course index. Preserve historical titles in archives.

Identify the visible audience from the actual output. Student text must not expose keys, teacher tactics, learner dossiers or internal labels. Parent text reports observed performance with accurate qualifications. Teacher text may contain answers and instruction notes. Preserve exact quoted sources and required grammar examples; do not present your own wording as a quotation to exempt it from revision.

For a teacher guide, keep each task and its answer together, followed where useful by reasoning, likely errors and a usable repair explanation. A requested teacher edition needs the complete student task wording in the same order. An appendix-only key is appropriate when specifically requested. Read [classroom cases](references/classroom-cases.md) only for a matching guide, course-pair or recurring content problem.

Use [visible language guidance](references/visible-language-guide.md) when a substantive rewrite needs examples. Inspect existing course terminology and the current source before replacing it. Compare the revised text with the original for omitted conditions, changed answers and new claims, then read it as a teacher or learner would.

When polishing a newly authored or substantively revised exercise set, inspect adjacent questions, the full page and booklet, and nearby stages. Ask what the learner must decide for each item. Flag repeated sentence frames with token-level swaps (for example, “autumn / every autumn / last autumn”) and repeated positive-sentence-to-negative/question instructions that leave the learner making the same decision, including copies spread across sections. If an answer can be copied from another item with one word changed, repair the affected items within the requested scope by changing the cue and reasoning: verb-cue completion, independent sentence writing, diagnosis and minimal repair, information-gap questions, or short-passage editing as the lesson permits. Keep deliberate repetition when it tests a new cue or delayed recall; teacher notes should identify that purpose. Across staged materials, check that earlier knowledge is used with the new point and that support recedes. Verify every changed prompt against the teacher answer, acceptable alternatives, and likely student misreading. Do not alter exact source quotations or add an unrelated task during a local wording correction.

Count the most frequent time phrases and scenario words in a full exercise booklet. High concentration can hide repeated choices across distant sections even when neighboring questions differ.

For every changed blank, put the teacher answer back into the student stem and read the resulting full sentence. Repair repeated words, incomplete predicates, and answers that contradict a stated time or source fact before rendering.

For data-backed or scenario-backed exercises, compare every model sentence, answer note, and rejected alternative with the actual source. Remove unreported actors, dates, causal claims, and subgroup claims. If a response is grammatical but does not use the preferred practice form, explain that distinction in the teacher copy instead of calling the English wrong. For long handwritten work, inspect the rendered student pages and count usable writing lines against the required words, paragraph breaks, and correction time; inspect teacher pages for stranded notes caused by unused answer lines.

For substantial teaching text or formal delivery, validate the visible text from this Skill directory:

```bash
python3 scripts/validate_teaching_polish.py --audience student <visible-text-file>
```

Use `--strict` for the applicable formal contract, `--audience teacher` only for actual teacher content, and `--language-only` for non-teaching prose. A local correction needs direct read-back and inspection in its existing surface. Do not run the checker against source code as though every code token were learner-facing text. Split mixed-audience content before checking; selecting `teacher` must never hide a student answer leak.

Use `--source-lines START:END` only for exact protected quotations. Its exemption does not waive answer-leak checks. Warnings need editorial judgment; passing a token check does not certify natural prose or exercise quality. The validator cannot detect repeated cognitive work across items, so complete the adjacent-item and answer check above even after a strict pass. Return the revised text or requested artifact and mention a material unresolved source issue plainly.
