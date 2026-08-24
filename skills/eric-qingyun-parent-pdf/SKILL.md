---
name: eric-qingyun-parent-pdf
description: 【家长说明册】青云 Typst 皮：暖黄书纸、楷题仿宋、左 38mm 边注、题签封面。适合售前说明、家长讲解与教师转介；客户可见只写青云未来。
---

# 青云 · 家长说明册

产品只写 **青云未来**（版式美术元素可保留「青云」二字）。本 skill 是 Document Master 淘汰 B 苔绿象牙之后的**替代底盘**，不是 A 雾蓝白的换色，禁止复用 `rail-head`。

先读本文件，再读 `references/visual-contract.md`，再 `#import "theme.typ"`。色值、字栈、38mm 边注、题签封面只许按合同，禁止发明第二套品牌色。

## 何时用 / 不用

**用：** 售前说明、家长讲解、教师转介。语气像坐下来跟家长说话。本季文种是选科，不要脚手架志愿方案。

**不用 / 改走别的皮：**

| 需求 | 走哪条 |
|---|---|
| 整套客户 PDF 基线：方案、签发、清单、咨询栏轨 | `$eric-qingyun-pdf`（A 雾蓝白，**不要改那条皮**） |
| 确认书、签发单、出分后密意见书 | C `$eric-qingyun-cold-ink-pdf` |
| 封面/页眉要让「青云」被认出来 | D `$eric-qingyun-teal-pdf` |
| 选科长文、来源页、爱读书的家长 | E `$eric-qingyun-editorial-pdf` |
| 出分后志愿冲稳保表、填报清单 | `$eric-qingyun-plan-pdf` / `$eric-qingyun-checklist-pdf` |
| 旧 B 苔绿象牙说明册 | **已淘汰**，不要再路由过去当交付皮；改走本皮 |
| 三人经营讨论稿、渠道返佣合同 | 不是这个家族 |

## 四硬差（每轴都换）

1. **纸**：暖黄书纸 `#EFE4D0`。不是 A `#F4F5F3`，不是 B `#F6F3EA` 暖象牙，不是 C `#F3F3F1`，不是 E `#E6E4DE`。
2. **字**：标题/题辞/题签/边注标签用楷体 `Kaiti SC`；正文用仿宋 `STFangsong`。不要 A 的苹方栏轨字，不要 E 的宋体章节号。
3. **网格**：左 **38mm 边注** / 沟约 6.5mm / 右正文。这是双栏页网格，不是 16mm 栏轨。禁止函数名或几何叫 `rail-head` / `split-rule`。页码放左边注底部，不要 A 的 `01` 栏轨编号。
4. **封面**：竖向纸签只写「青云」+ 居中大楷题辞。禁止拉丁 kicker，禁止封面底栏印 DOCUMENT / STATUS，封面无页眉页脚。

不要声明 `primary` 结构色，不要栏轨色块。不要把本皮 theme 抄进雾蓝白系统皮。

## 输入

最低输入（与共享案例字段对齐，见 `samples/facts.typ`）：

- 化名、省、年、批次（写「高一选科」，不要写本科批）
- 案例号、版本、日期
- 现行组合 / 备选组合 / 硬约束 / 软偏好 / 待补
- 科目门对照行（工科 / 医学 / 经管 / 放弃代价）
- 免责四句原文

没有当年官方来源的条目，标「待核验」，不得写成已核实事实。冲/稳/保仅出现在志愿方案；本册禁止院校冲稳保表。可以说「本册不开冲稳保」。

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

新稿不要写进 skill 包。`#import "theme.typ": *`，`#show: parent-doc.with(...)`。封面用 `cover-page`，内页用 `spread(note, body)`，门表用 `gate-table`（只有横 hairline，无填色、无勾选框）。

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

本季文种是选科（家长讲解 / 售前 / 转介）。禁止做成志愿冲稳保院校表。正文可以说「不开冲稳保」，但不要出现院校冲/稳/保分列。

禁止：录取概率、上岸率、保证上岸、一定录取、公章、国徽、真名。

每份客户稿必须有：署名「青云未来」、页脚「非正式官方文件 · 不保证录取」、免责四句、事实 / 判断 / 待核验。页脚可拆到边注 + 主栏，但原文必须出现。皮肤内部名「家长说明册」可以印在页脚微字。

免责四句原文锁定：

1. 本文件不是教育考试院或高校官方文件。
2. 本文件不构成录取、就业或薪资承诺。
3. 最终以当年官方系统、招生计划和高校招生章程为准。
4. 过期、缺失或相互冲突的数据，不得当作已核实事实。

客户文件名风格：`选科指导-案例合成TJ2026-0042-天津2026-V1-20260819.pdf`。小样可用 `document.pdf`。

## 完成门槛

- A4 竖、正好 4 页（本季小样锁 4 页）
- 暖黄书纸、楷题仿宋、38mm 边注、题签封面与 `visual-contract.md` 一致
- `self_check.py` 通过；`pdftotext` 无禁词
- 可选中文；前两屏见「青云」和「不保证录取」

## 本切片没做的

九套场景骨架、签发工作流、雾蓝白互编译、可勾选清单、志愿方案模块。不要回写 `$eric-qingyun-pdf`、`$eric-slate-white-pdf`、`$eric-moss-ivory-pdf` 或其他青云皮。
