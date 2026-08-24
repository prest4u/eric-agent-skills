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
  kind: "讲解提纲",
)

#cover-page(
  [ERIC SLATE WHITE PDF · 讲解提纲],
  [家长讲解提纲],
  [今晚只决定这几件事。本页不是方案报告。],
  [__CASE_ID__ · __ALIAS__\对应方案 __VERSION__],
  [现场提纲\不当主交付\不保证录取],
)

#pagebreak()
#rail-head(
  [01],
  [TONIGHT],
  [今晚只决定这些],
  premise: [讲清楚判断，不临场加承诺。],
)
#v(8mm)
#pad(left: 26mm)[
  #numbered([1], [约束], [硬约束有没有改口。])
  #v(5mm)
  #numbered([2], [类型], [冲、稳、保的三条是否仍可接受。], tone: secondary)
  #v(5mm)
  #numbered([3], [争议], [家庭仍未决的城市、学费或专业。])
  #v(5mm)
  #numbered([4], [待核验], [哪些条目今晚不能当已核实事实。], tone: secondary)
  #v(5mm)
  #numbered([5], [下一步], [修改窗口与谁在官方系统里提交。])
  #v(10mm)
  #disclaimer-block()
]
