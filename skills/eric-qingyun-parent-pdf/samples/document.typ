#import "/theme.typ": *
#import "facts.typ": *

#show: parent-doc.with(
  title: "给家长的说明 · 林同",
  author: studio,
)

#cover-page(
  title: "给家长的说明",
  slip: "青云",
  meta: alias + " · " + province + " · " + batch + " · " + case-id,
  colophon: [
    合成示例 · 非正式官方文件 · 不保证录取 \
    #doc-date · #version
  ],
)

#spread(
  [
    #text(size: 11pt, fill: ink)[怎么读]

    #v(5mm)
    事实\
    可回文件核对

    #v(3mm)
    判断\
    不是录取结论

    #v(3mm)
    待核验\
    不得当已核实

    #v(6mm)
    本册讲科目门\
    不开冲稳保
  ],
  [
    #set par(first-line-indent: 0em)
    #text(font: kai, size: 16pt, fill: ink)[怎么读这本说明]
    #v(6mm)
    #set par(first-line-indent: 2em)
    先把读法说清楚。这本说明是坐下来跟家长对一下科目门，不是咨询签发，也不开志愿方案。话分成三类，请按这个读。

    事实，是可以回到当年官方文件核对的条目。判断，是顾问的归类和取舍，不是录取结论。待核验，是缺来源、过期、或还没对照当年要求的条目；这一类不能当成已经核实的事实。

    本册只讲科目门：选了这组科，哪一类专业的门还开着，哪一类会关上。本册不开冲稳保。冲稳保只出现在志愿方案里，这里不列院校。
  ],
)

#pagebreak()

#spread(
  [
    #text(size: 11pt, fill: ink)[科目门]

    #v(5mm)
    现行\
    物化地

    #v(3mm)
    备选\
    物化生

    #v(3mm)
    第三组\
    物生地

    #v(6mm)
    只谈门是否关上\
    无填色、无勾选
  ],
  [
    #set par(first-line-indent: 0em)
    #text(font: kai, size: 16pt, fill: ink)[林同这组科目]
    #v(6mm)
    #labeled-rows((
      ([现行], [#current-combo（合成）]),
      ([备选], [#alt-combo（合成）]),
      ([第三组], [#third-combo（合成）]),
      ([硬约束], [#hard]),
      ([软偏好], [#soft]),
      ([待核验], [#pending]),
    ))
    #v(6mm)
    #set par(first-line-indent: 2em)
    下面这张表只谈门是否关上。没有填色，没有勾选，也不开冲稳保列。表里的状态是合成口径，一律待核验。具体专业仍以当年高校公布为准。
    #v(5mm)
    #gate-table(gate-rows)
    #v(5mm)
    若家里更看重工科门，保留物理和化学，通常比第三科来回换更稳妥。这是判断，不是结论。目标专业的最新选科要求，还待核验。
  ],
)

#pagebreak()

#spread(
  [
    #text(size: 11pt, fill: ink)[免责]

    #v(5mm)
    待核验来源\
    两行，未当作事实

    #v(3mm)
    四句原文\
    不得改写

    #v(6mm)
    家庭\
    作最终决定
  ],
  [
    #set par(first-line-indent: 0em)
    #text(font: kai, size: 16pt, fill: ink)[来源与免责]
    #v(6mm)
    #labeled-rows((
      ([待核验], [天津市普通高中学业水平选择性考试科目要求（合成示例，查询日 #doc-date）。]),
      ([待核验], [高校招生专业选科要求汇编（合成示例；须回当年高校章程）。]),
    ), row-gutter: 4.5mm)
    #v(8mm)
    #disclaimer-prose(disclaimer-lines)
    #v(8mm)
    #set par(first-line-indent: 2em)
    家里作最终决定。说明册帮家长看清门，不代替家长拍板，也不保证录取。
    #v(4mm)
    #set par(first-line-indent: 0em)
    #quiet([青云未来 · 家长说明册 · 合成示例。])
  ],
)
