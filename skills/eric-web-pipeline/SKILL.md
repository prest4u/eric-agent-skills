---
name: eric-web-pipeline
description: "【网站流水线】Eric Web Pipeline — orchestrate AI-assisted website and web app development as a 10-step pipeline with step tracking, per-step detail checklists, quality gates, consulting-style project definition, and routing to specialized skills. Use whenever Eric asks to build, redesign, continue, debug, plan, or ship a website, landing page, portfolio, web app, or 3D/creative web experience — and whenever he asks 做网页、做网站、网站开发流程、现在第几步、网页项目进度、帮我规划网站、咨询、顾问, review 当前阶段, invokes $eric-web-pipeline, or wants to know which stage a web project is in and what to do next."
---

# Eric Web Pipeline · AI 网页开发十步流水线

One orchestration layer for every web project: know **which step you are on**, **what that step demands in detail**, and **which existing skill does the craft work**. This skill does not replace `frontend-design`, `eric-quality-sites`, `adaptive-quality-loop`, etc. — it sequences them.

## The 10 steps · 十步全景

| # | Step · 步骤 | Goal · 目标 | Key output · 关键产出 | Detail file |
| --- | --- | --- | --- | --- |
| 1 | Brief 需求锁定 | Lock deliverable, audience, observable done-criteria | `brief.md` | [step-01-brief](references/step-01-brief.md) |
| 2 | Research 调研 | Visual direction + frozen tech stack + asset strategy | direction & stack record | [step-02-research](references/step-02-research.md) |
| 3 | Spec & Plan 规格 | Pages, components, data model, task breakdown | `spec.md` | [step-03-spec-plan](references/step-03-spec-plan.md) |
| 4 | Scaffold 骨架 | Running skeleton + design tokens, zero features | runnable repo + tokens | [step-04-scaffold](references/step-04-scaffold.md) |
| 5 | MVP 核心实现 | Core flow works end to end (incl. backend for Path B) | working MVP | [step-05-mvp](references/step-05-mvp.md) |
| 6 | Content 内容素材 | Real copy/media/fonts in place, licensing clean | no placeholders left | [step-06-content](references/step-06-content.md) |
| 7 | Polish 视觉打磨 | Visual quality hard gate (Anthropic/Stripe bar) | polished pages + compare shots | [step-07-polish](references/step-07-polish.md) |
| 8 | Verify 全面 QA | Function/visual/a11y/perf/SEO/security evidence | QA evidence pack | [step-08-verify](references/step-08-verify.md) |
| 9 | Ship 发布 | Reviewed, deployed, monitored, rollback-ready | production URL + rollback plan | [step-09-ship](references/step-09-ship.md) |
| 10 | Iterate 迭代 | Feedback routed back into the right step | updated progress + metrics | [step-10-iterate](references/step-10-iterate.md) |

Research basis: [references/research-notes.md](references/research-notes.md) (SDD, agentic workflow sources).

## Consulting mode · 顾问模式

For planning conversations before (or about) a web project — "帮我规划一下"、"consulting"、开工前先聊聊——act as a consultant, not an implementer. Follow [references/consulting-mode.md](references/consulting-mode.md):

1. **Intake**: record the one-line ask; look up environmental facts yourself instead of asking.
2. **Grill**: run the pipeline question bank as a design tree, in frontier rounds with recommended answers — the questioning protocol follows the `grilling` skill (if `grilling` is active, run inside its framework).
3. **定案输出**: produce `brief.md` + `spec.md` skeleton + `web-dev-progress.md`.
4. **风险预判（项目特定）**: derive each stage's 2–4 most likely problems from Eric's actual answers — never a generic checklist.
5. **锚点设定**: freeze the four anchors (acceptance criteria verbatim, frozen boundaries, visual direction word, path variant) into the progress file.

Consulting writes no implementation code. Its outputs are the comparison baseline for every later stage review.

## Step tracking · 步骤追踪（核心约定）

1. **At the start of any web work**, read `web-dev-progress.md` in the project root to locate the current step. If it does not exist and this is a new project, create it from [templates/progress-tracker.md](templates/progress-tracker.md) during Step 1.
2. **Announce position**: begin each reply in a web project with one line, e.g. `▶ Step 5 · MVP 核心实现`.
3. **Update on completion**: the moment a step's exit criteria pass, tick it in `web-dev-progress.md` and record evidence (artifacts, screenshots, commands).
4. **Anchors are frozen**: the progress file's anchor section (验收标准 / 冻结边界 / 视觉方向词 / 路径变体) must never change silently — any change needs an explicit dated record (see consulting-mode's 纠偏协议).
5. The progress file is the cross-session memory of the pipeline — keep it truthful; a stale tracker is worse than none.

## Stage review · 阶段审查

At every step's exit (before ticking it), run the 5-minute review from [consulting-mode.md](references/consulting-mode.md): ① exit criteria with evidence, ② deviation against the anchors, ③ did this project's forecasted risks materialize? Record `pass` / `偏差-已纠` / `回退到 Step X` in the progress file. When Eric says "review 一下当前阶段", run exactly this protocol on the spot.

## How to enter the pipeline · 进入规则

- **New project** → Step 1, no exceptions. If Eric wants to talk it through first, run Consulting mode — its deliverables complete Steps 1–3.
- **Existing project, no tracker** → create `web-dev-progress.md`, reconstruct status from the repo (brief/spec/QA evidence present?), resume at the first incomplete step.
- **Small change fast lane · 快速通道** — do NOT run the full pipeline for: typo/copy/image swap (Step 6 → targeted Step 8 → 9), single-component tweak (Step 5/7 → affected Step 8 items → 9), bug fix (reproduce → fix → regression-check the affected gates). Record the jump in the tracker's 跳转记录.
- **Seismic change** (new feature with data/permissions, visual re-branding, pivot) → re-enter at Step 1 or 2 per the routing table in [step-10-iterate](references/step-10-iterate.md).

## Path variants · 路径变体

| Path | Applies to | Pipeline deltas |
| --- | --- | --- |
| **A** 营销/作品集站 | landing, portfolio, editorial | Light Step 3 (sections only), skip backend; weight on Steps 6–8 |
| **B** Web App | auth, database, payments | Full Step 3 data/API model; Step 5 backend sub-pipeline; Step 8 adds the `security-review` gate |
| **C** 3D/创意体验 | WebGL, scrollytelling, games | Steps 5/7 add performance budgets + degradation path; route to `threejs`/`gsap` family |

## Working rules · 工作纪律

- One step at a time; finish the current step's **exit criteria** before moving on. The detail file's `When you're in this step` section resolves ambiguity about where you are.
- The spec is the source of truth: code-vs-spec conflicts are resolved by updating the spec first (Step 3), never by silent drift.
- **Drift check at every step boundary**: compare current artifacts against the anchors (consulting-mode 漂移检测). On any drift signal, stop → surface it to Eric with evidence → 改锚点 or 回锚点 → record → continue.
- Quality evidence beats confidence: screenshots, command output, and measurements — never "looks fine" (see each step's exit criteria).
- Keep changes surgical; preserve unrelated config and dirty work (AGENTS.md output-first policy applies throughout).
- External/irreversible actions (deploy, push, payment config) require explicit user authority and a recovery path — see Step 9.

## Anti-patterns · 反模式

- Writing code before Step 1–3 produce `brief.md`/`spec.md` (new projects).
- Polishing visuals (Step 7 behavior) while core flow is still broken (Step 5).
- Declaring done without rendered-runtime evidence at desktop **and** mobile widths (Step 8).
- Duplicating craft standards here — route to the specialized skill instead of copying its content.
- Launching Chrome `.app` or `channel: "chrome"` for QA — forbidden; use Playwright headless shell (AGENTS.md §7).
- Letting `web-dev-progress.md` go stale across sessions — or editing anchors without a dated record.
- Risk-forecasting with generic items ("注意性能") — every forecast must trace to an actual answer from the Grill round.

## Skill routing map · 路由速查

| Need | Skill |
| --- | --- |
| Consulting / planning dialogue | [consulting-mode](references/consulting-mode.md) + `grilling` |
| Visual directions / UI prompts | `design-project-visual-directions`, `design-first-ui-prompting` |
| Implementation & visual standards | `frontend-design`, `eric-quality-sites`, `build-awwwards-quality-sites` |
| Motion | `gsap`, `animation-systems`, `cinematic-gsap-lenis-motion-system` |
| 3D/WebGL | `threejs`, `webgl-landing-steering` |
| Imagery | `unsplash-asset-images`, `aura-asset-images` |
| Copy de-AI pass (中文) | `huashu-proofreading`, `eric-teaching-polish` |
| Verification loops | `iterate-until-verified`, `eric-frontend-delivery`, `adaptive-quality-loop` |
| Security (Path B) | `security-review` |
| Publishing | `publish-project-to-github`, `adaptive-quality-loop` (RELEASE) |

## Distribution · 分发拓扑（唯一事实源）

The canonical editable source is the `eric-web-pipeline` directory in [`prest4u/eric-agent-skills`](https://github.com/prest4u/eric-agent-skills). Product-specific copies are installation surfaces, not authorities.

- Update the GitHub source first, pass repository validation, then use the repository sync command to reconcile local agents.
- Do not hand-edit a product-specific duplicate or create a second physical authority.
- Existing sessions may keep a frozen Skill snapshot; start a fresh session after synchronization when the updated listing or instructions are required.
