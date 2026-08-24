#import "/theme.typ": *
#import "facts.typ": *

#show: fold-doc.with(
  title: "选科指导报告 · " + alias,
  author: studio,
)

#cover-page(
  title: "选科指导报告",
  student: alias + "  ·  " + province + "  ·  " + year + "  ·  " + batch + "  ·  " + case-id,
  premise: opener-line,
  facts: (
    ([事实], [#how-fact 年份、省、批次、科目名称，只有对得上当年文件，才用这个标记。选科阶段不写位次。]),
    ([判断], [#how-judge 若家庭更看重工科门，保留物理与化学的代价，通常小于第三科来回摇摆。此为工作假设。]),
    ([待核验], [#how-unv #pending]),
  ),
  colophon: [
    #case-id  ·  合成示例  ·  非正式官方文件 · 不保证录取  ·  #doc-date  ·  #version
  ],
)

#section-head([怎么读], premise: [三类话怎么分开])
#lead[
  本文件把文字分成三类，单栏左齐走，不按书页首行缩进排杂志段，也不做并排栏。先看门，再谈喜好。
]
#v(4mm)
#text(font: headline, size: 9pt, weight: "bold", fill: muted)[事实]
#v(2mm)
#lead[#how-fact 年份、省、批次、科目名称，只有对得上当年文件，才用这个标记。选科阶段不写位次。#rank-note]
#v(4.5mm)
#text(font: headline, size: 9pt, weight: "bold", fill: muted)[判断]
#v(2mm)
#lead[#how-judge 若家庭更看重工科门，保留物理与化学的代价，通常小于第三科来回摇摆。此为工作假设。]
#v(4.5mm)
#text(font: headline, size: 9pt, weight: "bold", fill: muted)[待核验]
#v(2mm)
#lead[#how-unv #pending]
#v(4.5mm)
#text(font: headline, size: 9pt, weight: "bold", fill: muted)[先看门]
#v(2mm)
#lead[#narrative-1 本册只谈科目门是否被关上。不开冲稳保，不上色，不列院校。]
#v(4.5mm)
#text(font: headline, size: 9pt, weight: "bold", fill: muted)[署名]
#v(2mm)
#lead[青云未来只署名「青云未来」。硬约束：#hard 软偏好：#soft]
#v(7mm)
#section-head([档案], premise: [档案与约束])
#row-table((
  ([省 / 年], [#province · #year · #batch]),
  ([位次口径], [#rank-note]),
  ([现行], [#current-combo（合成）]),
  ([备选], [#alt-combo（合成）]),
  ([硬约束], [#hard]),
  ([软偏好], [#soft]),
  ([待补], [#pending]),
))

#pagebreak()
#section-head([科目与专业门], premise: [只谈门是否被关上])
#lead[对照表只谈门是否被关上。具体专业以当年高校公布为准。下表为合成口径，状态为待核验。不开冲稳保，不上色。开表，无填色，无可勾选。]
#v(3.4mm)
#gate-table(gate-rows)
#v(5mm)
#lead[#narrative-1]
#v(3.2mm)
#lead[#narrative-2]
#v(3.2mm)
#lead[#narrative-3]
#v(5mm)
#text(font: headline, size: 9pt, weight: "bold", fill: muted)[现行 / 备选]
#v(2.2mm)
#lead[现行 #current-combo。备选 #alt-combo。第三路 #third-combo，只作对照，不升格为推荐。物化地多数可走工科门，多数走不通医学门。物化生工科仍多数可报，代价是实验与课时负担加重。]
#v(4.5mm)
#text(font: headline, size: 9pt, weight: "bold", fill: muted)[不放进表]
#v(2.2mm)
#lead[排除不等于贬低。史政地与工程底线冲突。物化政未纳入讨论。纯文组合超出范围，本册不展开。]
#v(3.2mm)
#row-table((
  ([#exclude-rows.at(0).at(0)], [#exclude-rows.at(0).at(1) · #exclude-rows.at(0).at(2)]),
  ([#exclude-rows.at(1).at(0)], [#exclude-rows.at(1).at(1) · #exclude-rows.at(1).at(2)]),
  ([#exclude-rows.at(2).at(0)], [#exclude-rows.at(2).at(1) · #exclude-rows.at(2).at(2)]),
))
#v(4.5mm)
#text(font: headline, size: 9pt, weight: "bold", fill: muted)[不是志愿]
#v(2.2mm)
#lead[本页没有志愿冲、稳、保分列，也没有院校网格。出分后再开志愿版档案。目标院校要求仍待观察。]

#pagebreak()
#section-head([来源与免责], premise: [核对前不得当事实])
#row-table(sources.map(s => ([#s.at(0)], [#s.at(1)])))
#v(5.5mm)
#text(font: headline, size: 9pt, weight: "bold", fill: muted)[免责]
#v(3mm)
#for line in disclaimer-lines {
  set par(first-line-indent: 0em, justify: false)
  set text(font: body-font, size: 11pt)
  line
  v(2.4mm)
}
#v(3.5mm)
#text(font: headline, size: 9pt, weight: "bold", fill: muted)[含什么]
#v(2.2mm)
#lead[#svc-in]
#v(4.5mm)
#text(font: headline, size: 9pt, weight: "bold", fill: muted)[不含什么]
#v(2.2mm)
#lead[#svc-out]
#v(4.5mm)
#text(font: headline, size: 9pt, weight: "bold", fill: muted)[对象]
#v(2.2mm)
#lead[#alias · #province · #batch。案例号 #case-id。选科指导报告。不是志愿方案，不是经营讨论稿，不是返佣合同。]
#v(4.5mm)
#text(font: headline, size: 9pt, weight: "bold", fill: muted)[下一步]
#v(2.2mm)
#lead[监护人确认硬约束仍是原意。对照当年选科要求，核物化地是否关上不可接受的专业门。相关科目是否跟得上——只记观察，不作录取预测。第三科在地理与生物之间还要观察什么，写进待补。]
#v(6mm)
#quiet([签发前须对照当年文件。家庭作最终决定。机构署名：青云未来。本页不含院校推荐，也不等于明年志愿方案。])
