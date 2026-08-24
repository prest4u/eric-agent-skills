// 青云 · 选科指导报告
// 内部名：藤紫点阵。客户可见只写「青云未来」，禁止把内部名印上 PDF。
// 四硬差：藤紫纸 #B7A8C8 / 全书仿宋 / 5mm 圆点点阵 / 封面左齐大题+其下小「青云」
// 不是 E 28mm 书页、不是 J 左齿孔、不是 I 六栏报头。无框无轨无栏。

#let paper = rgb("#B7A8C8")
#let ink = rgb("#2C2438")
#let muted = rgb("#564866")
#let micro = rgb("#6E5E82")
#let hair = rgb("#8A7A9C")
#let dot-paint = rgb("#9A8BB0")

#let fang = ("STFangsong",)

#let studio-name = "青云"
#let studio-full-name = "青云未来"

#let page-w = 210mm
#let page-h = 297mm
#let lattice-step = 5mm
#let lattice-radius = 0.48mm

#let page-margin = (
  top: 20mm,
  bottom: 16mm,
  left: 18mm,
  right: 18mm,
)

#let body-size = 10.5pt
#let cover-title-size = 34pt
#let cover-mark-size = 13pt
#let head-size = 16pt
#let footer-size = 7.5pt

#let quiet(body) = {
  set text(font: fang, size: 9pt, fill: micro)
  set par(leading: 1.05em, spacing: 0.4em, justify: false, first-line-indent: 0em)
  body
}

#let lead(body) = {
  set text(font: fang, size: 11pt, fill: ink)
  set par(leading: 1.12em, spacing: 0.7em, justify: false, first-line-indent: 0em)
  body
}

#let section-head(title) = {
  set par(first-line-indent: 0em)
  text(font: fang, size: head-size, fill: ink)[#title]
  v(4.2mm)
}

// 满页浅圆点阵：5mm 间距，点色略深于纸。不是线格、不是框、不是栏轨。
#let lattice-field() = {
  let cols = 43
  let rows = 61
  let paint = dot-paint.transparentize(28%)
  for i in range(cols) {
    for j in range(rows) {
      place(
        dx: i * lattice-step,
        dy: j * lattice-step,
        circle(radius: lattice-radius, fill: paint, stroke: none),
      )
    }
  }
}

#let row-table(rows, cols: (28mm, 1fr)) = {
  set par(first-line-indent: 0em)
  set text(font: fang, size: 9.6pt, fill: ink)
  table(
    columns: cols,
    inset: (x: 0mm, y: 2.6mm),
    stroke: (x: none, y: 0.25pt + hair),
    fill: none,
    align: (left + horizon, left + horizon),
    ..rows.map(r => (
      text(fill: muted)[#r.at(0)],
      [#r.at(1)],
    )).flatten(),
  )
}

#let gate-table(rows) = {
  set par(first-line-indent: 0em)
  set text(font: fang, size: 9pt, fill: ink)
  table(
    columns: (28mm, 1fr, 1fr, 1fr, 38mm),
    inset: (x: 1.2mm, y: 2.5mm),
    stroke: (x: none, y: 0.25pt + hair),
    fill: none,
    align: (left + horizon, center + horizon, center + horizon, center + horizon, left + horizon),
    text(fill: muted)[组合],
    text(fill: muted)[工科门],
    text(fill: muted)[医学门],
    text(fill: muted)[经管门],
    text(fill: muted)[放弃代价],
    ..rows.flatten().map(c => [#c]),
  )
}

#let lattice-footer() = {
  set text(font: fang, size: footer-size, fill: micro)
  set par(first-line-indent: 0em, justify: false)
  context [
    #studio-full-name · 非正式官方文件 · 不保证录取 · #counter(page).display()
  ]
}

#let cover-page(
  title: [选科指导报告],
  mark: studio-name,
  meta: [],
  opener: [],
  body: [],
) = page(
  header: none,
  footer: lattice-footer(),
  margin: page-margin,
)[
  #set par(first-line-indent: 0em, justify: false)
  #set align(left)
  #v(18mm)
  #text(font: fang, size: cover-title-size, fill: ink)[#title]
  #v(3.2mm)
  #text(font: fang, size: cover-mark-size, fill: ink)[#mark]
  #v(10mm)
  #text(font: fang, size: 11pt, fill: muted)[#meta]
  #v(8mm)
  #lead(opener)
  #v(7mm)
  #body
]

#let lattice-doc(
  title: "选科指导报告",
  author: studio-full-name,
  body,
) = {
  set document(title: title, author: author)
  set page(
    paper: "a4",
    fill: paper,
    margin: page-margin,
    header: none,
    background: lattice-field(),
    footer: lattice-footer(),
  )
  set text(font: fang, size: body-size, fill: ink, lang: "zh")
  set par(justify: false, leading: 1.12em, spacing: 0.78em, first-line-indent: 0em)
  set align(left)
  body
}

#let qingyun-doc = lattice-doc
