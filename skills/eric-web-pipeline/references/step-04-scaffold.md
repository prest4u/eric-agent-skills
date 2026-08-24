# Step 4 · 项目骨架 — Scaffold, Design Tokens & Tooling

> 中文速览：搭一个能跑的最小骨架——仓库结构、设计 tokens（色/字/间距）、基础布局壳、开发脚本。本步的纪律：**骨架先跑起来，功能一行不写在前面**。config 折腾半天页面还是空白，是本步最典型的失败。

## When you're in this step · 判定信号

- `spec.md` 已就绪，但仓库是空的或缺基础设施；
- 改版项目：需要新增设计 tokens 或调整目录结构。

## Inputs · 进入条件

- `spec.md` + 技术选型（Step 2–3 产物）；
- 视觉方向已定的色彩/字体结论。

## Action checklist · 行动清单

1. **仓库与目录**：
   - [ ] 初始化项目（`npm create vite` / `npx create-next-app` / 静态目录），按 spec 的页面清单建路由占位；
   - [ ] 目录约定：`components/`、`pages|app/`、`styles/`、`public/assets/`、`lib/`（Path B 加 `server/` 或 `api/`）；
   - [ ] `.gitignore`、README 骨架（项目名、启动命令）。
2. **设计 tokens（本步最重要的产出）**：
   - [ ] CSS 变量或 Tailwind theme：主色/强调色/中性色阶、字体栈、字级阶梯、间距阶梯、圆角、阴影；
   - [ ] dark/light 模式策略（如需要）；
   - [ ] tokens 与 Step 2 的视觉方向一致——这是视觉品质的源头，随手填的色值会在 Step 7 还债。
3. **基础布局壳**：
   - [ ] 页面外壳：header/nav、footer、主内容区、容器宽度与网格；
   - [ ] 全局 reset/基础样式、字体加载（`font-display: swap`）、favicon 占位；
   - [ ] Path B：布局壳含认证态的 nav 切换占位。
4. **Tooling（最小集）**：
   - [ ] dev server 能跑、热更新正常；
   - [ ] 构建命令能出产物（`npm run build` 通过）；
   - [ ] lint/format 沿用生态默认（ESLint/Prettier），不自定义一堆规则。
5. **基础设施（Path B）**：
   - [ ] 数据库连接与迁移工具就位（先建连接，表结构在 Step 5 随功能建）；
   - [ ] 环境变量模板 `.env.example`（不写真实密钥）。
6. **验证骨架**：浏览器打开每个占位路由，确认不报错、布局壳渲染正常。

## Decision tables · 决策表

| 决策点 | 默认 | 备注 |
| --- | --- | --- |
| 样式方案 | 项目已有则沿用；新项目 Tailwind 或纯 CSS 变量 | 不混用两套体系 |
| tokens 载体 | CSS custom properties | 框架无关，Tailwind 项目映射进 theme |
| 图标 | Iconify 按需引入 | 不整包引入 |
| 目录深度 | 扁平优先 | 三层以内，不预先抽象 |

## Exit criteria · 出口质量门

- [ ] `dev` 与 `build` 命令都通过；
- [ ] 所有占位路由在浏览器渲染不报错（控制台零 error）；
- [ ] 设计 tokens 文件存在并被布局壳实际使用；
- [ ] （Path B）数据库可连接，`.env.example` 存在且无真实密钥。

## Common pitfalls · 常见坑

- **配置松鼠病**：折腾 webpack/biome/husky 两小时，页面还是空白——骨架以"能跑"为唯一标准；
- **tokens 后补**：先把颜色硬编码进组件，后期统一改成本巨大；
- **过度工程**：单页站引入状态管理库、monorepo、Docker——按 spec 规模匹配复杂度；
- **密钥入库**：`.env` 被 commit——`.gitignore` 和 `.env.example` 在第一天就配好。

## Route to existing skills · 路由

- `tailwindcss` — Tailwind 项目的 tokens 与惯例；
- `frontend-design` 的 Delivery Boundary Checkpoint（开工边界核对）；
- `beautiful-shadows`、`css-border-gradient` 等视觉原子 skill 留到 Step 7 用，本步只做 tokens。

## Output artifacts · 产出物

- 可运行的仓库骨架 + tokens 文件；
- progress 文件 Step 4 勾选，记录 dev/build 命令。

## Handoff · 衔接

- 骨架验证通过 → **Step 5 MVP**；
- Step 5 中发现缺基础能力（如需要富文本编辑器）→ 回本步补一项依赖，不开新坑。
