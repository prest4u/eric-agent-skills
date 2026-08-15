#!/usr/bin/env python3
"""Create a fresh Eric editorial Typst project from the bundled starter."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, help="Fresh output directory")
    parser.add_argument("--title", required=True)
    parser.add_argument("--subtitle", default="")
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parents[1]
    output_dir = Path(args.out).expanduser().resolve()

    if not args.title.strip():
        raise SystemExit("Document title must not be empty")
    if output_dir.exists():
        raise SystemExit(f"Refusing to overwrite existing path: {output_dir}")
    protected_roots = (
        Path.home() / ".codex" / "skills",
        Path.home() / ".agents" / "skills",
        Path.home() / ".codex" / "plugins",
        skill_root,
    )
    for protected_root in protected_roots:
        try:
            output_dir.relative_to(protected_root.resolve())
        except ValueError:
            continue
        raise SystemExit(
            f"Refusing to create a document inside a skill/plugin package: {output_dir}"
        )

    starter = skill_root / "assets" / "starter.typ"
    if not starter.is_file():
        raise SystemExit(f"Missing starter asset: {starter}")

    source = starter.read_text(encoding="utf-8")
    source = source.replace(
        "__DOCUMENT_TITLE_JSON__", json.dumps(args.title, ensure_ascii=False)
    )
    source = source.replace(
        "__DOCUMENT_SUBTITLE_JSON__", json.dumps(args.subtitle, ensure_ascii=False)
    )
    if "__DOCUMENT_" in source:
        raise SystemExit("Unresolved starter placeholder")

    output_dir.mkdir(parents=True)
    output_file = output_dir / "document.typ"
    output_file.write_text(source, encoding="utf-8")
    print(output_file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
