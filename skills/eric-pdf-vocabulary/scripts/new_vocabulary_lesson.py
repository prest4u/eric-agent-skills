#!/usr/bin/env python3
"""Create a standalone, editable Typst vocabulary lesson without overwriting."""

from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_WORDS = [
    "evidence",
    "context",
    "contrast",
    "infer",
    "precise",
    "revise",
    "retain",
    "transfer",
    "relevant",
    "structure",
    "respond",
    "evaluate",
]


def escape_typst(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace("#", "\\#")
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("*", "\\*")
        .replace("_", "\\_")
    )


def build_source(title: str, words: list[str]) -> str:
    rows = []
    for index, word in enumerate(words, start=1):
        safe = escape_typst(word)
        rows.append(
            f"#grid(columns: (28pt, 1fr), gutter: 10pt, "
            f"[#text(fill: rgb(\"52766d\"), weight: \"bold\")[{index:02d}]], "
            f"[#text(size: 13pt, weight: \"bold\")[{safe}] #linebreak()\n"
            f"Meaning / phrase: #line(length: 70%, stroke: 0.5pt + rgb(\"b8c8c2\")) #linebreak()\n"
            f"My sentence: #line(length: 76%, stroke: 0.5pt + rgb(\"b8c8c2\"))])"
        )
    word_rows = "\n#v(7pt)\n".join(rows)
    safe_title = escape_typst(title)
    return f'''#set page(paper: "a4", margin: (x: 21mm, y: 18mm))
#set text(font: "Libertinus Serif", size: 10.5pt, fill: rgb("27332f"))
#set par(leading: 0.72em)

#rect(width: 100%, height: 38mm, fill: rgb("eef3ef"), stroke: none, inset: 14pt)[
  #text(size: 9pt, tracking: 0.12em, fill: rgb("52766d"))[Vocabulary Learning]
  #v(6pt)
  #text(size: 25pt, weight: "bold")[{safe_title}]
  #v(5pt)
  #text(size: 9.5pt, fill: rgb("6d7772"))[Memory Chain Lesson · Eric Teaching Studio]
]

#v(14pt)
#text(size: 15pt, weight: "bold", fill: rgb("385c53"))[Lesson route]
#v(5pt)
Read in context → notice the phrase → build one accurate sentence → review the red words.

#v(12pt)
#text(size: 15pt, weight: "bold", fill: rgb("385c53"))[Core words]
#v(7pt)
{word_rows}

#pagebreak()
#text(size: 18pt, weight: "bold", fill: rgb("385c53"))[Grammar bridge]
#v(8pt)
Choose four words. Write one sentence for each, then combine two ideas with a connector.

#v(8pt)
#for n in range(1, 5) [
  #text(weight: "bold", fill: rgb("52766d"))[#n.] #line(length: 86%, stroke: 0.6pt + rgb("aebdb7"))
  #v(13pt)
]

#v(8pt)
#rect(width: 100%, fill: rgb("f6f1e7"), stroke: 0.6pt + rgb("d8c9ad"), inset: 12pt)[
  #text(size: 14pt, weight: "bold", fill: rgb("765d35"))[Red-word review]
  #v(6pt)
  Circle three words that still feel slow. Add one phrase beside each word and review them tomorrow.
  #v(12pt)
  #line(length: 100%, stroke: 0.5pt + rgb("bda982"))
  #v(12pt)
  #line(length: 100%, stroke: 0.5pt + rgb("bda982"))
]

#v(18pt)
#text(size: 14pt, weight: "bold", fill: rgb("385c53"))[Before you leave]
#v(6pt)
The word I can now use accurately: #line(length: 48%, stroke: 0.6pt + rgb("aebdb7"))
#v(12pt)
The word I will practise next: #line(length: 54%, stroke: 0.6pt + rgb("aebdb7"))
'''


def create_project(output: Path, title: str, words: list[str]) -> Path:
    output = output.expanduser().resolve()
    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing path: {output}")
    if not title.strip():
        raise ValueError("title must not be empty")
    if not words:
        raise ValueError("at least one word is required")
    output.mkdir(parents=True)
    target = output / "lesson.typ"
    target.write_text(build_source(title.strip(), words), encoding="utf-8")
    return target


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--words", help="Comma-separated words; defaults to an anonymized sample set")
    args = parser.parse_args()
    words = [word.strip() for word in args.words.split(",") if word.strip()] if args.words else DEFAULT_WORDS
    try:
        print(create_project(args.out, args.title, words))
    except (FileExistsError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
