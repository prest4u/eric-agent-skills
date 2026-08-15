# Runtime Evidence

Use this only when the requested result depends on browser behavior or rendered output.

## Bind current evidence

Name the source/build identity, runtime command, loopback URL, route, viewport, state, and observation time that matter. Never mix screenshots or observations from another build. Bind servers to loopback unless external access is explicitly authorized.

## One combined BUILD check

Exercise the primary flow and the states required by the request. Check:

- no blocking overflow, clipping, overlap, hidden control, or unreadable text;
- responsive reflow rather than a scaled desktop canvas when mobile matters;
- semantic controls, accessible names, keyboard reachability, visible focus, and dialog focus return where applicable;
- understandable validation, error/retry, success, and non-color feedback;
- required fonts, icons, images, APIs, and resources;
- no blocking page, console, network, or resource error.

A screenshot proves pixels at one named state; it does not prove keyboard behavior or other states. DOM/accessibility inspection does not prove visual hierarchy. Source/build success does not prove served-current behavior. Use the evidence type that can falsify the acceptance criterion.

## PROOF and RELEASE

A proof inspects only its representative route/component/state. For RELEASE, inspect every journey/state/viewport made mandatory by the actual delivery contract against the frozen identity. Do not manufacture a coverage matrix for ordinary work or extrapolate an uninspected sample.
