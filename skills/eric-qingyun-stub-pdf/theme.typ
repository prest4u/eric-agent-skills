// 青云 · 选科指导报告
// 内部名：砖红票根。客户可见只写「青云未来」；票根「青云」为版式元素保留。禁止把内部名印上 PDF。
// 底盘 O：砖红纸 #D08A72 / 黑体题+行楷文 / 底 22mm 票根 / 齿孔撕线
// 整页是一张票，不是活页、不是浅青识别册、不是新闻栏、不是朱印砂卷。
// 禁止左齿孔、顶通栏、报头、六栏、6mm 细框、朱印。

#let paper = rgb("#D08A72")
#let ink = rgb("#111111")
#let muted = rgb("#3A2218")
#let micro = rgb("#4E2E24")
#let hair = rgb("#5C382C")
#let hole-fill = rgb("#E8B09E")
#let hole-stroke = rgb("#3A1E18")

#let hei = ("Heiti SC", "STHeiti", "Hiragino Sans GB")
#let xing = ("Xingkai SC", "Xingkai TC")

#let studio-name = "青云"
#let studio-full-name = "青云未来"

#let page-w = 210mm
#let page-h = 297mm
#let stub-h = 22mm
#let hole-diameter = 1.44mm
#let perf-count = 44
#let perf-inset = 8mm

#let page-margin = (
  top: 18mm,
  bottom: 28mm,
  left: 16mm,
  right: 16mm,
)

#let body-size = 11pt
#let cover-title-size = 36pt
#let section-size = 18pt

#let quiet(body) = {
  set text(font: hei, size: 8.2pt, fill: micro)
  set par(leading: 1em, justify: false, first-line-indent: 0em)
  body
}

#let lead(body) = {
  set text(font: xing, size: 12pt, fill: ink)
  set par(leading: 1.16em, justify: true, first-line-indent: 0em)
  body
}

#let section-head(title, premise: none) = {
  set par(first-line-indent: 0em)
  text(font: hei, size: section-size, weight: "bold", fill: ink)[#title]
  if premise != none {
    v(3.2mm)
    lead(premise)
  }
  v(5.5mm)
}

#let row-table(rows, cols: (28mm, 1fr)) = {
  set par(first-line-indent: 0em)
  set text(font: xing, size: 10pt, fill: ink)
  table(
    columns: cols,
    inset: (x: 0mm, y: 2.6mm),
    stroke: (x: none, y: 0.4pt + hair),
    fill: none,
    align: (left + horizon, left + horizon),
    ..rows.map(r => (
      text(font: hei, size: 8.6pt, weight: "bold", fill: muted)[#r.at(0)],
      [#r.at(1)],
    )).flatten(),
  )
}

#let gate-table(rows) = {
  set par(first-line-indent: 0em)
  set text(font: xing, size: 9pt, fill: ink)
  table(
    columns: (28mm, 1fr, 1fr, 1fr, 34mm),
    inset: (x: 1.2mm, y: 2.5mm),
    stroke: (x: none, y: 0.4pt + hair),
    fill: none,
    align: (left + horizon, center + horizon, center + horizon, center + horizon, left + horizon),
    text(font: hei, size: 8.4pt, weight: "bold")[组合],
    text(font: hei, size: 8.4pt, weight: "bold")[工科门],
    text(font: hei, size: 8.4pt, weight: "bold")[医学门],
    text(font: hei, size: 8.4pt, weight: "bold")[经管门],
    text(font: hei, size: 8.4pt, weight: "bold")[放弃代价],
    ..rows.flatten().map(c => [#c]),
  )
}

#let ticket-chrome(case-no: "") = {
  let y-perf = page-h - stub-h
  let r = hole-diameter / 2
  let usable = page-w - 2 * perf-inset
  for i in range(perf-count) {
    let x = perf-inset + usable * (i / (perf-count - 1))
    place(
      dx: x - r,
      dy: y-perf - r,
      circle(
        radius: r,
        fill: hole-fill,
        stroke: 0.4pt + hole-stroke,
      ),
    )
  }
  context {
    let pno = counter(page).display("01")
    place(
      bottom + left,
      block(
        width: page-w,
        height: stub-h,
        inset: (x: 16mm, top: 6.2mm, bottom: 4.5mm),
      )[
        #set par(first-line-indent: 0em, leading: 0.88em, spacing: 0em)
        #grid(
          columns: (1fr, auto, 1fr),
          align(left + horizon,
            text(font: hei, size: 15pt, weight: "bold", fill: ink)[#studio-name]
          ),
          align(center + horizon,
            text(font: hei, size: 8pt, fill: muted)[#case-no]
          ),
          align(right + horizon,
            text(font: hei, size: 12pt, weight: "bold", fill: ink)[#pno]
          ),
        )
        #v(2mm)
        #align(center,
          text(font: hei, size: 7pt, fill: micro)[非正式官方文件 · 不保证录取]
        )
      ],
    )
  }
}

#let stub-doc(
  title: "选科指导报告",
  author: studio-full-name,
  case-id: "",
  body,
) = {
  set document(title: title, author: author)
  set page(
    paper: "a4",
    fill: paper,
    margin: page-margin,
    header: none,
    footer: none,
    background: ticket-chrome(case-no: case-id),
  )
  set text(font: xing, size: body-size, fill: ink, lang: "zh")
  set par(justify: true, leading: 1.14em, spacing: 0.78em, first-line-indent: 0em)
  body
}

#let cover-page(
  title: "选科指导报告",
  case-id: "",
  meta: "",
  premise: [],
  colophon: [],
) = {
  page(
    header: none,
    footer: none,
    fill: paper,
    margin: page-margin,
    background: ticket-chrome(case-no: case-id),
  )[
    #set par(first-line-indent: 0em, justify: false)
    #v(14mm)
    #text(font: hei, size: cover-title-size, weight: "bold", fill: ink)[#title]
    #v(9mm)
    #text(font: xing, size: 14pt, fill: ink)[#meta]
    #v(7mm)
    #lead(premise)
    #v(1fr)
    #set text(font: hei, size: 8.4pt, fill: micro)
    #colophon
    #v(3mm)
  ]
}
