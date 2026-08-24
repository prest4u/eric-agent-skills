#!/usr/bin/env bash
# 青云霜蓝通缘 skill 自检：可发现、4 页、无禁印、无识别册残留、typst 可编译。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILL="$ROOT/SKILL.md"
THEME="$ROOT/theme.typ"
SRC="$ROOT/samples/选科指导报告-小样.typ"
PDF="$ROOT/samples/选科指导报告-小样.pdf"
FAIL=0
warn() { echo "WARN: $*" >&2; }
fail() { echo "FAIL: $*" >&2; FAIL=1; }
pass() { echo "PASS: $*"; }

echo "== eric-qingyun-frost-pdf self-check =="

# 1. skill discoverable
if [[ ! -f "$SKILL" ]]; then
  fail "SKILL.md missing"
else
  name="$(awk 'BEGIN{fm=0} /^---$/{fm++; next} fm==1 && $1=="name:"{sub(/^name:[ ]*/,""); print; exit}' "$SKILL")"
  desc="$(awk 'BEGIN{fm=0} /^---$/{fm++; next} fm==1 && $1=="description:"{sub(/^description:[ ]*/,""); print; exit}' "$SKILL")"
  if [[ "$name" == "eric-qingyun-frost-pdf" && -n "$desc" && ${#desc} -ge 20 ]]; then
    pass "SKILL.md frontmatter discoverable"
  else
    fail "SKILL.md frontmatter invalid (name='$name', desc_len=${#desc})"
  fi
fi

# 2. theme tokens + banned leftovers
if [[ ! -f "$THEME" ]]; then
  fail "theme.typ missing"
else
  for s in "#C5D4E0" "28mm" "Weibei"; do
    if grep -F -- "$s" "$THEME" >/dev/null 2>&1; then
      pass "theme.typ contains $s"
    else
      fail "theme.typ missing required token: $s"
    fi
  done
  HIT_THEME=0
  for s in "#DDE8E4" "#F4F6F5" "rail-head" "mark-square" "top-band"; do
    if grep -F -- "$s" "$THEME" >/dev/null 2>&1; then
      fail "theme.typ contains banned token: $s"
      HIT_THEME=1
    fi
  done
  if [[ "$HIT_THEME" -eq 0 ]]; then
    pass "theme.typ has no #DDE8E4 / #F4F6F5 / rail-head / mark-square / top-band"
  fi
fi

# 3. compile
if ! command -v typst >/dev/null 2>&1; then
  fail "typst not found"
else
  TMPDIR_C="$(mktemp -d -t qingyun-frost)"
  TMP="$TMPDIR_C/sample.pdf"
  if typst compile --root "$ROOT" --format pdf "$SRC" "$TMP"; then
    pass "typst compile --root succeeds"
    cp "$TMP" "$PDF"
  else
    fail "typst compile failed"
  fi
  rm -rf "$TMPDIR_C"
fi

# 4. 4 pages
if [[ ! -f "$PDF" ]]; then
  fail "sample PDF missing: $PDF"
else
  if command -v pdfinfo >/dev/null 2>&1; then
    pages="$(pdfinfo "$PDF" | awk '/^Pages:/{print $2}')"
    if [[ "$pages" == "4" ]]; then
      pass "sample PDF exists and is 4 pages"
    else
      fail "sample PDF page count=$pages, expected 4"
    fi
  else
    warn "pdfinfo not found; skip page-count check"
  fi
fi

# 5. banned brand + chrome labels
if [[ -f "$PDF" ]]; then
  TEXT=""
  if command -v pdftotext >/dev/null 2>&1; then
    TEXT="$(pdftotext -layout "$PDF" - 2>/dev/null || true)"
  fi
  STRINGS=""
  if command -v strings >/dev/null 2>&1; then
    STRINGS="$(strings "$PDF" 2>/dev/null || true)"
  fi
  HAYSTACK="${TEXT}
${STRINGS}"
  HIT=0
  for s in "青云知路" "青云志愿"; do
    if printf '%s' "$HAYSTACK" | grep -F -- "$s" >/dev/null 2>&1; then
      fail "banned brand string present: $s"
      HIT=1
    fi
  done
  if [[ "$HIT" -eq 0 ]]; then
    pass "no banned brand strings in pdftotext/strings"
  fi
  CHROME=0
  if printf '%s' "$TEXT" | grep -E -- '(^|[^A-Za-z])DOCUMENT([^A-Za-z]|$)' >/dev/null 2>&1; then
    fail "PDF text contains DOCUMENT chrome label"
    CHROME=1
  fi
  if printf '%s' "$TEXT" | grep -E -- '(^|[^A-Za-z])STATUS([^A-Za-z]|$)' >/dev/null 2>&1; then
    fail "PDF text contains STATUS chrome label"
    CHROME=1
  fi
  if [[ "$CHROME" -eq 0 ]]; then
    pass "no DOCUMENT / STATUS chrome labels in PDF text"
  fi
  if ! printf '%s' "$TEXT" | grep -F -- "青云" >/dev/null 2>&1; then
    warn "extracted text does not contain 青云 (font/encoding?)"
  fi
fi

if [[ "$FAIL" -ne 0 ]]; then
  echo "== RESULT: FAIL =="
  exit 1
fi
echo "== RESULT: PASS =="
