---
name: eric-qingyun-pdf
description: 【青云案卷总控】System skill for 青云未来 advisory PDFs in Eric Slate White PDF｜雾蓝白. Owns visual contract, 青云未来 signature, identity header, disclaimer, naming, ethics, routing, Typst theme, and QA. Use when making 青云未来选科指导、学业规划、志愿方案、服务说明、确认书、档案约束、填报清单、签发单、早鸟预售、家长讲解提纲, or 高考志愿/选科咨询 documents. Do not print 青云知路 or 青云志愿. Do not use for English textbooks, AI workshop decks, study-abroad contracts, or fake-official stamps.
---

# 青云未来文书系统｜雾蓝白案卷

产品叫 **青云未来**，不是「高考」系列。客户可见只写「青云未来」。

先读本 Skill，再按文种打开场景 Skill。本包内置完整视觉合同、伦理合同、主题和检查脚本；雾蓝白只描述视觉家族，不构成对 `$eric-slate-white-pdf` 的运行依赖。

## 必读顺序

1. 本文件（路由、伦理、命名、工作流）
2. `references/visual-contract.md`
3. `references/ethics.md`
4. 对应场景 skill
5. 薄文件：`references/teacher-one-pager.md`、`references/early-bird.md`（不单独建 skill）

## 何时用 / 不用

**用：** 青云未来高报线给家庭、顾问、老师看的咨询 PDF（本季主卖选科指导；志愿方案仍用同一皮肤）。

**不用：**

- 英语教材 → `$eric-designed-pdf` / `$eric-pdf`
- 成人 AI 工作坊大纲、读书会幻灯 → `$eric-ppt-skill` 或单独讲义，不进本家族
- 留学转介：客户与机构直签，不把机构交付写成青云未来方案报告
- 渠道老师返佣 / 机构返点合同：律师稿，不是本家族
- 三人经营讨论稿、计点方案：内部雾蓝白，不是客户交付
- OCR / 合并 → `$pdf`

旧名 `$eric-gaokao-*` 已废弃，已从本机发现目录卸下。不要再安装或调用高考桩；一律走本家族。

## 场景路由（按现在该卖的顺序）

本季（9–10 月）先交付选科，不硬卖出分填报。志愿方案技能保留，旺季再用。

| 优先级 | 时刻 | 文种 | Skill / 场景 | 页数 |
|---|---|---|---|---|
| **P0** | 售前 | 服务说明（默认选科） | `$eric-qingyun-service-brief-pdf` | 2–4 |
| **P0** | 签约 | 服务确认 / 知情同意 | `$eric-qingyun-consent-pdf` | 4–6 |
| **P0** | 诊断 | 档案与家庭约束 | `$eric-qingyun-profile-pdf` | 2–4 |
| **P0** | **本季主交付** | **选科指导报告** | `$eric-qingyun-subject-pdf` | 4–8 |
| **P0** | 归档 | 复核签发 | `$eric-qingyun-signoff-pdf` | 1–2 |
| **P1** | 锁客 | 2027 届早鸟一页纸 | 本 skill · `early-bird` | 1–2 |
| **P1** | 讲解 | 家长讲解提纲 | `$eric-qingyun-briefing-pdf` | 2 |
| **P1** | 出分后 | 志愿方案报告 | `$eric-qingyun-plan-pdf` | 8–14 |
| **P1** | 填报 | 填报执行清单 | `$eric-qingyun-checklist-pdf` | 2–6 |
| **P2** | 转介 | 合作老师一页纸 | 本 skill · `teacher` | 1–2 |

相邻关系：选科报告投影选科版 D3，不投影志愿候选池。志愿 D4 必须投影志愿版 D3。D5 只收已签发 D4。没有 D6 就不是正式 PDF。顾问工作台导出的家庭件仍是本家族文种的**只读签发快照**，不另开「工作台导出」skill；家庭先看顾问给的只读件，不自动推荐、不覆盖旧版。

## 工作流

1. 锁文种。本季默认 `subject`，不要一上来脚手架 `plan`。
2. 读对应场景 skill。
3. 在项目目录脚手架（勿写入 skill 包）：

```bash
python3 <eric-qingyun-pdf>/scripts/new_document.py \
  --scene subject \
  --out <fresh-project-dir> \
  --title "选科指导报告" \
  --case-id "案例合成-TJ2026-0042" \
  --alias "林同"
```

`--scene`：`service-brief` / `consent` / `profile` / `subject` / `signoff` / `early-bird` / `briefing` / `plan` / `checklist` / `teacher`

4. 改 `document.typ`，保留 `#import "theme.typ"`。署名写「青云未来」。
5. `typst compile` → `pdftoppm` → `scripts/check_pdf.py --scene <scene>`

## 皮肤与署名

- 主题：`Eric Slate White PDF｜雾蓝白`
- 客户可见机构名：**青云未来**
- 禁止印：青云知路、青云志愿（竞品名也不要印）
- 冲/稳/保仅出现在志愿方案/清单，选科报告禁止院校冲稳保表
- 气质：冷白咨询案卷

## 每份客户 PDF 必有

身份页眉、页脚「青云未来 · 非正式官方文件 · 不保证录取」、免责四句、事实/判断/待核验。选科件把「批次」写成「选科」即可。

## 命名

```
选科指导-案例合成TJ2026-0042-天津2026-V1-20260818.pdf
```

## 完成门槛

A4、可选中文、`check_pdf.py` 通过、灰印可读、前两屏能看到「青云未来」和「不保证录取」、有全称品牌青云未来、无概率、无公章、无真名。

Gate ledger：`Scope / Scene / Fresh compile / check_pdf / Rendered pages / Ethics / Remaining risk`
