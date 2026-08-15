---
name: adaptive-quality-loop
description: Use for durable implementation, multi-file changes, formal validation, release preparation, or another task where Codex must build an artifact and verify it. Default to BUILD; use PROOF only for costly ambiguity and RELEASE only for high-impact or external delivery. Do not use for ordinary advice, explanations, status checks, or inspect-only questions.
---

# Adaptive Quality Loop

Build the requested thing before expanding the process. Quality work must protect the result, not compete with it.

## Choose one mode

| Mode | Trigger | Required workflow |
| --- | --- | --- |
| `BUILD` | Default for reversible local work | Produce the visible artifact, run one targeted check, deliver. |
| `PROOF` | A wrong direction would cause material rework or cost | State the decisive assumption, build the smallest reversible proof, run one proof check, deliver it. |
| `RELEASE` | Publish, formal external delivery, security/privacy, destructive action, migration, deployment, or explicit sign-off | Confirm authority and recovery, freeze identity, run applicable checks, obtain at most one independent review. |

Do not expose mode labels unless they help Eric understand a real tradeoff.

## BUILD

1. Inspect the target and current evidence.
2. Resolve reversible implementation details independently.
3. Create or modify the actual artifact.
4. Run the cheapest check that can falsify the current acceptance criterion.
5. Deliver the artifact, exact check evidence, and any genuine gap.

Do not create a quality packet, ask for routine approval, or dispatch a reviewer. Do not run several equivalent checks merely to increase confidence.

## PROOF

Use PROOF only when one unresolved assumption could invalidate a costly direction. Produce the smallest representative result immediately. Ask Eric before scaling only when the proof exposes a material product choice, expense, lock-in, irreversible action, or external impact. A delegated or locally reversible choice does not require a contract ceremony.

Do not create a persistent QA record or use an independent reviewer for a proof.

## RELEASE

Before the high-impact action:

1. Name the exact artifact or commit identity and intended external action.
2. Confirm current authority and a usable recovery method.
3. Run only the domain checks required by the delivery contract.
4. Stop mutation and obtain one fresh independent review of that frozen identity.
5. Keep publish, deploy, send, upload, migration, and destructive execution separate from sign-off authority.

Use `scripts/validate_quality_packet.py` only when an explicit formal release record is required. Ordinary BUILD and PROOF work must not create that record.

## Agent budget

Use one main agent by default. Use at most one child agent only when its deliverable is independent and bounded; give it minimal task-local context, never a full-history fork. Same-agent checking is sufficient outside RELEASE or explicit independent review.

## Failure loop

1. Preserve the concrete failing command, observation, or artifact state.
2. Make one targeted repair and rerun the same relevant check.
3. If the same failure remains, gather new diagnostic evidence before a second repair.
4. If the second repair leaves the same failure, change approach or return the concrete blocker.

Do not encode JSON fingerprints, create review-of-review chains, or ask Eric to approve another repair unless scope, cost, irreversibility, or authority changes.

## Done

Report the artifact identity, the one applicable check or release evidence, reviewer provenance when required, unrelated drift preserved, and any unverified surface. Never substitute a source check for required render, runtime, browser, or playback evidence.
