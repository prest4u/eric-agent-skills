# Direction pack schema

Create one `direction-pack.json` per project:

```json
{
  "schema_version": "1.0",
  "project": "Project name",
  "delivery_mode": "cinematic-journey | product-native-spatial",
  "product_truth": "What the product actually helps the user do",
  "frozen_semantics": ["Behavior or claim that must not change"],
  "references": [
    {
      "source": "path or URL",
      "rights": "user-owned | permissive | unverified",
      "adopt": ["observable rule"],
      "exclude": ["identity, asset, copy, or composition"]
    }
  ],
  "directions": [
    {
      "id": "direction-a",
      "name": "Short original title",
      "product_truth": "How this direction expresses the product truth",
      "thesis": "One-sentence visual thesis",
      "spatial_metaphor": "The project-specific spatial idea",
      "hero_subject": "What carries the visual attention",
      "media_strategy": "video | image-sequence | canvas | webgl | native-ui-motion",
      "materials": ["surface behavior", "secondary material"],
      "lighting": "Direction, contrast, memorable event",
      "color_roles": {
        "ground": "#...",
        "ink": "#...",
        "accent": "#...",
        "signal": "#..."
      },
      "typography": "Hierarchy, scale, density, and local/system font strategy",
      "storyboard": [
        {"progress": "0–12%", "scene": "Opening truth"},
        {"progress": "12–32%", "scene": "Approach"},
        {"progress": "32–55%", "scene": "Transformation"},
        {"progress": "55–76%", "scene": "Decision or reveal"},
        {"progress": "76–92%", "scene": "Resolve"},
        {"progress": "92–100%", "scene": "End state"}
      ],
      "interaction": "Scroll, direct manipulation, navigation, and state behavior",
      "responsive": "Independent mobile composition and stress behavior",
      "reduced_motion": "Equivalent static or stepped experience",
      "content_mapping": ["Product content → visual role"],
      "states": ["Loading/empty/withheld/error/success states that matter"],
      "exclusions": ["What this direction must not become"],
      "acceptance": ["Falsifiable visual/runtime check"],
      "prompt_pipeline": {
        "concept": "Path to or summary of the divergent concept prompt",
        "media_or_motion": "Path to the selected journey/proof prompt",
        "site_implementation": "Path to the selected site implementation prompt"
      },
      "transformation_axes": {
        "space": "unique summary",
        "material": "unique summary",
        "light": "unique summary",
        "motion": "unique summary",
        "type": "unique summary",
        "density": "unique summary",
        "interaction": "unique summary"
      }
    }
  ]
}
```

## Prompt construction

When an implementation task needs a design prompt, concatenate only:

1. product truth and frozen semantics;
2. the selected direction;
3. current project stack and reusable primitives;
4. explicit viewport/state/runtime acceptance;
5. permissions and exclusions.

Do not paste rejected directions, unrelated visual history, or other projects’ complete prompts into the implementation task.

## Selection record

`selection.md` must answer:

- Which direction was selected?
- What product truth does it express better?
- Which one representative proof will falsify it?
- Which alternatives were rejected, and for what concrete reason?
- What would force a direction change?

Do not use numeric aesthetic scoring as a substitute for judgment.
