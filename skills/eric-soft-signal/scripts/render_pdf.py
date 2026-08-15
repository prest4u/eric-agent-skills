#!/usr/bin/env python3
"""Render every page of a PDF and create a deterministic contact sheet."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw


PAGE_NAME = re.compile(r"page-(\d+)\.png$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def page_number(path: Path) -> int:
    match = PAGE_NAME.fullmatch(path.name)
    if match is None:
        raise ValueError(f"Unexpected render name: {path.name}")
    return int(match.group(1))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render every PDF page to PNG and create a contact sheet."
    )
    parser.add_argument("pdf", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--dpi", type=int, default=170)
    args = parser.parse_args()

    pdf = args.pdf.resolve()
    output_dir = args.output_dir.resolve()
    if not pdf.is_file():
        parser.error(f"PDF does not exist: {pdf}")
    if args.dpi <= 0:
        parser.error("--dpi must be positive")
    if shutil.which("pdftoppm") is None:
        parser.error("pdftoppm is required")

    output_dir.mkdir(parents=True, exist_ok=True)
    existing = sorted(output_dir.glob("page-*.png"))
    contact = output_dir / "contact-sheet.png"
    if existing or contact.exists():
        parser.error("output directory already contains render output")

    prefix = output_dir / "page"
    render = subprocess.run(
        ["pdftoppm", "-png", "-r", str(args.dpi), str(pdf), str(prefix)],
        check=False,
        capture_output=True,
        text=True,
    )
    if render.returncode != 0:
        sys.stderr.write(render.stderr)
        return render.returncode

    pages = sorted(output_dir.glob("page-*.png"), key=page_number)
    if not pages:
        sys.stderr.write("pdftoppm produced no pages\n")
        return 1

    thumbnails: list[Image.Image] = []
    page_metadata: list[dict[str, int | str]] = []
    tile_width = 320
    tile_height = 0
    for page in pages:
        with Image.open(page) as rendered:
            width, height = rendered.size
            page_metadata.append(
                {
                    "file": page.name,
                    "height": height,
                    "sha256": sha256(page),
                    "width": width,
                }
            )
            thumb_height = round(height * tile_width / width)
            thumbnail = rendered.convert("RGB").resize((tile_width, thumb_height))
            thumbnails.append(thumbnail)
            tile_height = max(tile_height, thumb_height + 26)

    columns = min(4, len(thumbnails))
    rows = (len(thumbnails) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * (tile_width + 20) + 20, rows * (tile_height + 20) + 20), "white")
    draw = ImageDraw.Draw(sheet)
    for index, thumbnail in enumerate(thumbnails):
        column = index % columns
        row = index // columns
        x = 20 + column * (tile_width + 20)
        y = 20 + row * (tile_height + 20)
        sheet.paste(thumbnail, (x, y))
        draw.rectangle((x - 1, y - 1, x + tile_width, y + thumbnail.height), outline="#71675f", width=1)
        draw.text((x, y + thumbnail.height + 5), f"Page {index + 1}", fill="#211b17")
    sheet.save(contact, format="PNG", optimize=False)

    print(
        json.dumps(
            {
                "contact_sheet": {"file": contact.name, "sha256": sha256(contact)},
                "input_pdf": {"sha256": sha256(pdf)},
                "page_count": len(pages),
                "pages": page_metadata,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
