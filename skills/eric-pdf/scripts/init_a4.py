#!/usr/bin/env python3
"""Copy the bundled Eric A4 Typst starter to a fresh destination."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
STARTER = SKILL_ROOT / "assets" / "eric-a4-starter.typ"


def initialize(destination: Path) -> Path:
    destination = destination.expanduser().resolve()
    if destination.suffix.lower() != ".typ":
        raise ValueError("destination must end with .typ")
    if destination == STARTER.resolve():
        raise ValueError("destination must not replace the bundled starter")
    if destination.is_symlink() or destination.exists():
        raise FileExistsError(f"refusing to overwrite existing destination: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(STARTER, destination)
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    try:
        print(initialize(args.destination))
    except (FileNotFoundError, FileExistsError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
