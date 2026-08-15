#let paper = rgb("#fffdf8")
#let ink = rgb("#221a16")
#let muted = rgb("#74665d")
#let clay = rgb("#b85c38")
#let hairline = rgb("#dcc9ba")
#let card = rgb("#fffaf3")

#set page(
  paper: "a4",
  fill: paper,
  margin: (left: 2.2cm, right: 2.2cm, top: 2cm, bottom: 2cm),
  header: none,
  footer: none,
  numbering: none,
)
#set text(
  font: ("PingFang SC", "Hiragino Sans GB", "Arial"),
  size: 10.5pt,
  fill: ink,
)
#set par(leading: 0.82em)
#show heading.where(level: 1): it => [
  #v(12pt)
  #text(size: 15pt, weight: 700)[#it.body]
  #v(4pt)
]
#show heading.where(level: 2): it => [
  #v(9pt)
  #text(size: 12pt, weight: 650, fill: clay)[#it.body]
  #v(3pt)
]

#let note-box(title, body) = block(
  width: 100%,
  inset: 10pt,
  radius: 3pt,
  fill: card,
  stroke: 0.55pt + hairline,
  [#text(weight: 700, fill: clay)[#title] #h(0.7em) #body],
)

#let writing-lines(count: 4) = {
  for _ in range(count) {
    line(length: 100%, stroke: 0.45pt + hairline)
    v(12pt)
  }
}

#align(center)[
  #v(21%)
  #text(size: 22pt, weight: 700)[Classroom Handout]
  #v(7pt)
  #text(size: 13pt, weight: 600, fill: clay)[Replace with the lesson focus]
  #v(10pt)
  #line(length: 20%, stroke: 0.8pt + clay)
  #v(23%)
  #text(size: 9pt, fill: muted)[Student / Date]
]

#pagebreak()
#counter(page).update(1)
#set page(
  header: context {
    set text(size: 8pt, fill: muted)
    align(right)[Classroom Handout #h(1em) #counter(page).display("1")]
  },
)

= Learning focus

#note-box[Do][Replace this starter text with one clear learner action.]

== Practice

Keep the task sequence, answer space, and student/teacher boundary explicit.

#writing-lines(count: 5)

== Before you leave

- Check the evidence you used.
- Mark one point to revisit.
