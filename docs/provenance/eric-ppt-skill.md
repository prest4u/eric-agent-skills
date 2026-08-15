# Eric PPT Skill provenance boundary

## Included

- Eric's adapted workflow, design-system references, tests, and safety rules.
- MIT-authored material derived from `jinwyp/open-ppt-skill`, pinned in
  `catalog/upstreams.lock.json` at commit
  `07eeaadcb04c32c9adb107eb5c8608e6be4e1008`.
- The upstream MIT notice, retained verbatim in
  `skills/eric-ppt-skill/LICENSE`.
- `scripts/portable_ooxml.py`, a repository-owned implementation that writes
  editable OOXML using Python's standard library and PyYAML.

## Explicitly excluded

- The upstream `editor/neo-ppt/` snapshot and other mirrored Kimi product UI.
- Patched or extracted product WASM binaries.
- Fonts, icons, screenshots, templates, and other binary assets that lack a
  separate redistribution license and source record.

## Decision evidence

The pinned upstream describes itself as an unofficial reverse-engineered
implementation and identifies its editor directory as a mirror of a product
frontend. Its repository-level MIT license establishes rights for the author's
own contributions, but it does not establish ownership of every mirrored
third-party binary. Moonshot's published service terms reserve rights in Kimi
software and related components. No separate redistribution grant for the
mirrored Slides frontend was found during the release audit.

Primary references:

- Upstream source: <https://github.com/jinwyp/open-ppt-skill/tree/07eeaadcb04c32c9adb107eb5c8608e6be4e1008>
- Upstream license: <https://github.com/jinwyp/open-ppt-skill/blob/07eeaadcb04c32c9adb107eb5c8608e6be4e1008/LICENSE>
- Moonshot/Kimi terms: <https://www.kimi.com/user/agreement/en/modelUse>

This is a conservative release-engineering boundary, not a legal opinion. Any
future proposal to add excluded assets must include asset-level provenance,
redistribution terms, hashes, and an independent license review.
