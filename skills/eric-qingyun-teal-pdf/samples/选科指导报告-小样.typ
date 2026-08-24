#import "/theme.typ": *
#import "facts.typ": *

// 4 页选科指导报告小样。底盘：青云识别册（浅青灰卡 / 顶通栏 / 全无衬线）。
// 事实只来自 facts.typ，不另造学生口径。不是志愿冲稳保。

#show: qingyun-doc.with(
  title: "选科指导报告 · " + alias,
  author: studio,
  case-id: case-id,
  alias: alias,
  province: province,
  year: year,
  batch: batch,
)

#cover-page(
  title: [选科指导报告],
  student: [#alias  ·  #province  ·  #year  ·  #batch],
  premise: [#opener-line],
  band-center: [选科指导  ·  #alias  ·  #province],
  band-right: [#case-id],
  foot-line: [#version  ·  #doc-date  ·  合成示例  ·  家庭作最终决定],
)

#section-head([怎么读], premise: [先分清事实、判断和待核验。本页锁家庭原意。])
#read-trio((
  ([事实], how-fact),
  ([判断], how-judge),
  ([待核验], how-unv),
))
#v(9mm)
#section-head([档案摘要])
#row-table((
  ([省 / 年], [#province · #year · #batch]),
  ([位次口径], rank-note),
  ([现行], [#current-combo（合成）]),
  ([备选], [#alt-combo（合成）]),
  ([硬约束], hard),
  ([软偏好], soft),
  ([待补], pending),
))

#pagebreak()
#section-head([科目与专业门], premise: [对照表只谈门是否被关上。具体专业以当年高校公布为准。])
#quiet([合成口径，状态：待核验。不开冲稳保，不上色。])
#v(5mm)
#gate-table(gate-rows)
#v(8mm)
#row-table((
  ([判断], [若家庭更看重工科门，保留物理与化学的代价，通常小于第三科来回摇摆。]),
  ([待核验], [目标院校专业的最新选科要求仍待观察。]),
))

#pagebreak()
#section-head([来源与免责], premise: [可回文件核对的，才写成事实。其余标待核验。])
#row-table(sources)
#v(8mm)
#disclaimer-block(disclaimer-lines)
#v(8mm)
#quiet([签发前须对照当年文件。家庭作最终决定。署名：青云未来。])
