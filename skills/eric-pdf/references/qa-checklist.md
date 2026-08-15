# Typst A4 QA Checklist

Read this before inspecting rendered pages or when the QA script fails.

## Dependency failures

- `Typst executable not found`: stop and report that `typst` is required for a fresh compile. Do not claim an existing PDF is current.
- `PyMuPDF is required`: stop and report that the Python `fitz` module is required for structural checks and PNG rendering.
- Compile failure: repair the first Typst error reported by the script. Do not reuse a stale PDF.

## Machine gates

- PDF opens and has at least one page.
- Creator/producer metadata contains `Typst`.
- Every page is A4 portrait or landscape within the script tolerance.
- No page lacks text, vector drawing, and raster image content simultaneously.
- The Typst source contains none of the internal leak terms reported by the script.
- A student PDF contains no teacher-edition, solution, rubric, board-note, or teacher-only labels.
- Render output is fresh. Existing page PNGs require a new directory or explicit `--overwrite-rendered-pages` authority.

## Full-size visual review

Inspect the cover, first body page, densest/table/workspace/formula/diagram page, and final page. Reject:

- clipped or overlapping text, missing glyphs, formula overflow, or diagram-label collisions;
- blank-looking pages, giant accidental gaps, orphan headings, or cramped tables;
- collapsed writing lines or spaces too small for the learner action;
- a header or folio on the cover, incorrect body numbering, or mixed page-number systems;
- cold dashboard styling, nested UI cards, decorative gradients, watermarks, or stock-like filler;
- teacher answers, scoring rubrics, internal workflow language, source IDs, or local paths in student output.

For a one-page artifact, the same rendered page may satisfy multiple positional views, but still name the relevant dense/workspace/table/formula/diagram category that was inspected.

## Evidence report

Record:

```text
Typst: <absolute source path>
PDF: <absolute output path>
Compile: fresh pass/fail
Machine QA: pass/fail
Rendered pages checked: <absolute PNG paths and roles>
Fixes: <specific repairs or none>
Remaining risk: <specific risk or none>
```
