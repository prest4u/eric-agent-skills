# Alignment Gate

Use this reference only after the main Skill selects `ALIGN_FOCUSED` or `ALIGN_DISCOVERY`. Its job is to prevent two opposite failures: producing the wrong thing with excellent execution, and repeatedly interviewing Eric about work whose contract is already settled.

Alignment route is orthogonal to risk. A familiar public deliverable can be `ALIGN_DIRECT + Q2`; a novel but reversible internal experiment can be `ALIGN_DISCOVERY + Q1`.

## Inspect before asking

Read the narrowest current project evidence that can answer the question. Prefer, in order:

1. Eric's current explicit instruction;
2. the current project's canonical start/status/brief/spec/SOP/manifest;
3. linked approved examples, proofs, tests, and QA evidence;
4. relevant primary sources.

Current workspace evidence overrides stale memory, summaries, plans, or earlier assumptions. Treat memory only as a locator. If sources disagree, expose the conflict instead of silently choosing the most convenient version.

Do not ask Eric for a fact that is discoverable in the authorized workspace. Questions are for decisions, not file retrieval.

## Six alignment anchors

Before choosing a route, assess whether these anchors are locked:

- **Outcome:** the real change the work should produce, not merely an output noun;
- **Audience and use:** who will use it, in what situation, and what they must be able to do;
- **Deliverable:** exact artifact, scale, format, boundaries, and current identity;
- **Authority:** ordered sources of truth and the rule for resolving conflicts;
- **Acceptance:** observable evidence that would count as success;
- **Wrong product:** plausible polished outcomes that must still be rejected, plus explicit non-goals.

## Choose one route

### `ALIGN_DIRECT`

Choose Direct only when all six anchors are already settled by current evidence: an approved SOP/spec/brief and reference identity exist; the audience, use, artifact, scope, source priority, wrong-product boundary, and acceptance evidence are known; and no material conflict or decision remains.

Silently lock the contract in working context, cite the authority when useful, and proceed to RED or implementation. Ask zero alignment questions. Do not create a new alignment document or duplicate an existing brief.

If current evidence is missing, contradictory, or leaves a choice that would materially change the result, Direct is not available.

### `ALIGN_FOCUSED`

Choose Focused when the direction and canon are settled and only one to three local decisions can still change the result.

1. Inspect workspace facts first.
2. Name the contract field the decision closes.
3. Ask dependent questions one at a time. Independent questions may be grouped, never more than three in one turn.
4. Every question must include a concrete recommendation, the reason for it, and the meaningful cost or tradeoff.
5. Do not implement a branch controlled by an unresolved material decision. Stop questioning when each decision is resolved or explicitly delegated.
6. After the last answer, give a one-sentence delta-lock stating what changed and proceed automatically. Do not add a second formal confirmation ritual.

Escalate to Discovery if the unresolved choices become a branching, mutually dependent system; more than three material decisions remain; there is no accepted canon; or the choice controls a high-rework batch direction.

### `ALIGN_DISCOVERY`

Choose Discovery when any core anchor is unknown, when multiple reasonable interpretations would create substantially different products, when audience or product form is new, when authority conflicts remain, when Eric explicitly requests a stress-test/grill, or when a high-rework batch lacks an accepted proof.

Discovery has two hard approval gates:

1. **Contract gate:** before Eric confirms the current Alignment Contract identity, perform only read-only inspection, analysis, and alignment conversation. Do not edit files, scaffold, install, build, or generate delivery artifacts. A confirmation does not open the gate while an unresolved material decision still controls the proof.
2. **Proof gate:** after contract confirmation, persist the contract in its canonical home and create only the current representative proof. Do not produce the full set, batch, rollout, or final delivery until Eric confirms the current proof identity.

An instruction such as “直接做” does not bypass a material ambiguity. “你决定” is an explicit delegation: record the chosen option, recommendation, reasoning, and risk in the contract, then continue within the route's current gate.

Before presenting a Discovery contract that resolves delegated material choices, include a delegated-choice record for each material choice or coherent choice set: selected option, recommendation rationale, meaningful tradeoff, and risk. Merely labeling fields “delegated” is insufficient.

If Eric cannot yet choose, offer a small **alignment probe** only when it would reveal the decision. Label it `disposable`, `non-delivery`, and `no-scale`. A probe cannot be renamed into the representative proof; once it resolves the choice, re-lock the contract first.

## Asking useful questions

A good alignment question:

- changes a named outcome, audience, product, authority, boundary, or acceptance field;
- is grounded in inspected evidence and names the concrete artifact or boundary affected;
- recommends one option and explains both why it is preferred and what it gives up;
- separates facts from judgment;
- does not ask for implementation details the owning Skill can decide safely;
- ends when the decision is answered or delegated.

Do not ask a generic questionnaire. Do not front-load hypothetical decisions that only become relevant after an earlier choice.

## Alignment Contract

On the first Discovery response, present a compact current contract draft before asking the first material question. Fill known fields, mark unknown fields open, and include the three wrong-product tests even when the draft is incomplete; do not replace the draft with only a question or plan to draft later. The execution-ready contract must contain:

- audience, use context, and intended real-world outcome;
- exact deliverable, scale, format, boundaries, and identity;
- authoritative sources in order and a conflict-resolution rule;
- must-haves and explicit non-goals;
- resolved, delegated, and still-open decisions;
- for delegated material decisions, the selected option, recommendation rationale, tradeoff, and risk;
- at least three wrong-product tests:
  - polished work for the wrong audience, job, or task;
  - the wrong artifact form, experience, or format;
  - machine checks pass but the real outcome is not achieved;
- observable acceptance evidence;
- representative proof content, identity method, and approval point;
- permissions, scope, and a one-sentence playback of what will be built.

Eric's approval must refer to the current contract, not a superseded summary. Record a minimal locator and stable identity such as a content hash or version; do not store unnecessary private conversation text.

After approval, write the contract into the project's existing single source of truth. Do not create `CONTEXT.md`, an ADR, or a parallel status system by default. If no suitable authority exists and the work spans sessions, agents, or a batch, create one project brief that follows the repository's naming convention. Use an ADR only when the project already uses ADRs and the decision is hard to reverse, surprising, and genuinely contested.

## Representative proof

Choose the smallest complete slice that exposes the most expensive intent risk. The proof is not automatically the first page, the cheapest component, or an isolated visual mockup.

- **Code/UI:** one real public seam as an end-to-end vertical slice, plus the highest-cost boundary state.
- **Skill:** a pre-change RED case, an intended GREEN trigger, a non-trigger, and an ambiguous or adversarial route.
- **PDF:** a coherent mini-section containing title/cover behavior, ordinary body, the densest or writable page, and any special teacher/student page role; inspect both contact sheet and full-size PNG.
- **Course:** one typical-but-hard complete lesson with the student artifact and complete teacher master.
- **Video:** after storyboard approval, one continuous high-risk segment covering hook, transition, core explanation, captions, sound, and motion coupling.
- **Long-form/book:** reader promise, structure map, one complete representative chapter, and its adjacent transition.

State how the proof identity will be captured. Eric's proof approval must bind to the current identity. If the final artifact is itself the smallest meaningful slice, its first complete build is the proof; it still requires proof confirmation before it is labeled final delivery or copied into a larger series.

## Staleness and failure semantics

Any change to goal, audience, canon, deliverable form, material boundary, or contract identity invalidates the old contract approval and proof approval. Re-enter alignment at the smallest route that can resolve the change.

Feedback that changes what should be built is an alignment revision and does not consume the implementation repair budget. If the contract remains unchanged and the implementation fails it, use the existing failure loop.

Rejecting a proof stops scale immediately. Update the contract if the rejection reveals an intent change, produce a new proof identity, and obtain a new proof confirmation. Never reuse approval from an older identity.

## Quality packet mapping

Do not change the current packet schema for this behavior. For Q2/Q3 work, express alignment with existing fields:

- `ALIGN-OUTCOME-*` acceptance entries define the real result;
- `ALIGN-WRONG-PRODUCT-*` acceptance entries define plausible but unacceptable products;
- `G-ALIGNMENT-CONTRACT-APPROVED` records the confirmed contract locator, identity, and Eric approval;
- `G-REPRESENTATIVE-PROOF-ACCEPTED` records the current proof locator, identity, and Eric approval.

Schema structure alone cannot prove semantic understanding. Use fresh-context forward tests to verify route choice, question quality, write/build timing, stale-approval handling, and no-scale behavior.

## Method provenance

This gate uses original wording and a Codex-native implementation. Its requirements-discovery approach was informed by Matt Pocock's MIT-licensed [`mattpocock/skills`](https://github.com/mattpocock/skills) repository at commit `391a2701dd948f94f56a39f7533f8eea9a859c87`, especially the `grilling`, `grill-with-docs`, and `domain-modeling` Skill files. No third-party Skill is installed or forked, and no substantial source wording is copied.
