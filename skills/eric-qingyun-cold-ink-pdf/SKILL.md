---
name: eric-qingyun-cold-ink-pdf
description: 【冷墨事务所】制作青云未来密排细线意见备忘式 PDF，适用于选科指导报告、确认书、签发单与出分后方案。近白冷纸、无栏轨、无强调色；客户可见只写青云未来。
---

# 青云 · 冷墨事务所

本 Skill 只做皮肤 C 的视觉与选科样本，并可独立运行。若安装了 `$eric-qingyun-pdf`，可只读核对共享路由，但不是运行依赖。不要改其他 Skill。

## 何时用 / 不用

**用：** 选科指导报告、确认书、签发单、出分后方案。更密、细线、意见备忘。近白冷纸，无栏轨，无结构色。

**不用：**

- 雾蓝白案卷 → `$eric-qingyun-pdf` / `$eric-slate-white-pdf`
- 苔绿象牙家长说明册 → `$eric-moss-ivory-pdf`
- 志愿冲稳保表、院校名单
- 英语教材、AI 幻灯、留学合同、返佣合同、三人经营稿
- 本切片未做的场景：service-brief / consent / profile / plan / checklist / signoff / briefing / teacher / early-bird

## 工作流

1. 脚手架（目录必须是新的，且不能落在 skill/plugin 根下）：

```bash
python3 <eric-qingyun-cold-ink-pdf>/scripts/new_document.py \
  --scene subject \
  --out <fresh-project-dir> \
  --title "选科指导报告"
```

2. 改 `document.typ`，保留 `#import "theme.typ"`。
3. `typst compile document.typ document.pdf`
4. `python3 <本skill>/scripts/check_pdf.py --pdf document.pdf --scene subject`

## 主题锁定

- paper `#F3F3F1` / ink `#1F2122` / muted `#5E6366` / micro `#6A6F72` / hair `#B8BDBE` / rule `#2A2D2E`
- 宋体 9.2pt、tracking 0.006em、行距 0.86em、段距 0.52em、两端对齐
- 边距 18 / 16 / 18 / 18 mm；hairline 0.35pt；标签列 22mm
- 封面双线：0.55pt rule 通栏 + 0.35pt hair 36mm
- 无左栏轨、无结构色、无填色卡片、无冲稳保色灯

## 每份客户 PDF 必有

身份页眉（第 2 页起）、页脚「青云未来 · 非正式官方文件 · 不保证录取」、免责四句、事实 / 判断 / 待核验。

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

A4、typst 已编译、`check_pdf.py --scene subject` 通过、可选中文、字体嵌入且有 Unicode。前两屏能看到「青云」和「不保证录取」。无全称品牌、无概率、无公章、无真名。

Gate ledger：`Scope / Scene / Fresh compile / check_pdf / Rendered pages / Ethics / Remaining risk`

不要改其他青云或通用 PDF Skill。
