#import "theme.typ": *

#show: qingyun-document.with(
  title: "__TITLE__",
  case-id: "教师转介",
  student-alias: "—",
  province: "__PROVINCE__",
  year: "__YEAR__",
  batch: "—",
  version: "__VERSION__",
  doc-date: "__DATE__",
  kind: "教师一页纸",
  show-identity-header: false,
)

#cover-page(
  [ERIC SLATE WHITE PDF · 教师说明],
  [给老师的一页说明],
  [转介前请了解：青云未来本季主做选科指导，顾问签发，不代填、不承诺录取。],
  [青云未来\__PROVINCE__ · __DATE__],
  [转介说明\非正式官方文件\不保证录取],
)

#pagebreak()
#rail-head([01], [FOR TEACHERS], [转介时需要知道的])
#v(8mm)
#pad(left: 26mm)[
  #rule-row([做什么], [选科指导与学业规划；顾问签发；家庭最终决定])
  #rule-row([不做什么], [不代填官方系统、不承诺录取、不把学生资料默认给第三方], tone: secondary)
  #rule-row([资料], [最少必要；转介到外部机构前须单独同意])
  #rule-row([下一步], [老师介绍家庭后，由顾问预约说明与确认书])
  #v(8mm)
  #disclaimer-block()
]
