#import "theme.typ": *

#let case-id = "__CASE_ID__"
#let alias = "__ALIAS__"
#let province = "__PROVINCE__"
#let year = "__YEAR__"
#let batch = "__BATCH__"
#let version = "__VERSION__"
#let doc-date = "__DATE__"

#let current-combo = "物理、化学、地理"
#let alt-combo = "物理、化学、生物"
#let third = "物理、生物、地理"
#let hard = "不接受家庭点名拒绝的科目组合；高负担课程须事先同意。"
#let soft = "工程方向、城市资源。"
#let pending = "相关科目是否跟得上、目标专业选科要求，均未逐条对照当年文件。"

#let gate-headers = ("组合", "工科门", "医学门", "经管门", "放弃代价")
#let gate-rows = (
  ("物化地（现行）", "多数可报", "多数不可报", "部分可报", "关掉多数医学入口"),
  ("物化生（备选）", "多数可报", "部分可报", "部分可报", "实验与课时负担加重"),
  ("物生地", "部分可报", "部分可报", "部分可报", "化学门关闭，工程口径变窄"),
)

#show: night-page.with(
  title: "__TITLE__",
  case-id: case-id,
  alias: alias,
  province: province,
  year: year,
  batch: batch,
  version: version,
  doc-date: doc-date,
)

#cover-poster(
  case-id: case-id,
  alias: alias,
  province: province,
  year: year,
  batch: batch,
  version: version,
  doc-date: doc-date,
)

#night-column[
  #section-head[怎么读]
  #text(font: serif, size: 10pt, fill: body-ink)[本页只说明怎么读这份选科材料。先分清事实、判断与待核验，再看档案。]
  #v(7mm)
  #night-note([事实], [可回当年官方文件核对的条目，才写成事实。])
  #night-note([判断], [顾问归类与取舍建议。不是录取结论。])
  #night-note([待核验], [缺来源、过期或尚未对照当年要求的，不得当作已核实。])
  #section-head[档案摘要]
  #night-note([现行], [#current-combo（合成）])
  #night-note([备选], [#alt-combo（合成）])
  #night-note([第三], [#third（合成）])
  #night-note([硬约束], [#hard])
  #night-note([软偏好], [#soft])
  #night-note([待补], [#pending])
]

#pagebreak()

#night-column[
  #section-head[科目与专业门]
  #text(font: serif, size: 10pt, fill: body-ink)[合成口径，状态：待核验。对照表只谈门是否被关上。]
  #v(5mm)
  #row-table(gate-headers, gate-rows)
  #v(8mm)
  #night-note([判断], [若家庭更看重工科门，保留物理与化学的代价，通常小于第三科来回摇摆。])
  #night-note([待核验], [目标院校专业的最新选科要求仍待观察。])
]

#pagebreak()

#night-column[
  #section-head[来源与免责]
  #night-note([待核验], [天津市普通高中学业水平选择性考试科目要求（合成示例，查询日 #doc-date）。])
  #night-note([待核验], [高校招生专业选科要求汇编（合成示例；须回当年高校章程）。])
  #section-head[免责]
  #for line in disclaimer-lines {
    set text(font: serif, size: 10pt, fill: body-ink)
    set par(justify: true, leading: 1.05em)
    line
    v(3.2mm)
  }
  #v(10mm)
  #sign-block()
  #v(8mm)
  #text(font: serif, size: 10pt, fill: body-ink)[家庭作最终决定。青云]
]
