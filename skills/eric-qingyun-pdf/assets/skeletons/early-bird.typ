#import "theme.typ": *

#show: qingyun-document.with(
  title: "__TITLE__",
  case-id: "早鸟预售",
  student-alias: "—",
  province: "__PROVINCE__",
  year: "2027",
  batch: "早鸟",
  version: "__VERSION__",
  doc-date: "__DATE__",
  kind: "早鸟预售",
  show-identity-header: false,
)

#cover-page(
  [ERIC SLATE WHITE PDF · 早鸟说明],
  [2027 届早鸟预售说明],
  [锁的是明年一对一咨询的名额，不是今年的填报结果。价格未定时不得当成已报价。],
  [青云未来\定金、权益与退款待会上确定\__DATE__ · __VERSION__],
  [锁客一页纸\非正式官方文件\不保证录取],
)

#pagebreak()
#rail-head([01], [EARLY BIRD], [买什么、不买什么])
#v(8mm)
#pad(left: 26mm)[
  #rule-row([含什么], [2027 届一对一咨询的预约名额；出分前沟通窗口次数待定])
  #rule-row([不含什么], [不代填官方系统、不承诺录取、不含未约定的留学或课程], tone: secondary)
  #rule-row([定金], [金额、抵扣规则、退款条件——数字待定，未定时不得收款冒充已生效])
  #rule-row([关系], [可与选科指导分开购买；选科报告不自动等于早鸟权益], tone: secondary)
  #v(8mm)
  #disclaimer-block()
]
