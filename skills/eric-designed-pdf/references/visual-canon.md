# Visual Canon

Use this reference before any design transfer, rebuild, or visual repair task that should follow the Eric-designed textbook language.

## Source Of Truth

The public, self-contained source of truth is:

- this text grammar and its page-role anchors
- `visual-dna.md`, `component-grammar.md`, and `failure-taxonomy.md`
- the executable `starter-project` and `starter-project-v2` templates

Authorized private regression fixtures may add Golden PDFs, contact sheets, and rendered pages. They strengthen regression evidence but are optional: the public Skill must install, run, and pass its default maintenance gate without them.

Do not copy the golden sample text, images, or exact pages into user projects. Transfer the design grammar: page roles, hierarchy, rhythm, color logic, spacing, and component behavior.

## What The Canon Is

The canon is a printed textbook/workbook language:

- large visual signal only where it earns the page role: cover and opener, with separate one-use assets
- restrained editorial title lockups instead of UI cards
- teal structural rules, magenta activity labels, green/rust support accents
- white paper pages with quiet density, not app dashboards
- paper-textured practice blocks, stable writing lines, and compact rule tables
- editorial activity/planner surfaces that read like printed workbook pages, not diagnostic forms or production tools
- back matter with pale blue-gray lookup rhythm
- visible page-role contrast across the contact sheet

## Page-Role Anchors

| Page | Canon role | Transfer requirement |
| --- | --- | --- |
| p1 cover | Full-bleed image, heavy title lockup, tiny metadata | No centered web hero, no card, no thin title, no accidental Chinese/name/title wrapping; bottom-right Studio mark must remain readable over the photo. |
| p2 title | Quiet editorial title page | Keep whitespace; use a small mark/rule and quiet navigation rows rather than decorative blocks or empty ceremony. |
| p3 opener | Photo-led unit start with bottom objectives band | One controlled composition, not stacked cards; uses a distinct opener asset, not the cover bitmap. |
| p4 elements | Dense rule/explanation page with teal top rule | Must contain real method texture: rule, example, table, practice handoff. |
| p5 activity | Magenta activity label plus workbook record surface | Activity tag should read like a workbook, not a button; the page must resolve into a cohesive record block with numbered prompts and bounded writing lines, not loose trailing questions. |
| p6 paragraph practice | Paper-textured model passage and writing lines | Keep practice area tactile and stable. |
| p7 photo passage | Photo plus caption and short-answer lines | Photo gives context; text remains deterministic; uses a distinct passage/context asset, not the cover or opener bitmap. |
| p8 writing planner | Structured rows, paper-surface writing area, understated rule strip, editorial side labels, softened prompts, and editing checklist | Lines and rows must not collapse, feel spreadsheet-like, or read as a generic worksheet table. Left labels should read as printed marginalia, not UI controls. |
| p9 handbook | Pale blue-gray reference page with meta band, numbered compact index rows, mini rules, quiet section labels, and lookup table rhythm | Denser lookup hierarchy, not another worksheet. The page should switch into back-matter/reference mode at contact-sheet scale. |
| p10 answer key | Compact back-matter answer table | Teacher/back-matter profile only unless explicitly requested. |

## Typography Canon

For Chinese-heavy textbook pages, prefer the B/C proof direction:

- Primary Chinese sans: `Hiragino Sans GB`, then `PingFang SC`.
- Latin display: `Avenir Next Condensed`, `Arial Narrow`, or `Helvetica Neue Condensed` when available.
- Latin body: `Georgia` for editorial English body only; do not force Chinese body into a weak serif fallback.
- English model/passage titles inside paper-textured paragraph-practice blocks should keep an editorial serif route such as `Georgia`; forcing these English titles into a heavy CJK sans makes workbook pages feel like diagnostic dashboards instead of textbook pages.
- Cover Chinese title must use a firm semibold/bold weight. If the title looks thin at contact-sheet scale, it is a visual failure.
- Mixed Chinese/English cover titles, student names, and phrases such as `IELTS备考计划 for Sample Learner` must be locked deliberately. Do not let CSS/browser wrapping split a Chinese word or push a private-name suffix onto an accidental orphan line; label that failure `title-wrap-break`.
- Do not rely on Source Han/Noto CJK unless the build proves the font is installed and embedded. If it falls back to Songti/PingFang and becomes thin, reject the proof.

## Transfer Workflow

1. Read this canon, the visual DNA, and the component grammar. If authorized private Golden fixtures are installed, also inspect their contact sheet and at least six representative rendered pages.
2. Name the target page roles before editing: cover, navigation, opener, method, workbook, review, handbook.
3. Extract tokens and component grammar from the canon into the target theme before placing content.
4. Rebuild the target pages from the canon grammar. Do not patch a failed UI/dashboard design.
5. Render a small proof set first: cover, navigation, opener, dense method, workbook, review/checkpoint.
6. At contact-sheet scale, check the common transfer failures before scoring: cover title breaks, empty p2 navigation, loose workbook tail, diagnostic-form drift, plain spreadsheet-like planner, weak back matter, and rendered text glitches.
7. For custom projects, confirm the source and visible output carry the target book identity, not starter residue such as `Pathways to Better Writing`, `English Writing System`, or `canyon-cover`.
8. Compare the proof contact sheet against the public page-role anchors and reject patterns before expanding the book. When authorized private Golden fixtures are installed, add the Golden contact-sheet comparison.

## Release Rule

The visual review must include:

- `Canon comparison:` naming the public page-role anchors used and how the target matches them; include Golden page identifiers only when authorized private fixtures were available.
- `Reject patterns checked:` naming the failure labels reviewed from `failure-taxonomy.md`.
- `Font decision:` naming the selected font route and fallback.

If those fields are missing, visual review is pending even when the score says 9.5.
