#import "theme.typ": *

#show: qingyun-document.with(
  title: "__TITLE__",
  case-id: "__CASE_ID__",
  student-alias: "__ALIAS__",
  province: "__PROVINCE__",
  year: "__YEAR__",
  batch: "选科",
  version: "__VERSION__",
  doc-date: "__DATE__",
  kind: "选科指导",
)

#cover-page(
  [ERIC SLATE WHITE PDF · 选科指导],
  [选科指导报告],
  [青云未来本季主交付。科目门与轻度学业规划，不是缩小版志愿方案。],
  [__CASE_ID__ · __ALIAS__\__PROVINCE____YEAR__ · 青云未来],
  [选科文书\合成示例\不保证录取],
)

#pagebreak()
#rail-head(
  [01],
  [COMBINATIONS],
  [科目组合],
  premise: [先看放弃某科会关掉哪些大学专业门，再谈喜好。],
)
#v(8mm)
#pad(left: 26mm)[
  #rule-row([现行方向], [物理、化学、地理（合成）])
  #rule-row([备选], [物理、化学、生物（合成）], tone: secondary)
  #rule-row([代价], [放下地理或生物，分别影响哪些专业类，须回当年选科要求核对])
]

#pagebreak()
#rail-head([02], [GATES], [专业门与待观察])
#v(8mm)
#pad(left: 26mm)[
  #evidence-row([FACT], [具体专业选科要求以当年高校公布为准。本页不列院校志愿表。])
  #evidence-row([JUDGEMENT], [若家庭更看重工科门，保留物理与化学的代价通常小于保留第三科的摇摆。], tone: secondary)
  #evidence-row([UNVERIFIED], [目标院校专业的最新选科要求仍待观察。])
]

#pagebreak()
#rail-head([03], [WATCH], [待观察项])
#v(8mm)
#pad(left: 26mm)[
  #numbered([1], [成绩稳定性], [相关科目是否跟得上，不作录取预测。])
  #v(6mm)
  #numbered([2], [专业门], [家庭绝对不想关上一类专业时，第三科怎么选。], tone: secondary)
  #v(6mm)
  #numbered([3], [复核时间], [下次对照当年选科要求再核一次。])
  #v(10mm)
  #disclaimer-block()
]
