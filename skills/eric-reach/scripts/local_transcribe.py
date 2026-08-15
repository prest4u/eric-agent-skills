#!/usr/bin/env python3
"""Offline-only adapter for the separately installed, pinned MLX Whisper runtime."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys


def fail(message: str, code: int = 2) -> int:
    print(json.dumps({"status": "unavailable", "error": message}, ensure_ascii=False))
    return code


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("audio")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    locked = config["asr"]
    audio = Path(args.audio).resolve()
    model_dir = Path(locked["model_dir"]).expanduser().resolve()
    marker = model_dir / locked["revision_marker"]

    if not audio.is_file():
        return fail("audio input is missing")
    if not model_dir.is_dir():
        return fail("pinned local MLX model is missing; runtime never downloads models")
    if not marker.is_file() or marker.read_text(encoding="utf-8").strip() != locked["model_revision"]:
        return fail("local MLX model revision marker is missing or does not match the lock")
    for filename, expected_hash in locked.get("required_files", {}).items():
        target = model_dir / filename
        if not target.is_file():
            return fail(f"required pinned model file is missing: {filename}")
        digest = sha256_file(target)
        if digest != expected_hash:
            return fail(f"required pinned model file hash mismatch: {filename}")
    try:
        version = importlib.metadata.version(locked["package"])
    except importlib.metadata.PackageNotFoundError:
        return fail("mlx-whisper is not installed in the isolated runtime")
    if version != locked["version"]:
        return fail(f"mlx-whisper version mismatch: expected {locked['version']}, found {version}")

    # Enforce offline behavior before importing libraries that know about HF Hub.
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    os.environ["DO_NOT_TRACK"] = "1"

    try:
        import mlx_whisper  # type: ignore

        result = mlx_whisper.transcribe(str(audio), path_or_hf_repo=str(model_dir))
    except Exception as exc:  # runtime error is data; keep it bounded and local
        return fail(f"local MLX transcription failed: {type(exc).__name__}: {str(exc)[:300]}")

    segments = []
    for raw in result.get("segments", []):
        text = str(raw.get("text", "")).strip()
        if text:
            segments.append(
                {
                    "start": float(raw.get("start", 0.0)),
                    "end": float(raw.get("end", raw.get("start", 0.0))),
                    "text": text,
                }
            )
    print(
        json.dumps(
            {
                "status": "ok",
                "language": result.get("language"),
                "segments": segments,
                "model_revision": locked["model_revision"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
