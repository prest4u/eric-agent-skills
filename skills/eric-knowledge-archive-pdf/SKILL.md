---
name: eric-knowledge-archive-pdf
description: 创建专业彩色、适合打印且可检索的 A4 知识档案 PDF 系统，结合档案物件摄影、登记元数据、状态映射与克制配色。用于档案目录、知识库、藏品记录、保护修复报告，以及需要博物馆级编辑气质和可审计 PDF 证据的材料。
---

# Eric Knowledge Archive PDF

## Overview

Create archival publications whose structure reads as a catalogue rather than a dashboard. Keep text searchable, imagery unique to each page role, and colour subordinate to professional dark typography.

## Workflow

1. Lock the audience, collection scope, page count, source authority, output path, and no-overwrite policy.
2. Map content to archival page roles: cover/accession, condition record, collection context, cataloguing method, deposit sequence, and closure/boundary.
3. Read [production-grammar.md](references/production-grammar.md) before designing or adapting the route.
4. Build with deterministic HTML/CSS on A4 pages. Keep all instructional and record text live and searchable.
5. Register every image with source or generation method, prompt or deterministic transform, page role, dimensions, no-visible-text policy, and one-page-only use.
6. Render a fresh derivative PDF, then create PDF-origin PNGs and a contact sheet after the final source edit.
7. Verify six-page A4 structure when using the canonical sequence, searchable text, embedded fonts, no JavaScript, no external requests, and zero overlap, clipping, masking, or overflow.
8. Inspect the cover, every image-bearing page, the densest page, the method/data page, and the final page at full size. Freeze hashes only after all writer-side fixes are complete.

## Failure and recovery

Permit at most one bounded recovery for a failure fingerprint and hypothesis. If the same fingerprint repeats, stop editing, preserve the evidence, and withhold sign-off.

### Existing-output collision

- **Stop:** The intended PDF, render, contact-sheet, validation, or evidence path already exists and overwrite authority is absent.
- **One recovery:** Select one fresh derivative path inside the authorized project boundary; never delete, replace, rename, or overwrite the existing output.
- **Regenerate:** Build the PDF, all PDF-origin renders, contact sheet, structural/layout checks, provenance references, and hashes for the fresh path.
- **Withhold sign-off:** Until the fresh output identity is unambiguous and every dependent artifact points only to it.

### Unavailable dependency

- **Stop:** A required local renderer, PDF checker, font, or validator is unavailable, or the available substitute cannot prove the same acceptance criterion.
- **One recovery:** Use one already-installed local equivalent that proves the same criterion; otherwise request authority for the missing dependency and stop.
- **Regenerate:** Rerun the affected command and every downstream render, check, evidence record, and hash.
- **Withhold sign-off:** While the required capability or equivalent evidence remains unavailable; never install a dependency without explicit authority.

### Render or validator failure

- **Stop:** Rendering, structural validation, layout inspection, text extraction, font checking, or Skill validation returns non-zero or violates an acceptance threshold.
- **One recovery:** Preserve the fingerprint, form one falsifiable hypothesis, make one smallest supported repair, and rerun the targeted gate.
- **Regenerate:** If the repair changes source or assets, rebuild the PDF, all renders, contact sheet, dependent checks, provenance if affected, and hashes; otherwise regenerate the failed check and every dependent evidence record.
- **Withhold sign-off:** On any unresolved gate or if the same fingerprint repeats after the single recovery.

### Stale derivative evidence

- **Stop:** The PDF predates source/assets, or any page render, contact sheet, review, validation record, or hash predates the exact artifact it claims to verify.
- **One recovery:** Rebuild once from the current source and regenerate the full downstream evidence chain in dependency order.
- **Regenerate:** PDF, all PDF-origin renders, contact sheet, runtime/layout and PDF checks, visual inspection record, and hashes.
- **Withhold sign-off:** Until timestamps and hashes prove one current, internally consistent derivative chain; never reuse stale evidence.

### Hash or identity mismatch

- **Stop:** A recorded hash, file set, page count, path, or Skill-tree identity differs from the artifact under review.
- **One recovery:** Resolve the intended exact artifact once, rerun its applicable validation, and create a new frozen identity; do not rewrite history to fit a mismatched artifact.
- **Regenerate:** All validation and sign-off evidence bound to the mismatched identity, plus every dependent hash manifest.
- **Withhold sign-off:** Until the replacement artifact identity is reproducible and receives a fresh independent review.

### Incomplete image provenance or licensing

- **Stop:** Any used image lacks owned/licensed source authority, prompt or deterministic transform, page role, dimensions, no-visible-text policy, unique-use record, or required notice.
- **One recovery:** Complete verifiable records from existing authorized evidence, or replace the asset once with an owned/generated local asset; never infer rights or upload private material.
- **Regenerate:** Provenance and notices; when an asset changes, also rebuild the PDF, all renders, contact sheet, image inspection, downstream checks, and hashes.
- **Withhold sign-off:** While any source right, licence, transformation, text policy, or unique-use claim remains incomplete.

## Visual rules

- Use charcoal as the structural primary, paper beige as a neutral ground, dark moss as the secondary, and one muted signal colour.
- Put colour in object imagery, evidence classes, accession markers, and sparse signals. Never make colour the only carrier of status or meaning.
- Preserve asymmetric catalogue composition, fine rules, accession codes, generous paper fields, and distinct page-role rhythms.
- Use documentary object, material, conservation, or collection photography without visible text, labels, logos, watermarks, or fake marks.
- Use each image once. Do not reuse the cover plate on an inner page.
- Keep small record text legible in print, body typography professionally dark, and photographs at effective 180 DPI or higher.

## Boundaries

- Do not imitate a museum website, use UI panels, or turn the catalogue into an inventory spreadsheet.
- Do not rasterize text-heavy pages or embed third-party collection screenshots.
- Never overwrite an existing output; create a fresh derivative or stop.
- Never reuse stale derivative evidence or rewrite a frozen identity to fit current files.
- Never install this Skill or a dependency globally without explicit authority.
- Never publish, upload, deploy, email, or otherwise distribute an artifact without explicit authority.
- Never self-approve a frozen final; close the writer window and hand exact hashes to an independent reviewer.
