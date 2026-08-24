---
name: eric-qingyun-briefing-pdf
description: 【家长讲解提纲】Create the 2-page 青云未来家长讲解提纲 PDF. Use when preparing a live 选科 or 志愿 briefing, 讲解提纲, or tonight-only decision list. Includes its own portable visual, ethics, build, and QA baseline. Pull from the issued subject report or D4; do not replace it. Do not add new schools or promises.
---

# D7 家长讲解提纲

先读本包 `references/visual-contract.md` 与 `references/ethics.md`；`assets/theme.typ` 和 `scripts/` 让本 Skill 可独立使用。若安装了 `$eric-qingyun-pdf`，可只读核对共享版本，但不是运行依赖。现场防顾问临场加承诺。

## 何时用 / 不用

**用：** 讲解当晚，顾问自己拿着或投两页。本季可从已签发选科报告抽 5 个今晚决定。

**不用：** 当主交付发给家长代替选科报告或 D4；现场发明新院校或新科目组合。

## 规格

- 读者：顾问（家长可看，但不是主文件）
- 正好 2 页 A4 竖
- 提纲，不当主交付

## 页面建筑

1. Cover：对应方案版本 + 今晚只决定这些
2. 五件事：约束、类型、争议、待核验、下一步 + 免责

## 必须 / 禁止

必须：从已签发选科报告或 D4 抽取、写明「不保证录取」、列出待核验。

禁止：新候选、新科目组合、概率、把提纲写成第二份方案。

## 相邻文书

科目、数字和学校名必须能在对应主交付里找到。讲解后的改口记回 D3 与下一版本。

## 文件名

`讲解提纲-案例{ID}-V{n}-YYYYMMDD.pdf`

## 工作流

`--scene briefing`，`check_pdf.py --scene briefing`。

## 验收

正好两页。有「今晚」。无新表、无概率。
