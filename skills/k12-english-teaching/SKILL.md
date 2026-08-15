---
name: k12-english-teaching
description: Design K12 English lessons, units, courses, teaching diagnoses, remediation, and answerable practice. Use for natural requests to create or redesign school-age English instruction even when the user does not name this Skill; proceed with embedded diagnosis when level, weakness, or materials are unknown but a stage or goal and usable time are known. Use Eric Soft Signal for the document surface and active specialists only when their domain is actually required.
---

# K12 English Teaching

## Route before building

Choose the content owner from the request, not from the file type.

| Request | Owner |
|---|---|
| New lesson, unit, course, teaching diagnosis, remediation, or practice content | Keep `k12-english-teaching`. |
| Language polish or de-AI editing of already-written teaching content only | Route to `eric-teaching-polish`. |
| Parent feedback | Route to `eric-parent-feedback`. |
| Scheduling, exam-paper system, or another archived specialist domain | Produce the bounded result directly; activate an archived specialist only when Eric explicitly requests it. |
| Vocabulary handbook, cards, or workbook | Use `eric-soft-signal` as document owner and `eric-pdf-vocabulary` for vocabulary-specific structure when needed. |
| PDF requested by the user | Keep teaching content here and use `eric-soft-signal` for the document/PDF surface. Use generic `pdf` only for narrow file operations. |

Split genuinely mixed requests between owners. Do not expand K12 ownership merely because the material is English.

## Default to a visible teaching product

Ask at most one smallest question only when the answer changes product identity, learner safety, or feasible time. Otherwise make the narrowest safe assumption explicit and proceed.

When the usable time and at least one of the stage or goal are known, do not stop for missing current level, weak point, or source material. Start the artifact with an embedded diagnostic, provide result-based branches, or use clearly labeled `original practice`. Do not return only an intake form, `DIAGNOSTIC-ONLY`, or a pending status when a useful bounded artifact is feasible.

Produce the requested visible artifact first. Internally scale a single lesson, unit, or course to the real time available; do not require the user to complete a structured protocol.

## Build the minimum teaching contract

1. Lock one scoring or performance bottleneck and one observable signal, such as accuracy, response time, evidence location, retention, sentence control, or independent transfer. Use an opening task to choose the bottleneck when evidence is missing. Do not promise a score, ranking, or admission result.
2. Fit a runnable sequence to the stated time. Preserve diagnosis, focused teaching, guided practice, independent output, feedback, and a next task; cut optional extensions before compressing required student work invisibly.
3. Supply every passage, prompt, option, example, or taught mechanism needed to answer each exercise. Do not merely describe practice.
4. Use the minimum necessary, authorized learner information. Anonymize by default; do not inspect unrelated student files or infer private traits.

Read [Formal Teaching Contract](references/formal-teaching-contract.md) only for a formal lesson, multi-lesson sequence, course capacity, or differentiated paths.

## Protect student and source surfaces

Read [Student and Source Contract](references/student-source-contract.md) when creating exercises, paired student/teacher editions, or official, real-exam, current, or latest source claims.

- Keep student and teacher tasks in the same order with the same wording and inputs.
- Keep answers, explanations, common errors, repair moves, teacher strategy, and internal labels off the student surface.
- Use `official`, `real exam`, `past paper`, `current`, or `latest` only when a reliable source directly supports the exact claim and locator.
- If a requested source cannot be verified, ask for the source or relabel the material `original practice`; continue every part that does not depend on the unverified claim. Never invent provenance.
- Respect copyright and use only authorized supplied materials.

## Stop at the requested result

- For a lesson plan, sample, exercise, or classroom draft, deliver the visible product directly after one teaching/document check; same-agent repair is sufficient.
- For material not yet being distributed, check only the changed teaching surface and adjacent student/source boundaries.
- Only when the exact material is about to be formally handed to students, published, or explicitly signed off, freeze its identity and run at most one fresh independent review.
- Use `eric-soft-signal` for teaching-document output. Do not trigger formal visual review for an ordinary classroom draft.

Do not send, publish, install, or mutate external systems without separate authority. For package maintenance only, run the project tests; ordinary teaching tasks must not run them.
