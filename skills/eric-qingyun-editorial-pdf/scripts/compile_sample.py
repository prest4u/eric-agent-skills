#!/usr/bin/env python3
"""Compile the bundled 4-page 选科指导报告 sample with local typst."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "samples" / "document.typ"
OUT = ROOT / "samples" / "document.pdf"


def main() -> int:
    typst = shutil.which("typst")
    if typst is None:
        raise SystemExit("typst not found on PATH")
    if not SAMPLE.is_file():
        raise SystemExit(f"sample source missing: {SAMPLE}")
    completed = subprocess.run(
        [typst, "compile", "--root", str(ROOT), str(SAMPLE), str(OUT)],
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit(f"typst compile failed with exit {completed.returncode}")
    print(f"compiled {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
