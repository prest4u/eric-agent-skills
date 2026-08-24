#!/usr/bin/env bash
# 编译青云霜蓝通缘选科指导报告小样。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/samples/选科指导报告-小样.typ"
OUT="$ROOT/samples/选科指导报告-小样.pdf"

if ! command -v typst >/dev/null 2>&1; then
  echo "FAIL: typst not found" >&2
  exit 1
fi

typst compile --root "$ROOT" "$SRC" "$OUT"
echo "compiled: $OUT"
