---
name: eric-pdf
description: Explicit-only Typst A4 classroom adapter and QA workflow. Use only when the user invokes $eric-pdf to start from the bundled A4 Typst starter, adapt an already-defined classroom document into Typst, or freshly compile and inspect an A4 Typst PDF. Do not use for teaching-content authorship (use eric-soft-signal), long textbook/book systems (use eric-designed-pdf), or generic PDF operations (use pdf).
---

# Eric PDF

Adapt an already-defined classroom artifact to a restrained A4 Typst source, then prove that the delivered PDF was freshly compiled and visually inspected. Keep this Skill secondary to the content-owning workflow.

## Boundary

- Use `eric-soft-signal` as the primary route for creating or revising Eric English teaching documents, including their normal A4 output.
- Use `eric-designed-pdf` for textbook, workbook, handbook, book-trim, long-course, or publishing-system work. Use this Skill only for that system's explicit Typst A4 adapter/QA step.
- Use `pdf` for reading, extracting, merging, splitting, rotating, OCR, forms, encryption, or other generic PDF operations.
- Do not invent teaching content, visual doctrine, book architecture, or publication review here. Invocation grants no overwrite, install, external-action, or publication authority.

## Runtime root

Resolve `<skill-dir>` from the directory containing this `SKILL.md`. Use only paths below that resolved root for bundled resources; never hardcode an installed user path.

## Workflow

1. Confirm the authoritative source, audience (`student`, `teacher`, or `general`), destination `.typ` and `.pdf` paths, render directory, and overwrite policy. Default to new paths.
2. If a Typst source already exists, preserve its content and adapt only the A4 layout/QA surface requested. Otherwise create a starter with:

   ```bash
   python3 <skill-dir>/scripts/init_a4.py /absolute/path/to/document.typ
   ```

3. Keep imports relative to the document. Use `assets/eric-a4-starter.typ` only as a small layout adapter: warm paper, quiet clay accent, cover/body split, stable writing lines, and A4 page setup.
4. Build learner function before decoration. For student output, remove answers, teacher instructions, rubrics, internal labels, and source identifiers.
5. Freshly compile, check structure/leaks, and render key pages in one command:

   ```bash
   python3 <skill-dir>/scripts/qa_typst_a4.py /absolute/path/to/document.typ /absolute/path/to/document.pdf \
     --out-dir /absolute/path/to/_qa-pages --profile student --require-visual-checks \
     --visual-check cover,first-body,dense,final --json
   ```

6. Inspect the emitted PNGs at full size. Read [QA checklist](references/qa-checklist.md) for visual reject conditions and dependency failure handling. Repair the Typst source, choose a fresh PDF/render path, and rerun until the machine status is `pass` and visual issues are cleared.
7. Report the Typst path, PDF path, fresh compile result, machine QA status, rendered pages inspected, fixes made, and exact remaining risk.

## Completion conditions

- The PDF comes from the current Typst source in this run.
- Every page is A4, the file opens, no page is structurally blank, and the PDF metadata identifies Typst.
- Student/teacher profile and source leak scans pass.
- The render directory contains only pages from this run.
- The checked views include cover, first body, final, and at least one dense/table/workspace/formula/diagram page.
- A human has inspected the rendered pages; script success alone is not visual approval.

## Stop conditions

- If Typst or PyMuPDF is unavailable, stop with the script's dependency message. Do not install anything unless the user separately authorizes it.
- If an output or render directory already exists, use a new path unless exact overwrite authority is explicit; only then pass `--overwrite` or `--overwrite-rendered-pages`.
- If a scored/source-faithful diagram lacks a verified source crop, vector, or coordinates, leave it pending rather than inventing it.
- If the request grows into teaching-content design or a book system, return control to `eric-soft-signal` or `eric-designed-pdf`.
