---
template: correction-rewrite
variant: error-to-fix-rewrite
section: unit
kicker: "Rewrite"
ribbon_note: "error to output"
heading: "Correction Rewrite"
lesson_note: "Find the extra signal first. Then write the better sentence and say why the change works."
lens:
  - label: "Error"
    text: "because + so"
  - label: "Improve"
    text: "keep one connector"
  - label: "Proof"
    text: "the meaning still shows reason"
record_label: "Rewrite Record"
record_note: "error · better sentence · reason"
rewrite_rows:
  - label: "01"
    prompt: "Original: Because it rained, so we stayed home. Better sentence:"
    lines: 3
  - label: "02"
    prompt: "Original: Although the answer is easy, but I checked it. Better sentence:"
    lines: 3
  - label: "03"
    prompt: "Reason check: The connector I removed was ____ because ____."
    lines: 2
micro_rules:
  - "One relationship normally needs one clear connector."
  - "After rewriting, read the sentence without the extra word."
  - "If the meaning changes, the rewrite is not finished."
editing:
  - "Remove the extra connector."
  - "Keep only one clear logic signal."
  - "Read the sentence aloud once."
---
