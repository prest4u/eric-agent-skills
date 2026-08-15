# Visual DNA schema

Record evidence, not adjectives. Each dimension needs an observable rule and its target-medium translation.

## Required dimensions

1. `visual_style`: editorial, interface-derived, photographic, diagrammatic, etc.
2. `component_structure`: foreground/midground/background and repeated modules.
3. `composition`: grid, anchors, asymmetry, negative space, reading order.
4. `shot_and_lens`: crop, scale, focal distance, or `not_applicable` for non-image systems.
5. `lighting`: direction, contrast, surface response, or `not_applicable`.
6. `color_science`: semantic roles, contrast, saturation, print behavior.
7. `medium_texture`: paper, grain, line, surface, border, shadow.
8. `mood`: concrete atmosphere produced by the rules above.
9. `rendering_feel`: crisp/soft, vector/raster, depth and sampling behavior.
10. `era_culture`: broad observable era cues without artist/studio identity.
11. `spatial_logic`: columns, layers, stage, perspective, and alignment.
12. `density_blank_space`: target density, breathing room, cluster rhythm.
13. `dynamic_state`: static emphasis, sequencing, motion, or print translation.
14. `post_processing`: grain, halftone, bloom, scan trace, or none.
15. `signature_traits`: reusable fingerprints that survive content replacement.

## Document extension

Also record:

- `information_hierarchy`: title, thesis, evidence, action, metadata.
- `pagination`: page roles, break rules, orphan control, numbering.
- `data_visualization`: chart palette, labeling, evidence hierarchy.
- `iconography`: stroke, size, optical weight, license.
- `accessibility`: minimum type, contrast, reading order, alt text.
- `medium_translation`: source pattern → document/web/slide/image behavior.

## Token groups

Use semantic names:

- color: `paper`, `ink`, `muted`, `accent`, `signal`, `hairline`
- type: `display`, `body`, `mono`, `label`, with size and leading scales
- space: `2xs` through `2xl`, plus page margins and column gaps
- geometry: radius, rule width, icon size, crop ratio
- elevation: print-safe border/shadow rules
- chart: categorical and emphasis colors
- motion: duration/easing only when the target supports motion

Do not encode a source brand name into a token.
