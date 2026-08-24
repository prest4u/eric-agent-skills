---
name: eric-policy-impact-brief-pdf
description: 创建专业彩色、适合打印且可检索的 A4 政策影响简报，明确呈现干预措施、受影响群体、因果机制、证据、不确定性、决策与责任人。用于政策简报、公共部门分析、影响评估、试点决策和利益相关者问责材料。
---

# Eric Policy Impact Brief PDF

## Core outcome

Create a compact public-sector decision document that makes a policy intervention, its causal logic, its evidence limits, and its accountable decision visible. Keep the output editorial and civic, not a consulting slide deck, dashboard, campaign document, or branded government imitation.

## Workflow

1. Lock the decision audience, exact PDF identity, A4 page count, source authority, output path, and no-overwrite policy.
2. Map the content to the six route roles in [references/visual-production-grammar.md](references/visual-production-grammar.md). Preserve the accepted route when adapting an existing brief.
3. Use one primary civic navy, one secondary teal, and one signal ochre. Keep text and structural rules professionally dark. Pair every colour distinction with a label, number, rule position, or line style.
4. Use one unique, text-free public-space or infrastructure image per image-bearing page. Record generation or deterministic transform, page role, dimensions, hashes, and text policy.
5. Keep all substantive copy as HTML/CSS text. Do not rasterize text-heavy pages or invent quantitative evidence.
6. Build a new searchable A4 derivative. Generate fresh PDF-origin page renders and a contact sheet after the final PDF.
7. Verify zero overlap, clipping, masking, overflow, external requests, console errors, and page errors; run `qpdf --check`, `pdfinfo`, `pdftotext`, JavaScript absence, OCR, freshness, and exact-hash checks.
8. Inspect the cover, every image-bearing page, the densest page, the method/data page, and the final page at full size. Freeze the exact PDF, page renders, contact sheet, `SKILL.md`, and `agents/openai.yaml` hashes; then close the writer window.
9. Leave formal FINAL approval to a fresh independent reviewer. Any mutation after freeze invalidates that review identity.

## Image adaptation

For an owned monochrome source, run `scripts/tint_policy_image.py` with the locked palette. Use civic navy in shadows, choose teal or ochre as the role-specific midtone, and retain a warm paper highlight. The script refuses to overwrite existing outputs.

Do not use one image on multiple pages. Do not allow visible text, signs, labels, watermarks, fake statistics, logos, or political branding inside imagery.

## Hard stops

Stop for target collision, source-PDF overwrite, missing authority, paid/external asset requirement, private upload, destructive action, inability to prove artifact identity, or a need to modify the accepted source route or an installed global Skill.
