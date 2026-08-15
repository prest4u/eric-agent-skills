---
name: fusion-visual-system
description: Extract reusable visual DNA from inspected Figma frames, screenshots, documents, and open-source UI components, then translate it into an original, license-aware design system for HTML/PDF documents, websites, slides, or image prompts. Use when a user asks to reverse-engineer visual references, fuse multiple design references, adapt UI language into editorial documents, build a visual reference ledger, create cross-medium design tokens, or avoid template cloning while preserving useful design principles.
---

# Fusion Visual System

## Core rule

Extract observable rules, not protected identity. Preserve hierarchy, grid, rhythm, lighting, material, density, and interaction logic; remove source copy, logos, brands, proprietary imagery, named artists, distinctive illustrations, and complete page compositions. Fusion is not a copyright safe harbor.

## Checkpoint

Before building, lock:

- Actual references: inspect every supplied image/frame; inspect the repository and license for every code source.
- Target: document/PDF, web, slides, or image prompt.
- Output: exact new source, artifact, ledger, and QA paths; never overwrite a source artifact.
- Rights: record author, URL/path, license, attribution, asset-level exceptions, and allowed use.
- Originality: name at least five transformations and the source-specific elements that will be excluded.

If a visual reference cannot be opened, do not claim to have extracted its style. If a license cannot be verified, use the item only as a discovery lead and adopt none of its code or assets.

## Workflow

1. **Inventory references.** Create `reference-ledger.md` from `assets/reference-ledger.template.md`. Separate user-owned, permissively licensed, CC-licensed, and unverified sources.
2. **Decode visual DNA.** Read [visual-dna-schema.md](references/visual-dna-schema.md). Inspect the references and record all 15 visual dimensions plus document-specific hierarchy, pagination, data-visualization, and accessibility rules in `fusion-brief.json`.
3. **Generalize.** Read [license-and-originality.md](references/license-and-originality.md). Convert identity into observable primitives; remove brands, readable source text, original imagery, artist/studio names, named characters, exact locations, and signature page compositions.
4. **Tokenize.** Create semantic color, typography, spacing, geometry, border, shadow, image, chart, and motion tokens. Extend project-native tokens instead of replacing them.
5. **Compose.** Map reference patterns to the target medium. For documents, translate cards into information bands, side notes, comparison fields, or evidence matrices; translate hover and motion into static hierarchy.
6. **Adapt.** Read only the target section of [medium-adapters.md](references/medium-adapters.md). Keep HTML/PDF builds local and deterministic. Treat Figma MCP, ECharts, and Mermaid as optional accelerators, not required services.
7. **Validate.** Run `scripts/validate_fusion_bundle.py` against the project manifest. Fix P0/P1 issues, then perform a visual review of cover, first body, dense, and final pages. Machine checks never certify originality or visual quality.

## Minimum bundle

Require:

- `fusion-manifest.json`
- `fusion-brief.json`
- semantic token CSS
- source HTML/CSS or the target-native equivalent
- `reference-ledger.md`
- `THIRD_PARTY_NOTICES.md`
- rendered artifact and representative page renders
- a visual-review sentinel containing `FINAL_VISUAL_REVIEW: PASS`

Validate with:

```bash
python3 <skill-dir>/scripts/validate_fusion_bundle.py <bundle-root> \
  --manifest fusion-manifest.json \
  --out-dir qa/fusion-validation \
  --strict
```

Use `--no-write` for a read-only preflight. The validator writes only inside the declared bundle root and rejects absolute or escaping manifest paths.

## Acceptance

- Every adopted source has a verified right or is user-owned.
- Public output contains no source logos, copied copy, external runtime URLs, local absolute paths, or process language.
- Visual DNA contains all required dimensions and at least five concrete transformations.
- Document CSS declares A4 print behavior and uses semantic tokens.
- PDF page size, text extraction, renders, and visual-review sentinel pass.
- License notices remain with vendored code or icons.
- Final reporting distinguishes machine validation from human visual/originality judgment.

## Failure handling

- Missing reference image: stop visual extraction and request the actual image/frame.
- Unknown license: exclude code/assets and mark the source `unverified`.
- Generic output: re-decode composition, type, material, density, spatial rhythm, and signature traits.
- Clone-like output: change structure, proportion, typography, palette, assets, and content grouping before rendering again.
- PDF build without fresh renders: do not deliver; rebuild and inspect representative pages.
