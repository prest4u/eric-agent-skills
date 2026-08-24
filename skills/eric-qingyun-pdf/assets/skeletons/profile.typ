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
  kind: "档案确认",
)

#cover-page(
  [ERIC SLATE WHITE PDF · 档案确认],
  [档案与家庭约束确认],
  [本季默认选科版。家庭签字确认：这些约束是我们自己说的。改口先改本页。],
  [__CASE_ID__\__ALIAS__\__PROVINCE____YEAR__ · 青云未来],
  [诊断确认件\合成示例\不保证录取],
)

#pagebreak()
#rail-head(
  [01],
  [FACTS],
  [科目与硬约束],
  premise: [选科版先锁科目与底线。志愿版另开一页补位次来源与查询日。本页示例为合成数据。],
)
#v(8mm)
#pad(left: 26mm)[
  #rule-row([选科意向], [物理、化学、地理（合成）])
  #rule-row([硬约束], [不接受家庭点名拒绝的科目组合；高负担课程须事先同意])
  #rule-row([软偏好], [工程方向、城市资源], tone: secondary)
  #rule-row([待补], [高中课程负担与目标专业选科要求尚未逐条核对])
  #rule-row([志愿旺季另补], [位次、批次、查询来源与查询日——出分后再开志愿版 D3], tone: secondary)
]

#pagebreak()
#rail-head([02], [CONFIRM], [家庭确认])
#v(9mm)
#pad(left: 26mm)[
  #quiet([我们确认以上硬约束反映家庭原意。若此后改口，须先更新本确认再出选科报告或志愿方案。])
  #v(10mm)
  #disclaimer-block()
  #v(10mm)
  #sign-grid([监护人确认], [姓名 / 日期], [顾问收存], [姓名 / 日期])
]
