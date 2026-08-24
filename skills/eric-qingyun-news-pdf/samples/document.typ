#import "/theme.typ": *
#import "facts.typ": *

#show: news-doc.with(
  title: "选科指导报告 · 林同",
  author: studio,
  header-left: studio-name,
  header-right: "选科指导报告  ·  " + alias + "  ·  " + province,
)

#cover-page(
  date: "2026.08.19",
  title: "选科指导报告",
  dek: alias + "  ·  " + province + "  ·  " + year + "  ·  " + batch + "  ·  " + case-id,
  briefs: (
    [
      #text(font: sans, size: 7pt, weight: "bold", fill: muted)[01  /  先看门]
      #v(1.8mm)
      #opener-line
      #v(2mm)
      科目门与轻度学业规划。本册不是志愿方案，也不列院校表。
    ],
    [
      #text(font: sans, size: 7pt, weight: "bold", fill: muted)[02  /  事实]
      #v(1.8mm)
      #how-fact
    ],
    [
      #text(font: sans, size: 7pt, weight: "bold", fill: muted)[03  /  判断]
      #v(1.8mm)
      #how-judge
    ],
    [
      #text(font: sans, size: 7pt, weight: "bold", fill: muted)[04  /  待核验]
      #v(1.8mm)
      #how-unv
    ],
    [
      #text(font: sans, size: 7pt, weight: "bold", fill: muted)[05  /  组合]
      #v(1.8mm)
      现行 #current-combo。备选 #alt-combo。第三路 #third-combo，只作对照，不升格为推荐。
    ],
    [
      #text(font: sans, size: 7pt, weight: "bold", fill: muted)[06  /  签发]
      #v(1.8mm)
      青云未来签发。家庭作最终决定。合成示例，不保证录取。
    ],
  ),
  colophon: [
    #case-id  ·  合成示例  ·  非正式官方文件 · 不保证录取  ·  #doc-date  ·  #version
  ],
)

#deck-head([怎么读], [三类话怎么分开])
#news-six((
  [
    #text(font: sans, size: 7pt, weight: "bold", fill: muted)[栏怎么走]
    #v(1.6mm)
    本文件把文字分成三类，栏与栏并排走，不按书页首行缩进排杂志段。报式六栏给长文；门表、档案表跨栏。
  ],
  [
    #text(font: sans, size: 7pt, weight: "bold", fill: muted)[事实]
    #v(1.6mm)
    #how-fact 年份、省、批次、科目名称，只有对得上当年文件，才用这个标记。选科阶段不写位次。
  ],
  [
    #text(font: sans, size: 7pt, weight: "bold", fill: muted)[判断]
    #v(1.6mm)
    #how-judge 若家庭更看重工科门，保留物理与化学的代价，通常小于第三科来回摇摆。此为工作假设。
  ],
  [
    #text(font: sans, size: 7pt, weight: "bold", fill: muted)[待核验]
    #v(1.6mm)
    #how-unv #pending
  ],
  [
    #text(font: sans, size: 7pt, weight: "bold", fill: muted)[先看门]
    #v(1.6mm)
    #narrative-1 本册只谈科目门是否被关上。不开冲稳保，不上色，不列院校。
  ],
  [
    #text(font: sans, size: 7pt, weight: "bold", fill: muted)[署名]
    #v(1.6mm)
    青云未来只署名「青云未来」。硬约束：#hard 软偏好：#soft
  ],
))
#v(5mm)
#deck-head([档案], [档案与约束])
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
#deck-head([科目与专业门], [只谈门是否被关上])
#lead[对照表只谈门是否被关上。具体专业以当年高校公布为准。下表为合成口径，状态为待核验。不开冲稳保，不上色。门表跨六栏，开表，无填色，无可勾选。]
#v(3.2mm)
#gate-table(gate-rows)
#v(4.2mm)
#news-six((
  [
    #text(font: sans, size: 7pt, weight: "bold", fill: muted)[01]
    #v(1.6mm)
    #narrative-1
  ],
  [
    #text(font: sans, size: 7pt, weight: "bold", fill: muted)[02]
    #v(1.6mm)
    #narrative-2
  ],
  [
    #text(font: sans, size: 7pt, weight: "bold", fill: muted)[03]
    #v(1.6mm)
    #narrative-3
  ],
  [
    #text(font: sans, size: 7pt, weight: "bold", fill: muted)[现行 / 备选]
    #v(1.6mm)
    物化地多数可走工科门，多数走不通医学门。物化生工科仍多数可报，代价是实验与课时负担加重。
  ],
  [
    #text(font: sans, size: 7pt, weight: "bold", fill: muted)[不放进表]
    #v(1.6mm)
    排除不等于贬低。史政地与工程底线冲突。物化政未纳入讨论。纯文组合超出范围，本册不展开。
  ],
  [
    #text(font: sans, size: 7pt, weight: "bold", fill: muted)[不是志愿]
    #v(1.6mm)
    本页没有志愿冲、稳、保分列，也没有院校网格。出分后再开志愿版档案。目标院校要求仍待观察。
  ],
))

#pagebreak()
#deck-head([来源与免责], [核对前不得当事实])
#row-table(sources.map(s => ([#s.at(0)], [#s.at(1)])))
#v(5mm)
#for line in disclaimer-lines {
  set par(first-line-indent: 0em)
  set text(font: serif, size: 9.2pt)
  line
  v(2.2mm)
}
#v(3mm)
#news-six((
  [
    #text(font: sans, size: 7pt, weight: "bold", fill: muted)[含什么]
    #v(1.6mm)
    #svc-in
  ],
  [
    #text(font: sans, size: 7pt, weight: "bold", fill: muted)[不含什么]
    #v(1.6mm)
    #svc-out
  ],
  [
    #text(font: sans, size: 7pt, weight: "bold", fill: muted)[对象]
    #v(1.6mm)
    #alias · #province · #batch。案例号 #case-id。
  ],
  [
    #text(font: sans, size: 7pt, weight: "bold", fill: muted)[文种]
    #v(1.6mm)
    选科指导报告。不是志愿方案，不是经营讨论稿，不是返佣合同。
  ],
  [
    #text(font: sans, size: 7pt, weight: "bold", fill: muted)[下一步]
    #v(1.6mm)
    监护人确认硬约束仍是原意。对照当年选科要求，核物化地是否关上不可接受的专业门。
  ],
  [
    #text(font: sans, size: 7pt, weight: "bold", fill: muted)[提醒]
    #v(1.6mm)
    相关科目是否跟得上——只记观察，不作录取预测。第三科在地理与生物之间还要观察什么，写进待补。
  ],
))
#v(6mm)
#quiet([签发前须对照当年文件。家庭作最终决定。机构署名：青云未来。本页不含院校推荐，也不等于明年志愿方案。])
