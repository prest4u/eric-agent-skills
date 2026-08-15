#!/usr/bin/env python3
"""Run bounded structural checks on an Eric editorial PDF."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path


def run(*command: str) -> str:
    completed = subprocess.run(
        command,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return completed.stdout


def require_tool(name: str) -> None:
    if shutil.which(name) is None:
        raise SystemExit(f"Missing required local tool: {name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--expect-pages", type=int)
    parser.add_argument("--allow-non-a4", action="store_true")
    args = parser.parse_args()

    pdf = Path(args.pdf).expanduser().resolve()
    if not pdf.is_file():
        raise SystemExit(f"PDF not found: {pdf}")

    for tool in ("pdfinfo", "pdffonts", "pdftotext", "qpdf"):
        require_tool(tool)

    info = run("pdfinfo", str(pdf))
    page_match = re.search(r"^Pages:\s+(\d+)\s*$", info, re.MULTILINE)
    size_match = re.search(r"^Page size:\s+(.+)$", info, re.MULTILINE)
    if not page_match or not size_match:
        raise SystemExit("Could not read page count or page size")

    pages = int(page_match.group(1))
    if args.expect_pages is not None and pages != args.expect_pages:
        raise SystemExit(f"Expected {args.expect_pages} pages, found {pages}")
    if not args.allow_non_a4 and "A4" not in size_match.group(1):
        raise SystemExit(f"Expected A4 pages, found: {size_match.group(1)}")

    run("qpdf", "--check", str(pdf))
    extracted = run("pdftotext", str(pdf), "-")
    if len(extracted.strip()) < 20:
        raise SystemExit("Selectable text layer is empty or unexpectedly short")
    blank_pages = []
    for page_number in range(1, pages + 1):
        page_text = run(
            "pdftotext",
            "-f",
            str(page_number),
            "-l",
            str(page_number),
            str(pdf),
            "-",
        )
        if len(page_text.strip()) < 8:
            blank_pages.append(page_number)
    if blank_pages:
        raise SystemExit(
            "Pages with empty or unexpectedly short selectable text: "
            + ", ".join(map(str, blank_pages))
        )

    fonts = run("pdffonts", str(pdf))
    font_rows = []
    for line in fonts.splitlines():
        match = re.search(
            r"\s+(yes|no)\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+\s*$", line
        )
        if match:
            font_rows.append(match.groups())
    if not font_rows:
        raise SystemExit("Could not parse embedded font status")
    if any(
        embedded != "yes" or unicode_map != "yes"
        for embedded, _, unicode_map in font_rows
    ):
        raise SystemExit("All fonts must be embedded and have Unicode mappings")

    print(
        f"PASS: {pdf.name} | pages={pages} | size=A4 | "
        f"fonts={len(font_rows)} embedded | selectable_text=yes | blank_pages=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
