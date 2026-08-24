---
name: eric-slate-white-pdf
description: 【雾蓝白】Create, restructure, render, and visually QA restrained reader-facing PDFs in the official Eric Slate White PDF｜雾蓝白 editorial theme. Use for polished essays, thought pieces, briefs, explanatory documents, personal writing, and premium Chinese or bilingual PDFs that need cool white paper, slate-blue editorial structure, role-based typography, generous whitespace, and audience-first organization. Do not use for PDF forms, OCR, merging/splitting, posters, dashboards, or worksheet-heavy teaching packs.
---

# Eric Slate White PDF｜雾蓝白

Create quiet, analytical editorial PDFs. Preserve the official theme identity while adapting page roles to the content.

## Workflow

1. Lock the audience, source text, intended reading context, output path, and overwrite policy.
2. Reframe the material for the reader before styling it. Remove chat residue, process commentary, repeated claims, and language that talks down to the audience.
3. Read `references/page-roles.md` before selecting pages. Read `references/visual-system.md` before changing typography, color, spacing, or page structure.
4. Create a fresh working document:

   ```bash
   python3 scripts/new_document.py \
     --out <fresh-project-dir> \
     --title "<document title>" \
     --subtitle "<reader-facing subtitle>"
   ```

5. Edit the copied `document.typ`. Keep only page roles the content needs; add roles from the reference instead of repeating one shell.
6. Compile from the project directory:

   ```bash
   typst compile document.typ document.pdf
   ```

7. Render every page and inspect the real output:

   ```bash
   pdftoppm -png -r 144 document.pdf _qa/page
   ```

8. Run the structural check:

   ```bash
   python3 <skill-dir>/scripts/check_pdf.py --pdf document.pdf
   ```

9. Deliver the new PDF and, when useful, the editable Typst source. Never overwrite a supplied PDF.

## Theme Lock

- Use the exact display name `Eric Slate White PDF｜雾蓝白`.
- Keep the paper cool white, the body near-black, and slate blue as the only structural accent family.
- Use color for navigation, rules, section numerals, and restrained emphasis—not decoration.
- Keep the background visibly quieter than pure screen white without making it gray.
- Preserve grayscale readability.

## Page Grammar

- Use one main entry point per page.
- Keep the left editorial rail for section identity, not on every page by force.
- Vary emphasis among left-rail quotations, quiet side notes, evidence rows, and open whitespace. Do not center a pull quote on every page.
- Use filled boxes rarely. Prefer hairlines, spacing, alignment, or one-sided rules.
- Keep prose pages open; use denser structures only for comparisons, evidence, steps, or reference material.
- Use at least two page roles in documents longer than three pages and at least four roles in documents longer than seven pages.

## Typography

- Songti/serif: primary titles and body reading.
- PingFang/sans: leads, notes, labels, and functional explanation.
- Fangsong: selected pull quotations only.
- Avenir/Baskerville or safe fallbacks: English microtype and numerals only.
- Do not add another display family without explicit user direction.

## Cross-Theme Validation

When a structural change is intended for both official themes, render the same bounded sample with `$eric-moss-ivory-pdf`. The page roles, line breaks, hierarchy, and spacing should remain valid when only theme tokens change. Fix the shared structure before adding theme-specific exceptions.

## Completion

Confirm all of the following:

- A4 size, intended page count, selectable text, and embedded fonts.
- No blank page, overflow, clipping, missing glyph, detached note, or near-empty accidental spill page.
- Footer and microtext remain readable in grayscale and ordinary printing.
- The document reads like a publication, not a chat transcript, dashboard, poster, or component gallery.
- The visible title and filename contain no local paths, version chatter, or technical labels.
