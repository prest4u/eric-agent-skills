// 青云 · 选科指导报告
// 内部名：军绿指索。客户可见只写「青云未来」；封面拇指半圆「青云」为版式元素保留。禁止把内部名印上 PDF。
// 四硬差：军绿纸 #8B9170 / 全书隶书 / 右缘四枚拇指半圆索引 / 封面只露顶枚「青云」
// 不是 H 霜蓝通缘竖条，不是 F 朱印细框，不是 J 左齿孔。

#let paper = rgb("#8B9170")
#let ink = rgb("#1B1E14")
#let muted = rgb("#323628")
#let micro = rgb("#4A4F3A")
#let hair = rgb("#5C624C")
#let tab-fill = rgb("#6E7558")
#let tab-active = rgb("#4F563C")
#let tab-edge = rgb("#3A412C")
#let tab-label-fill = rgb("#EDEDD8")

#let baoli = ("Baoli SC", "Libian SC")
#let libian = ("Libian SC", "Baoli SC")

#let studio-name = "青云未来"

#let page-w = 210mm
#let page-h = 297mm
#let tab-d-quiet = 15.2mm
#let tab-d-active = 16.6mm
#let tab-centers = (36mm, 92mm, 148mm, 204mm)
#let tab-names = ("门", "表", "源", "注")

#let page-margin = (
  top: 18mm,
  bottom: 16mm,
  left: 18mm,
  right: 20mm,
)

#let body-size = 11pt
#let cover-title-size = 36pt

#let display(body, size: 22pt) = text(
  font: baoli,
  size: size,
  fill: ink,
  body,
)

#let lead(body) = {
  set text(font: libian, size: 12pt, fill: ink)
  set par(leading: 1.08em, justify: true, first-line-indent: 0em)
  body
}

#let quiet(body) = {
  set text(font: libian, size: 8.5pt, fill: micro)
  set par(leading: 1em, justify: false, first-line-indent: 0em)
  body
}

#let section-head(title, premise: none) = {
  set par(first-line-indent: 0em)
  display(title, size: 20pt)
  if premise != none {
    v(3.2mm)
    lead(premise)
  }
  v(6mm)
}

#let row-table(rows, cols: (28mm, 1fr)) = {
  set par(first-line-indent: 0em)
  set text(font: libian, size: 10pt, fill: ink)
  table(
    columns: cols,
    inset: (x: 0mm, y: 2.6mm),
    stroke: (x: none, y: 0.45pt + hair),
    fill: none,
    align: (left + horizon, left + horizon),
    ..rows.map(r => (
      text(font: baoli, size: 10pt, fill: muted)[#r.at(0)],
      [#r.at(1)],
    )).flatten(),
  )
}

#let gate-table(rows) = {
  set par(first-line-indent: 0em)
  set text(font: libian, size: 8.8pt, fill: ink)
  table(
    columns: (28mm, 1fr, 1fr, 1fr, 40mm),
    inset: (x: 1.4mm, y: 2.6mm),
    stroke: (x: none, y: 0.45pt + hair),
    fill: none,
    align: (left + horizon, center + horizon, center + horizon, center + horizon, left + horizon),
    text(font: baoli, size: 9.5pt, fill: muted)[组合],
    text(font: baoli, size: 9.5pt, fill: muted)[工科门],
    text(font: baoli, size: 9.5pt, fill: muted)[医学门],
    text(font: baoli, size: 9.5pt, fill: muted)[经管门],
    text(font: baoli, size: 9.5pt, fill: muted)[放弃代价],
    ..rows.flatten().map(c => [#c]),
  )
}

#let read-trio(items) = {
  set par(first-line-indent: 0em)
  grid(
    columns: (1fr, 1fr, 1fr),
    column-gutter: 6mm,
    ..items.map(it => [
      #text(font: baoli, size: 12pt, fill: ink)[#it.at(0)]
      #v(2.2mm)
      #set text(font: libian, size: 10pt, fill: ink)
      #set par(leading: 1.02em, justify: true, first-line-indent: 0em)
      #it.at(1)
    ]),
  )
  v(2.6mm)
  line(length: 100%, stroke: 0.45pt + hair)
}

#let disclaimer-block(lines) = {
  set par(first-line-indent: 0em)
  display([免责], size: 16pt)
  v(3.2mm)
  for line in lines {
    set text(font: libian, size: 11pt, fill: ink)
    set par(first-line-indent: 0em, leading: 1.1em, justify: true)
    line
    parbreak()
  }
}

// 字典拇指索引：半圆贴右裁口，圆心在右缘，只露左半。直径约 15mm。
// 不是 H 的通高竖条，不是 F 的细框，不是 J 的左齿孔。
#let draw-tab(center-y, label, active: false, stacked: false) = {
  let d = if active { tab-d-active } else { tab-d-quiet }
  let r = d / 2
  let fill = if active { tab-active } else { tab-fill }
  place(top + right, dy: center-y - r)[
    #box(width: r, height: d, clip: true)[
      #place(top + left)[
        #circle(width: d, fill: fill, stroke: 0.5pt + tab-edge)
      ]
      #align(center + horizon)[
        #if stacked {
          set par(leading: 0.78em, spacing: 0em, first-line-indent: 0em)
          text(font: baoli, size: 7.4pt, fill: tab-label-fill)[青]
          linebreak()
          text(font: baoli, size: 7.4pt, fill: tab-label-fill)[云]
        } else {
          text(font: baoli, size: 9pt, fill: tab-label-fill)[#label]
        }
      ]
    ]
  ]
}

#let thumb-index() = context {
  let n = counter(page).get().first()
  if n == 1 {
    draw-tab(tab-centers.at(0), [青云], active: true, stacked: true)
  } else {
    let active = if n == 2 { 0 } else if n == 3 { 1 } else { 2 }
    for i in range(4) {
      draw-tab(
        tab-centers.at(i),
        tab-names.at(i),
        active: i == active,
        stacked: false,
      )
    }
  }
}

#let inner-footer() = context {
  if counter(page).get().first() == 1 { none } else {
    set text(font: libian, size: 7.5pt, fill: micro)
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
  #text(font: baoli, size: 14pt, fill: ink)[#studio-name]
  #v(14mm)
  #align(left)[
    #display(title, size: cover-title-size)
  ]
  #v(9mm)
  #text(font: libian, size: 12.5pt, fill: muted)[#student]
  #v(9mm)
  #block(width: 128mm)[
    #lead(premise)
  ]
  #v(1fr)
  #line(length: 28mm, stroke: 0.45pt + hair)
  #v(3.2mm)
  #quiet(colophon)
]

#let thumb-doc(
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
    background: thumb-index(),
    footer: inner-footer(),
  )
  set text(font: libian, size: body-size, fill: ink, lang: "zh")
  set par(justify: true, leading: 1.06em, spacing: 0.82em, first-line-indent: 0em)
  body
}

#let qingyun-doc = thumb-doc
