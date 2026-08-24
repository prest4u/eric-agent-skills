#import "/theme.typ": *
#import "facts.typ": *

#show: lattice-doc.with(
  title: "选科指导报告 · 林同",
  author: studio,
)

#cover-page(
  title: [选科指导报告],
  mark: studio-name,
  meta: alias + "  ·  " + province + "  ·  " + year + "  ·  " + batch + "  ·  " + case-id,
  opener: opener-line,
  body: [
    #text(font: fang, size: 11pt, fill: ink)[怎么读]
    #v(3.6mm)
    #text(font: fang, size: 10.5pt, fill: ink)[事实]　#how-fact
    #v(2.4mm)
    #text(font: fang, size: 10.5pt, fill: ink)[判断]　#how-judge
    #v(2.4mm)
    #text(font: fang, size: 10.5pt, fill: ink)[待核验]　#how-unv
    #v(7mm)
    本册只谈科目门是否被关上。不是志愿方案，也不列院校表。不开冲稳保，不上色。
    #v(4mm)
    现行 #current-combo。备选 #alt-combo。第三路 #third-combo，只作对照，不升格为推荐。
    #v(1fr)
    #quiet([#case-id  ·  合成示例  ·  #doc-date  ·  #version  ·  家庭作最终决定。机构署名：青云未来。])
  ],
)

#section-head[档案与约束]
#lead[抽出这一页，先分清三类：事实、判断、待核验。年份、省、批次、科目名称，只有对得上当年文件，才写成事实。选科阶段不写位次。]
#v(3mm)
#row-table((
  ([省 / 年], [#province · #year · #batch]),
  ([位次口径], [#rank-note]),
  ([现行], [#current-combo（合成）]),
  ([备选], [#alt-combo（合成）]),
  ([第三组], [#third-combo（合成）]),
  ([硬约束], [#hard]),
  ([软偏好], [#soft]),
  ([待补], [#pending]),
))
#v(6mm)
#lead[若家庭更看重工科门，保留物理与化学的代价，通常小于第三科来回摇摆。此为工作假设，不是录取结论。目标院校要求仍待观察。]

#pagebreak()

#section-head[科目与专业门]
#lead[对照表只谈门是否被关上。具体专业以当年高校公布为准。下表为合成口径，状态为待核验。不开冲稳保，不上色。开表，无填色，无可勾选。]
#v(3mm)
#gate-table(gate-rows)
#v(6mm)
#lead[#narrative-1]
#v(3.2mm)
#lead[#narrative-2]
#v(3.2mm)
#lead[#narrative-3]
#v(6mm)
#row-table((
  ([#exclude-rows.at(0).at(0)], [#exclude-rows.at(0).at(1) · #exclude-rows.at(0).at(2)]),
  ([#exclude-rows.at(1).at(0)], [#exclude-rows.at(1).at(1) · #exclude-rows.at(1).at(2)]),
  ([#exclude-rows.at(2).at(0)], [#exclude-rows.at(2).at(1) · #exclude-rows.at(2).at(2)]),
), cols: (22mm, 1fr))
#v(5mm)
#quiet[排除不等于贬低。本页没有志愿冲、稳、保分列，也没有院校网格。出分后再开志愿版档案。]

#pagebreak()

#section-head[来源与免责]
#row-table(sources.map(s => ([#s.at(0)], [#s.at(1)])))
#v(6mm)
#for line in disclaimer-lines {
  set par(first-line-indent: 0em, justify: false)
  set text(font: fang, size: 11pt, fill: ink)
  line
  v(2.4mm)
}
#v(5mm)
#row-table((
  ([含什么], [#svc-in]),
  ([不含什么], [#svc-out]),
  ([对象], [#alias · #province · #batch。案例号 #case-id。]),
  ([文种], [选科指导报告。不是志愿方案，不是经营讨论稿，不是返佣合同。]),
  ([下一步], [监护人确认硬约束仍是原意。对照当年选科要求，核物化地是否关上不可接受的专业门。]),
  ([提醒], [相关科目是否跟得上——只记观察，不作录取预测。第三科在地理与生物之间还要观察什么，写进待补。]),
), cols: (24mm, 1fr))
#v(7mm)
#quiet[签发前须对照当年文件。家庭作最终决定。机构署名：青云未来。本页不含院校推荐，也不等于明年志愿方案。]
