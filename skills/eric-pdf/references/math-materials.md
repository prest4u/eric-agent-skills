# Eric PDF Math Materials

Use this reference when creating Eric-style math PDFs for middle-school entrance review, high-school entrance exam review, Gaokao review, or general math topic handbooks. Keep the Eric/Anthropic-light math style: A4, PingFang, warm ivory paper, clay functional emphasis, warm hairline tables, restrained boxes, spacious reasoning rhythm, and visual QA.

## Core Position

Math materials are not English handouts with different text. They need visible structures for:

- Concept entry: definition, formula, conditions, traps.
- Worked example: problem, diagram, key observation, step chain.
- Student workspace: enough blank/rule/grid area for real handwritten work.
- Variation training: one method across related problems.
- Scoring and feedback: points, common stuck steps, correction action.

The math design framework is:

1. **Concept entry**: one formula, theorem, or method boundary per warm formula box. Keep it bright and calm; never use dark theorem slabs.
2. **Condition map**: list known values, target, constraints, and required checks before calculation. This can be a small warm table beside a diagram.
3. **Worked example**: show the official-looking stem first, then key observation, then step chain. Do not bury the problem inside a decorative card.
4. **Student workspace**: give real ruled/grid/blank space immediately after the task, sized for handwritten math rather than visual balance alone.
5. **Error loop**: end a page or section with final-answer box, score/check table, or error log so the student knows what to correct.

Visual grammar for math:

- Formula boxes use pale peach/cream fills and clay titles; they should feel like clean editorial callouts, not warning panels.
- Example stems and diagram panels use warm paper cards with hairline borders; keep the panel quiet so formulas and diagrams remain the focus.
- Coordinate grids and geometry diagrams should use light warm grid lines with clay only for axes, auxiliary lines, or the one action students must notice.
- Workspaces stay mostly unfilled; the warmth comes from page color and line color, not shaded blocks.
- Avoid cool-toned table headers, cool-tinted note boxes, black theorem boxes, heavy ruled grids, and nested boxed explanations.

Default to a two-version system:

- **Student version**: shows concept, problem, hints, diagram, answer grid, workspace, and error log. It must not show full answers, scoring rubrics, teacher-only pacing, or hidden teaching language.
- **Teacher version**: shows everything in student version plus full solution steps, board-writing order, score points, common errors, and feedback notes.

Use an explicit `version: "student" | "teacher"` variable in demos or builders. Do not infer version from filename only.

## Topic Handbook Rhythm

Recommended order for a math topic textbook:

1. Cover: quiet identity, no visible page number.
2. How to use: how to read concepts, copy examples, complete workspace, and correct mistakes.
3. Topic map: concept, method, problem types, common errors.
4. Concept entry: formula/definition box, condition box, one short counterexample or trap.
5. Worked example: problem stem, diagram panel if needed, key observation, step table.
6. Student attempt: parallel problem with workspace and answer grid.
7. Variation set: 3-6 problems grouped by method, not by random difficulty.
8. Error log: wrong step, reason, correction action, next check.
9. Teacher appendix or teacher version: full solutions, score rubrics, board sequence.

## Problem-Type Page Grammar

Do not force all math problems into the same "example + solution table" layout. Choose the page grammar by the action students must perform.

| Problem type | Student action | Required components |
|---|---|---|
| 选择/填空 | identify condition, compute quickly, record answer | `eric-math-answer-grid`, short workspace, error log |
| 解答题流程 | write complete reasoning in order | `eric-math-large-question-table`, `eric-math-workspace`, `eric-math-final-answer-box` |
| 函数压轴 | transform conditions, classify cases, compare results | formula box, coordinate grid, large-question table, teacher score rubric |
| 导数大题 | definition domain, derivative, sign table, endpoint/stationary comparison | formula box, coordinate grid, large-question table, final answer box |
| 几何证明 | read diagram, mark known/target, write claim-reason chain | `eric-math-diagram-panel`, `eric-math-triangle-diagram`, `eric-math-known-target-table`, `eric-math-proof-table` |
| 应用/建模 | define variables, build equation/function, interpret answer | known-target table, diagram panel, workspace, final answer box |

For student versions, the page should make the next action obvious: mark the diagram, fill the known/target table, write the first transformation, or complete the final answer. For teacher versions, the same page can add solution steps, score points, and讲评 reminders.

## Middle School vs Gaokao

Middle-school entrance and Zhongkao math:

- Emphasize diagram reading, line/angle labeling, equation setup, unit conversion, and short step templates.
- Use `eric-math-diagram-panel` often, with a small "known / prove / find" table near it.
- Workspaces should be moderate: many problems need 4-8 lines rather than a full page.

High-school and Gaokao math:

- Emphasize condition transformation, function properties, derivative sign tables, sequence recursion, conic section coordinates, and proof chains.
- Use longer `eric-math-workspace` blocks and teacher-only `eric-math-step-table`.
- For large questions, split into "observation -> setup -> transformation -> conclusion" instead of dumping one long solution paragraph.

## Component Choices

- `eric-math-formula-box(title, formula, conditions, note: none)`: definitions, formulas, theorem cards, and method entry.
- `eric-math-example(no, title, body, tags: none, difficulty: none)`: official-looking example stem with metadata.
- `eric-math-step-table(body)`: teacher version solution steps: step, operation, reason, result.
- `eric-math-large-question-table(body)`: Gaokao-style flow table: phase, action, expression, conclusion.
- `eric-math-proof-table(body)`: geometry proof table: step, claim, reason, result.
- `eric-math-known-target-table(body)`: known/target/condition table for diagrams and proof problems.
- `eric-math-workspace(lines: 8, mode: "ruled", label: none)`: student handwritten area. Modes are `"ruled"`, `"grid"`, and `"blank"`.
- `eric-math-diagram-panel(title, body, note: none)`: standard area for coordinate systems, geometry diagrams, or embedded images.
- `eric-math-source-diagram(path, title: ..., width: ..., note: ...)`: source-accurate wrapper for original exam crops, GeoGebra exports, SVG/PDF/PNG figures, or verified external vector assets.
- `eric-math-diagram-needed(title: ..., note: ...)`: explicit placeholder when a complex figure is required but no verified source image/vector asset is available yet.
- `eric-math-coordinate-grid(..., axis-labels: true)`: quiet coordinate plane with emphasized axes and axis labels.
- `eric-math-triangle-diagram(a: [A], b: [B], c: [C], d: none, aux: none)`: simple schematic for teaching a triangle proof pattern only; not source-accurate and not suitable for complex geometry.
- `eric-math-answer-grid(kind: "mixed", count: 6)`: answer recording for choice, fill-in, or short-answer drills.
- `eric-math-final-answer-box(label: [最终答案], body: none)`: final conclusion area for written solution problems.
- `eric-math-score-rubric(body)`: teacher-only score points for solution problems.
- `eric-math-error-log(rows: 4)`: student correction table.
- `eric-math-solution-block(version: ..., title, teacher, student: ...)`: safe student/teacher switching. Prefer this over hand-writing `if version == "teacher"` around solution content.
- `eric-math-teacher-only` and `eric-math-student-only`: small visibility helpers for version-specific fragments.

## Formula And Diagram Rules

- Use Typst native math for formulas. Do not screenshot formulas.
- Use a three-tier diagram policy:
  1. **Source-bearing exam diagrams**: preserve the original crop or a verified GeoGebra/SVG/PDF export with `eric-math-source-diagram`. This is the default for real 中考/高考 geometry, analytic geometry, conic sections, folded shapes, shaded areas, or multi-object diagrams.
  2. **Simple teaching schematics**: use built-in Typst helpers only for blank coordinate grids, one-triangle proof patterns, basic auxiliary-line explanation, or non-scored visual scaffolds.
  3. **Missing/uncertain complex figures**: use `eric-math-diagram-needed` and stop for a verified figure source. Do not invent a complex geometry diagram from approximate hardcoded coordinates.
- Prefer simple Typst-drawn diagrams only for reusable standards: blank axes, one basic triangle, one auxiliary line, or labels that are not source-critical.
- Embed external images or vector exports for complex source-paper diagrams, and still place them inside `eric-math-diagram-panel` or `eric-math-source-diagram`.
- Leave enough whitespace around diagrams for handwritten marks after printing.
- Check long formulas visually; if a formula runs wide, split it into aligned lines or move explanatory text below it.
- For source-paper diagrams, never paste them naked into the page. Wrap them with title, note, and nearby known/target table so the page still has Eric PDF structure.
- Never claim a generated math figure is faithful unless it has been visually compared against the source or generated from a declared coordinate/vector source.

## QA Checklist

- Cover has no visible page number; first body page starts at 1.
- Student version has no full solutions, score rubrics, teacher notes, or hidden internal teaching terms.
- Student version does not show pages titled "教师解析", "评分点", "讲评", or "板书".
- Teacher version shows full solution steps and score rubrics.
- Formula boxes do not overflow.
- Workspaces have stable ruled/grid/blank area and do not collapse.
- Diagram panels have readable labels and no obvious overlap.
- Complex diagrams have a traceable source: original crop, GeoGebra file/export, SVG/PDF vector asset, or a written coordinate construction. Freehand model-drawn diagrams are not acceptable for scored geometry.
- Render diagram pages to PNG and inspect label collisions, clipped strokes, angle/arc placement, point labels, and whether the diagram still matches the problem statement.
- Error log has enough room for real correction, not tiny decorative rows.
