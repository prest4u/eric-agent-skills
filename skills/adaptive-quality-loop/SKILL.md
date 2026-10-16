---
name: adaptive-quality-loop
description: Use only when Eric explicitly requests Adaptive Quality Loop or this problem-solving reference. Choose a method for a consequential uncertainty, evidence gap, or repeated failure. Ordinary builds, design tasks, reviews, advice, and status checks do not automatically invoke this Skill.
---

# Adaptive Quality Loop

This is an opt-in reference for a specific unresolved problem. Host and task policy governs authorization, verification, independent review, and completion. Selecting this Skill supplies methods; it does not introduce another workflow or require another Skill.

## Choose a useful method

Read only the reference that addresses the actual problem. Do not classify every task, create a stage tracker, or run the whole table.

| Problem | Smallest useful next step | Reference |
| --- | --- | --- |
| A consequential assumption could invalidate costly work | Inspect available facts, then make a representative reversible proof | [Uncertainty](references/alignment-gate.md) |
| It is unclear what evidence is enough | Identify the acceptance claim and the risk that could falsify it | [Impact](references/risk-model.md) |
| A repair repeats the same failure | Gather diagnostic evidence and change the hypothesis or method | [Repair](references/failure-loop.md) |
| The artifact needs domain-specific evidence | Select the relevant runtime, rendered, calculation, or source observation | [Evidence](references/routing-matrix.md) |
| An independent specialist is actually needed | Hand off one bounded question with the current candidate and evidence | [Handoff](references/specialist-handoffs.md) |
| A formal machine-readable release record is explicitly required | Record existing authority, recovery, checks, and independent review | [Optional record](references/evidence-contract.md) |

## Use evidence proportionately

Produce or preserve the requested working artifact. Collect the smallest sufficient evidence set for its actual acceptance criteria; each check covers a distinct requirement or known risk. Reuse trustworthy current evidence. Source inspection does not replace required runtime, render, browser, or playback evidence.

Resolve reversible details independently. Ask only when a choice materially changes the result, cost, scope, irreversibility, or authority. Existing user delegation remains valid within its scope. A proof does not by itself require a contract, approval, packet, or independent reviewer.

After a repeated failure without new information, change the diagnosis or method. If a real dependency prevents progress, return the completed work and concrete blocker. Do not create JSON fingerprints, attempt ledgers, or approval ceremonies for ordinary repairs.

## Review and completion

Use one main agent by default; delegate only independently useful work or required review. Apply the host's risk-based review boundary. Required review covers the affected stable candidate, and is separate from publish, send, deploy, migration, or other execution authority.

After a required review stalls, allow one recovery or fresh replacement for the bounded question. If it still cannot conclude, return the local candidate, completed evidence, and pending review while keeping dependent release or high-impact actions blocked. Missing review is never approval. Resume only for new evidence, a material candidate change, or restored review capability.

Finish on sufficient acceptance evidence. Optional polish does not create another round.

## Compatibility

The labels `BUILD`, `PROOF`, and `RELEASE` remain understandable in existing records: local work, a representative proof, and a protected delivery boundary. They are not mandatory task stages. Earlier reference filenames remain valid links.

Use `scripts/validate_quality_packet.py` only when an explicit formal release record is required. Its current `schema_version: 1`, `mode: RELEASE` interface is unchanged. A structurally valid record does not prove correctness, reviewer independence, or external authority. Ordinary work does not create this record.
