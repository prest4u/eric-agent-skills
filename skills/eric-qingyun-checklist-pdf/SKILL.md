---
name: eric-qingyun-checklist-pdf
description: 【填报清单】Create the 2-6 page 青云未来填报执行清单 PDF for 出分后志愿填报. Use when a family will tick volunteer rows against the official system, or when making 填报清单、志愿顺序表、执行清单. Includes its own portable visual, ethics, build, and QA baseline. Only include candidates already issued in D4. Not an official form. Not for 选科.
---

# D5 填报执行清单

先读本包 `references/visual-contract.md` 与 `references/ethics.md`；`assets/theme.typ` 和 `scripts/` 让本 Skill 可独立使用。若安装了 `$eric-qingyun-pdf`，可只读核对共享版本，但不是运行依赖。这是对着官方系统勾的作业单。

## 何时用 / 不用

**用：** D4 已签发，家庭要按顺序填官方栏位。

**不用：** 还在讲道理（用 D4）；代替官方志愿表；一页硬塞 50 行（分组加页）。

## 规格

- 读者：出分后填报的家长/学生
- 2–6 页 A4 竖
- 给人用的清单，必须能手写勾

## 页面建筑

1. Cover：对应方案版本、批次窗口提醒
2. 志愿顺序表（序号、专业组、判断类型、服从调剂空位）
3. 填前五道检查 + 免责

## 必须 / 禁止

必须：只收 D4 已签发候选、服从调剂栏、五道检查、免责四句、版本对应关系。

禁止：新加 D4 没有的学校、概率、把清单设计成官方表格仿造。

## 相邻文书

候选与顺序以签发 D4 为准。约束以 D3 为准。无 D6 不得称正式清单。

## 文件名

`填报清单-案例{ID}-V{n}-YYYYMMDD.pdf`

## 工作流

`--scene checklist`，`check_pdf.py --scene checklist`。

## 验收

可打印勾选。灰印序号仍清。无彩灯。前两屏能看到对应方案版本。
