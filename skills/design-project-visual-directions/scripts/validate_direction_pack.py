#!/usr/bin/env python3
"""Validate structure and pairwise diversity of a visual direction pack."""

from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path


REQUIRED_DIRECTION_FIELDS = {
    "id",
    "name",
    "product_truth",
    "thesis",
    "spatial_metaphor",
    "hero_subject",
    "media_strategy",
    "materials",
    "lighting",
    "color_roles",
    "typography",
    "storyboard",
    "interaction",
    "responsive",
    "reduced_motion",
    "content_mapping",
    "states",
    "exclusions",
    "acceptance",
    "prompt_pipeline",
    "transformation_axes",
}
AXES = {"space", "material", "light", "motion", "type", "density", "interaction"}


def normalized(value: object) -> str:
    return " ".join(str(value).lower().split())


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read valid JSON: {exc}"]

    for field in ("schema_version", "project", "delivery_mode", "product_truth", "directions"):
        if not data.get(field):
            errors.append(f"missing top-level field: {field}")

    directions = data.get("directions")
    if not isinstance(directions, list):
        return errors + ["directions must be an array"]
    if not 3 <= len(directions) <= 4:
        errors.append("directions must contain 3 entries by default, or 4 when justified")

    ids: set[str] = set()
    metaphors: set[str] = set()
    valid_directions: list[dict] = []
    for index, direction in enumerate(directions):
        label = f"directions[{index}]"
        if not isinstance(direction, dict):
            errors.append(f"{label} must be an object")
            continue
        missing = sorted(field for field in REQUIRED_DIRECTION_FIELDS if not direction.get(field))
        if missing:
            errors.append(f"{label} missing: {', '.join(missing)}")
        direction_id = normalized(direction.get("id", ""))
        if direction_id in ids:
            errors.append(f"{label} duplicates id: {direction_id}")
        ids.add(direction_id)
        metaphor = normalized(direction.get("spatial_metaphor", ""))
        if metaphor in metaphors:
            errors.append(f"{label} repeats spatial_metaphor")
        metaphors.add(metaphor)

        storyboard = direction.get("storyboard")
        if not isinstance(storyboard, list) or len(storyboard) < 5:
            errors.append(f"{label}.storyboard must contain at least 5 beats")
        axes = direction.get("transformation_axes")
        if not isinstance(axes, dict):
            errors.append(f"{label}.transformation_axes must be an object")
        else:
            missing_axes = sorted(axis for axis in AXES if not axes.get(axis))
            if missing_axes:
                errors.append(f"{label}.transformation_axes missing: {', '.join(missing_axes)}")
        valid_directions.append(direction)

    for left, right in combinations(valid_directions, 2):
        left_axes = left.get("transformation_axes", {})
        right_axes = right.get("transformation_axes", {})
        if not isinstance(left_axes, dict) or not isinstance(right_axes, dict):
            continue
        differences = sum(
            normalized(left_axes.get(axis, "")) != normalized(right_axes.get(axis, ""))
            for axis in AXES
        )
        if differences < 5:
            errors.append(
                f"{left.get('id')} vs {right.get('id')} differ on only "
                f"{differences}/7 axes; require at least 5"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("direction_pack", type=Path)
    args = parser.parse_args()
    errors = validate(args.direction_pack)
    if errors:
        print(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"status": "PASS", "file": str(args.direction_pack)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
