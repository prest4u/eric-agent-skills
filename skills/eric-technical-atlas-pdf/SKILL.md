---
name: eric-technical-atlas-pdf
description: 创建专业彩色、适合打印且可检索的 A4 技术图谱 PDF，包含材质真实的工程图像、校准标注、系统剖面、方法与数据图版及运营决策页面。用于工程说明、技术手册、系统剖面、运营图谱及专业技术解读材料。
---

# Eric Technical Atlas PDF

## Core outcome

Build a searchable six-role technical publication rather than a dashboard or a raster poster. Keep typography, structure, and evidence professionally dark; use colour to clarify material, classification, chapter position, and sparse operational signals.

## Route

1. Lock the audience, exact copy, page count, A4 output identity, source authority, derivative path, and no-overwrite policy.
2. Preserve an accepted page-role sequence when adapting an existing route. Do not restart visual research unless the structure itself is rejected.
3. Map content to distinct roles: cover cutaway, proposition aperture, system relationship, exploded method plate, delivery evidence, and governance decision.
4. Keep all instructional and annotation text in HTML/CSS or another searchable vector text layer. Use raster imagery only inside bounded technical frames.
5. Read [references/technical-atlas-grammar.md](references/technical-atlas-grammar.md) before changing layout, palette, image treatment, or production QA.
6. Start from [assets/technical-atlas-tokens.css](assets/technical-atlas-tokens.css) when the route has no equivalent token layer.
7. Use [scripts/colorize_technical_asset.py](scripts/colorize_technical_asset.py) only for owned/generated local source images. Record every source hash, transform, mask, page role, dimensions, text policy, and unique use.

## Colour discipline

- Use one primary deep navy, one secondary copper, and one signal orange; treat steel grey as the neutral material family.
- Keep signal orange sparse. Never use colour as the sole carrier of meaning: pair it with a label, number, shape, rule, or position.
- Preserve material legibility. Copper should mark plausible bearings, fasteners, calibrated specimens, or load surfaces—not wash an entire page.
- Maintain dark body text and structural rules. Avoid neon, gradients in text, glossy UI panels, rounded app cards, and decorative data visualizations.

## Image contract

- Use one image once. Give every image a unique page role.
- Require no visible text, labels, letters, numbers, watermarks, logos, fake data, or answer marks inside generated or transformed imagery.
- Prefer close, immediately legible industrial scenes: cutaways, joints, exploded assemblies, calibration rigs, and material specimens.
- Keep annotations outside images as live text. Do not rasterize text-heavy pages.

## Production gates

1. Build a fresh PDF derivative; never overwrite the input PDF.
2. Verify exactly six A4 pages when using the canonical sequence, searchable text on every page, embedded fonts, `qpdf --check`, and `pdfinfo` JavaScript `no`.
3. Render every page from the final PDF and build a colour-preserving contact sheet after the PDF.
4. Run a browser/layout audit for overlap, clipping, masking, overflow, external requests, console errors, and page errors.
5. Inspect the cover, every image-bearing page, the densest page, method/data page, and final page at full size.
6. Freeze exact PDF, page-render, contact-sheet, provenance, source, and Skill hashes only after the final edit. Close the writer window before independent review.

## Stop conditions

Stop for target collision, unclear authority, required edits to a frozen source route or global Skill, private upload, paid/external asset need, destructive action, or inability to bind evidence to the exact derivative. Use one hypothesis-bounded repair for a repeated failure fingerprint; if it repeats, return diagnosis rather than continuing to patch.
