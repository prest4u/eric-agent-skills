---
name: eric-qingyun-editorial-pdf
description: 【编辑纸本】青云选科指导报告 Typst 皮：冷灰书纸、宋体章节、少铬条。适合选科长文、来源页和偏好书卷阅读的家长；客户可见只写青云未来。
---

# 青云 · 编辑纸本

产品只写 **青云未来**。本 skill 是视觉方案 E 的可复用皮，不是雾蓝白系统皮，也不是九套场景全家桶。

先读本文件，再读 `references/visual-contract.md`，再 `#import "theme.typ"`。色值、字号、边距、页眉只许从 E 研究稿提取，禁止发明。

本包只携带可再分发的主题、视觉合同与合成小样；内部研究稿不随 Skill 分发。

## 何时用 / 不用

**用：** 本季文种「选科指导报告」要做成冷灰书纸长文；来源页 / 怎么读 / 档案摘要 / 科目与专业门，给爱读书的家长。清单若出现，只作叙述条目，不必可勾选。

**不用 / 改走别的皮：**

| 需求 | 走哪条 |
|---|---|
| 整套客户 PDF 基线：方案、签发、清单、咨询栏轨 | `$eric-qingyun-pdf`（雾蓝白，**不要改那条皮**） |
| 本季选科报告但要雾蓝白案卷皮 | `$eric-qingyun-subject-pdf` + `$eric-qingyun-pdf` |
| 售前说明、暖象牙家长说明册 | 方案 B / `$eric-moss-ivory-pdf` 气质，不是本皮 |
| 确认书、签发单、出分后密意见书 | 方案 C 冷墨事务所 |
| 封面/页眉要让「青云」被认出来 | 方案 D 青云浅青 |
| 出分后志愿冲稳保表、填报清单 | `$eric-qingyun-plan-pdf` / `$eric-qingyun-checklist-pdf` |
| 三人经营讨论稿、渠道返佣合同 | 不是这个家族 |

## 和雾蓝白怎么选

- 雾蓝白：冷近白 `#F4F5F3`、16mm 栏轨、拉丁 eyebrow、咨询签发。
- 本皮：冷灰书纸 `#E6E4DE`、宋体章节号（一 / 二）、无栏轨、无结构色、无拉丁 kicker。页边距更大（上 26 / 下 24 / 左右 28mm）。
- 不要把本皮的 `theme.typ` 抄进 `$eric-qingyun-pdf`。也不要把雾蓝白的 `primary` / `rail-head` / `split-rule` 引进来。

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

编小样时脚本会带 `--root <skill-dir>`（小样 `#import "/theme.typ"`）。新项目把 `theme.typ` 拷到稿件目录后：

```bash
typst compile document.typ document.pdf
```

新稿不要写进 skill 包。`#import "theme.typ": *`，`#show: editorial-doc.with(...)`。封面用 `cover-page`，章节用 `chapter`，门表用 `gate-table`（只有横 hairline，无填色、无勾选框）。

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

## 完成门槛

- A4 竖、约 4 页（本季小样锁 4 页；加长文可到 8 页，仍不要做成志愿册）
- 纸色、宋体、边距、少铬条与 `visual-contract.md` 一致
- `self_check.py` 通过；`pdftotext` 无禁词
- 可选中文；灰印可读

## 本切片没做的

九套场景骨架、签发工作流、雾蓝白互编译、可勾选清单、志愿方案模块。见回报缺口。
