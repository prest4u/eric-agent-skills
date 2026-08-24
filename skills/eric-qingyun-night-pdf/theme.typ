// 青云 · 墨底夜页
// Second-round chassis G. Do not import cold-ink or slate-white.

#let paper = rgb("#2B2E2C")
#let inverted = rgb("#E8E6E1")
#let body-ink = rgb("#B8B5AE")
#let micro = rgb("#8A8882")
#let rule = rgb("#C8C5BE")

#let serif = ("Songti SC", "STSong")
#let sans = ("PingFang SC", "Hiragino Sans GB")
#let latin = ("Avenir Next", "Helvetica Neue")

#let studio-name = "青云"
#let studio-full-name = "青云未来"
#let skin-internal = "墨底夜页" // NEVER printed

#let column-width = 110mm

#let disclaimer-lines = (
  "本文件不是教育考试院或高校官方文件。",
  "本文件不构成录取、就业或薪资承诺。",
  "最终以当年官方系统、招生计划和高校招生章程为准。",
  "过期、缺失或相互冲突的数据，不得当作已核实事实。",
)

#let night-column(body) = block(width: column-width, breakable: true, body)

#let section-head(body) = {
  set par(justify: false, spacing: 0em)
  text(font: sans, size: 15pt, weight: "bold", fill: inverted, tracking: 0.04em, body)
  v(6mm)
}

#let night-note(label, body) = {
  set par(justify: false, spacing: 0em)
  text(font: sans, size: 7.2pt, fill: micro, tracking: 0.16em)[#label]
  v(1.8mm)
  set text(font: serif, size: 10pt, fill: body-ink)
  set par(justify: true, leading: 1.05em, spacing: 0em)
  body
  v(6.5mm)
}

#let row-table(headers, rows) = {
  set text(font: serif, size: 8pt, fill: body-ink)
  set par(justify: false, leading: 0.95em)
  table(
    columns: (26mm, 16mm, 16mm, 16mm, 1fr),
    inset: (x: 0.4mm, y: 2.6mm),
    stroke: (x: none, y: 0.35pt + rule),
    align: (left, center, center, center, left),
    ..headers.map(h => text(font: sans, weight: "bold", fill: inverted, size: 7pt)[#h]),
    ..rows.flatten().map(c => text(font: serif, size: 8pt, fill: body-ink)[#c]),
  )
}

#let sign-block() = {
  set text(font: sans, size: 7pt, fill: micro)
  set par(justify: false)
  grid(
    columns: (1fr, 1fr),
    gutter: 10mm,
    [
      顾问签发
      #v(12mm)
      #line(length: 100%, stroke: 0.35pt + rule)
      #v(1.6mm)
      姓名 / 日期
    ],
    [
      复核
      #v(12mm)
      #line(length: 100%, stroke: 0.35pt + rule)
      #v(1.6mm)
      姓名 / 日期
    ],
  )
}

#let cover-poster(
  title-word: "选科",
  micro-title: "指导报告",
  case-id: "案例合成-TJ2026-0042",
  alias: "林同",
  province: "天津",
  year: "2026",
  batch: "高一选科",
  version: "V1",
  doc-date: "2026-08-19",
  studio: studio-name,
) = page(
  paper: "a4",
  fill: paper,
  margin: 0mm,
  header: none,
  footer: none,
)[
  #set text(lang: "zh", fill: inverted)
  #place(top + left, dx: 16mm, dy: 22mm)[
    #text(font: sans, size: 7pt, fill: micro, tracking: 0.08em)[
      #case-id · #alias · #province · #batch
    ]
  ]
  #place(center + horizon, dy: -8mm)[
    #align(center)[
      #text(
        font: sans,
        size: 72pt,
        weight: "bold",
        fill: inverted,
        tracking: 0.22em,
      )[#title-word]
      #v(4mm)
      #text(font: sans, size: 8pt, fill: micro, tracking: 0.32em)[#micro-title]
    ]
  ]
  #place(bottom + left, dx: 16mm, dy: -20mm)[
    #text(font: sans, size: 13pt, weight: "bold", fill: inverted, tracking: 0.12em)[#studio]
    #v(3mm)
    #text(font: sans, size: 6.6pt, fill: micro, tracking: 0.06em)[不保证录取]
  ]
]

#let night-page(
  title: "选科指导报告",
  case-id: "案例合成-TJ2026-0042",
  alias: "林同",
  province: "天津",
  year: "2026",
  batch: "高一选科",
  version: "V1",
  doc-date: "2026-08-19",
  studio: studio-full-name,
  body,
) = {
  set document(title: title + " · " + alias, author: studio)
  set page(
    paper: "a4",
    fill: paper,
    margin: (top: 17mm, bottom: 22mm, left: 15mm, right: 20mm),
    header: context {
      if counter(page).get().first() > 1 {
        night-column[
          #set text(font: sans, size: 6.6pt, fill: micro, tracking: 0.03em)
          #grid(
            columns: (1fr, auto),
            case-id + "  " + alias + "  " + province + "  " + batch,
            studio,
          )
        ]
      }
    },
    footer: context {
      if counter(page).get().first() == 1 { none } else {
        pad(bottom: 8mm)[
          #night-column[
            #set text(font: sans, size: 6.5pt, fill: micro)
            #grid(
              columns: (1fr, auto, auto),
              column-gutter: 4mm,
              studio,
              [非正式官方文件 · 不保证录取 · 以签发版为准],
              counter(page).display("1"),
            )
          ]
        ]
      }
    },
  )
  set text(font: serif, size: 10pt, fill: body-ink, lang: "zh")
  set par(justify: true, leading: 1.05em, spacing: 0.7em)
  body
}
