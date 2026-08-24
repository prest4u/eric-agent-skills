// Polished low-saturation Typst helpers for Eric teaching PDFs.
// Import with:
// 1. Copy this file into the working output directory.
// 2. Import it locally:
// #import "soft-signal-template.typ": *

#let soft-paper = rgb("#fffdf8")
#let soft-ink = rgb("#211b17")
#let soft-muted = rgb("#71675f")
#let soft-clay = rgb("#bd623f")
#let soft-clay-pale = rgb("#f8e9df")
#let soft-line = rgb("#d9c8ba")
#let soft-card = rgb("#fff8f0")
#let soft-stripe = rgb("#fff6ed")
#let soft-signal = rgb("#7568a3")
#let soft-signal-pale = rgb("#f1edf8")
#let soft-warning-pale = rgb("#fff1c9")
#let soft-warning-ink = rgb("#7a4c12")
#let soft-hair = 0.36pt + soft-line
#let soft-body-font = ("PingFang SC", "Hiragino Sans GB")
#let soft-title-font = ("Zhuque Fangsong (technical preview)", "Noto Serif SC", "Songti SC", "STSong", "PingFang SC")
#let soft-heading-font = soft-title-font
#let soft-latin-title-font = ("Libertinus Serif", "New Computer Modern")

#let soft-plain-title-text(title) = {
  if type(title) == str {
    title
  } else if type(title) == content {
    repr(title)
  } else {
    str(title)
  }
}

#let soft-title-is-latin(title) = {
  let s = soft-plain-title-text(title)
  let has-cjk = s.contains(regex("[\u{4e00}-\u{9fff}]"))
  let has-latin = s.contains(regex("[A-Za-z]"))
  has-latin and not has-cjk
}

#let soft-cover-title-face(title, latin: auto) = {
  let use-latin = if latin == true {
    true
  } else if latin == false {
    false
  } else {
    soft-title-is-latin(title)
  }
  if use-latin { soft-latin-title-font } else { soft-title-font }
}

#let soft-cover-display-title(title, latin: auto, size: 28pt, weight: 520) = {
  text(
    font: soft-cover-title-face(title, latin: latin),
    size: size,
    weight: weight,
    fill: soft-ink,
  )[#title]
}

#let soft-checkbox = rect(width: 8pt, height: 8pt, stroke: 0.45pt + soft-muted, inset: 0pt)
#let soft-blank(width: 3.6em) = box(line(length: width, stroke: 0.45pt + soft-muted))
#let soft-inline-write-blank(height: 12pt, line-drop: 9.2pt) = box(width: 100%, height: height)[
  #v(line-drop)
  #line(length: 100%, stroke: 0.42pt + soft-line)
]
#let soft-table-write-cell(height: 15pt, line-drop: 13.6pt) = table.cell(align: left + bottom)[
  #box(width: 100%, height: height)[
    #v(line-drop)
    #line(length: 100%, stroke: 0.42pt + soft-line)
  ]
]

#let soft-cover-field(label) = grid(
  columns: (auto, 1fr),
  gutter: 6pt,
  align: top,
  [#text(size: 8.6pt, fill: soft-muted)[#label]],
  [
    #box(width: 100%, height: 11.5pt)[
      #v(9.2pt)
      #line(length: 100%, stroke: 0.42pt + soft-line)
    ]
  ],
)

#let soft-cover-identity-fields() = grid(
  columns: (1fr,),
  row-gutter: 3pt,
  soft-cover-field([姓名：]),
  soft-cover-field([日期：]),
)

#let soft-setup(body, title: none, meta: none, body-size: 10.7pt, leading: 0.88em) = {
  assert(
    body-size >= 10pt,
    message: "soft-setup body-size is below the 10pt print floor; shorten copy or rebalance task groups instead of shrinking type",
  )
  set page(
    paper: "a4",
    fill: soft-paper,
    margin: (left: 2.1cm, right: 2.1cm, top: 2.05cm, bottom: 1.8cm),
    header: context [
      #block(width: 100%)[
        #set text(size: 8.4pt, fill: soft-muted)
        #grid(
          columns: (1fr, auto),
          align: horizon,
          [#if title != none { title }],
          [
            #if meta != none [
              #meta
              #h(0.9em)
            ]
            #counter(page).display("1")
          ],
        )
        #v(3pt)
        #line(length: 100%, stroke: 0.42pt + soft-line)
      ]
    ],
    footer: none,
    numbering: none,
  )
  set text(font: soft-body-font, size: body-size, lang: "zh", fill: soft-ink)
  set par(leading: leading, first-line-indent: 0pt, justify: false)
  body
}

#let soft-cover-title(prefix, rest, latin: auto) = {
  let use-latin = if latin == true {
    true
  } else if latin == false {
    false
  } else {
    soft-title-is-latin(prefix) and soft-title-is-latin(rest)
  }
  let face = if use-latin { soft-latin-title-font } else { soft-title-font }
  grid(
    columns: (auto, 1fr),
    gutter: 4pt,
    align: horizon,
    [#text(font: face, size: 25.2pt, weight: 520, fill: soft-ink)[#prefix]],
    [#text(font: face, size: 28pt, weight: 520, fill: soft-ink)[#rest]],
  )
}

#let soft-cover-brand(footer) = place(bottom + right)[
  #text(size: 7.8pt, fill: soft-muted)[#footer]
]

#let soft-cover(title: none, subtitle: none, meta: none, code: none, footer: none, title-prefix: none, title-rest: none, latin: auto) = [
  #set page(
    paper: "a4",
    fill: soft-paper,
    margin: (left: 2.1cm, right: 2.1cm, top: 1.85cm, bottom: 1.8cm),
    header: none,
    footer: none,
    numbering: none,
  )
  #v(10%)
  #grid(
    columns: (1fr, 1fr, 1fr, 1fr),
    gutter: 5pt,
    [#rect(height: 8pt, fill: soft-clay-pale, stroke: none)],
    [#rect(height: 8pt, fill: soft-signal-pale, stroke: none)],
    [#rect(height: 8pt, fill: soft-warning-pale, stroke: none)],
    [#rect(height: 8pt, fill: soft-card, stroke: none)],
  )
  #v(19%)
  #if code != none {
    text(size: 7.8pt, weight: 650, fill: soft-clay)[#code]
    v(12pt)
  }
  #if title-prefix != none and title-rest != none {
    soft-cover-title(title-prefix, title-rest, latin: latin)
  } else {
    soft-cover-display-title(title, latin: latin, size: 28pt, weight: 520)
  }
  #v(7pt)
  #text(size: 13pt, weight: 540, fill: soft-clay)[#subtitle]
  #v(18pt)
  #box(width: 48%, inset: (x: 9pt, y: 6pt), fill: soft-clay-pale, stroke: soft-hair)[
    #text(size: 8.6pt, fill: soft-muted)[#meta]
  ]
  #if footer != none {
    soft-cover-brand(footer)
  }
]

#let soft-body(title: none, meta: none, body) = [
  #pagebreak()
  #counter(page).update(1)
  #set page(
    paper: "a4",
    fill: soft-paper,
    margin: (left: 2.1cm, right: 2.1cm, top: 2.05cm, bottom: 1.8cm),
    header: context [
      #block(width: 100%)[
        #set text(size: 8.4pt, fill: soft-muted)
        #grid(
          columns: (1fr, auto),
          align: horizon,
          [#if title != none { title }],
          [
            #if meta != none [
              #meta
              #h(0.9em)
            ]
            #counter(page).display("1")
          ],
        )
        #v(3pt)
        #line(length: 100%, stroke: 0.42pt + soft-line)
      ]
    ],
    footer: none,
    numbering: none,
  )
  #set text(font: soft-body-font, size: 10.7pt, lang: "zh", fill: soft-ink)
  #set par(leading: 0.88em, first-line-indent: 0pt, justify: false)
  #body
]

#let soft-heading-rules() = {
  show heading.where(level: 1): it => [
    v(18pt)
    text(font: soft-heading-font, size: 16.2pt, weight: 580, fill: soft-ink)[#it.body]
    v(4pt)
  ]
  show heading.where(level: 2): it => [
    v(20pt)
    text(size: 12.4pt, weight: 620, fill: soft-ink)[#it.body]
    v(8pt)
  ]
  show heading.where(level: 3): it => [
    v(9pt)
    text(size: 10.3pt, weight: 620, fill: soft-ink)[#it.body]
    v(2pt)
  ]
  show table: it => {
    set text(size: 9pt)
    set par(leading: 0.86em)
    it
  }
}

#let soft-meta(body) = text(size: 8.3pt, fill: soft-muted)[#body]

#let soft-subtitle(title, meta: none) = block(breakable: false, above: 18pt, below: 9pt)[
  #text(size: 12.4pt, weight: 640, fill: soft-ink)[#title]
  #if meta != none {
    v(4pt)
    text(size: 8.5pt, fill: soft-muted)[#meta]
  }
]

#let soft-passage-title(label, title, meta: none) = block(breakable: false, above: 22pt, below: 11pt)[
  #grid(
    columns: (auto, 1fr),
    gutter: 8pt,
    align: horizon,
    [#text(font: soft-heading-font, size: 13.6pt, weight: 650, fill: soft-clay)[#label]],
    [#text(font: soft-heading-font, size: 13.6pt, weight: 610, fill: soft-ink)[#title]],
  )
  #if meta != none {
    v(5pt)
    text(size: 8.6pt, fill: soft-muted)[#meta]
  }
]

#let soft-section(num: none, title: none) = block(
  width: 100%,
  breakable: false,
  sticky: true,
  above: 14pt,
  below: 6pt,
)[
  #grid(
    columns: (40pt, 1fr),
    gutter: 7pt,
    align: top,
    [#text(font: soft-heading-font, size: 13.4pt, weight: 620, fill: soft-clay)[#num]],
    [
      #text(font: soft-heading-font, size: 14pt, weight: 580, fill: soft-ink)[#title]
      #v(2pt)
      #line(length: 100%, stroke: soft-hair)
    ],
  )
]

#let soft-note(title, body) = box(
  width: 100%,
  inset: (x: 8pt, y: 6pt),
  fill: soft-clay-pale,
  stroke: soft-hair,
)[
  #text(size: 8.4pt, weight: 650, fill: soft-clay)[#title]
  #v(3pt)
  #text(size: 9.2pt, fill: soft-ink)[#body]
]

#let soft-signal-note(title, body) = box(
  width: 100%,
  inset: (x: 8pt, y: 6pt),
  fill: soft-signal-pale,
  stroke: 0.32pt + soft-signal,
)[
  #text(size: 8.4pt, weight: 650, fill: soft-signal)[#title]
  #v(3pt)
  #text(size: 9.2pt, fill: soft-ink)[#body]
]

#let soft-warning-note(title, body) = box(
  width: 100%,
  inset: (x: 8pt, y: 6pt),
  fill: soft-warning-pale,
  stroke: 0.32pt + soft-warning-ink,
)[
  #text(size: 8.4pt, weight: 650, fill: soft-warning-ink)[#title]
  #v(3pt)
  #text(size: 9.2pt, fill: soft-ink)[#body]
]

#let soft-table(columns, text-size: 9pt, leading: 0.86em, row-y: 6.4pt, row-x: 7pt, ..cells) = {
  assert(
    text-size >= 8.5pt,
    message: "soft-table text-size is below the 8.5pt print floor; split or rebalance the table instead of shrinking type",
  )
  set text(size: text-size)
  set par(leading: leading)
  table(
    columns: columns,
    stroke: (x, y) => if y == 0 { (top: 0.56pt + soft-line, bottom: 0.56pt + soft-line) } else { (bottom: 0.26pt + soft-line) },
    inset: (x: row-x, y: row-y),
    align: left + top,
    fill: (x, y) => if y == 0 { soft-clay-pale } else { if calc.rem(y, 2) == 0 { soft-stripe } else { none } },
    ..cells
  )
}

#let soft-practice-table(columns, ..cells) = soft-table(
  columns,
  text-size: 9.15pt,
  leading: 0.94em,
  row-y: 7.1pt,
  row-x: 7.4pt,
  ..cells
)

#let soft-word-family-table(..cells) = soft-practice-table(
  (1fr, 1.15fr),
  ..cells
)

#let soft-writable-table(columns, ..cells) = soft-table(
  columns,
  text-size: 9.15pt,
  leading: 0.96em,
  row-y: 9.6pt,
  row-x: 7.4pt,
  ..cells
)

#let soft-answer-line(label, height: none, after: 13pt, line-drop: 6.2pt, label-width: auto, gutter: 7pt, label-size: 8.9pt) = [
  #grid(
    columns: (label-width, 1fr),
    gutter: gutter,
    align: top,
    [#text(size: label-size, fill: soft-muted)[#label]],
    [
      #v(line-drop)
      #line(length: 100%, stroke: 0.42pt + soft-line)
    ],
  )
  #v(if height == none { after } else { height })
]

#let soft-exit-write-line(label) = grid(
  columns: (auto, 1fr),
  gutter: 7pt,
  align: top,
  [#text(size: 9.15pt, fill: soft-ink)[#label]],
  [
    #box(width: 100%, height: 18pt)[
      #v(14pt)
      #line(length: 100%, stroke: 0.42pt + soft-line)
    ]
  ],
)

#let soft-exit-write-lines(first, second) = block(width: 100%)[
  #soft-exit-write-line(first)
  #v(5pt)
  #soft-exit-write-line(second)
]

#let soft-prompt-line(body, after: 10pt, body-size: 9.25pt, fill: soft-ink) = [
  #text(size: body-size, fill: fill)[#body]
  #v(after)
]

#let soft-labeled-write-line(label, after: 13pt, line-drop: 7.2pt, label-width: auto, gutter: 3.5pt, label-size: 9.1pt) = [
  #soft-answer-line(
    label,
    after: after,
    line-drop: line-drop,
    label-width: label-width,
    gutter: gutter,
    label-size: label-size,
  )
]

#let soft-reason-line(label: [理由：], after: 15pt) = [
  #soft-labeled-write-line(
    label,
    after: after,
  )
]

#let soft-output-task(prompt, after: 12pt, prompt-after: 7pt, answer-after: 8pt, answer-label: [合并句：], reason-label: [理由：]) = block(breakable: false)[
  #soft-prompt-line(prompt, after: prompt-after)
  #soft-labeled-write-line(answer-label, after: answer-after)
  #soft-reason-line(label: reason-label, after: after)
]

#let soft-writing-area(label: none, lines: 5, preset: none, label-gap: 5.5pt, gap: 14pt, line-drop: none) = [
  // Named writing-length presets keep task types consistent across documents.
  #let preset-lines = ("short": 1, "rewrite": 2, "translate": 2, "composition": 8)
  #let effective-lines = if preset != none {
    assert(
      preset in preset-lines,
      message: "unknown soft-writing-area preset; use one of: short, rewrite, translate, composition",
    )
    preset-lines.at(preset)
  } else { lines }
  #let effective-line-drop = if line-drop == none { gap - 1.6pt } else { line-drop }
  #if label != none {
    text(size: 8.8pt, fill: soft-muted)[#label]
    v(label-gap)
  }
  #for i in range(effective-lines) {
    box(width: 100%, height: gap)[
      #v(effective-line-drop)
      #line(length: 100%, stroke: 0.42pt + soft-line)
    ]
  }
]

// Public MCQ contract: this is the only student-facing choice surface.
// Pass exactly four choices. Renders a 2x2 A-D four-box grid (soft-choice).
// Never write inline dotted A/B/C runs or a 3-option line; invent a fourth
// distractor or recast the task. Local wrappers (e.g. mcq) must call this helper.
#let soft-choice(label: none, body: none, correct: false) = box(
  width: 100%,
  inset: (x: 7pt, y: 5.2pt),
  fill: if correct { soft-signal-pale } else { soft-card },
  stroke: if correct { 0.45pt + soft-signal } else { soft-hair },
)[
  #grid(
    columns: (10pt, 18pt, 1fr),
    gutter: 4pt,
    align: top,
    [#if correct { circle(radius: 4pt, fill: soft-signal, stroke: none) } else { soft-checkbox }],
    [#text(size: 9.1pt, weight: 650, fill: soft-ink)[#label]],
    [#text(size: 9.1pt, fill: soft-ink)[#body]],
  )
]

#let soft-question(
  stem: none,
  choices: (),
  evidence-label: [证据：],
  correct-index: none,
  teacher-note: none,
) = block(width: 100%, breakable: false, above: 10pt)[
  #text(size: 9.55pt, weight: 560, fill: soft-ink)[#stem]
  #v(5pt)
  #grid(
    columns: (1fr, 1fr),
    column-gutter: 7pt,
    row-gutter: 5pt,
    soft-choice(label: [A.], body: choices.at(0), correct: correct-index == 0),
    soft-choice(label: [B.], body: choices.at(1), correct: correct-index == 1),
    soft-choice(label: [C.], body: choices.at(2), correct: correct-index == 2),
    soft-choice(label: [D.], body: choices.at(3), correct: correct-index == 3),
  )
  #if evidence-label != none {
    v(5pt)
    soft-answer-line(evidence-label, after: 2pt, line-drop: 6.2pt)
  }
  #if teacher-note != none {
    v(4pt)
    soft-signal-note([TEACHER], teacher-note)
  }
]

// Keep the marker, heading, prompt, and usable writing surface together.
#let soft-reflection(
  title: none,
  prompt: none,
  lines: 4,
  marker: [REFLECT],
) = block(width: 100%, breakable: false, above: 16pt)[
  #grid(
    columns: (52pt, 1fr),
    gutter: 8pt,
    align: top,
    [#text(size: 8.1pt, weight: 680, fill: soft-clay)[#marker]],
    [#text(font: soft-heading-font, size: 12.8pt, weight: 620, fill: soft-ink)[#title]],
  )
  #v(6pt)
  #text(size: 9.25pt, fill: soft-ink)[#prompt]
  #v(5pt)
  #soft-writing-area(lines: lines, gap: 14pt)
]

// Keep a written-response prompt and its writing lines in one unbreakable
// block so the answer surface can never separate from the task. Use this for
// rewrite, translate, and correction items instead of joining a bare prompt
// and bare writing lines with manual spacing.
#let soft-task(prompt, lines: 2, preset: none, after: 12pt, prompt-after: 6pt) = block(
  width: 100%,
  breakable: false,
  above: 10pt,
)[
  #soft-prompt-line(prompt, after: prompt-after)
  #soft-writing-area(lines: lines, preset: preset)
  #v(after)
]

// A reading or cloze passage that stays attached to the first task that
// follows it. Breakable so long passages may flow across pages; sticky keeps
// the passage from sitting alone at a page foot while its questions begin on
// the next page. When a short passage and its whole task group fit one page,
// prefer soft-exercise-group.
#let soft-passage(body, label: none, title: none, meta: none, above: 6pt, below: 8pt) = block(
  width: 100%,
  sticky: true,
  above: above,
  below: below,
)[
  #if label != none and title != none {
    soft-passage-title(label, title, meta: meta)
  }
  #body
]

// Keep a short passage and its entire task group on one page. Use for cloze
// or short-reading sets that comfortably fit within one page; use
// soft-passage instead when the passage alone may approach a full page.
#let soft-exercise-group(body) = block(width: 100%, breakable: false, above: 8pt)[
  #body
]
