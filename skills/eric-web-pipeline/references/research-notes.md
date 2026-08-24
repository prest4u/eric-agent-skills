# Research Notes · 调研笔记

> 中文速览：本文件记录 2025–2026 AI 辅助网页开发的主流流程研究结论，以及它们如何映射到本 skill 的 10 步流程和 Eric 本地已有的 skill 生态。仅供溯源，日常使用走 `SKILL.md`。

## 1. Spec-Driven Development (SDD) · 规格驱动开发

2025 年后 AI 编码的主流范式。核心主张：**先写清规格，再让 AI 实现**；spec 是人与 AI 的共同事实源（shared source of truth）。

- GitHub Spec Kit（2025-09 发布）：`/speckit.specify → /speckit.plan → /speckit.tasks → /speckit.analyze → /speckit.implement`，支持 13+ AI 编码助手，vendor 中立。
- AWS Kiro：把 SDD 直接集成进 IDE。
- OpenSpec：轻量替代，标准 YAML/JSON/Markdown，无外部服务依赖。

对本 skill 的映射：SDD 的 specify/plan/tasks 对应 **Step 1 (Brief) + Step 3 (Spec & Plan)**；implement 对应 **Step 4–7**；analyze 对应 **Step 8 (Verify)**。

来源：
- [Spec-Driven Development in 2025: Tools, Frameworks, Best Practices — marvinzhang.dev](https://marvinzhang.dev/blog/sdd-tools-practices)
- [A Spec-First Approach to AI-Native Engineering — Microsoft Developer](https://developer.microsoft.com/blog/spec-driven-development-ai-native-engineering/)
- [Spec-Driven Development with AI: Complete 2025 Guide — dplooy.com](https://www.dplooy.com/blog/spec-driven-development-with-ai-complete-2025-guide)
- [Spec-Driven AI Development — aroussi.com](https://aroussi.com/post/spec-driven-ai-development)

## 2. Agentic 工作流 · 工程化要点

生产级 agentic 工作流的共识结构（arXiv 2512.08769 及业界实践）：

1. 明确的任务契约（task contract）先行；
2. 分解为独立、可验证的工作流（workstreams）；
3. 制造者与评判者分离（making ≠ judging）；
4. 每个阶段有可观测的质量门（quality gates），不凭感觉交付；
5. 失败循环有界：同一方法失败两次就换路径，不空转。

对本 skill 的映射：任务契约 → Step 1；质量门 → 每个 step 文件的 Exit criteria；制造/评判分离 → Step 8–9 的独立 review。

来源：
- [A Practical Guide for Designing, Developing, and Deploying Production-Grade Agentic AI Workflows — arXiv](https://arxiv.org/html/2512.08769)
- [Weekly Research: AI-Assisted Development Landscape — GitHub DevExpGbb](https://github.com/DevExpGbb/vscode-ghcp-starter-kit/issues/10)

## 3. Web 技术共识（2025–2026）

- 渲染架构走向**混合模型**：边缘做路由/缓存，源站做重计算；静态优先、按需 SSR/ISR。
- 性能硬指标仍以 Core Web Vitals 为准（LCP / INP / CLS），见 Step 8 阈值表。

来源：[Web Development Best Practices 2025 — khacreationusa.com](https://khacreationusa.com/web-development-best-practices-2025-the-unified-field-of-performance-semantics-and-generative-intelligence/)

## 4. 本地 skill 生态映射（避免重复造轮子）

| 流程阶段 | 已有 skill | 本 pipeline 的角色 |
| --- | --- | --- |
| 设计方向 | `design-project-visual-directions`, `design-first-ui-prompting` | Step 2 路由过去 |
| 视觉/实现标准 | `frontend-design`, `eric-quality-sites`, `build-awwwards-quality-sites` | Step 5/7 路由过去 |
| 动效 | `gsap`, `animation-systems`, `cinematic-gsap-lenis-motion-system` | Step 7 路由过去 |
| 3D/WebGL | `threejs`, `webgl-landing-steering` 等 | Path C 路由过去 |
| 验证循环 | `adaptive-quality-loop`, `iterate-until-verified`, `eric-frontend-delivery` | Step 8 路由过去 |
| 安全 | `security-review` | Path B 的 Step 8 安全门 |
| 发布 | `publish-project-to-github`, `adaptive-quality-loop` (RELEASE) | Step 9 路由过去 |
| 图片素材 | `unsplash-asset-images`, `aura-asset-images` | Step 6 路由过去 |

**结论**：本 skill 只做流程编排、步骤追踪、细节清单与路由；各阶段的具体工艺标准以被路由的 skill 为准。
