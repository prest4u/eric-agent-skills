# Vocabulary Page Role Contracts

## Whole Lesson Contract

A lesson is not a word list with decoration. It must take the learner through a usable loop: meet words in context, understand them quickly, use core words in sentences, connect grammar, output, then carry weak words into review.

For a 40-word lesson, default distribution is A 12 / B 20 / C 8.

- A words get deep treatment: simple English, Chinese, phrase, grammar pattern, exam sentence, watch note, and learner sentence.
- B words get phrase/use treatment: collocation, short sentence, common mistake or exam use.
- C words get recognition treatment: meaning, part of speech, quick reading signal.

Role name map for routing and validators: `cover`, `title`, `unit-opener`, `reading`, `glossary`, `memory-chain`, `grammar bridge`, `B/C recognition`, `red-word challenge`, `before-you-leave`.

## Tone Contract

The lesson should read as a coherent premium workbook, not a dark cover plus unrelated pale worksheets.

- Cover and opener may use darker final assets, but overlays should preserve readability and avoid making the whole system feel gloomy.
- Cover/opener image treatment should be checked at contact-sheet scale and full-page scale; if they read as a dark separate book before the light workbook body begins, mark `FRONTMATTER_DARK_TONE_DRIFT`.
- Body-page headings should use coordinated deep teal/blue-ink, not isolated black patches.
- Magenta/red is reserved for target vocabulary and review emphasis.
- Yellow/amber is reserved for check/action strips.
- A visual repair must coordinate the surrounding page system, not only the complained-about line.

## p5 Reading Glossary And Quick Check

Learner action: understand target words from the reading and prove recognition with two quick written checks.

Required surface:

- A/B/C/D glossary example rows with stable columns.
- Red target word is visually distinct but not oversized.
- Simple English and Chinese are separate layers, not jammed into one sentence line.
- Phrase/collocation sits as a quiet final cue.
- Glossary Check has full-width low-baseline writing lines.

Reject:

- Whole example sentences running as uneven one-line paragraphs.
- Mid-cell underline, short underline, or underline detached from prompt.
- Dense table look that feels like a database export.

## p6-p8 Core Words

Learner action: learn four A words deeply and write one controlled sentence for each.

Required surface:

- Four word cards in a stable grid.
- Each card includes meaning, phrase, grammar, exam sentence, watch note, and My Sentence.
- The target word may be red/bold in example sentences.
- My Sentence uses a prompt plus semantic writing slot, normally `memory-sentence-line`.

Reject:

- Bullet-list output areas.
- Floating short blanks.
- Punctuation stranded after the line.
- Different card heights caused by writing lines.

## p9 Grammar Bridge

Learner action: turn vocabulary knowledge into sentence patterns.

Required surface:

- Long headings should use a compact two-line title, e.g. `Grammar Bridge:` then `Put a word in a sentence`.
- The intro box should be compact; it introduces the bridge, not consume the vertical space needed for pattern rows.
- The title color should coordinate with the lesson palette, normally deep teal/blue-ink, not a standalone black patch.
- Five pattern cards with consistent row height and spacing.
- Pattern, word, and sentence are visibly connected.
- Vocabulary markers inside pattern sentences must render as styled target words; raw `[[A:...]]`, `[[B:...]]`, or `[[C:...]]` is never student-visible.
- Map Check is a bottom strip or paired surface using `grammar-map-check-line`.
- Left label and right sentence block should share a real height/baseline relationship.

Reject:

- Oversized all-caps heading that wraps awkwardly across the page.
- Large empty intro box that makes the pattern rows feel cramped.
- Side labels that do not match the actual content height.
- Check strips that look pasted below the card grid.
- Pattern cards with random internal spacing.
- One-line color patches that leave the title, intro, cards, and Map Check in different visual systems.

## B Words Phrase Use

Learner action: recognize useful words quickly and make each one usable through a phrase plus a short example sentence.

Required surface:

- B words have phrase/use treatment rather than A-word deep cards.
- Each row shows word + part of speech, Chinese meaning + simple English, then a clearly readable `Phrase` and `Sentence`.
- The phrase and sentence should share a single use area so the learner reads them as a small usage unit.
- Target words inside example sentences are highlighted inline.
- CSS must scope part-of-speech styling narrowly; broad selectors such as `.b-row span` are forbidden because they can turn highlighted target words into block fragments.

Reject:

- Four-column tables where the sentence column is so narrow that examples break into one-word fragments.
- Target-word highlighting that forces the word onto its own line.
- Database-export feeling with no learner action.
- Fixing wrap by deleting real example content instead of repairing the reusable row layout.

## p15 Before You Leave

Learner action: decide what is still red and plan the next short review.

Required surface:

- Red Word Record is a workbook record surface, not a tiny note field.
- Number, prompt, and line align as one row.
- Next Practice Plan is an action ticket with enough writing width for a real answer.
- Lines use `final-record-line` and `next-plan-line`.
- Record rows disable normal row separators; the writing line is the only strong horizontal rule inside each row.

Reject:

- Lines too short to write in.
- Lines too close to the prompt or drifting vertically.
- Row separator lines colliding with student writing lines.
- Visual language that feels like a generic checklist instead of a printed workbook page.
