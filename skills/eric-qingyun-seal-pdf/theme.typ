// 青云 · 选科指导报告
// 内部名：朱印砂卷。客户可见只写「青云未来」；封面朱印「青云」为版式元素保留。禁止把内部名印上 PDF。
// 四硬差：砂褐纸 #C4A882 / 隶书题+楷体文 / 四周 6mm 细框 / 封面框内朱印「青云」
// 不是 A/B 换色。禁止栏轨、题签、顶通栏、拉丁底栏对、公章/国徽。

#let paper = rgb("#C4A882")
#let ink = rgb("#2A1F16")
#let muted = rgb("#4A3B2E")
#let micro = rgb("#6B5A48")
#let hair = rgb("#8A7358")
#let frame-paint = rgb("#3D2E22")
#let vermilion = rgb("#C23A2B")

#let baoli = ("Baoli SC", "Libian SC")
#let kai = ("Kaiti SC", "STKaiti")

#let studio-name = "青云未来"

#let page-w = 210mm
#let page-h = 297mm
#let frame-inset = 6mm
#let frame-thickness = 0.55pt
#let seal-size = 30mm

// 内容边距从裁切起算，落在细框内侧。
#let page-margin = (
  top: 17mm,
  bottom: 16mm,
  left: 17mm,
  right: 17mm,
)

#let body-size = 10.5pt
#let cover-title-size = 34pt

#let display(body, size: 28pt) = text(
  font: baoli,
  size: size,
  fill: ink,
  body,
)

#let lead(body) = {
  set text(font: kai, size: 11.5pt, fill: ink)
  set par(leading: 1.08em, justify: true, first-line-indent: 0em)
  body
}

#let quiet(body) = {
  set text(font: kai, size: 8.5pt, fill: micro)
  set par(leading: 1em, justify: false, first-line-indent: 0em)
  body
}

#let section-head(title, premise: none) = {
  set par(first-line-indent: 0em)
  display(title, size: 18pt)
  if premise != none {
    v(3.2mm)
    lead(premise)
  }
  v(6mm)
}

#let row-table(rows, cols: (28mm, 1fr)) = {
  set par(first-line-indent: 0em)
  set text(font: kai, size: 9.5pt, fill: ink)
  table(
    columns: cols,
    inset: (x: 0mm, y: 2.8mm),
    stroke: (x: none, y: 0.45pt + hair),
    align: (left + horizon, left + horizon),
    ..rows.map(r => (
      text(font: baoli, size: 9pt, fill: muted)[#r.at(0)],
      [#r.at(1)],
    )).flatten(),
  )
}

#let gate-table(rows) = {
  set par(first-line-indent: 0em)
  set text(font: kai, size: 8.6pt, fill: ink)
  table(
    columns: (26mm, 1fr, 1fr, 1fr, 42mm),
    inset: (x: 1.4mm, y: 2.8mm),
    stroke: (x: none, y: 0.45pt + hair),
    align: (left + horizon, center + horizon, center + horizon, center + horizon, left + horizon),
    text(font: baoli, size: 9pt, fill: muted)[组合],
    text(font: baoli, size: 9pt, fill: muted)[工科门],
    text(font: baoli, size: 9pt, fill: muted)[医学门],
    text(font: baoli, size: 9pt, fill: muted)[经管门],
    text(font: baoli, size: 9pt, fill: muted)[放弃代价],
    ..rows.flatten().map(c => [#c]),
  )
}

#let read-trio(items) = {
  set par(first-line-indent: 0em)
  grid(
    columns: (1fr, 1fr, 1fr),
    column-gutter: 6mm,
    ..items.map(it => [
      #text(font: baoli, size: 11pt, fill: ink)[#it.at(0)]
      #v(2.2mm)
      #set text(font: kai, size: 9.5pt, fill: ink)
      #set par(leading: 1.02em, justify: true, first-line-indent: 0em)
      #it.at(1)
    ]),
  )
  v(2.6mm)
  line(length: 100%, stroke: 0.45pt + hair)
}

#let disclaimer-block(lines) = {
  set par(first-line-indent: 0em)
  display([免责], size: 14pt)
  v(3.2mm)
  for line in lines {
    set text(font: kai, size: 10.5pt, fill: ink)
    set par(first-line-indent: 2em, leading: 1.1em, justify: true)
    line
    parbreak()
  }
}

// 工作室朱文方印「青云」。双线方印，朱砂字。不是公章，无星、无圆、无国徽。
#let studio-seal(size: seal-size) = {
  let gap = 1.55mm
  box(width: size, height: size)[
    #place(center + horizon)[
      #rect(
        width: size,
        height: size,
        fill: none,
        stroke: 1.2pt + vermilion,
      )
    ]
    #place(center + horizon)[
      #rect(
        width: size - 2 * gap,
        height: size - 2 * gap,
        fill: none,
        stroke: 0.5pt + vermilion,
      )
    ]
    #align(center + horizon)[
      #grid(
        rows: (auto, auto),
        row-gutter: 1.1mm,
        align: center,
        text(font: baoli, size: 20pt, fill: vermilion)[青],
        text(font: baoli, size: 20pt, fill: vermilion)[云],
      )
    ]
  ]
}

// 四周连续细框，距裁切 6mm。不是断轨，不是左栏轨，不是顶通栏。
#let page-frame() = {
  place(top + left, dx: frame-inset, dy: frame-inset)[
    #rect(
      width: page-w - 2 * frame-inset,
      height: page-h - 2 * frame-inset,
      fill: none,
      stroke: frame-thickness + frame-paint,
    )
  ]
}

#let inner-footer() = context {
  if counter(page).get().first() == 1 { none } else {
    set text(font: kai, size: 7.5pt, fill: micro)
    v(1.2mm)
    grid(
      columns: (1fr, auto, 1fr),
      studio-name,
      [非正式官方文件 · 不保证录取],
      align(right, counter(page).display("01")),
    )
  }
}

#let cover-page(
  title: [选科指导报告],
  student: [],
  premise: [],
  colophon: [],
) = page(
  header: none,
  footer: none,
  margin: page-margin,
)[
  #set par(first-line-indent: 0em)
  // 朱印落在框内右上，用 place 不撑破细框。
  #place(top + right, dx: 2mm, dy: 1mm)[
    #studio-seal(size: seal-size)
  ]
  #v(8mm)
  #align(left)[
    #display(title, size: cover-title-size)
  ]
  #v(9mm)
  #text(font: kai, size: 12pt, fill: muted)[#student]
  #v(8mm)
  #block(width: 118mm)[
    #lead(premise)
  ]
  #v(1fr)
  #line(length: 28mm, stroke: 0.45pt + hair)
  #v(3.2mm)
  #quiet(colophon)
]

#let seal-doc(
  title: "选科指导报告",
  author: studio-name,
  case-id: "",
  alias: "",
  province: "",
  year: "",
  batch: "",
  body,
) = {
  set document(title: title, author: author)
  set page(
    paper: "a4",
    fill: paper,
    margin: page-margin,
    header: none,
    background: page-frame(),
    footer: inner-footer(),
  )
  set text(font: kai, size: body-size, fill: ink, lang: "zh")
  set par(justify: true, leading: 1.05em, spacing: 0.82em)
  body
}

#let qingyun-doc = seal-doc
