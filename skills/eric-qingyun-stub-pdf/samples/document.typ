#import "/theme.typ": *
#import "facts.typ": *

#show: stub-doc.with(
  title: "选科指导报告 · " + alias,
  author: studio,
  case-id: case-id,
)

#cover-page(
  title: "选科指导报告",
  case-id: case-id,
  meta: alias + "  ·  " + province + "  ·  " + year + "  ·  " + batch,
  premise: [#opener-line],
  colophon: [#case-id  ·  #version  ·  #doc-date  ·  合成示例  ·  家庭作最终决定],
)

#section-head([怎么读], premise: [先分清事实、判断和待核验。本页只讲科目门，不开冲稳保。])
#lead[抽出这张票，先把三类话钉住。可回当年文件核对的，才写成事实。顾问的归类是判断，不是录取结论。缺来源、过期、或还没对照当年要求的，标待核验，不能当成已经核实。]
#v(4mm)
#row-table((
  ([事实], [#how-fact]),
  ([判断], [#how-judge]),
  ([待核验], [#how-unv]),
  ([省 / 年], [#province · #year · #batch]),
  ([现行], [#current-combo（合成）]),
  ([备选], [#alt-combo（合成）]),
  ([硬约束], [#hard]),
  ([软偏好], [#soft]),
  ([待补], [#pending]),
))
#v(5mm)
#lead[这一页不签发。它是票面读法：先分清三类，再看下一页的科目门。冲稳保只出现在出分后的填报档案里，这里不列院校。]

#pagebreak()
#section-head([科目与专业门], premise: [对照表只谈门是否被关上。具体专业以当年高校公布为准。])
#quiet([合成口径，状态：待核验。不开冲稳保，不上色。开表，无填色，无可勾选。])
#v(4mm)
#gate-table(gate-rows)
#v(5mm)
#lead[#narrative-1]
#v(3mm)
#lead[#narrative-2]
#v(3mm)
#lead[#narrative-3]
#v(5mm)
#row-table((
  ([判断], [若家庭更看重工科门，保留物理与化学的代价，通常小于第三科来回摇摆。]),
  ([待核验], [目标院校专业的最新选科要求仍待观察。]),
  ([第三组], [#third-combo。只作对照，不升格为推荐。]),
  ([不放进表], [史政地与工程底线冲突。物化政未纳入讨论。纯文组合超出范围，本册不展开。]),
))

#pagebreak()
#section-head([来源与免责], premise: [可回文件核对的，才写成事实。其余标待核验。核对前不得当事实。])
#row-table(sources.map(s => ([#s.at(0)], [#s.at(1)])))
#v(6mm)
#for line in disclaimer-lines {
  set par(first-line-indent: 0em)
  set text(font: xing, size: 12pt)
  line
  v(2.4mm)
}
#v(4mm)
#row-table((
  ([含什么], [#svc-in]),
  ([不含什么], [#svc-out]),
  ([对象], [#alias · #province · #batch。案例号 #case-id。]),
  ([文种], [选科指导报告。不是冲稳保院校表，不是经营讨论稿，不是返佣合同。]),
  ([下一步], [监护人确认硬约束仍是原意。对照当年选科要求，核物化地是否关上不可接受的专业门。]),
  ([提醒], [相关科目是否跟得上——只记观察，不作录取预测。第三科在地理与生物之间还要观察什么，写进待补。]),
))
#v(6mm)
#quiet([签发前须对照当年文件。家庭作最终决定。机构署名：青云未来。本页不含院校推荐，也不等于明年填报方案。])
