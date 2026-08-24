#import "theme.typ": *

#show: qingyun-document.with(
  title: "__TITLE__",
  subtitle: "合成案例 · 只供版式与流程核验",
  case-id: "__CASE_ID__",
  student-alias: "__ALIAS__",
  province: "__PROVINCE__",
  year: "__YEAR__",
  batch: "__BATCH__",
  version: "__VERSION__",
  doc-date: "__DATE__",
  kind: "方案报告",
)

#cover-page(
  [ERIC SLATE WHITE PDF · 志愿方案报告],
  [方案报告],
  [把事实、判断和待核验分开写清。本册是顾问签发的阅读件，不是官方志愿表。],
  [__CASE_ID__\__ALIAS__ · __PROVINCE____YEAR____BATCH__\版本 __VERSION__ · __DATE__],
  [合成数据\非正式官方文件\不保证录取\以签发版为准],
)

#pagebreak()
#rail-head(
  [01],
  [HOW TO READ],
  [怎么读这份报告],
  premise: [先看约束是否仍是家庭原意，再看判断类型，最后才看具体院校专业组。],
)
#v(9mm)
#pad(left: 26mm)[
  #evidence-row([FACT], [可回官方核对的成绩位次、选科、章程限制、学费与校区。])
  #evidence-row([JUDGEMENT], [顾问对冲、稳、保的归类，以及纳入或排除的理由。], tone: secondary)
  #evidence-row([UNVERIFIED], [缺年份、缺来源、互相冲突、或尚未核对章程的条目。])
  #v(4mm)
  #side-note([判断类型], [冲、稳、保是判断类型，不是录取率。归类依据是往年位次相对孩子今年位次，且组内最差专业家庭仍可接受。])
]

#pagebreak()
#rail-head(
  [02],
  [PROFILE],
  [档案摘要],
  premise: [本页必须与已确认的档案一致。若家庭改过约束，先改档案确认，再改本报告。],
)
#v(9mm)
#pad(left: 26mm)[
  #rule-row([位次口径], [合成位次 18420 · __PROVINCE__ · __YEAR__ · 查询日 __DATE__ · 来源：合成演示，非正式统计])
  #rule-row([选科], [物理、化学、地理], tone: secondary)
  #rule-row([硬约束], [可出津；不接受组内含家庭明确拒绝的专业；学费需事先说清])
  #rule-row([软偏好], [偏工程与城市资源，不把校名当作唯一目标], tone: secondary)
  #rule-row([待补], [目标专业组章程尚未逐条核对])
]

#pagebreak()
#rail-head(
  [03],
  [STRATEGY],
  [策略假设与停止条件],
  premise: [假设不成立时，停止使用本版，而不是继续往表里加学校。],
)
#v(10mm)
#pad(left: 26mm)[
  #numbered([1], [假设], [家庭接受出津，且组内最差专业可接受。])
  #v(7mm)
  #numbered([2], [排序逻辑], [先约束，再判断类型，再看城市与培养条件。], tone: secondary)
  #v(7mm)
  #numbered([3], [停止], [出现新的章程限制、位次口径变更、或家庭改口绝对不接受某专业。])
]

#pagebreak()
#rail-head(
  [04],
  [CANDIDATE POOL],
  [候选池总表],
  premise: [下表是合成条目，用来示范版式。正式交付必须换成经允许使用的当年数据。],
)
#v(8mm)
#pad(left: 26mm)[
  #grid(
    columns: (14mm, 18mm, 1fr, 28mm, 28mm),
    gutter: 3mm,
    [#label([类型])], [#label([序号])], [#label([院校专业组（合成）])], [#label([往年位次])], [#label([状态])],
  )
  #v(3mm)
  #line(length: 100%, stroke: 0.5pt + hair)
  #v(4mm)
  #grid(columns: (14mm, 18mm, 1fr, 28mm, 28mm), gutter: 3mm,
    [#judgment-mark("冲")], [01], [合成大学甲 · 工科组 A], [约 1.6 万], [#quiet([待核验])])
  #v(3.5mm)
  #line(length: 100%, stroke: 0.5pt + hair)
  #v(3.5mm)
  #grid(columns: (14mm, 18mm, 1fr, 28mm, 28mm), gutter: 3mm,
    [#judgment-mark("稳")], [02], [合成大学乙 · 电子信息组], [约 1.9 万], [#quiet([判断])])
  #v(3.5mm)
  #line(length: 100%, stroke: 0.5pt + hair)
  #v(3.5mm)
  #grid(columns: (14mm, 18mm, 1fr, 28mm, 28mm), gutter: 3mm,
    [#judgment-mark("保")], [03], [合成大学丙 · 计算机组], [约 2.4 万], [#quiet([判断])])
  #v(8mm)
  #quiet([冲：往年位次高于孩子，且组内最差专业仍可接受。稳：往年位次接近。保：往年位次明显低于孩子，且家庭真正接受。])
]

#pagebreak()
#rail-head(
  [05],
  [COMPARISON],
  [两组对照],
  premise: [对照是为了看清代价，不是为了分出好坏。],
)
#v(10mm)
#pad(left: 26mm)[
  #grid(
    columns: (1fr, 1fr),
    gutter: 10mm,
    [
      #label([合成大学乙])
      #v(4mm)
      城市与专业方向更接近家庭软偏好。章程与校区仍待核验。
    ],
    [
      #label([合成大学丙], tone: secondary)
      #v(4mm)
      往年位次更靠后，作为保的判断类型更稳妥，但培养模式需家庭接受。
    ],
  )
]

#pagebreak()
#rail-head(
  [06],
  [EXCLUSIONS],
  [排除清单],
  premise: [不放进表的理由，往往比推荐清单更能避免事后争执。],
)
#v(9mm)
#pad(left: 26mm)[
  #evidence-row([排除], [合成大学丁 · 中外合作组：学费与培养周期未获家庭接受。])
  #evidence-row([排除], [合成大学戊 · 含家庭明确拒绝的专业，调剂风险不可接受。], tone: secondary)
]

#pagebreak()
#rail-head(
  [07],
  [NEXT],
  [下一步],
  premise: [本版讲解后，只在约定次数内修改。家庭仍作最终填报决定。],
)
#v(9mm)
#pad(left: 26mm)[
  #numbered([1], [核验], [把标记为待核验的章程、校区和学费核对到当年文本。])
  #v(6mm)
  #numbered([2], [确认], [家庭再次确认硬约束没有改口。], tone: secondary)
  #v(6mm)
  #numbered([3], [清单], [签发后导出填报执行清单，对着官方系统勾。])
  #v(12mm)
  #disclaimer-block()
]

#pagebreak()
#rail-head(
  [08],
  [SOURCES],
  [来源与签发],
)
#v(9mm)
#pad(left: 26mm)[
  #source-row([FACT], [本册结构与免责为文书模板。条目数据为合成演示。])
  #source-row([UNVERIFIED], [任何未写年来源的计划、分数线或章程，一律不得当已核实事实。])
  #v(8mm)
  #sign-grid([顾问签发], [姓名 / 日期], [复核], [姓名 / 日期])
]
