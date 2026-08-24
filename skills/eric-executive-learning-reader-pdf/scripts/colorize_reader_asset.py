#!/usr/bin/env python3
"""Map an owned grayscale image through an ordered print-safe colour palette."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps


def parse_stops(raw: str) -> list[tuple[int, tuple[int, int, int]]]:
    stops: list[tuple[int, tuple[int, int, int]]] = []
    for item in raw.split(","):
        level_text, hex_text = item.split(":", 1)
        level = int(level_text)
        value = hex_text.strip().lstrip("#")
        if not 0 <= level <= 255 or len(value) != 6:
            raise ValueError(f"invalid stop: {item}")
        colour = tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))
        stops.append((level, colour))
    stops.sort(key=lambda entry: entry[0])
    if stops[0][0] != 0 or stops[-1][0] != 255:
        raise ValueError("stops must begin at 0 and end at 255")
    if any(left[0] == right[0] for left, right in zip(stops, stops[1:])):
        raise ValueError("stop levels must be unique")
    return stops


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--stops", required=True, help="e.g. 0:14213D,110:5B1E2D,205:B08A57,255:FBFAF7")
    args = parser.parse_args()

    source = Path(args.input).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"missing input: {source}")
    if output.exists():
        raise SystemExit(f"refusing to overwrite: {output}")
    if source == output:
        raise SystemExit("input and output must differ")

    stops = parse_stops(args.stops)
    gray = np.asarray(ImageOps.autocontrast(Image.open(source).convert("L")), dtype=np.float32)
    levels = np.array([entry[0] for entry in stops], dtype=np.float32)
    channels = []
    for channel_index in range(3):
        values = np.array([entry[1][channel_index] for entry in stops], dtype=np.float32)
        channels.append(np.interp(gray, levels, values))
    rgb = np.stack(channels, axis=-1).clip(0, 255).astype(np.uint8)

    output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgb, mode="RGB").save(output, optimize=True)
    print(f"input_sha256={sha256(source)}")
    print(f"output_sha256={sha256(output)}")
    print(f"dimensions={rgb.shape[1]}x{rgb.shape[0]}")


if __name__ == "__main__":
    main()
