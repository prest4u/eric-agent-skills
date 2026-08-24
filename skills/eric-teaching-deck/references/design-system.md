# Design system

Locked tokens and scene grammar for Eric Teaching Deck. Do not invent colors, radii, or faces outside this file.

The classroom product follows `EC-008-第5课-slides.html`: stone paper, amber accent, sans 700 titles, full-width cards. Paper Soft Signal (Zhuque Fangsong) stays on Typst.

## Color

| Token | Value | Use | Forbidden |
|---|---|---|---|
| `--bg` | `#fafaf9` | every scene canvas | a second color world |
| `--bg-soft` | `#f5f5f4` | idle exercise wash if needed | full-scene canvas |
| `--surface` | `#ffffff` | rule cards, chips, choice tiles | full-scene canvas |
| `--graphite` | `#fffbeb` | example / well (amber highlight, not a code block) | decorative type |
| `--ink` | `#1c1917` | titles and English stems | — |
| `--muted` | `#44403c` | rule body, why | stems |
| `--faint` | `#78716c` | header kicker, cover lead, footer mid | body |
| `--line` | `#e7e5e4` | hairlines, card borders | — |
| `--line-strong` | `#d6d3d1` | stronger card edge | — |
| `--accent` | `#d97706` | cover kicker, 4px divider, progress, 看对照, catalog link, well `<b>` | painting whole cards |
| `--accent-soft` | `#fffbeb` | picked chip, why fill | — |
| `--accent-line` | `#fde68a` | well / look / picked border | — |
| `--ok` | `#16a34a` | correct type and stroke | decoration |
| `--ok-fill` | `#f0fdf4` | correct fill | decoration |
| `--no` | `#dc2626` | wrong type and stroke | decoration |
| `--no-fill` | `#fef2f2` | wrong fill | decoration |

Do not add tokens. Do not keep `--snow`. No Apple blue, no black cover, no Function Journey terracotta as the theme.

## Radius / shadow

| Token | Value | Use |
|---|---|---|
| `--r-sm` | `6px` | micro |
| `--r-md` | `10px` | cards, wells, chips |
| `--r-lg` | `16px` | large panels |
| `--r-pill` | `100px` | 看对照, badges |
| `--shadow-card` | `0 1px 2px rgba(28,25,23,.04)` | cards |
| `--shadow-pop` | `0 4px 12px rgba(28,25,23,.06)` | catalog hover |

Cover divider is `48×4` `--accent`, radius `2px`.

Footer: `rgba(250,250,249,.94)` + `1.5px var(--line)`. Same on cover.

## Spacing (multiples of 8 only)

| Slot | Value |
|---|---|
| Scene padding | `48px 64px 96px` (footer 56px) |
| Header kicker | 12px padding-bottom + 1.5px rule, then 24px |
| Title → first block | `20px` |
| Sibling blocks | `16px` |
| White card padding | `32px 40px` |
| Single well padding | `48px 56px`; stacked tense wells `24px 32px` / min-height `176px` |
| Chip / choice | min-height `96px` / `112px`, padding `24px 32px` / `28px 32px` |
| Chip / choice gap | `16px` |
| Cover | centered cluster, max-width `1160px`, kicker→title `20px`, title→bar `24px`, bar→lead `24px`, optical lift `margin-top: -32px` |

Content is **full inner width**. Do not lock teach/rewrite/choose to 1080px — that leaves a dead column on a 1920 projector.

**Vertical mass (the thing that failed when only colors were swapped):**

- Cover / close: `justify-content: center`. Kicker + title + bar + lead are one glued cluster, not a title stuck at 16vh.
- Teach / rewrite: kicker stays top. Do **not** auto-center the leftover as a tiny island. Single-well scenes: `[data-beat].is-in:has(.example|.well)` is `flex: 1` so the amber well is the dominant rectangle in leftover height. Stacked `.form` wells stay compact and top-aligned.
- Judge / choose: kicker top; first/last `[data-beat]` use `margin-top/bottom: auto` so sentence+chips or stem+tiles sit as one mass in leftover height. Chips are full-width 2/3-col grids, not tiny pills.

## Type stack

```css
--font-sans: "PingFang SC", "Noto Sans SC", -apple-system, BlinkMacSystemFont,
             "Source Sans 3", sans-serif;
```

Titles **700** / tracking negative. Body 400. UI 600. No italic. No Songti / Fangsong on the deck.

See [type.md](type.md) for the per-role clamp table.

## New scene from a new item type

When a new item type needs a scene, pick one point on each axis. Do not invent a fourth color world.

| Axis | Allowed values |
|---|---|
| Paper | stone `#fafaf9` only |
| Alignment | left column (full width) or centered |
| Carrier | header+cards / highlight well / chip row / 2×2 tiles / bare cover cluster |

Only the **carrier** may be a new value. Two scenes must differ on at least two axes.

Current five:

| Scene | Paper | Alignment | Carrier | First read |
|---|---|---|---|---|
| cover | stone | center | kicker + 700 title + amber bar | title |
| teach | stone | left, full width | header + rule card + filling highlight well | example sentence |
| judge | stone | center | header rule + sentence + chips | English sentence |
| rewrite | stone | left, full width | highlight well first | source in the well |
| choose | stone | center, full width | 2×2 tiles | stem |

## Overflow protocol

No vertical scrollbar. If locked type + locked padding overflow, compress spacing — do not cut copy, do not add color, do not `scale` the scene.

1. **1080p stacked wells** (tense teach last beat): adjacent wells, and well → why, use `16px`. Wells live in separate `[data-beat]` nodes, so target `[data-beat]:has(.example) + [data-beat]:has(.example) .example`. Do not write `.example + .example`.
2. **Short height** (`max-height: 800px`, including 1280×720): scene padding `32px 40px 80px`; kicker→title `16px`; title→first `16px`; stacked-well and well→why gaps `16px`; card / well padding compressed (`16px 20px` / stacked `12px 20px`). Keep single-well `flex: 1` so the example still fills leftover height; only drop stacked-well `min-height`. Clamp type sizes do not change.
3. Never set `overflow: auto` on a scene to “fix” height. A source reference may scroll; this deck must not.
