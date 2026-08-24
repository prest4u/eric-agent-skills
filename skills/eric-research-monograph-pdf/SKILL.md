---
name: eric-research-monograph-pdf
description: 创建专业彩色、适合打印且以证据为核心的 A4 研究专著 PDF，包含可检索文本、明确语料、主张与来源追踪、综合协议、研究限制、独立图像、溯源记录和逐页质检。用于研究报告、文献综述、证据综合与方法专著，不用于幻灯片或普通咨询简报。
---

# Eric Research Monograph PDF

## Core contract

Create an evidence-led academic document whose authority comes from traceable claims, explicit limits, and restrained editorial production. Read [visual-production-grammar.md](references/visual-production-grammar.md) before building or adapting a monograph.

## Workflow

1. Lock the audience, research question, authoritative corpus, exclusions, output identity, page count, and overwrite policy.
2. Map content into proposition, corpus, claim-source trace, synthesis method, conclusion, limitation, and next-evidence roles. Preserve an accepted route when the request is an adaptation.
3. Build deterministic searchable text. Use figures only for observable documentary or material relationships, never as containers for research body text.
4. Use ink-dominant academic colour: one dark-indigo primary, one cool-grey secondary, and one muted signal. Pair every colour distinction with a written status, identifier, line style, or position.
5. Register every image with source or generation, prompt or deterministic transform, page role, dimensions, no-text policy, unique use, and hash.
6. Export a new derivative PDF. Render every page from the PDF and create a contact sheet after the PDF is final.
7. Run browser geometry/runtime checks and PDF structural checks. Use `scripts/inspect_monograph_pdf.py` for the reusable PDF gate, then inspect the required pages at full size.
8. Freeze exact PDF, render, contact-sheet, source, provenance, QA, and Skill hashes. Do not self-approve FINAL; leave the frozen identity for an independent reviewer.

## Hard boundaries

- Do not invent sources, evidence status, findings, quotations, citations, or external validity.
- Do not let colour imply an evidence grade that is not also stated in words.
- Do not reuse an image across pages or use visible text, fake labels, logos, or watermarks in generated imagery.
- Do not rasterize text-heavy pages, overwrite the source PDF, upload private files, or publish without explicit authority.
- Do not turn the monograph into a consulting journey, policy dossier, dashboard, card wall, or repeated table shell.
- Stop after one bounded repair if the same failure fingerprint repeats.

## Completion evidence

Report the new PDF and source paths, page count and A4 evidence, searchable-text and JavaScript status, fresh PDF-origin renders/contact sheet, browser/runtime audit, asset provenance and unique-use check, full-size pages inspected, exact frozen hashes, and unresolved risks. A same-agent inspection may support candidate readiness but cannot confer FINAL approval.
