# Failure patterns

Do not replace the artifact, change the audience, weaken a gate, or broaden the changed surface to obtain a pass.

| Observed failure | Targeted response |
| --- | --- |
| Build or render fails | Preserve the exact command, exit, affected source/page, and visible error. Make one correction aimed at that evidence, then rerun the same check. |
| Raw underscore blank disappears or causes an unclosed delimiter | Preserve the exact source line and compiler evidence; replace only that run with `#soft-blank()` at the authoring call site, then recompile. |
| A parameter is reported positional or named incorrectly | Inspect the current public template signature and correct only the call site to match it. For the current `soft-passage-title`, pass label and title positionally; do not guess from an older call. |
| The first correction does not resolve the failure | Gather a new diagnostic observation before making one second bounded correction. Do not repeat the same edit or unchanged check. |
| The second correction does not resolve the failure | Change approach or report the concrete blocker, evidence, and affected output. Ask Eric only if the next route changes scope, cost, irreversibility, or external authority. |
| Choice mark is detached from A–D | Replace the local layout with `soft-question`; do not reposition the mark independently. |
| 单项选择 renders as inline A. B. C. instead of the 2×2 four-box | Replace the item with `#soft-question(stem:, choices: (a, b, c, d), ...)`. If the source had three options, add a plausible fourth distractor or recast; do not keep the run-on line. |
| Reflection heading, prompt, or writing lines split/collide or create a near-empty page | Replace the local closing layout with `soft-reflection`, then rebalance semantic task groups against the locked page budget. Preserve comfortable type and writing lines. |
| A written-response prompt and its writing lines split across pages | Rewrite the task with a binding block (`soft-task`, `soft-output-task`, or `soft-reflection`); do not rejoin the pieces with manual `#v()` spacing. |
| A fragment page holds only stray options or questions, or questions are orphaned from their passage | Move the whole task group or passage as one unit (`soft-exercise-group` for a one-page group, sticky `soft-passage` for a longer one); do not push stray items back onto the previous page one by one. |
| A section title is stranded at the page foot while its first content starts on the next page | Confirm the call uses `soft-section(num:, title:)`. Restore the frozen sticky heading block (`breakable: false`, `sticky: true`) or apply the same sticky wrapper to the local section component, then fresh-compile and inspect every affected page plus the contact sheet. Do not insert manual page breaks for each observed instance. |
| A beginner is asked to decode, write, blend, spell from IPA, or receive a score for an untaught sound | Stop delivery. Add a student-visible articulation/auditory cue, teacher model, and word-level practice before that task, or downgrade the sound to an unscored teacher-modelled carrier with ordinary spelling only. Update and rerun the cumulative taught-sound gate. |
| A blind listening prompt exposes the word/sentence or its key follows a simple repeating cycle | Move the stimulus to the teacher-only script, leave only response structure on the student page, independently scramble the reading/key order, then recompile both editions and inspect the task plus answer parity. |
| A legitimate pronunciation variant is marked wrong, or a learner's variant replaces the actual listening stimulus in the key | Separate the two contracts: score listening against the teacher's actual reading, and list accepted stable production variants with a no-penalty note. |
| Missing font, unreadable glyph, A4 mismatch, or PDF metadata mismatch | Stop delivery immediately and report the evidence. |
| Blank page, clipping, overflow, overlap, or detached writing surface | Stop and report the affected page and render; do not treat compile success as closure. |
| Answer, rationale, teacher note, internal instruction, or local location visible to students | Stop delivery immediately; record a P1 or P0 as appropriate. |
| Unclear mode, source identity, overwrite authority, or reviewer independence | Stop immediately before any mutation or verdict. |
| Compilation succeeds | Continue rendering every page and inspect the contact sheet plus every page at full size; compilation is not visual evidence. |

For ordinary BUILD work, the same agent may repair and recheck. During frozen RELEASE sign-off, the reviewer remains read-only; any later edit invalidates that sign-off and returns the artifact to the producing agent.
