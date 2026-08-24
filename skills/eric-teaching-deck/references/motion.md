# Motion

Motion is punctuation. It marks a new beat. It does not entertain between sentences.

## Local GSAP

Copy `gsap.min.js` into `web/vendor/`. Load it with a relative script tag:

```html
<script src="vendor/gsap.min.js"></script>
<script src="js/deck.js"></script>
```

Do not use a CDN, jsDelivr, unpkg, esm.sh, or an npm bundler. The class machine may have no network.

Current vendored build: GSAP 3.x min file. When refreshing, download the min file once, replace `vendor/gsap.min.js`, and keep the page tags the same.

## Timeline on a beat

`js/deck.js` owns one timeline at a time.

1. Kill the previous timeline before starting a new beat.
2. Animate the `[data-beat]` that just became current.
3. Duration **0.45–0.6s**. Current engine default **0.55s** is in range. Ease `power2.out`.
4. Prefer `autoAlpha` + a 10–12px `y` rise. No bounce, no elastic, no 3D spin, no Ken Burns on type.

Target spec allows a same-beat block stagger of 80ms (60ms on four-box tiles) **only if the engine animates children**. The current `deck.js` animates the whole `[data-beat]` as one tween (`y: 10`, `0.55s`). That is accepted. **Do not patch `deck.js` to add child stagger. Do not fake stagger with CSS** — mash-skip (`timeline.progress(1)`) cannot finish a CSS child animation.

## Skip

```js
if (timeline && timeline.isActive()) {
  timeline.progress(1);
  return;
}
```

That is the only skip. The next press walks the next beat.

## Reduced motion

```js
const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
```

If true, `gsap.set(beat, { autoAlpha: 1, y: 0 })` and do not create a timeline. The teacher still advances one beat at a time.

## Scene change

Changing `data-scene` may fade the whole scene 200–300ms. Do not crossfade two example sentences. The outgoing scene is gone before beat 0 of the incoming scene plays.

Chip / choice color states: `150ms` ease, no movement. Progress width: `200ms linear`. 看对照: contrast fades in; the button hides. None of these advance the deck.

## What not to animate

- The progress bar width may ease; it must not bounce.
- Footer chrome does not fade on every beat.
- Do not animate hyphenation, font-size, or layout reflow as the “motion system.”
- No autoplay. No loop. No particle field.

## Proof

In the browser, press space through a teach scene, a judge scene, and a four-box scene. Confirm: one entrance at a time; mash space during the tween snaps that tween; the explanation of item 2 never appears beside item 1.
