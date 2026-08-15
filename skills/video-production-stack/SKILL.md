---
name: video-production-stack
description: Route a video project from its current artifact to the next visible result across planning, scripting, visual proof, implementation, rendering, QA, and release. Use only when the user explicitly invokes $video-production-stack for a video task; do not require the full production chain when one stage is enough.
---

# Video Production Stack

Move the video one visible stage forward. Start from the artifact that exists, produce the smallest useful next artifact, and verify that artifact before expanding scope.

Invoking this Skill does not authorize file writes, installs, downloads, paid generation, external account actions, publication, destructive replacement, subagents, or reviewers. Take an action only when the active request independently authorizes it. Never spawn agents as a side effect of this workflow.

## Resolve the current stage

Identify the project root, current source artifact, requested result, and safe output location from the request and workspace. Preserve unrelated files and existing renders. Ask only when competing project roots, source files, or output targets would materially change the result.

Do not manufacture a complete spec, visual system, implementation, render, QA packet, and release process when the user asked for only one of them.

| Current need | Route |
| --- | --- |
| Idea, plan, script, storyboard, shot list, or render-ready brief | Work directly and read `references/preproduction.md` only for the needed planning depth. |
| Spoken script is stiff, unclear, or hard to record | Read `references/spoken-script.md` and revise only the authorized scope. |
| Public video URL, subtitles, or source-video analysis | Invoke `$eric-reach` for read-only acquisition and faithful analysis, then transform the evidence locally. |
| Hero frame, scene proof, or new raster visual asset | Build the cheapest useful proof; invoke `$imagegen` only when an AI-generated bitmap is actually needed. |
| HyperFrames composition or render | Invoke `$hyperframes` for composition authoring and `$hyperframes-cli` for project, validation, inspection, preview, or render commands. |
| Remotion composition or render | Invoke `$remotion-best-practices` as the router; use `$remotion-create` for a new project and `$remotion-render` for export when those stages apply. |
| Rendered MP4/WebM inspection or suspicious output | Invoke `$video-qa` against the exact media file. |
| Public or formal release | Freeze the chosen render, run `$video-qa`, close rights/privacy issues, and publish or send only with separate explicit authority. |

Use only routes available in the current host. If a named dependency is unavailable, continue locally when the stage is still safely achievable or report the exact missing dependency. Do not substitute archived names or invent tool calls.

For a standalone installation, the pinned Remotion guidance is available locally under `references/upstream/`: read `remotion-best-practices/SKILL.md` first, then `remotion-create`, `remotion-captions`, or `remotion-multimedia` only when that stage applies. A host-installed Remotion Skill may be used instead when it is available and the user wants the installed version. Never fetch unpinned workflow text during production.

## Produce the next visible artifact

1. Choose one stage that owns the requested result.
2. Create or update its visible artifact: script, storyboard, `video-spec.md`, hero frame, scene proof, composition, draft render, final render, or QA report.
3. Run the smallest check that could falsify that stage.
4. Fix an ordinary failure in the same task and rerun the same check.
5. Stop when the requested stage is complete; continue to another stage only when the request requires it.

Use these stage checks:

- Plan or storyboard: timings add up, every scene has a viewer-facing payload, and missing assets have honest fallbacks.
- Spoken script: perform an aloud-readability pass; preserve facts, claims, quotations, and the author's intent.
- Visual proof: inspect the actual frame at the target aspect ratio and confirm it resolves the uncertain direction.
- HyperFrames: follow the invoked Skills and run the relevant project-native lint, validate, and inspect checks before render.
- Remotion: follow the invoked router and project conventions; preview the affected composition and run the relevant build/type checks before export.
- Render: verify the produced file and playback evidence; invoke `$video-qa` before calling a rendered deliverable complete.
- Release: verify the frozen render identity, intended platform output, asset rights, privacy, and generated-versus-archival labeling.

## Boundaries

- Prefer an existing project toolchain and visual system. Do not add a renderer or dependency merely because this Skill was invoked.
- Treat public source videos as evidence and inspiration, not a license to copy distinctive wording, footage, music, thumbnails, or creator identity.
- Keep generated or concept imagery distinguishable from archival or documentary evidence.
- Do not introduce cookie workflows, browser-profile extraction, external-download scripts, Gemini routes, paid APIs, persistent hardware assumptions, or obsolete Specialist Skills.
- Do not overwrite an existing spec, source asset, render, or QA folder silently. Use a new output path or obtain explicit replacement authority.
- A successful render command is not proof of visible or audible quality.

## Finish

Report the artifact path or identity, the check run and its result, and any real gap or integration dependency. For a public release, also state what was not published or sent unless that separate action was explicitly authorized and completed.
