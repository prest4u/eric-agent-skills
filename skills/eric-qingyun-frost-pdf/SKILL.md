---
name: eric-qingyun-frost-pdf
description: 【霜蓝通缘】青云选科指导报告 Typst 皮：霜蓝纸、右缘涂布色条、魏碑标题。适合需要通缘识别的选科报告；客户可见只写青云未来。
---

# 青云 · 霜蓝通缘

先用这张皮，当选科指导报告要做成霜蓝卡、右缘 28mm 涂布色条、魏碑标题。识别靠色条里的竖排「青云」，不是顶通栏，不是浅青卡。本 skill 是最小切片：可发现、可编译、可自检。没有九套场景模板。

**不是识别册。** 浅青卡 `#DDE8E4`、顶通栏 9mm、全无衬线苹方、品牌青 `#2F4A47`，全部不要当别名复活。也不要做成雾蓝白左轨、冷墨、编辑纸本。

## 何时用

- 文种是 **选科指导报告**（本季主交付）
- 需要霜蓝纸面 + 右缘通高色条 + 魏碑大标题
- 气质：**霜蓝通缘** — 纸是蓝，条在右，字是魏碑/黑体。不要医院绿，不要密表填色，不要案卷栏轨，不要识别册顶通栏

## 何时不用

| 场景 | 改用 |
|---|---|
| 识别册：浅青卡 + 顶通栏反白「青云」+ 全无衬线 | `$eric-qingyun-teal-pdf`（方案 D 识别册） |
| 整套客户 PDF 基线、签发/清单、雾蓝白案卷 | `$eric-qingyun-pdf` / `$eric-slate-white-pdf`（方案 A） |
| 确认书、出分后密件、冷墨事务所 | `$eric-qingyun-cold-ink-pdf` |
| 选科长文、来源页、爱读书家长 | `$eric-qingyun-editorial-pdf`（方案 E） |
| 家长说明、题签楷体 | `$eric-qingyun-parent-pdf` |
| 志愿冲稳保表 / 院校专业网格 | `$eric-qingyun-plan-pdf`；选科件禁止冲稳保 |
| 三人经营讨论稿、计点方案 | 内部稿，不是本家族 |
| 渠道返佣 / 机构返点合同 | 律师稿，不是本家族 |
| 英语教材、OCR、合并拆分 | `$eric-designed-pdf` / `$pdf` |

## 怎么编译

在本 skill 根目录：

```bash
bash scripts/compile.sh
```

或：

```bash
typst compile --root . samples/选科指导报告-小样.typ samples/选科指导报告-小样.pdf
```

新稿：复制 `theme.typ` 到项目目录，`#import "theme.typ"`，封面用 `cover-page`，内页用同一套 `right-strip`（经 `qingyun-doc`），表用 `row-table` / `gate-table`。署名写「青云未来」。事实另放，不要写进 theme。

必须带 `--root`，因为小样是 `#import "/theme.typ"`。

## 视觉合同

先读 `references/visual-contract.md`，再改字。Token 锁定 `theme.typ`。禁止把识别册换个蓝色交差，禁止做成 A 雾蓝白的蓝色版。

## 品牌禁印

署名（正文、页码旁）写 **青云未来**；封面/色条中的竖排「青云」为版式识别元素，保留不动。

禁止出现：

- 青云知路
- 青云志愿

也不要印竞品全称、公章、录取概率、真名。不要印 DOCUMENT / STATUS 铬条。不要把内部底盘名印到客户 PDF。

## 自检

```bash
bash scripts/check.sh
```

过关条件：

1. `SKILL.md` 有 YAML `name` + `description`，可被 agent 发现
2. 小样 PDF 存在且正好 4 页
3. `pdftotext` / `strings` 不含禁印品牌串，也不含 DOCUMENT / STATUS 铬条
4. `theme.typ` 含霜蓝纸 `#C5D4E0`、右缘 `28mm`、`Weibei`；不含识别册纸色、`rail-head`、`mark-square`
5. `typst compile --root` 成功

目检：纸是霜蓝（不是青/绿）；右缘通高色条约 28mm；标题魏碑；无顶通栏、无左轨、无 DOCUMENT/STATUS。
