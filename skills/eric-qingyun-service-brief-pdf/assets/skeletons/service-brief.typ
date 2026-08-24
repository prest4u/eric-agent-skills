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
  kind: "服务说明",
  show-identity-header: false,
)

#cover-page(
  [ERIC SLATE WHITE PDF · 服务说明],
  [服务说明与边界],
  [本季先卖选科指导。付钱之前先看清：买的是顾问陪同判断，不是录取结果。],
  [青云未来 · 选科指导\讲解次数与修改次数另行约定\__DATE__ · __VERSION__],
  [售前阅读件\非正式官方文件\不保证录取],
)

#pagebreak()
#rail-head(
  [01],
  [SCOPE],
  [含什么 / 不含什么],
  premise: [写在纸上的范围，才是后来计价和售后的依据。],
)
#v(9mm)
#pad(left: 26mm)[
  #grid(
    columns: (1fr, 1fr),
    gutter: 10mm,
    [
      #label([含什么])
      #v(4mm)
      一次需求深谈\选科与学业规划档案\选科指导报告与内部复核\一次正式讲解\约定次数内的修改与答疑
    ],
    [
      #label([不含什么], tone: secondary)
      #v(4mm)
      不承诺录取结果\不代替家庭做最终决定\不使用没有来源的政策或分数线\不无限次修改\不代为登录官方填报系统
    ],
  )
  #v(12mm)
  #disclaimer-block()
]

#pagebreak()
#rail-head(
  [02],
  [NEXT],
  [下一步],
)
#v(10mm)
#pad(left: 26mm)[
  #numbered([1], [确认服务], [若继续，签署服务确认书。确认书不是已审法律意见。])
  #v(7mm)
  #numbered([2], [建档], [家庭确认约束后，才开始方案。], tone: secondary)
  #v(10mm)
  #quiet([机构署名：青云未来。本文件不含具体院校推荐，也不等于明年志愿方案。])
]
