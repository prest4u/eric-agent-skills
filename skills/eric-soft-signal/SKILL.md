---
name: eric-soft-signal
description: Use as Eric's primary Skill for creating, editing, structuring, or delivering English teaching documents in the Soft Signal system, including student handouts, practice, homework, review materials, teacher editions, Markdown/structured content, and A4 Typst/PDF output. Use even when the request says “PDF” if the real product is an Eric English teaching document. Do not use for generic PDF file operations, DOCX/PPTX, posters, frontend work, or long textbook publishing systems.
---

# Eric Soft Signal

Own the teaching document from source material to a usable learning surface. Create the visible document before expanding QA. Treat the bundled template as the visual source of truth: extend it with local teaching components, but do not recreate its tokens, base components, or page theme as a parallel Soft Signal dialect unless Eric explicitly asks to redesign the system itself.

## Routing

- Route Eric's English teaching handouts, lessons, homework, review sheets, and teacher/student editions here first, including A4/PDF delivery.
- Use the generic `pdf` Skill only for narrow operations such as reading, extracting, merging, splitting, rotating, OCR, forms, or encryption.
- Use `eric-designed-pdf` only for long textbook or publishing-system work that exceeds the Soft Signal document contract.
- Treat `$eric-pdf` as the explicit-only Typst A4 adapter/QA route, not the default document creator.

## BUILD: default

1. Derive the learner, classroom use, authoritative source, output path, and student/teacher boundary from the request and workspace.
2. Build the teaching sequence before decoration. Every activity needs a clear learner action, usable writing space, and an intentional Chinese/English hierarchy.
   - In beginner pronunciation or phonics materials, a sound symbol is usable only after a student-visible articulation/auditory target, a teacher model, and word-level imitation or practice. Appearance is not instruction. Maintain a cumulative taught-sound ledger.
   - Treat sounds as `new target`, `previously taught`, or `carrier`. An untaught carrier may appear only inside an ordinarily spelled whole word or sentence that the teacher models first; do not expose its IPA, require independent decoding/transcription, or deduct for it.
   - A visible whole-word IPA decoding or spelling task is allowed only when every scored unit is already taught. Blind listening must hide the spoken word/sentence until the attempt is complete and must not use a periodic answer order that can be guessed without listening.
   - Keep the teacher's actual listening stimulus separate from accepted student production variants. Score listening against what was read; accept a documented, stable pronunciation variant in production instead of treating it as an error.
3. For A4 output, copy `assets/soft-signal-template.typ` verbatim and the complete `assets/fonts/` directory into the delivery folder; keep imports relative. Build subject-specific components on top of that copied template. Do not substitute a custom base theme that merely imitates the palette. Preserve the public `soft-section(num:, title:)` signature and its sticky title behavior: a section title must travel with the first following content block instead of remaining alone at a page foot.
4. Read [visual language](references/visual-language.md) before composing pages and [English teaching grammar](references/english-teaching-grammar.md) when organizing explanations or practice. Select compact handout mode or editorial self-study mode before setting page flow.
5. When Eric supplies a reference PDF or a verified Soft Signal artifact exists in the workspace, inspect representative rendered pages and reuse its page grammar or compatible local components. Do not infer the style from colors alone.
6. Produce the visible source/PDF first. For a draft, run only the cheapest check that can disprove the requested result, such as a fresh compile plus inspection of the changed page.
7. Deliver the artifact path, source identity, check evidence, and any genuine gap. The same agent may make ordinary fixes and recheck them.

Do not require a writer/reviewer handoff, persistent QA packet, dimension score, or formal verdict for a draft or normal classroom iteration.

## PROOF: costly visual direction

When page grammar, density, or audience structure is materially uncertain, make one representative page or short section. If a reference artifact exists, inspect at least its cover, one dense explanation page, one exercise page, one transition, and one teacher-facing page when available. Compare the proof against those structural traits—not only its palette. Show the proof before scaling. Freeze the copied template and the approved local components, then let batch work vary content rather than visual rules. Ask Eric only if the proof exposes a material product choice, large batch cost, overwrite, or external impact.

## Teaching images

Embed a scene image only when students must observe it to complete a meaningful task. Strong uses include time or state comparison, location and spatial relations, story sequence, information-gap speaking, reading reconstruction, and picture-based writing. Do not add decorative images merely to fill space.

- Define the learner action before generating or selecting the image. Every visible detail should support a question, comparison, inference, or piece of student writing.
- For multi-panel scenes, keep the protagonist, location, viewpoint, and visual style continuous; change only the details that carry the teaching contrast. Typical contrasts include Usually / Yesterday / Now, before / after, or two versions of the same room.
- Keep words, labels, arrows, and grammar prompts out of generated artwork. Add them in Typst so spelling, hierarchy, and print quality remain controllable.
- Place the image and its task on the same page whenever possible. Give enough physical size for the relevant objects, actions, and relationships to remain unambiguous when printed on A4.
- Use one image for several connected actions when useful: observe, choose a structure, answer questions, collect keywords, then write. Do not repeat the same low-value identification task.
- Use the identical asset, crop, panel order, and student wording in student and teacher editions. Add answers, likely observations, ambiguity warnings, and teaching moves beside the same task in the teacher edition.
- Keep image files inside the delivery folder and import them through relative paths. Inspect the final rendered page at intended print size for sharpness, cropping, misleading details, and sufficient writing space.
- Reject or regenerate any scene whose answer depends on an unclear object, inconsistent character, accidental AI artifact, or background detail not taught in the lesson.

## RELEASE: formal student or external delivery

1. Freeze the exact Typst/PDF identity and confirm output/overwrite authority.
2. Read [render and evidence](references/render-and-evidence.md), compile fresh from the delivery root, confirm A4 size and the intended page count.
3. Run `scripts/render_pdf.py` with `PYTHONDONTWRITEBYTECODE=1`, inspect the contact sheet and every page, and check clipping, blank pages, missing glyphs, detached writing areas, student-facing answer leaks, decorative empty space, repeated page skeletons that flatten the teaching hierarchy, and any section title left at a page foot while its first content begins on the next page. For a beginner pronunciation release, also validate the cumulative taught-sound ledger against every student-visible IPA/scoring surface and assessment target. A ledger declaration alone is insufficient: retain evidence of student-visible teach → teacher model → word practice before independent use.
4. Stop mutation and obtain at most one independent review when the artifact is a formal outward/student delivery or Eric explicitly requests sign-off.
5. Keep review separate from publish, send, upload, or overwrite authority.

Compile success alone is not release evidence. Source checks do not substitute for rendered-page inspection.

## Bounded repair

On a failed build or render, preserve the exact command and visible failure. Make one targeted correction and rerun the same check. If it repeats, gather new diagnostic evidence before a second correction. If the second correction repeats the failure, change approach or report the concrete blocker; do not generate JSON fingerprints or request routine approval.

Read [failure patterns](references/failure-patterns.md) only after an actual build or render failure. Read [audit rubric](references/audit-rubric.md) only for explicit formal sign-off.
