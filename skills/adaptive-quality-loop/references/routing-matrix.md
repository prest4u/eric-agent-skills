# Dynamic routing matrix

Route by artifact and decision, not generic words such as “check” or “quality”. Multiple routes may apply.

Resolve every specialist against the current runtime inventory. Plugin routes may exist on disk but remain unavailable to a runtime; cache presence alone is not execution evidence. Use the missing-specialist fallback in [specialist-handoffs.md](specialist-handoffs.md).

| Domain | Pre-build / incremental | Final evidence | Specialist | Build durable gate when |
|---|---|---|---|---|
| Code/UI | Behavior/interface contract; targeted tests | Suite, lint/type/build, runtime/E2E as applicable | security-review, e2e-testing, webapp-testing, project-native Skills | Regression recurs or release boundary lacks an executable contract |
| Data quality | Use, grain, keys, freshness, thresholds; profile/spot check | Nulls, duplicates, freshness, join coverage, reconciliation | data-analytics:analyze-data-quality | Schema/freshness/uniqueness expectation recurs |
| Analysis/report | Decision, sources/as-of, formulas/denominators/windows; recompute key metric | Method, calculations, visuals, claims, caveats, reproducibility | data-analytics:validate-data; visualize-data | Metric/report contract repeatedly fails |
| PDF/DOCX/slides | Reader, dimensions, identity, page roles; compile/target render | Current renders, leakage/accessibility, package usability | owning document Skill + eric-visual-delivery-review | Package/leak/page/freshness defect recurs |
| Video | Delivery spec/storyboard; lint/preview | Metadata, playback, frames/contact sheet, content/technical QA | video-qa, video-production-stack | Frame/audio/spec mismatch recurs |
| Skill/plugin | Trigger cases, RED baseline, negative routes; static/script test | RED/GREEN forward tests, adversarial cases, reference/metadata checks | `skill-creator`; `eric-review` | Bundle/script contract must be reusable |
| Teaching/research | Learner/source/claim contract; selected checks | Boundary/completeness/renders or claim ledger/conflicts/dates | teaching/PDF or eric-research + eric-review | Boundary, source, package, citation defect recurs |
| Release/external | Exact identity, approval, recovery, privacy; dry run only | All gates current; authority separately confirmed | eric-review | Add a project-native release gate |

## Precedence

1. Privacy, security, destructive, and external-mutation routes override convenience.
2. Raw data trust precedes analysis correctness; correctness precedes polish.
3. Source/compile/test never replaces render/runtime/playback inspection.
4. Use `building-validators` only after identifying a recurring or release-critical executable check; it never replaces domain review.
5. `eric-review` decides from evidence and cannot manufacture missing evidence.
