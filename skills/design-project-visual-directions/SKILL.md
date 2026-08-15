---
name: design-project-visual-directions
description: Generate, compare, select, and implement genuinely different visual-direction prompt packs for product websites and interactive surfaces. Use when Eric asks to brainstorm several design directions, create a project-specific visual language, translate cinematic or reference-derived principles without cloning, choose among visual concepts, or carry a chosen direction into a representative frontend proof.
---

# Design Project Visual Directions

Create a visual language from the product’s meaning, not from a reusable skin. A good result may inherit rhythm, depth, hierarchy, or motion principles from references, but it must change the spatial metaphor, material system, narrative cadence, and interaction model to fit the project.

## Required companion procedures

- When references, screenshots, videos, or prior candidates influence the work, use `fusion-visual-system` to inspect them, record rights, extract rules rather than identity, and name at least five transformations.
- When building a browser proof, use `frontend-design` and `eric-frontend-delivery`. Inspect the real runtime; source and build success alone are insufficient.
- Read [prompt-pack-schema.md](references/prompt-pack-schema.md) before generating directions.
- For a cinematic journey, completely read [cinematic-prompt-pipeline.md](references/cinematic-prompt-pipeline.md). Keep its three prompts separate until a direction is selected.
- Read [project-archetypes.md](references/project-archetypes.md) only for the relevant product archetype. Treat its seeds as starting points, never templates.

## Workflow

### 1. Lock product truth

Record:

- primary user outcome and audience;
- current surface, stack, and project-native components/tokens;
- semantics that must not change;
- frozen artifacts and evidence;
- data, scoring, recommendation, identity, payment, publication, and external-action boundaries;
- the specific visual or interaction gap being closed.

Do not invent a brand, product claim, persona, research result, or real-world validation.

### 2. Inspect evidence

Inspect the actual runtime and every visual reference used. Separate:

- product-owned material;
- permissively licensed material;
- unverified discovery references;
- failed or rejected candidates.

Rejected candidates are negative evidence, not style sources. Unknown-license assets may inform discovery only; adopt no code, imagery, copy, fonts, or distinctive composition from them.

### 3. Generate a direction pack

Generate exactly three directions by default. Use four only when a real product uncertainty demands it.

Each direction must:

- express the same product truth through a different spatial metaphor;
- define a distinct hero subject, material/light system, composition, typography, motion grammar, interaction model, and responsive strategy;
- map real product content and states into the visual system;
- include a six-beat storyboard and falsifiable acceptance checks;
- state what it excludes and what must not be inferred.

Pairwise diversity must differ on at least five axes:

1. space/composition;
2. material/surface;
3. lighting/color behavior;
4. motion/scroll cadence;
5. typography/hierarchy;
6. density/content grouping;
7. interaction/navigation.

Changing only palette, copy, or decorative objects is invalid. Do not default every project to glass prisms, dark cinematic rooms, orbital globes, cards floating in space, or scroll-video.

For cinematic sites, first generate a wide concept field, then select three candidates. Do not ask an implementation agent to invent the concept, media, and website simultaneously. The creative media or scene system carries the experience; the interface frames and navigates it.

Write `direction-pack.json`, then run:

```bash
python3 scripts/validate_direction_pack.py direction-pack.json
```

Fix structural or diversity failures before presenting or implementing a direction.

### 4. Select with a proof

If Eric delegates product-direction judgment, select the strongest direction and explain the decisive product fit in one paragraph. Otherwise present the three directions with one recommended choice.

Build only one representative proof: one route, chapter transition, critical state, or hero-to-decision sequence. Do not build three complete websites.

For a cinematic journey, the proof must exercise the selected media or motion strategy. A page shell around weak placeholder media is not a valid proof. If paid or licensed media generation is unavailable, produce an honest local motion study and label the missing media gate; do not claim it matches a generated film.

Judge the proof on:

- product meaning and comprehension;
- visual distinction and compositional force;
- material/light credibility;
- motion continuity and interaction clarity;
- mobile translation rather than desktop scaling;
- reduced-motion equivalence;
- runtime health and performance budget;
- originality and project-native fit.

Reject a technically functional proof that still looks like a generic shader, template, motion study, or reference clone.

### 5. Run the selected prompt pipeline

For a cinematic direction, keep three artifacts:

1. divergent concept prompt and selected concept;
2. concept-to-journey prompt with camera, physics, light, parallax, timing, reverse-scrub behavior, and media requirements;
3. journey-to-site prompt containing the selected asset identity, original concept, product semantics, scroll mapping, chapters, controls, responsive states, reduced motion, and runtime gates.

Verify the asset’s real frame rate and dimensions. Do not claim interpolation, 60fps, seamless reverse playback, or production readiness without media and runtime evidence.

For a product UI that does not benefit from a continuous cinematic asset, preserve the same reasoning sequence but replace the media prompt with a project-native spatial/interaction proof. Never force a landing-page film grammar onto a decision tool, evidence instrument, editorial product, or game.

### 6. Expand the selected language

After the proof passes:

- extend project-native tokens instead of replacing them;
- map loading, empty, withheld, error, success, keyboard, focus, menu, and mobile states that affect the primary flow;
- preserve product semantics and permissions;
- use one dominant visual gesture per chapter or state;
- keep text and controls legible over visual spectacle.

For a substantial whole-screen, shared-UI, or critical-interaction change, freeze the affected candidate and obtain one fresh independent review before declaring it ready.

### 7. Deliver durable outputs

Return:

- `direction-pack.json`;
- `selection.md` with selected direction, rejected alternatives, and decisive evidence;
- the three selected-direction prompt artifacts when cinematic mode is used;
- representative proof URL and source identity;
- applicable desktop, mobile, stress, interaction, reduced-motion, console, and build evidence;
- `visual-dna.md` containing the 15 `fusion-visual-system` dimensions, semantic tokens, at least five mandatory transformations, and non-transferable elements.

Never publish, deploy, log in, use paid generation, contact people, or introduce real data without separate authority.
