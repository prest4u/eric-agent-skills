# Vocabulary PDF QA Checklist

## Identity

- Cover upper-left says `Vocabulary Learning`.
- Cover lower-right says `Eric Teaching Studio` and lesson identity such as `Memory Chain Lesson`.
- Title page uses formal lesson language.
- No visible `sample`, `Sample Lesson`, `Template System Sample`, or old studio labels in active source, HTML, or extracted PDF text.

## Build Evidence

For BUILD, run only the commands relevant to the changed artifact and inspect the rendered pages that can falsify the request. The full sequence below is for explicit RELEASE/formal sign-off and stores evidence under the active version directory:

```bash
python3 tools/build.py --profile student-lesson-a4
python3 tools/render_pdf.py --profile student-lesson-a4
python3 tools/validate.py --profile student-lesson-a4
pdftotext outputs/<lesson>.pdf _qa/extracted-student-lesson-a4.txt
python3 <eric-teaching-polish-dir>/scripts/validate_teaching_polish.py --strict _qa/extracted-student-lesson-a4.txt
python3 <eric-designed-pdf-dir>/scripts/qa_textbook_pdf.py --root . --profile student-lesson-a4 --asset-mode final-assets
python3 ./scripts/validate_vocab_pdf.py --root . --profile student-lesson-a4
python3 ./scripts/validate_vocab_pdf.py --root . --profile student-lesson-a4 --require-formal-review
```

## Release visual review

Inspect contact sheet and full-size PNGs. Minimum key pages:

- p1 cover
- p2 title
- p5 glossary
- p6-p8 core-word memory chain
- p9 grammar bridge
- p14 red-word challenge when present
- p15 before-you-leave

The following provenance rules apply only to explicit RELEASE/formal sign-off:

- Formal visual review must be performed by Eric or a sub-agent/independent reviewer, not the implementing agent.
- The reviewer must explicitly use `$eric-review`.
- The review file must include `Skills used:` and name `eric-review`.
- The review file must include `Artifact PDF SHA-256:` for the exact frozen profile PDF; the validator recomputes it and rejects missing or mismatched identities.
- If a sub-agent was used, record `Reviewer: sub-agent-review:<agent-id-or-name>` or equivalent.
- Same-agent review must remain `FINAL_VISUAL_REVIEW: PENDING`.
- `validate_vocab_pdf.py` must read `_qa/visual-review-<profile>.md`; a missing, stale, failed, pending, or same-agent review must not produce a clean release-style PASS.
- p14 red-word challenge is a required key rendered page when present, because red-word line collisions are a known failure mode.

Check:

- No text overflow or orphan labels.
- Writing lines are low-edge handwriting surfaces.
- Record rows do not combine separator rules with student writing rules.
- p9 grammar bridge title uses a compact two-line lockup when the heading is long.
- p9 intro box is compact enough to leave real space for pattern cards and Map Check.
- p9 sentences must render vocabulary markers as styled target words; visible `[[A:...]]`, `[[B:...]]`, or `[[C:...]]` is `VISIBLE_VOCAB_MARKER_LEAK` and a P1 release blocker.
- p9 title, intro, pattern cards, and Map Check must be judged as one coordinated grammar-bridge surface, not as a one-line title patch.
- Tables and cards have stable internal heights.
- B-word Phrase Use pages render `Phrase` and `Sentence` as a readable use surface; example sentences must not break into one-word fragments.
- B-word target highlights stay inline. Treat broad selectors such as `.b-row span` as `B_WORD_SELECTOR_LEAK` and fail the renderer contract.
- Openers and visual pages do not feel repetitive or template-like.
- Functional colors are consistent: teal/blue for structure, magenta/red for target words, yellow/amber for check/action.
- Tone coordination is checked across cover, opener, and body pages; do not fix one page by turning a title black while leaving the rest of the system uncoordinated or too dark.
- Cover/opener dark-tone drift is a validator-backed failure mode. If the first visual pages feel gloomy compared with the workbook body, repair the asset treatment or overlay before formal review.
- Student-facing wording is English-forward and public-facing.

## Formal release rule

Same-agent inspection is sufficient for BUILD and PROOF. Formal RELEASE PASS requires Eric or one independent reviewer. If that sign-off is absent, mark only the release review pending and state the remaining risk plainly.
