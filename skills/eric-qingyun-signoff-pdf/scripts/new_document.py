#!/usr/bin/env python3
"""Scaffold a Qingyun Typst project from the shared theme and a scene skeleton."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

SCENES = ("signoff",)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scene", required=True, choices=SCENES)
    parser.add_argument("--out", required=True, help="Fresh output directory")
    parser.add_argument("--title", required=True)
    parser.add_argument("--case-id", default="案例合成-TJ2026-0042")
    parser.add_argument("--alias", default="林同")
    parser.add_argument("--province", default="天津")
    parser.add_argument("--year", default="2026")
    parser.add_argument("--batch", default="本科批")
    parser.add_argument("--version", default="V1")
    parser.add_argument("--date", default="2026-08-18")
    args = parser.parse_args()
    if args.batch == "本科批":
        args.batch = {
            "subject": "选科",
            "early-bird": "早鸟",
            "teacher": "转介",
            "service-brief": "选科",
            "consent": "选科",
            "profile": "选科",
        }.get(args.scene, args.batch)

    skill_root = Path(__file__).resolve().parents[1]
    output_dir = Path(args.out).expanduser().resolve()
    if not args.title.strip():
        raise SystemExit("Document title must not be empty")
    if output_dir.exists():
        raise SystemExit(f"Refusing to overwrite existing path: {output_dir}")

    protected_roots = (
        Path.home() / ".codex" / "skills",
        Path.home() / ".agents" / "skills",
        Path.home() / ".claude" / "skills",
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

    theme = skill_root / "assets" / "theme.typ"
    skeleton = skill_root / "assets" / "skeletons" / f"{args.scene}.typ"
    if not theme.is_file() or not skeleton.is_file():
        raise SystemExit(f"Missing theme or skeleton: {theme} / {skeleton}")

    source = skeleton.read_text(encoding="utf-8")
    replacements = {
        "__TITLE__": args.title,
        "__CASE_ID__": args.case_id,
        "__ALIAS__": args.alias,
        "__PROVINCE__": args.province,
        "__YEAR__": args.year,
        "__BATCH__": args.batch,
        "__VERSION__": args.version,
        "__DATE__": args.date,
    }
    for key, value in replacements.items():
        source = source.replace(key, value)
    if "__" in source and any(token in source for token in replacements):
        raise SystemExit("Unresolved skeleton placeholder")

    output_dir.mkdir(parents=True)
    shutil.copyfile(theme, output_dir / "theme.typ")
    output_file = output_dir / "document.typ"
    output_file.write_text(source, encoding="utf-8")
    print(output_file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
