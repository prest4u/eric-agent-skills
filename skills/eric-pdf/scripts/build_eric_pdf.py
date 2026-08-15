#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a simple Hermes-style Typst PDF from Markdown."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


def esc(text: str) -> str:
    replacements = {"\\": "\\\\", "#": "\\#", "$": "\\$", "[": "\\[", "]": "\\]"}
    return "".join(replacements.get(ch, ch) for ch in text)


def inline(text: str) -> str:
    out: list[str] = []
    pos = 0
    for match in re.finditer(r"\*\*(.+?)\*\*", text):
        out.append(esc(text[pos : match.start()]))
        out.append(f"#strong[{esc(match.group(1))}]")
        pos = match.end()
    out.append(esc(text[pos:]))
    return "".join(out)


def is_table_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and "|" in stripped[1:]


def is_separator(line: str) -> bool:
    parts = [p.strip() for p in line.strip().strip("|").split("|")]
    return bool(parts) and all(re.fullmatch(r":?-{3,}:?", part or "") for part in parts)


def split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def render_table(lines: list[str]) -> str:
    if len(lines) < 2 or not is_separator(lines[1]):
        return "\n".join(inline(line) for line in lines) + "\n"
    headers = split_row(lines[0])
    rows = [split_row(line) for line in lines[2:] if line.strip()]
    result = [
        "#table(\n",
        f"  columns: {len(headers)},\n",
        "  stroke: (x, y) => if y == 0 { (top: 0.65pt + c-border, bottom: 0.65pt + c-border) } else { (top: 0.3pt + c-border, bottom: 0.3pt + c-border) },\n",
        "  inset: (x: 6pt, y: 4pt),\n",
        "  align: left + top,\n",
        "  fill: (col, row) => if row == 0 { c-header-bg } else { if calc.rem(row, 2) == 0 { c-card } else { none } },\n",
        "  table.header(\n",
    ]
    for cell in headers:
        result.append(f"    [#text(weight: 700)[{inline(cell)}]],\n")
    result.append("  ),\n")
    for row in rows:
        for cell in (row[: len(headers)] + [""] * max(0, len(headers) - len(row))):
            result.append(f"    [{inline(cell)}],\n")
    result.append(")\n#v(8pt)\n")
    return "".join(result)


def render_list(lines: list[str]) -> str:
    out = []
    for line in lines:
        stripped = line.strip()
        if re.match(r"^\d+\.\s+", stripped):
            out.append("+ " + inline(re.sub(r"^\d+\.\s+", "", stripped)) + "\n")
        elif stripped.startswith("- "):
            out.append("- " + inline(stripped[2:]) + "\n")
    out.append("#v(4pt)\n")
    return "".join(out)


def preamble(title: str, subtitle: str, meta: str) -> str:
    return f"""#let c-paper = rgb("#fffdf8")
#let c-text = rgb("#221a16")
#let c-muted = rgb("#74665d")
#let c-amber = rgb("#b85c38")
#let c-border = rgb("#dcc9ba")
#let c-card = rgb("#fffaf3")
#let c-header-bg = rgb("#f7eadf")

#set page(
  paper: "a4",
  fill: c-paper,
  margin: (left: 2.2cm, right: 2.2cm, top: 2cm, bottom: 2cm),
  header: none,
  footer: none,
  numbering: none,
)
#set text(font: ("PingFang SC", "Hiragino Sans GB"), size: 11pt, lang: "zh", fill: c-text)
#set par(leading: 0.9em, first-line-indent: 0pt)

#show heading.where(level: 1): it => [#v(20pt)#text(size: 15pt, weight: 700)[#it.body]#v(3pt)]
#show heading.where(level: 2): it => [#v(16pt)#text(size: 13pt, weight: 600)[#it.body]#v(3pt)]
#show heading.where(level: 3): it => [#v(10pt)#text(size: 11pt, weight: 600)[#it.body]#v(2pt)]
#show table: it => {{
  set text(size: 9pt)
  set par(leading: 0.78em)
  it
}}
#show strong: it => text(weight: 700, fill: c-amber)[#it.body]

#align(center)[
  #v(22%)
  #text(size: 22pt, weight: 700)[{esc(title)}]
  #v(6pt)
  #text(size: 14pt, weight: 600, fill: c-amber)[{esc(subtitle)}]
  #v(10pt)
  #line(length: 20%, stroke: 0.8pt + c-amber)
  #v(25%)
  #text(size: 9pt, fill: c-muted)[{esc(meta)}]
]

#pagebreak()
#counter(page).update(1)
#set page(
  fill: c-paper,
  header: context {{
    set text(size: 8pt, fill: c-muted)
    align(right, [{esc(title)} #h(1em) #counter(page).display("1")])
  }},
  footer: none,
  numbering: none,
)

"""


def render(markdown: str) -> str:
    output: list[str] = []
    table_lines: list[str] = []
    list_lines: list[str] = []
    seen_h1 = False

    def flush() -> None:
        nonlocal table_lines, list_lines
        if table_lines:
            output.append(render_table(table_lines))
            table_lines = []
        if list_lines:
            output.append(render_list(list_lines))
            list_lines = []

    for raw in markdown.splitlines():
        line = raw.rstrip()
        if not line.strip():
            flush()
            output.append("\n")
            continue
        if is_table_line(line):
            if list_lines:
                output.append(render_list(list_lines))
                list_lines = []
            table_lines.append(line)
            continue
        if line.strip().startswith("- ") or re.match(r"^\d+\.\s+", line.strip()):
            if table_lines:
                output.append(render_table(table_lines))
                table_lines = []
            list_lines.append(line)
            continue
        flush()
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            heading = line[level:].strip()
            if level == 1:
                if seen_h1:
                    output.append("#pagebreak()\n")
                seen_h1 = True
                output.append(f"= {inline(heading)}\n")
            elif level == 2:
                output.append(f"== {inline(heading)}\n")
            else:
                output.append(f"=== {inline(heading)}\n")
            continue
        output.append(inline(line) + "\n")
    flush()
    return "".join(output)


def validate_output_paths(input_md: Path, output_pdf: Path, overwrite: bool) -> Path:
    if not input_md.exists():
        raise FileNotFoundError(f"input Markdown does not exist: {input_md}")
    if output_pdf.suffix.lower() != ".pdf":
        raise ValueError("output path must end with .pdf")
    typ_path = output_pdf.with_suffix(".typ")
    for path in (output_pdf, typ_path):
        if path.is_symlink():
            raise FileExistsError(f"refusing to write symlink output: {path}")
        if path.exists() and not overwrite:
            raise FileExistsError(f"refusing to overwrite existing output without --overwrite: {path}")
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    return typ_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a Hermes-style Typst PDF from Markdown.")
    parser.add_argument("input_md", type=Path)
    parser.add_argument("output_pdf", type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--subtitle", default="")
    parser.add_argument("--meta", default="")
    parser.add_argument("--typst", default="typst")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output PDF/Typst after explicit approval.")
    args = parser.parse_args()

    typ_path = validate_output_paths(args.input_md, args.output_pdf, args.overwrite)
    markdown = args.input_md.read_text(encoding="utf-8")
    typ_path.write_text(preamble(args.title, args.subtitle, args.meta) + render(markdown), encoding="utf-8")
    subprocess.run([args.typst, "compile", str(typ_path), str(args.output_pdf)], check=True)
    print(typ_path)
    print(args.output_pdf)


if __name__ == "__main__":
    main()
