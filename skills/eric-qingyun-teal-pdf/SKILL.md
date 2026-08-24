---
name: eric-qingyun-teal-pdf
description: 【青云识别册】浅青灰卡纸、顶通栏 9mm 反白「青云」、全无衬线。用于需要在册面快速识别青云未来的选科指导 PDF；客户可见只写青云未来。
---

# 青云识别册｜选科指导报告

先用这张皮，当客户必须在册面认出「青云」。纸本身是浅青灰卡，不是近白纸上的青色点缀。识别靠顶通栏反白「青云」，不是方块、不是左「青」字柱。本 skill 是最小切片：可发现、可编译、可自检。没有九套场景模板。

**旧 D 已死。** 近白纸 `#F4F6F5` / `#F5F6F4`、浅青方块、细轨、左「青」柱、右页签、宋体标题、封面 DOCUMENT/STATUS，全部废止，不要当别名复活。

## 何时用

- 文种是 **选科指导报告**（本季主交付）
- 需要品牌可识别：浅青灰卡 + 顶通栏反白「青云」+ 大号无衬线标题
- 气质：**青云识别册** — 浅青灰卡、全无衬线、顶通栏、行底线表。不要医院绿，不要密表填色，不要案卷栏轨

## 何时不用

| 场景 | 改用 |
|---|---|
| 整套客户 PDF 基线、签发/清单、雾蓝白案卷 | `$eric-qingyun-pdf` / `$eric-slate-white-pdf`（方案 A） |
| 分栏纪录纸、确认书、出分后密件 | 方案 C，不是本皮 |
| 选科长文、来源页、爱读书家长 | 方案 E 编辑纸本 |
| 售前说明册、偏文科读本 | `$eric-moss-ivory-pdf`（方案 B） |
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

新稿：复制 `theme.typ` 到项目目录，`#import "theme.typ"`，封面用 `cover-page`，内页用同一套 `top-band`（经 `qingyun-doc`），表用 `row-table` / `gate-table`。署名写「青云未来」。事实另放，不要写进 theme。

## 视觉合同

先读 `references/visual-contract.md`，再改字。Token 锁定 `theme.typ`。禁止把旧 D 换个颜色交差，禁止做成 A 雾蓝白的青色版。

## 品牌禁印

署名（页眉、页脚、正文、页码旁）写 **青云未来**；封面通栏美术字为版式元素，保留「青云」。

禁止出现：

- 青云知路
- 青云志愿

也不要印竞品全称、公章、录取概率、真名。不要印 DOCUMENT / STATUS 铬条。

## 自检

```bash
bash scripts/check.sh
```

过关条件：

1. `SKILL.md` 有 YAML `name` + `description`，可被 agent 发现
2. 小样 PDF 存在且正好 4 页
3. `pdftotext` / `strings` 不含禁印品牌串，也不含 DOCUMENT / STATUS 铬条
4. `theme.typ` 不含旧 D 函数与近白纸色
5. `typst compile --root` 成功

目检：纸是浅青灰卡，不是近白；顶通栏反白「青云」；标题无衬线；表只有行底线；没有方块、没有左轨、没有 DOCUMENT/STATUS。
