# Writing Line Standards

## Global Rule

Rendered PNGs are the source of truth. A line that is mathematically baseline-aligned can still fail if it visually floats through the middle of the text row.

Vocabulary PDFs must use semantic line classes. Do not solve all cases with generic `.write-line`.

## Required Classes

### `memory-sentence-line`

Use for My Sentence slots on A-word memory-chain cards.

- Prompt and line should feel like one sentence.
- Line sits low, close to the writing baseline.
- Keep sentence punctuation attached visually; avoid a lone period floating after a short blank.
- Keep card heights stable across the 2x2 grid.

### `glossary-record-line`

Use for p5 Glossary Check or short definition recall.

- Full-width or near full-width line inside the check surface.
- Low baseline, aligned with the prompt/number.
- Enough vertical breathing room for handwriting.

### `grammar-map-check-line`

Use for grammar bridge map checks.

- Works inside a strip or sentence block.
- Matches the height and baseline rhythm of neighboring pattern cards.
- Should not look like a small underline pasted into a large block.

### `red-review-line`

Use for p14 My Red Words / red-word challenge rows.

- Do not pair it with a normal row `border-bottom`.
- Multiple lines in one row need vertical spacing between handwriting rules.
- The line should start in the same content column as the prompt, not drift under the number.

### `final-record-line`

Use for p15 Red Word Record rows.

- Number dot, prompt, and line align as a single record row.
- Row height must support handwriting.
- Multiple rows should use the same line length unless the prompt intentionally changes the surface.
- Use this inside a `no-row-rule-record` surface. A normal row separator plus a final record line creates the visual conflict Eric rejected.

### `next-plan-line`

Use for p15 Next Practice Plan or future action ticket.

- Line should cover the main content width.
- If the prompt is long, place the line below the prompt rather than forcing a broken inline blank.
- Avoid short, biased, or visually suspended lines.

## Reject Patterns

- Floating blank: underline appears in the vertical middle of a text row.
- Short orphan line: blank is too short to invite a real written answer.
- Mid-cell underline: line crosses table cell center rather than sitting near the lower edge.
- Prompt-line disconnection: prompt is on one side, writing line feels unrelated.
- Punctuation orphan: period/comma sits alone after the line.
- Generic-line drift: broad `.write-line` CSS changes one page while breaking another.
- Row-rule collision: an article/table row separator overlaps or nearly overlaps the student's handwriting line.
