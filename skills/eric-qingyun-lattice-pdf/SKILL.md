---
name: eric-qingyun-lattice-pdf
description: 【藤紫点阵】青云选科指导报告 Typst 皮：藤紫纸、全书仿宋、满页 5mm 圆点点阵。适合点阵纸面而不是书页、报栏或齿孔的选科长文；客户可见只写青云未来。
---

# 青云 · 选科指导报告（内部皮：藤紫点阵）

产品只写 **青云未来**。本 skill 是 wave-3 皮 N。内部名「藤紫点阵」只出现在本文件与 `references/visual-contract.md`，**不得印上 PDF**。禁止从 E 编辑纸本、J 活页齿孔或 I 新闻栏换色交差。

先读本文件，再读 `references/visual-contract.md`，再 `#import "theme.typ"`。

## 何时用 / 不用

**用：** 本季文种「选科指导报告」要做成藤紫点阵纸面；全书仿宋、单栏左齐、满页浅圆点。给要点阵而不是书页、报栏或齿孔的家长。

**不用 / 改走别的皮：**

| 需求 | 走哪条 |
|---|---|
| 冷灰书纸、宋体章节、页码「一 / 三」、28mm 书页 | `$eric-qingyun-editorial-pdf`（方案 E 编辑纸本） |
| 石灰纸、行楷题+黑体文、左 12mm 齿孔 | `$eric-qingyun-binder-pdf`（方案 J 活页齿孔） |
| 新闻粗米、超粗黑头条、报式 6 栏 | `$eric-qingyun-news-pdf`（方案 I 新闻栏） |
| 浅青灰卡 + 顶通栏 9mm 反白「青云」 | `$eric-qingyun-teal-pdf`（识别册） |
| 整套客户 PDF 基线、雾蓝白案卷 | `$eric-qingyun-pdf` / `$eric-slate-white-pdf` |
| 确认书、签发单、冷墨事务所 | `$eric-qingyun-cold-ink-pdf` |
| 出分后志愿冲稳保表、填报清单 | `$eric-qingyun-plan-pdf` / `$eric-qingyun-checklist-pdf` |
| 三人经营讨论稿、渠道返佣合同 | 不是这个家族 |

## 四硬差（相对 E / J / I）

1. **纸**：藤紫 `#B7A8C8`。不是 E `#E6E4DE`，不是 J `#C9C6BF`，不是 I `#D2CBB8`，不是近白，不是 `#DDE8E4`。
2. **字**：全书 `STFangsong`。不要 E 的宋体章节号「一 / 二」，不要 J 的行楷+黑体，不要 I 的超粗黑头条。
3. **网格**：满页 5mm 圆点点阵。无框、无轨、无栏。禁止 28mm 书页边距、左齿孔、六栏竖线。
4. **封面**：同一张藤紫点阵纸。左齐大仿宋「选科指导报告」，其下小「青云」。无折角、无通栏黑条、无报头、无齿孔、无撕线。

页脚：`青云 · 非正式官方文件 · 不保证录取 ·` 页码。封面与内页同一纸、同一点阵。

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

新稿不要写进 skill 包。`#import "theme.typ": *`，`#show: lattice-doc.with(...)`。封面用 `cover-page`，内页用 `section-head` / `lead` / `row-table` / `gate-table`。门表只有横向 hairline，无填色、无勾选框。

自检：

```bash
python3 scripts/self_check.py
```

也可对任意 PDF：`python3 scripts/self_check.py --pdf <file.pdf>`。

## 禁词与文种边界

客户可见品牌只写「青云未来」。禁止出现：青云知路、青云志愿。

禁止把内部名「藤紫点阵」印上封面、页眉、页脚、正文。

本季文种是选科指导报告。禁止做成志愿冲稳保院校表。正文可以说「不开冲稳保」，但不要出现院校冲/稳/保分列。

禁止：录取概率、上岸率、保证上岸、一定录取、公章、国徽。

每份客户稿必须有：署名「青云未来」、页脚「非正式官方文件 · 不保证录取」、免责四句、事实 / 判断 / 待核验。

本季不是三人经营讨论稿、不是返佣合同。

## 完成门槛

- A4 竖、正好 4 页（本季小样锁 4 页）
- 纸色 `#B7A8C8`、全书仿宋、5mm 圆点点阵、封面左齐大题与 `visual-contract.md` 一致
- `self_check.py` 通过；`pdftotext` 无禁词，有「青云」「选科指导报告」「林同」
- 可选中文；点阵浅、可读

## 本切片没做的

九套场景骨架、签发工作流、与 E/J/I 互编译、可勾选清单、志愿方案模块。N 研究稿不回写 studies。
