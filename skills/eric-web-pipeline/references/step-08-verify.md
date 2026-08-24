# Step 8 · 全面验证 — QA: Function, Visual, A11y, Performance, SEO & Security

> 中文速览：交付前的系统性检查——真实浏览器里按清单逐项过，用证据说话（截图/命令输出），不靠"我觉得没问题"。铁律：没看过的页面不算做完；每条验收标准都要有对应证据。

## When you're in this step · 判定信号

- 功能、内容、打磨都已完成，准备交付/发布前；
- 任何"差不多好了"的时刻——那就是该跑本步的时刻。

## Inputs · 进入条件

- Step 1 的验收标准清单（QA 的对照基准）；
- 可运行的完整站点（本地或 staging）。

## Action checklist · 行动清单

> 自动化 QA 遵守 macOS Chrome 禁令：用 Playwright `chromium.launch({ headless: true })`（chrome-headless-shell），**禁止**启动任何 Chrome.app、禁止 `channel: "chrome"`。详见 AGENTS.md 第 7 条。

### 1. 功能验证

- [ ] 主流程端到端走一遍（真实点击，不只读代码）：导航、表单提交、搜索、登录、支付（测试模式）；
- [ ] 三态实测：断网看 error 态、清数据看 empty 态、慢网看 loading 态；
- [ ] 边界输入：超长文本、特殊字符、空提交、重复提交；
- [ ] 控制台：零 error、零未处理 promise rejection（warning 逐条过目）。

### 2. 视觉与响应式

| 断点 | 宽度 | 必查项 |
| --- | --- | --- |
| 手机 | 375×812 | 无横向滚动、触控目标 ≥ 44px、文字不溢出 |
| 平板 | 768×1024 | 栅格过渡自然、无半吊子两栏 |
| 桌面 | 1440×900 | 主视口气质、容器线对齐 |
| 宽屏 | 1920×1080 | 内容区有最大宽度、不摊成一行 |

- [ ] 每个页面 × 每个断点截图存档；hover/focus 状态抽查；
- [ ] 暗色/亮色模式（如有）各过一遍；
- [ ] 全页截图技巧问题（懒加载/动画导致空白）路由 `stitched-full-page-capture`。

### 3. 无障碍（基础硬项）

- [ ] 键盘走查：Tab 顺序合理、焦点可见、无键盘陷阱、Esc 关弹层；
- [ ] 语义：标题层级不跳级、表单控件有 label、按钮是 `<button>` 不是 `<div>`；
- [ ] 对比度：正文 ≥ 4.5:1、大字 ≥ 3:1；
- [ ] `prefers-reduced-motion` 回退已生效；图片 alt 策略落实。

### 4. 性能

- [ ] Lighthouse（移动档）跑分，目标：Performance ≥ 90，且 Core Web Vitals 达标：

| 指标 | 达标线 |
| --- | --- |
| LCP | ≤ 2.5s |
| INP | ≤ 200ms |
| CLS | ≤ 0.1 |

- [ ] 资源审计：图片压缩与尺寸、未用的 JS/CSS、第三方脚本数量与加载方式；
- [ ] 动画/滚动页加测：DevTools Performance 录屏看长任务与掉帧；
- [ ] Path C：主场景帧率实测，DPR/纹理预算复核。

### 5. SEO 与元信息

- [ ] 每页唯一 title/description、canonical、og/twitter 卡片（用分享调试器预览一次）；
- [ ] `sitemap.xml`、`robots.txt`、favicon 全套、404 页面；
- [ ] 结构化数据（如适用）：Organization / Article / Product。

### 6. 安全（Path B 硬门，其余路径过基础项）

- [ ] 基础（所有路径）：无硬编码密钥、依赖无已知高危漏洞（`npm audit`）、表单有 CSRF/频率限制意识；
- [ ] Path B 对照 `security-review` 清单逐项过：注入、XSS、鉴权绕越、越权访问（水平/垂直）、支付 webhook 验签、敏感日志泄漏。

### 7. 构建与工程

- [ ] 生产构建通过（`build` + 类型检查 + lint）；
- [ ] 构建产物本地预览一次（`preview`/start），与 dev 表现一致。

## Exit criteria · 出口质量门

- [ ] Step 1 的每条验收标准都有对应证据（截图/命令输出/录屏）；
- [ ] 上述七个维度中适用项全部通过，不适用项标注原因；
- [ ] 发现的问题已修复并**回归复验**，或明确记录为已知限制。

## Common pitfalls · 常见坑

- **只测主视口**：1440px 完美、375px 破版——断点表逐项过；
- **"我这没问题"**：dev server 正常 ≠ 生产构建正常；
- **修完不复验**：修复引入新破版是常态，改完必须重跑受影响项；
- **Lighthouse 玄学**：跑分波动大——移动档、节流、取两次中位数。

## Route to existing skills · 路由

- `iterate-until-verified` — gate 驱动的验证循环方法论；
- `eric-frontend-delivery` — 前端运行时验证清单；
- `adaptive-quality-loop` 的失败循环 — 修复纪律（同一失败两次换路径）；
- `optimize-web-animations` — 性能问题专项；
- `security-review` — Path B 安全门；
- `stitched-full-page-capture` — 全页截图异常处理。

## Output artifacts · 产出物

- QA 证据包：断点截图、Lighthouse 报告、问题清单与修复记录（附在 progress 文件）。

## Handoff · 衔接

- 全部门通过 → **Step 9 Ship**；
- 发现功能性缺陷 → 回 Step 5 修复后回归本步；
- 视觉类缺陷 → 回 Step 7 定点修。
