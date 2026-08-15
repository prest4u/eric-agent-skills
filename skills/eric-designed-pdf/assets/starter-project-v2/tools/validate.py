#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

import fitz
import yaml
from bs4 import BeautifulSoup
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
QA = ROOT / "_qa"
BOOK = ROOT / "book.yaml"

REQUIRED_TEMPLATES = {
    "cover",
    "title",
    "unit-opener",
    "elements",
    "activity",
    "paragraph-practice",
    "photo-passage",
    "writing-planner",
    "handbook",
    "answer-key",
}

REQUIRED_COMPONENTS = {
    "cover",
    "cover-brand",
    "title-page",
    "unit-opener",
    "objectives-band",
    "elements-page",
    "activity-block",
    "word-box",
    "words-to-know",
    "paragraph-practice",
    "photo-passage",
    "mechanics-table",
    "writing-planner",
    "editing-checklist",
    "handbook-page",
    "answer-key-page",
}

FORBIDDEN_VISIBLE = [
    "/Users",
    "National Geographic",
    "Great Writing",
    "NGL",
    "source_id",
    "validator",
    "placeholder",
    "TODO",
    "draft",
    "MBTI",
    "挖坑",
    "心法",
    "出招",
    "拆招",
    "定招",
    "教师动作",
    "预期回应",
    "教师话术",
    "后台",
    "路由",
    "维修层",
    "短程维修",
    "动作链",
    "主动作",
    "闭环",
    "天津高考英语一轮复习",
    "22讲",
    "Student workbook and A4 lesson pack",
    "book-trim",
]

# Keep these terms assembled so source-residue scans do not flag this detector vocabulary.
STARTER_SAMPLE_TITLE = "Pathways" + " to Better Writing"
STARTER_RESIDUE_TERMS = [
    "Pathways" + " to Better Writing",
    "English Writing" + " System",
    "Sentences, Paragraphs," + " and Writing Practice",
    "A Good Place" + " to Observe",
    "The Best Place" + " to Think",
    "canyon" + "-cover",
]
SOURCE_SCAN_PATHS = [
    "book.yaml",
    "assets/manifest.json",
    "theme/tokens.json",
    "tools/build.py",
    "tools/validate.py",
    "typst-adapter/lesson-a4-template.typ",
]
SOURCE_SCAN_GLOBS = ["pages/*.md", "typst-adapter/*.typ"]
COVER_BRAND_NAME = "Eric Teaching Studio"


def run(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return proc.returncode, proc.stdout


def load_book() -> dict:
    return yaml.safe_load(BOOK.read_text(encoding="utf-8"))


def configured_output_path(book: dict, profile: str, kind: str) -> Path:
    spec = book.get("profiles", {}).get(profile, {})
    nested = spec.get("outputs") or {}
    configured = spec.get(f"output_{kind}") or nested.get(kind)
    if configured:
        path = Path(configured)
        return path if path.is_absolute() else ROOT / path
    return OUT / f"textbook-template-sample-{profile}.{kind}"


def as_set(value: object, default: set[str]) -> set[str]:
    if value is None:
        return set(default)
    if isinstance(value, str):
        return {item.strip() for item in value.split(",") if item.strip()}
    return {str(item).strip() for item in value if str(item).strip()}


def profile_qa_config(book: dict, spec: dict) -> dict:
    qa = book.get("qa") or {}
    profile_qa = spec.get("qa") or {}
    return {
        "min_pages": profile_qa.get("min_pages") or qa.get("min_pages") or 8,
        "max_pages": profile_qa.get("max_pages") or qa.get("max_pages") or 12,
        "required_templates": as_set(profile_qa.get("required_templates") or qa.get("required_templates"), REQUIRED_TEMPLATES),
        "required_components": as_set(profile_qa.get("required_components") or qa.get("required_components"), REQUIRED_COMPONENTS),
    }


def is_starter_sample(book: dict, spec: dict) -> bool:
    qa = book.get("qa") or {}
    profile_qa = spec.get("qa") or {}
    if qa.get("allow_starter_residue") or profile_qa.get("allow_starter_residue"):
        return True
    return str(book.get("title") or "").strip().casefold() == STARTER_SAMPLE_TITLE.casefold()


def page_file_from_item(item: object) -> str | None:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        value = item.get("file") or item.get("path")
        return str(value) if value else None
    return None


def active_page_source_files(book: dict) -> set[Path]:
    files: set[Path] = set()
    for item in book.get("pages") or []:
        rel_path = page_file_from_item(item)
        if not rel_path:
            continue
        path = Path(rel_path)
        resolved = path if path.is_absolute() else ROOT / path
        if resolved.exists() and resolved.is_file():
            files.add(resolved.resolve())
    return files


def scanned_source_paths(book: dict | None = None) -> list[Path]:
    paths: list[Path] = []
    for rel_path in SOURCE_SCAN_PATHS:
        path = ROOT / rel_path
        if path.exists() and path.is_file():
            paths.append(path)
    active_pages = active_page_source_files(book) if book else set()
    for pattern in SOURCE_SCAN_GLOBS:
        if pattern == "pages/*.md" and active_pages:
            paths.extend(sorted(active_pages))
            continue
        paths.extend(path for path in sorted(ROOT.glob(pattern)) if path.is_file())
    return sorted(set(paths))


def starter_residue_hits(book: dict, spec: dict, visible_text: str, extracted_text: str) -> dict:
    if is_starter_sample(book, spec):
        return {}
    sources: list[tuple[str, str]] = [("visible-output", visible_text + "\n" + extracted_text)]
    for path in scanned_source_paths(book):
        try:
            label = str(path.relative_to(ROOT))
            sources.append((label, path.read_text(encoding="utf-8", errors="replace")))
        except OSError:
            continue
    hits: dict[str, list[dict]] = {}
    for term in STARTER_RESIDUE_TERMS:
        for label, text in sources:
            count = text.count(term)
            if count:
                hits.setdefault(term, []).append({"file": label, "count": count})
    return {term: {"total": sum(item["count"] for item in rows), "locations": rows[:8]} for term, rows in hits.items()}


def html_text(path: Path) -> tuple[str, BeautifulSoup]:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    for tag in soup(["style", "script"]):
        tag.decompose()
    text = re.sub(r"\s+", " ", soup.get_text(" ")).strip()
    return text, soup


def cover_brand_checks(soup: BeautifulSoup, book: dict) -> dict:
    cover = soup.select_one('.sheet[data-template="cover"], .template-cover')
    cover_text = re.sub(r"\s+", " ", cover.get_text(" ") if cover else "").strip()
    cover_top = cover.select_one(".cover-top") if cover else None
    cover_top_text = re.sub(r"\s+", " ", cover_top.get_text(" ") if cover_top else "").strip()
    level = str(book.get("level") or "").strip()
    checks = {
        "brand_text_present": COVER_BRAND_NAME in cover_text,
        "cover_brand_node_present": bool(cover and cover.select_one(".cover-brand")),
        "cover_top_level_badge_absent": not bool(level and level in cover_top_text),
    }
    return {"ok": all(checks.values()), "checks": checks, "cover_top_text": cover_top_text}


def page_asset_refs(book: dict) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for rel_page in book.get("pages") or []:
        page_path = ROOT / str(rel_page)
        try:
            raw = page_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        match = re.match(r"^---\n(.*?)\n---\n?", raw, flags=re.S)
        if not match:
            continue
        meta = yaml.safe_load(match.group(1)) or {}
        if meta.get("asset"):
            refs.append(
                {
                    "id": str(meta["asset"]),
                    "page": str(rel_page),
                    "template": str(meta.get("template") or ""),
                    "section": str(meta.get("section") or ""),
                }
            )
    return refs


def asset_usage_checks(assets: list[dict], refs: list[dict[str, str]]) -> dict:
    path_to_ids: dict[str, list[str]] = {}
    for asset in assets:
        path_to_ids.setdefault(str(asset.get("path") or ""), []).append(str(asset.get("id") or ""))
    duplicate_paths = {path: sorted(set(ids)) for path, ids in path_to_ids.items() if path and len(set(ids)) > 1}
    refs_by_id: dict[str, list[dict[str, str]]] = {}
    for ref in refs:
        refs_by_id.setdefault(ref["id"], []).append(ref)
    reused_refs = {asset_id: rows for asset_id, rows in refs_by_id.items() if len(rows) > 1}
    assets_by_id = {str(asset.get("id") or ""): asset for asset in assets}
    cover_inside = []
    template_mismatch = []
    for asset_id, rows in refs_by_id.items():
        asset = assets_by_id.get(asset_id, {})
        role = " ".join(str(asset.get(key) or "") for key in ("role", "purpose", "use_role")).lower()
        allowed = asset.get("allowed_templates") or []
        if isinstance(allowed, str):
            allowed = [item.strip() for item in allowed.split(",") if item.strip()]
        if ("cover" in role or "hero" in role) and not allowed:
            allowed = ["cover"]
        for ref in rows:
            if ("cover" in role or "hero" in role) and ref["template"] != "cover":
                cover_inside.append(ref)
            if allowed and ref["template"] not in allowed:
                template_mismatch.append({"id": asset_id, "template": ref["template"], "allowed_templates": allowed})
    checks = {
        "manifest_paths_unique": not duplicate_paths,
        "asset_refs_single_use": not reused_refs,
        "cover_assets_not_used_inside": not cover_inside,
        "asset_refs_match_allowed_templates": not template_mismatch,
    }
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "duplicate_paths": duplicate_paths,
        "reused_refs": reused_refs,
        "cover_inside": cover_inside,
        "template_mismatch": template_mismatch,
    }


def pdf_text(path: Path) -> str:
    code, out = run(["pdftotext", str(path), "-"])
    if code != 0:
        raise RuntimeError(out)
    return out


def exam_stem_slot_policy(soup: BeautifulSoup, raw_html: str) -> dict:
    generic_blank_hits = []
    for section in soup.select(".sheet"):
        page = section.get("data-page")
        for prompt in section.select(".guided-mcq-set p"):
            if prompt.select(".blank"):
                generic_blank_hits.append(
                    {
                        "page": page,
                        "text": re.sub(r"\s+", " ", prompt.get_text(" ")).strip()[:140],
                    }
                )
    css_ok = ".exam-stem-slot" in raw_html and ".exam-stem-keep" in raw_html
    return {
        "ok": not generic_blank_hits and css_ok,
        "generic_blank_hits": generic_blank_hits,
        "css_contract_present": css_ok,
        "required": "Guided MCQ/cloze stems must render author ____ as .exam-stem-slot, never as generic .blank.",
    }


def a4_sentence_map_surface_policy(soup: BeautifulSoup, profile: str) -> dict:
    checked = "a4" in profile.lower()
    if not checked:
        return {"ok": True, "checked": False, "wide_table_hits": [], "missing_card_stack": []}
    wide_table_hits = []
    missing_card_stack = []
    for section in soup.select('.sheet[data-template="sentence-map"]'):
        page = section.get("data-page")
        stack = section.select_one('.sentence-map-card-stack[data-surface-family="sentence-map"][data-surface]')
        if not stack:
            missing_card_stack.append({"page": page})
        if section.select(".textbook-table"):
            wide_table_hits.append({"page": page})
    return {
        "ok": not wide_table_hits and not missing_card_stack,
        "checked": True,
        "wide_table_hits": wide_table_hits,
        "missing_card_stack": missing_card_stack,
        "required": "A4 sentence-map pages must use .sentence-map-card-stack with data-surface markers, not a wide textbook table.",
    }


def a4_only_profile_policy(book: dict, raw_html: str = "") -> dict:
    output_mode = str((book.get("qa") or {}).get("output_mode") or "").strip().lower()
    checked = output_mode == "a4-only"
    if not checked:
        return {"ok": True, "checked": False, "profile_hits": [], "output_hits": [], "html_hits": []}
    profile_hits = [name for name in (book.get("profiles") or {}) if "book-trim" in name]
    output_hits = []
    for name, spec in (book.get("profiles") or {}).items():
        outputs = [spec.get("output_html"), spec.get("output_pdf")]
        nested = spec.get("outputs") if isinstance(spec.get("outputs"), dict) else {}
        outputs.extend(nested.values())
        for output in outputs:
            if output and "book-trim" in str(output):
                output_hits.append({"profile": name, "output": str(output)})
    html_hits = []
    if "book-trim" in raw_html:
        html_hits.append("book-trim")
    return {
        "ok": not profile_hits and not output_hits and not html_hits,
        "checked": True,
        "profile_hits": profile_hits,
        "output_hits": output_hits,
        "html_hits": html_hits,
        "required": "qa.output_mode: a4-only may expose only A4 profiles, A4 output names, and A4-only rendered HTML.",
    }


def validate(profile: str) -> dict:
    book = load_book()
    spec = book["profiles"][profile]
    qa_config = profile_qa_config(book, spec)
    html_path = configured_output_path(book, profile, "html")
    pdf_path = configured_output_path(book, profile, "pdf")
    failures: list[str] = []
    details: dict = {
        "profile": profile,
        "html": str(html_path.relative_to(ROOT)) if html_path.exists() else str(html_path),
        "pdf": str(pdf_path.relative_to(ROOT)) if pdf_path.exists() else str(pdf_path),
    }

    if not html_path.exists():
        failures.append("html missing")
        return {"status": "fail", "failures": failures, "details": details}
    if not pdf_path.exists():
        failures.append("pdf missing")
        return {"status": "fail", "failures": failures, "details": details}

    raw_html = html_path.read_text(encoding="utf-8", errors="replace")
    visible_html, soup = html_text(html_path)
    template_counts = Counter(section.get("data-template") for section in soup.select(".sheet"))
    component_counts = Counter(node.get("data-component") for node in soup.select("[data-component]"))
    details["template_counts"] = dict(template_counts)
    details["component_counts"] = dict(component_counts)
    a4_only = a4_only_profile_policy(book, raw_html)
    details["a4_only_profile_policy"] = a4_only
    if not a4_only["ok"]:
        failures.append(f"a4-only profile residue: {a4_only}")
    exam_stems = exam_stem_slot_policy(soup, raw_html)
    details["exam_stem_slot_policy"] = exam_stems
    if not exam_stems["ok"]:
        failures.append(f"exam stem slot drift: {exam_stems}")
    sentence_map_surface = a4_sentence_map_surface_policy(soup, profile)
    details["a4_sentence_map_surface_policy"] = sentence_map_surface
    if not sentence_map_surface["ok"]:
        failures.append(f"A4 sentence-map table cramp risk: {sentence_map_surface}")
    duplicated_question_blanks = []
    for section in soup.select(".sheet"):
        page = section.get("data-page")
        for item in section.select(".question-lines li"):
            if item.select(".blank") and item.select(".write-line"):
                duplicated_question_blanks.append(
                    {
                        "page": page,
                        "text": re.sub(r"\s+", " ", item.get_text(" ")).strip()[:120],
                    }
                )
    details["duplicated_question_blanks"] = duplicated_question_blanks
    if duplicated_question_blanks:
        failures.append(f"question prompt has inline blank plus writing line: {duplicated_question_blanks[:5]}")
    missing_templates = sorted(qa_config["required_templates"] - set(template_counts))
    missing_components = sorted(qa_config["required_components"] - set(component_counts))
    if missing_templates:
        failures.append(f"missing templates: {missing_templates}")
    if missing_components:
        failures.append(f"missing components: {missing_components}")
    cover_brand = cover_brand_checks(soup, book)
    details["cover_brand"] = cover_brand
    if not cover_brand["ok"]:
        failures.append(f"cover brand/stage placement failed: {cover_brand}")

    text = pdf_text(pdf_path)
    details["pdf_text_chars"] = len(text.strip())
    if len(text.strip()) < 1200:
        failures.append("pdf text extraction too short")

    combined_visible = visible_html + "\n" + text
    hits = {}
    for term in FORBIDDEN_VISIBLE:
        if re.fullmatch(r"[A-Za-z0-9_ ]+", term):
            pattern = r"(?<![A-Za-z0-9_])" + re.escape(term) + r"(?![A-Za-z0-9_])"
            count = len(re.findall(pattern, combined_visible))
        else:
            count = combined_visible.count(term)
        if count:
            hits[term] = count
    details["forbidden_hits"] = hits
    if hits:
        failures.append(f"forbidden visible terms: {hits}")

    starter_hits = starter_residue_hits(book, spec, visible_html, text)
    details["starter_residue_hits"] = starter_hits
    if starter_hits:
        failures.append(f"starter residue found: {starter_hits}")

    with fitz.open(pdf_path) as doc:
        details["page_count"] = doc.page_count
        if not (int(qa_config["min_pages"]) <= doc.page_count <= int(qa_config["max_pages"])):
            failures.append(f"page count outside {qa_config['min_pages']}-{qa_config['max_pages']}: {doc.page_count}")
        size_failures = []
        blank_pages = []
        for i, page in enumerate(doc, 1):
            w = round(page.rect.width, 2)
            h = round(page.rect.height, 2)
            if abs(w - float(spec["page_width_pt"])) > 2 or abs(h - float(spec["page_height_pt"])) > 2:
                size_failures.append([i, w, h])
            if len(page.get_text().strip()) < 5 and len(page.get_images(full=True)) == 0:
                blank_pages.append(i)
        details["size_failures"] = size_failures
        details["blank_pages"] = blank_pages
        if size_failures:
            failures.append(f"page size mismatch: {size_failures[:4]}")
        if blank_pages:
            failures.append(f"blank pages: {blank_pages}")

    assets = json.loads((ROOT / "assets" / "manifest.json").read_text(encoding="utf-8"))["assets"]
    asset_refs = page_asset_refs(book)
    usage = asset_usage_checks(assets, asset_refs)
    details["asset_refs"] = asset_refs
    details["asset_usage"] = usage
    if not usage["ok"]:
        failures.append(f"asset usage failed: {usage}")
    asset_issues = []
    asset_details = []
    for asset in assets:
        path = ROOT / asset["path"]
        if not path.exists():
            asset_issues.append(f"missing asset: {asset['path']}")
            continue
        with Image.open(path) as im:
            meta = {"id": asset["id"], "width": im.width, "height": im.height, "mode": im.mode}
            asset_details.append(meta)
            if min(im.width, im.height) < 800:
                asset_issues.append(f"asset too small: {asset['path']} {im.width}x{im.height}")
    details["assets"] = asset_details
    if asset_issues:
        failures.extend(asset_issues)

    overflow_path = QA / f"layout-overflow-{profile}.json"
    if not overflow_path.exists():
        failures.append("layout overflow report missing")
    else:
        rows = json.loads(overflow_path.read_text(encoding="utf-8"))
        overflows = [row for row in rows if row.get("verticalOverflow", 0) > 2 or row.get("horizontalOverflow", 0) > 2]
        details["layout_rows_checked"] = len(rows)
        details["layout_overflows"] = overflows
        if overflows:
            failures.append(f"layout overflow: {overflows[:5]}")

    contact = QA / f"contact-sheet-{profile}.png"
    details["contact_sheet"] = str(contact.relative_to(ROOT)) if contact.exists() else str(contact)
    if not contact.exists():
        failures.append("contact sheet missing")

    status = "pass" if not failures else "fail"
    return {"status": status, "failures": failures, "details": details}


def write_report(profile: str, report: dict) -> None:
    QA.mkdir(exist_ok=True)
    json_path = QA / f"validator-report-{profile}.json"
    md_path = QA / f"validator-report-{profile}.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    details = report["details"]
    failures = "\n".join(f"- {item}" for item in report["failures"]) or "- None"
    md = f"""# Textbook Template Validator - {profile}

- Status: **{report['status']}**
- Pages: {details.get('page_count')}
- PDF text chars: {details.get('pdf_text_chars')}
- Templates: {details.get('template_counts')}
- Components: {details.get('component_counts')}
- Contact sheet: `{details.get('contact_sheet')}`

## Failures

{failures}
"""
    md_path.write_text(md, encoding="utf-8")
    print(md_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="book-trim")
    args = parser.parse_args()
    report = validate(args.profile)
    write_report(args.profile, report)
    if report["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
