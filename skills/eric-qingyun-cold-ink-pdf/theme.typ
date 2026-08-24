// 青云 · 冷墨事务所
// Tokens extracted from C-cold-ink study. Do not import slate-white.

#let paper = rgb("#F3F3F1")
#let ink = rgb("#1F2122")
#let muted = rgb("#5E6366")
#let micro = rgb("#6A6F72")
#let hair = rgb("#B8BDBE")
#let rule = rgb("#2A2D2E")

#let serif = ("Songti SC", "STSong")
#let sans = ("PingFang SC", "Hiragino Sans GB")
#let latin = ("Avenir Next", "Helvetica Neue")

#let studio-name = "青云未来"
#let skin-internal = "冷墨事务所" // 内部皮肤名，禁止印到客户 PDF
#let study-label-default = studio-name

#let disclaimer-lines = (
  "本文件不是教育考试院或高校官方文件。",
  "本文件不构成录取、就业或薪资承诺。",
  "最终以当年官方系统、招生计划和高校招生章程为准。",
  "过期、缺失或相互冲突的数据，不得当作已核实事实。",
)

#let micro-t(body) = text(font: sans, size: 6.6pt, fill: micro, tracking: 0.04em, body)
#let kicker(body) = text(font: latin, size: 6.8pt, weight: "semibold", fill: muted, tracking: 0.14em, body)
#let quiet(body) = {
  set text(font: sans, size: 8pt, fill: micro)
  set par(leading: 0.9em, spacing: 0.28em, justify: false)
  body
}

#let hairline() = line(length: 100%, stroke: 0.35pt + hair)

#let item(k, body) = {
  grid(
    columns: (22mm, 1fr),
    gutter: 4mm,
    text(font: sans, size: 7.4pt, weight: "semibold", fill: ink)[#k],
    body,
  )
  v(2.1mm)
  hairline()
  v(2.1mm)
}

#let section-head(body) = {
  text(font: sans, size: 8pt, weight: "semibold", body)
  v(3mm)
  hairline()
  v(4mm)
}

#let gate-table(rows) = {
  set text(font: sans, size: 7.5pt)
  table(
    columns: (26mm, 1fr, 1fr, 1fr, 30mm),
    inset: (x: 2mm, y: 2.2mm),
    stroke: 0.35pt + rule,
    align: (left, center, center, center, left),
    text(weight: "semibold")[组合],
    text(weight: "semibold")[工科门],
    text(weight: "semibold")[医学门],
    text(weight: "semibold")[经管门],
    text(weight: "semibold")[放弃代价],
    ..rows.flatten().map(c => [#c]),
  )
}

#let sign-block() = grid(
  columns: (1fr, 1fr),
  gutter: 14mm,
  [
    #quiet([顾问签发])
    #v(11mm)
    #line(length: 100%, stroke: 0.4pt + rule)
    #v(1.5mm)
    #quiet([姓名 / 日期])
  ],
  [
    #quiet([复核])
    #v(11mm)
    #line(length: 100%, stroke: 0.4pt + rule)
    #v(1.5mm)
    #quiet([姓名 / 日期])
  ],
)

#let cold-ink-page(
  title: "选科指导报告",
  case-id: "案例合成-TJ2026-0042",
  alias: "林同",
  province: "天津",
  year: "2026",
  batch: "高一选科",
  version: "V1",
  doc-date: "2026-08-19",
  studio: studio-name,
  study-label: study-label-default,
  body,
) = {
  set document(title: title + " · " + alias, author: studio)
  set page(
    paper: "a4",
    fill: paper,
    margin: (top: 18mm, bottom: 18mm, left: 18mm, right: 18mm),
    header: context {
      if counter(page).get().first() > 1 {
        set text(font: sans, size: 6.6pt, fill: micro, tracking: 0.03em)
        grid(
          columns: (1fr, auto),
          case-id + "  " + alias + "  " + province + "  " + batch,
          study-label,
        )
        v(1.2mm)
        line(length: 100%, stroke: 0.35pt + hair)
      }
    },
    footer: context {
      if counter(page).get().first() == 1 { none } else {
        set text(font: sans, size: 6.5pt, fill: micro)
        pad(bottom: 8mm)[
          #v(1mm)
          #line(length: 100%, stroke: 0.35pt + hair)
          #v(2mm)
          #grid(
            columns: (1fr, auto, 1fr),
            studio,
            [非正式官方文件 · 不保证录取 · 以签发版为准],
            align(right, counter(page).display("01")),
          )
        ]
      }
    },
  )
  set text(font: serif, size: 9.2pt, fill: ink, lang: "zh", tracking: 0.006em)
  set par(justify: true, leading: 0.86em, spacing: 0.52em)
  body
}

#let cover-page(
  title: "选科指导报告",
  subtitle: "顾问签发意见。不是志愿方案，不列院校。",
  case-id: "案例合成-TJ2026-0042",
  alias: "林同",
  province: "天津",
  year: "2026",
  batch: "高一选科",
  version: "V1",
  doc-date: "2026-08-19",
  studio: studio-name,
  study-label: study-label-default,
  lead: [本意见只回答一件事：在家庭已确认的约束下，放弃某一科会关上哪一类专业门。不预测录取，不代替家庭作最终决定。],
) = page(header: none, footer: none)[
  #micro-t(study-label)
  #v(8mm)
  #kicker[QINGYUN  OPINION]
  #v(7mm)
  #text(font: serif, size: 22pt, weight: "bold", tracking: -0.01em)[#title]
  #v(3mm)
  #text(font: sans, size: 9pt, fill: muted)[#subtitle]
  #v(8mm)
  #line(length: 100%, stroke: 0.55pt + rule)
  #v(0.8mm)
  #line(length: 36mm, stroke: 0.35pt + hair)
  #v(7mm)
  #grid(
    columns: (1fr, 1fr, 1fr),
    gutter: 6mm,
    quiet([文件\ #case-id]),
    quiet([对象\ #alias · #province #year · #batch]),
    quiet([状态\ 合成示例 · 不保证录取]),
  )
  #v(9mm)
  #text(size: 9.2pt)[#lead]
  #v(1fr)
  #grid(
    columns: (1fr, 1fr),
    gutter: 10mm,
    quiet([机构\ #studio]),
    quiet([日期 / 版本\ #doc-date · #version]),
  )
]
