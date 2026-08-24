# Teacher beats

The deck is a live class instrument. The teacher decides when the room sees the next move.

## Advance

These all mean “next beat”:

- Space
- Right arrow
- Click on empty paper

They do **not** mean “next item” if the current item still has a leftover beat.

## Do not steal the click

Clicks on these stay local:

- `.choice` / `.chip`
- `button.look`（看对照）
- `a`, footer nav buttons
- text inputs if a later Stage needs them

A local click may mark a chip. It must not reveal the next item, and it must not reveal every answer on the scene.

## Skip

If a beat is still tweening, the next advance call finishes that tween at once (`timeline.progress(1)`). It does not skip the beat. A second press is required for the next beat.

There is no “skip to answers” and no “show all items in this section.”

## Back

Left arrow (and an optional footer control) goes to the previous beat. If the scene is already on beat 0, go to the last beat of the previous scene. Back is instant; do not replay the entrance.

## 看对照

Only legal on the current item.

- The button lives inside the current `[data-beat]`.
- It reveals one contrast node for that item (`looks` + adjective vs `looked for`, or one wrong form vs one right form).
- It does not open a key, a table of pairs, or the next item.

If the contrast is itself a teaching beat, prefer a teacher advance over a button. Use the button when the teacher wants the option to linger on the first line.

## Reduced motion

If `prefers-reduced-motion: reduce`, set the current beat to its end state with no tween. Advance still walks one beat at a time.

## Scene load

Entering a scene shows only beat 0. Later `[data-beat]` nodes stay at `autoAlpha: 0` until their turn. Never paint a scene with every beat already visible and then “animate for show.”

## Forbidden patterns

- A slide that lists 5–10 stems.
- A toggle that reveals every answer on the page.
- Auto-advance on a timer.
- Swipe carousels that dump the next three items.
- Right-click context menus as the official advance (right **arrow** is the key).
