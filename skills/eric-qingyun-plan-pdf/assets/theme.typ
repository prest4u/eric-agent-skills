// Eric Slate White PDF｜雾蓝白 · 青云文书增量层
// Token 与几何锁定雾蓝白。本文件只加案卷页眉、判断类型、免责与签字。
// 禁止第二套品牌色。禁止交通灯。禁止公章拟态。

#let paper = rgb("#F4F5F3")
#let ink = rgb("#24282A")
#let muted = rgb("#747B7E")
#let micro = rgb("#626B6F")
#let hair = rgb("#CCD2D3")
#let primary = rgb("#5D6C75")
#let secondary = rgb("#7D8990")

#let serif = ("Songti SC", "STSong")
#let sans = ("PingFang SC", "Hiragino Sans GB")
#let quote-face = ("STFangsong", "Songti SC")
#let latin = ("Avenir Next", "Helvetica Neue")

#let studio-name = "青云未来"

#let disclaimer-lines = (
  "本文件不是教育考试院或高校官方文件。",
  "本文件不构成录取、就业或薪资承诺。",
  "最终以当年官方系统、招生计划和高校招生章程为准。",
  "过期、缺失或相互冲突的数据，不得当作已核实事实。",
)

#let eyebrow(body, tone: secondary) = text(
  font: latin,
  size: 7.2pt,
  weight: "semibold",
  fill: tone,
  tracking: 0.16em,
  body,
)

#let display(body, size: 25pt) = text(
  font: serif,
  size: size,
  weight: "bold",
  fill: ink,
  tracking: -0.018em,
  body,
)

#let lead(body) = {
  set text(font: sans, size: 11.2pt, fill: ink, tracking: 0.008em)
  set par(justify: false, leading: 1em, spacing: 0.55em)
  body
}

#let label(body, tone: primary) = text(
  font: latin,
  size: 7.5pt,
  weight: "semibold",
  fill: tone,
  tracking: 0.07em,
  body,
)

#let quiet(body) = {
  set text(font: sans, size: 8.5pt, fill: micro, tracking: 0.004em)
  set par(justify: false, leading: 0.96em, spacing: 0.36em)
  body
}

#let pull(body, size: 16.5pt, tone: primary) = {
  set text(font: quote-face, size: size, fill: tone, tracking: 0.018em)
  set par(justify: false, leading: 1.06em, spacing: 0.28em)
  body
}

#let split-rule() = grid(
  columns: (2.35fr, 1fr),
  gutter: 0mm,
  line(length: 100%, stroke: 0.7pt + primary),
  line(length: 100%, stroke: 0.7pt + secondary),
)

#let rail-head(number, kicker, title, premise: none) = grid(
  columns: (16mm, 1fr),
  gutter: 10mm,
  [
    #text(font: latin, size: 9.6pt, weight: "semibold", fill: primary)[#number]
    #v(5mm)
    #line(start: (50%, 0%), end: (50%, 28mm), stroke: 0.9pt + primary)
    #line(start: (50%, 0%), end: (50%, 10mm), stroke: 0.9pt + secondary)
  ],
  [
    #eyebrow(kicker)
    #v(5.5mm)
    #display(title)
    #if premise != none [
      #v(5mm)
      #lead(premise)
    ]
  ],
)

#let side-note(title, body, tone: secondary) = block(
  width: 100%,
  inset: (left: 4mm, top: 1.5mm, bottom: 1.5mm),
  stroke: (left: 0.8pt + tone),
)[
  #label(title, tone: tone)
  #v(2.2mm)
  #quiet(body)
]

#let evidence-row(tag, body, tone: primary) = {
  grid(columns: (25mm, 1fr), gutter: 6mm, [#label(tag, tone: tone)], [#body])
  v(3.8mm)
  line(length: 100%, stroke: 0.5pt + hair)
  v(3.8mm)
}

#let numbered(n, title, body, tone: primary) = grid(
  columns: (13mm, 1fr),
  gutter: 5mm,
  [#text(font: latin, size: 14pt, weight: "medium", fill: tone)[#n]],
  [#label(title, tone: tone) #v(1.8mm) #body],
)

#let rule-row(title, body, note: none, tone: primary) = {
  grid(
    columns: (42mm, 1fr),
    gutter: 7mm,
    [#label(title, tone: tone)],
    [#body #if note != none [#v(1.2mm) #quiet(note)]],
  )
  v(3.2mm)
  line(length: 100%, stroke: 0.5pt + hair)
  v(3.2mm)
}

// 冲/稳/保：字重与线型，不上色。
#let judgment-mark(kind) = {
  let weight = if kind == "冲" { "regular" } else if kind == "稳" { "medium" } else { "bold" }
  let stroke-w = if kind == "冲" { 0.4pt } else if kind == "稳" { 0.7pt } else { 1.1pt }
  grid(
    columns: (auto, 8mm),
    gutter: 2.5mm,
    text(font: sans, size: 9pt, weight: weight, fill: ink)[#kind],
    align(horizon, line(length: 100%, stroke: stroke-w + ink)),
  )
}

#let identity-line(
  case-id: "",
  student-alias: "",
  province: "",
  year: "",
  batch: "",
  version: "V1",
  doc-date: "",
) = {
  set text(font: sans, size: 7.2pt, fill: micro, tracking: 0.02em)
  case-id + " · " + student-alias + " · " + province + str(year) + batch + " · " + version + " · " + doc-date + " · 仅供本家庭"
}

#let disclaimer-block() = {
  label([DISCLAIMER])
  v(3mm)
  for line in disclaimer-lines {
    quiet(line)
    v(1.2mm)
  }
}

#let source-row(status, body) = evidence-row(status, body, tone: if status == "FACT" { primary } else { secondary })

#let sign-grid(left-title, left-hint, right-title, right-hint) = grid(
  columns: (1fr, 1fr),
  gutter: 12mm,
  [
    #label(left-title)
    #v(14mm)
    #line(length: 100%, stroke: 0.6pt + hair)
    #v(2mm)
    #quiet(left-hint)
  ],
  [
    #label(right-title, tone: secondary)
    #v(14mm)
    #line(length: 100%, stroke: 0.6pt + hair)
    #v(2mm)
    #quiet(right-hint)
  ],
)

#let qingyun-document(
  title: "",
  subtitle: "",
  case-id: "案例合成-0000",
  student-alias: "学生化名",
  province: "天津",
  year: "2026",
  batch: "本科批",
  version: "V1",
  doc-date: "2026-08-18",
  issuer: studio-name,
  kind: "",
  keywords: ("高考志愿", "雾蓝白", "咨询案卷"),
  show-identity-header: true,
  body,
) = {
  set document(title: title, author: issuer, keywords: keywords)
  set page(
    paper: "a4",
    margin: (top: 24mm, bottom: 22mm, left: 25mm, right: 25mm),
    fill: paper,
    header: if show-identity-header {
      context {
        if counter(page).get().first() > 1 {
          set text(font: sans, size: 7pt, fill: micro, tracking: 0.02em)
          identity-line(
            case-id: case-id,
            student-alias: student-alias,
            province: province,
            year: year,
            batch: batch,
            version: version,
            doc-date: doc-date,
          )
        }
      }
    } else { none },
    footer: context {
      let n = counter(page).get().first()
      if n == 1 { none } else {
        set text(font: sans, size: 7pt, fill: micro, tracking: 0.025em)
        let folio = if n < 10 { "0" + str(n) } else { str(n) }
        grid(
          columns: (1fr, auto, 1fr),
          issuer,
          [非正式官方文件 · 不保证录取 · 以签发版为准],
          align(right)[#folio],
        )
      }
    },
  )
  set text(font: serif, size: 10pt, weight: "regular", fill: ink, lang: "zh", tracking: 0.01em)
  set par(justify: true, leading: 0.94em, spacing: 0.7em)
  set heading(numbering: none)
  body
}

#let cover-page(kicker, title, subtitle, meta-left, meta-right) = {
  set page(header: none, footer: none)
  v(15mm)
  eyebrow(kicker)
  v(22mm)
  grid(
    columns: (16mm, 1fr),
    gutter: 10mm,
    [
      #text(font: latin, size: 9pt, weight: "semibold", fill: primary)[SW]
      #v(6mm)
      #line(start: (50%, 0%), end: (50%, 62mm), stroke: 0.9pt + primary)
      #v(2mm)
      #line(start: (50%, 0%), end: (50%, 14mm), stroke: 0.9pt + secondary)
    ],
    [
      #display(title, size: 32pt)
      #v(11mm)
      #text(font: sans, size: 10.8pt, fill: muted)[#subtitle]
    ],
  )
  v(1fr)
  split-rule()
  v(5mm)
  grid(
    columns: (1fr, 1fr),
    gutter: 18mm,
    [
      #label([DOCUMENT])
      #v(3mm)
      #quiet(meta-left)
    ],
    [
      #label([STATUS], tone: secondary)
      #v(3mm)
      #quiet(meta-right)
    ],
  )
}
