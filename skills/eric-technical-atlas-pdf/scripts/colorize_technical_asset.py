#!/usr/bin/env python3
"""Apply the Eric technical-atlas navy/steel/copper map to an owned local image."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def parse_mask(value: str) -> tuple[float, float, float, float, float]:
    parts = tuple(float(part) for part in value.split(","))
    if len(parts) != 5 or any(part < 0 or part > 1 for part in parts):
        raise argparse.ArgumentTypeError("mask must be x1,y1,x2,y2,feather with normalized values 0..1")
    return parts


def gradient(gray: np.ndarray, low: np.ndarray, mid: np.ndarray, high: np.ndarray) -> np.ndarray:
    lower = np.clip(gray / 0.52, 0, 1)[..., None]
    upper = np.clip((gray - 0.52) / 0.48, 0, 1)[..., None]
    return np.where((gray < 0.52)[..., None], low + (mid - low) * lower, mid + (high - mid) * upper)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--mask", action="append", type=parse_mask, required=True)
    args = parser.parse_args()
    if not args.input.is_file():
        raise SystemExit(f"missing input: {args.input}")
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite: {args.output}")
    image = Image.open(args.input).convert("RGB")
    rgb = np.asarray(image, dtype=np.float32) / 255.0
    gray = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    steel = gradient(gray, np.array([10, 28, 42]), np.array([102, 116, 126]), np.array([238, 239, 235]))
    copper = gradient(gray, np.array([74, 43, 28]), np.array([166, 103, 58]), np.array([224, 184, 137]))
    combined = Image.new("L", image.size, 0)
    for x1, y1, x2, y2, feather in args.mask:
        mask = Image.new("L", image.size, 0)
        ImageDraw.Draw(mask).rectangle((x1 * image.width, y1 * image.height, x2 * image.width, y2 * image.height), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(max(2, int(min(image.size) * feather))))
        combined = Image.fromarray(np.maximum(np.asarray(combined), np.asarray(mask)).astype(np.uint8))
    alpha = np.clip(np.asarray(combined, dtype=np.float32) / 255.0 * (0.30 + 0.55 * gray), 0, 0.72)[..., None]
    result = steel * (1 - alpha) + copper * alpha
    args.output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.clip(result, 0, 255).astype(np.uint8), "RGB").save(args.output, optimize=True)
    print(args.output)


if __name__ == "__main__":
    main()
