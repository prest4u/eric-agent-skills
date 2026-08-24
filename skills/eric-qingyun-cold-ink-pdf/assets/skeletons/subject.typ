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
#let hard = "不接受家庭点名拒绝的科目组合；高负担课程须事先同意。"
#let soft = "工程方向、城市资源。"
#let pending = "相关科目是否跟得上、目标专业选科要求，均未逐条对照当年文件。"

#let gate-rows = (
  ("物化地（现行）", "多数可报", "多数不可报", "部分可报", "关掉多数医学入口"),
  ("物化生（备选）", "多数可报", "部分可报", "部分可报", "实验与课时负担加重"),
  ("物生地", "部分可报", "部分可报", "部分可报", "化学门关闭，工程口径变窄"),
)

#show: cold-ink-page.with(
  title: "__TITLE__",
  case-id: case-id,
  alias: alias,
  province: province,
  year: year,
  batch: batch,
  version: version,
  doc-date: doc-date,
)

#cover-page(
  title: "__TITLE__",
  subtitle: "顾问签发意见。不是志愿方案，不列院校。",
  case-id: case-id,
  alias: alias,
  province: province,
  year: year,
  batch: batch,
  version: version,
  doc-date: doc-date,
)

#section-head[一、怎么读]
#item([事实], [可回当年官方文件核对的条目，才写成事实。])
#item([判断], [顾问归类与取舍建议。不是录取结论。])
#item([待核验], [缺来源、过期或尚未对照当年要求的，不得当作已核实。])
#v(3mm)
#section-head[二、档案摘要]
#item([现行], [#current-combo（合成）])
#item([备选], [#alt-combo（合成）])
#item([硬约束], [#hard])
#item([软偏好], [#soft])
#item([待补], [#pending])

#pagebreak()
#section-head[三、科目与专业门]
#quiet([合成口径，状态：待核验。对照表只谈门是否被关上。])
#v(4mm)
#gate-table(gate-rows)
#v(5mm)
#set text(font: serif, size: 9.2pt)
#item([判断], [若家庭更看重工科门，保留物理与化学的代价，通常小于第三科来回摇摆。])
#item([待核验], [目标院校专业的最新选科要求仍待观察。])

#pagebreak()
#section-head[四、来源与免责]
#item([待核验], [天津市普通高中学业水平选择性考试科目要求（合成示例，查询日 #doc-date）。])
#item([待核验], [高校招生专业选科要求汇编（合成示例；须回当年高校章程）。])
#v(3mm)
#section-head[免责]
#for line in disclaimer-lines {
  quiet(line)
  v(1.4mm)
}
#v(8mm)
#sign-block()
#v(6mm)
#quiet([家庭作最终决定。青云])
