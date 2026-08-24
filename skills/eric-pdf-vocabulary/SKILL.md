---
name: eric-pdf-vocabulary
description: 【词汇讲义】Create, repair, and QA standalone A4 vocabulary lesson PDFs for Gaokao vocabulary, Vocabulary in Use for Exam, memory-chain pages, red-word review, and 40-word lesson packs. Use alone for a portable vocabulary lesson or optionally combine with Eric Soft Signal and Eric-designed-pdf when those skills are installed.
---

# Eric PDF Vocabulary

## Use This Skill When

Use this Skill for 高考词汇 PDF, vocabulary教材, `Vocabulary in Use for Exam`, memory-chain lessons, red-word review pages, 40-word lesson packs, or vocabulary PDF visual repair. It includes a standalone Typst starter. When `eric-soft-signal` or `eric-designed-pdf` is installed, their broader surface and QA rules may be added, but they are never required for this Skill to work.

Default output is an A4 independent student lesson pack. Add teacher guide, answer key, or full-book packaging only when the user asks for that layer.

## Operating Rule

If an artifact already exists, inspect the active `book.yaml`, `pages/`, `tools/build.py`, generated PDF/HTML, contact sheet, and relevant rendered pages before changing it. If none exists, create the smallest usable lesson artifact immediately. A visual acceptance decision requires rendered-artifact inspection; source code alone is insufficient.

Prefer repairing the renderer and reusable helpers instead of patching one page with local CSS. When a visual bug appears, convert it into a vocabulary PDF rule, validator check, or reusable component.

## Vocabulary PDF boundary

Derive the active project root, source word list, target audience, output profile, and delivery intent from the request and workspace. Ask only when a missing choice would change the actual product, overwrite an accepted version, incur cost, or trigger external release.

Confirm these boundaries:

- Default deliverable is a student-facing A4 vocabulary lesson pack unless Eric explicitly asks for teacher guide, answer key, or full-book packaging.
- A release build must use final-assets or approved licensed/owned visuals; proof placeholders cannot be presented as final.
- Do not overwrite an accepted candidate. Create a new version or archive the previous one first.
- Keep public identity stable: `Vocabulary Learning`, `Eric Teaching Studio`, and `Memory Chain Lesson`.
- Preserve the A/B/C word split unless the supplied word list forces a documented exception: A words: 12, B words: about 20, C words: about 8.
- BUILD and PROOF may use same-agent visual inspection and repair. Only an explicit RELEASE/formal sign-off requires independent `$eric-review` provenance.
- If the task is really a generic PDF operation, full textbook transfer, IELTS writing pack, or markdown whitepaper, route through the more specific PDF skill before editing.

## Workflow

1. Locate or create the active vocabulary project. For a new standalone lesson, run `python3 ./scripts/new_vocabulary_lesson.py --out <project-dir> --title "<lesson title>"`. Preserve an accepted prior version when a change would overwrite it.
2. Read the current PDF, contact sheet, and page PNGs at full size. Key pages are cover, title, opener, reading glossary, core words, grammar bridge, red-word challenge, and before-you-leave.
3. Confirm public identity:
   - Cover upper-left: `Vocabulary Learning`
   - Cover lower-right: restrained `Eric Teaching Studio` plus lesson identity, normally `Memory Chain Lesson`
   - No visible `sample`, `Sample Lesson`, or `Template System Sample` in source, HTML, or extracted PDF text.
4. Keep the 40-word lesson structure:
   - A words: 12 core words, deep use with meaning, phrase, grammar, exam sentence, watch note, and one learner sentence.
   - B words: about 20 useful words, phrase/use oriented.
   - C words: about 8 recognition words, fast reading and meaning recognition.
5. Build the learner route as reading -> glossary -> memory chain -> grammar bridge -> B/C recognition -> output -> red-word review -> before-you-leave.
6. Produce the visible lesson/PDF, then run the cheapest check that can falsify the current request. A normal BUILD usually needs a fresh build plus inspection of changed/key pages; do not automatically run every equivalent validator.
7. For an explicit RELEASE or formal sign-off, run the full applicable domain checks and vocabulary QA with `--require-formal-review`. Draft and proof work must not use that flag or wait for an independent reviewer.

## Review protocol

Same-agent inspection is valid for BUILD and PROOF and may be followed by ordinary fixes. It does not grant formal RELEASE sign-off.

For an explicit RELEASE or formal visual sign-off, freeze the exact artifact and use at most one independent reviewer with `$eric-review`. The release review file records:

- `Reviewer: sub-agent-review:<agent-id-or-name>` or `Reviewer: independent-review:<name>` or `Reviewer: user-confirmed`
- `Skills used: eric-review, eric-pdf-vocabulary` plus `eric-designed-pdf` when visual design is being judged
- `Review method: sub-agent read-only review` or equivalent provenance
- `Artifact PDF SHA-256:` matching the exact frozen profile PDF
- `Tone coordination:` covering cover/opener/body-page palette harmony and dark-tone drift
- `Canon comparison:`, `Reject patterns checked:`, `Font decision:`, `Visual diagnosis:`, `Weak pages:`, and `Remaining risk:`

Do not write formal `FINAL_VISUAL_REVIEW: PASS` from the same agent that implemented the frozen RELEASE artifact. If release review is unavailable, keep that release status `PENDING`; do not block an ordinary classroom draft on this formal field.

Known release blockers that must be named in review and encoded in the validator:

- `VISIBLE_VOCAB_MARKER_LEAK`: raw `[[A:...]]`, `[[B:...]]`, or `[[C:...]]` appears in HTML or extracted PDF text.
- `GRAMMAR_TITLE_COORDINATION_DRIFT`: p9/Grammar Bridge is repaired by an isolated black title patch instead of a coordinated teal/blue-ink surface.
- `FRONTMATTER_DARK_TONE_DRIFT`: cover or opener dark-pixel balance makes the first impression too gloomy compared with the light workbook pages.
- `B_WORD_SELECTOR_LEAK`: broad selectors such as `.b-row span` make highlighted target words render as block fragments and break Phrase/Sentence reading flow.
- `RELEASE_TEACHER_PRODUCTION_LABEL_LEAK`: final teacher total books or reader-package teacher PDFs visibly say `Teacher Control` or `教师控制页` instead of the release-facing `Teaching Guide` / `教师教案`.
- `READER_FACING_PRODUCTION_NAME_LEAK`: final reader-package filenames, indexes, or manifests expose production labels such as `teacher_control`, `Teacher Control`, or `教师控制页`.

## Page Roles

Vocabulary lessons should feel like a printed workbook, not a form dashboard. Page roles must carry a clear learner action:

- `cover`: formal book identity with one final visual asset.
- `title`: public course rhythm and navigation, no sample wording.
- `unit-opener`: strong visual entry and lesson route.
- `reading`: context-first exposure to target words.
- `glossary`: short meaning access plus a quick check.
- `memory-chain`: word card with meaning, phrase, grammar, example, and one low-baseline sentence slot.
- `grammar bridge`: pattern transfer from word to sentence.
- `B/C recognition`: fast phrase/use recognition, not deep word-card repetition.
- `output`: one accurate sentence or short paragraph that uses selected words.
- `red-word challenge`: lightweight spaced review.
- `before-you-leave`: final record surface and next practice plan.

See `references/page-role-contracts.md` for stricter page contracts.

## Writing Lines

Do not use a single generic `.write-line` for every vocabulary writing surface. Use semantic writing-line classes:

- `memory-sentence-line`
- `glossary-record-line`
- `grammar-map-check-line`
- `red-review-line`
- `final-record-line`
- `next-plan-line`
- `no-row-rule-record`

Every line must read as a low-edge writing space after PNG inspection. Reject floating blanks, short orphan lines, mid-cell underlines, prompt-line disconnection, and punctuation isolated after a blank.

Record surfaces must not combine ordinary row separators with handwriting lines. Use `no-row-rule-record` on red-word/final-record surfaces so the writing line is the only strong horizontal rule inside a row.

Grammar bridge pages should use a compact two-line title lockup (`grammar-bridge-title`) and compact intro surface (`grammar-bridge-compact`) when the heading contains a colon or long sentence.

See `references/writing-line-standards.md`.

## B-Word Phrase Pages

B-word pages are not database tables. They should make each word immediately usable through a readable `Phrase` + `Sentence` surface.

- Keep the row structure closer to: word/part of speech, meaning/simple English, then a combined use area with phrase and sentence.
- The example sentence must read horizontally as a sentence, not as isolated one-word fragments.
- Target-word highlighting must remain inline inside the sentence.
- Do not use broad selectors like `.b-row span`; scope part-of-speech styling to the word-head cell, for example `.b-row > div:first-child span`.
- If a visual bug makes B examples wrap into target-word fragments, repair the renderer/helper and add a validator check rather than shortening one lesson's examples.

## Visual Standards

Use premium, light, printed-workbook design. Avoid template-looking gradients, cramped form rows, repeated identical opener surfaces, and student-facing tool labels such as scorecard/self-check card. Keep English-forward workbook language; Chinese is for necessary scaffolding, exam terms, or identity.

Cover, opener, photo-passage, and context visuals should be final ImageGen/licensed/owned assets for release builds. Proof placeholders are acceptable only during layout validation and must not be marked final.

## QA Commands

Typical A4 lesson closeout:

```bash
python3 ./scripts/new_vocabulary_lesson.py --out <project-dir> --title "Vocabulary Learning"
typst compile <project-dir>/lesson.typ <project-dir>/lesson.pdf
pdftotext <project-dir>/lesson.pdf <project-dir>/lesson.txt
python3 ./scripts/validate_vocab_pdf.py --root <project-dir> --profile student-lesson-a4
# Optional integrations when the corresponding skills are installed:
python3 <eric-teaching-polish-dir>/scripts/validate_teaching_polish.py --strict _qa/extracted-student-lesson-a4.txt
python3 <eric-designed-pdf-dir>/scripts/qa_textbook_pdf.py --root . --profile student-lesson-a4 --asset-mode final-assets
```

Only for explicit RELEASE/formal sign-off, add:

```bash
python3 ./scripts/validate_vocab_pdf.py --root . --profile student-lesson-a4 --require-formal-review
```

Same-agent visual inspection is sufficient for ordinary drafts. A formal RELEASE PASS requires Eric or one independent reviewer using `$eric-review`; do not create a review-of-review chain.

Run package maintenance after editing this skill:

```bash
python3 ./scripts/test_validate_skill_gates.py
python3 ./scripts/validate_skill_gates.py
```

## Failure Branches

| If this happens | Do this |
|---|---|
| Source word count or A/B/C split is unclear | Stop layout work, make the split explicit, and record any deviation from A 12 / B 20 / C 8 before rendering. |
| `[[A:...]]`, `[[B:...]]`, or `[[C:...]]` appears in HTML/PDF text | Treat as `VISIBLE_VOCAB_MARKER_LEAK`, repair marker rendering in the reusable helper, rerender, and rerun vocabulary QA. |
| B-word example sentences break into isolated fragments | Treat as `B_WORD_SELECTOR_LEAK`, fix selector scope or row geometry in the renderer, not by deleting examples. |
| Writing lines float, collide with row rules, or become too short | Replace generic line styling with the semantic line class for that page role and inspect the rendered PNG. |
| Cover/opener feels dark while body pages are light | Treat as frontmatter tone drift; repair image treatment/overlay and get a fresh contact sheet review. |
| Teacher total guide still says `Teacher Control` or `教师控制页` | Treat as `RELEASE_TEACHER_PRODUCTION_LABEL_LEAK`, rebuild the affected teacher unit PDFs and total books, refresh extracted text QA, and rerun release validation plus sub-agent review. |
| Reader package filenames, indexes, or manifests still say `teacher_control`, `Teacher Control`, or `教师控制页` | Treat as `READER_FACING_PRODUCTION_NAME_LEAK`, rename reader-facing teacher files to `teacher_guide`, regenerate indexes/manifests, and add a validator gate before release. |
| Only same-agent review exists for an explicit RELEASE | Keep `FINAL_VISUAL_REVIEW: PENDING`, run `validate_vocab_pdf.py --require-formal-review`, and request Eric or one independent review. |
| Validator catches a new visual bug | Add the reusable rule to `validate_vocab_pdf.py`, this skill, or the relevant reference before closing the task. |

## References

- `references/page-role-contracts.md`: vocabulary page role contracts.
- `references/writing-line-standards.md`: reusable writing-line standards and reject patterns.
- `references/qa-checklist.md`: 9.8/9.9 release checklist and evidence requirements.
- `scripts/validate_vocab_pdf.py`: vocabulary-specific identity and line-class validator.
- `scripts/validate_skill_gates.py`: package maintenance gate for this skill.
- `test-prompts.json`: forward prompts for regression and routing checks.
