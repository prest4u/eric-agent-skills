# UI and UX Review Lens

Use for an existing website, app, form, onboarding, checkout, dashboard, or multi-step flow. Derive the exact build, critical journey, and supported states/viewports from the artifact and request; do not make Eric complete a preflight form.

## Checks

- Complete the critical journey, including validation, error, retry, success, cancel/back, and recovery states that apply.
- Check pointer and keyboard access, focus order/visibility, labels, error association, and essential non-color cues.
- Inspect the declared responsive viewports for clipping, overflow, order, reachability, and touch targets.
- Confirm users can tell where they are, what changed, what happens next, and whether destructive actions are clear.
- Check missing assets, fonts, network failures, and broken links when relevant.

Build-matched runtime interaction is stronger than screenshots; screenshots are stronger than source-only claims. Unit tests, snapshot hashes, source code, or old screenshots do not prove a visible critical journey by themselves.

For FORMAL_SIGNOFF, use `NOT READY` for a concrete P0/P1 and `INSUFFICIENT EVIDENCE` when a mandatory runtime gate cannot be checked. Use Playwright/browser evidence when the task authorizes it. Route code or security fixes to the owning workflow; do not activate an archived review Skill.

Do not claim backend correctness, security, performance capacity, or full accessibility compliance from UI inspection alone.
