---
name: eric-qingyun-signoff-pdf
description: 【复核签发】Create the 1-2 page 青云未来复核签发单 PDF. Use when an advisor is about to issue a formal 选科报告, volunteer plan, or checklist, or when making 签发单、复核单. Includes its own portable visual, ethics, build, and QA baseline. No signoff means the PDF is not formal. Do not use for the family-facing report body.
---

# D6 复核签发单

先读本包 `references/visual-contract.md` 与 `references/ethics.md`；`assets/theme.typ` 和 `scripts/` 让本 Skill 可独立使用。若安装了 `$eric-qingyun-pdf`，可只读核对共享版本，但不是运行依赖。没有本页，选科报告 / D4 / D5 只能叫草稿。工作台导出前也走这一闸门。

## 何时用 / 不用

**用：** 导出正式选科报告、D4、D5 前的内部闸门；必要时向家长出示「谁签的」。

**不用：** 代替方案报告；还没做复核检查。

## 规格

- 读者：主顾问、制作人、复核人
- 1–2 页 A4 竖
- 内部文书，可附在交付包首页之后

## 页面建筑

1. Cover：案例、对应版本、不得覆盖
2. 检查项勾选 + 双人签字 + 免责

## 必须 / 禁止

必须：约束一致、来源年份、无概率承诺、未核验未当事实、不得覆盖、签发人与日期。

禁止：改写 D4 内容、用签发单承诺录取、覆盖旧版文件。

## 相邻文书

D6 通过后，选科报告 / D4 / D5 封面才可写「已签发」。已交付版本只出 Vn+1。

## 文件名

`签发单-案例{ID}-V{n}-YYYYMMDD.pdf`

## 工作流

`--scene signoff`，`check_pdf.py --scene signoff`。

## 验收

有「不得覆盖」和双人签字栏。无学生志愿大表。
