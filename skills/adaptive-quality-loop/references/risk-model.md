# Risk model

Risk changes validation intensity, never the need for final evidence.

| Tier | Typical scope | Required evidence | Review |
|---|---|---|---|
| Q0 MICRO | Internal wording, typo, non-contract rename | Exact target inspection, surgical edit, one proportionate check; no persistent QA files | Same-agent sanity check |
| Q1 STANDARD | Local reversible feature, fix, refactor, routine artifact | Acceptance before edit; failing test/fixture for behavior; targeted gate; relevant suite | Same-agent verification |
| Q2 HIGH | Multi-file or cross-module; decision-facing analysis; public/student/customer or rendered artifact; weak tests | Written packet; positive/negative evidence; domain runtime/render/source and package gates; bounded repair | Independent review for formal delivery or same-agent subjective work |
| Q3 CRITICAL | Auth/secrets/privacy, destructive action, migration, deploy/publish/upload, regulated/material external claims | Q2 plus explicit authority, rollback/recovery, security/source route, fresh evidence | Independent reviewer or Eric; no same-agent sign-off |

## Mandatory escalation

- Credential, secret, auth/authorization, payment, private record, or personal data: Q3.
- Migration, destructive filesystem work, deployment, publishing, upload, or external mutation: Q3 plus explicit authority.
- Material financial, legal, medical, regulatory, market, or current API claim: Q3 if externally shared; otherwise at least Q2.
- Delivery-bound PDF, slide, video, UI, teaching package, or public content: at least Q2.
- Stakeholder decision analysis: at least Q2.
- Missing tests, unfamiliar validator, broad dirty tree, ambiguous identity, or conflicting requirements: raise one tier or block the affected gate.
- Repeated failure fingerprint: switch from repair to diagnosis; repeated unknowns may raise one tier.
- Formal sign-off: independent provenance regardless of tier.

## Downshift

Lower risk only when concrete evidence removes the signal: prove the change non-behavioral, remove external action, exclude sensitive paths, or narrow impact through authoritative requirements. Convenience, deadline, confidence, and unrelated passing tests never downshift risk.
