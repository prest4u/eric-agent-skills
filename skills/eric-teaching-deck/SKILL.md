---
name: eric-teaching-deck
description: "【教学投屏】Build file:// classroom projection HTML for Eric's Stage and 讲解 decks. Use when creating or rewriting a Stage webpage, teaching HTML, 投屏讲解, one-item-at-a-time lecture, or any English grammar Stage after the Soft Signal paper exists. Owns five scenes, teacher beats, local GSAP, a reviewed classroom-slide surface (stone paper, amber accent, full-width cards), and item-ledger web columns. Do not use for Awwwards sites, ten-step website pipelines, PPT, or paper PDFs."
---

# Eric Teaching Deck

Classroom projection is the product. One Stage is one HTML file. The teacher advances beats. Students never see a dumped list of items or a dumped list of answers.

## Stable identity

- Keep the folder and invocation name as `eric-teaching-deck`.
- Keep the UI display name as **Eric Teaching Deck**.
- Do not rename this Skill to a website, PPT, or slide-writer Skill.

## Route here

Use this Skill for every Stage / 讲解 HTML in `雅思英语句子语法`, `高考英语句子语法`, and later series that share the same teaching HTML job.

Do **not** route through:

- `eric-quality-sites` (portfolio / Awwwards sites)
- `eric-web-pipeline` (ten-step website build)
- `eric-ppt-skill` (PowerPoint)
- `eric-soft-signal` (paper PDFs stay there)
- `eric-designed-pdf`

Paper Typst and the two PDFs stay untouched unless Eric explicitly asks to change paper.

## Contract

These are rules, not adjectives.

1. **一拍一意** — One screen serves one teaching move. The next beat appears only when the teacher triggers it (space, right arrow, or click on empty paper). Mash-skip finishes the current animation only. It does not jump the item or dump the answer.
2. **五种场面** — Change the scene when the item type changes. Do not invent a new visual world per page.
   1. 封面 / 收束
   2. 讲规则（知识点 + 一道例题）
   3. 判断一题（实义/系动词、主谓/主谓宾/主系表、核心）
   4. 改写 / 改错（三种句子、找错）
   5. 四框选择
3. **综合场在后** — Teach every knowledge point of this Stage with scene 2 and one example each. Only then run a mixed set on scenes 3 / 4 / 5. Each mix type: 2 basic items + 1 trap item. Still one item, then that item's explanation.
4. **字体是设计，不是默认** — The deck uses the reviewed classroom-slide stack: PingFang SC + local Noto Sans SC / Source Sans 3. Titles are 700 with negative tracking. Cover titles are a tight two-line cluster `clamp(56px, 6.2vw, 92px)`; long Chinese covers need stronger wall presence. Teach h2 stays a slide title `clamp(28px, 2.8vw, 40px)`; the example well fills leftover height. Judge sentences `clamp(44px, 5vw, 68px)`. Do not copy a 26px content title onto a 2-block 一拍一意 scene, and do not leave rule + a thin well at the top with an empty lower half. English examples stay in the same sans. Do not dress the deck in Soft Signal Zhuque Fangsong or Function Journey Songti. Paper PDFs stay Soft Signal.
5. **动效** — GSAP timelines hang on `data-beat`. Entrance is 0.45–0.6s (current engine 0.55s). Teacher mash-skip completes the current beat at once. `prefers-reduced-motion: reduce` shows the current beat with no tween. Vendor GSAP inside the project. No CDN. No npm app. Do not patch `deck.js` to add child stagger.
6. **题库** — Rewrite the web-example and web-practice columns of `item-ledger.md` first, then write HTML. Do not touch the paper column. Web sentences stay inside that Stage's word bank and must not collide with paper or with the sibling exam series.
7. **验收** — Watch the full beat sequence in a real browser. One screen does not scroll. One screen does not pour out several items or several answers.

Read the matching reference before implementing that layer:

- [design-system](references/design-system.md) — tokens, radii, overflow protocol, how to derive a new scene
- [scenes](references/scenes.md) — composition, type size, scene change
- [beats](references/beats.md) — advance, skip, 看对照
- [type](references/type.md) — font roles and bans
- [motion](references/motion.md) — local GSAP, ease, reduced motion

## Build order

1. Read the Soft Signal lesson thinking for this Stage. Do not copy paper stems.
2. Run a holographic probe only if a named student is attached; the workspace dossier wins on conflict.
3. Rewrite `item-ledger.md` columns **网页例题** and **网页当页练** only.
4. Copy or reuse the Stage web runtime: `vendor/gsap.min.js`, `fonts/` plus `SOURCES.md`, shared `css/deck.css`, `js/deck.js`.
5. Proof the five scenes with real new content from this Stage. Open that file in the browser before writing the full deck.
6. Write the full Stage HTML in teach → example → mix → close order. Update the series catalog with the same type and cover grammar.
7. Before calling it delivered: `eric-teaching-polish --strict` on student-visible HTML, a `file://` pass with no network, mash-skip, and open the **full** deck in the browser—not only the proof.

## Teach spine (default)

```text
封面
each knowledge point     场面2 + 1 例
综合场                   场面3 / 4 / 5，每类 2 基础 + 1 挖坑，仍一题一讲
收束                     场面1 → 去做纸面
```

Stage One pedagogy lock, until Eric changes it:

- First: lexical vs linking; core vs modifier; lexical verbs ask `do / does / did`; `be` changes itself.
- Sense verbs: recognize only. Do not drill their three sentence forms.
- Stay out of there be, modals, passive, progressive, perfect, and clauses.
- Four writing situations stay on paper. The web mix uses judge / rewrite / choose.

## Runtime shape

One Stage folder:

```text
stage-n/web/
  vendor/gsap.min.js
  fonts/          # OFL files + SOURCES.md + license
  css/deck.css
  js/deck.js
  scenes-proof.html   # five-scene gate only
  stage-n.html        # the class file
```

Shared rules for the engine:

- Each `<section class="scene" data-scene="cover|teach|judge|rewrite|choose">` is one scene.
- Each teaching move is `[data-beat]`. Hidden until its turn.
- Clicking a chip, choice, 看对照, or a nav control does **not** advance the deck.
- 看对照 reveals contrast for the **current** item only.
- Visible text must survive `eric-teaching-polish --strict`. No ledger codes (`WE-01`), no `答案：` / `解析：`, no `Soft Signal`, no `挖坑`, no file paths.

## Language and family

The deck is a reviewed classroom-projection surface, not a projected Soft Signal booklet, not an Apple product page, and not a Function Journey notebook. Use `#fafaf9` canvas, `#1c1917` ink, `#d97706` amber for kicker / progress / divider / 看对照 / catalog「进入」, white cards, amber highlight wells (`#fffbeb` + `#fde68a`), and a full-width content column. Student-visible pages must not say MBTI, 功能, 类型, or 八维. No Google Fonts CDN.

Student-facing Chinese sounds like Eric in class. After drafting, run polish (strict) and a `humanizer-zh` pass if that Skill is installed. Re-open the file after wording changes.

Footer may say `ERIC TEACHING STUDIO`. No student names, no EC numbers, no band numbers.

## Done means

- `file://` plays the whole Stage with the network off.
- Space / right arrow / empty-paper click advances one beat.
- Mash-skip finishes the current tween; the next item still waits.
- Five scenes are visually distinct and still one classroom-slide product.
- Browser inspection of the **full** deck, not only the proof.
- Ledger web columns updated. Memory / holographic updated when the workflow itself changed.
