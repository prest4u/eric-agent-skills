---
name: eric-qingyun-plan-pdf
description: 【志愿方案】Create the 8-14 page 青云未来志愿方案报告 PDF for 出分后填报. Peak-season mother deliverable, not the default first file this season. Use when drafting 方案报告、志愿方案、冲稳保方案, or a family-facing 只读方案快照. Includes its own portable visual, ethics, build, and QA baseline. Must project volunteer D3. Do not invent admission probabilities or official seals.
---

# D4 志愿方案报告（旺季母本）

先读本包 `references/visual-contract.md` 与 `references/ethics.md`；`assets/theme.typ` 和 `scripts/` 让本 Skill 可独立使用。若安装了 `$eric-qingyun-pdf`，可只读核对共享版本，但不是运行依赖。出分填报旺季家庭主要买这一份。本季（9–10 月）默认先出选科报告，不要一上来脚手架本册。

## 何时用 / 不用

**用：** 出分后、志愿版 D3 已确认、复核后正式交付；每次修改出新版本，旧版不可覆盖。工作台导出的家庭只读快照也走本 skill。

**不用：** 售前说明；还没有志愿版 D3；只要填报勾选表（先有本册再出 D5）；选科阶段（`$eric-qingyun-subject-pdf`，不要塞冲稳保院校表）。

## 规格

- 读者：家长主读，讲解时打印或投影
- 8–14 页 A4 竖（到 16 须拆附录）
- 给人看的报告，但是签发件

## 页面建筑

1. Cover：案例、省年批次、版本、签发状态
2. How to read：FACT / JUDGEMENT / UNVERIFIED
3. 档案摘要（投影 D3）
4. 策略假设与停止条件（process）
5. 候选池总表（判断类型，不上色）
6. 2–4 组对照（argument，不写成好坏）
7. 排除清单
8. 下一步
9. 来源 + 签发栏

8 页以上必须有结论页和来源页。密表单独成页。

## 必须 / 禁止

必须：与 D3 一致的约束、判断类型操作定义、排除理由、待核验、免责四句、版本、身份页眉。

禁止：录取概率、交通灯、推荐指数、公章、未定品牌、内部词、真实姓名进文件名、覆盖旧版。

## 相邻文书

无 D3 不得称正式 D4。D5 只收本册已签发候选。D6 通过前文件名与封面只能当草稿。D7 从本册抽 5 个今晚决定，不另造表。

## 文件名

`方案报告-案例{ID}-{省}{年}-V{n}-YYYYMMDD.pdf`

## 工作流

```bash
python3 <eric-qingyun-pdf>/scripts/new_document.py \
  --scene plan --out <fresh-dir> --title "方案报告" \
  --case-id "案例合成-TJ2026-0042" --alias "林同"
typst compile document.typ document.pdf
pdftoppm -png -r 144 document.pdf _qa/page
python3 <eric-qingyun-pdf>/scripts/check_pdf.py --pdf document.pdf --scene plan
```

默认合成数据。换真实家庭前须有授权，且仍用化名，除非 Eric 明确要求实名。

## 验收

前两屏有身份与「不保证录取」。冲稳保无彩灯。有待核验和排除清单。灰印表线仍在。D3 数字与约束对得上。
