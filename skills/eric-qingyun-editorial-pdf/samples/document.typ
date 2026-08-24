#import "/theme.typ": *
#import "facts.typ": *

#show: editorial-doc.with(
  title: "选科指导报告 · 林同",
  author: studio,
  header-left: "选科指导报告",
  header-right: alias + " · " + province,
)

#cover-page(
  kicker: skin-label,
  title: "选科指导报告",
  meta: alias + " · " + province + " · 二〇二六 · 高一选科",
  lead: [科目门与轻度学业规划。本册不是志愿方案，也不列院校表。先看放弃某科会关掉哪一类专业门，再谈喜好。],
  colophon: [
    #case-id \
    合成示例 · 非正式官方文件 · 不保证录取 \
    #doc-date · #version
  ],
)

#chapter([一], [怎么读])
本文件把文字分成三类。事实，是可以回到当年官方文件核对的条目。判断，是顾问的归类与取舍建议，不是录取结论。待核验，是缺来源、过期、或尚未对照当年要求的条目；不得当作已核实事实。
#v(4mm)
#chapter([二], [档案摘要])
#labeled-rows((
  ([现行], [#current-combo（合成）]),
  ([备选], [#alt-combo（合成）]),
  ([硬约束], [#hard]),
  ([软偏好], [#soft]),
  ([待补], [#pending]),
))

#pagebreak()
#chapter([三], [科目与专业门])
对照表只谈门是否被关上。具体专业以当年高校公布为准。下表为合成口径，状态为待核验。不开冲稳保，不上色。
#v(5mm)
#gate-table(gate-rows)
#v(6mm)
#set text(size: 10.5pt)
#set par(first-line-indent: 2em)
若家庭更看重工科门，保留物理与化学的代价，通常小于第三科来回摇摆。此为判断。目标院校专业的最新选科要求仍待观察。

#pagebreak()
#chapter([四], [来源与免责])
#labeled-rows((
  ([待核验], [天津市普通高中学业水平选择性考试科目要求（合成示例，查询日 #doc-date）。]),
  ([待核验], [高校招生专业选科要求汇编（合成示例；须回当年高校章程）。]),
), row-gutter: 4.5mm)
#v(8mm)
#disclaimer-prose(disclaimer-lines)
#v(8mm)
#set par(first-line-indent: 0em)
#quiet([签发前须对照当年文件。家庭作最终决定。纸色为冷灰书纸，不是暖象牙。])
