---
name: eric-qingyun-fold-pdf
description: 【豆绿折角】青云选科指导报告 Typst 皮：豆绿纸、右上 42mm 三角折角、粗黑题+楷文、单栏左齐。适合折角识别的选科长文；客户可见只写青云未来。
---

# 青云 · 豆绿折角

产品只写 **青云未来**。本 skill 是第三轮皮 K 的可复用皮：豆绿纸、右上 42mm 等腰直角三角折角、粗黑标题、楷体正文、单栏左齐。磁盘上没有 K 研究稿。禁止从 D 识别册、H 霜蓝通缘、E 编辑纸本或 I 新闻栏换色交差。内部可称「豆绿折角」，**不得印上 PDF**。

先读本文件，再读 `references/visual-contract.md`，再 `#import "theme.typ"`。

## 何时用 / 不用

**用：** 本季文种「选科指导报告」要做成折角选科长文；单栏左齐走叙述，门表开表。给要豆绿折角而不是顶通栏、右通缘或书页的家长。

**不用 / 改走别的皮：**

| 需求 | 走哪条 |
|---|---|
| 浅青灰卡 + 顶通栏 9mm 反白「青云」 | `$eric-qingyun-teal-pdf`（识别册 D） |
| 霜蓝卡 + 右缘 28mm 涂布竖条 | `$eric-qingyun-frost-pdf`（霜蓝通缘 H） |
| 冷灰书纸、宋体章节、页码「一 / 三」 | `$eric-qingyun-editorial-pdf`（方案 E 编辑纸本） |
| 新闻粗米、超粗黑头条、报式 6 栏 | `$eric-qingyun-news-pdf`（新闻栏 I） |
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

新稿不要写进 skill 包。`#import "theme.typ": *`，`#show: fold-doc.with(...)`。封面用 `cover-page`，内页用 `section-head`。门表用 `gate-table`（开表，无填色、无勾选框）。单栏左齐，不要 `columns()`，不要分栏 grid。

自检：

```bash
python3 scripts/self_check.py
```

也可对任意 PDF：`python3 scripts/self_check.py --pdf <file.pdf>`。

## 禁词与文种边界

客户可见品牌只写「青云未来」。禁止出现：青云知路、青云志愿。

本季文种是选科指导报告。禁止做成志愿冲稳保院校表。正文可以说「不开冲稳保」，但不要出现院校冲/稳/保分列。

禁止：录取概率、上岸率、保证上岸、一定录取、公章、国徽。禁止把皮肤名「豆绿折角」印上 PDF。

每份客户稿必须有：署名「青云未来」、页脚「非正式官方文件 · 不保证录取」、免责四句、事实 / 判断 / 待核验。

本季不是三人经营讨论稿、不是返佣合同。

## 完成门槛

- A4 竖、正好 4 页
- 纸色 `#A3C4A8`、右上 42mm 等腰直角三角折角、粗黑题 + 楷文、单栏左齐，与 `visual-contract.md` 一致
- `self_check.py` 通过；`pdftotext` 无禁词，有「青云」「选科指导报告」「林同」
- 可选中文；灰印可读

## 本切片没做的

九套场景骨架、签发工作流、与 D/H/E/I 互编译、可勾选清单、志愿方案模块。K 研究稿不存在，本皮不回写 studies。
