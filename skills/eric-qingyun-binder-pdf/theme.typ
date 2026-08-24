// 青云 · 活页齿孔
// 第二轮新底盘 J。石灰纸 / 行楷题+黑体文 / 左 12mm 齿孔 / 抽出页封面

#let paper = rgb("#C9C6BF")
#let ink = rgb("#2C2C2A")
#let muted = rgb("#5C5B57")
#let micro = rgb("#7A7974")
#let hair = rgb("#A8A59E")
#let punch = rgb("#6A6964")

#let xing = ("Xingkai SC", "Xingkai TC")
#let hei = ("Heiti SC", "STHeiti", "Hiragino Sans GB")

#let studio-name = "青云未来"
#let skin-label = "活页齿孔"
#let punch-gutter = 12mm
#let hole-diameter = 2.9mm

#let page-margin = (
  top: 20mm,
  bottom: 18mm,
  left: 19mm,
  right: 17mm,
)

#let body-size = 10pt
#let header-size = 7.5pt
#let cover-title-size = 30pt

#let quiet(body) = {
  set text(font: hei, size: 8.5pt, fill: micro)
  set par(leading: 1em, justify: false, first-line-indent: 0em)
  body
}

#let labeled-rows(rows, row-gutter: 4mm) = {
  set par(first-line-indent: 0em)
  grid(
    columns: (18mm, 1fr),
    row-gutter: row-gutter,
    column-gutter: 5mm,
    ..rows.map(row => (
      text(font: xing, fill: muted, size: 11pt)[#row.at(0)],
      text(font: hei)[#row.at(1)],
    )).flatten(),
  )
}

#let gate-table(rows) = {
  set par(first-line-indent: 0em)
  set text(font: hei, size: 8.5pt)
  table(
    columns: (22mm, 1fr, 1fr, 1fr, 32mm),
    inset: (x: 0mm, y: 2.8mm),
    stroke: (x: none, y: 0.4pt + hair),
    align: (left, center, center, center, left),
    text(font: xing, size: 10pt)[组合],
    text(font: xing, size: 10pt)[工科门],
    text(font: xing, size: 10pt)[医学门],
    text(font: xing, size: 10pt)[经管门],
    text(font: xing, size: 10pt)[放弃代价],
    ..rows.flatten().map(c => [#c]),
  )
}

#let disclaimer-prose(lines) = {
  for sentence in lines {
    set par(first-line-indent: 0em, leading: 1.12em, spacing: 0.85em)
    sentence
    parbreak()
  }
}

#let binder-holes() = {
  let page-h = 297mm
  let n = 7
  let top-pad = 24mm
  let bot-pad = 22mm
  let span = page-h - top-pad - bot-pad
  let hole-r = hole-diameter / 2

  place(dx: punch-gutter, dy: 0mm, line(
    start: (0pt, 0pt),
    end: (0pt, page-h),
    stroke: (paint: punch, thickness: 0.45pt, dash: (1.1pt, 1.6pt)),
  ))

  for i in range(n) {
    let y = top-pad + span * i / (n - 1)
    place(
      dx: punch-gutter - hole-r,
      dy: y - hole-r,
      circle(
        radius: hole-r,
        fill: none,
        stroke: 0.55pt + punch,
      ),
    )
  }
}

#let binder-footer() = context {
  if counter(page).get().first() == 1 { none } else {
    set text(font: hei, size: header-size, fill: micro)
    grid(
      columns: (1fr, 1fr),
      [#studio-name · #counter(page).display()],
      align(right)[非正式官方文件 · 不保证录取],
    )
  }
}

#let binder-doc(
  title: "选科说明",
  author: studio-name,
  body,
) = {
  set document(title: title, author: author)
  set page(
    paper: "a4",
    fill: paper,
    margin: page-margin,
    background: binder-holes(),
    header: none,
    footer: binder-footer(),
  )
  set text(font: hei, size: body-size, fill: ink, lang: "zh")
  set par(justify: true, leading: 1.12em, spacing: 0.85em, first-line-indent: 0em)
  body
}

#let cover-page(
  title: "选科说明",
  mark: "青云",
  meta: "",
  colophon: [],
) = {
  page(
    header: none,
    footer: none,
    fill: paper,
    margin: page-margin,
    background: binder-holes(),
  )[
    #set par(first-line-indent: 0em, justify: false)
    #align(right)[
      #text(font: hei, size: 10pt, fill: muted)[#mark]
    ]
    #v(22mm)
    #text(font: xing, size: cover-title-size, fill: ink, weight: "bold")[#title]
    #v(8mm)
    #text(font: hei, size: 10.5pt, fill: muted)[#meta]
    #v(1fr)
    #set text(font: hei, size: 9pt, fill: micro)
    #colophon
    #v(4mm)
  ]
}
