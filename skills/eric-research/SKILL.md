---
name: eric-research
description: 【研究路由】Use only when Eric explicitly invokes $eric-research to investigate, verify, compare, or synthesize claims across finance, education/academic, marketing, news/social/entertainment, or mixed evidence domains. Supports new public-source research and supplied-source-only review with evidence depth scaled to risk; does not trigger from ordinary research-like requests.
---

# Eric Research

## Visible writing

Apply this to newly authored reader-facing text and the task reply, including titles, notes and exported text. Do not use “边界” or “证据” in Chinese prose; describe the specific rule, source, observed result or limitation. Preserve citations and exact quoted source text, official names, code/schema fields and explicitly requested grammar examples. Quotation marks alone do not exempt newly generated prose.

Ban “不是……而是……”, “并非……而是……”, “不在于……而在于……”, “不是 X，是 Y” and stock English equivalents. Remove rhetorical parallelism, repeated sentence openings, slogan triplets, artificial crescendos and empty concluding uplift. Keep real task steps and useful comparisons. Write the point directly, with concrete facts and natural sentences; do not replace one abstract label with another or invent details to sound human.

Read the changed visible text once before delivery or rendering. Fix the offending sentences while preserving the requested format and facts. Internal method labels and reference examples do not override this rule. This check adds no extra artifact, Skill dependency, reviewer or approval step.

Keep source evaluation and factual qualifications. Express them with the actual source, date, finding or missing fact; internal research statuses are not mandatory reader-facing headings.

Turn a research question into a source-backed answer whose certainty matches the evidence. Keep one workflow across domains and load only the relevant domain reference.

## Set The Scope

1. Identify the decision or question, material claims, domain(s), time boundary, geography or jurisdiction, and source restrictions.
2. Ask at most one question only when the missing answer would materially change the evidence standard or result. Otherwise state a reasonable assumption.
3. Choose an evidence depth from [references/evidence-contract.md](references/evidence-contract.md): quick answer, standard verification, or decision/high-risk research.
4. Read every domain reference that covers a material claim:
   - Finance: [references/finance.md](references/finance.md)
   - Education or academic: [references/education-academic.md](references/education-academic.md)
   - Marketing: [references/marketing.md](references/marketing.md)
   - News, social, or entertainment: [references/news-social-entertainment.md](references/news-social-entertainment.md)
5. For mixed-domain work, split claims by domain, apply each delta, then synthesize once under the common evidence contract. Do not let evidence from one domain certify a claim in another.

## Spend effort on the unresolved claim

Use retrieval for missing facts, calculations for numerical claims, and deeper reasoning for competing explanations or tradeoffs. A short high-consequence claim still needs strong evidence; a long extraction task need not become open-ended research. Stop when the material question is answered at the required evidence standard and consequential gaps are explicit. Do not pad the source count, search adjacent topics, or create a formal record for an ordinary answer.

## Acquire Or Inspect

- If Eric supplied all allowed sources, inspect only those sources. Do not browse, invoke `$eric-reach`, or imply that currentness was checked. Label material current claims `Not checked`.
- If new internet material is needed, keep acquisition separate from judgment. Use `$eric-reach` as the acquisition layer when it is available; accept its retrieval packet without duplicating backend selection. If it is unavailable, use only host-provided read-only retrieval capabilities and report access limits.
- Do not invoke acquisition for local-only synthesis, citation audit, or source ranking over supplied material.
- Inspect the underlying source and a reproducible passage, table, figure, filing section, dataset row, or original post. Treat snippets, AI summaries, citation lists, and uninspected links as leads only.

## Verify And Synthesize

1. Separate factual claims, interpretations, estimates, recommendations, and unknowns.
2. Apply the source ranks, evidence statuses, conflict rules, dates, and scaled output fields in the common evidence contract.
3. Preserve inaccessible sources, missing dates, stale evidence, credible disagreement, and unverified items. Never fill a gap from memory.
4. Keep each conclusion no stronger than its weakest material supporting claim. Link recommendations to the evidence they depend on.
5. Return in chat by default. Create or update a research log only when Eric explicitly asks to save one; then use the opt-in persistence rules in the common evidence contract.

## Return

Answer the question directly. Put source links beside the claims they support. When a missing date, untested assumption or disagreement changes the conclusion, state that specific fact in ordinary language. Add a next action only when it helps resolve the user's question. Do not force four named sections or expose internal status codes; preserve a user-requested report schema.

Do not restore or invoke archived research specialist Skills. Do not provide personalized financial, medical, legal, or educational advice beyond the evidence.
