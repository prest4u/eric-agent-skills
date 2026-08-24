# Step 7 · 视觉打磨 — Polish, Motion & Micro-interactions

> 中文速览：把"功能对"升维到"品质硬"——完善视觉系统细节、动效编排、微交互。Eric 的硬门：视觉品质对标 Anthropic/Stripe 水准，"能编译"不算完成。打磨要有节制：服务于 Step 2 定下的方向词，不堆砌特效。

## When you're in this step · 判定信号

- 功能与内容都已就位，但页面"看起来像模板"；
- 用户反馈"差点意思""不够高级"——几乎都是本步欠账。

## Inputs · 进入条件

- Step 5–6 产物（功能通、内容真）；
- Step 2 的视觉方向词与参考分析（打磨的对齐基准）。

## Action checklist · 行动清单

1. **排版精修**（投入产出比最高）：
   - [ ] 字级阶梯统一，行高/字距逐处调（大标题收紧 letter-spacing，正文 1.5–1.7 行高）；
   - [ ] 行长控制：正文 45–75 字符；标题换行有节奏（必要时手动 `<br>` 或 `text-wrap: balance`）；
   - [ ] 对齐纪律：所有元素对得上网格/容器线，无"差不多对齐"。
2. **空间与层次**：
   - [ ] 间距阶梯一致（4/8pt 体系），疏密有对比——该挤的挤、该留白的留白；
   - [ ] 层次三级以内：主信息 / 次信息 / 弱化信息，对比拉开；
   - [ ] 阴影/边框/分割线统一语言（参考 `beautiful-shadows`、`css-border-gradient`）。
3. **色彩与氛围**：
   - [ ] 主色 + 强调色纪律：强调色只给 CTA 和关键信号，不遍地开花；
   - [ ] 背景有质感（纹理/渐变/噪点/光效，按方向词选），不是死白或死黑；
   - [ ] 对比度达标（正文 ≥ 4.5:1）。
4. **动效编排**（ cinematically restrained ）：
   - [ ] 一个高潮点：编排好首屏入场（staggered reveal）比撒满微交互更高级；
   - [ ] 滚动叙事按需：scroll reveal / parallax / pinned sections（路由 GSAP 系 skill）；
   - [ ] 缓动与时长统一体系（参考 `animation-systems` 的默认值），全站一致；
   - [ ] **reduced motion**：`prefers-reduced-motion` 下全部有静态/简化回退。
5. **微交互**：
   - [ ] hover / focus / active / disabled 全状态覆盖，过渡 150–300ms；
   - [ ] 交互反馈即时：点击有响应、加载有指示、成功有确认；
   - [ ] 自定义细节（cursor、选中文颜色、滚动条）与方向词一致。
6. **整体走查**：对照参考站做 side-by-side 气质对比，找出差距最大的三处先改。

## Decision tables · 决策表

| 方向词 | 打磨重心 |
| --- | --- |
| minimal / editorial | 排版 + 留白 + 字体细节，动效极简 |
| luxury / cinematic | 光效 + 动效编排 + 材质感 |
| playful / brutalist | 大胆色彩/版式 + 俏皮微交互 |
| technical / dashboard | 密度 + 对齐 + 数据可读性，动效让位 |

## Exit criteria · 出口质量门

- [ ] 与参考站做并排对比，排版密度与气质不输（截图存档）；
- [ ] 所有交互元素五态齐全（default/hover/focus/active/disabled）；
- [ ] 动效在 `prefers-reduced-motion` 下有回退；
- [ ] 主视口与移动宽度各走查一遍：无文字溢出、无错位、无挤压；
- [ ] 动效滚动时帧率不劣化（DevTools Performance 面板抽查一次）。

## Common pitfalls · 常见坑

- **特效堆料**：一个页面三种动效风格——统一到方向词；
- **只调桌面**：打磨全部在 1440px 完成，移动端破版没发现；
- **紫色渐变默认脸**：AI 味重灾区（默认字体 + 紫渐变 + 卡片海）——回看 `frontend-design` 的 anti-patterns；
- **动效挡信息**：装饰性遮挡、巨大标题压住正文、视差让文字难读；
- **改坏了不回看**：每次打磨改动后必须重看渲染结果，不看结果不改下一处。

## Route to existing skills · 路由

- `frontend-design` / `eric-quality-sites` / `build-awwwards-quality-sites` — 视觉标准总纲；
- `gsap`, `animation-systems`, `cinematic-gsap-lenis-motion-system`, `cinematic-scroll-storytelling` — 动效实现；
- `masked-reveal`, `staggered-word-reveal`, `animation-on-scroll` — 文字与滚动动效；
- `beautiful-shadows`, `css-border-gradient`, `glass-dark-ui`, `skeuomorphic-ui` — 表面质感；
- 各设计系统 skill（`agency-grid-layout-minimal`、`editorial-tech` 等）— 按方向词选一套体系对齐；
- `optimize-web-animations` — 动效引起的性能问题。

## Output artifacts · 产出物

- 打磨后的页面 + 与参考的对比截图（存入 progress 文件备注）。

## Handoff · 衔接

- 视觉过硬门 → **Step 8 Verify**；
- 打磨中发现布局/内容结构性问题 → 回 Step 5 或 6 定点修，不在本步硬糊。
