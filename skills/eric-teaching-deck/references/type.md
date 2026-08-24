# Type roles

The deck reads like a reviewed classroom slide on a projector. One sans stack. Titles are 700. Type plus cards fill the frame. Do not copy a 26px content-slide title onto a 一拍一意 deck that only has two or three blocks — that leaves a title plus a thin well and a huge empty lower half.

## Stack

```css
--font-sans: "PingFang SC", "Noto Sans SC", -apple-system, BlinkMacSystemFont,
             "Source Sans 3", sans-serif;
```

On Eric's Mac, PingFang SC is the live face. Noto Sans SC and Source Sans 3 in `web/fonts/` are the offline fallback. Do not load Google Fonts. Do not load Songti or Noto Serif on the deck.

Weights: **400 / 600 / 700**. `font-style: italic` is banned.

Do not load Zhuque Fangsong or Source Serif 4. Those belong to the paper booklet.

## Per-role table (1080p clamps)

| Role | Selector | Size | Weight | Line | Tracking | Color |
|---|---|---|---|---|---|---|
| Cover / close title | `.scene-cover h1` | `clamp(56px, 6.2vw, 92px)` | 700 | 1.12 | `-0.03em` | `--ink` |
| Scene title | `.scene-teach h2` | `clamp(28px, 2.8vw, 40px)` | 700 | 1.25 | `-0.02em` | `--ink` |
| Header kicker | `.kicker` on teach/judge | `13px` | 600 | 1.3 | `+0.12em` | `--faint` |
| Cover kicker | `.scene-cover .kicker` | `14px` | 600 | 1.3 | `+0.14em` | `--accent` |
| Cover lead | `.lead` | `clamp(18px, 1.7vw, 20px)` | 400 | 1.65 | 0 | `--faint` |
| Rule body | `.rule-band` | `clamp(20px, 2vw, 26px)` | 400 | 1.75 | 0 | `--muted` |
| Single well English | `.scene-teach:not(:has(.form)) .example .en` | `clamp(36px, 3.8vw, 56px)` | 600 | 1.4 | `-0.01em` | `--ink` |
| Stacked well English | `.scene-teach:has(.form) .example .en` | `clamp(26px, 2.6vw, 36px)` | 600 | 1.4 | `-0.01em` | `--ink` |
| Default well English | `.example .en`, `.well .en` | `clamp(32px, 3.4vw, 48px)` | 600 | 1.4 | `-0.01em` | `--ink` |
| Judge sentence | `.sentence` | `clamp(44px, 5vw, 68px)` | 700 | 1.25 | `-0.02em` | `--ink` |
| Rewrite source | `.sentence-mid` | `clamp(32px, 3.6vw, 52px)` | 600 | 1.35 | `-0.01em` | `--ink` |
| Choose stem | `.stem` | `clamp(32px, 3.4vw, 48px)` | 700 | 1.3 | `-0.02em` | `--ink` |
| Chip / choice | `.chip`, `.choice` | `clamp(20px, 2vw, 26px)` | 600 | 1.3 | 0 | `--ink` |
| Reason | `.why` | `clamp(18px, 1.7vw, 22px)` | 400 | 1.75 | 0 | `--muted` |
| Helper | `.gap-note` | `clamp(16px, 1.5vw, 18px)` | 400 | 1.6 | 0 | `--faint` |
| 看对照 | `.look` | `14px` | 600 | 1 | `+0.02em` | `--accent` |
| Footer | `.nav` | `13px` | 600 | 1 | `+0.02em` | `--ink` / `--faint` |

Cover titles are two long Chinese lines. Their reference cover is three characters at 64px; ours must go larger (`92px` cap) with tight tracking so two lines occupy similar wall presence. Internal cover gaps stay tight: kicker→title `20px`, title→bar `24px`, bar→lead `24px`.

Well `<b>` is `--accent` / 700. Inline `.en` is 500, never italic.

`.look` inside a flex well must stay `align-self: flex-start` / `width: auto` — otherwise the pill stretches into a full-width bar. Keep `.look[hidden]{display:none}` because `.look` is `display:inline-block`.

## English

Wrap example sentences in `<p class="en">`. Do not hyphenate.

## Emphasis

- 700 for Chinese headings and judge/choose stems.
- Amber (`#d97706`) for cover kicker, 4px bar, progress, 看对照, catalog link, and well verbs.

## Banned

- Soft Signal Zhuque Fangsong as the deck world.
- Function Journey Songti / terracotta paper as the deck world.
- Apple gray / black / `#0071e3`.
- Google Fonts CDN.
- `font-style: italic` anywhere on the deck.
- Student-visible words: MBTI, 功能, 类型, 八维.
- Copying a reference's 26px slide-title onto a 2-block teach scene (empty lower half).
