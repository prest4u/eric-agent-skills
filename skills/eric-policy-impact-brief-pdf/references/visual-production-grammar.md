# Policy Impact Brief Visual and Production Grammar

Use this reference when adapting the six-page route or building a sibling brief from equivalent content.

## Page sequence

1. Decision condition: title, public-space image, stakeholder access, accountable hand-off.
2. Decision frame: intervention, affected groups, decision use, owner.
3. Mechanism and evidence: intervention → mechanism → outcome → evidence, including baseline and counterfactual.
4. Evidence loop: decision result → baseline → mechanism → implementation → pilot/control → assessment → learning.
5. Decision artifacts: definition, evidence design, implementation responsibility, decision record.
6. Accountability close: uncertainty, four decision implications, accountable-owner chain, operating boundaries.

Keep these roles explicit. Change the sequence only when the source decision process requires a different causal order.

## Colour grammar

- Primary civic navy: institutional structure, route rails, major rules, reversed close.
- Secondary teal: evidence, affected groups, monitoring, iterative learning.
- Signal ochre: decision points, counterfactual attention, implementation hand-offs.
- Keep paper, ink, and neutral rules dominant. Use colour as a sparse classifier, never as decoration or the only carrier of meaning.
- Require text labels, numbering, rule position, or line style to duplicate every colour distinction.
- For print safety, keep body text dark and maintain at least 4.5:1 contrast for normal text.

## Image grammar

Use anonymous public-space or civic-infrastructure images with no visible text. Give every image one page role and one semantic mapping:

- access and ownership on the cover;
- mechanism and dependencies on the causal-chain page;
- responsibility, transfer, and monitoring on the artifact page.

Do not reuse an image across pages. Record source or generation, prompt or deterministic transform, input/output hashes, dimensions, page role, semantic mapping, and no-visible-text policy.

For an owned monochrome source, use `scripts/tint_policy_image.py` to apply a deterministic three-stop grade. Keep the route palette fixed; vary only the role-specific midtone emphasis.

## Production boundary

- Keep all substantive text in HTML/CSS so the PDF remains searchable.
- Build a new derivative; never overwrite the source PDF.
- Use A4 portrait with fixed page boxes and no accidental pagination.
- Render every PDF page to a fresh PNG and regenerate the contact sheet after the final PDF.
- Run browser layout checks, `qpdf --check`, `pdfinfo`, `pdftotext`, image OCR, render freshness, and exact-hash freeze.
- Leave formal FINAL review pending for a fresh independent reviewer after the writer window closes.
