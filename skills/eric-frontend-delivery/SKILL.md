---
name: eric-frontend-delivery
description: Create, prototype, repair, run, and check real frontend product surfaces such as web apps, tools, dashboards, routes, components, and interactive HTML. Use when responsive layout, states, interaction, accessibility basics, resources, runtime behavior, or visual finish matters. Do not use for backend-only, infrastructure-only, content-only, non-visual code review, unrendered data analysis, PDFs, or generic visual art.
---

# Eric Frontend Delivery

Own the working interface and its current runtime evidence. Do not create a second maturity, writer/reviewer, scoring, or verdict control plane. `$adaptive-quality-loop` supplies BUILD/PROOF/RELEASE timing; `$eric-review` owns an explicitly requested review.

## BUILD: default

1. Resolve the project root, requested product surface, primary user outcome, existing stack, and safe local runtime from the request and workspace. Ask only when competing targets or product choices would materially change the result.
2. Reuse project-native components, tokens, state patterns, scripts, fonts, icons, and assets. Add no dependency or broad abstraction without current evidence that it is needed.
3. Build or repair the visible primary flow first. Implement the default and the loading, empty, validation, error, retry, success, menu, dialog, keyboard, focus, and responsive states that actually affect that flow.
4. Run one combined check that can falsify the request: the relevant project-native build/test plus current loopback runtime/render inspection. When responsive behavior is part of acceptance, include the required desktop and mobile views in that same pass.
5. The same agent may fix ordinary findings and rerun the affected check. Deliver the working surface, exact identity/evidence, and genuine gaps without a persistent packet or dimension score.

Do not replace an app, tool, workflow, or dashboard with a marketing wrapper. Preserve unrelated dirty work and configuration.

## PROOF: costly product direction

When a visual grammar, interaction model, or responsive strategy is materially uncertain, produce one representative route, component, or state. Run one proof check and show it before scaling. A proof needs no independent reviewer.

## RELEASE: deployment or formal external delivery

For deployment, public/client delivery, security/privacy-sensitive behavior, destructive replacement, or explicit sign-off:

1. Confirm external authority and recovery, then freeze the exact source/build identity.
2. Run the mandatory project-native checks and inspect the release-critical journey in the required current states/viewports.
3. Stop mutation and use at most one independent `$eric-review` when formal sign-off is required.
4. Keep sign-off separate from deploy, publish, upload, send, migration, or account authority.

## Runtime evidence

Read [runtime evidence](references/runtime-evidence.md) when the acceptance criterion depends on a browser/runtime. Source, unit tests, and screenshot hashes do not substitute for visible runtime evidence. Inspect the changed impact surface and adjacent boundaries; do not expand to every route/state unless the delivery contract actually requires it.

Use [product lenses](references/product-profile-lenses.md) only when a lens helps the requested product outcome. It is not a rating system.

## Pinned engineering references

When the implementation uses React, read `references/upstream/vercel-react-best-practices/SKILL.md` and load only the referenced rule files needed for the affected surface. When component APIs or boolean-prop sprawl are the problem, also read `references/upstream/vercel-composition-patterns/SKILL.md`. These references inform implementation; this Skill still owns delivery scope, runtime evidence, and release boundaries.

Do not fetch newer instructions during a product task. The canonical hub updates these snapshots through a reviewed lock-file PR.

## Failure loop

Preserve the failing command, route/state, and visible observation. Make one targeted repair and rerun the same check. If it repeats, gather new evidence before a second repair. If the second repair repeats the failure, change approach or return the concrete blocker. Never weaken a test or baseline merely to pass.

## Agent budget and delivery

Use the main agent by default. At most one child agent may own a genuinely independent, bounded task; ordinary visual inspection never requires one.

Report the changed files/surface, exact build/runtime identity, applicable command and exit, inspected route/state/viewport, unexercised external permissions, and remaining gaps.
