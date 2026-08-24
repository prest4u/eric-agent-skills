// 青云 · 选科指导报告
// Token 来自 Chief of Staff / Document Master 第三轮皮 K 调度。
// 禁止从 D 识别册 / H 霜蓝通缘 / E 编辑纸本 / I 新闻栏换色交差。
// 客户可见只写「青云未来」。皮肤名不得印上 PDF。

#let paper = rgb("#A3C4A8")
#let fold-face = rgb("#8BA78F")
#let ink = rgb("#1C241E")
#let muted = rgb("#3D4A3F")
#let micro = rgb("#5A685C")
#let hair = rgb("#7A8B7C")

#let headline = ("Heiti SC", "Hiragino Sans GB", "PingFang SC")
#let body-font = ("Kaiti SC", "STKaiti")

#let studio-name = "青云未来"
#let fold-size = 42mm

#let page-margin = (
  top: 18mm,
  bottom: 16mm,
  left: 18mm,
  right: 16mm,
)

#let body-size = 10.5pt
#let cover-title-size = 28pt
#let section-size = 16pt

#let quiet(body) = {
  set text(font: headline, size: 7.4pt, fill: micro)
  set par(leading: 0.96em, spacing: 0.28em, justify: false, first-line-indent: 0em)
  body
}

#let lead(body) = {
  set text(font: body-font, size: 11pt, fill: ink)
  set par(leading: 1.08em, spacing: 0.56em, justify: false, first-line-indent: 0em)
  body
}

#let section-head(title, premise: none) = {
  set par(first-line-indent: 0em, justify: false)
  text(font: headline, size: section-size, weight: "bold", fill: ink)[#title]
  if premise != none {
    v(2.6mm)
    lead(premise)
  }
  v(4.8mm)
}

#let row-table(rows, cols: (26mm, 1fr)) = {
  set par(first-line-indent: 0em, justify: false)
  set text(font: headline, size: 9pt, fill: ink)
  table(
    columns: cols,
    inset: (x: 0mm, y: 2.6mm),
    stroke: (x: none, y: 0.4pt + hair),
    fill: none,
    align: (left + horizon, left + horizon),
    ..rows.map(r => (
      text(fill: muted, weight: "bold")[#r.at(0)],
      text(font: body-font, size: 10pt)[#r.at(1)],
    )).flatten(),
  )
}

#let gate-table(rows) = {
  set par(first-line-indent: 0em, justify: false)
  set text(font: headline, size: 8.2pt, fill: ink)
  table(
    columns: (28mm, 1fr, 1fr, 1fr, 34mm),
    inset: (x: 1.4mm, y: 2.5mm),
    stroke: (x: none, y: 0.4pt + hair),
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

#let fold-corner() = {
  place(top + right)[
    #box(width: fold-size, height: fold-size)[
      #place(top + left)[
        #polygon(
          fill: fold-face,
          stroke: none,
          (0mm, 0mm),
          (fold-size, 0mm),
          (fold-size, fold-size),
        )
      ]
      #place(top + left)[
        #line(
          start: (0mm, 0mm),
          end: (fold-size, fold-size),
          stroke: 0.4pt + micro,
        )
      ]
      #place(top + left, dx: 23mm, dy: 9mm)[
        #rotate(45deg, reflow: false)[
          #text(
            font: headline,
            size: 9pt,
            weight: "bold",
            fill: ink,
          )[青云]
        ]
      ]
    ]
  ]
}

#let fold-footer() = context {
  if counter(page).get().first() == 1 { none } else {
    set text(font: headline, size: 7.2pt, fill: micro)
    set par(justify: false, first-line-indent: 0em)
    [#studio-name · 非正式官方文件 · 不保证录取 · #counter(page).display("01")]
  }
}

#let fold-doc(
  title: "选科指导报告",
  author: studio-name,
  body,
) = {
  set document(title: title, author: author)
  set page(
    paper: "a4",
    fill: paper,
    margin: page-margin,
    header: none,
    footer: fold-footer(),
    foreground: fold-corner(),
  )
  set text(font: body-font, size: body-size, fill: ink, lang: "zh")
  set par(justify: false, leading: 1.05em, spacing: 0.62em, first-line-indent: 0em)
  body
}

#let cover-page(
  title: "选科指导报告",
  student: [],
  premise: [],
  facts: (),
  colophon: [],
) = {
  page(
    header: none,
    footer: none,
    foreground: fold-corner(),
    margin: (top: 26mm, bottom: 16mm, left: 18mm, right: 16mm),
  )[
    #set par(first-line-indent: 0em, justify: false)
    #set align(left)
    #text(
      font: headline,
      size: cover-title-size,
      weight: "bold",
      fill: ink,
    )[#title]
    #v(7mm)
    #text(font: headline, size: 11pt, fill: muted)[#student]
    #v(5mm)
    #lead[#premise]
    #v(8mm)
    #for item in facts {
      text(font: headline, size: 9pt, weight: "bold", fill: muted)[#item.at(0)]
      v(2.2mm)
      lead[#item.at(1)]
      v(6mm)
    }
    #v(1fr)
    #line(length: 100%, stroke: 0.4pt + hair)
    #v(2.4mm)
    #quiet[#colophon]
  ]
}
