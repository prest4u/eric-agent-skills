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
  kind: "服务确认",
)

#cover-page(
  [ERIC SLATE WHITE PDF · 服务确认],
  [服务确认书],
  [非正式法律文本，待专业审查。签署前请完整阅读。],
  [__CASE_ID__\__ALIAS__ 的监护人\__PROVINCE____YEAR__],
  [待专业审查\非正式法律文本\不保证录取],
)

#pagebreak()
#rail-head([01], [PARTIES], [当事人与服务范围])
#v(9mm)
#pad(left: 26mm)[
  #rule-row([学生], [化名 __ALIAS__（合成示例，正式件替换为约定称呼）])
  #rule-row([监护人], [签署栏所载监护人], tone: secondary)
  #rule-row([服务], [本季默认选科指导：访谈、档案、选科报告、一次讲解、约定次数内修改])
  #rule-row([不含], [录取承诺、代填官方系统、无限咨询、未经约定的留学申请], tone: secondary)
]

#pagebreak()
#rail-head([02], [LIMITS], [周期、价款与资料])
#v(9mm)
#pad(left: 26mm)[
  #rule-row([周期], [起止日期与讲解次数、修改次数（数字待三人定稿后填入）])
  #rule-row([价款], [金额、付款节点、可退与不可退（数字待定）], tone: secondary)
  #rule-row([资料], [最少必要；向外部提供前须单独同意；不满十四周岁须监护人相应同意])
  #v(6mm)
  #quiet([本页数字未定时，不得当作已报价合同。])
]

#pagebreak()
#rail-head(
  [03],
  [ACKNOWLEDGEMENT],
  [知情与签字],
  premise: [家庭仍作最终填报决定。顾问签发不等于保证结果。],
)
#v(8mm)
#pad(left: 26mm)[
  #disclaimer-block()
  #v(8mm)
  #quiet([非正式法律文本，待专业审查。])
  #v(10mm)
  #sign-grid([监护人签字], [姓名 / 日期], [顾问签收], [姓名 / 日期])
]
