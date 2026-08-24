// 青云识别册 · 选科指导报告
// 新底盘：浅青灰卡 + 全无衬线 + 顶通栏 9mm。旧近白纸 / 方块 / 细轨已废止。

#let paper = rgb("#DDE8E4")
#let ink = rgb("#1F2A28")
#let muted = rgb("#3D4E4B")
#let micro = rgb("#5A6B68")
#let hair = rgb("#8F9F9B")
#let brand = rgb("#2F4A47")
#let reverse = rgb("#F7FAF9")

#let sans = ("PingFang SC", "Hiragino Sans GB")
#let latin = ("Avenir Next", "Helvetica Neue")

#let studio-name = "青云"
#let studio-full-name = "青云未来"
#let band-h = 9mm
#let page-x = 18mm
#let page-w = 210mm

#let display(body, size: 30pt) = text(
  font: sans, size: size, weight: "medium", fill: ink, tracking: -0.02em, body,
)

#let kicker(body) = text(
  font: sans, size: 8pt, weight: "medium", fill: brand, tracking: 0.08em, body,
)

#let quiet(body) = {
  set text(font: sans, size: 8.2pt, fill: micro)
  set par(leading: 0.96em, spacing: 0.28em, justify: false)
  body
}

#let lead(body) = {
  set text(font: sans, size: 11pt, fill: ink)
  set par(leading: 1.02em, justify: false)
  body
}

#let top-band(brand-left: studio-name, mid: "", side-right: "") = block(
  width: page-w,
  height: band-h,
  fill: brand,
  inset: (x: page-x, y: 0mm),
  breakable: false,
)[
  #set text(font: sans, size: 8pt, fill: reverse, weight: "medium")
  #align(center + horizon)[
    #grid(
      columns: (1fr, auto, 1fr),
      column-gutter: 4mm,
      align(left + horizon)[#brand-left],
      align(center + horizon)[#mid],
      align(right + horizon)[#side-right],
    )
  ]
]

#let section-head(title, premise: none) = {
  display(title, size: 17pt)
  if premise != none {
    v(3.2mm)
    lead(premise)
  }
  v(6mm)
}

#let row-table(rows, cols: (26mm, 1fr)) = {
  set text(font: sans, size: 9.2pt, fill: ink)
  table(
    columns: cols,
    inset: (x: 0mm, y: 2.6mm),
    stroke: (x: none, y: 0.45pt + hair),
    align: (left + horizon, left + horizon),
    ..rows.map(r => (
      text(fill: brand, weight: "medium")[#r.at(0)],
      [#r.at(1)],
    )).flatten(),
  )
}

#let gate-table(rows) = {
  set text(font: sans, size: 8pt, fill: ink)
  table(
    columns: (28mm, 1fr, 1fr, 1fr, 32mm),
    inset: (x: 1.6mm, y: 2.6mm),
    stroke: (x: none, y: 0.45pt + hair),
    align: (left + horizon, center + horizon, center + horizon, center + horizon, left + horizon),
    text(fill: brand, weight: "medium")[组合],
    text(fill: brand, weight: "medium")[工科门],
    text(fill: brand, weight: "medium")[医学门],
    text(fill: brand, weight: "medium")[经管门],
    text(fill: brand, weight: "medium")[放弃代价],
    ..rows.flatten().map(c => [#c]),
  )
}

#let read-trio(items) = {
  grid(
    columns: (1fr, 1fr, 1fr),
    column-gutter: 6mm,
    ..items.map(it => [
      #text(font: sans, size: 8pt, weight: "medium", fill: brand)[#it.at(0)]
      #v(2mm)
      #set text(font: sans, size: 9pt, fill: ink)
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
  band-center: [],
  band-right: [],
  foot-line: [],
) = page(
  header: none,
  footer: none,
  background: place(top + left)[
    #top-band(mid: band-center, side-right: band-right)
  ],
  margin: (top: 37mm, bottom: 16mm, left: page-x, right: page-x),
)[
  #display(title, size: 30pt)
  #v(8mm)
  #text(font: sans, size: 12pt, fill: muted)[#student]
  #v(7mm)
  #lead(premise)
  #v(1fr)
  #line(length: 100%, stroke: 0.45pt + hair)
  #v(3.2mm)
  #quiet(foot-line)
]

#let qingyun-doc(
  title: "选科指导报告",
  author: studio-full-name,
  case-id: "",
  alias: "",
  province: "",
  year: "",
  batch: "",
  body,
) = {
  let band-center = "选科指导" + "  ·  " + alias + "  ·  " + province
  set document(title: title, author: author)
  set page(
    paper: "a4",
    fill: paper,
    margin: (top: 18mm, bottom: 16mm, left: page-x, right: page-x),
    header: none,
    background: context {
      place(top + left)[
        #top-band(mid: band-center, side-right: case-id)
      ]
    },
    footer: context {
      if counter(page).get().first() == 1 { none } else {
        set text(font: sans, size: 7pt, fill: micro)
        grid(
          columns: (1fr, auto, 1fr),
          studio-full-name,
          [非正式官方文件 · 不保证录取],
          align(right, counter(page).display("01")),
        )
      }
    },
  )
  set text(font: sans, size: 10pt, fill: ink, lang: "zh")
  set par(justify: true, leading: 0.98em, spacing: 0.64em)
  body
}
