# Student Book Form DNA

Use this reference when Eric asks to absorb the form of a professional Level 1/student-book style PDF, or when a Chinese exam course should become a real student book rather than a worksheet pack.

This is an abstraction layer only. Never copy reference-book logos, brand names, passages, exercises, images, screenshots, or whole-page layouts. The inspected reference PDF was image-only/raster in structure; that is a warning, not a production model. Eric-designed output must keep instructional text, questions, answers, tables, captions, and blanks deterministic, selectable, searchable, and QA-able.

## Form Contract

The student-book form is not just color. It is a sequence of page roles:

1. **Photo-led article opener**
   - A dominant contextual visual anchors the page.
   - The opener visual is unique to this page role; do not reuse the cover image.
   - The title is large and editorial, with one clear accent hierarchy.
   - Paragraphs are lettered or grouped as reading flow, not scattered cards.
   - Keywords can be highlighted inside text; definitions belong in small footnotes or margin notes.
   - For Chinese exam grammar, this can become a concept opener built around an exam-sentence problem, a clause story, or a long-sentence scenario.

2. **White article / inset evidence page**
   - Mostly white editorial page with a map, diagram, or inset image.
   - The visual is evidence/context, not decoration.
   - If the page uses an image, it must be a separate evidence/context asset rather than the cover or opener image.
   - Use for long-sentence annotation, clause-boundary pages, or reading-to-grammar transfer.

3. **Comprehension / check page**
   - Yellow or warm section ribbon at the top.
   - Exercise sections use A/B/C rhythm.
   - Left micro-labels name the cognitive move: main idea, inference, detail, categorizing; for grammar use 位置, 缺成分, 逻辑, 回填.
   - MCQ, short answer, and small tables can coexist, but must not become UI/dashboard cards.

4. **Skill / method page**
   - A compact concept box states the method.
   - A model sentence or short excerpt immediately demonstrates it.
   - Guided questions or a small transfer strip close the page.
   - For 高二升高三 grammar, method pages should translate teacher-internal scripts into visible student actions.

5. **Vocabulary / grammar practice page**
   - Section ribbon plus task sublabels: Completion, Words in Context, Collocations, Connector Bank, Clause Choice.
   - Word boxes are compact choice banks, not full writing lines.
   - Contextual margin image/cutout is allowed when it supports the task.
   - Margin/context visuals are one-use assets; repeated cover/opener imagery weakens the student-book rhythm.
   - All cloze blanks must use the blank baseline contract; literal underscores are blocked.

6. **Diagram / map / chart page**
   - A bounded thinking surface carries the structure: tree, grid, map, timeline, relationship chart.
   - Prompts around it are short and actionable.
   - Use for clause-boundary maps, 三栏判断表, logic relationship charts, or sentence-skeleton review.

7. **Video / task review page**
   - Top ribbon, short puzzle/check items, MCQs, critical-thinking strip, and vocabulary/review checklist.
   - Use for timed diagnostic, exam-paper mini simulation, or post-task reflection.

8. **Back-matter lookup page**
   - Micro-section labels and dense lookup rows.
   - Glossary/index tables are compact and quiet.
   - Use for grammar handbook, connector index, answer-key navigation, or clause-type lookup.

9. **Self-study reference / learning handbook page**
   - Use when Eric asks for a student hand-held self-study manual rather than a workbook.
   - The page must teach one learnable point through explanation blocks, short examples, a compact rule/table, a small quick check, and a remember strip.
   - Practice lines may appear, but they cannot be the page identity. Do not let the handbook become a planner, log, checklist run, or homework workbook with a nicer cover.
   - For IELTS first-week materials, reference pages should answer "what should I understand before doing the class task?" Examples: listening answer type, speaking answer expansion, sentence core, TRUE/FALSE/NOT GIVEN evidence, accurate sentence core, and useful chunks.

10. **Reference-book explanation/practice pair**
   - Use when Eric cites Cambridge, English Vocabulary in Use, English Grammar in Use, National Geographic, GIC, or similar professional books.
   - Transfer the abstract rhythm only: reference/explanation first, matching exercise next, A/B/C section labels, compact rule or vocabulary tables, controlled-to-personal exercise progression, and real-world context visuals when they carry meaning.
   - On A4, treat the pair as consecutive pages rather than forcing a book-trim spread. A good pair follows Know -> See -> Try -> Use.
   - Never copy brand marks, original passages, exercises, images, screenshots, or exact page layouts from the reference books.

## Chinese Exam Grammar Mapping

For 中高考 / 高二升高三 grammar lessons, map source blocks this way:

| Source teaching block | Student-book page form |
| --- | --- |
| Lesson route / timing | title-navigation or contents route; no visible production wording |
| Quick diagnostic | comprehension/check page with A/B sections and cognitive labels |
| Core grammar model | skill/method page plus diagram/map page |
| Think-aloud | model sentence page with worked annotation and student record rows |
| Classified drill | vocabulary/grammar practice page with word box and compact taxonomy |
| Mixed timed drill | task review page with score/check table and short reflection |
| Reading long sentence | white article / inset evidence page with deterministic annotation |
| Writing correction | workbook-practice or writing planner surface |
| Personal rule summary | back-matter lookup page or handbook mini rules |

Visible copy must not say route, 主动作, 维修, 后台, 闭环, validator, or other production words. Use student-facing phrasing such as 本页要完成, 判断顺序, 证据, 回填检查, 易错提醒, 复盘记录.

## Distinctive Components

These components may appear in `pages/*.md` frontmatter or renderer data when a project needs student-book form:

- `section-ribbon`: top page label for reading, vocabulary, grammar, review, or handbook sections.
- `skill-side-label`: small left label naming the cognitive move.
- `article-title-lockup`: large editorial title plus subtitle/category.
- `lettered-paragraph`: A/B/C paragraph flow for reading or concept story.
- `vocab-highlight`: deterministic inline keyword highlight, never baked into an image.
- `definition-footnote`: compact explanation line near passage text.
- `guided-mcq-set`: MCQ block with task label and stable answer spacing.
- `categorizing-chart`: small table for grouping evidence or errors.
- `critical-thinking-strip`: colored transfer/reflection strip with short response lines.
- `diagram-callout`: labeled structure diagram or sentence map.
- `practice-word-box`: compact no-wrap choice bank.
- `study-reference`: self-study explanation page with rule blocks, examples, a compact table, quick check, and remember strip; required when the artifact is a learning handbook rather than only a workbook.
- `reference-practice-pair`: paired reference and exercise pages for Cambridge/In Use-style self-study grammar or vocabulary work; on A4 the pair can be sequential rather than side-by-side.
- `personal-output-box`: short transfer task where the student uses target language for their own speaking/writing answer.
- `unit-folio`: quiet page number/unit marker.

## Visual Acceptance

The contact sheet should show visible alternation among article/opener, skill/method, practice, diagram, review, and back-matter pages. A 10-page proof cannot receive a visual pass if most pages are only white question lists with different headings.

For a self-study learning handbook, the contact sheet must show repeated reference-book pages with real knowledge density. If most pages are writing records, planners, review logs, or form surfaces, mark `self-study-handbook-drift` and rebuild the page roles before visual scoring.

For Cambridge/In Use/National Geographic/GIC-inspired work, the contact sheet should show explanation/practice pairing, reference density, exercise progression, and context visuals where they are pedagogically needed. If the pages are merely prettier worksheets, mark `reference-book-dna-missing`; if the design shadows a named book too closely, mark `copycat-reference-book-risk`.

Reject with the named labels:

- `raster-book-drift`: text-heavy pages are exported as page images or body text is hidden in images.
- `article-form-missing`: an article/concept opener has a title but lacks an anchored visual/evidence field or paragraph rhythm.
- `skill-ribbon-missing`: skill/practice pages lack a clear ribbon/section marker and side cognitive labels when the page role calls for them.
- `exercise-taxonomy-flat`: practice pages are long numbered lists without A/B/C sections, word boxes, charts, or task-type contrast.
- `backmatter-index-weak`: handbook pages lack compact lookup rows or index-table rhythm.
- `self-study-handbook-drift`: a requested self-study handbook is mostly workbook/planner/log surfaces instead of teachable reference pages with explanations, examples, compact tables, and quick checks.
- `reference-book-dna-missing`: a requested Cambridge/In Use/NatGeo-style output lacks explanation/practice pairing, A/B/C rhythm, reference density, real context visuals, or controlled-to-personal exercise progression.
- `copycat-reference-book-risk`: an output copies protected reference-book brand, content, images, screenshots, exact spreads, or full-page layout instead of abstracting the grammar.

These labels are not cosmetic. They indicate the system is drifting back toward a worksheet/diagnostic packet instead of a student book.
