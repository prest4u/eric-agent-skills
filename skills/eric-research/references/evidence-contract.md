# Evidence Contract

Use one internal source-assessment vocabulary across every domain, but scale the record to the decision and risk. The labels below support analysis and explicitly requested structured records. Ordinary replies use the visible-writing rules in SKILL.md: explain the actual source, date, result or missing fact in prose, with citations; do not copy internal labels into headings.

## Evidence Depth

| Depth | Use when | Required record |
|---|---|---|
| Quick | One or two low-risk claims; a short factual answer | Conclusion, supporting source link, and any material caveat or conflict; assess source quality without displaying a metadata form. |
| Standard | Several claims, comparison, citation audit, or a recommendation | Explain material claims with supporting sources and limitations; use a compact comparison table when it aids the decision. |
| Decision / high-risk | Financial, legal, policy, safety, reputation, current public-figure, or consequential business/education decision | Standard fields plus domain context, exact evidence locator, method/applicability, and explicit unverified alternatives. |

Do not create a giant ledger for a simple question. Do not omit a material caveat merely to keep the answer short.

## Source Ranks

| Rank | Meaning | Allowed use |
|---|---|---|
| `S1` | Official or primary: government, regulator, filing/IR, original paper/data/interview/post, or direct evidence | Support directly entailed claims within the source's scope. |
| `S2` | Reliable secondary with an inspectable source trail | Cross-check or support when S1 is absent and the domain permits it. |
| `S3` | Lead or interested-party evidence: vendor market claims, social posts, forums, testimonials, anonymous reports | Use as a lead or explicitly bounded signal, not independent proof. |
| `S4` | Non-evidence: snippet, AI summary, unsourced aggregator, citation list, uninspected URL | Discover sources only. |

An official vendor page is S1 only for what that vendor says about itself, not for market demand, efficacy, uniqueness, or category leadership.

## Evidence Status

- `verified`: directly supported by suitable S1 evidence, or by multiple independent S2 sources where the domain permits, with no unresolved higher-quality conflict.
- `supported_with_caveat`: supported but bounded by date, geography, sample, method, metric, applicability, or source scope.
- `needs_cross_check`: plausible but depends on one source, weak independence, or missing primary confirmation.
- `conflicting`: credible sources disagree at the same time and scope.
- `unsupported`: searched or inspected allowed evidence and found no adequate support.
- `unverifiable`: required evidence is unavailable, inaccessible, private, prohibited, or not published.

When currentness or another requested check was not performed, say exactly what was not checked in the reader’s language. Keep `Not checked` only when the user requested that status field. Do not imply that the check passed.

## Standard Claim Fields

For an explicitly requested evidence ledger or a decision/high-risk record that needs structured traceability, the following fields are available. Ordinary standard answers may express the same relevant information in prose; do not force an eleven-column table:

`claim_id | claim | domain | source | source_rank | evidence_status | confidence | published_or_updated | accessed_at | conflict_or_caveat | action`

Keep exact evidence locators and relevant domain context for consequential claims. Preserve an explicitly requested schema; otherwise include only fields that help assess the decision. Do not invent numerical confidence or hide material claims to fit a record. Dates use the user's timezone when material; record `not found` rather than inventing a publication date.

## Verification Rules

- A source must support the exact claim, not merely discuss the topic.
- Separate observed fact from implication. An implication cannot be more certain than its supporting facts.
- Preserve each side of a credible conflict and name what would resolve it. Later evidence may resolve a conflict by time or scope; it does not erase the earlier state.
- For current claims, browse current sources when allowed and record access dates. Compare publication/update dates before saying `latest` or `current`.
- Under supplied-source-only or no-web constraints, distinguish historical evidence from current claims and label currentness `Not checked`.
- Treat repeated coverage derived from one origin as one evidence chain, not independent corroboration.

## Opt-In Research Log

Persist only when Eric explicitly asks to save a research log. Confirm or use his supplied path; do not choose a personal absolute path. Create a new file rather than overwrite an existing log unless he explicitly requests an update. Save only necessary paraphrases, links, dates, statuses, conflicts, and next checks; exclude secrets, account data, private raw text, and long copyrighted passages. Verify the file exists after writing. If persistence fails, return the findings in chat and state that the log was not saved.
