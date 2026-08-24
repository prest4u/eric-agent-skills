// 青云 · 霜蓝通缘 · 选科指导报告
// 底盘 H：霜蓝卡 + 魏碑标题 + 右缘 28mm 涂布色条。
// 不是识别册（浅青卡 + 顶通栏 + 全无衬线）。禁止顶通栏 / 左轨 / DOCUMENT/STATUS。
// 客户可见只写「青云未来」；封面/色条竖排「青云」为版式元素保留。

#let paper = rgb("#C5D4E0")
#let ink = rgb("#1A2430")
#let muted = rgb("#3A4C5C")
#let micro = rgb("#5C7084")
#let hair = rgb("#8A9BB0")
#let strip = rgb("#2B4C63")
#let reverse = rgb("#F3F7FA")

#let display-font = ("Weibei SC", "Heiti SC", "STHeiti")
#let body-font = (
  (name: "Avenir Next", covers: "latin-in-cjk"),
  "Heiti SC",
  "STHeiti",
)
#let latin = ("Avenir Next", "Helvetica Neue")

#let studio-name = "青云未来"
#let strip-w = 28mm
#let page-h = 297mm
#let page-x = 18mm

#let display(body, size: 40pt) = text(
  font: display-font, size: size, fill: ink, body,
)

#let kicker(body) = text(
  font: body-font, size: 8pt, fill: strip, tracking: 0.06em, body,
)

#let quiet(body) = {
  set text(font: body-font, size: 8.2pt, fill: micro)
  set par(leading: 0.96em, spacing: 0.28em, justify: false)
  body
}

#let lead(body) = {
  set text(font: body-font, size: 11pt, fill: ink)
  set par(leading: 1.05em, justify: false)
  body
}

#let page-label(n) = numbering("01", n)

#let right-strip(n, is-cover: false) = {
  place(top + right)[
    #block(
      width: strip-w,
      height: page-h,
      fill: strip,
      clip: true,
    )[
      #place(top + center, dy: if is-cover { 38mm } else { 16mm })[
        #align(center)[
          #text(
            font: display-font,
            size: if is-cover { 20pt } else { 10pt },
            fill: reverse,
          )[青]
          #v(if is-cover { 5mm } else { 2.2mm })
          #text(
            font: display-font,
            size: if is-cover { 20pt } else { 10pt },
            fill: reverse,
          )[云]
        ]
      ]
      #place(bottom + center, dy: -18mm)[
        #rotate(-90deg, reflow: false)[
          #text(
            font: latin,
            size: if is-cover { 10pt } else { 9pt },
            fill: reverse,
            tracking: 0.18em,
          )[#page-label(n)]
        ]
      ]
    ]
  ]
}

#let section-head(title, premise: none) = {
  display(title, size: 18pt)
  if premise != none {
    v(3.2mm)
    lead(premise)
  }
  v(6mm)
}

#let row-table(rows, cols: (26mm, 1fr)) = {
  set text(font: body-font, size: 9.2pt, fill: ink)
  table(
    columns: cols,
    inset: (x: 0mm, y: 2.6mm),
    stroke: (x: none, y: 0.45pt + hair),
    align: (left + horizon, left + horizon),
    ..rows.map(r => (
      text(fill: strip)[#r.at(0)],
      [#r.at(1)],
    )).flatten(),
  )
}

#let gate-table(rows) = {
  set text(font: body-font, size: 8pt, fill: ink)
  table(
    columns: (28mm, 1fr, 1fr, 1fr, 32mm),
    inset: (x: 1.6mm, y: 2.6mm),
    stroke: (x: none, y: 0.45pt + hair),
    align: (left + horizon, center + horizon, center + horizon, center + horizon, left + horizon),
    text(fill: strip)[组合],
    text(fill: strip)[工科门],
    text(fill: strip)[医学门],
    text(fill: strip)[经管门],
    text(fill: strip)[放弃代价],
    ..rows.flatten().map(c => [#c]),
  )
}

#let read-trio(items) = {
  grid(
    columns: (1fr, 1fr, 1fr),
    column-gutter: 6mm,
    ..items.map(it => [
      #text(font: display-font, size: 12pt, fill: strip)[#it.at(0)]
      #v(2mm)
      #set text(font: body-font, size: 9pt, fill: ink)
      #set par(leading: 0.98em, justify: false)
      #it.at(1)
    ]),
  )
  v(2.4mm)
  line(length: 100%, stroke: 0.45pt + hair)
}

#let disclaimer-block(lines) = {
  kicker([免责])
  v(2.4mm)
  for line in lines {
    quiet(line)
    v(1.1mm)
  }
}

#let cover-page(
  title: [选科指导报告],
  student: [],
  premise: [],
  foot-line: [],
) = page(
  header: none,
  footer: none,
  fill: paper,
  background: context {
    right-strip(counter(page).get().first(), is-cover: true)
  },
  margin: (top: 32mm, bottom: 18mm, left: page-x, right: strip-w),
)[
  #align(left)[
    #display(title, size: 40pt)
    #v(10mm)
    #text(font: body-font, size: 12pt, fill: muted)[#student]
    #v(8mm)
    #lead(premise)
  ]
  #v(1fr)
  #line(length: 100%, stroke: 0.45pt + hair)
  #v(3.2mm)
  #quiet(foot-line)
]

#let qingyun-doc(
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
    margin: (top: 18mm, bottom: 16mm, left: page-x, right: strip-w),
    header: none,
    footer: none,
    background: context {
      let n = counter(page).get().first()
      right-strip(n, is-cover: n == 1)
    },
  )
  set text(font: body-font, size: 10pt, fill: ink, lang: "zh")
  set par(justify: false, leading: 1.0em, spacing: 0.64em)
  body
}
