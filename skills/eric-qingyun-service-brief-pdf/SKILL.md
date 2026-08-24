---
name: eric-qingyun-service-brief-pdf
description: 【服务说明】Create the 2-4 page 青云未来服务说明与边界 PDF. Default this season is 选科指导售前. Use when a parent asks what 青云未来 includes before paying, or when making 服务说明、边界、售前说明. Includes its own portable visual, ethics, build, and QA baseline. Do not use for the signed confirmation, volunteer plan, or English teaching PDFs.
---

# D1 服务说明与边界

先读本包 `references/visual-contract.md` 与 `references/ethics.md`；`assets/theme.typ` 和 `scripts/` 让本 Skill 可独立使用。若安装了 `$eric-qingyun-pdf`，可只读核对共享版本，但不是运行依赖。用本包脚本脚手架，不要用雾蓝白散文 starter。

## 何时用 / 不用

**用：** 面谈前、微信先发、老师转介绍后家长还没付钱。本季默认写选科指导，不默认一对一志愿填报。

**不用：** 已决定签约（改 D2）；已有学生约束（改 D3）；要具体院校表（改旺季 D4）；早鸟定金说明（`--scene early-bird`）。

## 规格

- 读者：家长（学生可旁观）
- 2–4 页 A4 竖
- 给人看的说明，不是文书

## 页面建筑

1. Cover：一句话服务 + 不保证录取
2. 含什么 / 不含什么（argument）
3. 下一步：确认书 → 建档（process）
4. 可选：周期与讲解次数（数字未定就写「另行约定」）

## 必须 / 禁止

必须：含什么、不含什么、不代填官方系统、不承诺录取、免责四句、署名「青云未来」。

禁止：具体院校、冲稳保表、价格假装已定、青云知路/青云志愿、法律腔假装已审合同。

## 相邻文书

本文件打开门。D2 才签字。不要把 D1 和 D2 订成一份冒充合同。

## 文件名

`服务说明-选科指导-v1-YYYYMMDD.pdf`
志愿旺季售前：`服务说明-志愿咨询-v1-YYYYMMDD.pdf`

## 工作流

```bash
python3 <eric-qingyun-pdf>/scripts/new_document.py \
  --scene service-brief --out <fresh-dir> --title "服务说明与边界"
typst compile document.typ document.pdf
python3 <eric-qingyun-pdf>/scripts/check_pdf.py --pdf document.pdf --scene service-brief
```

## 验收

微信前两屏能读到「不保证录取」。灰印可读。无院校表、无概率、无真名。
