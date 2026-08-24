// 青云 · 家长说明册
// 终审淘汰 B 苔绿象牙之后的替代底盘，不是 A 的换色。
// 四硬差：暖黄书纸 / 楷题仿宋 / 左 38mm 边注 / 题签+题辞封面
// 禁止栏轨函数、拉丁底栏、结构色。客户可见只写「青云未来」；封面题签「青云」为版式元素保留。

#let paper = rgb("#EFE4D0")
#let ink = rgb("#3A3228")
#let muted = rgb("#6E6356")
#let micro = rgb("#8A7F70")
#let hair = rgb("#C9B89A")

#let kai = ("Kaiti SC", "STKaiti", "Kaiti TC")
#let fang = ("STFangsong", "Songti SC", "STSong")

#let studio-name = "青云"
#let studio-full-name = "青云未来"
#let skin-label = "家长说明册"
#let sidenote-width = 38mm
#let sidenote-gutter = 6.5mm

#let page-margin = (
  top: 22mm,
  bottom: 20mm,
  left: 15mm,
  right: 17mm,
)

#let body-size = 10.5pt
#let note-size = 8.5pt
#let header-size = 7.5pt
#let cover-title-size = 34pt

#let quiet(body) = {
  set text(font: fang, size: 9pt, fill: micro)
  set par(leading: 1em, justify: false, first-line-indent: 0em)
  body
}

#let labeled-rows(rows, row-gutter: 4.2mm) = {
  set par(first-line-indent: 0em)
  grid(
    columns: (22mm, 1fr),
    row-gutter: row-gutter,
    column-gutter: 5mm,
    ..rows.map(row => (
      text(font: kai, fill: muted, size: 10pt)[#row.at(0)],
      text(font: fang)[#row.at(1)],
    )).flatten(),
  )
}

#let gate-table(rows) = {
  set par(first-line-indent: 0em)
  set text(font: fang, size: 8.5pt)
  table(
    columns: (20mm, 1fr, 1fr, 1fr, 34mm),
    inset: (x: 0mm, y: 3mm),
    stroke: (x: none, y: 0.4pt + hair),
    align: (left, center, center, center, left),
    text(font: kai, weight: "regular")[组合],
    text(font: kai, weight: "regular")[工科门],
    text(font: kai, weight: "regular")[医学门],
    text(font: kai, weight: "regular")[经管门],
    text(font: kai, weight: "regular")[放弃代价],
    ..rows.flatten().map(c => [#c]),
  )
}

#let disclaimer-prose(lines) = {
  for sentence in lines {
    set par(first-line-indent: 2em)
    sentence
    parbreak()
  }
}

#let spread(note, body) = {
  set par(first-line-indent: 0em)
  grid(
    columns: (sidenote-width, 1fr),
    column-gutter: sidenote-gutter,
    {
      set text(font: kai, size: note-size, fill: muted)
      set par(leading: 0.95em, justify: false, first-line-indent: 0em, spacing: 0.7em)
      note
    },
    {
      set text(font: fang, size: body-size, fill: ink)
      set par(justify: true, leading: 1.08em, spacing: 0.9em, first-line-indent: 2em)
      body
    },
  )
}

#let parent-footer() = context {
  if counter(page).get().first() == 1 { none } else {
    set text(font: kai, size: header-size, fill: micro)
    grid(
      columns: (sidenote-width, 1fr),
      column-gutter: sidenote-gutter,
      {
        skin-label
        h(2.5mm)
        counter(page).display()
      },
      [#studio-full-name · 非正式官方文件 · 不保证录取],
    )
  }
}

#let parent-doc(
  title: "给家长的说明",
  author: studio-full-name,
  body,
) = {
  set document(title: title, author: author)
  set page(
    paper: "a4",
    fill: paper,
    margin: page-margin,
    header: none,
    footer: parent-footer(),
  )
  set text(font: fang, size: body-size, fill: ink, lang: "zh")
  set par(justify: true, leading: 1.08em, spacing: 0.9em, first-line-indent: 2em)
  body
}

#let title-slip(chars: "青云") = {
  block(
    width: 14mm,
    inset: 1.1mm,
    stroke: 0.45pt + ink,
  )[
    #block(
      width: 100%,
      inset: (x: 1.4mm, y: 10mm),
      stroke: 0.3pt + hair,
    )[
      #align(center)[
        #set text(font: kai, size: 16pt, fill: ink)
        #set par(leading: 0.9em, first-line-indent: 0em)
        #chars.clusters().join(v(2.2mm))
      ]
    ]
  ]
}

#let cover-page(
  title: "给家长的说明",
  slip: "青云",
  meta: "",
  colophon: [],
) = {
  page(header: none, footer: none, fill: paper, margin: page-margin)[
    #set par(first-line-indent: 0em)
    #v(10mm)
    #align(right)[
      #pad(right: 10mm)[
        #title-slip(chars: slip)
      ]
    ]
    #v(1fr)
    #align(center)[
      #text(font: kai, size: cover-title-size, fill: ink)[#title]
      #v(12mm)
      #text(font: kai, size: 11pt, fill: muted)[#meta]
    ]
    #v(1fr)
    #align(center)[
      #set text(font: fang, size: 9pt, fill: micro)
      #colophon
    ]
    #v(12mm)
  ]
}
