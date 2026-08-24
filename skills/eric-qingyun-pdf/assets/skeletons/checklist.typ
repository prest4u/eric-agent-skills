#import "theme.typ": *

#show: qingyun-document.with(
  title: "__TITLE__",
  case-id: "__CASE_ID__",
  student-alias: "__ALIAS__",
  province: "__PROVINCE__",
  year: "__YEAR__",
  batch: "__BATCH__",
  version: "__VERSION__",
  doc-date: "__DATE__",
  kind: "填报清单",
)

#cover-page(
  [ERIC SLATE WHITE PDF · 填报清单],
  [填报执行清单],
  [对着官方系统勾。本清单不能代替官方志愿表。],
  [__CASE_ID__ · __ALIAS__\对应方案版本 __VERSION__\__PROVINCE____YEAR____BATCH__],
  [只收录已签发候选\非正式官方文件\不保证录取],
)

#pagebreak()
#rail-head(
  [01],
  [ORDER],
  [志愿顺序],
  premise: [正式件按当年批次栏位数展开。本页三条为合成示范。],
)
#v(8mm)
#pad(left: 26mm)[
  #grid(
    columns: (14mm, 1fr, 22mm, 22mm),
    gutter: 3mm,
    [#label([序号])], [#label([院校专业组])], [#label([类型])], [#label([服从调剂])],
  )
  #v(3mm)
  #line(length: 100%, stroke: 0.5pt + hair)
  #v(4mm)
  #grid(columns: (14mm, 1fr, 22mm, 22mm), gutter: 3mm,
    [01], [合成大学甲 · 工科组 A], [#judgment-mark("冲")], [#quiet([家庭填])])
  #v(3.5mm)
  #line(length: 100%, stroke: 0.5pt + hair)
  #v(3.5mm)
  #grid(columns: (14mm, 1fr, 22mm, 22mm), gutter: 3mm,
    [02], [合成大学乙 · 电子信息组], [#judgment-mark("稳")], [#quiet([家庭填])])
  #v(3.5mm)
  #line(length: 100%, stroke: 0.5pt + hair)
  #v(3.5mm)
  #grid(columns: (14mm, 1fr, 22mm, 22mm), gutter: 3mm,
    [03], [合成大学丙 · 计算机组], [#judgment-mark("保")], [#quiet([家庭填])])
]

#pagebreak()
#rail-head([02], [CHECKS], [填前五道检查])
#v(9mm)
#pad(left: 26mm)[
  #numbered([1], [选科], [该专业组是否符合选考科目。])
  #v(5mm)
  #numbered([2], [接受度], [组内最差专业能否接受。], tone: secondary)
  #v(5mm)
  #numbered([3], [章程], [单科、语种、体检等限制是否核对。])
  #v(5mm)
  #numbered([4], [费用校区], [学费、校区、培养模式是否清楚。], tone: secondary)
  #v(5mm)
  #numbered([5], [服从调剂], [服从后可能进入的专业是否仍可接受。])
  #v(10mm)
  #disclaimer-block()
]
