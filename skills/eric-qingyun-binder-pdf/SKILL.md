---
name: eric-qingyun-binder-pdf
description: 【活页齿孔】青云 Typst 皮：石灰纸、行楷题+黑体文、左 12mm 齿孔、抽出页封面。课堂/会议可撕页、需要齿孔识别的选科说明用这张皮。Use when a 青云 subject-selection PDF needs the binder-punch skin. Customer-facing brand is only 青云未来.
---

# 青云 · 活页齿孔

产品只写 **青云未来**（版式美术元素可保留「青云」二字）。本 skill 是第二轮**新底盘 J**，不是家长说明册换色，也不是 A 雾蓝白栏轨。禁止复用 38mm 边注、竖题签、暖黄书纸、`rail-head`。

先读本文件，再读 `references/visual-contract.md`，再 `#import "theme.typ"`。色值、字栈、12mm 齿孔、抽出页封面只许按合同，禁止发明第二套品牌色。

## 何时用 / 不用

**用：** 活页抽出页气质的选科说明、课堂/会议发的可撕页、需要齿孔识别的青云选科 PDF。语气像从活页夹抽出的一页，不是坐下来讲解，也不是咨询签发。本季文种是选科，不要脚手架志愿方案。

**不用 / 改走别的皮：**

| 需求 | 走哪条 |
|---|---|
| 整套客户 PDF 基线：方案、签发、清单、咨询栏轨 | `$eric-qingyun-pdf`（A 雾蓝白，**不要改那条皮**） |
| 售前说明、家长讲解、教师转介 | `$eric-qingyun-parent-pdf`（暖黄 + 38mm 边注 + 题签） |
| 确认书、签发单、出分后密意见书 | C `$eric-qingyun-cold-ink-pdf` |
| 封面/页眉要让「青云」被认出来 | D `$eric-qingyun-teal-pdf` |
| 选科长文、来源页、爱读书的家长 | E `$eric-qingyun-editorial-pdf` |
| 出分后志愿冲稳保表、填报清单 | `$eric-qingyun-plan-pdf` / `$eric-qingyun-checklist-pdf` |
| 三人经营讨论稿、渠道返佣合同 | 不是这个家族 |

## 四硬差（每轴都换）

1. **纸**：石灰 `#C9C6BF`。不是 A `#F4F5F3`，不是家长说明册 `#EFE4D0`，不是 B `#F6F3EA`，不是 E `#E6E4DE`，不是 C `#F3F3F1`。
2. **字**：标题/封面主标题用行楷 `Xingkai SC`；正文用真黑体 `Heiti SC`。不要 A 的苹方栏轨字，不要家长说明册的楷+仿，不要把苹方当正文主栈交差。
3. **网格**：左 **12mm 齿孔** = 竖向虚线 + 一列圆点（活页打孔）。内容从齿孔右侧起排。这不是 16mm 栏轨，也不是 38mm 边注。禁止函数名或几何叫 `rail-head` / `split-rule`。页码不要 `01` 栏轨编号。
4. **封面**：像从活页夹抽出的一页。左边同样 12mm 齿孔；右上横排小「青云」；主标题左齐行楷。不要居中题辞，不要竖题签匣，无 DOCUMENT/STATUS 底栏，封面无咨询页眉。

不要声明 `primary` 结构色，不要栏轨色块。不要把本皮 theme 抄进雾蓝白系统皮或家长说明册。

## 输入

最低输入（与共享案例字段对齐，见 `samples/facts.typ`）：

- 化名、省、年、批次（写「高一选科」，不要写本科批）
- 案例号、版本、日期
- 现行组合 / 备选组合 / 硬约束 / 软偏好 / 待补
- 科目门对照行（工科 / 医学 / 经管 / 放弃代价）
- 免责四句原文

没有当年官方来源的条目，标「待核验」，不得写成已核实事实。冲/稳/保仅出现在志愿方案；本册禁止院校冲稳保表。可以说「本页不开冲稳保」。

## 怎么编译

需要 Typst 0.14.x，并确保 `typst` 在 `PATH` 中可用。

编本 skill 自带 4 页小样：

```bash
python3 scripts/compile_sample.py
```

编小样时脚本会带 `--root <skill-dir>`（小样 `#import "/theme.typ"`）。新项目把 `theme.typ` 拷到稿件目录后：

```bash
typst compile document.typ document.pdf
```

新稿不要写进 skill 包。`#import "theme.typ": *`，`#show: binder-doc.with(...)`。封面用 `cover-page`，门表用 `gate-table`（只有横 hairline，无填色、无勾选框）。齿孔由 `binder-holes` 画在每页 background，几何锁在 `punch-gutter`。

自检：

```bash
python3 scripts/self_check.py
```

也可对任意 PDF：`python3 scripts/self_check.py --pdf <file.pdf>`。

目检页图（可选）：

```bash
pdftoppm -png -r 140 samples/document.pdf samples/page
```

## 禁词与文种边界

客户可见品牌只写「青云未来」。禁止出现：青云知路、青云志愿。

本季文种是选科（课堂/会议可撕页、抽出页说明）。禁止做成志愿冲稳保院校表。正文可以说「不开冲稳保」，但不要出现院校冲/稳/保分列。

禁止：录取概率、上岸率、保证上岸、一定录取、公章、国徽、真名。

每份客户稿必须有：署名「青云未来」、页脚「非正式官方文件 · 不保证录取」、免责四句、事实 / 判断 / 待核验。皮肤内部名「活页齿孔」可以印在页脚微字。

免责四句原文锁定：

1. 本文件不是教育考试院或高校官方文件。
2. 本文件不构成录取、就业或薪资承诺。
3. 最终以当年官方系统、招生计划和高校招生章程为准。
4. 过期、缺失或相互冲突的数据，不得当作已核实事实。

客户文件名风格：`选科说明-案例合成TJ2026-0042-天津2026-V1-20260819.pdf`。小样可用 `document.pdf`。

不要在客户页写「客户可见只写青云未来」这种内部句。

## 完成门槛

- A4 竖、正好 4 页（本季小样锁 4 页）
- 石灰纸、行楷题+黑体文、12mm 齿孔、抽出页封面与 `visual-contract.md` 一致
- `self_check.py` 通过；`pdftotext` 无禁词
- 可选中文；前两屏见「青云」和「不保证录取」

## 本切片没做的

九套场景骨架、签发工作流、雾蓝白互编译、可勾选清单、志愿方案模块。不要回写 `$eric-qingyun-pdf`、`$eric-qingyun-parent-pdf`、`$eric-slate-white-pdf` 或其他青云皮。
