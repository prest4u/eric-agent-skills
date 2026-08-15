# Render and evidence

Use one authorized delivery root with this exact shape:

```text
source/student-handout.typ
source/teacher-edition.typ
soft-signal-template.typ
fonts/
outputs/
renders/student/
renders/teacher/
```

Copy the bundled template and complete bundled font/license directory. Keep the template beside `source/`, not inside it.

## Public authoring contract

Use named arguments exactly as shown. The only positional argument in `soft-setup` and `soft-body` is the trailing content block.

For a one-page artifact:

```typ
#import "../soft-signal-template.typ": *

#soft-setup(title: [Sentence practice], meta: [Student handout])[
  = Complete the sentence
  The parcel arrived #soft-blank().
]
```

For a cover plus body pages:

```typ
#import "../soft-signal-template.typ": *

#soft-cover(
  title: [CURRENT LESSON TITLE],
  subtitle: [CURRENT LEARNING FOCUS],
  meta: [STUDENT · Name: #soft-blank(width: 5em)],
  code: [UNIT-ID],
)

#soft-body(title: [CURRENT LESSON TITLE], meta: [STUDENT])[
  #soft-section(num: [01], title: [Read · Choose])
  The learner placed the notebook on the #soft-blank().

  #soft-question(
    stem: [(1) Choose the best word for #soft-blank().],
    choices: ("desk", "cloud", "sing", "carefully"),
    evidence-label: [Evidence: ],
  )

  #pagebreak()
  #soft-reflection(
    title: [Reflect on your choice],
    prompt: [Name one clue that made your answer fit the sentence.],
    lines: 4,
  )
]
```

This is synthetic scaffold content, not delivery content. Replace every uppercase identity placeholder, sentence, option, number, and reflection prompt with material supported by the current authoritative source.

`soft-cover` is named-only: never pass its title positionally. `soft-section`, `soft-question`, and `soft-reflection` are also named-only. Pass exactly four strings to `choices`.

`soft-section(num:, title:)` has a frozen public signature and sticky page behavior. Its heading block is unbreakable and moves with the first following content block when the remaining page space is insufficient. Local teaching components may wrap it, but must not remove `sticky: true`, replace it with a free-standing grid, or add a forced break between the heading and its first content.

## Fragile syntax rules

- Use `#soft-blank()` or `#soft-blank(width: 5em)` inside markup. Never type raw underscore runs such as `____`; Typst parses them as markup and may hide the blank or break delimiters.
- Use `soft-question` for every A–D item. It keeps each mark, label, and option in one unbreakable cell. Do not place checkboxes in a separate grid row.
- Use `soft-reflection` for the closing heading, prompt, and ruled response surface. The whole block moves together when space is insufficient, and its fixed marker column prevents label collisions.
- Set paragraph leading with a scoped block and `#set par(leading: 1em)`. Do not pass `leading` to `text`.
- Keep type at or above comfortable print size and preserve the requested writing lines. If the page budget fails, shorten nonessential copy, reduce decorative padding, or rebalance task groups.

## Student and teacher sources

Author two separate source files. A student source must omit `correct-index` and `teacher-note`. A teacher source must say `TEACHER EDITION` or `教师版` on the cover/header and may use:

```typ
#soft-question(
  stem: [(1) Choose the best word for #soft-blank().],
  choices: ("desk", "cloud", "sing", "carefully"),
  evidence-label: none,
  correct-index: 0,
  teacher-note: [A · desk. The preposition "on" needs a plausible surface; if a learner selects an adverb, ask what noun can follow "the".],
)
```

Set `evidence-label: none` in a compact teacher key when no learner writing line is needed. Keep the default evidence line in student practice.

Do not generate the student PDF by visually hiding teacher content. Compile the two explicit sources to two explicit output identities.

## Compile and inspect

From the delivery root, run these literal commands:

```bash
typst compile --root . --font-path fonts source/student-handout.typ outputs/student-handout.pdf
typst compile --root . --font-path fonts source/teacher-edition.typ outputs/teacher-edition.pdf
```

`--root .` is required for the `source/ -> ../soft-signal-template.typ` import. Then run `pdfinfo` and `pdffonts`, extract both PDFs with `pdftotext`, and render each into its own empty directory:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 /path/to/eric-soft-signal/scripts/render_pdf.py outputs/student-handout.pdf renders/student
PYTHONDONTWRITEBYTECODE=1 python3 /path/to/eric-soft-signal/scripts/render_pdf.py outputs/teacher-edition.pdf renders/teacher
```

Inspect each contact sheet and every page at full size. Confirm the locked page budget, A4 geometry, embedded fonts, visible blanks, attached choices, reflection attachment, nonblank pages, margins, glyphs, absence of clipping/overlap, and absence of a section heading stranded at a page foot. Extracted student text must contain no answer, rationale, `TEACHER`, `教师版`, internal path, or production note; teacher text must be unmistakably teacher-only.

Record source/PDF/render hashes, exact command exits, page counts, inspected pages, and findings. Compilation proves only buildability; rendered pages prove visible integrity.
