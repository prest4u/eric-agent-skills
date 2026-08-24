# 视觉合同 · 青云编辑纸本

锁死对象：2026-08-19 视觉方案 E。字号、边距、页眉页脚、封面语法摘自

The reviewed internal study is not distributed. This contract and `theme.typ` are the portable authority.

客户纸色由 Document Master 终审改锁为冷灰书纸 `#E6E4DE`，必须离开 C 的 `#F3F3F1`。研究稿 L6 仍是 `#F3F3F1`，不要回写研究稿。父级 README 把 E 写成「冷灰书纸、宋体章节、少铬条」。

禁止发明第二套品牌色，禁止把 A/B/C/D 的栏轨或结构色搬进来。

## 纸色与墨

| token | hex | 来源 |
|---|---|---|
| `paper` | `#E6E4DE` | Document Master 终审（客户稿）。备选曾列 `#E0DDD6`，本皮锁前者。研究稿 L6 仍是 `#F3F3F1`，勿回写。 |
| `ink` | `#262626` | L7 |
| `muted` | `#6B6B6B` | L8 |
| `micro` | `#707070` | L9 |
| `hair` | `#C8C8C4` | L10 |

没有 `primary` / `secondary`。不要加苔绿、浅青、雾蓝栏轨色。

纸色口头叫「冷灰书纸」`#E6E4DE`，**不是** B 的暖象牙 `#F6F3EA`，也**不是** C 的近白纸 `#F3F3F1`。研究稿与 C 曾共用 `#F3F3F1`；客户稿必须离开该 hex。字/网格/封面语法仍按研究稿，不要为了换纸去改边距或宋体章节。

## 字体栈

| 角色 | 栈 | 研究稿 |
|---|---|---|
| 正文 / 标题 / 页眉页脚 | `Songti SC`, `STSong` | L12, L51 |
| 封面方案微标（仅此一处 sans） | `PingFang SC`, `Hiragino Sans GB` | L13, L74 |
| 拉丁 / Avenir | **不用** | E 未声明 `latin` |

正文字号 10.5pt，`tracking: 0.02em`，`lang: "zh"`。段落两端对齐，`leading: 1.05em`，`spacing: 0.85em`，首行缩进 2em（L51–52）。

章节：中文数字 22pt 粗 + 标题 16pt 粗，下跟 22mm、0.6pt `ink` 短线（L54–66）。不要 01 栏轨编号，不要拉丁 kicker。

封面主标题 30pt 粗、`tracking: 0.08em`；机构名「青云」11pt、`tracking: 0.42em`（L72–76）。

## 页边距与纸张

A4 竖。`margin: (top: 26mm, bottom: 24mm, left: 28mm, right: 28mm)`（L26）。比 A/B/D 的 24/22/25/25 更宽，比 C 的 18mm 松得多。

## 铬条策略（少铬条）

允许：

- 章节下 22mm 墨线
- 封面 18mm、0.55pt 墨线
- 页眉下 0.4pt `hair` 横线
- 门表只有横向 hairline：`stroke: (x: none, y: 0.4pt + hair)`，`inset: (x: 0mm, y: 3.2mm)`（L120–123）

禁止：

- A/B/D 的 16mm 左栏轨 + 竖线（A `theme.typ` `rail-head` L43–56）
- A/B/D 的双色 `split-rule`（A L38–42）
- D 页眉 2.4mm 浅青方块（D `document.typ` L44）
- 拉丁 eyebrow / `QINGYUN OPINION`（C L77）
- 填色卡片、可勾选框、红黄绿、冲稳保上色

## 页眉页脚

封面：`header: none, footer: none`（L68）。

第 2 页起页眉：宋体 8pt `micro`，左「选科指导报告」，右「化名 · 省」，下 0.4pt hair 线（L27–37）。

第 2 页起页脚：宋体 8pt `micro`，左「青云 · 编辑纸本」（研究稿写「青云 · 视觉方案 E · 编辑纸本」，客户稿去掉「视觉方案 E」），中「非正式官方文件 · 不保证录取」，右中文页码 `counter(page).display("一")`（L39–48）。不要 `01` 阿拉伯页码。

## 与 A/B/C/D 的硬差异

1. **纸色与边距**：客户稿 E `#E6E4DE` + 26/24/28/28mm（边距仍是 E L26）。A `#F4F5F3` + 24/22/25/25（A `theme.typ` L4, L83）。B 暖象牙 `#F6F3EA`（B `theme.typ` L4）。D `#F4F6F5`（D L6）。C `#F3F3F1` + 18mm（C L6, L30）。纸必须离开 C。
2. **无栏轨 / 无结构色**：A/B/D 有 `primary` 与 `rail-head`（A L9–10, L43–56；D L11–12, L69–75）。E 不声明 `primary`，章节只靠宋体号 + 短墨线（E L54–66）。
3. **宋体书页 vs 咨询铬条**：E 正文宋体 10.5pt、首行缩进 2em、页眉页脚也是宋体、中文页码（E L51–52, L29, L46）。A 页眉苹方 7pt、页码 `01`、拉丁 label（A L87–98）。C 更密 9.2pt、sans 微字、拉丁 kicker（C L18–19, L58, L77）。B 暖象牙 + 苔绿栏轨 + 仿宋 pull quote（B L4, L9, L38–41）。

父级 README 对照：`qingyun-pdf-visual-studies/2026-08-19/README.md`。

## 禁词

客户可见只写「青云未来」。禁止：青云知路、青云志愿。

禁止：上岸率、录取概率、保证上岸、一定录取、公章、国徽。

## 不是什么文种

- 不是志愿冲稳保表、不是填报执行清单
- 不是可勾选核对表
- 不是确认书 / 签发单（偏 C）
- 不是三人经营讨论稿、不是渠道返佣合同
- 不是英语教材、不是讲座幻灯

本季只做选科指导报告。门表只谈门是否被关上，不上色，不开院校冲稳保。
