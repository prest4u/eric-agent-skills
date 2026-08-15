# English teaching grammar

Build each teaching artifact around an observable learner action: notice, select, classify, transform, explain, produce, or reflect. Match the action to the stated language objective and audience.

## Structure a learner task

1. State a short bilingual purpose.
2. Supply the minimum context needed to make the language choice meaningful.
3. Give one unambiguous action with visible response space.
4. Use options that are plausible but distinguishable by the targeted language feature.
5. Add a concise evidence or reflection prompt when reasoning matters.

## Write multiple-choice practice

- Test one main language decision per item unless integration is the stated objective.
- Keep the stem, options, and punctuation parallel.
- Use context that determines the intended tense, word class, connector, reference, or meaning.
- Avoid clues created by option length, grammatical mismatch, or repeated wording.
- Author each item with `soft-question(stem:, choices:)`. Keep each checkbox, A–D label, and option text in the same `soft-choice` cell; never build marks as a separate row or column.
- Replace every source blank with `soft-blank`; never carry raw underscore runs into Typst markup.
- Separate items visually so students can scan, mark, and revisit them without losing place. Keep one question block unbroken across pages.

## Sequence beginner pronunciation

- Classify every sound in a task as a new target, a previously taught target, or an untaught carrier. Keep a cumulative taught-sound ledger across lessons.
- Before a new target can be independently heard, decoded, transcribed, blended, spelled from IPA, or scored, give students an accurate visible articulation/auditory cue, let them hear a teacher model, and practise it in complete words.
- An untaught carrier may support a target only through ordinary spelling plus a teacher-modelled whole word or sentence. Do not show its IPA, ask learners to decode it, or deduct for its production.
- If a whole IPA string is student-visible and independently scored, every scored unit in that string must already be in the taught ledger. Homophones need context, a constrained word bank, or explicitly accepted alternatives.
- Blind listening prompts show only numbers, response spaces, and necessary categories. Keep the teacher's word/sentence in the teacher-only script, reveal any passage text only after the first response, and scramble answer order so a simple cycle cannot substitute for listening.
- Distinguish stimulus scoring from production scoring. A listening key follows the teacher's actual reading; a learner's stable, documented accent variant remains acceptable in oral production when it preserves the intended contrast.

## Serve different audiences

Student artifacts contain only learner-facing purpose, instructions, prompts, and response areas. Omit `correct-index` and `teacher-note` from the student source. Keep answers, rationale, scoring notes, and teaching moves out of student pages. Author a separate teacher source and label its cover and header `TEACHER EDITION` or `教师版`; use `correct-index` and `teacher-note` only there. Preserve the same factual source in both.

## Preserve task-by-task parity

- Keep every student task in the teacher edition in the same learning sequence.
- Put the answer/evidence or observable success criteria near each matching task.
- Give every reflection or production task an exemplar or observable criteria.
- For each multiple-choice task, name the likely wrong option or common-error signal and give a concrete, task-specific repair move; the correct answer alone is insufficient.

## Sequence and density

Move from orientation to practice, then to a small transfer or reflection action when space permits. Keep each explanation close to the first task that applies it. In a multi-part lesson, allow the next subsection to begin on the same page when the previous task ends naturally; do not turn every teaching step into a separate page. When the brief fixes page count, place semantic page breaks before authoring the final page and use one `soft-reflection` block for its heading, prompt, and writing lines. Do not make a page so dense that writing becomes an afterthought, but do not use empty space as decoration. Shorten nonessential copy or rebalance related task groups before shrinking type, removing writing space, padding page count, or forcing a nearly empty page.
