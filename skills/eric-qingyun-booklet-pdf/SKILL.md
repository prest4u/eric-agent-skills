---
name: eric-qingyun-booklet-pdf
description: 【线装竖册】青云选科指导报告 Typst 皮：藕荷纸、全书楷体竖排右起左行、线装右竖题封面、门对照一组合一竖栏。给要线装册而不是横排书页或报纸栏的家长。客户可见只写青云未来。
---

# 青云 · 线装竖册

产品只写 **青云未来**。本 skill 是第三轮皮 L 的可复用皮：藕荷纸、楷全书、竖排右起左行、线装封面。禁止从 E 编辑纸本、H 霜蓝通缘或 I 新闻栏换色交差。内部皮名只出现在本文件与 `references/visual-contract.md`，**不得印上 PDF**。

先读本文件，再读 `references/visual-contract.md`，再 `#import "theme.typ"`。

Typst 0.14.2 拒绝 `text(dir: ttb)`（`text direction must be horizontal`）。本皮用 `stack(dir: ttb)` 做单字顶到底的真竖排，用 `stack(dir: rtl)` 让栏从右往左走。不要改成整块 `rotate(90deg)`（字会躺倒，不是竖排）。

## 何时用 / 不用

**用：** 本季文种「选科指导报告」要做成线装竖册；全书竖排，门表是竖栏不是横表。给要册页而不是书页或报纸的家长。

**不用 / 改走别的皮：**

| 需求 | 走哪条 |
|---|---|
| 冷灰书纸、宋体章节、页码「一 / 三」、28mm 居中书页 | `$eric-qingyun-editorial-pdf`（方案 E 编辑纸本） |
| 霜蓝卡、魏碑题、右缘 28mm 涂布色条 | `$eric-qingyun-frost-pdf`（方案 H 霜蓝通缘） |
| 新闻粗米、超粗黑头条、报式 6 栏、黑底反白报头 | `$eric-qingyun-news-pdf`（方案 I 新闻栏） |
| 浅青灰卡 + 顶通栏 9mm 反白「青云」 | `$eric-qingyun-teal-pdf`（识别册） |
| 整套客户 PDF 基线、雾蓝白案卷 | `$eric-qingyun-pdf` / `$eric-slate-white-pdf` |
| 确认书、签发单、冷墨事务所 | `$eric-qingyun-cold-ink-pdf` |
| 出分后志愿冲稳保表、填报清单 | `$eric-qingyun-plan-pdf` / `$eric-qingyun-checklist-pdf` |
| 三人经营讨论稿、渠道返佣合同 | 不是这个家族 |

## 输入

最低输入（与共享案例字段对齐，见 `samples/facts.typ`）：

- 化名、省、年、批次（写「高一选科」，不要写本科批）
- 案例号、版本、日期
- 现行组合 / 备选组合 / 硬约束 / 软偏好 / 待补
- 科目门对照行（工科 / 医学 / 经管 / 放弃代价）
- 免责四句原文

没有当年官方来源的条目，标「待核验」，不得写成已核实事实。不要改 `facts.typ` 里的学生事实。

## 怎么编译

需要 Typst 0.14.x，并确保 `typst` 在 `PATH` 中可用。

编本 skill 自带 4 页小样：

```bash
python3 scripts/compile_sample.py
```

编小样时脚本会带 `--root <skill-dir>`（小样 `#import "/theme.typ"`）。不要把 `samples/` 当 root。

新项目把 `theme.typ` 拷到稿件目录后：

```bash
typst compile document.typ document.pdf
```

新稿不要写进 skill 包。`#import "theme.typ": *`，`#show: booklet-doc.with(...)`。封面用 `cover-page`，竖行用 `v-run` / `v-flow`，右起多栏用 `rtl-cols`，门对照用 `gate-columns`（每种组合一竖栏，禁止横表）。

自检：

```bash
python3 scripts/self_check.py
```

也可对任意 PDF：`python3 scripts/self_check.py --pdf <file.pdf>`。

## 禁词与文种边界

客户可见品牌只写「青云未来」。禁止出现：青云知路、青云志愿。

本季文种是选科指导报告。禁止做成志愿冲稳保院校表。正文可以说「不开冲稳保」，但不要出现院校冲/稳/保分列。

禁止：录取概率、上岸率、保证上岸、一定录取、公章、国徽。

每份客户稿必须有：署名「青云未来」、页脚「非正式官方文件 · 不保证录取」、免责四句、事实 / 判断 / 待核验。

封面右缘是 11mm 线装订口加四孔，不是 H 的 28mm 涂布色条，也不是通栏黑底报头。页边距不是 E 的 28mm。页码是阿拉伯 `01`，不是「一」「二」。

## 完成门槛

- A4 竖、正好 4 页（本季小样锁 4 页；加长文可到 8 页，仍不要做成志愿册）
- 纸色 `#D9B8C4`、全书楷体、竖排右起左行、线装封面与 `visual-contract.md` 一致
- `self_check.py` 通过；`pdftotext` 无禁词，有「青云」「选科指导报告」「林同」（竖排抽出时允许按字换行，自检会去空白）
- 可选中文；藕荷底上墨色可读

## 本切片没做的

九套场景骨架、签发工作流、与 E/H/I 互编译、可勾选清单、志愿方案模块。L 研究稿不回写 studies。
