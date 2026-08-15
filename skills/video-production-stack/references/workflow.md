# Video Production Stack Workflow

## Purpose

Use this reference to decide which local skill should own the next action. The stack is not a replacement for the specialist skills; it is the traffic controller.

Before routing, confirm the project root, stage, required artifact, and output scope. If a route would install packages, render, download/upload assets, publish, push, delete, or mutate external systems, stop for explicit approval and use the specialist skill that owns that action.

## Default Production Chain

```text
idea / brief
-> script
-> video-spec.md
-> visual system
-> HyperFrames project
-> lint / validate / inspect
-> draft render
-> video-qa
-> eric-review
-> verification-log
```

## Multi-Version Chain

Use this when Eric asks for multiple visual directions, director styles, or A/B/C samples.

```text
version A plan
-> version A implementation
-> version A lint / validate / inspect / render / video-qa / eric-review
-> version A reusable lessons
-> version B plan
-> ...
```

Subagents can help with research and critique, but do not give several agents ownership of final video direction at the same time unless the versions are intentionally independent rough explorations. For refined samples, accumulated judgment from the previous render is part of the input to the next one.

## Skill Roles

| Skill | Owns | Does not own |
| --- | --- | --- |
| `video-director-spec` | Detailed pre-production spec, project root resolution, component contracts, asset gaps | Rendering or HTML implementation |
| `video-director` | Lightweight render-ready `video-spec.md` gate | Heavy project-specific planning |
| `huashu-script-polish` | Spoken Chinese script polish and pacing | Visual production or render QA |
| `huashu-design` | Visual identity, hero frame, HTML motion/design direction | Final MP4 technical QA |
| `hyperframes-producer` | Approved spec to HyperFrames implementation and render evidence | Re-inventing the creative brief |
| `hardware-profile` | Local machine defaults, workers, FFmpeg/HyperFrames paths | Creative decisions |
| `video-qa` | MP4/WebM probe, sampled frames, contact sheet, black/static checks | Content truth or philosophy quality |
| `eric-review` | Final multi-lens review of content, visuals, risks | Rendering mechanics |

## Choosing `video-director-spec` vs `video-director`

Use `video-director-spec` when:

- The project has existing docs, design rules, assets, or episode folders.
- The video needs scene component contracts, placeholders, or asset ownership.
- The topic is conceptually risky and needs boundaries.
- The user is planning a durable series or reusable template.

Use `video-director` when:

- The user needs a quick render-ready plan.
- The brief is simple and self-contained.
- There is no project-specific planning system.

## Required Evidence By Stage

| Stage | Minimum evidence before moving on |
| --- | --- |
| Script | `script.md` or approved narration text |
| Spec | `video-spec.md` with duration, ratio, fps, visual system, scene timings, asset statuses, QA expectations |
| Visual | `DESIGN.md`, visual grammar, or explicit style decisions |
| Production | HyperFrames project files and command notes |
| Pre-render | `lint`, `validate`, `inspect` results |
| Render | MP4/WebM path |
| QA | `video-qa-report.md` and `qa-frames/contact-sheet.png` |
| Review | `eric-review-report.md` or review notes with severities |

All evidence paths must live under the confirmed project or a temporary work directory, not inside a skill/plugin package or broad parent workspace.

## Failure Routing

| Problem | Route |
| --- | --- |
| Project root/spec/render is ambiguous | Stop and ask Eric to choose; do not continue by guessing |
| Vague idea | `video-director-spec` or `video-director` |
| Script too formal | `huashu-script-polish` |
| Generic/AI-looking visuals | `huashu-design` |
| Missing `DESIGN.md` before HTML | `huashu-design` |
| HyperFrames validation or layout problem | `hyperframes-producer` plus `hyperframes-cli` |
| Render succeeded but content might be black/static/wrong | `video-qa` |
| Video technically passes but feels wrong | `eric-review` |
| Asset rights/privacy unclear | Asset planning/review before production; mark blocker and fallback |
| External side effect requested | Owning specialist skill after explicit approval |

## Common Mistakes

- Starting HyperFrames from a rough idea instead of a spec.
- Running production commands before confirming project root and output scope.
- Treating `video-director` and `video-director-spec` as mandatory duplicates.
- Asking multiple agents to produce final-style video versions in parallel when the real need is sequential taste refinement.
- Rendering after `lint` but before `validate` and `inspect`.
- Calling a video done because the render command exited 0.
- Using `eric-review` before `video-qa` on a rendered artifact.
- Forgetting that `hardware-profile` is a local environment reference, not a creative authority.
- Treating installs, downloads, uploads, publishes, Git pushes, or account mutations as normal routing steps.
