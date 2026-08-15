#let teal = rgb("#0f7890")
#let activity = rgb("#9a3370")
#let rust = rgb("#b8642f")
#let green = rgb("#43856f")
#let linec = rgb("#9fc3c6")
#let ink = rgb("#161616")
#let paper = rgb("#ffffff")

#set page(paper: "a4", margin: (left: 2.2cm, right: 2.2cm, top: 2cm, bottom: 2cm), fill: paper)
#set text(font: ("PingFang SC", "Hiragino Sans GB", "Arial"), size: 10.5pt, fill: ink, lang: "en")
#set par(leading: 0.78em)

#let top-rule() = rect(width: 100%, height: 4pt, fill: teal)
#let activity-title(no, title) = [
  #text(fill: activity, weight: 800, size: 12pt)[ACTIVITY #no] #text(fill: activity, size: 13pt)[ | #title]
]
#let write-line() = line(length: 100%, stroke: 0.55pt + gray)
#let words-to-know(body) = rect(width: 100%, stroke: 0.7pt + linec, inset: 8pt)[
  #text(fill: green, weight: 800)[WORDS TO KNOW] #body
]

#top-rule()
#v(10pt)
#text(fill: teal, size: 21pt, tracking: 1pt)[ELEMENTS OF BETTER WRITING]
#line(length: 100%, stroke: 0.7pt + rgb("#c8e2e4"))
#v(14pt)

#text(fill: teal, size: 16pt)[What Is a Sentence?]

A simple sentence expresses one complete thought. It has a subject and a verb. It may have an object or other information after the verb.

#v(8pt)
#table(
  columns: (1fr, 1fr, 1fr, 1fr),
  stroke: 0.6pt + linec,
  inset: 6pt,
  table.cell(fill: teal)[#text(fill: white, weight: 800)[SUBJECT]],
  table.cell(fill: teal)[#text(fill: white, weight: 800)[VERB]],
  table.cell(fill: teal)[#text(fill: white, weight: 800)[OBJECT]],
  table.cell(fill: teal)[#text(fill: white, weight: 800)[OTHER INFORMATION]],
  [Maya], [studies], [], [every evening.],
  [The teacher], [checks], [the paragraph], [after class.],
)

#v(12pt)
#activity-title(1, [Identifying sentence parts])

Underline the subject. Circle the verb. Double underline any object.

1. My friend and I read travel stories.

2. The students write clear sentences.

3. A small mistake changes the meaning.

#v(12pt)
#words-to-know[
  #h(1em)#strong[journal] (n) a notebook for recording ideas #h(2em)
  #strong[observe] (v) to look carefully
]

#v(16pt)
#text(fill: teal, size: 16pt)[Writing]

Write one clear sentence about a quiet place.

#v(8pt)
#write-line()
#v(14pt)
#write-line()
#v(14pt)
#write-line()
