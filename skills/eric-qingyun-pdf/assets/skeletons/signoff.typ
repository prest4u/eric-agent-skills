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
  kind: "签发单",
)

#cover-page(
  [ERIC SLATE WHITE PDF · 复核签发],
  [复核签发单],
  [没有本页签发，方案报告与填报清单不得称为正式版。已交付版本不得覆盖。],
  [__CASE_ID__ · __ALIAS__\方案版本 __VERSION__ · __DATE__],
  [内部闸门\可向家庭出示签发人\不保证录取],
)

#pagebreak()
#rail-head([01], [CHECKS], [签发前检查])
#v(8mm)
#pad(left: 26mm)[
  #rule-row([约束一致], [方案摘要与档案确认一致])
  #rule-row([来源年份], [每条关键数据写明年份与来源状态], tone: secondary)
  #rule-row([无概率承诺], [未见录取率、上岸或百分比保证])
  #rule-row([未核验未当事实], [缺失与冲突仍标为待核验], tone: secondary)
  #rule-row([不得覆盖], [本版签发后只可出新版本，不可改旧文件冒充])
  #v(8mm)
  #disclaimer-block()
  #v(10mm)
  #sign-grid([顾问签发], [姓名 / 日期], [复核], [姓名 / 日期])
]
