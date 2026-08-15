#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
import json
import re
import subprocess
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import fitz
import yaml
from bs4 import BeautifulSoup
from PIL import Image


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
    "workbook-practice",
    "paragraph-practice",
    "photo-passage",
    "mechanics-table",
    "writing-planner",
    "editing-checklist",
    "handbook-page",
    "answer-key-page",
}

V2_PAGE_FAMILY_REQUIREMENTS = {
    "front-matter": {
        "contents-route",
        "diagnostic-entry",
    },
    "unit-opening": {
        "unit-opener",
        "article-opener",
        "article-evidence",
    },
    "teaching-core": {
        "skill-method",
        "sentence-map",
    },
    "practice": {
        "activity",
        "categorizing-chart",
        "exam-mini-set",
    },
    "reading-transfer": {
        "photo-passage",
        "article-evidence",
    },
    "writing-output": {
        "writing-planner",
        "correction-rewrite",
        "final-check",
    },
    "back-matter": {
        "handbook",
        "vocab-bank",
    },
}
V2_PAGE_FAMILY_ALTERNATIVES = {
    "back-matter": [
        {"answer-key", "teacher-answer-key", "teacher-guide-page"},
    ],
}
V2_PAGE_FAMILY_MODES = {"v2-full", "full-coverage-v2", "v2", "student-book", "teacher-book"}
ANSWER_VISIBILITY_MODES = {"off", "student", "student-with-answer-key", "teacher"}

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
    "得分动作",
    "动作卡",
    "自检卡",
    "私人自检卡",
    "优先动作卡",
    "主动作",
    "闭环",
    "Route Map",
    "Repair",
    "repair",
    "score moves",
    "scorecard",
    "self-check card",
    "答案如下",
    "第本课程",
]

FORBIDDEN_VISIBLE_PATTERNS = [
    ("第N讲", r"第[\s_-]*\d{1,2}[\s_-]*讲"),
]

STUDENT_FORBIDDEN_VISIBLE = [
    "['",
    '["',
    "教师",
    "surface family",
    "page rhythm",
    "design system",
    "Lesson Route",
    "Route Map",
    "Lesson Rhythm",
    "Practice Rhythm",
    "Micro Skills",
    "five score moves",
    "personal start record",
    "action scorecard",
    "不提前报出规则或答案",
    "点名时先追问",
    "执行时先给学生",
    "答案为",
    "因此选",
    "不按题号逐题念答案",
    "教师示范",
    "教师聚焦反馈",
]
GAOKAO_WORKBOOK_MARKERS = ("高考", "中考", "天津卷", "升高三", "Gaokao")
RENDERER_UI_LABEL_DRIFT_PATTERNS = [
    (re.compile(r"<span>\s*本讲路线\s*•"), "本讲路线 footer label"),
    (re.compile(r"<span>\s*课前记录\s*•"), "课前记录 footer label"),
    (re.compile(r"<span>\s*第\d{1,2}讲\s*•"), "第xx讲 footer label"),
    (re.compile(r"<span>\s*(?:LESSON MAP|Lesson Map|BOOK MAP|Book Map)\s*•\s*[^<]*(?:高考|中考|天津卷|升高三)"), "Chinese course-title footer label"),
    (re.compile(r"<b>\s*第\d{1,2}讲\s*</b>"), "第xx讲 badge label"),
    (re.compile(r'<section class="exam-timing-strip">\s*<b>\s*时间\s*</b>'), "时间 timing strip label"),
]
WORKBOOK_PROMPT_LANGUAGE_DRIFT_TERMS = (
    "接下来我们",
    "本页回收",
    "复盘记录",
    "微技能训练",
    "段落诊断",
    "作业说明",
    "今日记录",
    "完成前检查",
    "进入下一页前",
    "先确认这一页",
    "下次先改哪一类题",
    "主动作",
    "动作链",
    "维修",
    "路由",
    "后台",
    "闭环",
)
WORKBOOK_PROMPT_LANGUAGE_DRIFT_PATTERNS = (
    (re.compile(r"\bRecord\s*(?:/|·|;)\s*Record\b"), "degenerated Record/Record workbook prompt"),
    (re.compile(r"\bRecord\s*(?:/|·|;)\s*Record\s*(?:/|·|;)\s*Record\b"), "degenerated Record/Record/Record workbook prompt"),
    (re.compile(r"\babout\s+0\s+min\b", re.I), "zero-minute route prompt"),
    (re.compile(r"\bPreview\s+todays\b", re.I), "apostrophe-stripped today prompt"),
    (re.compile(r"^\s*Practice\s*$", re.I), "standalone generic Practice prompt"),
    (re.compile(r"完形填空第\s*\d+\s*空"), "Chinese cloze blank prompt"),
    (re.compile(r"第\s*\d+\s*空"), "Chinese blank-number prompt"),
    (re.compile(r"根据全文.*选择"), "Chinese choose-from-whole-text prompt"),
    (re.compile(r"选择最符合"), "Chinese best-fit choice prompt"),
    (re.compile(r"^\s*(?:完形填空|阅读理解|阅读表达|任务型阅读)\b"), "Chinese source-type prefix in article body"),
    (re.compile(r"[一二三四五六七八九十]+、\s*$"), "Chinese trailing source section marker in article body"),
    (re.compile(r"(?:\b\d{1,2}\s*_{1,2}\b|\b_{1,2}\s*\d{1,2}\s*_{0,2}\b|\b[A-Za-z]+_{1,}\d{1,2}\b|\b[A-Za-z]+_\d{1,2}_{1,}\b)"), "raw cloze underscore marker in article body"),
    (re.compile(r"\b[A-Za-z]{2,}[-‐‑‒–—]\s+[A-Za-z]{2,}\b"), "OCR split word in article body"),
    (re.compile(r"\b(?:whenI|becauseI|ifI|thatI|asI|onthe|inthe|tothe|ofthe|forthe|andthe|bea)\b"), "OCR fused word in article body"),
    (re.compile(r"\b[A-Za-z]+\s+[,.;:!?]\s*[A-Za-z]"), "OCR punctuation spacing in article body"),
    (re.compile(r"先用哪一个证据检查"), "Chinese final-check evidence prompt"),
    (re.compile(r"完成后删掉哪一种模糊答案"), "Chinese final-check vague-answer prompt"),
    (re.compile(r"下次先看哪一类错误"), "Chinese final-check error-type prompt"),
)
WORKBOOK_PROMPT_SELECTORS = (
    ".question-lines li",
    ".record-prompt",
    ".planner-prompt",
    ".workbook-record",
    ".exam-timing-strip",
    ".activity-block p",
    ".activity-block li",
    ".review-rules",
    ".evidence-task-strip",
    ".article-flow .lettered-paragraph p",
    ".method-card",
    ".writing-planner",
    ".final-check",
)
WORKBOOK_HEADING_TEMPLATES = {
    "activity",
    "article-evidence",
    "contents-route",
    "article-opener",
    "exam-mini-set",
    "paragraph-practice",
    "photo-passage",
    "writing-planner",
    "categorizing-chart",
    "skill-method",
    "final-check",
    "sentence-map",
    "correction-rewrite",
    "handbook",
    "vocab-bank",
}
WORKBOOK_AI_HEADING_TERMS = (
    "路线",
    "本讲节奏",
    "微技能训练",
    "段落诊断",
    "作业说明",
    "复盘记录",
    "今日记录",
    "完成前检查",
    "Today On The Page",
    "Evidence Pause",
    "Practice Review",
    "Lesson Route",
    "Lesson Rhythm",
    "Practice Rhythm",
    "Micro Skills",
    "Method Model",
    "Demo Practice",
    "Tool Practice",
)
READING_SURFACE_MARKERS = (
    "Reading Text",
    "Key Evidence",
    "Boundary Check",
    "Read for exact evidence",
    "Guided Reading",
    "Source Reading",
    "Timed Reading",
    "Extra Reading",
)
CJK_RE = re.compile(r"[\u3400-\u9fff]")

STARTER_SAMPLE_TITLE = "Pathways to Better Writing"
STARTER_RESIDUE_TERMS = [
    "Pathways to Better Writing",
    "English Writing System",
    "Sentences, Paragraphs, and Writing Practice",
    "A Good Place to Observe",
    "The Best Place to Think",
    "canyon-cover",
]
SOURCE_SCAN_PATHS = [
    "book.yaml",
    "assets/manifest.json",
    "theme/tokens.json",
    "tools/build.py",
    "tools/validate.py",
    "typst-adapter/lesson-a4-template.typ",
]
SOURCE_SCAN_GLOBS = [
    "pages/*.md",
    "typst-adapter/*.typ",
]
SOURCE_FRESHNESS_GLOBS = [
    "book.yaml",
    "pages/**/*.md",
    "assets/manifest.json",
    "theme/**/*",
    "tools/build.py",
    "tools/render_pdf.py",
]

STRICT = {"P0", "P1"}
UNDERSCORE_RUN_RE = re.compile(r"_{3,}")
STRONG_BLANK_ALIGN = "-0.82em"
STRONG_QUESTION_BLANK_ALIGN = "-0.88em"
MODEL_PARAGRAPH_BLANK_ALIGN = "-0.22em"
RECORD_PROMPT_BLANK_ALIGN = "-0.32em"
INLINE_CLOZE_BLANK_ALIGN = "-0.30em"
WORDBOX_PHRASE_BLANK_ALIGN = "-0.26em"
COMPACT_RULE_BLANK_ALIGN = "-0.24em"
CHECKLIST_COMPACT_BLANK_ALIGN = "-0.24em"
TITLE_PAGE_FOR_SCALE = "1em"
COVER_BRAND_NAME = "Eric Teaching Studio"
WEAK_TITLE_FOR_SCALE_VALUES = (".86em", "0.86em", ".85em", "0.85em", ".8em", "0.8em")
WEAK_BLANK_ALIGN_VALUES = ("-0.64em", "-0.68em", "-0.42em", "-0.44em")
GENERIC_FUNCTIONAL_TITLE_TERMS = (
    "备考计划",
    "学习计划",
    "复习计划",
    "课程计划",
    "workbook",
    "lesson pack",
    "student workbook",
    "a4 lesson pack",
)
GENERIC_STUDENT_NAME_TERMS = ("Sample Learner",)
IDENTITY_ANCHOR_TEMPLATES = {
    "cover",
    "title",
    "contents-route",
    "unit-opener",
    "article-opener",
    "article-evidence",
    "photo-passage",
    "correction-rewrite",
    "final-check",
    "handbook",
    "vocab-bank",
    "connector-index",
    "answer-key",
    "teacher-answer-key",
}
FORM_REPEAT_TEMPLATES = {
    "activity",
    "workbook-record",
    "writing-planner",
    "final-check",
    "exam-mini-set",
    "categorizing-chart",
    "skill-method",
}
STRUCTURE_LIBRARY_REPEAT_TEMPLATES = {
    "activity",
    "article-evidence",
    "article-opener",
    "categorizing-chart",
    "comprehension-check",
    "connector-bank",
    "correction-rewrite",
    "exam-mini-set",
    "final-check",
    "grammar-rule",
    "guided-discovery",
    "handbook",
    "model-annotation",
    "sentence-map",
    "skill-method",
    "vocab-bank",
    "workbook-record",
    "writing-planner",
}
STRUCTURE_LIBRARY_MIN_COUNTS_FINAL = {
    "handbook": 3,
}
INLINE_CLOZE_SELECTORS = (
    ".activity-block p .blank",
    ".activity-block li .blank",
    ".word-box .blank",
    ".words-to-know .blank",
    ".textbook-table td .blank",
    ".review-rules .blank",
    ".planner-prompt .blank",
    ".editing-checklist label .blank",
    ".handbook-page .blank",
    ".answer-table .blank",
)
ASSET_MODE_PROOF = "proof-placeholder"
ASSET_MODE_FINAL = "final-assets"
VALID_ASSET_MODES = {ASSET_MODE_PROOF, ASSET_MODE_FINAL}
FINAL_ASSET_KINDS = {
    "imagegen",
    "licensed-photo",
    "owned-photo",
    "original-photo",
    "commissioned-illustration",
    "licensed-illustration",
}
PLACEHOLDER_ASSET_KINDS = {
    "placeholder",
    "proof-placeholder",
    "procedural-raster",
    "mock",
    "starter",
    "layout-placeholder",
}
PLACEHOLDER_ASSET_TERMS = (
    "placeholder",
    "proof",
    "draft",
    "starter",
    "sample",
    "procedural",
    "mock",
    "temporary",
    "temp",
)
NATURE_ASSET_ANCHORS = (
    "nature",
    "natural",
    "wildlife",
    "animal",
    "animals",
    "bird",
    "birds",
    "crane",
    "cranes",
    "forest",
    "mountain",
    "mountains",
    "river",
    "lake",
    "ocean",
    "sea",
    "coast",
    "wetland",
    "valley",
    "field",
    "meadow",
    "grassland",
    "tree",
    "trees",
    "sky",
)
LEARNING_LIFE_ASSET_ANCHORS = (
    "photo",
    "photographic",
    "photorealistic",
    "realistic",
    "landscape",
    "outdoor",
    "campus",
    "school",
    "classroom",
    "library",
    "student",
    "teacher",
    "study",
    "desk",
    "notebook",
    "workbook",
    "modern life",
    "modern human",
    "human",
    "window",
    "room",
    "city",
    "street",
    "home",
    "cafe",
    "hands",
)
REAL_WORLD_ASSET_ANCHORS = NATURE_ASSET_ANCHORS + LEARNING_LIFE_ASSET_ANCHORS
ABSTRACT_ASSET_DRIFT_TERMS = (
    "abstract",
    "symbolic",
    "conceptual",
    "paper sculpture",
    "paper decision map",
    "decision map",
    "evidence board",
    "floating token",
    "floating tokens",
    "grammar token",
    "grammar tokens",
    "token map",
    "blank strip",
    "blank strips",
    "paper strip",
    "paper strips",
    "floating strip",
    "floating strips",
    "cards and arrows",
    "floating arrows",
    "label-like",
    "pictogram",
    "icon-like",
    "geometric shapes",
    "concept art",
    "shape collage",
)
ANIMAL_STYLE_DRIFT_TERMS = (
    "cartoon",
    "mascot",
    "sticker",
    "sticker-like",
    "sticker style",
    "chibi",
    "anime",
    "kawaii",
    "toy-like",
    "cute character",
    "playful mascot",
    "childish mascot",
)
VISUAL_ASSET_ROLE_RE = re.compile(r"(cover|unit[-_ ]?opener|opener|photo|context|passage|hero)", re.I)
COVER_ASSET_ROLE_RE = re.compile(r"(cover|hero)", re.I)


def run(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return proc.returncode, proc.stdout


def issue(severity: str, code: str, detail: str, file: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"severity": severity, "code": code, "detail": detail}
    if file:
        payload["file"] = file
    return payload


def unnegated_term_hits(text: str, terms: tuple[str, ...]) -> list[str]:
    hits: list[str] = []
    for term in terms:
        pattern = re.compile(re.escape(term), re.I)
        for match in pattern.finditer(text):
            prefix = text[max(0, match.start() - 28) : match.start()]
            if re.search(r"(?:no|avoid|without|not|never|reject|ban)\s+[\w\s-]{0,18}$", prefix, re.I):
                continue
            hits.append(term)
            break
    return hits


def asset_interpretable_scene_policy(asset: dict[str, Any]) -> dict[str, Any]:
    scene_text = " ".join(
        str(asset.get(key) or "")
        for key in (
            "id",
            "role",
            "purpose",
            "source_note",
            "focus",
            "prompt",
            "generation_prompt",
            "prompt_summary",
            "content_brief",
            "visual_direction",
            "uniqueness_note",
        )
    ).lower()
    abstract_hits = unnegated_term_hits(scene_text, ABSTRACT_ASSET_DRIFT_TERMS)
    style_drift_hits = unnegated_term_hits(scene_text, ANIMAL_STYLE_DRIFT_TERMS)
    real_world_hits = [term for term in REAL_WORLD_ASSET_ANCHORS if term in scene_text]
    return {
        "ok": not abstract_hits and not style_drift_hits and bool(real_world_hits),
        "abstract_hits": abstract_hits,
        "style_drift_hits": style_drift_hits,
        "real_world_hits": real_world_hits,
    }


def asset_nature_first_policy(asset: dict[str, Any]) -> dict[str, Any]:
    scene_text = " ".join(
        str(asset.get(key) or "")
        for key in (
            "id",
            "role",
            "purpose",
            "source_note",
            "focus",
            "prompt",
            "generation_prompt",
            "prompt_summary",
            "content_brief",
            "visual_direction",
            "uniqueness_note",
            "visual_family",
            "image_family",
            "scene_family",
            "family_rationale",
            "nature_first_rationale",
            "visual_family_rationale",
        )
    ).lower()
    visual_family = str(
        asset.get("visual_family") or asset.get("image_family") or asset.get("scene_family") or ""
    ).strip()
    rationale = str(
        asset.get("family_rationale")
        or asset.get("nature_first_rationale")
        or asset.get("visual_family_rationale")
        or ""
    ).strip()
    nature_hits = [term for term in NATURE_ASSET_ANCHORS if term in scene_text]
    explicit_nature_family = bool(
        re.search(r"\b(nature|natural|landscape|wildlife|animal|animals|forest|mountain|river|lake|wetland)\b", visual_family, re.I)
    )
    ok = bool(nature_hits or explicit_nature_family or rationale)
    return {
        "ok": ok,
        "severity": "OK" if ok else "P2",
        "nature_hits": nature_hits,
        "visual_family": visual_family,
        "rationale_present": bool(rationale),
    }


def asset_license_status_policy(asset: dict[str, Any]) -> dict[str, Any]:
    source_note = str(asset.get("source_note") or "").strip()
    status = str(asset.get("status") or "").strip()
    source = source_note.lower()
    normalized_status = re.sub(r"[^a-z0-9]+", " ", status.lower())

    source_cc_by_sa = bool(re.search(r"\bcc\s*by\s*-?\s*sa\b|\bcc-by-sa\b|creative commons attribution[- ]sharealike", source))
    source_cc_by = source_cc_by_sa or bool(re.search(r"\bcc\s*by\b|\bcc-by\b|creative commons attribution", source))
    source_public_domain = bool(re.search(r"\bpublic domain\b", source))
    status_public_domain = bool(re.search(r"\bpublic\s+domain\b", normalized_status))
    status_cc_by = bool(re.search(r"\bcc\b", normalized_status) and re.search(r"\bby\b", normalized_status))
    status_cc_by_sa = status_cc_by and bool(re.search(r"\bsa\b|\bsharealike\b", normalized_status))

    mismatches: list[str] = []
    if source_public_domain and not status_public_domain:
        mismatches.append("source_note says Public domain but status does not")
    if source_cc_by and not status_cc_by:
        mismatches.append("source_note says CC BY/Creative Commons attribution but status does not")
    if source_cc_by_sa and not status_cc_by_sa:
        mismatches.append("source_note says CC BY-SA but status does not")
    if source_public_domain and status_cc_by:
        mismatches.append("status says CC BY while source_note says Public domain")
    if source_cc_by and status_public_domain:
        mismatches.append("status says Public domain while source_note says CC BY/Creative Commons")

    return {
        "ok": not mismatches,
        "mismatches": mismatches,
        "source_note": source_note,
        "status": status,
    }


def normalize_asset_mode(value: Any) -> str:
    raw = str(value or ASSET_MODE_PROOF).strip().lower().replace("_", "-")
    aliases = {
        "proof": ASSET_MODE_PROOF,
        "layout-proof": ASSET_MODE_PROOF,
        "placeholder": ASSET_MODE_PROOF,
        "proof-placeholders": ASSET_MODE_PROOF,
        "final": ASSET_MODE_FINAL,
        "production": ASSET_MODE_FINAL,
        "production-assets": ASSET_MODE_FINAL,
    }
    return aliases.get(raw, raw)


def configured_asset_mode(book: dict[str, Any], spec: dict[str, Any], override: str | None = None) -> str:
    qa = book.get("qa") or {}
    profile_qa = spec.get("qa") or {}
    return normalize_asset_mode(override or profile_qa.get("asset_mode") or qa.get("asset_mode"))


def infer_answer_visibility_from_profile(profile: str | None, spec: dict[str, Any]) -> str:
    fields = [
        profile,
        spec.get("label"),
        spec.get("audience"),
        spec.get("output_html"),
        spec.get("output_pdf"),
    ]
    outputs = spec.get("outputs") if isinstance(spec.get("outputs"), dict) else {}
    fields.extend([outputs.get("html"), outputs.get("pdf")])
    blob = " ".join(str(item or "") for item in fields).lower().replace("_", "-")
    if "teacher" in blob:
        return "teacher"
    if "student" in blob:
        if "answer-key" in blob or "with-key" in blob or "with-answer" in blob:
            return "student-with-answer-key"
        return "student"
    return "off"


def configured_answer_visibility(book: dict[str, Any], spec: dict[str, Any], profile: str | None = None) -> str:
    qa = book.get("qa") or {}
    profile_qa = spec.get("qa") or {}
    for value in (
        profile_qa.get("answer_visibility"),
        spec.get("answer_visibility"),
        qa.get("answer_visibility"),
    ):
        if value is not None and str(value).strip():
            return normalize_answer_visibility(value)
    return infer_answer_visibility_from_profile(profile, spec)


def rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def load_book(root: Path) -> dict[str, Any]:
    return yaml.safe_load((root / "book.yaml").read_text(encoding="utf-8"))


def html_text(path: Path) -> tuple[str, BeautifulSoup]:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    for tag in soup(["style", "script"]):
        tag.decompose()
    text = re.sub(r"\s+", " ", soup.get_text(" ")).strip()
    return text, soup


def duplicated_question_blank_hits(soup: BeautifulSoup) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for section in soup.select(".sheet"):
        page = section.get("data-page") or ""
        for item in section.select(".question-lines li"):
            if item.select(".blank") and item.select(".write-line"):
                hits.append(
                    {
                        "page": page,
                        "text": re.sub(r"\s+", " ", item.get_text(" ")).strip()[:160],
                    }
                )
    return hits


def exam_stem_slot_policy(soup: BeautifulSoup, raw_html: str) -> dict[str, Any]:
    generic_blank_hits: list[dict[str, str]] = []
    for section in soup.select(".sheet"):
        page = section.get("data-page") or ""
        template = section.get("data-template") or ""
        for prompt in section.select(".guided-mcq-set p"):
            if prompt.select(".blank"):
                generic_blank_hits.append(
                    {
                        "page": page,
                        "template": template,
                        "text": re.sub(r"\s+", " ", prompt.get_text(" ")).strip()[:160],
                    }
                )
    slot_count = len(soup.select(".guided-mcq-set p .exam-stem-slot"))
    slot_rule = css_rule_body_for_selector(raw_html, ".guided-mcq-set p .exam-stem-slot")
    keep_rule = css_rule_body_for_selector(raw_html, ".exam-stem-keep")
    css_checks = {
        "checked": bool(slot_count),
        "slot_rule_present": bool(slot_rule) if slot_count else True,
        "slot_has_border": "border-bottom" in slot_rule if slot_count else True,
        "slot_not_generic_blank": not generic_blank_hits,
        "punctuation_keep_rule": css_has_declaration(keep_rule, "white-space", "nowrap") if slot_count else True,
    }
    return {
        "ok": not generic_blank_hits and all(value for key, value in css_checks.items() if key != "checked"),
        "slot_count": slot_count,
        "generic_blank_hits": generic_blank_hits,
        "css_checks": css_checks,
        "required": "Guided MCQ/cloze stems must render author ____ as .exam-stem-slot with no-wrap punctuation, never as generic .blank.",
    }


def a4_sentence_map_surface_policy(soup: BeautifulSoup, profile: str) -> dict[str, Any]:
    checked = "a4" in str(profile).lower()
    if not checked:
        return {"ok": True, "checked": False, "wide_table_hits": [], "missing_card_stack": []}
    wide_table_hits: list[dict[str, str]] = []
    missing_card_stack: list[dict[str, str]] = []
    for section in soup.select('.sheet[data-template="sentence-map"]'):
        page = section.get("data-page") or ""
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


def a4_only_profile_policy(book: dict[str, Any], raw_html: str = "") -> dict[str, Any]:
    output_mode = str((book.get("qa") or {}).get("output_mode") or "").strip().lower()
    checked = output_mode == "a4-only"
    if not checked:
        return {"ok": True, "checked": False, "profile_hits": [], "output_hits": [], "html_hits": []}
    profile_hits = [name for name in (book.get("profiles") or {}) if "book-trim" in str(name)]
    output_hits: list[dict[str, str]] = []
    for name, spec in (book.get("profiles") or {}).items():
        if not isinstance(spec, dict):
            continue
        outputs: list[Any] = [spec.get("output_html"), spec.get("output_pdf")]
        nested = spec.get("outputs") if isinstance(spec.get("outputs"), dict) else {}
        outputs.extend(nested.values())
        for output in outputs:
            if output and "book-trim" in str(output):
                output_hits.append({"profile": str(name), "output": str(output)})
    html_hits = []
    for term in ("book-trim", "Student workbook and A4 lesson pack", "22讲", "天津高考英语一轮复习", "第本课程"):
        if term in raw_html:
            html_hits.append(term)
    if re.search(r"第[\s_-]*\d{1,2}[\s_-]*讲", raw_html):
        html_hits.append("第N讲")
    return {
        "ok": not profile_hits and not output_hits and not html_hits,
        "checked": True,
        "profile_hits": profile_hits,
        "output_hits": output_hits,
        "html_hits": html_hits,
        "required": "When qa.output_mode is a4-only, the project must expose only A4 profiles, A4 output paths, and A4-only rendered HTML.",
    }


def pdf_text(path: Path) -> str:
    code, out = run(["pdftotext", str(path), "-"])
    if code != 0:
        raise RuntimeError(out)
    return out


def forbidden_hits(text: str) -> dict[str, int]:
    hits: dict[str, int] = {}
    for term in FORBIDDEN_VISIBLE:
        if re.fullmatch(r"[A-Za-z0-9_ ]+", term):
            pattern = r"(?<![A-Za-z0-9_])" + re.escape(term) + r"(?![A-Za-z0-9_])"
            count = len(re.findall(pattern, text))
        else:
            count = text.count(term)
        if count:
            hits[term] = count
    for label, pattern in FORBIDDEN_VISIBLE_PATTERNS:
        count = len(re.findall(pattern, text))
        if count:
            hits[label] = count
    return hits


def student_forbidden_hits(text: str) -> dict[str, int]:
    hits: dict[str, int] = {}
    for term in STUDENT_FORBIDDEN_VISIBLE:
        count = text.count(term)
        if count:
            hits[term] = count
    return hits


def gaokao_workbook_language_applies(book: dict[str, Any], visible_text: str) -> bool:
    fields = [
        book.get("title"),
        book.get("subtitle"),
        book.get("series"),
        book.get("level"),
        book.get("edition"),
        (book.get("identity") or {}).get("positioning"),
        (book.get("identity") or {}).get("audience"),
        visible_text[:3000],
    ]
    blob = " ".join(str(item or "") for item in fields)
    return any(marker in blob for marker in GAOKAO_WORKBOOK_MARKERS)


def visible_heading_language_policy(soup: BeautifulSoup, book: dict[str, Any], visible_text: str, *, answer_visibility: str) -> dict[str, Any]:
    checked = answer_visibility == "student" and gaokao_workbook_language_applies(book, visible_text)
    if not checked:
        return {
            "ok": True,
            "checked": False,
            "ai_heading_hits": [],
            "workbook_cjk_heading_hits": [],
            "reading_cjk_heading_hits": [],
        }

    ai_heading_hits: list[dict[str, str]] = []
    workbook_cjk_heading_hits: list[dict[str, str]] = []
    reading_cjk_heading_hits: list[dict[str, str]] = []
    for section in soup.select(".sheet"):
        template = str(section.get("data-template") or "").strip()
        if template not in WORKBOOK_HEADING_TEMPLATES:
            continue
        page = str(section.get("data-page") or "")
        heading_node = section.select_one("h1, h2, h3")
        heading = re.sub(r"\s+", " ", heading_node.get_text(" ") if heading_node else "").strip()
        if not heading:
            continue
        for term in WORKBOOK_AI_HEADING_TERMS:
            if term in heading:
                ai_heading_hits.append({"page": page, "template": template, "heading": heading, "term": term})
                break
        if CJK_RE.search(heading):
            workbook_cjk_heading_hits.append({"page": page, "template": template, "heading": heading})
        surface_text = re.sub(r"\s+", " ", section.get_text(" ")).strip()
        is_reading_surface = template == "exam-mini-set" and ("Reading" in heading or "阅读" in heading)
        if template == "article-opener":
            is_reading_surface = is_reading_surface or any(marker in surface_text for marker in READING_SURFACE_MARKERS)
        if is_reading_surface and CJK_RE.search(heading):
            reading_cjk_heading_hits.append({"page": page, "template": template, "heading": heading})

    return {
        "ok": not ai_heading_hits and not workbook_cjk_heading_hits and not reading_cjk_heading_hits,
        "checked": True,
        "ai_heading_hits": ai_heading_hits,
        "workbook_cjk_heading_hits": workbook_cjk_heading_hits,
        "reading_cjk_heading_hits": reading_cjk_heading_hits,
    }


def renderer_ui_label_language_policy(raw_html: str, book: dict[str, Any], visible_text: str, *, answer_visibility: str) -> dict[str, Any]:
    checked = answer_visibility == "student" and gaokao_workbook_language_applies(book, visible_text)
    if not checked:
        return {"ok": True, "checked": False, "hits": []}

    hits: list[dict[str, str]] = []
    for pattern, label in RENDERER_UI_LABEL_DRIFT_PATTERNS:
        for match in pattern.finditer(raw_html):
            start = max(0, match.start() - 120)
            end = min(len(raw_html), match.end() + 120)
            snippet = re.sub(r"\s+", " ", raw_html[start:end]).strip()
            hits.append({"label": label, "snippet": snippet[:220]})
            if len(hits) >= 12:
                break
        if len(hits) >= 12:
            break

    return {"ok": not hits, "checked": True, "hits": hits}


def cloze_blank_label_language_policy(visible_text: str, book: dict[str, Any]) -> dict[str, Any]:
    checked = gaokao_workbook_language_applies(book, visible_text)
    if not checked:
        return {"ok": True, "checked": False, "hits": []}

    hits: list[dict[str, str]] = []
    for match in re.finditer(r"第\s*\d+\s*空", visible_text):
        start = max(0, match.start() - 80)
        end = min(len(visible_text), match.end() + 100)
        snippet = re.sub(r"\s+", " ", visible_text[start:end]).strip()
        hits.append({"term": match.group(0), "text": snippet[:180]})
        if len(hits) >= 12:
            break
    return {"ok": not hits, "checked": True, "hits": hits}


def student_prompt_language_policy(soup: BeautifulSoup, book: dict[str, Any], visible_text: str, *, answer_visibility: str) -> dict[str, Any]:
    checked = answer_visibility == "student" and gaokao_workbook_language_applies(book, visible_text)
    if not checked:
        return {"ok": True, "checked": False, "hits": []}

    hits: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for selector in WORKBOOK_PROMPT_SELECTORS:
        for node in soup.select(selector):
            text = re.sub(r"\s+", " ", node.get_text(" ")).strip()
            if not text:
                continue
            for term in WORKBOOK_PROMPT_LANGUAGE_DRIFT_TERMS:
                if term not in text:
                    continue
                page_node = node.find_parent(class_="sheet") or node
                page = str(page_node.get("data-page") or "")
                template = str(page_node.get("data-template") or "")
                key = (page, selector, term)
                if key in seen:
                    continue
                seen.add(key)
                hits.append(
                    {
                        "page": page,
                        "template": template,
                        "selector": selector,
                        "term": term,
                        "text": text[:180],
                    }
                )
                if len(hits) >= 16:
                    break
            if len(hits) >= 16:
                break
            for pattern, label in WORKBOOK_PROMPT_LANGUAGE_DRIFT_PATTERNS:
                if not pattern.search(text):
                    continue
                page_node = node.find_parent(class_="sheet") or node
                page = str(page_node.get("data-page") or "")
                template = str(page_node.get("data-template") or "")
                key = (page, selector, label)
                if key in seen:
                    continue
                seen.add(key)
                hits.append(
                    {
                        "page": page,
                        "template": template,
                        "selector": selector,
                        "term": label,
                        "text": text[:180],
                    }
                )
                if len(hits) >= 16:
                    break
            if len(hits) >= 16:
                break
        if len(hits) >= 16:
            break

    return {"ok": not hits, "checked": True, "hits": hits}


def literal_underscore_runs(sources: dict[str, str], limit: int = 12) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for label, text in sources.items():
        for match in UNDERSCORE_RUN_RE.finditer(text):
            start = max(0, match.start() - 28)
            end = min(len(text), match.end() + 28)
            hits.append(
                {
                    "source": label,
                    "start": match.start(),
                    "length": len(match.group(0)),
                    "snippet": text[start:end].replace("\n", " "),
                }
            )
            if len(hits) >= limit:
                return hits
    return hits


def css_rule_body(raw_html: str, selector_pattern: str) -> str:
    match = re.search(selector_pattern + r"\s*\{(?P<body>[^}]*)\}", extract_css_text(raw_html), flags=re.S)
    if not match:
        return ""
    return re.sub(r"\s+", " ", match.group("body")).strip()


def normalize_css_selector(selector: str) -> str:
    selector = re.sub(r"</?style[^>]*>", "", selector, flags=re.I)
    return re.sub(r"\s+", " ", selector.strip())


def extract_css_text(raw_html: str) -> str:
    blocks = re.findall(r"<style[^>]*>(.*?)</style>", raw_html, flags=re.I | re.S)
    if blocks:
        return "\n".join(blocks)
    return re.sub(r"</?style[^>]*>", "", raw_html, flags=re.I)


def css_rule_body_for_selector(raw_html: str, selector: str) -> str:
    bodies = css_rule_bodies_for_selector(raw_html, selector)
    return bodies[0] if bodies else ""


def css_rule_bodies_for_selector(raw_html: str, selector: str) -> list[str]:
    wanted = normalize_css_selector(selector)
    bodies: list[str] = []
    css_text = extract_css_text(raw_html)
    for match in re.finditer(r"(?P<selectors>[^{}]+)\{(?P<body>[^}]*)\}", css_text, flags=re.S):
        selectors = [normalize_css_selector(item) for item in match.group("selectors").split(",")]
        if wanted in selectors:
            bodies.append(re.sub(r"\s+", " ", match.group("body")).strip())
    return bodies


def css_last_rule_body_for_selector(raw_html: str, selector: str) -> str:
    bodies = css_rule_bodies_for_selector(raw_html, selector)
    return bodies[-1] if bodies else ""


def css_has_declaration(rule_body: str, prop: str, value: str) -> bool:
    return bool(re.search(re.escape(prop) + r"\s*:\s*" + re.escape(value) + r"\b", rule_body))


def blank_baseline_css_checks(raw_html: str) -> dict[str, Any]:
    blank_rule = css_rule_body(raw_html, r"(?<![-\w])\.blank")
    question_rule = css_rule_body(raw_html, r"\.question-lines\s+\.blank")
    model_paragraph_rule = css_rule_body(raw_html, r"\.paragraph-practice\s+p\s+\.blank")
    record_prompt_rule = css_rule_body(raw_html, r"\.record-prompt\s+\.blank")
    cloze_keep_rule = css_rule_body(raw_html, r"\.cloze-keep")
    word_box_rule = css_rule_body(raw_html, r"\.word-box")
    word_box_item_rule = css_rule_body(raw_html, r"\.word-box-item")
    word_box_specific_rule = css_last_rule_body_for_selector(raw_html, ".word-box .blank")
    handbook_rules_blank_rule = css_rule_body(raw_html, r"\.handbook-rules\s+\.blank")
    inline_cloze_rules = {selector: css_rule_body_for_selector(raw_html, selector) for selector in INLINE_CLOZE_SELECTORS}
    inline_cloze_checks = {
        selector: css_has_declaration(rule, "vertical-align", INLINE_CLOZE_BLANK_ALIGN)
        for selector, rule in inline_cloze_rules.items()
    }
    compact_phrase_checks = {
        "cloze_keep_no_wrap": css_has_declaration(cloze_keep_rule, "white-space", "nowrap"),
        "word_box_phrase_items_no_wrap": css_has_declaration(word_box_item_rule, "white-space", "nowrap"),
        "word_box_not_four_equal_columns": "repeat(4, 1fr)" not in word_box_rule,
        "word_box_compact_blank_adjustment": css_has_declaration(word_box_specific_rule, "vertical-align", WORDBOX_PHRASE_BLANK_ALIGN),
        "handbook_rules_compact_blank_adjustment": css_has_declaration(handbook_rules_blank_rule, "vertical-align", COMPACT_RULE_BLANK_ALIGN),
    }
    checks = {
        "blank_rule_present": bool(blank_rule),
        "zero_height_blank_box": css_has_declaration(blank_rule, "height", "0"),
        "bottom_rule_border": "border-bottom" in blank_rule,
        "strong_lower_baseline_align": css_has_declaration(blank_rule, "vertical-align", STRONG_BLANK_ALIGN),
        "strong_question_blank_adjustment": css_has_declaration(question_rule, "vertical-align", STRONG_QUESTION_BLANK_ALIGN),
        "model_paragraph_blank_adjustment": css_has_declaration(model_paragraph_rule, "vertical-align", MODEL_PARAGRAPH_BLANK_ALIGN),
        "record_prompt_blank_adjustment": css_has_declaration(record_prompt_rule, "vertical-align", RECORD_PROMPT_BLANK_ALIGN),
        "inline_cloze_context_adjustments": all(inline_cloze_checks.values()),
        "compact_phrase_blank_adjustments": all(compact_phrase_checks.values()),
        "legacy_middle_align_rejected": not any(f"vertical-align: {value}" in raw_html or f"vertical-align:{value}" in raw_html for value in WEAK_BLANK_ALIGN_VALUES),
        "no_old_upward_blank_transform": "translateY(-2pt)" not in raw_html,
    }
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "required": {
            ".blank vertical-align": STRONG_BLANK_ALIGN,
            ".question-lines .blank vertical-align": STRONG_QUESTION_BLANK_ALIGN,
            ".paragraph-practice p .blank vertical-align": MODEL_PARAGRAPH_BLANK_ALIGN,
            ".record-prompt .blank vertical-align": RECORD_PROMPT_BLANK_ALIGN,
            "inline cloze selectors vertical-align": INLINE_CLOZE_BLANK_ALIGN,
            ".word-box .blank compact vertical-align": WORDBOX_PHRASE_BLANK_ALIGN,
            ".handbook-rules .blank compact vertical-align": COMPACT_RULE_BLANK_ALIGN,
            ".cloze-keep white-space": "nowrap",
            ".word-box-item white-space": "nowrap",
        },
        "inline_cloze_selectors": inline_cloze_checks,
        "compact_phrase_blank": compact_phrase_checks,
    }


def title_lockup_css_checks(raw_html: str) -> dict[str, Any]:
    soup = BeautifulSoup(raw_html, "html.parser")
    uses_title_page_mixed_title = bool(soup.select(".title-page h1.title-single .title-for"))
    uses_cover_mixed_title = bool(soup.select(".cover-title.title-single .title-for"))
    uses_mixed_title = uses_title_page_mixed_title or uses_cover_mixed_title
    title_single_rule = css_rule_body_for_selector(raw_html, ".title-page h1.title-single")
    title_for_rule = css_last_rule_body_for_selector(raw_html, ".title-page h1.title-single .title-for")
    cover_single_rule = css_rule_body_for_selector(raw_html, ".cover-title.title-single h1")
    cover_for_rule = css_last_rule_body_for_selector(raw_html, ".cover-title.title-single .title-for")
    title_weak_scale_present = any(value in title_for_rule for value in WEAK_TITLE_FOR_SCALE_VALUES)
    cover_weak_scale_present = any(value in cover_for_rule for value in WEAK_TITLE_FOR_SCALE_VALUES)
    checks = {
        "mixed_title_uses_deliberate_lockup": True
        if not uses_mixed_title
        else (not uses_title_page_mixed_title or bool(title_single_rule and title_for_rule))
        and (not uses_cover_mixed_title or bool(cover_single_rule and cover_for_rule)),
        "title_single_no_wrap": True
        if not uses_title_page_mixed_title
        else css_has_declaration(title_single_rule, "white-space", "nowrap"),
        "title_for_same_optical_scale": True
        if not uses_title_page_mixed_title
        else css_has_declaration(title_for_rule, "font-size", TITLE_PAGE_FOR_SCALE) and not title_weak_scale_present,
        "title_for_weight_not_demoted": True
        if not uses_title_page_mixed_title
        else "font-weight: inherit" in title_for_rule or "font-weight" not in title_for_rule,
        "cover_title_single_no_wrap": True
        if not uses_cover_mixed_title
        else css_has_declaration(cover_single_rule, "white-space", "nowrap"),
        "cover_title_for_same_optical_scale": True
        if not uses_cover_mixed_title
        else css_has_declaration(cover_for_rule, "font-size", TITLE_PAGE_FOR_SCALE) and not cover_weak_scale_present,
        "cover_title_for_weight_not_demoted": True
        if not uses_cover_mixed_title
        else "font-weight: inherit" in cover_for_rule or "font-weight" not in cover_for_rule,
        "legacy_title_for_shrink_rejected": not title_weak_scale_present and not cover_weak_scale_present,
    }
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "uses_mixed_title": uses_mixed_title,
        "required": {
            ".title-page h1.title-single white-space": "nowrap",
            ".title-page h1.title-single .title-for font-size": TITLE_PAGE_FOR_SCALE,
            ".title-page h1.title-single .title-for font-weight": "inherit or omitted",
            ".cover-title.title-single h1 white-space": "nowrap",
            ".cover-title.title-single .title-for font-size": TITLE_PAGE_FOR_SCALE,
            ".cover-title.title-single .title-for font-weight": "inherit or omitted",
        },
    }


def cover_brand_checks(raw_html: str, book: dict[str, Any]) -> dict[str, Any]:
    soup = BeautifulSoup(raw_html, "html.parser")
    cover = soup.select_one('.sheet[data-template="cover"], .template-cover')
    cover_text = re.sub(r"\s+", " ", cover.get_text(" ") if cover else "").strip()
    cover_top = cover.select_one(".cover-top") if cover else None
    cover_top_text = re.sub(r"\s+", " ", cover_top.get_text(" ") if cover_top else "").strip()
    brand_node = cover.select_one(".cover-brand") if cover else None
    brand_rule = css_rule_body_for_selector(raw_html, ".cover-brand")
    brand_contrast_css = bool(
        brand_rule
        and re.search(
            r"(?<![-\w])(?:background|background-color|text-shadow|box-shadow|backdrop-filter|-webkit-backdrop-filter)\s*:",
            brand_rule,
        )
    )
    level = str(book.get("level") or "").strip()
    checks = {
        "cover_present": cover is not None,
        "brand_text_present": COVER_BRAND_NAME in cover_text,
        "cover_brand_node_present": brand_node is not None,
        "brand_bottom_right_css": bool(
            brand_rule
            and "position: absolute" in brand_rule
            and re.search(r"\bright\s*:", brand_rule)
            and re.search(r"\bbottom\s*:", brand_rule)
        ),
        "brand_contrast_css": brand_contrast_css,
        "cover_top_level_badge_absent": not bool(level and level in cover_top_text),
    }
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "brand": COVER_BRAND_NAME,
        "level": level,
        "cover_top_text": cover_top_text,
    }


def unit_opener_composition_checks(raw_html: str) -> dict[str, Any]:
    soup = BeautifulSoup(raw_html, "html.parser")
    openers = soup.select('.sheet[data-template="unit-opener"], .template-unit-opener')
    floating_caption_pages: list[str] = []
    prompt_missing_from_band: list[str] = []
    prompt_pages: list[str] = []
    for idx, opener in enumerate(openers, 1):
        page = opener.get("data-page") or str(idx)
        caption = opener.select_one(".photo-caption")
        if caption and caption.get_text(" ", strip=True):
            floating_caption_pages.append(str(page))
        text = re.sub(r"\s+", " ", opener.get_text(" ", strip=True))
        has_before_prompt = bool(re.search(r"\bBefore (?:the )?unit begins\b|\bBefore You Begin\b", text, re.I))
        prompt = opener.select_one(".objectives-band .opener-prompt")
        if prompt:
            prompt_pages.append(str(page))
        if has_before_prompt and not prompt:
            prompt_missing_from_band.append(str(page))

    objectives_intro_rule = css_rule_body_for_selector(raw_html, ".objectives-intro")
    opener_prompt_rule = css_rule_body_for_selector(raw_html, ".opener-prompt")
    objectives_list_rule = css_rule_body_for_selector(raw_html, ".objectives-list ul")
    has_prompt = bool(prompt_pages)
    checks = {
        "unit_openers_present": bool(openers),
        "floating_photo_caption_absent": not floating_caption_pages,
        "before_prompt_inside_objectives_band": not prompt_missing_from_band,
        "opener_prompt_css_present": True if not has_prompt else bool(opener_prompt_rule),
        "objectives_intro_css_present": True if not has_prompt else bool(objectives_intro_rule),
        "objectives_list_css_present": bool(objectives_list_rule) if openers else True,
        "legacy_photo_caption_css_rejected": ".photo-caption" not in raw_html,
    }
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "unit_opener_count": len(openers),
        "prompt_pages": prompt_pages,
        "floating_caption_pages": floating_caption_pages,
        "prompt_missing_from_band": prompt_missing_from_band,
        "required": "Unit opener prompts such as `Before the unit begins...` must live inside .objectives-band as .opener-prompt, not as a floating .photo-caption above the band.",
    }


def unit_opener_variation_checks(raw_html: str) -> dict[str, Any]:
    soup = BeautifulSoup(raw_html, "html.parser")
    openers = soup.select('.sheet[data-template="unit-opener"], .template-unit-opener')
    opener_data: list[dict[str, str]] = []
    for idx, opener in enumerate(openers, 1):
        page = str(opener.get("data-page") or idx)
        band = opener.select_one(".objectives-band")
        layout = str(opener.get("data-opener-layout") or (band.get("data-opener-layout") if band else "") or "").strip()
        accent = str(opener.get("data-opener-accent") or (band.get("data-opener-accent") if band else "") or "").strip().lower()
        variant = str(opener.get("data-variant") or "").strip()
        opener_data.append({"page": page, "layout": layout, "accent": accent, "variant": variant})
    checked = len(opener_data) >= 4
    if not checked:
        return {
            "ok": True,
            "checked": False,
            "unit_opener_count": len(opener_data),
            "layouts": sorted({item["layout"] for item in opener_data if item["layout"]}),
            "accents": sorted({item["accent"] for item in opener_data if item["accent"]}),
            "missing_metadata_pages": [],
        }
    layouts = {item["layout"] for item in opener_data if item["layout"]}
    accents = {item["accent"] for item in opener_data if item["accent"]}
    variants = {item["variant"] for item in opener_data if item["variant"]}
    missing_metadata_pages = [
        item["page"]
        for item in opener_data
        if not item["layout"] or not item["accent"] or not item["variant"]
    ]
    min_layouts = 2
    min_accents = 3 if len(opener_data) >= 6 else 2
    checks = {
        "opener_metadata_present": not missing_metadata_pages,
        "multiple_layouts_present": len(layouts) >= min_layouts,
        "multiple_accents_present": len(accents) >= min_accents,
        "variants_present": len(variants) >= min_layouts,
    }
    return {
        "ok": all(checks.values()),
        "checked": True,
        "checks": checks,
        "unit_opener_count": len(opener_data),
        "layouts": sorted(layouts),
        "accents": sorted(accents),
        "variants": sorted(variants),
        "missing_metadata_pages": missing_metadata_pages,
        "required": "A long book's unit openers should not all share one color and one stacked structure; require per-unit accent/layout metadata and visible variation.",
    }


def checklist_control_css_checks(raw_html: str) -> dict[str, Any]:
    soup = BeautifulSoup(raw_html, "html.parser")
    uses_checklist = bool(soup.select(".editing-checklist"))
    generic_label_span_rule = css_rule_body_for_selector(raw_html, ".editing-checklist label span")
    check_mark_rule = css_rule_body_for_selector(raw_html, ".editing-checklist .check-mark")
    checklist_blank_rule = css_last_rule_body_for_selector(raw_html, ".editing-checklist label .blank")
    checks = {
        "check_mark_nodes_present": True if not uses_checklist else bool(soup.select(".editing-checklist .check-mark")),
        "check_mark_css_present": True if not uses_checklist else bool(check_mark_rule) and "border" in check_mark_rule,
        "generic_label_span_selector_rejected": not bool(generic_label_span_rule),
        "checklist_blank_compact_override": True
        if not uses_checklist
        else css_has_declaration(checklist_blank_rule, "vertical-align", CHECKLIST_COMPACT_BLANK_ALIGN),
    }
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "uses_checklist": uses_checklist,
        "required": {
            "control marker": ".editing-checklist .check-mark",
            "forbidden selector": ".editing-checklist label span",
            ".editing-checklist label .blank vertical-align": CHECKLIST_COMPACT_BLANK_ALIGN,
        },
    }


def workbook_record_checks(raw_html: str) -> dict[str, Any]:
    soup = BeautifulSoup(raw_html, "html.parser")
    checks = {
        "workbook_practice_component_present": bool(soup.select('[data-component="workbook-practice"]')),
        "record_surface_present": bool(soup.select(".workbook-record")),
        "record_header_present": bool(soup.select(".record-head")),
        "numbered_record_rows_present": bool(soup.select(".record-index")) and bool(soup.select(".record-lines")),
    }
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "required": "Workbook/activity pages must end in a cohesive record surface, not loose Q&A lines.",
    }


def planner_surface_checks(raw_html: str) -> dict[str, Any]:
    soup = BeautifulSoup(raw_html, "html.parser")
    planner_nodes = soup.select('[data-component="writing-planner"]')
    legacy_planner_table = bool(soup.select("table.planner-table")) or any(node.find("table") for node in planner_nodes)
    variant_surface_selector = ", ".join(
        [
            '.planner-rows[data-component="writing-planner"]',
            '.route-map-surface[data-component="writing-planner"]',
            '.daily-rhythm-grid[data-component="writing-planner"]',
            '.answer-sheet-surface[data-component="writing-planner"]',
            '.task2-printed-surface[data-component="writing-planner"]',
            '.visual-planner-steps[data-component="writing-planner"]',
            '.cue-card-surface[data-component="writing-planner"]',
            '.reading-evidence-grid[data-component="writing-planner"]',
        ]
    )
    variant_surfaces = soup.select(variant_surface_selector)
    variant_texture = bool(
        soup.select(
            ".route-map-surface article, .daily-rhythm-grid article, .answer-sheet-surface article, "
            ".task2-printed-surface article, .task2-position-ladder article, .task2-body-lanes article, "
            ".visual-planner-steps article, .cue-card-surface aside, .reading-evidence-grid article"
        )
    )
    activity_or_variant_head = bool(
        soup.select(".review-rules, .answer-sheet-head, .route-activity, .schedule-activity, .cue-card-surface")
    )
    checks = {
        "planner_surface_present": bool(variant_surfaces),
        "planner_role_texture_present": (bool(soup.select(".planner-row")) and bool(soup.select(".planner-key"))) or variant_texture,
        "review_rules_or_variant_head_present": activity_or_variant_head,
        "legacy_table_planner_rejected": not legacy_planner_table,
    }
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "required": "Planner must use paper-surface row cards or a named variant surface, not a table/grid that reads like a spreadsheet.",
    }


def rendered_page_count_checks(rendered_count: int, expected_count: int | None) -> dict[str, Any]:
    if not expected_count:
        return {
            "ok": rendered_count > 0,
            "checks": {
                "rendered_pages_present": rendered_count > 0,
                "rendered_page_count_exact": True,
                "rendered_pages_missing": False,
                "rendered_pages_stale": False,
            },
            "expected": expected_count,
            "actual": rendered_count,
        }
    checks = {
        "rendered_pages_present": rendered_count > 0,
        "rendered_page_count_exact": rendered_count == expected_count,
        "rendered_pages_missing": rendered_count < expected_count,
        "rendered_pages_stale": rendered_count > expected_count,
    }
    return {
        "ok": checks["rendered_page_count_exact"],
        "checks": checks,
        "expected": expected_count,
        "actual": rendered_count,
    }


RENDERED_CONFLICT_NAME_RE = re.compile(r"(?: \d+|conflicted|conflict|copy)", re.I)


def expected_rendered_page_name(profile: str, page_number: int) -> str:
    page_token = f"{page_number:03d}" if page_number < 1000 else str(page_number)
    return f"{profile}-page-{page_token}.png"


def rendered_page_filename_checks(names: list[str], profile: str, expected_count: int | None) -> dict[str, Any]:
    canonical_re = re.compile(rf"^{re.escape(profile)}-page-(\d{{3,}})\.png$")
    conflict_files: list[str] = []
    unexpected_files: list[str] = []
    canonical_files: list[str] = []
    page_numbers: list[int] = []
    seen_numbers: set[int] = set()
    duplicate_numbers: list[int] = []

    for name in sorted(names):
        if RENDERED_CONFLICT_NAME_RE.search(name):
            conflict_files.append(name)
            continue
        match = canonical_re.match(name)
        if not match:
            unexpected_files.append(name)
            continue
        number = int(match.group(1))
        canonical_files.append(name)
        page_numbers.append(number)
        if number in seen_numbers:
            duplicate_numbers.append(number)
        seen_numbers.add(number)

    missing_files: list[str] = []
    if expected_count:
        expected_names = {expected_rendered_page_name(profile, page) for page in range(1, expected_count + 1)}
        missing_files = sorted(expected_names.difference(canonical_files))

    checks = {
        "no_conflict_files": not conflict_files,
        "no_unexpected_files": not unexpected_files,
        "continuous_sequence": not missing_files,
        "no_duplicate_page_numbers": not duplicate_numbers,
    }
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "expected": expected_count,
        "actual": len(canonical_files),
        "canonical_files": canonical_files,
        "conflict_files": conflict_files,
        "unexpected_files": unexpected_files,
        "missing_files": missing_files[:20],
        "missing_count": len(missing_files),
        "duplicate_page_numbers": duplicate_numbers,
        "page_numbers_sample": page_numbers[:12],
    }


def artifact_mtime(path: Path) -> float | None:
    try:
        return path.stat().st_mtime
    except OSError:
        return None


def rendered_artifact_freshness_checks(
    rendered_pages: list[Path],
    *,
    html_path: Path,
    pdf_path: Path,
    contact_path: Path,
) -> dict[str, Any]:
    reference_times = {
        "html": artifact_mtime(html_path),
        "pdf": artifact_mtime(pdf_path),
    }
    reference_times = {key: value for key, value in reference_times.items() if value is not None}
    if not rendered_pages or not reference_times:
        return {
            "ok": bool(rendered_pages),
            "checked": False,
            "reference_times": reference_times,
            "stale_rendered_pages": [],
            "contact_sheet_fresh": contact_path.exists(),
        }
    min_required = max(reference_times.values())
    stale_rendered_pages = [
        page
        for page in rendered_pages
        if artifact_mtime(page) is None or (artifact_mtime(page) or 0) + 0.5 < min_required
    ]
    contact_time = artifact_mtime(contact_path)
    contact_sheet_fresh = bool(contact_time is not None and contact_time + 0.5 >= min_required)
    return {
        "ok": not stale_rendered_pages and contact_sheet_fresh,
        "checked": True,
        "reference_times": reference_times,
        "min_required_mtime": min_required,
        "contact_sheet_fresh": contact_sheet_fresh,
        "contact_sheet_mtime": contact_time,
        "stale_rendered_pages": [
            {"path": str(page), "mtime": artifact_mtime(page)}
            for page in stale_rendered_pages[:12]
        ],
        "stale_rendered_count": len(stale_rendered_pages),
    }


def source_path_has_glob(value: str) -> bool:
    return any(char in value for char in "*?[")


def unique_source_files(root: Path, paths: list[Path]) -> list[Path]:
    blocked_parts = {"outputs", "_qa", "qa", ".git", "node_modules"}
    unique: dict[str, Path] = {}
    for path in paths:
        try:
            resolved = path.resolve()
        except Exception:
            resolved = path
        try:
            rel_parts = resolved.relative_to(root).parts
            if any(part in blocked_parts for part in rel_parts):
                continue
        except ValueError:
            rel_parts = resolved.parts
        if resolved.is_file():
            unique[str(resolved)] = resolved
    return sorted(unique.values(), key=lambda item: str(item))


def configured_source_input_paths(root: Path, source_inputs: Any) -> list[Path]:
    paths: list[Path] = []
    for raw in as_list(source_inputs):
        item = raw.strip()
        if not item:
            continue
        raw_path = Path(item)
        if source_path_has_glob(item):
            pattern = item if raw_path.is_absolute() else str(root / item)
            paths.extend(Path(match) for match in glob.glob(pattern, recursive=True))
            continue
        path = raw_path if raw_path.is_absolute() else root / raw_path
        if path.is_dir():
            paths.extend(child for child in path.rglob("*") if child.is_file())
        else:
            paths.append(path)
    return unique_source_files(root, paths)


def collect_source_input_paths(root: Path, configured_inputs: Any = None) -> list[Path]:
    paths: list[Path] = []
    for pattern in SOURCE_FRESHNESS_GLOBS:
        for path in root.glob(pattern):
            if path.is_file():
                paths.append(path.resolve())
    manifest_path = root / "assets" / "manifest.json"
    if manifest_path.exists():
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            assets = data.get("assets", data if isinstance(data, list) else [])
            if isinstance(assets, list):
                for asset in assets:
                    if not isinstance(asset, dict):
                        continue
                    asset_path = str(asset.get("path") or "").strip()
                    if not asset_path:
                        continue
                    path = Path(asset_path)
                    paths.append((root / path if not path.is_absolute() else path).resolve())
        except Exception:
            paths.append(manifest_path.resolve())
    paths.extend(configured_source_input_paths(root, configured_inputs))
    return unique_source_files(root, paths)


def source_output_freshness_checks(
    root: Path,
    *,
    html_path: Path,
    pdf_path: Path,
    configured_inputs: Any = None,
) -> dict[str, Any]:
    configured_sources = configured_source_input_paths(root, configured_inputs)
    sources = collect_source_input_paths(root, configured_inputs)
    source_times = [(path, artifact_mtime(path)) for path in sources]
    source_times = [(path, mtime) for path, mtime in source_times if mtime is not None]
    output_times = {
        "html": artifact_mtime(html_path),
        "pdf": artifact_mtime(pdf_path),
    }
    if not source_times or any(value is None for value in output_times.values()):
        return {
            "ok": bool(source_times) and all(value is not None for value in output_times.values()),
            "checked": False,
            "source_count": len(source_times),
            "configured_source_count": len(configured_sources),
            "output_times": output_times,
            "latest_sources": [],
            "stale_outputs": {},
        }
    latest_time = max(mtime for _, mtime in source_times if mtime is not None)
    latest_sources = [
        {"path": str(path), "mtime": mtime}
        for path, mtime in sorted(source_times, key=lambda item: item[1] or 0, reverse=True)[:8]
    ]
    stale_outputs = {
        name: mtime
        for name, mtime in output_times.items()
        if mtime is None or mtime + 0.5 < latest_time
    }
    return {
        "ok": not stale_outputs,
        "checked": True,
        "source_count": len(source_times),
        "configured_source_count": len(configured_sources),
        "latest_source_mtime": latest_time,
        "latest_sources": latest_sources,
        "output_times": output_times,
        "stale_outputs": stale_outputs,
    }


def is_starter_sample(book: dict[str, Any], spec: dict[str, Any]) -> bool:
    qa = book.get("qa") or {}
    profile_qa = spec.get("qa") or {}
    if qa.get("allow_starter_residue") or profile_qa.get("allow_starter_residue"):
        return True
    title = str(book.get("title") or "").strip().casefold()
    return title == STARTER_SAMPLE_TITLE.casefold()


def active_page_source_files(root: Path, book: dict[str, Any]) -> set[Path]:
    files: set[Path] = set()
    for entry in book.get("pages") or []:
        if isinstance(entry, dict):
            value = entry.get("file") or entry.get("path")
        else:
            value = entry
        if not value:
            continue
        path = (root / str(value)).resolve()
        if path.exists() and path.is_file():
            files.add(path)
    return files


def inactive_page_source_files(root: Path, book: dict[str, Any], limit: int = 24) -> dict[str, Any]:
    pages_dir = root / "pages"
    if not pages_dir.exists():
        return {"count": 0, "files": []}
    active = active_page_source_files(root, book)
    files = sorted(path for path in pages_dir.glob("*.md") if path.resolve() not in active)
    return {"count": len(files), "files": [rel(root, path) for path in files[:limit]]}


def scanned_source_paths(root: Path, book: dict[str, Any] | None = None) -> list[Path]:
    paths: list[Path] = []
    for rel_path in SOURCE_SCAN_PATHS:
        path = root / rel_path
        if path.exists() and path.is_file():
            paths.append(path)
    active_pages = active_page_source_files(root, book) if book else set()
    for pattern in SOURCE_SCAN_GLOBS:
        if pattern == "pages/*.md" and active_pages:
            paths.extend(sorted(active_pages))
            continue
        paths.extend(path for path in sorted(root.glob(pattern)) if path.is_file())
    return sorted(set(paths))


def stale_duplicate_page_files(root: Path, limit: int = 24) -> dict[str, Any]:
    pages_dir = root / "pages"
    if not pages_dir.exists():
        return {"count": 0, "files": []}
    pattern = re.compile(r" [0-9]+\.md$")
    files = sorted(path for path in pages_dir.glob("*.md") if pattern.search(path.name))
    return {"count": len(files), "files": [rel(root, path) for path in files[:limit]]}


def qa_evidence_conflict_files(root: Path, limit: int = 24) -> dict[str, Any]:
    qa_dir = root / "_qa"
    if not qa_dir.exists():
        return {"count": 0, "files": []}
    pattern = re.compile(r" [0-9]+\.(?:png|jpg|jpeg|md|json)$", re.I)
    candidates = [
        *qa_dir.glob("contact-sheet-*"),
        *qa_dir.glob("review-sheet-*"),
        *qa_dir.glob("visual-review-*"),
        *qa_dir.glob("textbook-qa-*"),
    ]
    files = sorted(path for path in candidates if path.is_file() and pattern.search(path.name))
    return {"count": len(files), "files": [rel(root, path) for path in files[:limit]]}


def starter_residue_hits(root: Path, book: dict[str, Any], spec: dict[str, Any], visible_text: str, extracted_text: str) -> dict[str, Any]:
    if is_starter_sample(book, spec):
        return {}
    locations: dict[str, list[dict[str, Any]]] = {}
    sources: list[tuple[str, str]] = [("visible-output", visible_text + "\n" + extracted_text)]
    for path in scanned_source_paths(root, book):
        try:
            sources.append((rel(root, path), path.read_text(encoding="utf-8", errors="replace")))
        except OSError:
            continue
    for term in STARTER_RESIDUE_TERMS:
        for label, text in sources:
            count = text.count(term)
            if count:
                locations.setdefault(term, []).append({"file": label, "count": count})
    return {term: {"total": sum(item["count"] for item in rows), "locations": rows[:8]} for term, rows in locations.items()}


def read_page_frontmatter(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    match = re.match(r"^---\n(.*?)\n---\n?", raw, flags=re.S)
    if not match:
        return {}
    try:
        return yaml.safe_load(match.group(1)) or {}
    except Exception:
        return {}


def page_asset_refs(root: Path, book: dict[str, Any]) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for rel_page in book.get("pages") or []:
        page_path = root / str(rel_page)
        meta = read_page_frontmatter(page_path)
        asset_id = meta.get("asset")
        if asset_id:
            refs.append(
                {
                    "id": str(asset_id),
                    "page": str(rel_page),
                    "template": str(meta.get("template") or ""),
                    "section": str(meta.get("section") or ""),
                }
            )
    return refs


def asset_is_visual_ref(asset: dict[str, Any], refs: list[dict[str, str]]) -> bool:
    role_blob = " ".join(str(asset.get(key) or "") for key in ("role", "purpose", "use_role"))
    if VISUAL_ASSET_ROLE_RE.search(role_blob):
        return True
    for ref in refs:
        if str(asset.get("id")) == ref["id"] and VISUAL_ASSET_ROLE_RE.search(ref.get("template", "")):
            return True
    return False


def as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return [str(item).strip() for item in value if str(item).strip()]


def asset_usage_policy(assets: list[dict[str, Any]], refs: list[dict[str, str]]) -> dict[str, Any]:
    asset_ids = [str(asset.get("id") or "").strip() for asset in assets]
    manifest_id_counts = Counter(asset_id for asset_id in asset_ids if asset_id)
    duplicate_manifest_ids = {asset_id: count for asset_id, count in manifest_id_counts.items() if count > 1}
    path_to_ids: dict[str, list[str]] = {}
    for asset in assets:
        asset_id = str(asset.get("id") or "").strip()
        path = str(asset.get("path") or "").strip()
        if path:
            path_to_ids.setdefault(path, []).append(asset_id)
    duplicate_paths = {
        path: sorted(set(ids))
        for path, ids in path_to_ids.items()
        if len(set(ids)) > 1
    }
    refs_by_id: dict[str, list[dict[str, str]]] = {}
    for ref in refs:
        refs_by_id.setdefault(ref["id"], []).append(ref)
    reused_asset_refs = {
        asset_id: rows
        for asset_id, rows in refs_by_id.items()
        if len(rows) > 1
    }
    cover_asset_inside_refs: list[dict[str, Any]] = []
    allowed_template_mismatches: list[dict[str, Any]] = []
    for asset in assets:
        asset_id = str(asset.get("id") or "").strip()
        role_blob = " ".join(str(asset.get(key) or "") for key in ("role", "purpose", "use_role")).lower()
        is_cover_ref = bool(COVER_ASSET_ROLE_RE.search(role_blob))
        allowed_templates = as_list(asset.get("allowed_templates") or asset.get("allowed_template"))
        if is_cover_ref and not allowed_templates:
            allowed_templates = ["cover"]
        for ref in refs_by_id.get(asset_id, []):
            if is_cover_ref and ref.get("template") != "cover":
                cover_asset_inside_refs.append({"id": asset_id, **ref})
            if allowed_templates and ref.get("template") not in allowed_templates:
                allowed_template_mismatches.append(
                    {
                        "id": asset_id,
                        "page": ref.get("page"),
                        "template": ref.get("template"),
                        "allowed_templates": allowed_templates,
                    }
                )
    checks = {
        "manifest_asset_ids_unique": not duplicate_manifest_ids,
        "manifest_paths_unique": not duplicate_paths,
        "asset_refs_single_use": not reused_asset_refs,
        "cover_assets_not_used_inside": not cover_asset_inside_refs,
        "asset_refs_match_allowed_templates": not allowed_template_mismatches,
    }
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "duplicate_manifest_ids": duplicate_manifest_ids,
        "duplicate_paths": duplicate_paths,
        "reused_asset_refs": reused_asset_refs,
        "cover_asset_inside_refs": cover_asset_inside_refs,
        "allowed_template_mismatches": allowed_template_mismatches,
    }


def page_family_coverage_policy(
    pages: list[dict[str, Any]], *, mode: str | None = None, answer_visibility: str | None = None
) -> dict[str, Any]:
    normalized_mode = str(mode or "").strip().lower()
    if normalized_mode not in V2_PAGE_FAMILY_MODES:
        return {
            "ok": True,
            "mode": normalized_mode or "off",
            "checked": False,
            "families": {},
            "missing_families": [],
        }
    templates = {str(page.get("template") or "").strip() for page in pages if str(page.get("template") or "").strip()}
    families: dict[str, dict[str, Any]] = {}
    missing_families: list[str] = []
    for family, required in V2_PAGE_FAMILY_REQUIREMENTS.items():
        required = set(required)
        present_required = sorted(required & templates)
        missing_required = sorted(required - templates)
        alternatives = V2_PAGE_FAMILY_ALTERNATIVES.get(family, [])
        if family == "writing-output" and normalized_mode in {"student-book", "teacher-book"}:
            required = {"writing-planner", "final-check"}
            alternatives = [{"correction-rewrite", "paragraph-practice"}]
            present_required = sorted(required & templates)
            missing_required = sorted(required - templates)
        if family == "back-matter" and str(answer_visibility or "").strip().lower() == "student":
            alternatives = []
        present_alternatives: list[list[str]] = []
        missing_alternatives: list[list[str]] = []
        alternatives_ok = True
        for group in alternatives:
            present_group = sorted(group & templates)
            present_alternatives.append(present_group)
            if not present_group:
                alternatives_ok = False
                missing_alternatives.append(sorted(group))
        ok = not missing_required and alternatives_ok
        families[family] = {
            "ok": ok,
            "required": sorted(required),
            "present_required": present_required,
            "missing_required": missing_required,
            "alternative_required_any": [sorted(group) for group in alternatives],
            "present_alternatives": present_alternatives,
            "missing_alternatives": missing_alternatives,
        }
        if not ok:
            missing_families.append(family)
    return {
        "ok": not missing_families,
        "mode": normalized_mode,
        "checked": True,
        "templates": sorted(templates),
        "families": families,
        "missing_families": missing_families,
    }


def generic_book_identity_policy(book: dict[str, Any], *, asset_mode: str, starter_sample: bool) -> dict[str, Any]:
    identity = book.get("identity") or {}
    title = str(book.get("title") or "").strip()
    subtitle = str(book.get("subtitle") or "").strip()
    cover_title = str(identity.get("cover_title") or book.get("cover_title") or title).strip()
    positioning = str(identity.get("positioning") or identity.get("editorial_positioning") or "").strip()
    audience = str(identity.get("audience") or "").strip()
    front_matter_role = str(identity.get("front_matter_role") or "").strip()
    title_blob = " ".join([title, subtitle, cover_title]).casefold()
    visible_title_blob = " ".join([title, subtitle, cover_title]).casefold()
    core_title_blob = " ".join([title, cover_title]).casefold()
    functional_hits: list[str] = []
    for term in GENERIC_FUNCTIONAL_TITLE_TERMS:
        normalized = term.casefold()
        if normalized in {"workbook"}:
            core_parts = {title.casefold().strip(), cover_title.casefold().strip()}
            if normalized in core_parts:
                functional_hits.append(term)
            continue
        if normalized in core_title_blob or normalized in visible_title_blob:
            functional_hits.append(term)
    name_hits = [term for term in GENERIC_STUDENT_NAME_TERMS if term.casefold() in title_blob]
    final_mode = asset_mode == ASSET_MODE_FINAL and not starter_sample
    checks = {
        "not_starter_sample_or_final_gate": final_mode,
        "generic_student_names_absent": not name_hits,
        "identity_block_present": bool(identity) if final_mode else True,
        "cover_title_present": bool(cover_title) if final_mode else True,
        "cover_title_not_only_functional": not functional_hits if final_mode else True,
        "positioning_present": bool(positioning) if final_mode else True,
        "audience_present": bool(audience) if final_mode else True,
        "front_matter_role_present": bool(front_matter_role) if final_mode else True,
    }
    ok = checks["generic_student_names_absent"] and (
        True
        if not final_mode
        else all(
            checks[key]
            for key in (
                "identity_block_present",
                "cover_title_present",
                "cover_title_not_only_functional",
                "positioning_present",
                "audience_present",
                "front_matter_role_present",
            )
        )
    )
    return {
        "ok": ok,
        "checked": final_mode,
        "checks": checks,
        "title": title,
        "subtitle": subtitle,
        "cover_title": cover_title,
        "visible_title_blob": visible_title_blob,
        "functional_hits": functional_hits,
        "student_name_hits": name_hits,
        "required": {
            "identity.cover_title": "a publishable book identity, not only a functional course label",
            "identity.positioning": "one sentence explaining the book's editorial promise",
            "identity.audience": "the intended generic reader",
            "identity.front_matter_role": "what p1-p3 establish beyond usage instructions",
        },
    }


def page_role_rhythm_policy(pages: list[dict[str, Any]], *, page_family_mode: str, asset_mode: str) -> dict[str, Any]:
    templates = [str(page.get("template") or "").strip() for page in pages if str(page.get("template") or "").strip()]
    checked = len(templates) >= 24 and str(page_family_mode or "").strip().lower() in V2_PAGE_FAMILY_MODES
    if not checked:
        return {
            "ok": True,
            "checked": False,
            "windows_without_anchor": [],
            "max_form_run": 0,
            "template_counts": dict(Counter(templates)),
        }
    window_size = 12
    windows_without_anchor: list[dict[str, Any]] = []
    for start in range(0, max(0, len(templates) - window_size + 1), window_size):
        window = templates[start : start + window_size]
        if not any(template in IDENTITY_ANCHOR_TEMPLATES for template in window):
            windows_without_anchor.append(
                {"pages": [start + 1, start + len(window)], "templates": window}
            )
    max_form_run = 0
    current_run = 0
    current_start = 0
    form_runs: list[dict[str, Any]] = []
    for idx, template in enumerate(templates, 1):
        if template in FORM_REPEAT_TEMPLATES:
            if current_run == 0:
                current_start = idx
            current_run += 1
        else:
            if current_run:
                form_runs.append({"pages": [current_start, idx - 1], "length": current_run})
            max_form_run = max(max_form_run, current_run)
            current_run = 0
    if current_run:
        form_runs.append({"pages": [current_start, len(templates)], "length": current_run})
    max_form_run = max(max_form_run, current_run)
    warning_threshold = 11 if asset_mode == ASSET_MODE_FINAL else 14
    ok = not windows_without_anchor and max_form_run <= warning_threshold
    return {
        "ok": ok,
        "checked": True,
        "window_size": window_size,
        "windows_without_anchor": windows_without_anchor,
        "max_form_run": max_form_run,
        "form_runs": [run for run in form_runs if run["length"] > warning_threshold - 2],
        "template_counts": dict(Counter(templates)),
        "warning_threshold": warning_threshold,
    }


def page_role_variant_policy(pages: list[dict[str, Any]], *, page_family_mode: str, asset_mode: str) -> dict[str, Any]:
    checked = len(pages) >= 50 and str(page_family_mode or "").strip().lower() in V2_PAGE_FAMILY_MODES
    target_templates = {"writing-planner", "final-check"}
    target_pages = [
        {
            "page": str(page.get("page") or idx),
            "template": str(page.get("template") or "").strip(),
            "variant": str(page.get("variant") or "").strip(),
        }
        for idx, page in enumerate(pages, 1)
        if str(page.get("template") or "").strip() in target_templates
    ]
    if not checked or len(target_pages) < 8:
        return {
            "ok": True,
            "checked": False,
            "target_page_count": len(target_pages),
            "missing_variant_pages": [],
            "dense_variant_windows": [],
            "variant_counts": dict(Counter(f"{page['template']}:{page['variant'] or 'missing'}" for page in target_pages)),
        }
    missing_variant_pages = [
        {"page": page["page"], "template": page["template"]}
        for page in target_pages
        if not page["variant"]
    ]
    dense_variant_windows: list[dict[str, Any]] = []
    window_size = 12
    repeat_threshold = 4 if asset_mode == ASSET_MODE_FINAL else 5
    for start in range(0, max(0, len(pages) - window_size + 1)):
        window = pages[start : start + window_size]
        keys = [
            f"{str(page.get('template') or '').strip()}:{str(page.get('variant') or '').strip()}"
            for page in window
            if str(page.get("template") or "").strip() in target_templates
            and str(page.get("variant") or "").strip()
        ]
        counts = Counter(keys)
        dense = {key: count for key, count in counts.items() if count >= repeat_threshold}
        if dense:
            dense_variant_windows.append({"pages": [start + 1, start + len(window)], "variants": dense})
    ok = not missing_variant_pages and not dense_variant_windows
    return {
        "ok": ok,
        "checked": True,
        "target_page_count": len(target_pages),
        "window_size": window_size,
        "repeat_threshold": repeat_threshold,
        "missing_variant_pages": missing_variant_pages,
        "dense_variant_windows": dense_variant_windows,
        "variant_counts": dict(Counter(f"{page['template']}:{page['variant'] or 'missing'}" for page in target_pages)),
        "required": "Long v2 books must give planner/final-check pages semantic variants so repeated form families become page roles, not copy-pasted templates.",
    }


def normalize_structure_variant(variant: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", str(variant or "").strip().lower()).strip("-")
    if not slug:
        return ""
    slug = re.sub(r"-(practice|set)-\d+$", "", slug)
    slug = re.sub(r"-(part|passage)-\d+(?=-|$)", r"-\1", slug)
    slug = re.sub(r"-\d+$", "", slug)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug


def page_rendered_surface(page: dict[str, Any]) -> str:
    surface = normalize_structure_variant(str(page.get("surface") or "").strip())
    if surface:
        return surface
    return normalize_structure_variant(str(page.get("variant") or "").strip())


def page_rendered_surface_family(page: dict[str, Any]) -> str:
    return normalize_structure_variant(str(page.get("surface_family") or "").strip())


def page_rendered_surface_key(page: dict[str, Any]) -> str:
    family = page_rendered_surface_family(page)
    surface = page_rendered_surface(page)
    if family and surface:
        return f"{family}:{surface}"
    return surface or normalize_structure_variant(str(page.get("variant") or "").strip())


def rendered_page_records(soup: BeautifulSoup) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for idx, section in enumerate(soup.select(".sheet"), 1):
        surface_node = section.select_one("[data-surface]")
        records.append(
            {
                "page": section.get("data-page") or str(idx),
                "template": section.get("data-template"),
                "variant": section.get("data-variant"),
                "surface": surface_node.get("data-surface") if surface_node else section.get("data-surface"),
                "surface_family": surface_node.get("data-surface-family") if surface_node else section.get("data-surface-family"),
            }
        )
    return records


def page_structure_variant_library_policy(
    pages: list[dict[str, Any]], *, page_family_mode: str, asset_mode: str
) -> dict[str, Any]:
    def repeated_threshold_for(template: str) -> int:
        default = 4 if asset_mode == ASSET_MODE_FINAL else 5
        if asset_mode == ASSET_MODE_FINAL:
            return min(default, STRUCTURE_LIBRARY_MIN_COUNTS_FINAL.get(template, default))
        return default

    checked = len(pages) >= 50 and str(page_family_mode or "").strip().lower() in V2_PAGE_FAMILY_MODES
    target_pages = [
        {
            "page": str(page.get("page") or idx),
            "template": str(page.get("template") or "").strip(),
            "variant": str(page.get("variant") or "").strip(),
            "normalized_variant": normalize_structure_variant(str(page.get("variant") or "").strip()),
            "surface": str(page.get("surface") or "").strip(),
            "normalized_surface": page_rendered_surface(page),
            "surface_family": str(page.get("surface_family") or "").strip(),
        }
        for idx, page in enumerate(pages, 1)
        if str(page.get("template") or "").strip() in STRUCTURE_LIBRARY_REPEAT_TEMPLATES
    ]
    by_template: dict[str, list[dict[str, str]]] = {}
    for page in target_pages:
        by_template.setdefault(page["template"], []).append(page)
    repeated_groups = {
        template: rows
        for template, rows in by_template.items()
        if len(rows) >= repeated_threshold_for(template)
    }
    if not checked or not repeated_groups:
        return {
            "ok": True,
            "checked": False,
            "default_repeated_threshold": 4 if asset_mode == ASSET_MODE_FINAL else 5,
            "repeated_groups": {template: len(rows) for template, rows in repeated_groups.items()},
            "weak_template_groups": [],
            "missing_variant_pages": [],
            "metadata_only_surface_pages": [],
            "dense_structure_windows": [],
            "template_variant_counts": {
                template: dict(Counter(row["normalized_variant"] or "missing" for row in rows))
                for template, rows in by_template.items()
            },
            "template_surface_counts": {
                template: dict(Counter(row["normalized_surface"] or "missing" for row in rows))
                for template, rows in by_template.items()
            },
        }

    weak_template_groups: list[dict[str, Any]] = []
    missing_variant_pages: list[dict[str, str]] = []
    metadata_only_surface_pages: list[dict[str, str]] = []
    missing_surface_family_pages: list[dict[str, str]] = []
    for template, rows in sorted(repeated_groups.items()):
        structures = [page_rendered_surface_key(row) for row in rows if page_rendered_surface_key(row)]
        unique_structures = sorted(set(structures))
        missing = [{"page": row["page"], "template": template} for row in rows if not row["variant"]]
        missing_variant_pages.extend(missing)
        if template in {"writing-planner", "final-check"}:
            metadata_only = [
                {"page": row["page"], "template": template, "variant": row["variant"]}
                for row in rows
                if row["variant"] and not row["surface"]
            ]
            missing_family = [
                {"page": row["page"], "template": template, "variant": row["variant"], "surface": row["surface"]}
                for row in rows
                if row["surface"] and not row["surface_family"]
            ]
            metadata_only_surface_pages.extend(metadata_only)
            missing_surface_family_pages.extend(missing_family)
        else:
            metadata_only = []
            missing_family = []
        repeated_threshold = repeated_threshold_for(template)
        required_variants = 3 if len(rows) >= repeated_threshold * 2 else 2
        if missing or metadata_only or missing_family or len(unique_structures) < required_variants:
            weak_template_groups.append(
                {
                    "template": template,
                    "count": len(rows),
                    "unique_variants": sorted(set(row["normalized_variant"] for row in rows if row["normalized_variant"])),
                    "unique_surfaces": unique_structures,
                    "unique_surface_families": sorted(set(row["surface_family"] for row in rows if row["surface_family"])),
                    "required_unique_variants": required_variants,
                    "repeated_threshold": repeated_threshold,
                    "missing_variant_pages": [row["page"] for row in rows if not row["variant"]],
                    "metadata_only_surface_pages": [row["page"] for row in metadata_only],
                    "missing_surface_family_pages": [row["page"] for row in missing_family],
                }
            )

    dense_structure_windows: list[dict[str, Any]] = []
    window_size = 12
    dense_threshold = 4 if asset_mode == ASSET_MODE_FINAL else 5
    for start in range(0, max(0, len(pages) - window_size + 1)):
        window = pages[start : start + window_size]
        keys = [
            f"{str(page.get('template') or '').strip()}:{page_rendered_surface_key(page) or 'missing'}"
            for page in window
            if str(page.get("template") or "").strip() in STRUCTURE_LIBRARY_REPEAT_TEMPLATES
        ]
        counts = Counter(keys)
        dense = {key: count for key, count in counts.items() if count >= dense_threshold}
        if dense:
            dense_structure_windows.append({"pages": [start + 1, start + len(window)], "structures": dense})

    ok = not weak_template_groups and not dense_structure_windows
    return {
        "ok": ok,
        "checked": True,
        "default_repeated_threshold": 4 if asset_mode == ASSET_MODE_FINAL else 5,
        "dense_threshold": dense_threshold,
        "window_size": window_size,
        "repeated_groups": {template: len(rows) for template, rows in repeated_groups.items()},
        "weak_template_groups": weak_template_groups,
        "missing_variant_pages": missing_variant_pages,
        "metadata_only_surface_pages": metadata_only_surface_pages,
        "missing_surface_family_pages": missing_surface_family_pages,
        "dense_structure_windows": dense_structure_windows,
        "template_variant_counts": {
            template: dict(Counter(row["normalized_variant"] or "missing" for row in rows))
            for template, rows in by_template.items()
        },
        "template_surface_counts": {
            template: dict(Counter(page_rendered_surface_key(row) or "missing" for row in rows))
            for template, rows in by_template.items()
        },
        "required": (
            "Long v2 books need an optional structure library for any repeated student-book template family. "
            "The book may choose not to use every structure, but repeated families need rendered data-surface "
            "markers and visible surface differences so topic/content can call a different form when needed."
        ),
    }


def asset_metadata_policy(asset: dict[str, Any], *, asset_mode: str, is_visual_ref: bool) -> dict[str, Any]:
    required = ["id", "path", "kind", "role", "status", "text_policy", "source_note", "focus"]
    missing = [field for field in required if not str(asset.get(field) or "").strip()]
    kind = str(asset.get("kind") or "").strip().lower()
    status = str(asset.get("status") or "").strip().lower()
    text_policy = str(asset.get("text_policy") or "").strip().lower()
    prompt = str(asset.get("prompt") or asset.get("generation_prompt") or asset.get("prompt_summary") or "").strip()
    blob = " ".join(str(asset.get(key) or "") for key in ("id", "path", "kind", "role", "status", "source_note")).lower()
    role_blob = " ".join(str(asset.get(key) or "") for key in ("role", "purpose", "use_role")).lower()
    is_cover_ref = bool(COVER_ASSET_ROLE_RE.search(role_blob))
    content_brief = str(asset.get("content_brief") or "").strip()
    visual_direction = str(asset.get("visual_direction") or "").strip()
    uniqueness_note = str(asset.get("uniqueness_note") or "").strip()
    concept_text = " ".join([content_brief, visual_direction, uniqueness_note]).lower()
    scene_policy = asset_interpretable_scene_policy(asset)
    nature_first_policy = asset_nature_first_policy(asset)
    license_status_policy = asset_license_status_policy(asset)
    checks = {
        "required_manifest_fields_present": not missing,
        "text_policy_blocks_image_text": "text" in text_policy
        and ("no visible" in text_policy or "no text" in text_policy)
        and any(term in text_policy for term in ("question", "answer", "teaching", "正文", "题干", "答案")),
        "license_status_matches_source_note": license_status_policy["ok"],
        "final_kind_allowed": True,
        "final_status_approved": True,
        "final_not_placeholder": True,
        "imagegen_prompt_recorded": True,
        "final_cover_content_concept_recorded": True,
        "final_cover_uniqueness_recorded": True,
        "final_visual_asset_interpretable_scene": True,
        "nature_first_family_or_rationale": True,
    }
    if asset_mode == ASSET_MODE_FINAL and is_visual_ref:
        checks["final_kind_allowed"] = kind in FINAL_ASSET_KINDS
        checks["final_status_approved"] = any(term in status for term in ("final", "approved", "licensed", "owned", "cleared"))
        checks["final_not_placeholder"] = kind not in PLACEHOLDER_ASSET_KINDS and not any(term in blob for term in PLACEHOLDER_ASSET_TERMS)
        checks["imagegen_prompt_recorded"] = kind != "imagegen" or bool(prompt)
        checks["final_visual_asset_interpretable_scene"] = scene_policy["ok"]
        checks["nature_first_family_or_rationale"] = nature_first_policy["ok"]
        if is_cover_ref:
            checks["final_cover_content_concept_recorded"] = bool(content_brief and visual_direction)
            checks["final_cover_uniqueness_recorded"] = bool(uniqueness_note) and not any(
                term in concept_text for term in ("generic", "template", "starter", "same as previous", "reuse previous")
            )
    blocking_checks = {key: value for key, value in checks.items() if key != "nature_first_family_or_rationale"}
    return {
        "ok": all(blocking_checks.values()),
        "checks": checks,
        "nonblocking_checks": ["nature_first_family_or_rationale"],
        "missing_fields": missing,
        "kind": kind,
        "status": status,
        "is_visual_ref": is_visual_ref,
        "is_cover_ref": is_cover_ref,
        "asset_mode": asset_mode,
        "scene_policy": scene_policy,
        "nature_first_policy": nature_first_policy,
        "license_status_policy": license_status_policy,
    }


def as_set(value: Any, default: set[str]) -> set[str]:
    if value is None:
        return set(default)
    if isinstance(value, str):
        return {item.strip() for item in value.split(",") if item.strip()}
    return {str(item).strip() for item in value if str(item).strip()}


def normalize_answer_visibility(value: Any) -> str:
    raw = str(value or "").strip().lower().replace("_", "-")
    aliases = {
        "": "off",
        "none": "off",
        "off": "off",
        "student": "student",
        "student-only": "student",
        "student-clean": "student",
        "student-no-answers": "student",
        "student-with-key": "student-with-answer-key",
        "student-answer-key": "student-with-answer-key",
        "student-with-answer-key": "student-with-answer-key",
        "teacher": "teacher",
        "teacher-only": "teacher",
        "teacher-key": "teacher",
    }
    return aliases.get(raw, raw)


def answer_visibility_policy(soup: BeautifulSoup, *, mode: str) -> dict[str, Any]:
    normalized = normalize_answer_visibility(mode)
    templates = [
        str(section.get("data-template") or "").strip()
        for section in soup.select(".sheet")
        if str(section.get("data-template") or "").strip()
    ]
    teacher_only_nodes = soup.select('[data-teacher-only="true"]')
    answer_key_nodes = soup.select('[data-component="answer-key-page"]')

    blocked_templates: list[str] = []
    blocked_components: list[str] = []
    if normalized == "student":
        blocked_templates = sorted({template for template in templates if template in {"answer-key", "teacher-answer-key"}})
        if answer_key_nodes:
            blocked_components.append("answer-key-page")
    elif normalized == "student-with-answer-key":
        blocked_templates = sorted({template for template in templates if template == "teacher-answer-key"})
        if teacher_only_nodes:
            blocked_components.append("teacher-only")

    ok = normalized in {"off", "teacher"} or (not blocked_templates and not blocked_components and not teacher_only_nodes)
    if normalized == "student-with-answer-key":
        ok = not blocked_templates and not teacher_only_nodes
    return {
        "ok": ok,
        "mode": normalized,
        "templates": templates,
        "blocked_templates": blocked_templates,
        "blocked_components": blocked_components,
        "teacher_only_nodes": len(teacher_only_nodes),
        "answer_key_nodes": len(answer_key_nodes),
    }


def teacher_book_integrity_policy(soup: BeautifulSoup, raw_html: str, *, profile: str, mode: str) -> dict[str, Any]:
    normalized = normalize_answer_visibility(mode)
    checked = profile.startswith("teacher") or normalized == "teacher"
    if not checked:
        return {"ok": True, "checked": False}
    sheets = soup.select(".sheet")
    templates = [str(section.get("data-template") or "").strip() for section in sheets]
    guide_pages = [
        str(section.get("data-page") or "")
        for section in sheets
        if str(section.get("data-template") or "").strip() == "teacher-guide-page"
    ]
    teacher_notes = soup.select('[data-component="teacher-page-note"]')
    answer_strips = soup.select('[data-component="teacher-answer-strip"]')
    wrong_guide_shells = [
        str(section.get("data-page") or "")
        for section in sheets
        if str(section.get("data-template") or "").strip() == "teacher-answer-key"
        and "Teacher Guide" in re.sub(r"\s+", " ", section.get_text(" "))
    ]
    boilerplate_terms = [
        "执行时先给学生",
        "点名时先追问",
        "不提前报出规则或答案",
        "下课前把本环节产出收回",
        "Student profile excludes this page",
        "Classroom prompts",
    ]
    boilerplate_hits = {term: raw_html.count(term) for term in boilerplate_terms if raw_html.count(term)}
    first_teacher_backmatter = next(
        (
            idx
            for idx, section in enumerate(sheets, 1)
            if str(section.get("data-template") or "").strip() in {"teacher-answer-key", "teacher-guide-page"}
            or str(section.get("data-section") or "").strip() == "backmatter"
        ),
        None,
    )
    appendix_only_risk = bool(first_teacher_backmatter and first_teacher_backmatter > 10 and not teacher_notes and not answer_strips)
    checks = {
        "teacher_guide_template_present": bool(guide_pages),
        "teacher_page_notes_present": len(teacher_notes) >= 4,
        "teacher_answer_strips_present": len(answer_strips) >= 4,
        "teacher_guide_not_answer_key_shell": not wrong_guide_shells,
        "teacher_boilerplate_absent": not boilerplate_hits,
        "not_appendix_only": not appendix_only_risk,
    }
    return {
        "ok": all(checks.values()),
        "checked": True,
        "checks": checks,
        "templates": templates,
        "guide_pages": guide_pages,
        "teacher_page_note_count": len(teacher_notes),
        "teacher_answer_strip_count": len(answer_strips),
        "wrong_guide_shells": wrong_guide_shells,
        "boilerplate_hits": boilerplate_hits,
        "appendix_only_risk": appendix_only_risk,
        "required": "Teacher books must be true teacher editions with integrated teacher notes/answer strips and real teacher-guide pages. Student-book-plus-appendix is not enough unless explicitly labeled as appendix mode.",
    }


def profile_qa_config(
    book: dict[str, Any],
    spec: dict[str, Any],
    *,
    profile: str | None = None,
    min_pages: int | None,
    max_pages: int | None,
    required_templates: list[str] | None,
    required_components: list[str] | None,
    asset_mode: str | None = None,
) -> dict[str, Any]:
    qa = book.get("qa") or {}
    profile_qa = spec.get("qa") or {}
    return {
        "min_pages": min_pages or profile_qa.get("min_pages") or qa.get("min_pages") or 8,
        "max_pages": max_pages or profile_qa.get("max_pages") or qa.get("max_pages") or 12,
        "required_templates": set(required_templates)
        if required_templates
        else as_set(profile_qa.get("required_templates") or qa.get("required_templates"), REQUIRED_TEMPLATES),
        "required_components": set(required_components)
        if required_components
        else as_set(profile_qa.get("required_components") or qa.get("required_components"), REQUIRED_COMPONENTS),
        "asset_mode": configured_asset_mode(book, spec, asset_mode),
        "page_family_mode": str(profile_qa.get("page_family_mode") or qa.get("page_family_mode") or "").strip(),
        "answer_visibility": configured_answer_visibility(book, spec, profile=profile),
        "source_inputs": as_list(qa.get("source_inputs")) + as_list(profile_qa.get("source_inputs")),
    }


def resolve_output_path(root: Path, out: Path, profile: str, spec: dict[str, Any], kind: str) -> tuple[Path, dict[str, Any]]:
    key = f"output_{kind}"
    nested = spec.get("outputs") or {}
    configured = spec.get(key) or nested.get(kind)
    if configured:
        path = Path(configured)
        return (root / path if not path.is_absolute() else path).resolve(), {"mode": "configured", "key": key}

    default = out / f"textbook-template-sample-{profile}.{kind}"
    if default.exists():
        return default, {"mode": "default"}

    matches = sorted(out.glob(f"*{profile}*.{kind}"), key=lambda path: path.stat().st_mtime, reverse=True)
    if matches:
        return matches[0], {"mode": "discovered", "candidates": [match.name for match in matches[:5]]}
    return default, {"mode": "missing-default"}


def resolve_review_artifact(root: Path | None, review_path: Path, value: str | None) -> Path | None:
    if not value:
        return None
    cleaned = value.strip().strip("`").strip()
    if not cleaned:
        return None
    markdown_match = re.match(r"\[[^\]]+\]\((.+?)\)", cleaned)
    if markdown_match:
        cleaned = markdown_match.group(1).strip()
    cleaned = cleaned.strip("<>")
    candidate = Path(cleaned)
    if candidate.is_absolute():
        return candidate
    if root is not None:
        return root / candidate
    return review_path.parent / candidate


def review_artifact_evidence(
    root: Path | None,
    review_path: Path,
    *,
    profile: str | None,
    contact_sheet: str | None,
    key_pages: list[str],
) -> dict[str, Any]:
    if root is None:
        return {
            "contact_sheet_exists": bool(contact_sheet),
            "contact_sheet_profile_match": True,
            "contact_sheet_path": contact_sheet,
            "key_pages_exist": bool(key_pages),
            "key_pages_existing_count": len([item for item in key_pages if item.strip()]),
            "key_pages_declared_count": len([item for item in key_pages if item.strip()]),
            "key_pages_profile_match": True,
            "key_pages_under_rendered": True,
            "review_fresh_after_artifacts": True,
            "review_mtime": artifact_mtime(review_path),
            "max_reviewed_artifact_mtime": None,
            "missing_key_pages": [],
        }
    contact_path = resolve_review_artifact(root, review_path, contact_sheet)
    key_page_paths = [resolve_review_artifact(root, review_path, item) for item in key_pages if item.strip()]
    key_page_paths = [path for path in key_page_paths if path is not None]
    existing_key_pages = [path for path in key_page_paths if path.exists()]
    profile_key_re = re.compile(rf"^{re.escape(profile or '')}-page-\d{{3,}}\.png$") if profile else None
    key_pages_profile_match = True
    if profile_key_re and key_page_paths:
        key_pages_profile_match = all(profile_key_re.match(path.name) for path in key_page_paths)
    key_pages_under_rendered = True
    if root is not None and key_page_paths:
        rendered_dir = (root / "_qa" / "rendered-pages").resolve()
        key_pages_under_rendered = all(path.resolve().parent == rendered_dir for path in key_page_paths)
    contact_profile_match = True
    if profile and contact_path:
        contact_profile_match = contact_path.name == f"contact-sheet-{profile}.png"
    review_time = artifact_mtime(review_path)
    reviewed_artifact_times = []
    if contact_path and contact_path.exists():
        reviewed_artifact_times.append(artifact_mtime(contact_path))
    reviewed_artifact_times.extend(artifact_mtime(path) for path in existing_key_pages)
    reviewed_artifact_times = [mtime for mtime in reviewed_artifact_times if mtime is not None]
    max_reviewed_artifact_time = max(reviewed_artifact_times) if reviewed_artifact_times else None
    review_fresh_after_artifacts = (
        bool(review_time is not None and max_reviewed_artifact_time is not None and review_time + 0.5 >= max_reviewed_artifact_time)
        if key_page_paths or contact_path
        else False
    )
    return {
        "contact_sheet_exists": bool(contact_path and contact_path.exists()),
        "contact_sheet_profile_match": contact_profile_match,
        "contact_sheet_path": rel(root, contact_path) if root is not None and contact_path else str(contact_path) if contact_path else None,
        "key_pages_exist": len(existing_key_pages) == len(key_page_paths) and bool(key_page_paths),
        "key_pages_existing_count": len(existing_key_pages),
        "key_pages_declared_count": len(key_page_paths),
        "key_pages_profile_match": key_pages_profile_match,
        "key_pages_under_rendered": key_pages_under_rendered,
        "review_fresh_after_artifacts": review_fresh_after_artifacts,
        "review_mtime": review_time,
        "max_reviewed_artifact_mtime": max_reviewed_artifact_time,
        "missing_key_pages": [
            rel(root, path) if root is not None else str(path)
            for path in key_page_paths
            if not path.exists()
        ],
    }


def parse_human_review(path: Path, *, root: Path | None = None, profile: str | None = None) -> dict[str, Any]:
    if not path.exists():
        return {"ok": False, "reason": "missing"}
    text = path.read_text(encoding="utf-8", errors="replace")
    status_match = re.search(r"FINAL_VISUAL_REVIEW:\s*([A-Z_]+)", text)
    status = status_match.group(1) if status_match else None
    score_match = re.search(r"Score:\s*([0-9]+(?:\.[0-9]+)?)\s*/\s*10", text)
    p0_match = re.search(r"P0:\s*(\d+)", text)
    p1_match = re.search(r"P1:\s*(\d+)", text)
    reviewer_match = re.search(r"Reviewer:\s*(.+)", text)
    checked_match = re.search(r"Checked:\s*(.+)", text)
    contact_match = re.search(r"Contact sheet:\s*(.+)", text)
    key_pages_match = re.search(r"Key pages:\s*(.+)", text)
    reviewer = reviewer_match.group(1).strip() if reviewer_match else None
    checked = [item.strip() for item in checked_match.group(1).split(",")] if checked_match else []
    contact_sheet = contact_match.group(1).strip() if contact_match else None
    key_pages = [item.strip() for item in key_pages_match.group(1).split(",")] if key_pages_match else []
    forbidden_reviewer = bool(reviewer and re.search(r"\b(agent-self|self|same-agent)\b", reviewer, re.I))
    allowed_reviewer = bool(
        reviewer
        and re.search(
            r"^(user-confirmed|independent-review|external-review:[A-Za-z0-9_.:-]+|sub-agent-review:[A-Za-z0-9_.:-]+)\b",
            reviewer,
            re.I,
        )
    )
    has_diagnosis = "Visual diagnosis:" in text and "Weak pages:" in text
    has_render_evidence = bool(contact_sheet and len([item for item in key_pages if item]) >= 4)
    has_canon_comparison = "Canon comparison:" in text
    has_reject_patterns = "Reject patterns checked:" in text
    has_font_decision = "Font decision:" in text
    artifact_evidence = review_artifact_evidence(
        root,
        path,
        profile=profile,
        contact_sheet=contact_sheet,
        key_pages=key_pages,
    )
    review_paths_ok = all(
        artifact_evidence[key]
        for key in (
            "contact_sheet_exists",
            "contact_sheet_profile_match",
            "key_pages_exist",
            "key_pages_profile_match",
            "key_pages_under_rendered",
            "review_fresh_after_artifacts",
        )
    )
    ok = (
        status == "PASS"
        and score_match is not None
        and float(score_match.group(1)) >= 9.5
        and p0_match is not None
        and int(p0_match.group(1)) == 0
        and p1_match is not None
        and int(p1_match.group(1)) == 0
        and reviewer is not None
        and not forbidden_reviewer
        and allowed_reviewer
        and len([item for item in checked if item]) >= 4
        and has_diagnosis
        and has_render_evidence
        and has_canon_comparison
        and has_reject_patterns
        and has_font_decision
        and review_paths_ok
    )
    return {
        "ok": ok,
        "status": status,
        "formal_fail": status == "FAIL",
        "score": float(score_match.group(1)) if score_match else None,
        "p0": int(p0_match.group(1)) if p0_match else None,
        "p1": int(p1_match.group(1)) if p1_match else None,
        "reviewer": reviewer,
        "allowed_reviewer": allowed_reviewer,
        "checked_count": len([item for item in checked if item]),
        "has_diagnosis": has_diagnosis,
        "contact_sheet": contact_sheet,
        "key_page_count": len([item for item in key_pages if item]),
        "has_render_evidence": has_render_evidence,
        "has_canon_comparison": has_canon_comparison,
        "has_reject_patterns": has_reject_patterns,
        "has_font_decision": has_font_decision,
        "forbidden_reviewer": forbidden_reviewer,
        "review_paths_ok": review_paths_ok,
        "artifact_evidence": artifact_evidence,
    }


def validate(
    root: Path,
    profile: str,
    require_human_review: bool = False,
    *,
    min_pages: int | None = None,
    max_pages: int | None = None,
    required_templates: list[str] | None = None,
    required_components: list[str] | None = None,
    asset_mode: str | None = None,
) -> dict[str, Any]:
    root = root.expanduser().resolve()
    out = root / "outputs"
    qa = root / "_qa"
    issues: list[dict[str, Any]] = []
    evidence: dict[str, Any] = {"profile": profile}

    try:
        book = load_book(root)
    except Exception as exc:
        issues.append(issue("P1", "BOOK_YAML_INVALID", str(exc), "book.yaml"))
        return make_report(root, profile, issues, evidence)

    profiles = book.get("profiles") or {}
    if profile not in profiles:
        issues.append(issue("P1", "UNKNOWN_PROFILE", f"profile {profile!r} not in book.yaml", "book.yaml"))
        return make_report(root, profile, issues, evidence)
    spec = profiles[profile]
    qa_config = profile_qa_config(
        book,
        spec,
        profile=profile,
        min_pages=min_pages,
        max_pages=max_pages,
        required_templates=required_templates,
        required_components=required_components,
        asset_mode=asset_mode,
    )
    if qa_config["asset_mode"] not in VALID_ASSET_MODES:
        issues.append(
            issue(
                "P1",
                "UNKNOWN_ASSET_MODE",
                f"asset_mode must be one of {sorted(VALID_ASSET_MODES)}, got {qa_config['asset_mode']!r}",
                "book.yaml",
            )
        )
    evidence["qa_config"] = {
        "min_pages": qa_config["min_pages"],
        "max_pages": qa_config["max_pages"],
        "required_templates": sorted(qa_config["required_templates"]),
        "required_components": sorted(qa_config["required_components"]),
        "asset_mode": qa_config["asset_mode"],
        "page_family_mode": qa_config["page_family_mode"] or "off",
        "answer_visibility": qa_config["answer_visibility"],
        "source_inputs": qa_config["source_inputs"],
    }
    if qa_config["answer_visibility"] not in ANSWER_VISIBILITY_MODES:
        issues.append(
            issue(
                "P1",
                "UNKNOWN_ANSWER_VISIBILITY",
                f"answer_visibility must be one of {sorted(ANSWER_VISIBILITY_MODES)}, got {qa_config['answer_visibility']!r}",
                "book.yaml",
            )
        )

    html_path, html_resolution = resolve_output_path(root, out, profile, spec, "html")
    pdf_path, pdf_resolution = resolve_output_path(root, out, profile, spec, "pdf")
    evidence["html"] = rel(root, html_path)
    evidence["pdf"] = rel(root, pdf_path)
    evidence["output_resolution"] = {"html": html_resolution, "pdf": pdf_resolution}
    if not html_path.exists():
        issues.append(issue("P1", "HTML_MISSING", "Run tools/build.py for this profile.", rel(root, html_path)))
        return make_report(root, profile, issues, evidence)
    if not pdf_path.exists():
        issues.append(issue("P1", "PDF_MISSING", "Run tools/render_pdf.py for this profile.", rel(root, pdf_path)))
        return make_report(root, profile, issues, evidence)

    source_freshness = source_output_freshness_checks(
        root,
        html_path=html_path,
        pdf_path=pdf_path,
        configured_inputs=qa_config["source_inputs"],
    )
    evidence["source_output_freshness"] = {
        **source_freshness,
        "latest_sources": [
            {
                **item,
                "path": rel(root, Path(item["path"])),
            }
            for item in source_freshness.get("latest_sources", [])
        ],
    }
    if not source_freshness["ok"]:
        issues.append(
            issue(
                "P1",
                "SOURCE_OUTPUTS_STALE",
                "HTML/PDF must be generated after the current book.yaml, pages, manifest, theme, assets, renderer inputs, and configured qa.source_inputs. Rerun tools/build.py and tools/render_pdf.py from the current source tree.",
                rel(root, html_path),
            )
        )

    duplicate_page_files = stale_duplicate_page_files(root)
    evidence["stale_duplicate_page_files"] = duplicate_page_files
    if duplicate_page_files["count"]:
        issues.append(
            issue(
                "P1",
                "STALE_DUPLICATE_PAGE_FILES",
                "Generated page directories must not contain stale Finder/iCloud-style duplicates such as `pages/0002-title 2.md`; delete them before review because they pollute source scans and future agent searches.",
                "pages/",
            )
        )

    qa_conflict_files = qa_evidence_conflict_files(root)
    evidence["qa_evidence_conflict_files"] = qa_conflict_files
    if qa_conflict_files["count"]:
        issues.append(
            issue(
                "P1",
                "QA_EVIDENCE_CONFLICT_FILES",
                "QA evidence folders must not contain Finder/iCloud-style duplicate contact sheets, review sheets, visual reviews, or QA reports such as `_qa/contact-sheet-book-trim 2.png`; delete them and regenerate evidence before review.",
                "_qa/",
            )
        )

    inactive_page_files = inactive_page_source_files(root, book)
    evidence["inactive_page_source_files"] = inactive_page_files
    if inactive_page_files["count"]:
        issues.append(
            issue(
                "P1",
                "INACTIVE_PAGE_SOURCE_FILES",
                "Every generated `pages/*.md` file must be referenced by book.yaml. Unreferenced page files can preserve old wording, stale teacher keys, or rejected visual variants, and they pollute source scans/reviews. Regenerate cleanly or delete the inactive files before QA.",
                "pages/",
            )
        )

    raw_html = html_path.read_text(encoding="utf-8", errors="replace")
    visible_html, soup = html_text(html_path)
    template_counts = Counter(section.get("data-template") for section in soup.select(".sheet"))
    component_counts = Counter(node.get("data-component") for node in soup.select("[data-component]"))
    evidence["template_counts"] = dict(template_counts)
    evidence["component_counts"] = dict(component_counts)
    a4_only_profiles = a4_only_profile_policy(book, raw_html)
    evidence["a4_only_profile_policy"] = a4_only_profiles
    if not a4_only_profiles["ok"]:
        issues.append(
            issue(
                "P1",
                "A4_ONLY_PROFILE_RESIDUE",
                "A4-only lesson-pack projects must not keep book-trim profiles or book-trim output paths. Ask the user before producing book-trim again.",
                "book.yaml",
            )
        )
    duplicated_question_blanks = duplicated_question_blank_hits(soup)
    evidence["duplicated_question_blanks"] = duplicated_question_blanks
    if duplicated_question_blanks:
        issues.append(
            issue(
                "P1",
                "QUESTION_INLINE_BLANK_WITH_WRITE_LINE",
                "Question-line prompts that already receive write-line answer space must not also render inline .blank slots; strip author underscores in question-lines and let the dedicated write-line carry the answer.",
                rel(root, html_path),
            )
        )
    exam_stem_slots = exam_stem_slot_policy(soup, raw_html)
    evidence["exam_stem_slot_policy"] = exam_stem_slots
    if not exam_stem_slots["ok"]:
        issues.append(
            issue(
                "P1",
                "EXAM_STEM_SLOT_DRIFT",
                "Guided MCQ/cloze stems must not use generic .blank. Render author ____ as .exam-stem-slot with punctuation bound in .exam-stem-keep.",
                rel(root, html_path),
            )
        )
    a4_sentence_map_surface = a4_sentence_map_surface_policy(soup, profile)
    evidence["a4_sentence_map_surface_policy"] = a4_sentence_map_surface
    if not a4_sentence_map_surface["ok"]:
        issues.append(
            issue(
                "P1",
                "A4_SENTENCE_MAP_TABLE_CRAMP",
                "A4 sentence-map pages must render as card/stack surfaces with data-surface markers, not wide three-column tables.",
                rel(root, html_path),
            )
        )
    missing_templates = sorted(qa_config["required_templates"] - set(template_counts))
    missing_components = sorted(qa_config["required_components"] - set(component_counts))
    if missing_templates:
        issues.append(issue("P1", "MISSING_TEMPLATES", ", ".join(missing_templates), rel(root, html_path)))
    if missing_components:
        issues.append(issue("P1", "MISSING_COMPONENTS", ", ".join(missing_components), rel(root, html_path)))
    answer_visibility = answer_visibility_policy(soup, mode=qa_config["answer_visibility"])
    evidence["answer_visibility"] = answer_visibility
    if not answer_visibility["ok"]:
        issues.append(
            issue(
                "P1",
                "STUDENT_ANSWER_VISIBILITY_LEAK",
                f"answer_visibility={answer_visibility['mode']} blocked templates={answer_visibility['blocked_templates']} blocked components={answer_visibility['blocked_components']} teacher_only_nodes={answer_visibility['teacher_only_nodes']}",
                rel(root, html_path),
            )
        )
    teacher_integrity = teacher_book_integrity_policy(
        soup,
        raw_html,
        profile=profile,
        mode=qa_config["answer_visibility"],
    )
    evidence["teacher_book_integrity_policy"] = teacher_integrity
    if not teacher_integrity["ok"]:
        issues.append(
            issue(
                "P1",
                "TEACHER_BOOK_APPENDIX_ONLY_DRIFT",
                "Teacher profile must include integrated teacher notes/answer strips and real teacher-guide pages. Do not ship a student book plus appended answer tables as a Teacher's Book.",
                rel(root, html_path),
            )
        )
    page_family = page_family_coverage_policy(
        [{"template": section.get("data-template")} for section in soup.select(".sheet")],
        mode=qa_config["page_family_mode"],
        answer_visibility=qa_config["answer_visibility"],
    )
    evidence["page_family_coverage"] = page_family
    if not page_family["ok"]:
        issues.append(
            issue(
                "P1",
                "V2_PAGE_FAMILY_COVERAGE_MISSING",
                json.dumps(page_family["missing_families"], ensure_ascii=False),
                rel(root, html_path),
            )
        )

    starter_sample = is_starter_sample(book, spec)
    generic_identity = generic_book_identity_policy(
        book,
        asset_mode=qa_config["asset_mode"],
        starter_sample=starter_sample,
    )
    evidence["generic_book_identity"] = generic_identity
    if not generic_identity["ok"]:
        issues.append(
            issue(
                "P1",
                "GENERIC_BOOK_IDENTITY_WEAK",
                "A final no-student-name book needs a publishable identity, not only a functional course label. Add identity.cover_title, identity.positioning, identity.audience, and identity.front_matter_role; avoid defaulting the visible title to a bare plan/workbook label.",
                "book.yaml",
            )
        )

    rendered_pages = rendered_page_records(soup)
    page_role_rhythm = page_role_rhythm_policy(
        rendered_pages,
        page_family_mode=qa_config["page_family_mode"],
        asset_mode=qa_config["asset_mode"],
    )
    evidence["page_role_rhythm"] = page_role_rhythm
    if not page_role_rhythm["ok"]:
        issues.append(
            issue(
                "P2",
                "PAGE_ROLE_RHYTHM_WEAK",
                "Long v2 books should not become long runs of practice/form pages. Insert or redesign editorial anchors such as unit openers, article/evidence pages, photo passages, handbook/reference pages, or answer-key back matter so the contact sheet reads as a book.",
                rel(root, html_path),
            )
        )
    page_role_variants = page_role_variant_policy(
        rendered_pages,
        page_family_mode=qa_config["page_family_mode"],
        asset_mode=qa_config["asset_mode"],
    )
    evidence["page_role_variants"] = page_role_variants
    if not page_role_variants["ok"]:
        issues.append(
            issue(
                "P2",
                "PAGE_ROLE_VARIANT_RHYTHM_WEAK",
                "Planner/final-check pages in long v2 books need semantic variants; repeated form families should render as distinct workbook roles rather than copy-pasted planning/check pages.",
                rel(root, html_path),
            )
        )
    page_structure_variants = page_structure_variant_library_policy(
        rendered_pages,
        page_family_mode=qa_config["page_family_mode"],
        asset_mode=qa_config["asset_mode"],
    )
    evidence["page_structure_variant_library"] = page_structure_variants
    if not page_structure_variants["ok"]:
        issues.append(
            issue(
                "P2",
                "PAGE_STRUCTURE_VARIANT_LIBRARY_WEAK",
                "Long v2 books need an optional structure library for repeated template families such as activity, skill-method, categorizing-chart, exam-mini-set, handbook, vocab-bank, article/evidence, and sentence-map pages. Add semantic variants so the format can change when the content calls for it.",
                rel(root, html_path),
            )
        )

    try:
        text = pdf_text(pdf_path)
    except Exception as exc:
        issues.append(issue("P1", "PDF_TEXT_EXTRACTION_FAILED", str(exc), rel(root, pdf_path)))
        text = ""
    evidence["pdf_text_chars"] = len(text.strip())
    if len(text.strip()) < 1200:
        issues.append(issue("P1", "PDF_TEXT_TOO_SHORT", f"extracted {len(text.strip())} chars", rel(root, pdf_path)))

    underscore_hits = literal_underscore_runs({"generated-html": raw_html, "pdf-text": text})
    evidence["literal_underscore_runs"] = underscore_hits
    if underscore_hits:
        issues.append(
            issue(
                "P1",
                "LITERAL_UNDERSCORE_BLANKS",
                "Generated output still contains 3+ underscore runs; render fill-in blanks as low-baseline .blank elements.",
                rel(root, html_path),
            )
        )

    blank_css = blank_baseline_css_checks(raw_html)
    evidence["blank_baseline_css"] = blank_css
    if not blank_css["ok"]:
        issues.append(
            issue(
                "P1",
                "BLANK_BASELINE_CSS_WEAK",
                "Generated HTML must render blanks with context-specific writing/cloze rules: .blank -0.82em, .question-lines .blank -0.88em, .paragraph-practice p .blank -0.22em, .record-prompt .blank -0.32em, inline cloze containers -0.30em, word-box phrase blanks -0.26em with no-wrap items, and handbook mini-rule blanks -0.24em; legacy centered values are blocked.",
                rel(root, html_path),
            )
        )

    title_lockup = title_lockup_css_checks(raw_html)
    evidence["title_lockup_css"] = title_lockup
    if not title_lockup["ok"]:
        issues.append(
            issue(
                "P1",
                "MIXED_TITLE_SCALE_DRIFT",
                "Mixed cover/title-page lockups such as `IELTS备考计划 for Sample Learner` must keep the suffix at the same optical scale and weight inside the H1, or move it to a true subtitle. Do not shrink `for Sample Learner` with .86em/.85em/absolute-small styling.",
                rel(root, html_path),
            )
        )

    cover_brand = cover_brand_checks(raw_html, book)
    evidence["cover_brand"] = cover_brand
    if not cover_brand["checks"]["brand_text_present"] or not cover_brand["checks"]["cover_brand_node_present"] or not cover_brand["checks"]["brand_bottom_right_css"]:
        issues.append(
            issue(
                "P1",
                "COVER_BRAND_MARK_MISSING",
                "Cover must place `Eric Teaching Studio` as a bottom-right `.cover-brand` mark; do not hide the studio identity in title-page metadata only.",
                rel(root, html_path),
            )
        )
    if not cover_brand["checks"]["brand_contrast_css"]:
        issues.append(
            issue(
                "P1",
                "COVER_BRAND_CONTRAST_WEAK",
                "Cover brand must include a contrast treatment such as a restrained scrim, background, text shadow, or similar CSS so `Eric Teaching Studio` remains readable on complex cover photos.",
                rel(root, html_path),
            )
        )
    if not cover_brand["checks"]["cover_top_level_badge_absent"]:
        issues.append(
            issue(
                "P1",
                "COVER_TOP_LEVEL_BADGE",
                "Course stage/level belongs on title/navigation pages, not as a cover top-right badge.",
                rel(root, html_path),
            )
        )

    unit_opener_composition = unit_opener_composition_checks(raw_html)
    evidence["unit_opener_composition"] = unit_opener_composition
    if not unit_opener_composition["ok"]:
        issues.append(
            issue(
                "P1",
                "STACKED_OPENER_PROMPT_FLOAT",
                "Unit opener prompts must be integrated into the objectives band, not floated as a separate photo caption that can visually collide with the band. Use .objectives-intro, .opener-prompt, and .objectives-list inside .objectives-band.",
                rel(root, html_path),
            )
        )
    unit_opener_variation = unit_opener_variation_checks(raw_html)
    evidence["unit_opener_variation"] = unit_opener_variation
    if not unit_opener_variation["ok"]:
        issues.append(
            issue(
                "P2",
                "UNIT_OPENER_VARIATION_WEAK",
                "Long books should not reuse one opener color and one structure for every unit. Add per-unit accent/layout metadata and at least two visible opener structures.",
                rel(root, html_path),
            )
        )

    checklist_control = checklist_control_css_checks(raw_html)
    evidence["checklist_control_css"] = checklist_control
    if not checklist_control["ok"]:
        issues.append(
            issue(
                "P1",
                "CHECKLIST_CONTROL_SELECTOR_LEAK",
                "Editing checklist controls must use a named .check-mark marker and compact checklist blank override; generic selectors such as `.editing-checklist label span` can turn content blanks into checkbox-like rectangles.",
                rel(root, html_path),
            )
        )

    workbook_record = workbook_record_checks(raw_html)
    evidence["workbook_record"] = workbook_record
    if not workbook_record["ok"]:
        issues.append(
            issue(
                "P1",
                "WORKBOOK_RECORD_SURFACE_MISSING",
                "Generated workbook/activity page must include a cohesive record surface with header, numbered rows, and stable writing lines; loose trailing Q&A lines are not enough.",
                rel(root, html_path),
            )
        )

    planner_surface = planner_surface_checks(raw_html)
    evidence["planner_surface"] = planner_surface
    if not planner_surface["ok"]:
        issues.append(
            issue(
                "P1",
                "PLAIN_PLANNER_TABLE",
                "Generated planner must be tactile row-card writing surface, not a legacy table/spreadsheet layout.",
                rel(root, html_path),
            )
        )

    hits = forbidden_hits(visible_html + "\n" + text)
    evidence["forbidden_hits"] = hits
    if hits:
        issues.append(issue("P0", "PUBLIC_FORBIDDEN_TERM", json.dumps(hits, ensure_ascii=False), rel(root, pdf_path)))

    student_hits = student_forbidden_hits(visible_html + "\n" + text)
    evidence["student_forbidden_hits"] = student_hits
    if qa_config["answer_visibility"] in {"student", "student-with-answer-key"} and student_hits:
        issues.append(issue("P0", "STUDENT_PUBLIC_FORBIDDEN_TERM", json.dumps(student_hits, ensure_ascii=False), rel(root, pdf_path)))

    heading_language = visible_heading_language_policy(
        soup,
        book,
        visible_html + "\n" + text,
        answer_visibility=qa_config["answer_visibility"],
    )
    evidence["visible_heading_language_policy"] = heading_language
    if heading_language["ai_heading_hits"]:
        issues.append(
            issue(
                "P1",
                "VISIBLE_TITLE_AI_LANGUAGE",
                json.dumps(heading_language["ai_heading_hits"][:8], ensure_ascii=False),
                rel(root, html_path),
            )
        )
    if heading_language.get("workbook_cjk_heading_hits"):
        issues.append(
            issue(
                "P1",
                "WORKBOOK_TITLE_LANGUAGE_DRIFT",
                json.dumps(heading_language["workbook_cjk_heading_hits"][:8], ensure_ascii=False),
                rel(root, html_path),
            )
        )
    if heading_language["reading_cjk_heading_hits"]:
        issues.append(
            issue(
                "P1",
                "READING_TITLE_LANGUAGE_DRIFT",
                json.dumps(heading_language["reading_cjk_heading_hits"][:8], ensure_ascii=False),
                rel(root, html_path),
            )
        )

    renderer_label_language = renderer_ui_label_language_policy(
        raw_html,
        book,
        visible_html + "\n" + text,
        answer_visibility=qa_config["answer_visibility"],
    )
    evidence["renderer_ui_label_language_policy"] = renderer_label_language
    if renderer_label_language["hits"]:
        issues.append(
            issue(
                "P1",
                "RENDERER_UI_LABEL_LANGUAGE_DRIFT",
                json.dumps(renderer_label_language["hits"][:8], ensure_ascii=False),
                rel(root, html_path),
            )
        )

    blank_label_language = cloze_blank_label_language_policy(visible_html + "\n" + text, book)
    evidence["cloze_blank_label_language_policy"] = blank_label_language
    if blank_label_language["hits"]:
        issues.append(
            issue(
                "P1",
                "CLOZE_BLANK_LABEL_LANGUAGE_DRIFT",
                json.dumps(blank_label_language["hits"][:8], ensure_ascii=False),
                rel(root, html_path),
            )
        )

    prompt_language = student_prompt_language_policy(
        soup,
        book,
        visible_html + "\n" + text,
        answer_visibility=qa_config["answer_visibility"],
    )
    evidence["student_prompt_language_policy"] = prompt_language
    if prompt_language["hits"]:
        issues.append(
            issue(
                "P1",
                "STUDENT_PROMPT_LANGUAGE_DRIFT",
                json.dumps(prompt_language["hits"][:8], ensure_ascii=False),
                rel(root, html_path),
            )
        )

    starter_hits = starter_residue_hits(root, book, spec, visible_html, text)
    evidence["starter_residue_hits"] = starter_hits
    if starter_hits:
        issues.append(issue("P1", "STARTER_RESIDUE_FOUND", json.dumps(starter_hits, ensure_ascii=False), "book.yaml"))

    try:
        with fitz.open(pdf_path) as doc:
            evidence["page_count"] = doc.page_count
            if not (int(qa_config["min_pages"]) <= doc.page_count <= int(qa_config["max_pages"])):
                issues.append(
                    issue(
                        "P1",
                        "PAGE_COUNT_OUTSIDE_RANGE",
                        f"{doc.page_count} not in {qa_config['min_pages']}-{qa_config['max_pages']}",
                        rel(root, pdf_path),
                    )
                )
            size_failures = []
            blank_pages = []
            page_text_chars = []
            for number, page in enumerate(doc, 1):
                w = round(page.rect.width, 2)
                h = round(page.rect.height, 2)
                chars = len(page.get_text().strip())
                page_text_chars.append(chars)
                if abs(w - float(spec["page_width_pt"])) > 2 or abs(h - float(spec["page_height_pt"])) > 2:
                    size_failures.append([number, w, h])
                if chars < 5 and len(page.get_images(full=True)) == 0:
                    blank_pages.append(number)
            evidence["size_failures"] = size_failures
            evidence["blank_pages"] = blank_pages
            evidence["page_text_chars"] = page_text_chars
            if size_failures:
                issues.append(issue("P1", "PAGE_SIZE_MISMATCH", str(size_failures[:4]), rel(root, pdf_path)))
            if blank_pages:
                issues.append(issue("P1", "BLANK_PAGES", str(blank_pages), rel(root, pdf_path)))
            low_density_pages = [idx for idx, chars in enumerate(page_text_chars, 1) if chars < 180]
            if len(low_density_pages) > max(2, doc.page_count // 4):
                issues.append(issue("P2", "LOW_DENSITY_RADAR", str(low_density_pages), rel(root, pdf_path)))
    except Exception as exc:
        issues.append(issue("P1", "PDF_OPEN_FAILED", str(exc), rel(root, pdf_path)))

    manifest_path = root / "assets" / "manifest.json"
    if not manifest_path.exists():
        issues.append(issue("P1", "ASSET_MANIFEST_MISSING", "assets/manifest.json is required.", rel(root, manifest_path)))
    else:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            assets = manifest["assets"]
            refs = page_asset_refs(root, book)
            usage_policy = asset_usage_policy(assets, refs)
            evidence["asset_usage_policy"] = usage_policy
            if usage_policy["duplicate_manifest_ids"]:
                issues.append(
                    issue(
                        "P1",
                        "ASSET_ID_DUPLICATE_IN_MANIFEST",
                        json.dumps(usage_policy["duplicate_manifest_ids"], ensure_ascii=False),
                        rel(root, manifest_path),
                    )
                )
            if usage_policy["duplicate_paths"]:
                issues.append(
                    issue(
                        "P1",
                        "ASSET_PATH_REUSED_IN_MANIFEST",
                        json.dumps(usage_policy["duplicate_paths"], ensure_ascii=False),
                        rel(root, manifest_path),
                    )
                )
            if usage_policy["reused_asset_refs"]:
                issues.append(
                    issue(
                        "P1",
                        "ASSET_REUSED_ACROSS_PAGES",
                        json.dumps(usage_policy["reused_asset_refs"], ensure_ascii=False),
                        rel(root, manifest_path),
                    )
                )
            if usage_policy["cover_asset_inside_refs"]:
                issues.append(
                    issue(
                        "P1",
                        "COVER_ASSET_REUSED_INSIDE_BOOK",
                        json.dumps(usage_policy["cover_asset_inside_refs"], ensure_ascii=False),
                        rel(root, manifest_path),
                    )
                )
            if usage_policy["allowed_template_mismatches"]:
                issues.append(
                    issue(
                        "P1",
                        "ASSET_ALLOWED_TEMPLATE_MISMATCH",
                        json.dumps(usage_policy["allowed_template_mismatches"], ensure_ascii=False),
                        rel(root, manifest_path),
                    )
                )
            assets_by_id = {str(asset.get("id")): asset for asset in assets}
            missing_refs = [ref for ref in refs if ref["id"] not in assets_by_id]
            if missing_refs:
                issues.append(
                    issue(
                        "P1",
                        "ASSET_REFERENCE_MISSING_FROM_MANIFEST",
                        json.dumps(missing_refs, ensure_ascii=False),
                        rel(root, manifest_path),
                    )
                )
            asset_details = []
            for asset in assets:
                path = root / asset["path"]
                if not path.exists():
                    issues.append(issue("P1", "ASSET_MISSING", asset["path"], rel(root, manifest_path)))
                    continue
                with Image.open(path) as im:
                    is_visual_ref = asset_is_visual_ref(asset, refs)
                    metadata_policy = asset_metadata_policy(asset, asset_mode=qa_config["asset_mode"], is_visual_ref=is_visual_ref)
                    asset_details.append(
                        {
                            "id": asset.get("id"),
                            "width": im.width,
                            "height": im.height,
                            "kind": asset.get("kind"),
                            "role": asset.get("role"),
                            "status": asset.get("status"),
                            "is_visual_ref": is_visual_ref,
                            "metadata_policy": metadata_policy,
                        }
                    )
                    if min(im.width, im.height) < 800:
                        issues.append(issue("P2", "ASSET_SMALL", f"{asset['path']} {im.width}x{im.height}", rel(root, path)))
                    if not metadata_policy["checks"]["required_manifest_fields_present"]:
                        issues.append(
                            issue(
                                "P1",
                                "ASSET_MANIFEST_FIELDS_MISSING",
                                f"{asset.get('id')}: missing {metadata_policy['missing_fields']}",
                                rel(root, manifest_path),
                            )
                        )
                    if not metadata_policy["checks"]["text_policy_blocks_image_text"]:
                        issues.append(
                            issue(
                                "P1",
                                "ASSET_TEXT_POLICY_WEAK",
                                f"{asset.get('id')}: images must declare no visible text and not carry questions/answers/teaching body.",
                                rel(root, manifest_path),
                            )
                        )
                    if not metadata_policy["checks"]["license_status_matches_source_note"]:
                        license_policy = metadata_policy.get("license_status_policy") or {}
                        issues.append(
                            issue(
                                "P1",
                                "ASSET_LICENSE_STATUS_SOURCE_MISMATCH",
                                f"{asset.get('id')}: {'; '.join(license_policy.get('mismatches') or [])}",
                                rel(root, manifest_path),
                            )
                        )
                    if qa_config["asset_mode"] == ASSET_MODE_FINAL and is_visual_ref:
                        if not metadata_policy["checks"]["final_kind_allowed"]:
                            issues.append(
                                issue(
                                    "P1",
                                    "FINAL_ASSET_SOURCE_NOT_APPROVED",
                                    f"{asset.get('id')}: final visual assets must be ImageGen or licensed/owned originals, got {asset.get('kind')!r}.",
                                    rel(root, manifest_path),
                                )
                            )
                        if not metadata_policy["checks"]["final_status_approved"]:
                            issues.append(
                                issue(
                                    "P1",
                                    "FINAL_ASSET_STATUS_NOT_APPROVED",
                                    f"{asset.get('id')}: final visual assets need an approved/final/licensed/cleared status, got {asset.get('status')!r}.",
                                    rel(root, manifest_path),
                                )
                            )
                        if not metadata_policy["checks"]["final_not_placeholder"]:
                            issues.append(
                                issue(
                                    "P1",
                                    "FINAL_ASSET_PLACEHOLDER_OR_PROOF",
                                    f"{asset.get('id')}: final visual assets cannot be placeholders, procedural rasters, starter/sample/proof assets, or temporary mocks.",
                                    rel(root, manifest_path),
                                )
                            )
                        if not metadata_policy["checks"]["imagegen_prompt_recorded"]:
                            issues.append(
                                issue(
                                    "P1",
                                    "IMAGEGEN_PROMPT_MISSING",
                                    f"{asset.get('id')}: ImageGen assets must record prompt/generation_prompt/prompt_summary in manifest for final mode.",
                                    rel(root, manifest_path),
                                )
                            )
                        if not metadata_policy["checks"]["final_cover_content_concept_recorded"]:
                            issues.append(
                                issue(
                                    "P1",
                                    "COVER_CONTENT_CONCEPT_MISSING",
                                    f"{asset.get('id')}: final cover/hero assets must record content_brief and visual_direction so the image is designed from the lesson/book content.",
                                    rel(root, manifest_path),
                                )
                            )
                        if not metadata_policy["checks"]["final_cover_uniqueness_recorded"]:
                            issues.append(
                                issue(
                                    "P1",
                                    "COVER_UNIQUENESS_NOTE_MISSING",
                                    f"{asset.get('id')}: final cover/hero assets must record uniqueness_note; avoid generic or reused template cover art.",
                                    rel(root, manifest_path),
                                )
                            )
                        if not metadata_policy["checks"]["final_visual_asset_interpretable_scene"]:
                            scene_policy = metadata_policy.get("scene_policy") or {}
                            abstract_hits = ", ".join(scene_policy.get("abstract_hits") or [])
                            style_drift_hits = ", ".join(scene_policy.get("style_drift_hits") or [])
                            real_world_hits = ", ".join(scene_policy.get("real_world_hits") or [])
                            issues.append(
                                issue(
                                    "P1",
                                    "FINAL_ASSET_UNINTERPRETABLE_SCENE",
                                    f"{asset.get('id')}: final visual assets must be immediately understandable real-world imagery. Prefer nature, landscape, wildlife, or realistic animal scenes when content allows; otherwise use campus/classroom/study or modern human learning/life scenes. Abstract drift terms: {abstract_hits or 'none'}; non-realistic animal/style drift terms: {style_drift_hits or 'none'}; real-world anchors: {real_world_hits or 'none'}.",
                                    rel(root, manifest_path),
                                )
                            )
                        if not metadata_policy["checks"]["nature_first_family_or_rationale"]:
                            issues.append(
                                issue(
                                    "P2",
                                    "FINAL_ASSET_NATURE_FIRST_RATIONALE_MISSING",
                                    f"{asset.get('id')}: Eric prefers landscape, nature, wildlife, and realistic animal imagery first when suitable. Use that family or record family_rationale / nature_first_rationale explaining why a campus, classroom, library, study, or modern-life scene fits this content better.",
                                    rel(root, manifest_path),
                                )
                            )
            evidence["asset_refs"] = refs
            evidence["assets"] = asset_details
        except Exception as exc:
            issues.append(issue("P1", "ASSET_MANIFEST_INVALID", str(exc), rel(root, manifest_path)))

    overflow_path = qa / f"layout-overflow-{profile}.json"
    if not overflow_path.exists():
        issues.append(issue("P1", "LAYOUT_OVERFLOW_REPORT_MISSING", "Run tools/render_pdf.py.", rel(root, overflow_path)))
    else:
        rows = json.loads(overflow_path.read_text(encoding="utf-8"))
        overflows = [row for row in rows if row.get("verticalOverflow", 0) > 2 or row.get("horizontalOverflow", 0) > 2]
        evidence["layout_rows_checked"] = len(rows)
        evidence["layout_overflows"] = overflows
        if overflows:
            issues.append(issue("P1", "LAYOUT_OVERFLOW", json.dumps(overflows[:5], ensure_ascii=False), rel(root, overflow_path)))

    contact = qa / f"contact-sheet-{profile}.png"
    evidence["contact_sheet"] = rel(root, contact)
    if not contact.exists():
        issues.append(issue("P1", "CONTACT_SHEET_MISSING", "Run tools/render_pdf.py.", rel(root, contact)))

    rendered_dir = qa / "rendered-pages"
    rendered_candidates = sorted(rendered_dir.glob(f"{profile}-page-*.png")) if rendered_dir.exists() else []
    expected_rendered = evidence.get("page_count")
    filename_checks = rendered_page_filename_checks(
        [page.name for page in rendered_candidates],
        profile,
        int(expected_rendered) if expected_rendered else None,
    )
    canonical_names = set(filename_checks.get("canonical_files", []))
    rendered_pages = [page for page in rendered_candidates if page.name in canonical_names]
    evidence["rendered_pages"] = {
        "dir": rel(root, rendered_dir),
        "count": len(rendered_pages),
        "candidate_count": len(rendered_candidates),
        "expected": expected_rendered,
        "sample": [rel(root, page) for page in rendered_pages[:5]],
        "filename_checks": filename_checks,
    }
    rendered_count = rendered_page_count_checks(len(rendered_pages), int(expected_rendered) if expected_rendered else None)
    evidence["rendered_page_count"] = rendered_count
    rendered_freshness = rendered_artifact_freshness_checks(
        rendered_pages,
        html_path=html_path,
        pdf_path=pdf_path,
        contact_path=contact,
    )
    evidence["rendered_artifact_freshness"] = {
        **rendered_freshness,
        "stale_rendered_pages": [
            {
                **item,
                "path": rel(root, Path(item["path"])),
            }
            for item in rendered_freshness.get("stale_rendered_pages", [])
        ],
    }
    if not rendered_dir.exists() or not rendered_candidates:
        issues.append(issue("P1", "RENDERED_PAGES_MISSING", "Run tools/render_pdf.py.", rel(root, rendered_dir)))
    elif not filename_checks["ok"]:
        if filename_checks["conflict_files"]:
            code = "RENDERED_PAGE_CONFLICT_FILES"
            detail = f"Remove stale/conflict rendered page files: {', '.join(filename_checks['conflict_files'][:8])}"
        elif filename_checks["missing_files"]:
            code = "RENDERED_PAGE_SEQUENCE_MISSING"
            detail = f"Rendered page sequence is not continuous; missing {filename_checks['missing_count']} canonical files such as {', '.join(filename_checks['missing_files'][:8])}."
        else:
            code = "RENDERED_PAGE_FILENAME_DRIFT"
            detail = f"Rendered page filenames must be canonical {profile}-page-001.png style; unexpected files: {', '.join(filename_checks['unexpected_files'][:8])}."
        issues.append(issue("P1", code, detail, rel(root, rendered_dir)))
    elif expected_rendered and rendered_count["checks"]["rendered_pages_missing"]:
        issues.append(
            issue(
                "P1",
                "RENDERED_PAGES_INCOMPLETE",
                f"{len(rendered_pages)} rendered pages for {expected_rendered} PDF pages",
                rel(root, rendered_dir),
            )
        )
    elif expected_rendered and rendered_count["checks"]["rendered_pages_stale"]:
        issues.append(
            issue(
                "P1",
                "RENDERED_PAGES_STALE",
                f"{len(rendered_pages)} rendered pages for {expected_rendered} PDF pages; remove stale {profile}-page-*.png files and rerender.",
                rel(root, rendered_dir),
            )
        )
    elif rendered_pages and not rendered_freshness["ok"]:
        issues.append(
            issue(
                "P1",
                "RENDERED_ARTIFACTS_STALE",
                "Rendered page PNGs and contact sheet must be generated from the current HTML/PDF; rerun tools/render_pdf.py and do not copy stale _qa/rendered-pages into release evidence.",
                rel(root, rendered_dir),
            )
        )

    review_path = qa / f"visual-review-{profile}.md"
    human = parse_human_review(review_path, root=root, profile=profile)
    evidence["human_visual_review"] = {"path": rel(root, review_path), **human}
    if require_human_review and not human["ok"]:
        issues.append(issue("P1", "HUMAN_VISUAL_REVIEW_MISSING_OR_FAILED", str(human), rel(root, review_path)))
    elif not human["ok"]:
        issues.append(issue("P2", "HUMAN_VISUAL_REVIEW_PENDING", str(human), rel(root, review_path)))

    return make_report(root, profile, issues, evidence)


def make_report(root: Path, profile: str, issues: list[dict[str, Any]], evidence: dict[str, Any]) -> dict[str, Any]:
    counts = {sev: sum(1 for item in issues if item["severity"] == sev) for sev in ["P0", "P1", "P2", "P3"]}
    status = "fail" if counts["P0"] or counts["P1"] else ("warn" if counts["P2"] or counts["P3"] else "pass")
    next_action = (
        "Fix blocking issues and rerun the validator."
        if status == "fail"
        else "Proceed to human visual review before formal handoff."
        if status == "warn"
        else "Executable gates passed; report evidence and remaining risk."
    )
    return {
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "profile": profile,
        "summary": {"counts": counts, "strict_fail_severities": sorted(STRICT)},
        "issues": issues,
        "evidence": evidence,
        "next_action": next_action,
    }


def write_reports(root: Path, profile: str, report: dict[str, Any], release_gate: bool = False) -> None:
    qa = root / "_qa"
    qa.mkdir(exist_ok=True)
    suffix = "-release" if release_gate else ""
    json_path = qa / f"textbook-qa-{profile}{suffix}.json"
    md_path = qa / f"textbook-qa-{profile}{suffix}.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        f"# Textbook QA - {profile}{' Release Gate' if release_gate else ''}",
        "",
        f"- Status: **{report['status']}**",
        f"- Strict fail severities: {', '.join(report['summary']['strict_fail_severities'])}",
        f"- Counts: {report['summary']['counts']}",
        f"- Next action: {report['next_action']}",
        "",
        "## Blocking Issues",
        "",
    ]
    blockers = [item for item in report["issues"] if item["severity"] in STRICT]
    lines.extend(f"- [{item['severity']}] {item['code']}: {item['detail']}" for item in blockers)
    if not blockers:
        lines.append("- None")
    lines.extend(["", "## Warnings", ""])
    warnings = [item for item in report["issues"] if item["severity"] not in STRICT]
    lines.extend(f"- [{item['severity']}] {item['code']}: {item['detail']}" for item in warnings)
    if not warnings:
        lines.append("- None")
    lines.extend(["", "## Evidence", "", "```json", json.dumps(report["evidence"], ensure_ascii=False, indent=2), "```", ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")


def self_test() -> dict[str, Any]:
    sample = "Clean text /Users sample TODO"
    hits = forbidden_hits(sample)
    forbidden_ok = hits.get("/Users") == 1 and hits.get("TODO") == 1 and "Clean" not in hits
    underscore_hits = literal_underscore_runs({"html": "Question ___ should become a blank.", "pdf": "No run here."})
    underscore_ok = len(underscore_hits) == 1 and underscore_hits[0]["length"] == 3
    blank_css = blank_baseline_css_checks(
        """
        <style>
        .blank { height: 0; border-bottom: 0.9pt solid #8f8f8f; vertical-align: -0.82em; }
        .paragraph-practice p .blank { vertical-align: -0.22em; }
        .question-lines .blank { vertical-align: -0.88em; }
        .record-prompt .blank { vertical-align: -0.32em; }
        .activity-block p .blank,
        .activity-block li .blank,
        .word-box .blank,
        .words-to-know .blank,
        .textbook-table td .blank,
        .review-rules .blank,
        .planner-prompt .blank,
        .editing-checklist label .blank,
        .handbook-page .blank,
        .answer-table .blank { vertical-align: -0.30em; }
        .cloze-keep { white-space: nowrap; }
        .word-box { grid-template-columns: repeat(3, minmax(0, 1fr)); }
        .word-box-item { white-space: nowrap; }
        .word-box .blank { vertical-align: -0.26em; }
        .handbook-rules .blank { vertical-align: -0.24em; }
        </style>
        """
    )
    weak_blank_css = blank_baseline_css_checks(
        """
        <style>
        .blank { height: 0; border-bottom: 0.9pt solid #8f8f8f; vertical-align: -0.64em; }
        .question-lines .blank { vertical-align: -0.68em; }
        </style>
        """
    )
    blank_css_ok = blank_css["ok"] and not weak_blank_css["ok"]
    title_lockup = title_lockup_css_checks(
        """
        <style>
        .title-page h1.title-single { white-space: nowrap; }
        .title-page h1.title-single .title-for { margin-left: 7pt; font-size: 1em; font-weight: inherit; }
        </style>
        <main class="title-page"><h1 class="title-single"><span class="title-main">IELTS备考计划</span><span class="title-for">for Sample Learner</span></h1></main>
        """
    )
    weak_title_lockup = title_lockup_css_checks(
        """
        <style>
        .title-page h1.title-single { white-space: nowrap; }
        .title-page h1.title-single .title-for { margin-left: 6pt; font-size: .86em; }
        </style>
        <main class="title-page"><h1 class="title-single"><span class="title-main">IELTS备考计划</span><span class="title-for">for Sample Learner</span></h1></main>
        """
    )
    title_lockup_ok = title_lockup["ok"] and not weak_title_lockup["ok"]
    cover_brand = cover_brand_checks(
        """
        <style>
        .cover-brand { position: absolute; right: 39pt; bottom: 40pt; background: rgba(8,42,48,.62); text-shadow: 0 1pt 2pt rgba(0,0,0,.42); }
        </style>
        <section class="sheet template-cover" data-template="cover">
          <div class="cover-top"><span>Grammar Transition</span></div>
          <div class="cover-brand"><b>Eric Teaching Studio</b><span>Student Book</span></div>
        </section>
        """,
        {"level": "高二升高三"},
    )
    weak_cover_brand = cover_brand_checks(
        """
        <style>
        .cover-meta { position: absolute; right: 39pt; bottom: 40pt; }
        </style>
        <section class="sheet template-cover" data-template="cover">
          <div class="cover-top"><span>Grammar Transition</span><b>高二升高三</b></div>
          <div class="cover-meta"><b>Student Book</b></div>
        </section>
        """,
        {"level": "高二升高三"},
    )
    cover_brand_ok = cover_brand["ok"] and not weak_cover_brand["ok"]
    checklist_control = checklist_control_css_checks(
        """
        <style>
        .editing-checklist .check-mark { display: inline-block; border: 0.8pt solid #999; }
        .editing-checklist label .blank { vertical-align: -0.24em; }
        </style>
        <section class="editing-checklist"><label><span class="check-mark"></span><span class="blank"></span></label></section>
        """
    )
    weak_checklist_control = checklist_control_css_checks(
        """
        <style>
        .editing-checklist label span { display: inline-block; border: 0.8pt solid #999; }
        </style>
        <section class="editing-checklist"><label><span></span><span class="blank"></span></label></section>
        """
    )
    checklist_control_ok = checklist_control["ok"] and not weak_checklist_control["ok"]
    planner_surface = planner_surface_checks(
        """
        <section class="planner-surface">
          <div class="review-rules"><span>one focus</span></div>
          <div class="planner-rows" data-component="writing-planner">
            <article class="planner-row"><div class="planner-key"></div><div class="planner-body"></div></article>
          </div>
        </section>
        <table class="mechanics-table"></table>
        """
    )
    weak_planner_surface = planner_surface_checks(
        """
        <section class="planner-surface">
          <table class="planner-table" data-component="writing-planner"></table>
        </section>
        """
    )
    planner_surface_ok = planner_surface["ok"] and not weak_planner_surface["ok"]
    workbook_record = workbook_record_checks(
        """
        <section class="workbook-record" data-component="workbook-practice">
          <div class="record-head"><b>Diagnostic Record</b><span>one proof</span></div>
          <article><span class="record-index">01</span><div class="record-lines"></div></article>
        </section>
        """
    )
    weak_workbook_record = workbook_record_checks(
        """
        <ol class="question-lines">
          <li>What is the next step?<div class="write-line"></div></li>
        </ol>
        """
    )
    workbook_record_ok = workbook_record["ok"] and not weak_workbook_record["ok"]
    with tempfile.TemporaryDirectory(prefix="eric-designed-pdf-self-") as tmp:
        review_path = Path(tmp) / "visual-review-book-trim.md"
        review_path.write_text(
            "\n".join(
                [
                    "FINAL_VISUAL_REVIEW: PASS",
                    "Reviewer: independent-review",
                    "Score: 9.7/10",
                    "P0: 0",
                    "P1: 0",
                    "Checked: cover, unit opener, dense practice, workbook page, handbook",
                    "Visual diagnosis: Solid.",
                    "Weak pages: None.",
                    "Remaining risk: None.",
                ]
            ),
            encoding="utf-8",
        )
        missing_evidence = parse_human_review(review_path)
        review_path.write_text(
            "\n".join(
                [
                    "FINAL_VISUAL_REVIEW: PASS",
                    "Reviewer: independent-review",
                    "Score: 9.7/10",
                    "P0: 0",
                    "P1: 0",
                    "Checked: cover, unit opener, dense practice, workbook page, handbook",
                    "Contact sheet: _qa/contact-sheet-book-trim.png",
                    "Key pages: _qa/rendered-pages/book-trim-page-001.png, _qa/rendered-pages/book-trim-page-002.png, _qa/rendered-pages/book-trim-page-006.png, _qa/rendered-pages/book-trim-page-010.png",
                    "Canon comparison: compared against golden p1 cover, p3 opener, p4 elements, p6 paragraph practice, p9 handbook.",
                    "Reject patterns checked: thin-cover-type, dashboard-panel, ui-number-block, component-collage, patch-drift, form-repeat.",
                    "Font decision: B modern sans primary; C system clean fallback.",
                    "Visual diagnosis: Solid.",
                    "Weak pages: None.",
                    "Remaining risk: None.",
                ]
            ),
            encoding="utf-8",
        )
        with_evidence = parse_human_review(review_path)
        review_path.write_text(
            review_path.read_text(encoding="utf-8").replace(
                "Reviewer: independent-review",
                "Reviewer: sub-agent-review:Kuhn",
            ),
            encoding="utf-8",
        )
        subagent_evidence = parse_human_review(review_path)
    review_ok = not missing_evidence["ok"] and with_evidence["ok"] and subagent_evidence["ok"]
    with tempfile.TemporaryDirectory(prefix="eric-designed-pdf-residue-") as tmp:
        tmp_root = Path(tmp)
        (tmp_root / "tools").mkdir()
        (tmp_root / "tools" / "build.py").write_text("label = 'English Writing System'\n", encoding="utf-8")
        residue_hits = starter_residue_hits(tmp_root, {"title": "Custom IELTS Book"}, {}, "", "")
        allowed_residue_hits = starter_residue_hits(tmp_root, {"title": STARTER_SAMPLE_TITLE}, {}, "", "")
    residue_ok = "English Writing System" in residue_hits and allowed_residue_hits == {}
    final_asset = asset_metadata_policy(
        {
            "id": "learner-cover-hero-v1",
            "path": "assets/generated/learner-cover-hero-v1.png",
            "kind": "imagegen",
            "role": "cover_hero",
            "status": "approved_final",
            "text_policy": "no visible text; not used to carry teaching body, questions, or answers",
            "source_note": "Generated with ImageGen for this project.",
            "focus": "upper-left writing desk with calm negative space",
            "prompt": "Editorial writing desk image with no text.",
            "content_brief": "IELTS writing plan for Sample Learner, focused on essay planning and evidence selection.",
            "visual_direction": "Personal study desk with layered planning papers and calm teal editorial light.",
            "uniqueness_note": "Designed as a personalized IELTS planning cover, distinct from grammar or workbook covers.",
        },
        asset_mode=ASSET_MODE_FINAL,
        is_visual_ref=True,
    )
    weak_final_asset = asset_metadata_policy(
        {
            "id": "sample-learner-writing-desk",
            "path": "assets/generated/sample-learner-writing-desk.png",
            "kind": "procedural-raster",
            "role": "cover_and_unit_opener",
            "status": "original_for_cold_start_proof",
            "text_policy": "no visible text, not used to carry questions or answers",
            "source_note": "Generated locally as a proof placeholder.",
            "focus": "center",
        },
        asset_mode=ASSET_MODE_FINAL,
        is_visual_ref=True,
    )
    licensed_public_domain_asset = asset_metadata_policy(
        {
            "id": "licensed-heron",
            "path": "assets/generated/heron.png",
            "kind": "licensed-photo",
            "role": "cover_hero",
            "status": "licensed_final_public_domain",
            "text_policy": "no visible text; not used to carry teaching body, questions, or answers",
            "source_note": "Public domain photograph from Wikimedia Commons.",
            "focus": "wetland bird",
            "content_brief": "IELTS planning book with calm nature focus.",
            "visual_direction": "Public domain wetland wildlife photograph.",
            "uniqueness_note": "Specific nature asset for this book only.",
        },
        asset_mode=ASSET_MODE_FINAL,
        is_visual_ref=True,
    )
    mismatched_license_asset = asset_metadata_policy(
        {
            "id": "licensed-forest",
            "path": "assets/generated/forest.png",
            "kind": "licensed-photo",
            "role": "unit_opener",
            "status": "licensed_final_public_domain",
            "text_policy": "no visible text; not used to carry teaching body, questions, or answers",
            "source_note": "CC BY-SA 2.0 photograph from Wikimedia Commons.",
            "focus": "forest path",
        },
        asset_mode=ASSET_MODE_FINAL,
        is_visual_ref=True,
    )
    asset_policy_ok = (
        final_asset["ok"]
        and not weak_final_asset["ok"]
        and licensed_public_domain_asset["ok"]
        and not mismatched_license_asset["ok"]
    )
    asset_usage = asset_usage_policy(
        [
            {"id": "sample-cover", "path": "assets/generated/sample-cover.png", "role": "cover_hero", "allowed_templates": ["cover"]},
            {"id": "sample-opener", "path": "assets/generated/sample-opener.png", "role": "unit_opener", "allowed_templates": ["unit-opener"]},
        ],
        [
            {"id": "sample-cover", "page": "pages/01-cover.md", "template": "cover", "section": "front"},
            {"id": "sample-opener", "page": "pages/03-unit-opener.md", "template": "unit-opener", "section": "unit"},
        ],
    )
    weak_asset_usage = asset_usage_policy(
        [
            {"id": "sample-cover", "path": "assets/generated/shared.png", "role": "cover_hero"},
            {"id": "sample-opener", "path": "assets/generated/shared.png", "role": "unit_opener"},
        ],
        [
            {"id": "sample-cover", "page": "pages/01-cover.md", "template": "cover", "section": "front"},
            {"id": "sample-cover", "page": "pages/03-unit-opener.md", "template": "unit-opener", "section": "unit"},
        ],
    )
    asset_usage_ok = asset_usage["ok"] and not weak_asset_usage["ok"]
    ok = (
        forbidden_ok
        and underscore_ok
        and blank_css_ok
        and title_lockup_ok
        and cover_brand_ok
        and checklist_control_ok
        and planner_surface_ok
        and workbook_record_ok
        and review_ok
        and residue_ok
        and asset_policy_ok
        and asset_usage_ok
    )
    return {
        "status": "pass" if ok else "fail",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": ".",
        "summary": {"counts": {"P0": 0 if ok else 1, "P1": 0, "P2": 0, "P3": 0}, "strict_fail_severities": sorted(STRICT)},
        "issues": []
        if ok
        else [
            issue(
                "P0",
                "SELF_TEST_FAILED",
                json.dumps(
                    {
                        "forbidden_hits": hits,
                        "underscore_hits": underscore_hits,
                        "blank_css": blank_css,
                        "weak_blank_css": weak_blank_css,
                        "title_lockup": title_lockup,
                        "weak_title_lockup": weak_title_lockup,
                        "cover_brand": cover_brand,
                        "weak_cover_brand": weak_cover_brand,
                        "checklist_control": checklist_control,
                        "weak_checklist_control": weak_checklist_control,
                        "planner_surface": planner_surface,
                        "weak_planner_surface": weak_planner_surface,
                        "workbook_record": workbook_record,
                        "weak_workbook_record": weak_workbook_record,
                        "final_asset": final_asset,
                        "weak_final_asset": weak_final_asset,
                        "licensed_public_domain_asset": licensed_public_domain_asset,
                        "mismatched_license_asset": mismatched_license_asset,
                        "asset_usage": asset_usage,
                        "weak_asset_usage": weak_asset_usage,
                        "missing_evidence": missing_evidence,
                        "with_evidence": with_evidence,
                    },
                    ensure_ascii=False,
                ),
            )
        ],
        "evidence": {
            "forbidden_hits": hits,
            "literal_underscore_runs": underscore_hits,
            "blank_baseline_css_contract": {"strong": blank_css, "weak": weak_blank_css},
            "title_lockup_contract": {"strong": title_lockup, "weak": weak_title_lockup},
            "cover_brand_contract": {"strong": cover_brand, "weak": weak_cover_brand},
            "checklist_control_contract": {"strong": checklist_control, "weak": weak_checklist_control},
            "planner_surface_contract": {"strong": planner_surface, "weak": weak_planner_surface},
            "workbook_record_contract": {"strong": workbook_record, "weak": weak_workbook_record},
            "asset_policy_contract": {
                "final": final_asset,
                "weak_final": weak_final_asset,
                "licensed_public_domain": licensed_public_domain_asset,
                "mismatched_license": mismatched_license_asset,
            },
            "asset_usage_contract": {"strong": asset_usage, "weak": weak_asset_usage},
            "visual_review_contract": {"missing_evidence": missing_evidence, "with_evidence": with_evidence},
            "starter_residue_contract": {"hits": residue_hits, "allowed_hits": allowed_residue_hits},
        },
        "next_action": "Self-test passed." if ok else "Fix forbidden term scanner or visual review contract parser.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an Eric-designed textbook PDF project.")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--profile", default="book-trim")
    parser.add_argument("--min-pages", type=int)
    parser.add_argument("--max-pages", type=int)
    parser.add_argument("--required-template", action="append")
    parser.add_argument("--required-component", action="append")
    parser.add_argument("--asset-mode", choices=sorted(VALID_ASSET_MODES), help="Override qa.asset_mode: proof-placeholder or final-assets.")
    parser.add_argument("--require-human-review", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    report = (
        self_test()
        if args.self_test
        else validate(
            args.root,
            args.profile,
            args.require_human_review,
            min_pages=args.min_pages,
            max_pages=args.max_pages,
            required_templates=args.required_template,
            required_components=args.required_component,
            asset_mode=args.asset_mode,
        )
    )
    if not args.self_test and not args.no_write:
        write_reports(args.root.expanduser().resolve(), args.profile, report, release_gate=args.require_human_review)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Status: {report['status']}")
        print(f"Counts: {report['summary']['counts']}")
        print(f"Next action: {report['next_action']}")
    return 0 if report["status"] != "fail" else 1


if __name__ == "__main__":
    raise SystemExit(main())
