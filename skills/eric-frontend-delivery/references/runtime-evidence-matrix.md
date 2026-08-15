# Build-matched runtime evidence matrix

Create this matrix after Q2 and before Q3. Every row must name the same current build identity.

Record Q3 `reviewer_provenance` as `same_agent`, `independent_agent`, or `eric`. It identifies the rendered recheck operator only; Q4 still requires its separate fresh `eric-review` or Eric provenance for formal readiness.

| Surface | Minimum current evidence | Failure meaning |
| --- | --- | --- |
| Primary flow | Start-to-finish browser interaction, transitions, recovery, and outcome | Missing mandatory runtime evidence or observed flow blocker |
| Desktop | Declared desktop viewport plus applicable pointer/keyboard states | No formal responsive closeout without current evidence |
| Mobile | Declared mobile viewport plus touch/reflow/text-fit evidence | Missing mobile coverage blocks formal delivery |
| Edge viewport | Each declared breakpoint where composition changes | Unverified declared support remains an evidence gap |
| States | Every applicable default/loading/empty/disabled/validation/error/retry/success/focus/modal/menu state | Missing declared state blocks formal delivery |
| Accessibility basics | Keyboard order/reachability, visible focus, names/labels, semantics, basic contrast/non-color cues | Record observed defect or route deeper audit; do not claim compliance |
| Resources | Assets/fonts/media/network and delivery-breaking console errors | Broken required resource is a release blocker |
| Visual delivery | `HTML-G1`, `HTML-G2`, and `HTML-G3` from the canonical visual review | Machine checks cannot substitute for this rendered review |

Use current screenshots, DOM/accessibility observations, interaction traces, and commands as evidence locators. A screenshot cannot prove keyboard or semantic behavior. An automated test cannot prove the pixels are correct. If source identity, build identity, runtime, or evidence freshness differs, rebuild the matrix instead of merging versions.

The packet validator treats every JSON string as malformed/untrusted. Runtime URLs fail closed on raw C0/DEL, scheme, authority, host, port, and the explicit loopback contract. It does not claim to model undeclared theoretical URL transformations.
