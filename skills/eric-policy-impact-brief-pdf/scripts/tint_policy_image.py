#!/usr/bin/env python3
"""Apply a deterministic three-stop civic colour grade to a monochrome image."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageEnhance


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.removeprefix("#")
    if len(value) != 6:
        raise argparse.ArgumentTypeError("colours must use six-digit hex notation")
    try:
        return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("invalid hex colour") from exc


def mix(a: tuple[int, int, int], b: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return tuple(round(x + (y - x) * amount) for x, y in zip(a, b, strict=True))


def grade_pixel(
    gray: int,
    shadow: tuple[int, int, int],
    midtone: tuple[int, int, int],
    highlight: tuple[int, int, int],
) -> tuple[int, int, int]:
    if gray <= 128:
        return mix(shadow, midtone, gray / 128)
    return mix(midtone, highlight, (gray - 128) / 127)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--shadow", type=hex_rgb, required=True)
    parser.add_argument("--midtone", type=hex_rgb, required=True)
    parser.add_argument("--highlight", type=hex_rgb, required=True)
    parser.add_argument("--contrast", type=float, default=1.04)
    args = parser.parse_args()

    source = Path(args.input).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing output: {output}")

    with Image.open(source) as image:
        gray = ImageEnhance.Contrast(image.convert("L")).enhance(args.contrast)
        lut = [grade_pixel(value, args.shadow, args.midtone, args.highlight) for value in range(256)]
        red = gray.point([item[0] for item in lut])
        green = gray.point([item[1] for item in lut])
        blue = gray.point([item[2] for item in lut])
        result = Image.merge("RGB", (red, green, blue))
        output.parent.mkdir(parents=True, exist_ok=True)
        result.save(output, format="PNG", optimize=True)

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
