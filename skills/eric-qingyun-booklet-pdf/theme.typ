// 青云 · 选科指导报告 · 线装竖册
// Wave-3 皮 L。Typst 0.14.2 拒绝 text(dir: ttb)（error: text direction must be horizontal）。
// 真竖排用 stack(dir: ttb) 单字顶到底；栏序 stack(dir: rtl) 右起左行。
// 不是 E 居中横排书页，不是 H 霜蓝右缘涂布条，不是 I 报式六栏。
// 客户可见只写「青云未来」。内部皮名不得印上 PDF。

#let paper = rgb("#D9B8C4")
#let ink = rgb("#2E1C24")
#let muted = rgb("#6B4A56")
#let micro = rgb("#8A6874")
#let hair = rgb("#B8909C")
#let bind = rgb("#C49AAB")
#let hole-ring = rgb("#6A3A4A")

#let kai-stack = ("Kaiti SC", "STKaiti", "Kaiti TC")

#let studio-name = "青云"
#let studio-full-name = "青云未来"

#let bind-w = 11mm

#let page-margin = (
  top: 14mm,
  bottom: 16mm,
  left: 12mm,
  right: 16mm,
)

#let body-size = 9pt
#let cover-title-size = 34pt
#let head-size = 14pt

#let latin-char(c) = c.match(regex("[A-Za-z0-9.,:;/_\\-–—·()\\[\\]#]")) != none

#let v-char(c, size: body-size, fill: ink) = {
  box(
    width: 1.08em,
    height: 1.05em,
    align(center + horizon, text(font: kai-stack, size: size, fill: fill, c)),
  )
}

#let v-run(s, size: body-size, fill: ink, spacing: 0.02em) = {
  let chars = str(s).clusters()
  let items = ()
  let buf = ""
  for c in chars {
    if latin-char(c) {
      buf += c
    } else {
      if buf != "" {
        items.push(rotate(90deg, reflow: true)[
          #text(font: kai-stack, size: size, fill: fill, buf)
        ])
        buf = ""
      }
      items.push(v-char(c, size: size, fill: fill))
    }
  }
  if buf != "" {
    items.push(rotate(90deg, reflow: true)[
      #text(font: kai-stack, size: size, fill: fill, buf)
    ])
  }
  stack(dir: ttb, spacing: spacing, ..items)
}

#let rtl-cols(items, gutter: 7mm) = {
  stack(dir: rtl, spacing: gutter, ..items)
}

#let v-flow(s, height: 228mm, size: body-size, fill: ink, gutter: 6.2mm) = {
  let leading = size * 1.28
  let per = calc.max(1, calc.floor(height / leading))
  let chars = str(s).clusters()
  let cols = ()
  let i = 0
  while i < chars.len() {
    let end = calc.min(i + per, chars.len())
    cols.push(v-run(chars.slice(i, end).join(), size: size, fill: fill))
    i = end
  }
  stack(dir: rtl, spacing: gutter, ..cols)
}

#let v-head(title) = v-run(title, size: head-size, fill: ink, spacing: 0.16em)

// 封面竖题单独留字间。Master：stack 叠死认不出六字；字间 ≥ 0.4–0.6em。
// 不改 v-char / v-run 默认，避免动已过的内页竖排。
#let cover-title-run(s) = {
  // em 跟着页正文 9pt，不能拿来量 34pt 题。字盒和字间都按题号算。
  let sz = cover-title-size
  let items = str(s).clusters().map(c => {
    box(
      width: sz * 1.15,
      height: sz * 1.10,
      align(center + horizon, text(font: kai-stack, size: sz, fill: ink, c)),
    )
  })
  stack(dir: ttb, spacing: sz * 0.55, ..items)
}

#let quiet(body) = {
  set text(font: kai-stack, size: 8pt, fill: micro, dir: ltr)
  set par(leading: 0.95em, spacing: 0.28em, justify: false, first-line-indent: 0em)
  body
}

#let stitch-binding() = place(right + top)[
  #block(width: bind-w, height: 297mm, fill: bind)[
    #place(left + top, dx: 0.35mm)[
      #line(length: 297mm, angle: 90deg, stroke: 0.45pt + hole-ring)
    ]
    #for dy in (48mm, 108mm, 168mm, 228mm) {
      place(center + top, dy: dy)[
        #circle(radius: 2.0mm, fill: paper, stroke: 0.7pt + hole-ring)
      ]
    }
  ]
]

#let inner-stitch() = place(right + top, dx: 4mm)[
  #for dy in (46mm, 106mm, 166mm, 226mm) {
    place(center + top, dy: dy)[
      #circle(radius: 1.15mm, fill: none, stroke: 0.55pt + hole-ring)
    ]
  }
]

#let gate-columns(rows) = {
  let one(row) = block(
    width: 30mm,
    inset: (x: 2.2mm, y: 3.2mm),
    stroke: 0.4pt + hair,
  )[
    #align(center)[
      #v-run(row.at(0), size: 12pt, fill: ink, spacing: 0.12em)
      #v(5mm)
      #v-run("工科门", size: 8pt, fill: muted)
      #v(1.6mm)
      #v-run(row.at(1), size: 10pt, fill: ink)
      #v(4.2mm)
      #v-run("医学门", size: 8pt, fill: muted)
      #v(1.6mm)
      #v-run(row.at(2), size: 10pt, fill: ink)
      #v(4.2mm)
      #v-run("经管门", size: 8pt, fill: muted)
      #v(1.6mm)
      #v-run(row.at(3), size: 10pt, fill: ink)
      #v(4.2mm)
      #v-run("放弃代价", size: 8pt, fill: muted)
      #v(1.6mm)
      #v-run(row.at(4), size: 10pt, fill: ink)
    ]
  ]
  stack(dir: rtl, spacing: 6mm, ..rows.map(one))
}

#let v-pairs(rows, gutter: 7mm) = {
  stack(dir: rtl, spacing: gutter, ..rows.map(r => {
    stack(
      dir: ttb,
      spacing: 3.2mm,
      v-run(r.at(0), size: 8pt, fill: muted),
      v-run(r.at(1), size: 10pt, fill: ink),
    )
  }))
}

#let booklet-footer() = context {
  if counter(page).get().first() == 1 { none } else {
    set text(font: kai-stack, size: 8pt, fill: micro, dir: ltr)
    [#studio-full-name · 非正式官方文件 · 不保证录取 · #counter(page).display("01")]
  }
}

#let page-frame(body) = {
  block(width: 100%, height: 246mm, breakable: false, clip: false)[
    #align(top + right, body)
  ]
}

#let booklet-doc(
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
    footer: booklet-footer(),
    background: context {
      if counter(page).get().first() == 1 { none } else { inner-stitch() }
    },
  )
  set text(font: kai-stack, size: body-size, fill: ink, lang: "zh")
  set par(justify: false, leading: 1em, spacing: 0.5em, first-line-indent: 0em)
  body
}

#let cover-page(
  title: "选科指导报告",
  student: "",
  meta: "",
  opener: "",
  colophon: "",
) = page(
  header: none,
  footer: none,
  margin: (top: 16mm, bottom: 18mm, left: 16mm, right: 18mm),
  background: stitch-binding(),
)[
  #place(right + top, dx: -20mm, dy: 24mm)[
    #cover-title-run(title)
  ]
  #place(right + top, dx: -38mm, dy: 36mm)[
    #v-run(student, size: 13pt, fill: muted, spacing: 0.12em)
  ]
  #place(right + top, dx: -52mm, dy: 36mm)[
    #v-run(meta, size: 10pt, fill: micro, spacing: 0.1em)
  ]
  #place(right + top, dx: -70mm, dy: 48mm)[
    #v-run(opener, size: 12pt, fill: ink, spacing: 0.12em)
  ]
  #place(left + bottom, dy: -4mm)[
    #text(font: kai-stack, size: 18pt, fill: ink, dir: ltr)[#studio-name]
  ]
  #place(left + bottom, dy: -16mm)[
    #text(font: kai-stack, size: 8pt, fill: micro, dir: ltr)[#colophon]
  ]
]
