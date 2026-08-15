---
template: diagnostic-entry
section: front
kicker: "Diagnostic"
ribbon_note: "before the lesson"
heading: "What Do You Notice First?"
lead: "Choose the answer that shows the sentence connection most clearly."
teacher_note_title: "Diagnostic Cue"
teacher_note: "Before confirming the letter, ask which sentence job the student noticed."
teacher_answers:
  - "01 B"
  - "02 A"
labels: ["位置", "缺成分", "逻辑"]
checks:
  - prompt: "The sentence has two verbs. What should you check first?"
    options: ["A. time", "B. connector", "C. spelling"]
  - prompt: "Which word can begin a reason clause?"
    options: ["A. because", "B. quickly", "C. desk"]
diagnostic_notes:
  - label: "A"
    title: "Verb signal"
    text: "Two finite verbs usually mean the sentence needs a connector or a clear boundary."
  - label: "B"
    title: "Logic signal"
    text: "Because gives a reason; although gives contrast; before gives time order."
  - label: "C"
    title: "Fast risk"
    text: "Do not choose a connector only because the sentence sounds familiar."
diagnostic_ladder:
  - "Underline the finite verbs."
  - "Name the logic between the two ideas."
  - "Choose the connector that matches the logic."
record_label: "Diagnostic Record"
record_note: "one clue · one risk · one next check"
record_rows:
  - label: "01"
    prompt: "The first clue I should check is ____."
    lines: 2
  - label: "02"
    prompt: "The connector risk I need to slow down for is ____."
    lines: 1
---
