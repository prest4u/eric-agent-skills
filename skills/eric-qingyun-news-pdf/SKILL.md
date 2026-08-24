---
name: eric-qingyun-news-pdf
description: 【新闻栏】青云选科指导报告 Typst 皮：新闻粗米纸、超粗黑头条、报式六栏、封面报头与通栏黑底反白标题。适合报式选科长文；客户可见只写青云未来。
---

# 青云 · 新闻栏

产品只写 **青云未来**。本 skill 是第二轮底盘 I 的可复用皮：新闻粗米、超粗黑头条、宋体分栏。磁盘上没有 I 研究稿。禁止从 E 编辑纸本、D 识别册或 v2 C 分栏纪录纸换色交差。

先读本文件，再读 `references/visual-contract.md`，再 `#import "theme.typ"`。

## 何时用 / 不用

**用：** 本季文种「选科指导报告」要做成报式选科长文；六栏走叙述，门表可跨栏。给要报纸栏而不是书页的家长。

**不用 / 改走别的皮：**

| 需求 | 走哪条 |
|---|---|
| 冷灰书纸、宋体章节、页码「一 / 三」 | `$eric-qingyun-editorial-pdf`（方案 E 编辑纸本） |
| 浅青灰卡 + 顶通栏 9mm 反白「青云」 | `$eric-qingyun-teal-pdf`（识别册） |
| 分栏纪录纸、报头底墨线 +「青云纪录」 | 方案 C，不是本皮，也不要给 C 换一张米纸交差 |
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

没有当年官方来源的条目，标「待核验」，不得写成已核实事实。

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

新稿不要写进 skill 包。`#import "theme.typ": *`，`#show: news-doc.with(...)`。封面用 `cover-page`，内页用 `deck-head` / `news-six`（与表混排），整页长文才用 `news-flow`（Typst `columns()` 会吃掉本页剩余高度）。门表用 `gate-table`（开表，无填色、无勾选框；可跨六栏）。

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

本季不是三人经营讨论稿、不是返佣合同。

## 完成门槛

- A4 竖、正好 4 页（本季小样锁 4 页；加长文可到 8 页，仍不要做成志愿册）
- 纸色 `#D2CBB8`、超粗黑头条、六栏、封面黑底反白与 `visual-contract.md` 一致
- `self_check.py` 通过；`pdftotext` 无禁词，有「青云」「选科指导报告」「林同」
- 可选中文；灰印可读

## 本切片没做的

九套场景骨架、签发工作流、与 E/D/C 互编译、可勾选清单、志愿方案模块。I 研究稿不存在，本皮不回写 studies。
