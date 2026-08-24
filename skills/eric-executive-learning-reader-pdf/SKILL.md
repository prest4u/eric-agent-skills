---
name: eric-executive-learning-reader-pdf
description: 创建专业彩色的六页 A4 高管学习读本 PDF，采用克制的午夜蓝、酒红与古铜编辑体系，提供可检索文本、独立无字图像、打印安全排版、来源记录和逐页质检。用于高管教育、研讨会读本、领导力案例与职业学习材料。
---

# Eric Executive Learning Reader PDF

Create a compact executive reader that changes the participant's point of attention across six non-repeating page roles. Keep the result editorial, reflective, searchable, and safe to print.

## Workflow

1. Lock the audience, six-page A4 identity, authoritative copy, derivative output path, and no-overwrite policy.
2. Preserve the six roles: paced interruption, case question, dialogue positions, seminar interval, case-room deliberation, and organizational transfer.
3. Read [references/visual-production-grammar.md](references/visual-production-grammar.md) before styling or selecting imagery.
4. Keep live text in HTML/CSS. Use raster imagery only as a supporting field; never rasterize a text-heavy page.
5. Limit the edition to one primary, one secondary, and one signal colour plus paper neutrals. Keep dark typography and structural rules legible without colour.
6. Give every image a unique page role and file. Register its source/generation method, prompt or deterministic transform, dimensions, no-visible-text policy, and page use.
7. For deterministic duotone/tritone adaptation of an owned grayscale source, use `scripts/colorize_reader_asset.py`. Never overwrite its input or an existing output.
8. Build a new `-color` PDF, render all six PDF-origin pages, and create a fresh contact sheet.
9. Run `qpdf --check`, `pdfinfo`, `pdftotext`, a JavaScript scan, and a browser geometry audit for overflow, collision, occlusion, clipping, console errors, and external requests.
10. Inspect the cover, every image-bearing page, the densest page, the method/data page, and the final page at full size. Record writer inspection as candidate evidence only; do not self-approve FINAL.
11. Freeze exact hashes for the PDF, contact sheet, six page renders, SKILL.md, and `agents/openai.yaml`; close the writer window after freezing.

## Stop conditions

Stop rather than patch repeatedly when the same failure fingerprint returns after one hypothesis-bounded repair. Stop for overwrite risk, unclear authority, private upload, paid/external dependency, text rasterization, asset reuse, or inability to prove exact identity.
