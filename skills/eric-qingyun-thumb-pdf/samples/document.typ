#import "/theme.typ": *
#import "facts.typ": *

// 4 页选科指导报告小样。内部皮：军绿指索（军绿纸 / 全书隶书 / 右缘拇指索引）。
// 内部名不得印上 PDF。事实只来自 facts.typ。不是志愿方案，不列院校。

#show: thumb-doc.with(
  title: "选科指导报告 · " + alias,
  author: studio,
)

#cover-page(
  title: [选科指导报告],
  student: [#alias  ·  #province  ·  #year  ·  #batch \
    #case-id],
  premise: [#opener-line],
  colophon: [#version  ·  #doc-date  ·  合成示例  ·  家庭作最终决定],
)

#section-head([怎么读], premise: [先分清事实、判断和待核验。本页锁家庭原意。本册只谈科目门是否被关上，不列院校。])
#read-trio((
  ([事实], how-fact),
  ([判断], how-judge),
  ([待核验], how-unv),
))
#v(8mm)
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
#quiet([合成口径，状态：待核验。不上色，不列院校。])
#v(5mm)
#gate-table(gate-rows)
#v(7mm)
#row-table((
  ([判断], [若家庭更看重工科门，保留物理与化学的代价，通常小于第三科来回摇摆。]),
  ([待核验], [目标院校专业的最新选科要求仍待观察。]),
))
#v(6mm)
#lead(narrative-2)

#pagebreak()
#section-head([来源与免责], premise: [可回文件核对的，才写成事实。其余标待核验。])
#row-table(sources)
#v(8mm)
#disclaimer-block(disclaimer-lines)
#v(8mm)
#quiet([签发前须对照当年文件。家庭作最终决定。署名：青云未来。])
