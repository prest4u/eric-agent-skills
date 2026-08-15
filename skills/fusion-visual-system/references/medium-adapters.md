# Medium adapters

## Document / PDF

- Preserve the project-native HTML/CSS or Typst pipeline.
- Translate responsive grids into fixed A4 columns and page-role variants.
- Translate cards into information bands, evidence matrices, side notes, comparison fields, or action strips.
- Translate hover/animation into type, color, position, sequence, or repeated static states.
- Use local SVG/PNG assets; block external runtime URLs.
- Declare `@page { size: A4; margin: 0; }`, explicit page dimensions, print color adjustment, and break rules.
- Render cover, first body, dense, and final pages; inspect the contact sheet.

## Web

- Use the existing project stack. For a new React/Tailwind project, prefer open-code primitives such as shadcn/ui, Lucide, and restrained motion.
- Keep design tokens in the project-native system and preserve accessibility states.
- Vendor only the components actually used; retain their notices.
- Test mobile overflow, keyboard navigation, reduced motion, and production build.

## Slides / Keynote

- Convert page roles into master layouts and safe zones.
- Export diagrams/icons as layered SVG where possible.
- Rebuild motion natively with appear/build, Magic Move, emphasis, and path animation; HTML motion does not become editable Keynote animation automatically.
- Keep a motion cue sheet with object, trigger, duration, easing, and sequence.

## Image prompt

- Require an inspected visual reference.
- Preserve composition, lens, lighting, palette, texture, density, motion, and post-processing.
- Remove the original subject, private people, IP, brands, readable text, exact places, artist/studio names, and plot events.
- Use exactly one replaceable subject placeholder for reusable extraction prompts.
