// 青云 · 编辑纸本
// 字/网格/封面语法提取自 2026-08-19/E-editorial/document.typ，禁止发明栏轨。
// 客户纸色由 Document Master 终审锁定为冷灰书纸 #E6E4DE，必须离开 C 的 #F3F3F1。
// 研究稿路径：
// Portable extraction of the reviewed editorial study; the private study file is not distributed.

#let paper = rgb("#E6E4DE")
#let ink = rgb("#262626")
#let muted = rgb("#6B6B6B")
#let micro = rgb("#707070")
#let hair = rgb("#C8C8C4")

#let serif = ("Songti SC", "STSong")
#let sans = ("PingFang SC", "Hiragino Sans GB")

#let studio-name = "青云未来"
#let skin-label = "编辑纸本"

#let page-margin = (
  top: 26mm,
  bottom: 24mm,
  left: 28mm,
  right: 28mm,
)

#let body-size = 10.5pt
#let header-size = 8pt
#let chapter-num-size = 22pt
#let chapter-title-size = 16pt
#let cover-title-size = 30pt

#let quiet(body) = {
  set text(font: serif, size: 9pt, fill: micro)
  set par(leading: 1em, justify: false)
  body
}

#let chapter(num, title) = {
  set par(first-line-indent: 0em)
  v(2mm)
  grid(
    columns: (14mm, 1fr),
    gutter: 6mm,
    text(size: chapter-num-size, weight: "bold")[#num],
    align(horizon, text(size: chapter-title-size, weight: "bold")[#title]),
  )
  v(3mm)
  line(length: 22mm, stroke: 0.6pt + ink)
  v(7mm)
}

#let labeled-rows(rows, row-gutter: 4.2mm) = {
  set par(first-line-indent: 0em)
  grid(
    columns: (24mm, 1fr),
    row-gutter: row-gutter,
    column-gutter: 6mm,
    ..rows.map(row => (
      text(fill: muted)[#row.at(0)],
      [#row.at(1)],
    )).flatten(),
  )
}

#let gate-table(rows) = {
  set par(first-line-indent: 0em)
  set text(size: 9pt)
  table(
    columns: (26mm, 1fr, 1fr, 1fr, 30mm),
    inset: (x: 0mm, y: 3.2mm),
    stroke: (x: none, y: 0.4pt + hair),
    align: (left, center, center, center, left),
    text(weight: "bold")[组合],
    text(weight: "bold")[工科门],
    text(weight: "bold")[医学门],
    text(weight: "bold")[经管门],
    text(weight: "bold")[放弃代价],
    ..rows.flatten().map(c => [#c]),
  )
}

#let disclaimer-prose(lines) = {
  for line in lines {
    set par(first-line-indent: 2em)
    line
  }
}

#let editorial-header(left, right) = context {
  if counter(page).get().first() > 1 {
    set text(font: serif, size: header-size, fill: micro)
    grid(
      columns: (1fr, auto),
      left,
      right,
    )
    v(2mm)
    line(length: 100%, stroke: 0.4pt + hair)
  }
}

#let editorial-footer(left) = context {
  if counter(page).get().first() == 1 { none } else {
    set text(font: serif, size: header-size, fill: micro)
    grid(
      columns: (1fr, auto, 1fr),
      left,
      [非正式官方文件 · 不保证录取],
      align(right, counter(page).display("一")),
    )
  }
}

#let editorial-doc(
  title: "选科指导报告",
  author: studio-name,
  header-left: "选科指导报告",
  header-right: "",
  footer-left: none,
  body,
) = {
  let foot-left = if footer-left == none {
    studio-name + " · " + skin-label
  } else {
    footer-left
  }
  set document(title: title, author: author)
  set page(
    paper: "a4",
    fill: paper,
    margin: page-margin,
    header: editorial-header(header-left, header-right),
    footer: editorial-footer(foot-left),
  )
  set text(font: serif, size: body-size, fill: ink, lang: "zh", tracking: 0.02em)
  set par(justify: true, leading: 1.05em, spacing: 0.85em, first-line-indent: 2em)
  body
}

#let cover-page(
  kicker: skin-label,
  title: "选科指导报告",
  meta: "",
  lead: [],
  colophon: [],
) = {
  page(header: none, footer: none)[
    #set par(first-line-indent: 0em)
    #align(center)[
      #v(18mm)
      #text(size: 11pt, tracking: 0.42em)[#studio-name]
      #v(3mm)
      #text(font: sans, size: 6.8pt, fill: micro, tracking: 0.06em)[#kicker]
      #v(22mm)
      #text(size: cover-title-size, weight: "bold", tracking: 0.08em)[#title]
      #v(10mm)
      #text(size: 11pt, fill: muted)[#meta]
      #v(14mm)
      #line(length: 18mm, stroke: 0.55pt + ink)
      #v(12mm)
      #block(width: 92mm)[
        #set par(justify: true, leading: 1.12em, first-line-indent: 0em)
        #set text(size: 11pt)
        #lead
      ]
      #v(1fr)
      #set text(size: 9pt, fill: micro)
      #colophon
      #v(8mm)
    ]
  ]
}
