# Step 2 · 调研与方向 — Research, Visual Direction & Tech Selection

> 中文速览：动手前把两件事定下来——**长什么样**（视觉方向、参考分析）和**用什么做**（技术选型、素材策略）。产出物是视觉方向结论和技术选型记录。原则：先沿用项目现有栈，新增依赖必须有明确收益。

## When you're in this step · 判定信号

- `brief.md` 已完成，但还没有确定视觉风格或技术栈；
- 用户发来参考网站/截图，说"像这种感觉"；
- 老项目改版：代码已存在，需要判断沿用还是替换现有方案。

## Inputs · 进入条件

- Step 1 的 `brief.md`（路径 A/B/C 已定）；
- 用户提供的参考资料（网站、截图、品牌指南），可有可无；
- 现有项目的 `package.json` / 框架结构（改版时）。

## Action checklist · 行动清单

### 视觉方向（所有路径）

- [ ] 收集 2–5 个参考（用户给的 + 主动找的），逐个记录：版式节奏、字体气质、色彩策略、动效风格、信息密度——**学其神，不抄其形**；
- [ ] 定一个明确的审美方向词（brutally minimal / editorial / retro-futuristic / luxury…），写进进度文件；
- [ ] 需要多方向对比时，生成 2–3 个候选方向让用户挑（路由 `design-project-visual-directions`）；
- [ ] 定 typography 策略：主字体 + 备选，遵守已有设计系统的字体约定（不替换品牌字体）。

### 技术选型（按路径）

- [ ] **检查现有项目依赖**（manifest、lockfile、相邻文件 import）——有现成方案一律复用；
- [ ] Path A：定静态 HTML/CSS/JS 还是框架（React/Next/Astro），动效库（GSAP/Lenis）按需；
- [ ] Path B：定全栈框架、数据库、ORM、认证方案、支付方案（见下表）；
- [ ] Path C：定 Three.js/WebGL 方案、性能预算（目标帧率、draw call 上限）；
- [ ] 每个新增依赖写一句理由（"收益 > 集成成本"），写不出的不加。

### 素材策略

- [ ] 列出所需素材清单：图片、视频、图标、字体、3D 模型；
- [ ] 每项定来源：真实拍摄 / AI 生成 / 素材站（Unsplash/Aura）/ 程序生成；
- [ ] 确认版权与授权风险，避免热链脆弱 URL。

## Decision tables · 决策表

**技术栈快速选型（无既有约束时的默认值）：**

| 场景 | 默认选择 | 何时换 |
| --- | --- | --- |
| 单页营销站 | 静态 HTML + Tailwind + GSAP | 需要 CMS/多页路由 → Astro |
| React 生态项目 | Next.js / 现有 Vite+React | 项目已有别的框架则沿用 |
| Web App 数据层 | Postgres + Prisma（或项目现有） | 轻量原型 → SQLite； realtime → Supabase |
| 认证 | Clerk / Auth.js / Supabase Auth | 内部工具可免认证 |
| 支付 | Stripe（国际）/ 微信支付+支付宝（国内） | 仅在 Step 5 Path B 需要时接入 |
| 3D 体验 | Three.js + React Three Fiber | 纯展示可用 CSS 3D |

**素材来源：**

| 素材 | 首选 | 备选 |
| --- | --- | --- |
| 照片/背景 | `unsplash-asset-images` / `aura-asset-images` skill | AI 生成 |
| 图标 | Iconify（`solar-duotone-bold` / `company-logos` skill） | 自绘 SVG |
| 字体 | Google Fonts / 品牌字体 | 系统字体栈（性能最优） |

## Exit criteria · 出口质量门

- [ ] 视觉方向词 + 参考分析已记录（每个参考至少 3 条具体观察）；
- [ ] 技术栈已冻结并写入进度文件，每个新依赖有理由；
- [ ] 素材清单与来源已定，版权风险已标注；
- [ ] 若生成了多个视觉方向，用户已选定其一。

## Common pitfalls · 常见坑

- **上来就装库**：没检查项目已有依赖就加新包（违反 AGENTS.md 第 10 条）；
- **参考抄袭**：复刻参考站的版式/文案/签名元素——只取节奏与气质；
- **方向漂移**：选了"极简"又忍不住加渐变和动画——选定后所有决策服务于该方向；
- **字体侵权/缺失**：商用项目用了未授权字体，或依赖用户机器没有的字体且无 fallback。

## Route to existing skills · 路由

- `design-project-visual-directions` — 生成并对比多个视觉方向；
- `design-first-ui-prompting` — 把方向写成结构化 UI 提示词；
- `unsplash-asset-images` / `aura-asset-images` — 图片素材选取；
- `webgl-landing-steering` — Path C 的 WebGL 方向权衡。

## Output artifacts · 产出物

- 视觉方向记录（可并入 `brief.md` 或单独的 `direction.md`）；
- 技术选型与依赖清单（写入 `web-dev-progress.md` 的 Step 2 备注）。

## Handoff · 衔接

- 方向与选型冻结 → **Step 3 Spec & Plan**；
- 做到 Step 5 发现选型不可行（如库不兼容）→ 回本步改选型并记录原因，不要带着错选型硬写。
