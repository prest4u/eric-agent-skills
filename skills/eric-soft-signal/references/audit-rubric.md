# Audit rubric

Use this rubric only for formal RELEASE sign-off. The reviewer remains read-only and names the exact frozen source/PDF identity before reviewing.

## Hard-gate questions

- Does the source, PDF, audience, requested result, and authorized location agree?
- Is every required learning task present, accurate, and internally consistent?
- For beginner pronunciation, does every independently used or scored sound have prior student-visible articulation/auditory teaching, teacher modelling, and word practice, with untaught carriers excluded from visible IPA and scoring?
- Do blind listening tasks conceal their stimuli, resist answer-pattern guessing, and distinguish the actual stimulus from accepted oral-production variants?
- Is the artifact safe for its stated audience, with no answers, teacher notes, internal instructions, or local locations exposed to students?
- Does the current source freshly produce an A4 PDF with bundled fonts and resolvable imports?
- Does every 单项选择 / MCQ use `soft-question` four-box (exactly four choices), with no inline `A. … B. … C. …` run?
- Does every rendered page remain readable, nonblank, unclipped, connected to its writing surface, and free of a section title stranded at the page foot?
- Does the evidence identify commands, hashes, coverage, and reviewer provenance?

A failed hard gate prevents a positive final verdict.

## Record findings

Write one finding per defect. Include a page or source locator, observed condition, impact, severity, and the evidence needed to close it. Use P0 for unsafe, unusable, or identity-breaking defects; P1 for blocking learning, audience-safety, build, or render defects; P2 for material classroom or key-page impairment; P3 for minor polish.

## Decide the verdict

Return only `READY`, `NOT READY`, or `INSUFFICIENT EVIDENCE`, followed by blocking findings and material risks. `READY` requires every hard gate to pass, no open P0/P1, no unaccepted P2 on a key page, complete current render coverage, and a fresh reviewer who did not modify the frozen identity. Any later edit invalidates the verdict.
