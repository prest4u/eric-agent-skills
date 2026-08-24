---
name: eric-qingyun-stub-pdf
description: 【票根】青云选科指导报告 Typst 皮：砖红纸、黑体题+行楷文、底部 22mm 票根与齿孔撕线。适合票据式识别的选科材料；客户可见只写青云未来。
---

# 青云 · 选科指导报告（内部皮：砖红票根）

产品只写 **青云未来**（版式美术元素可保留「青云」二字）。本 skill 是 wave-3 底盘 O，**不是** J 活页齿孔、I 新闻栏、D 浅青识别册或 F 朱印砂卷的换色。禁止左 12mm 齿孔、顶通栏 / 报头、六栏、四周 6mm 细框、朱印。内部名只出现在本文件与 `references/visual-contract.md`，**不得印上 PDF**。

先读本文件，再读 `references/visual-contract.md`，再 `#import "theme.typ"`。

## 何时用 / 不用

**用：** 本季文种「选科指导报告」要做成一张可撕票根：砖红纸、上半是正文、底 22mm 票根印「青云」。给要票、不要报纸栏、不要活页夹、不要浅青册面的家长。

**不用 / 改走别的皮：**

| 需求 | 走哪条 |
|---|---|
| 石灰纸、左 12mm 齿孔、抽出页 | `$eric-qingyun-binder-pdf`（底盘 J 活页齿孔） |
| 新闻粗米、超粗黑头条、报式 6 栏 | `$eric-qingyun-news-pdf`（底盘 I 新闻栏） |
| 浅青灰卡 + 顶通栏 9mm 反白「青云」 | `$eric-qingyun-teal-pdf`（识别册 D） |
| 砂褐纸 + 6mm 细框 + 框内朱印 | `$eric-qingyun-seal-pdf`（朱印砂卷 F） |
| 冷灰书纸、宋体章节、页码「一 / 三」 | `$eric-qingyun-editorial-pdf`（方案 E） |
| 整套客户 PDF 基线、雾蓝白案卷 | `$eric-qingyun-pdf` / `$eric-slate-white-pdf` |
| 确认书、签发单、冷墨事务所 | `$eric-qingyun-cold-ink-pdf` |
| 出分后冲稳保表、填报清单 | `$eric-qingyun-plan-pdf` / `$eric-qingyun-checklist-pdf` |
| 三人经营讨论稿、渠道返佣合同 | 不是这个家族 |

## 四硬差（每轴都换）

1. **离开 J 活页齿孔。** J 是石灰 `#C9C6BF` + **左 12mm 竖列圆孔**。本皮是砖红 `#D08A72` + **底 22mm 票根 + 横向齿孔撕线**。无左孔。
2. **离开 I 新闻栏。** I 是新闻粗米 `#D2CBB8` + **顶报头 / 通栏黑底反白 + 六栏**。本皮无报头、无六栏、无顶带；品牌在底票根。
3. **离开 D 浅青识别册。** D 是浅青灰 `#DDE8E4` + **顶 9mm 反白通栏**。本皮纸必须读红，品牌在底 22mm 票根，无 `band-h`。
4. **离开 F 朱印砂卷。** F 是砂褐 `#C4A882` + **四周 6mm 细框 + 框内朱印**。本皮无框、无印；纸是砖红不是砂黄。

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

新稿不要写进 skill 包。`#import "theme.typ": *`，`#show: stub-doc.with(...)`。封面用 `cover-page`，内页用 `section-head` / `row-table` / `gate-table`。票根与齿孔由 `ticket-chrome` 画在每页 `background`。页脚只写在票根里。

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

客户可见品牌只写「青云未来」。禁止出现：青云知路、青云志愿。客户页不要写「知路」品牌后缀。

内部名禁止出现在封面、页眉、页脚、正文、票根、页码旁。

本季文种是选科指导报告。禁止做成冲稳保院校表。正文可以说「不开冲稳保」，但不要出现院校冲/稳/保分列。

禁止：录取概率、上岸率、保证上岸、一定录取、公章、国徽。

每份客户稿必须有：署名「青云未来」、票根「非正式官方文件 · 不保证录取」、免责四句、事实 / 判断 / 待核验。

本季不是三人经营讨论稿、不是返佣合同。

## 完成门槛

- A4 竖、正好 4 页（本季小样锁 4 页）
- 纸色 `#D08A72`、黑体题+行楷文、底 22mm 票根、齿孔撕线与 `visual-contract.md` 一致
- `self_check.py` 通过；`pdftotext` 无禁词，有「青云」「选科指导报告」「林同」
- 纸必须读红，不是砂褐、不是新闻粗米、不是浅青
- 可选中文；票根可读

## 本切片没做的

九套场景骨架、签发工作流、与 J/I/D/F 互编译、可勾选清单、冲稳保模块。O 研究稿不回写 studies。
