#!/usr/bin/env python3
"""Run the reusable structural checks for a research-monograph PDF."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


def run(*command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, check=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--expected-pages", type=int)
    args = parser.parse_args()
    if not args.pdf.is_file():
        raise SystemExit(f"PDF not found: {args.pdf}")

    info = run("pdfinfo", str(args.pdf))
    syntax = run("qpdf", "--check", str(args.pdf))
    text = run("pdftotext", str(args.pdf), "-")
    pages_match = re.search(r"^Pages:\s+(\d+)", info.stdout, re.M)
    page_size = re.search(r"^Page size:\s+(.+)$", info.stdout, re.M)
    javascript = re.search(r"^JavaScript:\s+no$", info.stdout, re.M)
    pages = int(pages_match.group(1)) if pages_match else 0
    checks = {
        "qpdf": syntax.returncode == 0,
        "a4": bool(page_size and "A4" in page_size.group(1)),
        "searchable": len(text.stdout.strip()) >= 120,
        "javascript_absent": bool(javascript),
        "page_count": args.expected_pages is None or pages == args.expected_pages,
    }
    for name, passed in checks.items():
        print(f"{name}: {'PASS' if passed else 'FAIL'}")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
