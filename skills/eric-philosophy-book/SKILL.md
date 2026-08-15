---
name: eric-philosophy-book
description: 'Use when designing, rebuilding, reviewing, or QA-ing Eric''s philosophy book publication workflow, including cover, A5/PDF interior typography, illustration placement, illustration briefs, historical/philosophical visual language, book-feel proofs, and final publication readiness for 《东西方哲学史故事集》 or related philosophy-book artifacts.'
---

# Eric Philosophy Book

## Core Direction

Build a finished literary-philosophy book, not a decorative PDF. The current approved direction is the P07 Recommended Hybrid proof in:

`<project-dir>`

Use P07 as the living visual anchor: quiet paper, strong Chinese title, restrained museum/archive atmosphere, historical-philosophical images, and stable long-form reading. Preserve the earlier M17 page-feel preference when choosing illustration density and image tone.

## Visual Principles

- Treat images as historical/philosophical evidence or atmosphere, not filler. Empty areas may carry historical traces, diagrams, maps, sky, water, manuscripts, ruins, instruments, or conceptual shadows if they deepen the reading.
- Keep illustration frequency generous but not dominant: many chapters can use partial-page visual moments, but text remains the book's center of gravity.
- Treat P07 as a visual atmosphere, not a fixed page template. Do not let every task use the same image/title/body/caption arrangement. Build a varied page grammar library and rotate forms by chapter pressure, page role, image type, and reading rhythm.
- Avoid visible template repetition. The same opener, image-text, side-caption, notes, or text-heavy layout must not recur mechanically across adjacent pages, adjacent chapters, or successive proof tasks. If a contact sheet looks like the same page with different text, redesign.
- Avoid repeated cover art inside the book. Cover imagery is cover-only.
- Do not expose internal labels, variants, validators, "Eric Teaching Studio", proof names, model names, or production language in reader-facing pages.
- Prefer quiet editorial restraint over showy design. If a page looks like a poster, dashboard, worksheet, landing page, or AI art showcase, redesign.

## Current Decisions

- M17 remains the page-feel anchor; P07 remains the premium typography and book-atmosphere anchor.
- M75/M76 are the active interior-language decisions: page-native corner paper fields, typography-led breaks, no decorative lines/circles through body text, varied chapter grammar, and first-batch rollout across Thales through Plato.
- M78 is the active full-book production map: all 60 main chapters have visual slots, asset routes, ratio targets, batch order, and review gates.
- M80 is downgraded to a pagination skeleton, not a visual direction. M81 is the active Part-level design recovery node: it renders the first part as a real book section using the accepted M75/M76 language.
- M81 follow-up: page-native background image fields should be visibly present, not barely-there. Deepen paper/image fields contextually on reading pages while keeping the body text clear.
- M81 correction: never build a chapter by generating one background image and reusing it across that chapter. Each reading page needs a one-use page-native visual field; same-chapter pages must rotate multiple historical/philosophical sources, crops, image grammars, and text layout variants.
- Copywriting decision: DeepSeek owns Chinese prose output when Eric asks for rewriting, chapter copy, reader-facing transitions, captions, or de-AI polishing. Codex should give DeepSeek direction, constraints, context, and acceptance gates, then preserve DeepSeek's Chinese as the copy source instead of rewriting it with Codex prose. Codex remains responsible for visual direction, typography, layout, asset curation, PDF building, and QA. Do not expose provider/model names in reader-facing pages.
- Current M75/M76 assets are proof assets, not final publication art. Final book production still needs slot-native, print-size ImageGen or licensed assets, one-use asset manifests, and Eric or independent visual review.

## Typography System

Start from this type hierarchy unless the artifact proves it should change:

- Cover Chinese title: `Songti SC`, bold, large, slightly tracked, with ample paper around it.
- Body: `Songti SC`, around 9.1pt on A5, comfortable leading, justified only where it improves reading.
- Running heads and small labels: `Avenir Next` or another restrained sans.
- Captions and notes: `STFangsong` or quiet Songti treatment, lighter than body text.
- Latin/Greek philosophical terms: use tasteful italic, but avoid forced luxury.

For cover English subtitles, do not over-letterspace. Use `Baskerville italic`, `Hoefler Text italic`, or similarly literary serif italic with tight-to-moderate tracking, usually `0.015em-0.035em`. Avoid wide tracking like `0.075em+` unless a proof shows it is optically better. Decorative or calligraphic English is allowed only if it feels printed-book natural rather than wedding-card or logo-like.

## Workflow

1. Inspect the current V4 workspace and relevant proof/report before changing anything.
2. Preserve approved text unless Eric explicitly requests copy changes. When copy changes are needed, route Chinese prose generation to DeepSeek with clear editorial direction and use its output as the copy source; Codex should not "improve" the Chinese afterward except for mechanical integration or explicit Eric-requested constraints.
3. Select or design page grammars before building: at minimum choose distinct roles for opener, text-heavy page, image-text page, notes/source page, and transition page.
4. Make proof changes through source scripts/templates, not manual PDF edits.
5. Generate PDF plus rendered page PNG/contact sheet for review.
6. Perform visual self-review at full-page size and contact-sheet size, including a repetition scan across the contact sheet.
7. Run relevant validators and scans before claiming readiness.
8. Commit scoped changes when Eric asks to advance or preserve a node.

## Push-Up Rule

When Eric says a direction is OK or asks to continue, move upward from local polish to book-scale production: page proof -> chapter batch -> full-book slot map -> asset generation batches -> representative section proof -> full-book proof. Do not keep making another small page-detail pass unless Eric names a specific page problem.

If work starts revolving around one line, one circle, one opacity, one corner field, or one page's minor detail for more than one correction pass, stop and create the next higher-level rollout artifact instead.

Repeated corrections must be preserved in this skill and in the project `AGENTS.md`: no internal language in reader pages, no cover reuse, no template repetition, no decorative marks crossing body text, no final/publication-ready claims without gates, and no small-detail trap after a direction is accepted.

## QA Gates

Before calling a proof "right" or ready to promote:

- PDF has expected pages, extractable text, embedded fonts, no Type 3 surprise unless explicitly accepted.
- Reader-facing text contains no internal project language, proof labels, API/provider names, or brand marks that were not requested.
- Cover, `给读者`, a chapter opener, one text-heavy spread, one image-text page, and notes page are visually inspected as rendered PNGs.
- Contact sheet does not reveal a mechanical repeated template. Each selected chapter or task batch should show meaningful variation in crop, image role, title placement, density, margin behavior, caption logic, and text rhythm while staying inside the same book identity.
- Same-chapter page backgrounds are checked for visible reuse. A repeated chapter-wide mother image, even with different opacity or crop, fails unless it is a deliberate and documented motif on only one or two pages.
- English subtitle and Latin terms are checked separately for font, tracking, baseline, and tone.
- If a formal visual PASS is needed, use Eric confirmation or an independent review; same-agent review is only self-check.

## Current Recommendation

For the next philosophy-book iteration, continue from the M75/M76 accepted direction:

- Start from M81 when Eric asks to continue the book design: render the next Part-level PDF, not another map, ledger, or CSV control layer.
- After M81, continue Part-by-Part rendered design proofs, checking actual pages, chapter entrance cadence, text density, image integration, and final-intent asset needs.
- Keep P07 cover atmosphere and M75/M76 interior language, but do not treat any current sample asset as final art.
- Only return to page-detail polishing when Eric points to a concrete rendered-page issue.
