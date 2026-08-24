---
name: eric-workflow-router
description: 【工作流总路由】Eric 的跨工具工作流总路由，适用于 Codex、Kimi Code/Kimi Desktop、Cursor、Claude Code 与 Hermes Agent。任何新项目、新课程包、新网站、新 PDF/文档任务、研究任务或“不知道该走哪套流程”时先调用本 Skill。它把任务分流到 L0 目标锁定 → L1 领域实现 → L2 校验 → L3 签核交付四层链路，并给出每条链路的精确 Skill 调用顺序。
---

# Eric 工作流路由 · 四层质量链路

核心纪律：**治理交付物的质量链路，而不是治理 Skill 的存在**。本 Skill 只做分流与纪律检查，不亲自实现产出物；不同工具都以同一 GitHub Skill 目录为准。

## 分流表：先判定场景

| 场景信号 | 链路 |
|---|---|
| 课程、讲义、练习、词汇、考试、学生 | A. 教学 |
| 家长反馈、课后总结、试听反馈 | B. 家长沟通 |
| 网站、落地页、前端、UI、设计系统 | C. 前端设计 |
| PDF、讲义排版、书面材料、书 | D. PDF 书面 |
| PPT、演示、幻灯片 | E. 演示 |
| 调研、求证、对比、行业分析 | F. 研究 |
| 想法还很模糊、需求没理清、新项目第一次对话 | 先走 L0，禁止直接产出 |

## L0 目标锁定（新任务强制入口）

新任务**第一次**对话，按模糊程度二选一：

1. 需求模糊、方向未定 → 调 `grilling`（拷问模式：一次一问，沿决策树收敛；问完整理成计划再动手）
2. 需求较清楚但要交给长程 Agent 跑 → 调 `leader`（先实测调研，再问 ≤5 个必答题，产出任务书）

然后由 `eric-task-contract` 锁定边界：非目标、验收证据、权限、漂移边界。

**红线**：L0 未收敛，禁止进入 L1。简单只读问答（查个事实、改个句子）可豁免。

## L1 领域实现（按链路调用）

- **A. 教学**：`eric-soft-signal`（主路由）→ `k12-english-teaching`（课程设计）→ 词汇域叠加 `eric-pdf-vocabulary`；题库类用 `exam-corpus-system`
- **B. 家长沟通**：`eric-parent-feedback` → `eric-teaching-polish`（去 AI 味终稿）
- **C. 前端设计**：`eric-quality-sites`（艺术指导+实现）→ `eric-frontend-delivery`（运行验证）
- **D. PDF 书面**：教科书级用 `eric-designed-pdf`；散文/双语用 `eric-moss-ivory-pdf` 或 `eric-slate-white-pdf`；Typst A4 适配走 `eric-pdf`（显式调用）
- **E. 演示**：`eric-ppt-skill`
- **F. 研究**：`eric-research`（显式调用）；记忆/知识库内查证走 Holograph 官方入口 `query_holographic.py`

新引入的通用工程 Skill（mattpocock 系）按阶段嵌入：`to-spec`（规格）→ `to-tickets`（拆工单）→ `implement` / `tdd`（实现）→ `code-review`。教学场景用 `teach` 辅助讲解设计。超大工程用 `wayfinder` 绘图分区推进。

## L2 校验（学生可见 / 对外发布 / 生产变更不可跳过）

1. 有反复失败模式的检查 → 用 `building-validators` 编成可执行校验器
2. 多文件改动 → `adaptive-quality-loop`（BUILD/PROOF/RELEASE）
3. 视觉/前端交付 → `eric-frontend-delivery`（运行时与渲染核查）+ `eric-review` 复审

## L3 签核交付

- 正式交付前 → `eric-review`（QUICK_REVIEW 起步；学生可见物用 FORMAL_SIGNOFF）
- 跨任务交接/暂停 → `eric-handoff`
- 交付渠道：优先使用本地文件；外部链接、发送或发布必须由当前任务明确授权

## 横切能力（按当前工具能力启用）

- 重复性工作（周报、定期采集、持续追踪）→ 仅在当前工具具备正式自动化能力且用户授权后配置
- 需要持久可视化的结果 → 使用当前工具已有的看板或本地可视化，不虚构连接器
- Skill 生命周期管理（激活/停用/回滚）→ 以 `prest4u/eric-agent-skills` 为唯一版本源；若 `$darwin-skill` 已安装，只作辅助盘点
- 记忆库读写 → 只用当前任务已经提供并授权的记忆或知识库入口

## 反模式（禁止）

- 跳过 L0 直接产出"第一版"
- 学生可见物未经 L2/L3 直接发出
- 一次性加载 5 个以上 Skill 正文（按需渐进加载，用 Skill 工具逐个点名）
- 让任一工具自己的旧副本覆盖 GitHub 权威版本；发现同名多份时先做版本与解析路径审计
