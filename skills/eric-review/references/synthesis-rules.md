# Synthesis Rules

Use evidence, not report length or vote count.

- Merge duplicate findings and keep the strongest concrete locator.
- Separate observed defects from missing evidence and inferred concerns.
- P0/P1 blocks readiness; P2/P3 is follow-up unless the acceptance criterion says otherwise.
- A source/test pass does not imply a render, browser, playback, or package pass.
- Missing mandatory FORMAL_SIGNOFF evidence yields `INSUFFICIENT EVIDENCE`; missing independent provenance yields `PENDING INDEPENDENT REVIEW` only after other mandatory gates pass.
- Preserve material source conflicts and state what would resolve them.
- Never invent findings, severities, or certainty to fill a template.

QUICK_REVIEW and REVIEW_AND_FIX end with a concise plain-language decision. FORMAL_SIGNOFF uses the verdicts in `SKILL.md` and names the frozen identity, mandatory evidence, reviewer provenance, blockers, and unverified surface.
