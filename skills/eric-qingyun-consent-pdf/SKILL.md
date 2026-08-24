---
name: eric-qingyun-consent-pdf
description: 【服务确认】Create the 4-6 page 青云未来服务确认 / 知情同意 PDF. Default this season is 选科指导签约. Use when a family is about to pay or sign, or when making 确认书、知情同意、服务协议. Includes its own portable visual, ethics, build, and QA baseline. Not legal advice; mark 待专业审查. Do not use for the volunteer plan or a sales brochure.
---

# D2 服务确认 / 知情同意

先读本包 `references/visual-contract.md` 与 `references/ethics.md`；`assets/theme.typ` 和 `scripts/` 让本 Skill 可独立使用。若安装了 `$eric-qingyun-pdf`，可只读核对共享版本，但不是运行依赖。本文件是给人交的确认书，**不是已审法律意见**。

## 何时用 / 不用

**用：** 收款前后需要签字留档。本季默认服务范围写选科指导，不要默认写成出分填报套餐。

**不用：** 只是介绍服务（D1）；还没定周期/修改/退款数字时，可以出模板但必须标明数字待定，不得假装已报价。

## 规格

- 读者：监护人签、顾问留档
- 4–6 页 A4 竖
- 给人交的文书（待专业审查）

## 页面建筑

1. Cover：文种 +「非正式法律文本，待专业审查」
2. 当事人与服务范围
3. 周期、价款、资料用途与保留、对外提供须单独同意
4. 知情四句 + 签字栏

## 必须 / 禁止

必须：待专业审查、含/不含、监护人签字、未成年人监护同意提示、免责四句、家庭作最终决定。

禁止：保证录取、冒充律师已审、公章拟态、把未定价格写成已生效。

## 相邻文书

D1 说明范围，D2 签字。D3 另签约束。不要把方案表订进确认书。

## 文件名

`服务确认书-案例{ID}-V{n}-YYYYMMDD.pdf`

## 工作流

`--scene consent`，然后 `check_pdf.py --scene consent`。

## 验收

封面或首页可见「待专业审查」。有签字栏。无概率承诺。数字空缺须明示。
