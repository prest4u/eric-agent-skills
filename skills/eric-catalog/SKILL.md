---
name: eric-catalog
description: 【Eric Skill总库】查看、选择、创建、升级或跨工具同步 Eric Skill 时使用。把 Codex、Cursor、Kimi、Claude、Hermes、OpenCode、Zed、Roo Code、Cline 等入口收束到同一 GitHub 权威库；不用于普通项目代码或非 Eric 社区 Skill。
---

# Eric 系列目录

Eric 系列是你自己的交付操作系统，不是社区视觉素材库。调用名保持 `eric-...`。中文名只用于认路和介绍。

本文件提供中文可读目录；机器可读的完整版本与版本号以 GitHub 仓库的 [`catalog/skills.yaml`](https://github.com/prest4u/eric-agent-skills/blob/main/catalog/skills.yaml) 为准。

## 总库治理

`prest4u/eric-agent-skills` 是唯一可编辑权威源。先读 `~/.local/state/eric-agent-skills/status.json` 取得当前 checkout；默认是 `~/.local/share/eric-agent-skills`。产品目录只负责发现，不是第二份源码。

当用户要求创建、升级、迭代、安装、重命名或同步 Eric Skill：

1. 已有 Skill 只编辑 `<checkout>/skills/<name>/`。如果入口来自 `.cursor/skills`、`.claude/skills`、`.roo/skills` 等路径，先解析链接，确认最终落在 checkout。
2. 新 Skill 直接创建在 `<checkout>/skills/<name>/`，同时登记 `catalog/skills.yaml`、恰好一个 collection 和各产品 manifest；不要先在某个产品目录造副本再搬运。
3. “最新”指通过隐私、许可、可移植性、安全和测试门禁的最新有效版本，不按修改时间盲目覆盖。
4. 本地验证后再请求发布授权；发布后运行 `<checkout>/scripts/sync_user_install.py --apply`，并以 `--check --json` 的零漂移结果验收。
5. 不自动启用 LaunchAgent、定时同步或后台上传。外部推送仍需当前任务授权。

### 已内置的产品入口

| 读取方式 | 产品 |
|---|---|
| 原生读取 `$HOME/.agents/skills`，清理高优先级同名副本 | Codex、Cursor、Kimi Code、OpenCode、Zed、Roo Code |
| 每个 Skill 链接到共享源 | Claude Code、Hermes Agent、Cline |
| 配置共享源为第一搜索路径 | Kimi Desktop |

### 登记其他 Agent 工具

先查该工具官方说明，确认它的全局 Skill 根目录及优先级。然后从本 Skill 目录运行：

```bash
python3 scripts/register_tool_surface.py \
  --name <tool-name> --mode links --skills-root "$HOME/.tool/skills"
python3 <checkout>/scripts/sync_user_install.py --apply
```

- `links`：工具不能原生读取 `$HOME/.agents/skills`，在它的专用根目录创建指向共享源的逐 Skill 链接。
- `shadows`：工具已经原生读取共享源；专用根目录只用于检测并备份会抢优先级的同名副本。

机器专属路径只写入 `~/.config/eric-agent-skills/tool-surfaces.json`，不进入公开 GitHub。只接受末级名称以 `skills` 结尾的专用目录；注册器拒绝 `/`、用户主目录、共享根和权威 checkout 等危险目标，同步器会再次校验并在任何变更前停止。

同步器不会沿“目录集合链接”跨出已登记根目录执行移动；如果该链接暴露了同名 Eric Skill，会在任何写入前停止并要求人工核对。单个 Skill 链接只备份链接本身，不移动其外部目标。

## 怎么选

1. 新任务还不清楚走哪条链路 → `$eric-workflow-router`；想法还很糊 → `$grilling`
2. 英语讲义 / 练习 / 作业 / 复习册 → `$eric-soft-signal`
3. 课堂一点一点往前翻的讲解页 → `$eric-teaching-deck`
4. 课后给家长的信 → `$eric-parent-feedback`
5. 青云未来咨询 PDF → 先读 `$eric-qingyun-pdf`，再开场景 skill
6. 网站从哪一步开始 → `$eric-web-pipeline`；要做到艺术指导级 → `$eric-quality-sites`
7. 长线教材整书 → `$eric-designed-pdf`；散文阅读件 → `$eric-slate-white-pdf` 或 `$eric-moss-ivory-pdf`
8. 明确要求二审 / 放行 → `$eric-review`；收工换会话 → `$eric-handoff`

不要用 `$eric-gaokao-*`。那是已卸下的旧名。

## 分类

### 总控与开工

| 中文名 | 调用名 | 一句话 |
|---|---|---|
| Eric 系列目录 | `$eric-catalog` | 查看中文分类、用途与调用名 |
| 工作流总路由 | `$eric-workflow-router` | 不知道走哪条链路时先看这一份总图 |
| 任务合同 | `$eric-task-contract` | 把模糊意图收成有边界、有验收的任务简报 |

### 英语教学

| 中文名 | 调用名 | 一句话 |
|---|---|---|
| 软信号 | `$eric-soft-signal` | 英语讲义主技能，从内容到 A4 PDF |
| 教学投屏 | `$eric-teaching-deck` | 课堂上一点一点往前翻的 HTML 讲解页 |
| 词汇讲义 | `$eric-pdf-vocabulary` | 软信号的词汇分册：高考词汇、红词、记忆链 |
| 教学去AI味 | `$eric-teaching-polish` | 清掉讲义、反馈、家长信里的生成腔 |
| 家长反馈 | `$eric-parent-feedback` | 三段式 TXT：课上内容 / 课上反馈 / 课后作业 |

### 书面 PDF

| 中文名 | 调用名 | 一句话 |
|---|---|---|
| 教学 Typst PDF | `$eric-pdf` | Typst A4 适配与质检，不是默认创作入口 |
| 教材级 PDF | `$eric-designed-pdf` | 长线教材、学生用书、练习册整书系统 |
| 雾蓝白 | `$eric-slate-white-pdf` | 克制读者向皮肤；青云案卷也用这套几何 |
| 苔绿象牙 | `$eric-moss-ivory-pdf` | 散文、短论、阅读件 |
| 哲学书 | `$eric-philosophy-book` | 哲学书封面、内文、插图位置 |

### 职业 PDF 系列

| 中文名 | 调用名 | 一句话 |
|---|---|---|
| 战略咨询 | `$eric-strategic-advisory-pdf` | 董事会、管理层与转型决策材料 |
| 交易尽调 | `$eric-transaction-dealbook-pdf` | 交易逻辑、依赖、整合门槛与风险 |
| 政策影响 | `$eric-policy-impact-brief-pdf` | 公共政策、试点与责任归属 |
| 技术图谱 | `$eric-technical-atlas-pdf` | 工程说明、系统剖面与运营图谱 |
| 学习指南 | `$eric-learning-field-guide-pdf` | 成人学习、工作坊与实践任务 |
| 高管读本 | `$eric-executive-learning-reader-pdf` | 领导力学习与研讨会读本 |
| 研究专著 | `$eric-research-monograph-pdf` | 文献、主张、来源和研究限制 |
| 知识档案 | `$eric-knowledge-archive-pdf` | 档案目录、知识库与藏品记录 |

### 青云未来咨询案卷

产品名是 **青云未来**。先读总控，再开场景。本季默认先卖选科，不硬卖出分填报。

| 中文名 | 调用名 | 一句话 |
|---|---|---|
| 青云案卷总控 | `$eric-qingyun-pdf` | 视觉、伦理、命名、路由、质检的总入口 |
| 服务说明 | `$eric-qingyun-service-brief-pdf` | 售前 2–4 页，讲清卖什么、不卖什么 |
| 服务确认 | `$eric-qingyun-consent-pdf` | 签约用知情同意，不是法律意见 |
| 档案约束 | `$eric-qingyun-profile-pdf` | 锁死选科底线和家庭硬约束 |
| 选科指导报告 | `$eric-qingyun-subject-pdf` | 本季主卖的 4–8 页选科报告 |
| 复核签发 | `$eric-qingyun-signoff-pdf` | 正式件出门前的签发单 |
| 家长讲解提纲 | `$eric-qingyun-briefing-pdf` | 当晚讲解用的两页提纲 |
| 志愿方案 | `$eric-qingyun-plan-pdf` | 出分后的冲稳保方案，不是本季第一份 |
| 填报清单 | `$eric-qingyun-checklist-pdf` | 对着官方系统勾的志愿顺序表 |

### 青云视觉皮

这些是独立可安装的视觉底盘。只有用户明确要求换皮时才调用；文种和事实边界仍以当前任务为准。

| 中文名 | 调用名 | 一句话 |
|---|---|---|
| 活页齿孔 | `$eric-qingyun-binder-pdf` | 石灰纸、左齿孔、抽出页气质 |
| 线装竖册 | `$eric-qingyun-booklet-pdf` | 藕荷纸、右起竖排、线装封面 |
| 冷墨事务所 | `$eric-qingyun-cold-ink-pdf` | 近白冷纸、细线意见备忘 |
| 编辑纸本 | `$eric-qingyun-editorial-pdf` | 冷灰书纸、宋体章节、长文阅读 |
| 豆绿折角 | `$eric-qingyun-fold-pdf` | 豆绿纸、右上折角、单栏左齐 |
| 霜蓝通缘 | `$eric-qingyun-frost-pdf` | 霜蓝纸、右缘色条、魏碑标题 |
| 藤紫点阵 | `$eric-qingyun-lattice-pdf` | 藤紫纸、点阵结构 |
| 新闻栏 | `$eric-qingyun-news-pdf` | 粗米纸、报式六栏、黑底头条 |
| 墨底夜页 | `$eric-qingyun-night-pdf` | 深色满版、反白字、左窄文柱 |
| 家长说明册 | `$eric-qingyun-parent-pdf` | 暖黄书纸、边注、题签封面 |
| 朱印砂卷 | `$eric-qingyun-seal-pdf` | 砂褐纸、四周细框、朱印识别 |
| 票根 | `$eric-qingyun-stub-pdf` | 砖红纸、底部票根与撕线 |
| 青云识别册 | `$eric-qingyun-teal-pdf` | 浅青灰卡、顶通栏、无衬线 |
| 军绿指索 | `$eric-qingyun-thumb-pdf` | 军绿纸、右缘字典拇指索引 |

### 网站与前端

| 中文名 | 调用名 | 一句话 |
|---|---|---|
| 精品站点 | `$eric-quality-sites` | 艺术指导级网站，从方向到上线 |
| 前端交付 | `$eric-frontend-delivery` | 把页面跑起来并自检，或做只读 UI 审计 |
| 网站流水线 | `$eric-web-pipeline` | 网页项目十步编排：现在第几步、下一步找谁 |

### 演示与影像

| 中文名 | 调用名 | 一句话 |
|---|---|---|
| 演示文稿 | `$eric-ppt-skill` | PPT / PPTD；不进青云案卷，也不进英语讲义 |
| 视觉记忆转译 | `$eric-visual-memory-translator` | 把照片收成克制的编辑页、记忆页、展览票 |

### 研究与外联

| 中文名 | 调用名 | 一句话 |
|---|---|---|
| 研究路由 | `$eric-research` | 跨域查证、引文、多源核对 |
| 外联取证 | `$eric-reach` | 打开链接、看视频、搜网上正在发生的事 |

### 质量与交接

| 中文名 | 调用名 | 一句话 |
|---|---|---|
| 独立评审 | `$eric-review` | 明确要求二审、挑错、放行时才用 |
| 任务交接 | `$eric-handoff` | 收工或换会话时留下可恢复的快照 |

### 工程工具

| 中文名 | 调用名 | 一句话 |
|---|---|---|
| 逆向工程 | `$eric-reverse-skill` | 搞清陌生二进制怎么工作 |

## 版本纪律

- 同名 Skill 只允许由 `prest4u/eric-agent-skills` 的本地 checkout 提供实体文件；各工具入口使用链接或共享发现路径。
- 不用修改时间单独判“最新版”。优先选择通过隐私、许可、可移植性与测试门禁的最新有效版本。
- 社区视觉、游戏或动效 Skill 不属于 Eric 系列，不纳入本目录的版本同步。
