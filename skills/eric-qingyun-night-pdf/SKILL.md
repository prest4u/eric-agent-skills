---
name: eric-qingyun-night-pdf
description: 【墨底夜页】制作青云未来深色满版选科 PDF：墨底、反白字、左 110mm 文柱与夜间海报式封面。适合明确要求深色底盘的选科指导报告；客户可见只写青云未来。
---

# 青云 · 墨底夜页

本 Skill **只做皮肤 G 的视觉与选科样本**，并可独立运行。若安装了 `$eric-qingyun-pdf`，可只读核对共享路由，但不是运行依赖。本皮不是 C 冷墨意见书的换色。

**禁止改** `$eric-qingyun-cold-ink-pdf`、`$eric-qingyun-pdf`、雾蓝白 / 苔绿 / 浅青 / 编辑纸本 / 家长说明册，以及 A–E 研究稿。

## 何时用 / 不用

**用：** 选科指导报告，要满版墨底、反白字、左窄文柱。

**不用：**

- 冷墨意见书 / 确认书 / 签发单 → `$eric-qingyun-cold-ink-pdf`（不要改那条皮）
- 雾蓝白案卷 → `$eric-qingyun-pdf`
- 家长说明册 → `$eric-qingyun-parent-pdf`
- 浅青品牌封面 → `$eric-qingyun-teal-pdf`
- 选科长文编辑纸本 → `$eric-qingyun-editorial-pdf`
- 志愿冲稳保表、院校名单、英语教材、AI 幻灯、返佣合同、三人经营稿
- 本切片未做的场景：service-brief / consent / profile / plan / checklist / signoff / briefing / teacher / early-bird

## 工作流

1. 脚手架（目录必须是新的，且不能落在 skill/plugin 根下）：

```bash
python3 <eric-qingyun-night-pdf>/scripts/new_document.py \
  --scene subject \
  --out <fresh-project-dir> \
  --title "选科指导报告"
```

2. 改 `document.typ`，保留 `#import "theme.typ"`。
3. `typst compile document.typ document.pdf`
4. `python3 <本skill>/scripts/check_pdf.py --pdf document.pdf --scene subject --expect-pages 4`
5. 复核：重新运行本包的 `check_pdf.py`，并目检每一页。

## 主题锁定

先读 `references/visual-contract.md`。色值、文柱、满版封面、行线表只许按合同。

- 纸 / 页底 `#2B2E2C`；反白 `#E8E6E1`；正文浅灰宋 `#B8B5AE`；微字 `#8A8882`
- 标题粗黑反白（苹方 / 冬青黑）；正文宋体；拉丁 Avenir Next 少用
- 内页左文柱约 110mm，右侧大留白
- 表：只有反白横行线，无全框、无填色、无色灯
- 封面：满版海报，中部「选科」，左下「青云」
- 客户可见只写「青云未来」。皮肤内部名「墨底夜页」不得印到 PDF

## 每份客户 PDF 必有

「非正式官方文件」「不保证录取」、免责四句、事实 / 判断 / 待核验、选科、待观察。首页微字见「不保证录取」。

免责四句原文（勿改）：

1. 本文件不是教育考试院或高校官方文件。
2. 本文件不构成录取、就业或薪资承诺。
3. 最终以当年官方系统、招生计划和高校招生章程为准。
4. 过期、缺失或相互冲突的数据，不得当作已核实事实。

## 命名

```
选科指导-案例合成TJ2026-0042-天津2026-V1-20260819.pdf
```

## 完成门槛

A4、4 页、`check_pdf.py --scene subject` 通过、可选中文、字体嵌入且有 Unicode。无全称品牌、无概率、无公章、无真名、无皮肤名。

本切片不做九套场景。不要回写其他青云皮。
