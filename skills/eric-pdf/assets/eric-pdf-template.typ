// Hermes classroom Typst template
// Use for A4 teaching PDFs: handouts, lesson notes, practice sheets, manuals.

#let c-paper = rgb("#fffdf8")
#let c-text = rgb("#221a16")
#let c-muted = rgb("#74665d")
#let c-amber = rgb("#b85c38")
#let c-border = rgb("#dcc9ba")
#let c-card = rgb("#fffaf3")
#let c-header-bg = rgb("#f7eadf")
#let c-accent-bg = rgb("#fff1e6")
#let c-accent-border = rgb("#e4a070")
#let c-note-bg = rgb("#fff8ea")
#let c-note-border = rgb("#ead7bf")
#let c-grid = rgb("#efe4da")

#let blank = box(line(length: 3.5em, stroke: 0.6pt + c-muted))
#let checkbox = rect(width: 8pt, height: 8pt, stroke: 0.5pt + c-muted, inset: 0pt)

#let setup-hermes-page(title: none) = {
  set page(
    paper: "a4",
    fill: c-paper,
    margin: (left: 2.2cm, right: 2.2cm, top: 2cm, bottom: 2cm),
    footer: none,
    header: context {
      if title != none {
        set text(size: 8pt, fill: c-muted)
        align(right, [
          #title
          #h(1em)
          #counter(page).display("1")
        ])
      }
    },
    numbering: none,
  )
  set text(font: ("PingFang SC", "Hiragino Sans GB"), size: 11pt, lang: "zh", fill: c-text)
  set par(leading: 0.9em, first-line-indent: 0pt)
}

// Start body content after a cover. Use directly only when writing
// top-level Typst; for reusable templates prefer eric-body(...)[...].
#let eric-body-start(title: none) = {
  pagebreak()
  counter(page).update(1)
  set page(
    fill: c-paper,
    header: context {
      if title != none {
        set text(size: 8pt, fill: c-muted)
        align(right, [
          #title
          #h(1em)
          #counter(page).display("1")
        ])
      }
    },
    footer: none,
    numbering: none,
  )
}

// Wrap all body pages after a cover. This is the safest way to keep the
// cover unnumbered and make the first body page display page 1.
#let eric-body(title: none, body) = [
  #pagebreak()
  #counter(page).update(1)
  #set page(
    fill: c-paper,
    header: context {
      if title != none {
        set text(size: 8pt, fill: c-muted)
        align(right, [
          #title
          #h(1em)
          #counter(page).display("1")
        ])
      }
    },
    footer: none,
    numbering: none,
  )
  #body
]

#show heading.where(level: 1): it => [
  #v(20pt)
  #text(size: 15pt, weight: 700, fill: c-text)[#it.body]
  #v(3pt)
]
#show heading.where(level: 2): it => [
  #v(16pt)
  #text(size: 13pt, weight: 600, fill: c-text)[#it.body]
  #v(3pt)
]
#show heading.where(level: 3): it => [
  #v(10pt)
  #text(size: 11pt, weight: 600, fill: c-text)[#it.body]
  #v(2pt)
]

#let hermes-cover(title, subtitle, meta) = [
  #align(center)[
    #v(22%)
    #text(size: 22pt, weight: 700, fill: c-text)[#title]
    #v(6pt)
    #text(size: 14pt, weight: 600, fill: c-amber)[#subtitle]
    #v(10pt)
    #line(length: 20%, stroke: 0.8pt + c-amber)

    #v(25%)
    #text(size: 9pt, fill: c-muted)[#meta]
  ]
]

#let hermes-table(columns, body) = table(
  columns: columns,
  stroke: (x, y) => if y == 0 { (top: 0.75pt + c-border, bottom: 0.75pt + c-border) } else { (top: 0.35pt + c-border, bottom: 0.35pt + c-border) },
  inset: (x: 6pt, y: 4pt),
  align: left + top,
  fill: (col, row) => if row == 0 { c-header-bg } else { if calc.rem(row, 2) == 0 { c-card } else { none } },
  ..body
)

// Exam-like cloze option row. Use for 完形填空 instead of bordered tables.
#let eric-choice-row(no, a, b, c, d) = [
  #grid(
    columns: (2.4em, 1fr, 1fr, 1fr, 1fr),
    column-gutter: 0.75em,
    row-gutter: 0pt,
    [#text(size: 10.2pt)[(#no)]],
    [#text(size: 10.2pt)[A. #a]],
    [#text(size: 10.2pt)[B. #b]],
    [#text(size: 10.2pt)[C. #c]],
    [#text(size: 10.2pt)[D. #d]],
  )
  #v(3pt)
]

// Compact answer grid for multiple-choice drills.
#let eric-choice-answer-grid(count: 10) = [
  #let numbers = range(1, count + 1).map(i => [#i])
  #let blanks = range(1, count + 1).map(i => [])
  #hermes-table(
    (1fr,) + range(count).map(i => 0.72fr),
    (
      [题号],
      ..numbers,
      [答案],
      ..blanks,
    ),
  )
]

// Muted metadata block for student/date/version lines.
#let eric-meta(body) = [
  #text(size: 9.5pt, fill: c-muted)[#body]
]

// Functional emphasis box for rules, exam reminders, and action checks.
#let eric-rule-box(title, body) = [
  #rect(
    width: 100%,
    fill: c-accent-bg,
    inset: (x: 12pt, y: 8pt),
    radius: 4pt,
    stroke: 0.45pt + c-accent-border,
  )[
    #text(size: 9pt, weight: 700, fill: c-amber)[#title]
    #v(3pt)
    #text(size: 9pt, fill: c-text)[#body]
  ]
  #v(6pt)
]

// Quiet reference box for formulas, memory cues, and compact notes.
#let eric-note-box(title, body) = [
  #rect(
    width: 100%,
    fill: c-note-bg,
    inset: (x: 12pt, y: 8pt),
    radius: 4pt,
    stroke: 0.45pt + c-note-border,
  )[
    #text(size: 9pt, weight: 700, fill: c-text)[#title]
    #v(3pt)
    #text(size: 9pt, fill: c-text)[#body]
  ]
  #v(6pt)
]

// Compact action strip for timed drills, lookup entries, and classroom rounds.
#let eric-action-strip(label, detail) = [
  #rect(
    width: 100%,
    fill: c-accent-bg,
    inset: (x: 10pt, y: 6pt),
    radius: 3pt,
    stroke: 0.45pt + c-accent-border,
  )[
    #text(size: 9pt, weight: 700, fill: c-amber)[#label]
    #h(0.8em)
    #text(size: 9pt, fill: c-text)[#detail]
  ]
  #v(6pt)
]

// Backward-compatible alias for timed drills.
#let eric-timed-strip(label, detail) = eric-action-strip(label, detail)

// Neutral lookup strip for manual sections such as 调用入口.
#let eric-lookup-strip(label, detail) = [
  #rect(
    width: 100%,
    fill: c-card,
    inset: (x: 10pt, y: 6pt),
    radius: 3pt,
    stroke: 0.35pt + c-border,
  )[
    #text(size: 9pt, weight: 700, fill: c-amber)[#label]
    #h(0.8em)
    #text(size: 9pt, fill: c-text)[#detail]
  ]
  #v(6pt)
]

#let eric-step-card(title, body) = rect(
  width: 100%,
  fill: c-card,
  inset: (x: 10pt, y: 8pt),
  radius: 3pt,
  stroke: 0.35pt + c-border,
)[
  #text(size: 9.5pt, weight: 700, fill: c-amber)[#title]
  #v(4pt)
  #text(size: 9pt, fill: c-text)[#body]
]

// Three-step usage guide for manuals and lookup handbooks.
#let eric-method-steps(step1-title, step1-body, step2-title, step2-body, step3-title, step3-body) = [
  #grid(
    columns: (1fr, 1fr, 1fr),
    column-gutter: 10pt,
    [
      #eric-step-card([1. #step1-title], step1-body)
    ],
    [
      #eric-step-card([2. #step2-title], step2-body)
    ],
    [
      #eric-step-card([3. #step3-title], step3-body)
    ],
  )
  #v(8pt)
]

// Directory card for scene vocab manuals and review handbooks.
#let eric-directory-card(no, title, desc, count: none) = [
  #rect(
    width: 100%,
    fill: c-card,
    inset: (x: 10pt, y: 8pt),
    radius: 3pt,
    stroke: 0.35pt + c-border,
  )[
    #text(size: 10pt, weight: 700, fill: c-amber)[#no #title]
    #v(5pt)
    #text(size: 9.5pt, fill: c-text)[#desc]
    #if count != none {
      v(5pt)
      text(size: 8.5pt, fill: c-muted)[#count]
    }
  ]
]

// Dense lookup tables for scene vocab manuals.
#let eric-dense-table(columns, body) = [
  #set text(size: 8.6pt)
  #table(
    columns: columns,
    stroke: (x, y) => if y == 0 { (top: 0.65pt + c-border, bottom: 0.65pt + c-border) } else { (top: 0.3pt + c-border, bottom: 0.3pt + c-border) },
    inset: (x: 5pt, y: 2.6pt),
    align: left + top,
    fill: (col, row) => if row == 0 { c-header-bg } else { if calc.rem(row, 2) == 0 { c-card } else { none } },
    ..body
  )
]

#let eric-vocab-table(body) = eric-dense-table(
  (1.05fr, 0.38fr, 0.55fr, 1.25fr, 2.5fr),
  body,
)

// Small drill table that ends a lookup section with visible student action.
#let eric-initial-drill-table(body) = eric-dense-table(
  (0.65fr, 2.7fr, 0.9fr, 1.25fr),
  body,
)

// Homework and routine block: one action, one check, one visible completion target.
#let eric-task-card(title, body) = [
  #rect(
    width: 100%,
    fill: c-card,
    inset: (x: 12pt, y: 8pt),
    radius: 4pt,
    stroke: 0.35pt + c-border,
  )[
    #text(size: 10pt, weight: 700, fill: c-text)[#title]
    #v(4pt)
    #text(size: 9.5pt, fill: c-text)[#body]
  ]
  #v(6pt)
]

// Teacher-only operational strip. Use only in teacher-facing PDFs.
#let eric-teacher-strip(body) = [
  #align(right)[
    #text(size: 8pt, fill: c-muted)[仅供教师使用 · #body]
  ]
  #v(6pt)
]

// Ruled handwriting area for writing tasks. Prefer this over loose line()
// calls so line spacing stays stable in printed PDFs.
#let eric-writing-area(lines: 8, label: none) = [
  #if label != none {
    text(size: 9pt, fill: c-muted)[#label]
    v(4pt)
  }
  #table(
    columns: (1fr,),
    stroke: (x, y) => (bottom: 0.45pt + c-border),
    inset: (x: 0pt, y: 8.5pt),
    align: left + bottom,
    fill: none,
    ..range(lines).map(i => [])
  )
  #v(6pt)
]

// Backward-compatible alias.
#let eric-writing-lines(count: 6) = eric-writing-area(lines: count)

// Small checkbox list helper for routines and self-checks.
#let eric-check-item(body) = [
  #checkbox
  #h(0.6em)
  #body
  #linebreak()
]

// Show content only in teacher math versions.
#let eric-math-teacher-only(body, version: "student") = [
  #if version == "teacher" {
    body
  }
]

// Backward-compatible alias.
#let eric-teacher-only(body, version: "student") = eric-math-teacher-only(body, version: version)

// Show content only in student math versions.
#let eric-math-student-only(body, version: "student") = [
  #if version == "student" {
    body
  }
]

// Safe solution block: teacher sees full solution, student sees only the
// provided prompt/hint. Use this instead of hand-writing page-level if/else.
#let eric-math-solution-block(title, teacher, version: "student", student: none) = [
  #if version == "teacher" {
    eric-teacher-strip[教师版 · #title]
    teacher
  } else if student != none {
    student
  }
]

// Formula, definition, theorem, or method entry for math materials.
#let eric-math-formula-box(title, formula, conditions, note: none, misuse: none) = [
  #rect(
    width: 100%,
    fill: c-accent-bg,
    inset: (x: 12pt, y: 8pt),
    radius: 4pt,
    stroke: 0.45pt + c-accent-border,
  )[
    #text(size: 9.5pt, weight: 700, fill: c-amber)[#title]
    #v(5pt)
    #text(size: 12pt, fill: c-text)[#formula]
    #v(5pt)
    #text(size: 9pt, fill: c-text)[适用条件：#conditions]
    #if note != none {
      v(4pt)
      text(size: 8.8pt, fill: c-muted)[#note]
    }
    #if misuse != none {
      v(4pt)
      text(size: 8.8pt, fill: c-amber)[常见误用：#misuse]
    }
  ]
  #v(7pt)
]

// Official-looking math example block.
#let eric-math-example(no, title, body, tags: none, difficulty: none) = [
  #rect(
    width: 100%,
    fill: c-card,
    inset: (x: 12pt, y: 8pt),
    radius: 4pt,
    stroke: 0.35pt + c-border,
  )[
    #grid(
      columns: (1fr, auto),
      [
        #text(size: 10pt, weight: 700, fill: c-text)[例 #no · #title]
      ],
      [
        #if difficulty != none {
          text(size: 8.5pt, fill: c-amber)[#difficulty]
        }
      ],
    )
    #if tags != none {
      v(3pt)
      text(size: 8.5pt, fill: c-muted)[#tags]
    }
    #v(5pt)
    #text(size: 10pt, fill: c-text)[#body]
  ]
  #v(7pt)
]

// Teacher-facing solution step table: step, operation, reason, result.
#let eric-math-step-table(body) = hermes-table(
  (0.55fr, 1.8fr, 1.55fr, 1.15fr),
  body,
)

// Large-question solution flow for Gaokao-style written problems.
#let eric-math-large-question-table(body) = hermes-table(
  (0.8fr, 1.55fr, 1.8fr, 1.25fr),
  body,
)

// Geometry proof table: claim, reason, derived conclusion.
#let eric-math-proof-table(body) = hermes-table(
  (0.55fr, 1.65fr, 1.65fr, 1.25fr),
  body,
)

// Known/target/constraint table for diagram and proof problems.
#let eric-math-known-target-table(body) = hermes-table(
  (0.9fr, 2.2fr),
  body,
)

// Stable handwritten calculation area for math. Modes: ruled, grid, blank.
#let eric-math-workspace(lines: 8, mode: "ruled", label: none) = [
  #if label != none {
    text(size: 9pt, fill: c-muted)[#label]
    v(4pt)
  }
  #if mode == "grid" {
    table(
      columns: range(8).map(i => 1fr),
      rows: range(lines).map(i => 18pt),
      stroke: 0.35pt + c-border,
      inset: 0pt,
      fill: none,
      ..range(lines * 8).map(i => [])
    )
  } else if mode == "blank" {
    rect(width: 100%, height: lines * 18pt, stroke: 0.45pt + c-border, fill: none)
  } else {
    table(
      columns: (1fr,),
      stroke: (x, y) => (bottom: 0.45pt + c-border),
      inset: (x: 0pt, y: 8.5pt),
      align: left + bottom,
      fill: none,
      ..range(lines).map(i => [])
    )
  }
  #v(7pt)
]

// Standard panel for graphs, geometry diagrams, and source-paper images.
#let eric-math-diagram-panel(title, body, note: none) = [
  #rect(
    width: 100%,
    fill: c-card,
    inset: (x: 12pt, y: 8pt),
    radius: 4pt,
    stroke: 0.5pt + c-border,
  )[
    #text(size: 9.5pt, weight: 700, fill: c-amber)[#title]
    #v(6pt)
    #body
    #if note != none {
      v(5pt)
      text(size: 8.5pt, fill: c-muted)[#note]
    }
  ]
  #v(7pt)
]

// Source-accurate diagram wrapper for exam crops, GeoGebra exports, SVG/PDF/PNG
// diagrams, and other verified figure assets.
#let eric-math-source-diagram(path, title: [原题图], width: 100%, note: none) = eric-math-diagram-panel(
  title,
  [
    #align(center)[#image(path, width: width)]
  ],
  note: note,
)

// Explicit placeholder when a complex figure is required but the source image
// or vector asset has not been provided yet. Prefer this over inventing a
// complex source-bearing diagram from hardcoded coordinates.
#let eric-math-diagram-needed(title: [图形待补], note: [需补入原题图裁切、GeoGebra 导出图或经验证的矢量图。]) = eric-math-diagram-panel(
  title,
  [
    #rect(width: 100%, height: 120pt, fill: none, stroke: 0.45pt + c-border)[
      #align(center + horizon)[
        #text(size: 9pt, fill: c-muted)[此处保留图形位，生成前必须补入可核验图源。]
      ]
    ]
  ],
  note: note,
)

// Lightweight coordinate grid for blank function and geometry sketches.
// Axis labels are intentionally quiet so students can write over the graph.
#let eric-math-coordinate-grid(cols: 10, rows: 6, height: 130pt, x-label: [$x$], y-label: [$y$], origin-label: [$O$], axis-labels: true) = [
  #let axis-col = calc.floor(cols / 2)
  #let axis-row = calc.floor(rows / 2)
  #table(
    columns: range(cols).map(i => 1fr),
    rows: range(rows).map(i => height / rows),
    stroke: (col, row) => {
      let base = 0.3pt + c-grid
      let strong = 0.6pt + c-border
      (
        left: if col == axis-col { strong } else { base },
        top: if row == axis-row { strong } else { base },
        right: base,
        bottom: base,
      )
    },
    inset: 0pt,
    fill: (col, row) => if col == axis-col or row == axis-row { c-accent-bg } else { none },
    ..range(cols * rows).map(i => {
      let col = calc.rem(i, cols)
      let row = calc.floor(i / cols)
      if axis-labels and col == axis-col and row == axis-row {
        text(size: 7pt, fill: c-muted)[#origin-label]
      } else if axis-labels and col == cols - 1 and row == axis-row {
        align(right + top, text(size: 7pt, fill: c-muted)[#x-label])
      } else if axis-labels and col == axis-col and row == 0 {
        align(left + top, text(size: 7pt, fill: c-muted)[#y-label])
      } else {
        []
      }
    })
  )
]

// Simple geometry schematic only: triangle with labeled vertices and optional
// auxiliary point/line. Do not use this for source-accurate or complex geometry.
#let eric-math-triangle-diagram(a: [A], b: [B], c: [C], d: none, aux: none, height: 135pt) = [
  #let show-aux = d != none or aux != none
  #let d-label = if d == none { [D] } else { d }
  #rect(width: 100%, height: height, fill: none, stroke: 0.35pt + c-grid)[
    #align(center + horizon)[
      #box(width: 190pt, height: 104pt)[
        #place(dx: 0pt, dy: 0pt, line(start: (48pt, 86pt), end: (102pt, 14pt), stroke: 1pt + c-text))
        #place(dx: 0pt, dy: 0pt, line(start: (102pt, 14pt), end: (168pt, 86pt), stroke: 1pt + c-text))
        #place(dx: 0pt, dy: 0pt, line(start: (48pt, 86pt), end: (168pt, 86pt), stroke: 1pt + c-text))
        #if show-aux {
          place(dx: 0pt, dy: 0pt, line(start: (102pt, 14pt), end: (112pt, 86pt), stroke: 0.85pt + c-amber))
          place(dx: 106pt, dy: 88pt, text(size: 8pt, fill: c-muted)[#d-label])
        }
        #place(dx: 96pt, dy: 0pt, text(size: 8pt, fill: c-muted)[#a])
        #place(dx: 38pt, dy: 88pt, text(size: 8pt, fill: c-muted)[#b])
        #place(dx: 170pt, dy: 88pt, text(size: 8pt, fill: c-muted)[#c])
      ]
    ]
  ]
  #if aux != none {
    v(3pt)
    text(size: 8.5pt, fill: c-muted)[辅助线：#aux]
  }
]

// Answer recording grid for math choice, fill-in, mixed, or short-answer sets.
#let eric-math-answer-grid(kind: "mixed", count: 6) = [
  #let numbers = range(1, count + 1).map(i => [#i])
  #let blanks = range(1, count + 1).map(i => [])
  #let label = if kind == "choice" { [选项] } else if kind == "fill" { [结果] } else { [答案] }
  #hermes-table(
    (1fr,) + range(count).map(i => 0.8fr),
    (
      [题号],
      ..numbers,
      label,
      ..blanks,
    ),
  )
  #v(7pt)
]

// Final answer box for solution problems. Keeps the conclusion visible.
#let eric-math-final-answer-box(label: [最终答案], body: none) = [
  #rect(
    width: 100%,
    fill: c-card,
    inset: (x: 10pt, y: 7pt),
    radius: 3pt,
    stroke: 0.35pt + c-border,
  )[
    #text(size: 9pt, weight: 700, fill: c-amber)[#label]
    #h(0.8em)
    #if body != none {
      text(size: 9.5pt, fill: c-text)[#body]
    } else {
      box(line(length: 70%, stroke: 0.5pt + c-border))
    }
  ]
  #v(7pt)
]

// Teacher-facing scoring table for solution problems.
#let eric-math-score-rubric(body) = [
  #text(size: 10pt, weight: 700, fill: c-amber)[评分点]
  #v(4pt)
  #hermes-table(
    (0.8fr, 2.4fr, 0.7fr),
    body,
  )
  #v(7pt)
]

// Student correction table for math mistakes.
#let eric-math-error-log(rows: 4) = [
  #text(size: 10pt, weight: 700, fill: c-amber)[错因归档]
  #v(4pt)
  #let row-cells = range(1, rows + 1).map(i => ([#i], [], [], [])).flatten()
  #hermes-table(
    (0.45fr, 1.25fr, 1.6fr, 1.25fr),
    (
      [序号], [错因/卡点], [订正动作], [复查结果],
      ..row-cells,
    ),
  )
  #v(7pt)
]
