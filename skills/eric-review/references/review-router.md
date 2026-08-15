# Review Router

Use only the smallest lens that can answer Eric's review question. Do not create an artifact-by-lens matrix or dispatch several reviewers for overlapping coverage.

| Artifact or question | Optional lens | Evidence that matters |
| --- | --- | --- |
| Code, config, API, dependency, tests | `code-review.md` | exact diff/version, nearby call sites, relevant tests/runtime |
| Interactive website or app | `ui-ux-review.md` | build-matched critical journey and required states/viewports |
| Lesson, worksheet, student/teacher pack | `teaching-review.md` | actual learner-facing artifact, source, timing and answer boundary |
| PDF, DOCX, slides, print/screen document | `visual-document-review.md` | current rendered pages/screens and delivery dimensions |
| Video script, title, cover, storyboard | `video-content-review.md` | exact text/frames/timestamps and stated audience |
| Rendered video | `video-qa` plus a content lens only if requested | frozen media, metadata, representative frames/playback |
| Security-sensitive change | `security-review` plus the owning code check | trust boundaries, exploit path, tests and recovery |
| Current/source-heavy claims | direct current-source verification; use `$eric-research` only when Eric separately invokes it | inspected current sources, conflicts, dates and support status |

QUICK_REVIEW normally uses one lens and reports only the verdict, blockers, key risks, and uninspected surface. REVIEW_AND_FIX uses the same agent and one recheck. FORMAL_SIGNOFF may combine mandatory domain evidence in one independent pass against the frozen identity.

For a mixed deliverable, inspect only the components required for the requested decision. Name any mandatory component not checked; do not infer a package pass from a sample.
