# 视觉合同 · 青云墨底夜页

第二轮底盘 G。无研究稿文件夹，按本文件与 brief 执行。不是 C 冷墨意见书的换色，也不是 A–E 近白纸的反相滤镜。

皮肤内部名「墨底夜页」只留在本 skill / 本契约，**客户 PDF 不得印「墨底夜页」「冷墨事务所」**。

## 四硬差（主差正好四条）

1. 满版墨底 #2B2E2C + 反白字 #E8E6E1（对照第一轮 A–E 近白/象牙/灰书纸）
2. 封面满版海报：中部反白「选科」、左下「青云」（对照 C 的 QINGYUN OPINION 三栏、A/D 栏轨封面）
3. 左窄文柱约 110mm + 右侧大留白（对照 C 18mm 全宽、A 16mm 栏轨）
4. 表只用反白行线，禁止 18mm 全框表（对照 C 细线封闭表）

## 纸与墨

| token | hex | 角色 |
|---|---|---|
| `paper` | `#2B2E2C` | 满版墨底夜场。整页 fill，不是近白纸 |
| `inverted` | `#E8E6E1` | 标题、行线、强调反白 |
| `body-ink` | `#B8B5AE` | 浅灰宋正文。不要用纯白铺正文 |
| `micro` | `#8A8882` | 标签、页眉页脚、微字 |
| `rule` | `#C8C5BE` | 表的反白横行线 |

没有 `primary` / `secondary`。不要雾蓝、苔绿、浅青、石板蓝、teal。不要 SW / MI 标记。

## 字体栈

| 角色 | 栈 | 填色 |
|---|---|---|
| 标题 / 封面「选科」/ 节题 | PingFang SC / Hiragino Sans GB，heavy/bold | `#E8E6E1` |
| 正文 | Songti SC / STSong | `#B8B5AE` |
| 微字 / 标签 / 页眉页脚 | PingFang SC / Hiragino Sans GB | `#8A8882` |
| 拉丁 fallback | Avenir Next / Helvetica Neue | 少用 |

禁止印 `QINGYUN OPINION`。不要用拉丁 kicker 当封面语法。

正文约 10pt，`lang: "zh"`，两端对齐。不要 E 的首行缩进书页。不要 C 的 9.2pt/0.86em 密排。

## 网格

A4 竖。

- 内页：左边约 14–16mm，顶约 16–18mm，底 ≥18mm。页脚文字距裁切 ≥8mm（footer `pad(bottom: 8mm)`）。
- 正文落在左侧约 **110mm** 文柱（`block`/`box` 定宽），右侧大留白。除封面外，内容不要爬进右空。
- 不是 16mm 左编辑栏轨，不是 C 的 18mm 全宽密页，不是 22mm 标签列 + hairline 条目栈。

## 封面

满版墨底海报。`margin: 0`，整页 fill `#2B2E2C`。无页眉页脚。

- 中部（或居中）反白「选科」，粗黑，约 64–80pt。主标题就是这两个字，不是「选科指导报告」。
- 「指导报告」可作微字落在大字下。
- 左下「青云」sans。
- 安静一行案例：`案例号 · 化名 · 省 · 高一选科`。
- 第一屏必须有微字「不保证录取」。

禁止：QINGYUN OPINION、三栏封面元数据、双线意见书封面、栏轨封面、题签封面。

## 表

`row-table`：只有横向发丝线，`0.3–0.4pt`，`#E8E6E1` 或 `#C8C5BE`。

`stroke: (x: none, y: 0.35pt + rule)`。

禁止：全框描边、18mm 细线封闭网格、单元格填色、红黄绿色灯、冲稳保院校表。

## 页眉页脚（第 2 页起）

- 页眉：`案例号 化名 省 批次 | 青云`（落在左文柱宽内）
- 页脚：`青云 | 非正式官方文件 · 不保证录取 · 以签发版为准 | 页码`

封面无页眉页脚。

## 铬条禁则（对照第一轮 A–E）

- 无左 16mm 编辑栏轨
- 无石板蓝 / 苔绿 / 浅青强调色
- 无 SW / MI 标记
- 无书籍首行缩进章节页
- 无双线意见书封面
- 无从 C 抄来的 22mm 标签 + hairline 条目栈

## API

`theme.typ` 必须提供：`night-page`、`cover-poster`、`row-table`、`section-head`、`sign-block`、`disclaimer-lines`、`studio-name`、`skin-internal`。

`skin-internal` 只作内部名，**永不打印**。不要 `#import` 冷墨或雾蓝白 theme。

## 禁词（客户 PDF）

青云知路、青云志愿、冷墨事务所、墨底夜页、QINGYUN OPINION、上岸率、录取概率、保证上岸、一定录取、公章、国徽、fixture、SaaS、高考（正文）。

客户可见机构名只写「青云未来」。
