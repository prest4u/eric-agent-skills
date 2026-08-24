#import "/theme.typ": *
#import "facts.typ": *

#show: binder-doc.with(
  title: "选科说明 · 林同",
  author: studio,
)

#cover-page(
  title: "选科说明",
  mark: "青云",
  meta: alias + " · " + province + " · " + batch + " · " + case-id,
  colophon: [
    合成示例 · 非正式官方文件 · 不保证录取 \
    #doc-date · #version
  ],
)

#set par(first-line-indent: 0em)
#text(font: xing, size: 17pt, fill: ink, weight: "bold")[怎么读]
#v(5mm)

抽出这一页，先分三类钉住：事实、判断、待核验。本页只讲科目门，不开冲稳保。

#v(3mm)
#labeled-rows((
  ([事实], [可以回到当年官方文件核对的条目。]),
  ([判断], [顾问的归类和取舍，不是录取结论。]),
  ([待核验], [缺来源、过期、或还没对照当年要求的条目；这一类不能当成已经核实的事实。]),
), row-gutter: 5mm)

#v(7mm)
这一页不签发、不坐下来讲解。它是从活页夹抽出的读法页：先分清三类，再看下一页的科目门。冲稳保只出现在志愿方案里，这里不列院校。

#pagebreak()

#set par(first-line-indent: 0em)
#text(font: xing, size: 17pt, fill: ink, weight: "bold")[林同这组科目]
#v(5mm)

#labeled-rows((
  ([现行], [#current-combo（合成）]),
  ([备选], [#alt-combo（合成）]),
  ([第三组], [#third-combo（合成）]),
  ([硬约束], [#hard]),
  ([软偏好], [#soft]),
  ([待核验], [#pending]),
))

#v(6mm)
下面这张表只谈门是否关上。没有填色，没有勾选，也不开冲稳保列。表里的状态是合成口径，一律待核验。具体专业仍以当年高校公布为准。
#v(4mm)
#gate-table(gate-rows)
#v(5mm)
若家里更看重工科门，保留物理和化学，通常比第三科来回换更稳妥。这是判断，不是结论。目标专业的最新选科要求，还待核验。

#pagebreak()

#set par(first-line-indent: 0em)
#text(font: xing, size: 17pt, fill: ink, weight: "bold")[来源与免责]
#v(5mm)

#labeled-rows((
  ([待核验], [天津市普通高中学业水平选择性考试科目要求（合成示例，查询日 #doc-date）。]),
  ([待核验], [高校招生专业选科要求汇编（合成示例；须回当年高校章程）。]),
), row-gutter: 4.5mm)

#v(7mm)
#disclaimer-prose(disclaimer-lines)
#v(6mm)
家里作最终决定。这一页帮家庭看清口径，不代替拍板，也不保证录取。
