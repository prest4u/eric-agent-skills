# Five scenes

One product grammar. The scene changes when the job changes. Distinguish scenes by **alignment × carrier**, not by a new theme color. All scenes share stone paper `#fafaf9`.

Projection: 1920×1080 and 1280×720. One scene fills the viewport. No page scroll.

Shared chrome: 3px `--accent` amber progress; 56px footer (目录 · 上一拍 | `#pos` | 空格继续). Catalog link is amber.

Kicker on teach / judge / rewrite / choose sits outside `[data-beat]` and stays on as the scene enters. Cover / close kicker is beat 0.

Student-visible kickers:

| data-scene | Kicker |
|---|---|
| cover | series name, or 这一册 / 课上到这儿 |
| teach | 先把这条看清 |
| judge | 判断这一句 |
| rewrite | 改这一句 |
| choose | 选一个 |

## Spacing (multiples of 8)

See [design-system.md](design-system.md). Default scene padding is `48px 64px 96px`. Header kicker sits on a 1.5px rule. Title → first block `20px`. Sibling blocks `16px`. Content is full inner width.

Teach / rewrite: kicker top, single example well `flex: 1` in leftover height. Judge / choose: kicker top, remaining beats optically centered as one mass.

## 1. 封面 / 收束

Job: announce the Stage, or send students to paper.

Composition: centered cluster from the reviewed classroom cover grammar. Amber 14px kicker, 700 title, `48×4` amber bar, then lead. Max width `1160px`. Stone `#fafaf9`. Optical lift `margin-top: -32px`.

Type: title `clamp(56px, 6.2vw, 92px)` / 700 / −0.03em. Lead `clamp(18px, 1.7vw, 20px)` `--faint`. Two-line Chinese covers need the 92px cap — their 「第5课」 is 64px for three characters.

Beats: kicker + h1 + rule-mark first; lead second. Keep the `<br>` in the title. Do not put a syllabus of later Stages on the cover.

## 2. 讲规则

Job: one knowledge point, then **one** example of that point.

Composition: full inner width. Header kicker on a hairline. h2 is a **slide title**, not a billboard. White rule card, then an amber highlight well that **fills leftover viewport** on single-example scenes (`flex: 1`, padding `48px 56px`, English `clamp(36px, 3.8vw, 56px)`). Why is an amber left-bar note, full width, under the well.

Stacked tense scenes (`.example.form`): keep wells compact (`min-height: 176px`, English `clamp(26px, 2.6vw, 36px)`), top-aligned, so three forms + why occupy the wall without scrolling.

Type: h2 `clamp(28px, 2.8vw, 40px)` / 700. Rule `clamp(20px, 2vw, 26px)`.

Beats: rule only; then the example (看对照 rides with the well); then why for that sentence only. Tense scenes may add `.example.form` wells on later beats.

Sense-verb recognition uses the same scene. 看对照 is a pill with `--accent` type and `#fde68a` hairline, not a solid amber fill, and must not stretch full-well width.

## 3. 判断一题

Job: one sentence, one judgment.

Composition: header kicker, then a vertically centered mass: 700 sentence + full-width chip row. `.chips.two` / `.chips.three` are `1fr` grids, chip min-height `96px`. Why is the amber left-bar note, full width, under the chips.

Type: sentence `clamp(44px, 5vw, 68px)` / 700. Chips `clamp(20px, 2vw, 26px)` / 600.

Beats: sentence; chips; why. Chip states: picked / ok / no change color only (150ms). Wrong uses `--no` / `--no-fill`, not opacity.

## 4. 改写 / 改错

Job: one source sentence, one rewrite or one repair.

Composition: same full-width column as teach. Highlight well first, `flex: 1`, padding `40px 48px`, so the source sentence is the hero rectangle. Prompt is bare type under the well. Why is the amber left-bar note.

Type: source `clamp(32px, 3.6vw, 52px)` / 600. Prompt 20–24px / 500. Model line inside `.why` is 18–22px / 600.

Beats: well; prompt; model + `.gap-note`.

## 5. 四框选择

Job: one stem, four equal tiles, then this item's reason.

Composition: full inner width. Stem + 2×2 tiles optically centered under the header. `.choices` is `1fr 1fr`, gap `16px`. Tiles min-height `112px`, left-aligned text.

Type: stem `clamp(32px, 3.4vw, 48px)` / 700. Tiles same as chips, `--r-md` + `--shadow-card`.

Beats: stem; four tiles; why.

## Overflow protocol

No vertical scrollbar. If locked type + locked padding overflow, compress spacing. Do not cut copy, do not add color, do not `scale`.

1. **1080p stacked wells** (tense teach last beat): adjacent wells, and well → why, use `16px`. Wells live in separate `[data-beat]` nodes — use `[data-beat]:has(.example) + [data-beat]:has(.example) .example`. Do not write `.example + .example`.
2. **Short height** (`max-height: 800px`, including 1280×720): scene padding `32px 40px 80px`; kicker→title `16px`; title→first `16px`; stacked-well and well→why gaps `16px`; white card / well padding compressed. Keep single-well `flex: 1`. Drop stacked-well `min-height` only. Clamp type sizes do not change.
3. Never set `overflow: auto` on a scene to “fix” height. A source reference may scroll; this deck must not.

## Scene change test

From two meters, a new scene should read as a new job (centered 700 title + amber bar; full-width header+cards; centered sentence; well-first rewrite; 2×2 tiles) and still look like one classroom-slide product. Squint test: five 1920×1080 frames scaled to 320px wide, readable without the words.
