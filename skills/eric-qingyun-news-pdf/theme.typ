// 青云 · 新闻栏 · 选科指导报告
// Token 来自 Chief of Staff / Document Master 第二轮新底盘 I 调度。
// 磁盘无 I 研究稿，本皮不是从 I 研究稿提取。
// 禁止从 E 编辑纸本 / D 识别册 / v2 C 分栏纪录纸换色交差。
// 客户可见只写「青云未来」；封面报头「青云」为版式元素保留。

#let paper = rgb("#D2CBB8")
#let ink = rgb("#111111")
#let muted = rgb("#4A463C")
#let micro = rgb("#6A6458")
#let hair = rgb("#8A8474")
#let mast = rgb("#111111")
#let reverse = rgb("#F4EFE4")

#let serif = ("Songti SC", "STSong")
#let headline = ("Heiti SC", "Hiragino Sans GB", "PingFang SC")
#let sans = ("Heiti SC", "Hiragino Sans GB", "PingFang SC")

#let studio-name = "青云"
#let studio-full-name = "青云未来"
#let skin-label = "新闻栏"

#let columns-n = 6
#let col-gutter = 2.8mm

#let page-margin = (
  top: 15mm,
  bottom: 11mm,
  left: 11mm,
  right: 11mm,
)

#let body-size = 8.4pt
#let kicker-size = 7pt
#let deck-size = 18pt
#let cover-title-size = 26pt
#let mast-name-size = 15pt

#let quiet(body) = {
  set text(font: sans, size: 7.2pt, fill: micro)
  set par(leading: 0.92em, spacing: 0.28em, justify: false, first-line-indent: 0em)
  body
}

#let lead(body) = {
  set text(font: serif, size: 9.2pt, fill: ink)
  set par(leading: 0.95em, justify: true, first-line-indent: 0em)
  body
}

#let deck-head(kicker, title) = {
  set par(first-line-indent: 0em)
  text(font: sans, size: kicker-size, weight: "bold", fill: muted, tracking: 0.08em)[#kicker]
  v(1.6mm)
  text(font: headline, size: deck-size, weight: "bold", fill: ink, tracking: -0.02em)[#title]
  v(3.2mm)
}

// Typst columns() 会吃掉本页剩余高度。整页长文用这个；与表混排用 news-six。
#let news-flow(body) = {
  set text(font: serif, size: body-size, fill: ink)
  set par(justify: true, leading: 0.88em, spacing: 0.46em, first-line-indent: 0em)
  columns(columns-n, gutter: col-gutter, body)
}

#let news-six(items) = {
  set par(first-line-indent: 0em, justify: true, leading: 0.9em, spacing: 0.42em)
  set text(font: serif, size: body-size, fill: ink)
  grid(
    columns: (1fr, 1fr, 1fr, 1fr, 1fr, 1fr),
    column-gutter: 0mm,
    ..items.enumerate().map(((i, item)) => {
      block(
        width: 100%,
        inset: (
          left: if i == 0 { 0mm } else { 2.1mm },
          right: 2.0mm,
        ),
        stroke: (left: if i == 0 { none } else { 0.3pt + hair }),
        item,
      )
    }),
  )
}

#let row-table(rows, cols: (22mm, 1fr)) = {
  set par(first-line-indent: 0em)
  set text(font: sans, size: 8pt, fill: ink)
  table(
    columns: cols,
    inset: (x: 0mm, y: 2.4mm),
    stroke: (x: none, y: 0.35pt + hair),
    fill: none,
    align: (left + horizon, left + horizon),
    ..rows.map(r => (
      text(fill: muted, weight: "bold")[#r.at(0)],
      text(font: serif, size: 8.4pt)[#r.at(1)],
    )).flatten(),
  )
}

#let gate-table(rows) = {
  set par(first-line-indent: 0em)
  set text(font: sans, size: 7.4pt, fill: ink)
  table(
    columns: (28mm, 1fr, 1fr, 1fr, 34mm),
    inset: (x: 1.4mm, y: 2.3mm),
    stroke: (x: none, y: 0.35pt + hair),
    fill: none,
    align: (left + horizon, center + horizon, center + horizon, center + horizon, left + horizon),
    text(weight: "bold")[组合],
    text(weight: "bold")[工科门],
    text(weight: "bold")[医学门],
    text(weight: "bold")[经管门],
    text(weight: "bold")[放弃代价],
    ..rows.flatten().map(c => [#c]),
  )
}

#let news-header(left, right) = context {
  if counter(page).get().first() > 1 {
    set text(font: sans, size: 7pt, fill: micro)
    grid(
      columns: (1fr, auto),
      left,
      right,
    )
    v(1.3mm)
    line(length: 100%, stroke: 0.45pt + ink)
  }
}

#let news-footer(left) = context {
  if counter(page).get().first() == 1 { none } else {
    set text(font: sans, size: 7pt, fill: micro)
    grid(
      columns: (1fr, auto, 1fr),
      left,
      [非正式官方文件 · 不保证录取],
      align(right, counter(page).display("01")),
    )
  }
}

#let news-doc(
  title: "选科指导报告",
  author: studio-full-name,
  header-left: studio-full-name,
  header-right: "",
  footer-left: none,
  body,
) = {
  let foot-left = if footer-left == none { studio-full-name } else { footer-left }
  set document(title: title, author: author)
  set page(
    paper: "a4",
    fill: paper,
    margin: page-margin,
    header: news-header(header-left, header-right),
    footer: news-footer(foot-left),
  )
  set text(font: serif, size: body-size, fill: ink, lang: "zh")
  set par(justify: true, leading: 0.88em, spacing: 0.46em, first-line-indent: 0em)
  body
}

#let cover-page(
  date: "",
  title: "选科指导报告",
  dek: "",
  briefs: (),
  colophon: [],
) = {
  page(
    header: none,
    footer: none,
    margin: (top: 12mm, bottom: 11mm, left: 11mm, right: 11mm),
  )[
    #set par(first-line-indent: 0em)
    #grid(
      columns: (1fr, auto),
      text(font: headline, size: mast-name-size, weight: "bold", fill: ink)[#studio-name],
      align(bottom, text(font: sans, size: 8pt, fill: muted)[#date]),
    )
    #v(2.2mm)
    #block(
      width: 100%,
      fill: mast,
      inset: (x: 3.2mm, y: 4.6mm),
    )[
      #set align(center)
      #text(
        font: headline,
        size: cover-title-size,
        weight: "bold",
        fill: reverse,
        tracking: 0.04em,
      )[#title]
    ]
    #v(3.2mm)
    #text(font: sans, size: 9pt, fill: muted)[#dek]
    #v(3.6mm)
    #if briefs != () {
      news-six(briefs)
    }
    #v(1fr)
    #line(length: 100%, stroke: 0.45pt + ink)
    #v(2.2mm)
    #set text(font: sans, size: 7.2pt, fill: micro)
    #colophon
  ]
}
