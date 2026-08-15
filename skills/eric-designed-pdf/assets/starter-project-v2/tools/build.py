#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

import markdown
import yaml


ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book.yaml"
TOKENS = ROOT / "theme" / "tokens.json"
OUT = ROOT / "outputs"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def inline_text(value: object, *, blank_mode: str = "default") -> str:
    """Escape text and convert author-typed blanks into real writing rules."""
    def blank_repl(match: re.Match[str]) -> str:
        prefix = match.groupdict().get("prefix") or ""
        length = len(match.group("blank"))
        punct = match.group("punct") or ""
        cls = "blank"
        if length <= 4:
            cls += " blank-short"
        elif length >= 7:
            cls += " blank-wide"
        if blank_mode in {"wordbox", "compact"}:
            cls += f" blank-{blank_mode}"
        blank = f'<span class="{cls}"></span>'
        unit = prefix + blank + (f"&#8288;{punct}" if punct else "")
        if punct or (prefix and blank_mode in {"wordbox", "compact"}):
            return f'<span class="cloze-keep">{unit}</span>'
        return unit

    punctuation = r"[.,;:!?，。；：！？、]?"
    if blank_mode in {"wordbox", "compact"}:
        pattern = (
            r"(?:(?P<prefix>(?:[A-Za-z0-9][A-Za-z0-9'’/-]*|[\u3400-\u9fff]+))\s+)?"
            r"(?P<blank>_{3,})(?P<punct>" + punctuation + r")"
        )
    else:
        pattern = r"(?P<blank>_{3,})(?P<punct>" + punctuation + r")"
    return re.sub(pattern, blank_repl, esc(value))


def exam_stem_text(value: object) -> str:
    """Render MCQ/cloze stem blanks as compact stem slots, not workbook write lines."""
    def blank_repl(match: re.Match[str]) -> str:
        length = len(match.group("blank"))
        punct = match.group("punct") or ""
        cls = "exam-stem-slot"
        if length <= 4:
            cls += " exam-stem-slot-short"
        elif length >= 7:
            cls += " exam-stem-slot-wide"
        slot = f'<span class="{cls}"></span>'
        if punct:
            return f'<span class="exam-stem-keep">{slot}&#8288;{punct}</span>'
        return slot

    punctuation = r"[.,;:!?，。；：！？、]?"
    pattern = r"(?P<blank>_{3,})(?P<punct>" + punctuation + r")"
    return re.sub(pattern, blank_repl, esc(value))


def prompt_text_before_write_lines(value: object) -> str:
    """Render prompts that already receive dedicated writing lines below them."""
    text = str(value)
    text = re.sub(r"\s*_{3,}\s*[.,;:!?，。；：！？、]?", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return inline_text(text)


def has_cjk(value: str) -> bool:
    return bool(re.search(r"[\u3400-\u9fff]", value))


def cover_title_markup(title: str) -> tuple[str, str]:
    """Return a cover-title mode plus markup; mixed CJK/private titles must not break mid-name."""
    if " for " in title:
        main_title, for_title = title.split(" for ", 1)
        return "title-single", (
            f'<span class="title-main">{esc(main_title)}</span>'
            f'<span class="title-for">for {esc(for_title)}</span>'
        )
    if has_cjk(title):
        return "title-single", f'<span class="title-main">{esc(title)}</span>'
    return "title-stack", esc(title)


def cover_subtitle_markup(subtitle: str) -> str:
    parts = [part.strip() for part in subtitle.split(" · ") if part.strip()]
    if len(parts) >= 2 and any(has_cjk(part) for part in parts[1:]):
        first = esc(parts[0])
        rest = " · ".join(esc(part) for part in parts[1:])
        return f'<p class="cover-subtitle"><span>{first}</span><span class="cover-subtitle-cn">{rest}</span></p>'
    return f'<p class="cover-subtitle">{esc(subtitle)}</p>'


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def configured_output_path(book: dict, profile: str, kind: str) -> Path:
    spec = book.get("profiles", {}).get(profile, {})
    nested = spec.get("outputs") or {}
    configured = spec.get(f"output_{kind}") or nested.get(kind)
    if configured:
        path = Path(configured)
        return path if path.is_absolute() else ROOT / path
    return OUT / f"textbook-template-sample-{profile}.{kind}"


def as_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [part.strip() for part in str(value).split(",") if part.strip()]


def profile_answer_visibility(book: dict, profile: str) -> str:
    spec = book.get("profiles", {}).get(profile, {}) or {}
    profile_qa = spec.get("qa") or {}
    global_qa = book.get("qa") or {}
    value = (
        profile_qa.get("answer_visibility")
        or spec.get("answer_visibility")
        or spec.get("audience")
        or global_qa.get("answer_visibility")
    )
    if value is None:
        if profile.startswith("teacher"):
            return "teacher"
        if profile.startswith("student"):
            return "student"
        return ""
    return str(value).strip().lower()


def page_in_profile(meta: dict, profile: str, book: dict) -> bool:
    include_profiles = as_list(meta.get("include_profiles"))
    if include_profiles and profile not in include_profiles:
        return False
    exclude_profiles = as_list(meta.get("exclude_profiles"))
    if profile in exclude_profiles:
        return False

    visibility = profile_answer_visibility(book, profile)
    template = str(meta.get("template", "")).strip().lower()
    audience = str(meta.get("audience", "")).strip().lower()

    if audience in {"teacher", "teacher-only"} or template in {"teacher-answer-key", "teacher-guide-page"}:
        return visibility in {"", "teacher"}
    if template == "answer-key":
        return visibility in {"", "student-with-answer-key", "teacher"}
    if audience in {"student", "student-only"}:
        return visibility in {"", "student", "student-with-answer-key"}
    return True


def parse_page(path: Path) -> tuple[dict, str]:
    raw = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n?(.*)$", raw, flags=re.S)
    if not match:
        return {}, raw
    return yaml.safe_load(match.group(1)) or {}, match.group(2)


def md(value: str) -> str:
    return markdown.markdown(value or "", extensions=["tables"])


def asset_path(asset_id: str, assets: dict) -> str:
    item = assets.get(asset_id)
    if not item:
        return ""
    return "../" + item["path"]


def bullet_list(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{inline_text(item)}</li>" for item in items) + "</ul>"


def teacher_default_note(meta: dict) -> str:
    title = meta.get("teacher_note_title") or "Teacher Note"
    note = meta.get("teacher_note") or ""
    if not note:
        return ""
    return f"""
    <aside class="teacher-margin-note" data-component="teacher-page-note" data-teacher-only="true">
      <b>{esc(title)}</b>
      <span>{inline_text(note)}</span>
    </aside>
    """


def teacher_answer_strip(meta: dict) -> str:
    answers = meta.get("teacher_answers") or []
    if not answers:
        return ""
    items = "".join(f"<span>{inline_text(str(item))}</span>" for item in answers[:6])
    return f"""
    <aside class="teacher-answer-strip" data-component="teacher-answer-strip" data-teacher-only="true">
      <b>Answer Focus</b>
      <div>{items}</div>
    </aside>
    """


def teacher_page_layer(meta: dict, profile: str, book: dict) -> str:
    visibility = profile_answer_visibility(book, profile)
    if visibility not in {"", "teacher"}:
        return ""
    template = str(meta.get("template", "")).strip().lower()
    if template in {"cover", "title", "teacher-answer-key", "teacher-guide-page"}:
        return ""
    return teacher_default_note(meta) + teacher_answer_strip(meta)


def lines(count: int = 1, label: str = "") -> str:
    label_html = f"<span>{esc(label)}</span>" if label else ""
    return "".join(f"<div class=\"write-line\">{label_html}</div>" for _ in range(count))


def table_html(headers: list[str], rows: list[list[str]], component: str = "mechanics-table") -> str:
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{inline_text(cell)}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    return f"<table class=\"textbook-table\" data-component=\"{esc(component)}\"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def sentence_map_cards(headers: list[str], rows: list[list[str]]) -> str:
    labels = list(headers[:3])
    while len(labels) < 3:
        labels.append(["Sentence", "Analysis", "Check"][len(labels)])
    cards = ""
    for idx, row in enumerate(rows, 1):
        cells = list(row[:3])
        while len(cells) < 3:
            cells.append("")
        cards += f"""
        <article>
          <b>{idx:02d}</b>
          <div class="sentence-map-card-field sentence-map-card-sentence">
            <span>{esc(labels[0])}</span>
            <p>{inline_text(cells[0], blank_mode='compact')}</p>
          </div>
          <div class="sentence-map-card-field sentence-map-card-analysis">
            <span>{esc(labels[1])}</span>
            <p>{inline_text(cells[1], blank_mode='compact')}</p>
          </div>
          <div class="sentence-map-card-field sentence-map-card-check">
            <span>{esc(labels[2])}</span>
            <p>{inline_text(cells[2], blank_mode='compact')}</p>
          </div>
        </article>
        """
    return f"""
    <section class="sentence-map-card-stack" data-component="categorizing-chart" data-surface-family="sentence-map" data-surface="a4-card-stack">
      {cards}
    </section>
    """


def section_ribbon(meta: dict, default: str = "Grammar") -> str:
    return f"""
    <div class="section-ribbon" data-component="section-ribbon">
      <b>{esc(meta.get('kicker', default))}</b>
      <span>{esc(meta.get('ribbon_note', meta.get('focus', '')))}</span>
    </div>
    """


def skill_side_labels(labels: list[str]) -> str:
    if not labels:
        return ""
    items = "".join(f"<span>{esc(label)}</span>" for label in labels)
    return f"<aside class=\"skill-side-label\" data-component=\"skill-side-label\">{items}</aside>"


def lettered_paragraphs(items: list[dict]) -> str:
    rows = ""
    for idx, item in enumerate(items, 1):
        label = item.get("label") or chr(64 + idx)
        rows += f"""
        <article class="lettered-paragraph" data-component="lettered-paragraph">
          <b>{esc(label)}</b>
          <p>{inline_text(item.get('text', ''))}</p>
        </article>
        """
    return rows


def definition_notes(items: list[str]) -> str:
    if not items:
        return ""
    rows = "".join(f"<span>{inline_text(item, blank_mode='compact')}</span>" for item in items)
    return f"<div class=\"definition-footnote\" data-component=\"definition-footnote\">{rows}</div>"


def guided_mcq(items: list[dict]) -> str:
    rows = ""
    for idx, item in enumerate(items, 1):
        options = "".join(f"<span>{esc(opt)}</span>" for opt in item.get("options", []))
        prompt = item.get("prompt", item.get("question", ""))
        rows += f"""
        <article>
          <b>{idx:02d}</b>
          <p>{exam_stem_text(prompt)}</p>
          <div>{options}</div>
        </article>
        """
    return f"<section class=\"guided-mcq-set\" data-component=\"guided-mcq-set\">{rows}</section>"


def workbook_rows(rows: list[dict], label: str = "Practice Record", note: str = "one answer · one reason · one next step") -> str:
    items = ""
    for idx, raw_item in enumerate(rows, 1):
        item = raw_item if isinstance(raw_item, dict) else {"prompt": raw_item}
        items += f"""
        <article>
          <span class="record-index">{esc(item.get('label', f'{idx:02d}'))}</span>
          <div>
            <p class="record-prompt">{prompt_text_before_write_lines(item.get('prompt', ''))}</p>
            <div class="record-lines">{lines(int(item.get('lines', 2)))}</div>
          </div>
        </article>
        """
    return f"""
    <section class="workbook-record" data-component="workbook-practice">
      <div class="record-head">
        <b>{esc(label)}</b>
        <span>{inline_text(note)}</span>
      </div>
      {items}
    </section>
    """


def diagram_callout(meta: dict) -> str:
    nodes = "".join(f"<span>{inline_text(node, blank_mode='compact')}</span>" for node in meta.get("nodes", []))
    return f"""
    <section class="diagram-callout" data-component="diagram-callout">
      <h2>{esc(meta.get('title', 'Sentence Map'))}</h2>
      <div>{nodes}</div>
      <p>{inline_text(meta.get('note', ''))}</p>
    </section>
    """


def critical_strip(items: list[str], label: str = "Check") -> str:
    rows = "".join(f"<span>{inline_text(item, blank_mode='compact')}</span>" for item in items)
    return f"""
    <section class="critical-thinking-strip" data-component="critical-thinking-strip">
      <b>{esc(label)}</b>
      <div>{rows}</div>
    </section>
    """


def contents_scope_map(items: list[dict]) -> str:
    if not items:
        return ""
    rows = "".join(
        f"""
        <article>
          <b>{esc(item.get('family', 'Family'))}</b>
          <span>{esc(item.get('pages', ''))}</span>
          <p>{inline_text(item.get('forms', ''))}</p>
          <small>{inline_text(item.get('proof', ''))}</small>
        </article>
        """
        for item in items
    )
    return f"<section class=\"contents-scope-map\">{rows}</section>"


def contents_page_index(items: list[dict]) -> str:
    if not items:
        return ""
    rows = "".join(
        f"""
        <article>
          <b>{esc(item.get('label', 'p'))}</b>
          <div>
            <strong>{esc(item.get('title', 'Page'))}</strong>
            <span>{inline_text(item.get('role', ''))}</span>
          </div>
        </article>
        """
        for item in items
    )
    return f"<section class=\"contents-page-index\">{rows}</section>"


def diagnostic_ladder(items: list[str]) -> str:
    if not items:
        return ""
    rows = "".join(f"<span><b>{idx:02d}</b>{inline_text(item)}</span>" for idx, item in enumerate(items, 1))
    return f"<section class=\"diagnostic-ladder\">{rows}</section>"


def diagnostic_notes(items: list[dict]) -> str:
    if not items:
        return ""
    rows = "".join(
        f"""
        <article>
          <b>{esc(item.get('label', ''))}</b>
          <h2>{esc(item.get('title', 'Note'))}</h2>
          <p>{inline_text(item.get('text', ''))}</p>
        </article>
        """
        for item in items
    )
    return f"<section class=\"diagnostic-mini-note\">{rows}</section>"


def evidence_flow(items: list[dict]) -> str:
    if not items:
        return ""
    return f"<section class=\"evidence-flow\">{lettered_paragraphs(items)}</section>"


def evidence_cues(items: list[dict]) -> str:
    if not items:
        return ""
    rows = "".join(
        f"""
        <article>
          <b>{esc(item.get('label', 'Cue'))}</b>
          <span>{inline_text(item.get('text', ''), blank_mode='compact')}</span>
        </article>
        """
        for item in items
    )
    return f"<section class=\"evidence-cues\">{rows}</section>"


def evidence_task_strip(items: list[dict]) -> str:
    if not items:
        return ""
    rows = "".join(
        f"""
        <article>
          <b>{esc(item.get('label', f'{idx:02d}'))}</b>
          <h2>{esc(item.get('title', 'Check'))}</h2>
          <p>{inline_text(item.get('prompt', ''))}</p>
          {lines(int(item.get('lines', 1)))}
        </article>
        """
        for idx, item in enumerate(items, 1)
    )
    return f"<section class=\"evidence-task-strip\" data-component=\"critical-thinking-strip\">{rows}</section>"


def exam_pressure_grid(items: list[dict]) -> str:
    if not items:
        return ""
    rows = "".join(
        f"""
        <article>
          <b>{esc(item.get('label', ''))}</b>
          <h2>{esc(item.get('title', 'Check'))}</h2>
          <p>{inline_text(item.get('task', ''))}</p>
          <small>{inline_text(item.get('check', ''))}</small>
        </article>
        """
        for item in items
    )
    return f"<section class=\"exam-pressure-grid\">{rows}</section>"


def exam_timing_strip(note: str) -> str:
    if not note:
        return ""
    return f"<section class=\"exam-timing-strip\"><b>Timing</b><span>{inline_text(note)}</span></section>"


def rewrite_lens(items: list[dict]) -> str:
    if not items:
        return ""
    rows = "".join(
        f"""
        <article>
          <b>{esc(item.get('label', 'Lens'))}</b>
          <span>{inline_text(item.get('text', ''), blank_mode='compact')}</span>
        </article>
        """
        for item in items
    )
    return f"<section class=\"rewrite-lens\">{rows}</section>"


def rewrite_micro_rules(items: list[str]) -> str:
    if not items:
        return ""
    rows = "".join(f"<span>{inline_text(item, blank_mode='compact')}</span>" for item in items)
    return f"<section class=\"rewrite-micro-rules\"><b>Rewrite Rules</b><div>{rows}</div></section>"


def final_check_summary(items: list[dict]) -> str:
    if not items:
        return ""
    rows = "".join(
        f"""
        <article>
          <b>{esc(item.get('label', 'Check'))}</b>
          <span>{inline_text(item.get('text', ''), blank_mode='compact')}</span>
        </article>
        """
        for item in items
    )
    return f"<section class=\"final-check-summary\">{rows}</section>"


def slugify(value: object, default: str = "") -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", str(value or "").strip().lower()).strip("-")
    return slug or default


def surface_attrs(family: str, surface: str) -> str:
    return f' data-surface-family="{esc(family)}" data-surface="{esc(slugify(surface))}"'


def task2_checks(meta: dict) -> str:
    return "".join(
        f"<label><span class=\"check-mark\"></span>{inline_text(item, blank_mode='compact')}</label>"
        for item in meta.get("editing", [])
    )


def task2_timing_strip(meta: dict) -> str:
    timing = "".join(f"<span>{inline_text(item, blank_mode='compact')}</span>" for item in meta.get("timing_strip", []))
    return f"<div>{timing}</div>" if timing else ""


def task2_page_header(meta: dict, h1: str) -> str:
    return f"""
      <div class="top-rule"></div>
      <h1>{esc(h1)}</h1>
      <section class="answer-sheet-head" data-component="activity-block">
        <h3><span>Activity {esc(meta['activity_no'])}</span> | {esc(meta['title'])}</h3>
        <p>{inline_text(meta.get('answer_focus', ''))}</p>
        {task2_timing_strip(meta)}
      </section>
    """


def page_shell(num: int, meta: dict, book: dict, body: str, profile: str) -> str:
    template = meta.get("template", "page")
    section = meta.get("section", "unit")
    variant = str(meta.get("variant") or "").strip()
    variant_slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", variant).strip("-").lower()
    variant_class = f" variant-{esc(variant_slug)}" if variant_slug else ""
    variant_attr = f' data-variant="{esc(variant_slug)}"' if variant_slug else ""
    opener_attrs = ""
    style_attr = ""
    if template == "unit-opener":
        layout = str(meta.get("opener_layout") or "bottom-band").strip()
        accent = str(meta.get("opener_accent") or "#9a5625").strip()
        band = str(meta.get("opener_band") or "#9a5625").strip()
        soft = str(meta.get("opener_soft") or "#efe2c6").strip()
        opener_attrs = f' data-opener-layout="{esc(layout)}" data-opener-accent="{esc(accent)}"'
        style_attr = f' style="--opener-accent:{esc(accent)};--opener-band:{esc(band)};--opener-soft:{esc(soft)};"'
    footer = ""
    if template not in {"cover", "title", "unit-opener"}:
        unit = book.get("unit", {})
        unit_number = meta.get("unit_number", unit.get("number", 1))
        unit_title = meta.get("unit_title", unit.get("title", "Unit"))
        footer_label = f"UNIT {esc(unit_number)} • {esc(unit_title)}"
        if section == "frontmatter":
            footer_book_title = book.get("footer_title") or (book.get("identity") or {}).get("footer_title") or book.get("title", "Student Book")
            footer_label = f"{esc(meta.get('folio_label', 'BOOK MAP'))} • {esc(footer_book_title)}"
        footer = f"""
        <footer class="folio">
          <b>{num}</b>
          <span>{footer_label}</span>
        </footer>
        """
    if section == "backmatter":
        footer = f"""
        <footer class="folio backmatter-folio">
          <b>{num}</b>
          <span>{esc(meta.get('heading', 'Back Matter'))}</span>
        </footer>
        """
    teacher_layer = teacher_page_layer(meta, profile, book)
    return f"""
    <section class="sheet template-{esc(template)} section-{esc(section)} profile-{esc(profile)}{variant_class}"
      data-page="{num}" data-section="{esc(section)}" data-template="{esc(template)}"{variant_attr}{opener_attrs}{style_attr}>
      {body}
      {teacher_layer}
      {footer}
    </section>
    """


def render_cover(meta: dict, book: dict, assets: dict) -> str:
    src = asset_path(meta.get("asset", ""), assets)
    identity = book.get("identity") or {}
    cover_title = str(identity.get("cover_title") or book.get("cover_title") or book["title"])
    title_mode, title_markup = cover_title_markup(cover_title)
    subtitle_markup = cover_subtitle_markup(str(book.get("subtitle", "")))
    series_label = book.get("series") or "English Course"
    return f"""
    <div class="cover-photo" data-component="cover"><img src="{esc(src)}" alt=""></div>
    <div class="cover-top">
      <span class="series-box"></span>
      <span>{esc(series_label)}</span>
    </div>
    <div class="cover-title {title_mode}">
      <h1>{title_markup}</h1>
      {subtitle_markup}
    </div>
    <div class="cover-brand" data-component="cover-brand">
      <b>Eric Teaching Studio</b>
      <span>{esc(book.get('edition', 'Sample'))}</span>
    </div>
    """


def render_title(meta: dict, book: dict, assets: dict) -> str:
    identity = book.get("identity") or {}
    cover_title = str(identity.get("cover_title") or book.get("cover_title") or book["title"])
    title_mode, title_markup = cover_title_markup(cover_title)
    nav_items = identity.get("navigation") or [
        {"code": "01", "title": "Look", "text": "Notice the target skill before the lesson begins."},
        {"code": "02", "title": "Practice", "text": "Use examples, tables, and short writing space."},
        {"code": "03", "title": "Review", "text": "Check the page evidence before moving on."},
        {"code": "04", "title": "Record", "text": "Keep only the evidence that tells you what to practise next."},
    ]
    nav = "".join(
        f"""
        <article>
          <b>{esc(item.get('code', f'{idx:02d}'))}</b>
          <span>{esc(item.get('title', 'Step'))}</span>
          <p>{inline_text(item.get('text', ''))}</p>
        </article>
        """
        for idx, item in enumerate(nav_items, 1)
    )
    chinese_title = identity.get("chinese_title")
    chinese_line = f"<p class=\"title-cn\">{esc(chinese_title)}</p>" if chinese_title else ""
    return f"""
    <main class="title-page" data-component="title-page">
      <div class="brand-mark"></div>
      <h1 class="{title_mode}">{title_markup}</h1>
      {chinese_line}
      <p>{esc(book['subtitle'])}</p>
      <div class="title-rule"></div>
      <nav class="title-route" data-component="title-navigation">
        {nav}
      </nav>
      <section>
        <b>{esc(book.get('level', 'Level'))}</b>
        <span>{esc(book.get('edition', 'Template System Sample'))}</span>
      </section>
      <small>{esc(book.get('imprint_note', 'Evidence-first course edition'))}</small>
    </main>
    """


def render_unit_opener(meta: dict, book: dict, assets: dict) -> str:
    unit = book["unit"]
    src = asset_path(meta.get("asset", ""), assets)
    objectives = bullet_list(meta.get("objectives", []))
    unit_number = meta.get("unit_number", unit.get("number", 1))
    unit_title = meta.get("unit_title", unit.get("title", "Unit"))
    layout = str(meta.get("opener_layout") or "bottom-band").strip()
    objective_label = meta.get("objective_label", "Objectives")
    before_label = meta.get("before_label", "Before You Begin")
    freewrite = str(meta.get("freewrite", "")).strip()
    opener_prompt = (
        f'<p class="opener-prompt"><b>{esc(before_label)}</b><span>{esc(freewrite)}</span></p>'
        if freewrite
        else ""
    )
    return f"""
    <div class="unit-photo" data-component="unit-opener"><img src="{esc(src)}" alt=""></div>
    <header class="unit-lockup layout-{esc(layout)}">
      <b>{esc(unit_number)}</b>
      <span></span>
      <h1>{esc(unit_title)}</h1>
    </header>
    <section class="objectives-band layout-{esc(layout)}" data-component="objectives-band">
      <div class="objectives-intro">
        <h2>{esc(objective_label)}</h2>
        {opener_prompt}
      </div>
      <div class="objectives-list">
        {objectives}
      </div>
    </section>
    """


def render_elements(meta: dict, book: dict, assets: dict) -> str:
    table = table_html(meta["table"]["headers"], meta["table"]["rows"])
    activity_items = "".join(
        f"<li><b>{idx}.</b> {inline_text(item)}</li>"
        for idx, item in enumerate(meta.get("items", []), 1)
    )
    return f"""
    <main class="body-page elements-page" data-component="elements-page">
      <div class="top-rule"></div>
      <h1>{esc(meta['heading'])}</h1>
      <h2>{esc(meta['subheading'])}</h2>
      <p class="lead"><b>{esc(meta['rule_lead'].split(' is ')[0])}</b> is {esc(' is '.join(meta['rule_lead'].split(' is ')[1:]))}</p>
      {bullet_list(meta.get("bullets", []))}
      {table}
      <section class="activity-block" data-component="activity-block">
        <h3><span>Activity 1</span> | {esc(meta['activity_title'])}</h3>
        <p><b>{inline_text(meta['activity_instructions'])}</b></p>
        <ol>{activity_items}</ol>
      </section>
    </main>
    """


def render_words_to_know(items: list[list[str]], label: str = "Words To Know") -> str:
    rows = "".join(
        f"<div><b>{esc(word)}</b> {inline_text(defn)}</div>"
        for word, defn in items
    )
    return f"<section class=\"words-to-know\" data-component=\"words-to-know\"><h4>{esc(label)}</h4>{rows}</section>"


def render_activity(meta: dict, book: dict, assets: dict) -> str:
    word_box = "".join(
        f"<span class=\"word-box-item\">{inline_text(word, blank_mode='wordbox')}</span>"
        for word in meta.get("word_box", [])
    )
    numbered_paragraph = inline_text(meta["paragraph"])
    practice_rows = meta.get("practice_rows") or [
        {"label": f"{idx}.", "prompt": q}
        for idx, q in enumerate(meta.get("questions", []), 1)
    ]
    practice_items = "".join(
        f"""
        <article>
          <span class="record-index">{esc(item.get('label', str(idx)))}</span>
          <div>
            <p class="record-prompt">{inline_text(item['prompt'])}</p>
            <div class="record-lines">{lines(int(item.get('lines', 2)))}</div>
          </div>
        </article>
        """
        for idx, item in enumerate(practice_rows, 1)
    )
    practice_block = ""
    if practice_items:
        practice_block = f"""
        <section class="workbook-record" data-component="workbook-practice">
          <div class="record-head">
            <b>{esc(meta.get('practice_label', 'Practice Record'))}</b>
            <span>{inline_text(meta.get('practice_note', 'write one clear answer for each line'))}</span>
          </div>
          {practice_items}
        </section>
        """
    return f"""
    <main class="body-page activity-page">
      <section class="activity-block large" data-component="activity-block">
        <h3><span>Activity {esc(meta['activity_no'])}</span> | {esc(meta['title'])}</h3>
        <p><b>{inline_text(meta['instructions'])}</b></p>
        <div class="word-box" data-component="word-box">{word_box}</div>
      </section>
      {render_words_to_know(meta.get("words_to_know", []))}
      <section class="paragraph-practice" data-component="paragraph-practice">
        <div class="paragraph-label">{esc(meta['paragraph_label'])}</div>
        <h2>{esc(meta['paragraph_title'])}</h2>
        <p>{numbered_paragraph}</p>
      </section>
      {practice_block}
    </main>
    """


def render_paragraph_practice(meta: dict, book: dict, assets: dict) -> str:
    questions = "".join(
        f"<li>{prompt_text_before_write_lines(q)}{lines(1)}</li>" for q in meta.get("questions", [])
    )
    return f"""
    <main class="body-page paragraph-page">
      <section class="activity-block" data-component="activity-block">
        <h3><span>Activity {esc(meta['activity_no'])}</span> | {esc(meta['title'])}</h3>
        <p><b>{inline_text(meta['instructions'])}</b></p>
      </section>
      {render_words_to_know(meta.get("words_to_know", []))}
      <section class="paragraph-practice model" data-component="paragraph-practice">
        <div class="paragraph-label">{esc(meta['paragraph_label'])}</div>
        <h2>{esc(meta['paragraph_title'])}</h2>
        <p>{inline_text(meta['paragraph'])}</p>
      </section>
      <ol class="question-lines">{questions}</ol>
    </main>
    """


def render_photo_passage(meta: dict, book: dict, assets: dict) -> str:
    src = asset_path(meta.get("asset", ""), assets)
    return f"""
    <main class="body-page photo-passage-page">
      <figure class="photo-passage" data-component="photo-passage">
        <img src="{esc(src)}" alt="">
        <figcaption>{esc(meta['caption'])}</figcaption>
      </figure>
      <section class="activity-block" data-component="activity-block">
        <h3><span>Activity {esc(meta['activity_no'])}</span> | {esc(meta['title'])}</h3>
        <p><b>{inline_text(meta['instructions'])}</b></p>
      </section>
      {workbook_rows(meta.get("questions", []), meta.get("record_label", "Observation Record"), meta.get("record_note", "detail · phrase · task"))}
    </main>
    """


def render_route_map_planner(meta: dict) -> str:
    weeks = "".join(
        f"""
        <article>
          <b>{esc(item.get('week', 'Week'))}</b>
          <h2>{esc(item.get('focus', 'Focus'))}</h2>
          <p>{inline_text(item.get('proof', ''))}</p>
          <small>{inline_text(item.get('checkpoint', ''))}</small>
        </article>
        """
        for item in meta.get("route_weeks", [])
    )
    milestones = "".join(f"<li>{inline_text(item)}</li>" for item in meta.get("milestones", []))
    return f"""
    <main class="body-page writing-page route-map-page">
      <div class="top-rule"></div>
      <h1>30-Day Map</h1>
      <section class="activity-block route-activity" data-component="activity-block">
        <h3><span>Planner {esc(meta['activity_no'])}</span> | {esc(meta['title'])}</h3>
        <div class="review-rules">{"".join(f"<span>{inline_text(item)}</span>" for item in meta.get("instructions", []))}</div>
      </section>
      <section class="route-map-surface" data-component="writing-planner"{surface_attrs('writing-planner', 'book-roadmap-planner')}>
        {weeks}
      </section>
      <section class="milestone-strip">
        <b>Milestones</b>
        <ol>{milestones}</ol>
      </section>
      {workbook_rows(meta.get('record_rows', []), meta.get('record_label', 'Monthly Proof Record'), meta.get('record_note', 'week · proof · checkpoint'))}
    </main>
    """


def render_daily_schedule(meta: dict) -> str:
    days = "".join(
        f"""
        <article>
          <b>{esc(item.get('day', 'Day'))}</b>
          <h2>{esc(item.get('task', 'Practice'))}</h2>
          <p>{inline_text(item.get('proof', ''))}</p>
          <small>{esc(item.get('time', ''))}</small>
        </article>
        """
        for item in meta.get("rhythm_days", [])
    )
    checks = "".join(
        f"<label><span class=\"check-mark\"></span>{inline_text(item, blank_mode='compact')}</label>"
        for item in meta.get("editing", [])
    )
    return f"""
    <main class="body-page writing-page daily-schedule-page">
      <div class="top-rule"></div>
      <h1>Daily Rhythm</h1>
      <section class="activity-block schedule-activity" data-component="activity-block">
        <h3><span>Planner {esc(meta['activity_no'])}</span> | {esc(meta['title'])}</h3>
        <div class="review-rules">{"".join(f"<span>{inline_text(item)}</span>" for item in meta.get("instructions", []))}</div>
      </section>
      <section class="daily-rhythm-grid" data-component="writing-planner"{surface_attrs('writing-planner', 'daily-practice-schedule')}>
        {days}
      </section>
      {workbook_rows(meta.get('habit_rows', []), 'Today Record', 'page · evidence · next practice')}
      <section class="editing-checklist" data-component="editing-checklist">
        <h2>{esc(meta.get('check_label', 'Daily Check'))}</h2>
        <p>{inline_text(meta.get('check_note', 'Check the rhythm before stopping.'))}</p>
        <div>{checks}</div>
      </section>
    </main>
    """


def render_task2_ladder(meta: dict, surface: str) -> str:
    ladder_items = meta.get("position_ladder") or [
        {"label": item.get("label", "Step"), "prompt": item.get("hint", ""), "lines": item.get("lines", 1)}
        for item in meta.get("answer_sections", [])[:4]
    ]
    lanes = meta.get("paragraph_lanes") or [
        {"label": "Body 1", "hint": "reason + example", "lines": 2},
        {"label": "Body 2", "hint": "reason + contrast", "lines": 2},
    ]
    ladder = "".join(
        f"""
        <article>
          <b>{esc(item.get('label', f'{idx:02d}'))}</b>
          <p>{inline_text(item.get('prompt', item.get('hint', '')))}</p>
          {lines(int(item.get('lines', 1)))}
        </article>
        """
        for idx, item in enumerate(ladder_items, 1)
    )
    lane_html = "".join(
        f"""
        <article>
          <b>{esc(item.get('label', 'Body'))}</b>
          <small>{inline_text(item.get('hint', ''))}</small>
          {lines(int(item.get('lines', 2)))}
        </article>
        """
        for item in lanes
    )
    return f"""
    <main class="body-page writing-page task2-answer-sheet-page task2-ladder-page"{surface_attrs('task2-writing', surface)}>
      {task2_page_header(meta, 'Position Ladder')}
      <section class="task2-ladder-surface task2-printed-surface" data-component="writing-planner"{surface_attrs('task2-writing', surface)}>
        <div class="task2-position-ladder">{ladder}</div>
        <div class="task2-body-lanes">{lane_html}</div>
      </section>
      <section class="editing-checklist" data-component="editing-checklist">
        <h2>{esc(meta.get('check_label', 'Task 2 Check'))}</h2>
        <p>{inline_text(meta.get('check_note', 'Check the paragraph jobs before scoring.'))}</p>
        <div>{task2_checks(meta)}</div>
      </section>
    </main>
    """


def render_task2_two_view(meta: dict, surface: str) -> str:
    views = meta.get("view_columns") or [
        {"label": "View A", "prompt": "Why some people agree", "lines": 2},
        {"label": "View B", "prompt": "Why others disagree", "lines": 2},
    ]
    bridges = meta.get("bridge_rows") or [
        {"label": "My opinion", "prompt": "Which side is stronger?", "lines": 1},
        {"label": "Bridge", "prompt": "How will I connect both views?", "lines": 1},
    ]
    view_html = "".join(
        f"""
        <article>
          <b>{esc(item.get('label', 'View'))}</b>
          <p>{inline_text(item.get('prompt', ''))}</p>
          {lines(int(item.get('lines', 2)))}
        </article>
        """
        for item in views
    )
    bridge_html = "".join(
        f"""
        <article>
          <b>{esc(item.get('label', 'Bridge'))}</b>
          <p>{inline_text(item.get('prompt', ''))}</p>
          {lines(int(item.get('lines', 1)))}
        </article>
        """
        for item in bridges
    )
    return f"""
    <main class="body-page writing-page task2-answer-sheet-page task2-two-view-page"{surface_attrs('task2-writing', surface)}>
      {task2_page_header(meta, 'Two Views')}
      <section class="task2-two-view-surface task2-printed-surface" data-component="writing-planner"{surface_attrs('task2-writing', surface)}>
        <div class="task2-view-columns">{view_html}</div>
        <div class="task2-bridge-strip">{bridge_html}</div>
      </section>
      <section class="editing-checklist" data-component="editing-checklist">
        <h2>{esc(meta.get('check_label', 'Task 2 Check'))}</h2>
        <p>{inline_text(meta.get('check_note', 'Check the paragraph jobs before scoring.'))}</p>
        <div>{task2_checks(meta)}</div>
      </section>
    </main>
    """


def render_task2_problem_solution(meta: dict, surface: str) -> str:
    rows = meta.get("problem_solution_rows") or [
        {"label": "Problem", "prompt": "What is happening?", "lines": 1},
        {"label": "Cause", "prompt": "Why does it happen?", "lines": 1},
        {"label": "Solution", "prompt": "What should change?", "lines": 1},
        {"label": "Result", "prompt": "What improves?", "lines": 1},
    ]
    row_html = "".join(
        f"""
        <article>
          <b>{esc(item.get('label', f'{idx:02d}'))}</b>
          <p>{prompt_text_before_write_lines(item.get('prompt', ''))}</p>
          {lines(int(item.get('lines', 1)))}
        </article>
        """
        for idx, item in enumerate(rows, 1)
    )
    paragraph_blocks = "".join(
        f"""
        <article>
          <b>{esc(item.get('label', 'Body'))}</b>
          <small>{inline_text(item.get('hint', ''))}</small>
          {lines(int(item.get('lines', 2)))}
        </article>
        """
        for item in meta.get("paragraph_lanes", [])
    )
    return f"""
    <main class="body-page writing-page task2-answer-sheet-page task2-problem-page"{surface_attrs('task2-writing', surface)}>
      {task2_page_header(meta, 'Problem / Solution')}
      <section class="task2-problem-surface task2-printed-surface" data-component="writing-planner"{surface_attrs('task2-writing', surface)}>
        <div class="task2-problem-matrix">{row_html}</div>
        <div class="task2-solution-lines">{paragraph_blocks}</div>
      </section>
      <section class="editing-checklist" data-component="editing-checklist">
        <h2>{esc(meta.get('check_label', 'Task 2 Check'))}</h2>
        <p>{inline_text(meta.get('check_note', 'Check the paragraph jobs before scoring.'))}</p>
        <div>{task2_checks(meta)}</div>
      </section>
    </main>
    """


def render_task2_balance(meta: dict, surface: str) -> str:
    columns = meta.get("balance_columns") or [
        {"label": "Advantage", "prompt": "Strong point", "lines": 2},
        {"label": "Disadvantage", "prompt": "Risk or limit", "lines": 2},
    ]
    decisions = meta.get("decision_rows") or [
        {"label": "Balance", "prompt": "Which side is stronger?", "lines": 1},
        {"label": "Final sentence", "prompt": "What will the conclusion say?", "lines": 1},
    ]
    column_html = "".join(
        f"""
        <article>
          <b>{esc(item.get('label', 'Side'))}</b>
          <p>{inline_text(item.get('prompt', ''))}</p>
          {lines(int(item.get('lines', 2)))}
        </article>
        """
        for item in columns
    )
    decision_html = "".join(
        f"""
        <article>
          <b>{esc(item.get('label', 'Decision'))}</b>
          <p>{inline_text(item.get('prompt', ''))}</p>
          {lines(int(item.get('lines', 1)))}
        </article>
        """
        for item in decisions
    )
    return f"""
    <main class="body-page writing-page task2-answer-sheet-page task2-balance-page"{surface_attrs('task2-writing', surface)}>
      {task2_page_header(meta, 'Balance Sheet')}
      <section class="task2-balance-surface task2-printed-surface" data-component="writing-planner"{surface_attrs('task2-writing', surface)}>
        <div class="task2-balance-columns">{column_html}</div>
        <div class="task2-decision-strip">{decision_html}</div>
      </section>
      <section class="editing-checklist" data-component="editing-checklist">
        <h2>{esc(meta.get('check_label', 'Task 2 Check'))}</h2>
        <p>{inline_text(meta.get('check_note', 'Check the paragraph jobs before scoring.'))}</p>
        <div>{task2_checks(meta)}</div>
      </section>
    </main>
    """


def render_task2_booklet(meta: dict, surface: str) -> str:
    sections = "".join(
        f"""
        <article>
          <div class="answer-sheet-key">
            <b>{esc(item.get('label', 'Part'))}</b>
            <small>{inline_text(item.get('hint', ''))}</small>
          </div>
          <div class="answer-sheet-lines">{lines(int(item.get('lines', 1)))}</div>
        </article>
        """
        for item in meta.get("answer_sections", [])
    )
    return f"""
    <main class="body-page writing-page task2-answer-sheet-page task2-booklet-page"{surface_attrs('task2-writing', surface)}>
      {task2_page_header(meta, 'Answer Booklet')}
      <section class="answer-sheet-surface task2-booklet-surface" data-component="writing-planner"{surface_attrs('task2-writing', surface)}>
        {sections}
      </section>
      <section class="editing-checklist" data-component="editing-checklist">
        <h2>{esc(meta.get('check_label', 'Task 2 Check'))}</h2>
        <p>{inline_text(meta.get('check_note', 'Check the paragraph jobs before scoring.'))}</p>
        <div>{task2_checks(meta)}</div>
      </section>
    </main>
    """


def render_task2_answer_sheet(meta: dict) -> str:
    surface = slugify(meta.get("variant"), "task2-full-mock-answer-booklet")
    if surface == "task2-agree-disagree-answer-ladder":
        return render_task2_ladder(meta, surface)
    if surface == "task2-discussion-two-view-bridge":
        return render_task2_two_view(meta, surface)
    if surface == "task2-problem-solution-matrix":
        return render_task2_problem_solution(meta, surface)
    if surface == "task2-advantage-balance-scale":
        return render_task2_balance(meta, surface)
    return render_task2_booklet(meta, surface)


def render_task1_visual_planner(meta: dict) -> str:
    steps = "".join(
        f"""
        <article>
          <b>{esc(item.get('label', 'Step'))}</b>
          <p>{inline_text(item.get('text', ''))}</p>
        </article>
        """
        for item in meta.get("visual_steps", [])
    )
    checks = "".join(
        f"<label><span class=\"check-mark\"></span>{inline_text(item, blank_mode='compact')}</label>"
        for item in meta.get("editing", [])
    )
    return f"""
    <main class="body-page writing-page task1-visual-planner-page">
      <div class="top-rule"></div>
      <h1>Visual Plan</h1>
      <section class="visual-planner-steps" data-component="writing-planner"{surface_attrs('writing-planner', 'task1-visual-planner')}>{steps}</section>
      {workbook_rows(meta.get('record_rows', []), meta.get('record_label', 'Task 1 Planning Field'), meta.get('record_note', 'overview · details · final'))}
      <section class="editing-checklist" data-component="editing-checklist">
        <h2>Overview Check</h2>
        <div>{checks}</div>
      </section>
    </main>
    """


def render_speaking_cue_card(meta: dict) -> str:
    card = meta.get("cue_card", {})
    buckets = "".join(f"<span>{inline_text(item, blank_mode='compact')}</span>" for item in card.get("buckets", []))
    ladder = "".join(
        f"""
        <article>
          <b>{esc(item.get('label', 'Step'))}</b>
          <p>{inline_text(item.get('text', ''))}</p>
        </article>
        """
        for item in meta.get("expansion_ladder", [])
    )
    checks = "".join(
        f"<label><span class=\"check-mark\"></span>{inline_text(item, blank_mode='compact')}</label>"
        for item in meta.get("editing", [])
    )
    return f"""
    <main class="body-page writing-page speaking-cue-page">
      <div class="top-rule"></div>
      <h1>Cue Card</h1>
      <section class="cue-card-surface" data-component="writing-planner"{surface_attrs('writing-planner', 'speaking-cue-card')}>
        <aside>
          <b>Part 2 Prompt</b>
          <p>{inline_text(card.get('prompt', ''))}</p>
          <div>{buckets}</div>
        </aside>
        <div class="speaking-ladder">{ladder}</div>
      </section>
      {workbook_rows(meta.get('record_rows', []), meta.get('record_label', 'Cue-Card Notes'), meta.get('record_note', 'keywords · example · transfer'))}
      <section class="editing-checklist" data-component="editing-checklist">
        <h2>Speaking Check</h2>
        <div>{checks}</div>
      </section>
    </main>
    """


def render_reading_evidence_planner(meta: dict) -> str:
    rows = "".join(
        f"""
        <article>
          <b>{esc(item.get('label', 'Q'))}</b>
          <span>{inline_text(item.get('target', ''))}</span>
          <p>{inline_text(item.get('check', ''))}</p>
        </article>
        """
        for item in meta.get("evidence_rows", [])
    )
    checks = "".join(
        f"<label><span class=\"check-mark\"></span>{inline_text(item, blank_mode='compact')}</label>"
        for item in meta.get("editing", [])
    )
    return f"""
    <main class="body-page writing-page reading-evidence-planner-page">
      <div class="top-rule"></div>
      <h1>Evidence Record</h1>
      <section class="reading-evidence-grid" data-component="writing-planner"{surface_attrs('writing-planner', 'reading-evidence-record')}>{rows}</section>
      {workbook_rows(meta.get('record_rows', []), meta.get('record_label', 'Evidence Review'), meta.get('record_note', 'question · line clue · paraphrase'))}
      <section class="editing-checklist" data-component="editing-checklist">
        <h2>Evidence Check</h2>
        <div>{checks}</div>
      </section>
    </main>
    """


def render_writing_planner(meta: dict, book: dict, assets: dict) -> str:
    variant = str(meta.get("variant") or "")
    if variant == "book-roadmap-planner":
        return render_route_map_planner(meta)
    if variant == "daily-practice-schedule":
        return render_daily_schedule(meta)
    if variant.startswith("task2-"):
        return render_task2_answer_sheet(meta)
    if variant == "task1-visual-planner":
        return render_task1_visual_planner(meta)
    if variant == "speaking-cue-card":
        return render_speaking_cue_card(meta)
    if variant == "reading-evidence-record":
        return render_reading_evidence_planner(meta)
    instructions = "".join(f"<span>{inline_text(item)}</span>" for item in meta.get("instructions", []))
    items = meta.get("planner", [])
    requested_budget = meta.get("max_planner_lines")
    default_budget = 6 if len(items) >= 5 else 8
    line_budget = max(len(items), int(requested_budget or default_budget))
    remaining_lines = line_budget
    planner_rows = ""
    for idx, item in enumerate(items, 1):
        rows_left = len(items) - idx
        requested_lines = int(item.get("lines", 2 if len(items) >= 5 else 3))
        line_count = max(1, min(requested_lines, remaining_lines - rows_left))
        remaining_lines -= line_count
        planner_rows += f"""
        <article class="planner-row">
          <div class="planner-key">
            <span>{idx:02d}</span>
            <b>{esc(item['label'])}</b>
            <small>{inline_text(item.get('hint', ''))}</small>
          </div>
          <div class="planner-body">
            <p class="planner-prompt">{inline_text(item['prompt'])}</p>
            <div class="planner-write">{lines(line_count)}</div>
          </div>
        </article>
        """
    checks = "".join(
        f"<label><span class=\"check-mark\"></span>{inline_text(item, blank_mode='compact')}</label>"
        for item in meta.get("editing", [])
    )
    return f"""
    <main class="body-page writing-page">
      <div class="top-rule"></div>
      <h1>Writing</h1>
      <section class="activity-block" data-component="activity-block">
        <h3><span>Activity {esc(meta['activity_no'])}</span> | {esc(meta['title'])}</h3>
        <div class="review-rules">{instructions}</div>
      </section>
      <section class="planner-surface">
        <div class="paragraph-label">Writing Plan</div>
        <aside class="planner-note">
          <b>Rule</b>
          <span>one focus · one proof · one next step</span>
        </aside>
        <div class="planner-rows" data-component="writing-planner">{planner_rows}</div>
      </section>
      <section class="editing-checklist" data-component="editing-checklist">
        <h2>{esc(meta.get('check_label', 'Editing'))}</h2>
        <p>{inline_text(meta.get('check_note', 'Before the next page, check the plan once.'))}</p>
        <div>{checks}</div>
      </section>
    </main>
    """


def render_handbook(meta: dict, book: dict, assets: dict) -> str:
    entries = "".join(
        f"<tr><th><span>{idx:02d}</span>{esc(name)}</th><td>{inline_text(desc)}</td></tr>"
        for idx, (name, desc) in enumerate(meta.get("entries", []), 1)
    )
    table = table_html(meta["table"]["headers"], meta["table"]["rows"], component="handbook-table")
    rules = "".join(
        f"<article><b>{esc(item['label'])}</b><span>{inline_text(item['text'], blank_mode='compact')}</span></article>"
        for item in meta.get("rules", [])
    )
    return f"""
    <main class="handbook-page" data-component="handbook-page">
      <div class="top-rule"></div>
      <h1>{esc(meta['heading'])}</h1>
      <div class="handbook-meta">
        <span>{esc(meta.get('kicker', 'Handbook'))}</span>
        <span>{esc(meta.get('reference_label', 'Writing reference'))}</span>
        <span>{esc(meta.get('reference_note', 'Find / Check / Revise'))}</span>
      </div>
      <p class="handbook-lead">{inline_text(meta.get('lead', 'Use this page as a compact reference before writing, checking, or revising.'))}</p>
      <section class="handbook-section">
        <h2>{esc(meta.get('index_title', 'Language & Record Index'))}</h2>
        <table class="handbook-index"><tbody>{entries}</tbody></table>
      </section>
      <section class="handbook-section handbook-rule-section">
        <h2>{esc(meta.get('rules_title', 'Revision Rule'))}</h2>
        <section class="handbook-rules">{rules}</section>
      </section>
      <section class="handbook-section handbook-rhythm-section">
        <h2>{esc(meta.get('table_title', 'Reference Table'))}</h2>
      {table}
      </section>
    </main>
    """


def normalized_answer_groups(meta: dict) -> list[dict]:
    groups = meta.get("answer_groups") or meta.get("groups")
    if groups:
        return groups
    return [
        {
            "title": meta.get("table_title", "Answer Index"),
            "note": meta.get("table_note", "Compact answer lookup."),
            "items": meta.get("answers", []),
        }
    ]


def answer_row_markup(item) -> str:
    if isinstance(item, dict):
        label = item.get("label", "")
        answer = item.get("answer", item.get("text", ""))
        note = item.get("note", "")
    else:
        values = list(item)
        label = values[0] if values else ""
        answer = values[1] if len(values) > 1 else ""
        note = values[2] if len(values) > 2 else ""
    note_markup = f"<small>{inline_text(note)}</small>" if note else ""
    return f"<tr><th>{esc(label)}</th><td><span class=\"answer-main\">{inline_text(answer)}</span>{note_markup}</td></tr>"


def render_answer_key(meta: dict, book: dict, assets: dict) -> str:
    meta_items = meta.get("meta_items") or ["Teacher profile", "Back matter", "Student pages exclude this key"]
    meta_strip = "".join(f"<span>{esc(item)}</span>" for item in meta_items[:3])
    groups = "".join(
        f"""
        <article class="answer-group">
          <h2><span>{idx:02d}</span>{esc(group.get('title', 'Answer Group'))}</h2>
          <p>{inline_text(group.get('note', ''))}</p>
          <table class="answer-table" data-component="answer-key-page"><tbody>{''.join(answer_row_markup(item) for item in (group.get('items') or group.get('answers') or []))}</tbody></table>
        </article>
        """
        for idx, group in enumerate(normalized_answer_groups(meta), 1)
    )
    return f"""
    <main class="answer-key-page" data-component="answer-key-page">
      <div class="top-rule"></div>
      <h1>{esc(meta['heading'])}</h1>
      <div class="handbook-meta answer-key-meta">{meta_strip}</div>
      <p>{esc(meta.get('note', ''))}</p>
      <section class="answer-key-grid">{groups}</section>
    </main>
    """


def render_contents_route(meta: dict, book: dict, assets: dict) -> str:
    rows = "".join(
        f"""
        <article>
          <b>{esc(item.get('code', f'{idx:02d}'))}</b>
          <div>
            <h2>{esc(item.get('title', 'Unit Step'))}</h2>
            <p>{inline_text(item.get('text', ''))}</p>
          </div>
        </article>
        """
        for idx, item in enumerate(meta.get("route", []), 1)
    )
    return f"""
    <main class="body-page contents-route-page">
      <div class="top-rule"></div>
      {section_ribbon(meta, 'Contents')}
      <h1>{esc(meta.get('heading', 'Contents Map'))}</h1>
      <p class="lead">{inline_text(meta.get('lead', 'Use this map to see how the unit moves from noticing to output.'))}</p>
      <section class="contents-route" data-component="title-navigation">{rows}</section>
      {contents_scope_map(meta.get('scope_rows', []))}
      {contents_page_index(meta.get('page_index', []))}
    </main>
    """


def render_diagnostic_entry(meta: dict, book: dict, assets: dict) -> str:
    return f"""
    <main class="body-page diagnostic-entry-page">
      <div class="top-rule"></div>
      {section_ribbon(meta, 'Diagnostic')}
      {skill_side_labels(meta.get('labels', []))}
      <h1>{esc(meta.get('heading', 'Before You Start'))}</h1>
      <p class="lead">{inline_text(meta.get('lead', 'Check what you can already do before the lesson starts.'))}</p>
      {diagnostic_ladder(meta.get('diagnostic_ladder', []))}
      {guided_mcq(meta.get('checks', []))}
      {diagnostic_notes(meta.get('diagnostic_notes', []))}
      {workbook_rows(meta.get('record_rows', []), meta.get('record_label', 'Diagnostic Record'), meta.get('record_note', 'one clue · one risk · one next step'))}
    </main>
    """


def render_article_opener(meta: dict, book: dict, assets: dict) -> str:
    return f"""
    <main class="body-page article-opener-page">
      {section_ribbon(meta, 'Reading')}
      <header class="article-title-lockup" data-component="article-title-lockup">
        <h1>{esc(meta.get('heading', 'Concept Opener'))}</h1>
        <p>{inline_text(meta.get('subheading', ''))}</p>
      </header>
      <section class="article-flow">
        {lettered_paragraphs(meta.get('paragraphs', []))}
      </section>
      {definition_notes(meta.get('notes', []))}
      {evidence_task_strip(meta.get('evidence_task_rows', []))}
    </main>
    """


def render_article_evidence(meta: dict, book: dict, assets: dict) -> str:
    src = asset_path(meta.get("asset", ""), assets)
    visual = f"<figure class=\"evidence-visual\"><img src=\"{esc(src)}\" alt=\"\"><figcaption>{esc(meta.get('caption', ''))}</figcaption></figure>" if src else ""
    evidence_record = (
        workbook_rows(
            meta.get("record_rows", []),
            meta.get("record_label", "Evidence Check"),
            meta.get("record_note", "sentence clue · grammar job · answer"),
        )
        if meta.get("record_rows")
        else ""
    )
    return f"""
    <main class="body-page article-evidence-page">
      <div class="top-rule"></div>
      {section_ribbon(meta, 'Evidence')}
      <h1>{esc(meta.get('heading', 'Evidence Page'))}</h1>
      {visual}
      {diagram_callout(meta.get('diagram', {}))}
      {evidence_flow(meta.get('evidence_paragraphs', []))}
      {evidence_cues(meta.get('evidence_cues', []))}
      {evidence_task_strip(meta.get('evidence_task_rows', []))}
      {definition_notes(meta.get('notes', []))}
      {evidence_record}
    </main>
    """


def render_skill_method(meta: dict, book: dict, assets: dict) -> str:
    applications = "".join(
        f"""
        <article>
          <b>{esc(item.get('label', f'{idx:02d}'))}</b>
          <h3>{esc(item.get('title', 'Use It'))}</h3>
          <p>{inline_text(item.get('text', ''))}</p>
        </article>
        """
        for idx, item in enumerate(meta.get("method_applications", []), 1)
    )
    application_block = (
        f"""
        <section class="method-application" data-component="guided-discovery">
          {applications}
        </section>
        """
        if applications
        else ""
    )
    return f"""
    <main class="body-page skill-method-page">
      <div class="top-rule"></div>
      {section_ribbon(meta, 'Skill')}
      {skill_side_labels(meta.get('labels', []))}
      <h1>{esc(meta.get('heading', 'Skill Method'))}</h1>
      <section class="method-card" data-component="mechanics-table">
        <h2>{esc(meta.get('method_title', 'Method'))}</h2>
        <p>{inline_text(meta.get('method', ''))}</p>
      </section>
      {table_html(meta.get('table', {}).get('headers', []), meta.get('table', {}).get('rows', []))}
      {application_block}
      {critical_strip(meta.get('checks', []), meta.get('check_label', 'Try It'))}
    </main>
    """


def render_sentence_map(meta: dict, book: dict, assets: dict) -> str:
    headers = meta.get('chart', {}).get('headers', [])
    chart_rows = meta.get('chart', {}).get('rows', [])
    sentence_cards = sentence_map_cards(headers, chart_rows)
    return f"""
    <main class="body-page sentence-map-page">
      <div class="top-rule"></div>
      {section_ribbon(meta, 'Map')}
      {skill_side_labels(meta.get('labels', []))}
      <h1>{esc(meta.get('heading', 'Sentence Map'))}</h1>
      {diagram_callout(meta.get('diagram', {}))}
      {sentence_cards}
      {critical_strip(meta.get('checks', []), meta.get('check_label', 'Map Check'))}
    </main>
    """


def render_categorizing_chart(meta: dict, book: dict, assets: dict) -> str:
    return f"""
    <main class="body-page categorizing-chart-page">
      <div class="top-rule"></div>
      {section_ribbon(meta, 'Practice')}
      {skill_side_labels(meta.get('labels', []))}
      <h1>{esc(meta.get('heading', 'Categorizing Chart'))}</h1>
      <p class="lead">{inline_text(meta.get('lead', 'Put each example into the right group.'))}</p>
      {table_html(meta.get('chart', {}).get('headers', []), meta.get('chart', {}).get('rows', []), component='categorizing-chart')}
      {workbook_rows(meta.get('record_rows', []), meta.get('record_label', 'Chart Record'), meta.get('record_note', 'category · reason · correction'))}
    </main>
    """


def render_exam_mini_set(meta: dict, book: dict, assets: dict) -> str:
    return f"""
    <main class="body-page exam-mini-set-page">
      <div class="top-rule"></div>
      {section_ribbon(meta, 'Exam Set')}
      {skill_side_labels(meta.get('labels', []))}
      <h1>{esc(meta.get('heading', 'Mini Set'))}</h1>
      {exam_timing_strip(meta.get('timing_note', ''))}
      {guided_mcq(meta.get('questions', []))}
      {exam_pressure_grid(meta.get('pressure_rows', []))}
      {workbook_rows(meta.get('record_rows', []), meta.get('record_label', 'Score Record'), meta.get('record_note', 'wrong item · cause · next drill'))}
    </main>
    """


def render_correction_rewrite(meta: dict, book: dict, assets: dict) -> str:
    checks = "".join(
        f"<label><span class=\"check-mark\"></span>{inline_text(item, blank_mode='compact')}</label>"
        for item in meta.get("editing", [])
    )
    return f"""
    <main class="body-page correction-rewrite-page">
      <div class="top-rule"></div>
      {section_ribbon(meta, 'Rewrite')}
      <h1>{esc(meta.get('heading', 'Correction Rewrite'))}</h1>
      <p class="lead rewrite-note">{inline_text(meta.get('lesson_note', 'Rewrite the sentence and keep the reason visible.'))}</p>
      {rewrite_lens(meta.get('lens', []))}
      {workbook_rows(meta.get('rewrite_rows', []), meta.get('record_label', 'Rewrite Record'), meta.get('record_note', 'error · better sentence · reason'))}
      {rewrite_micro_rules(meta.get('micro_rules', []))}
      <section class="editing-checklist" data-component="editing-checklist">
        <h2>{esc(meta.get('check_label', 'Final Check'))}</h2>
        <div>{checks}</div>
      </section>
    </main>
    """


def listening_checks(meta: dict) -> str:
    return "".join(
        f"<label><span class=\"check-mark\"></span>{inline_text(item, blank_mode='compact')}</label>"
        for item in meta.get("editing", [])
    )


def listening_action_rows(meta: dict) -> str:
    return "".join(
        f"""
        <article>
          <b>{esc(item.get('label', f'{idx:02d}'))}</b>
          <p>{inline_text(item.get('prompt', ''))}</p>
          {lines(int(item.get('lines', 1)))}
        </article>
        """
        for idx, item in enumerate(meta.get("action_rows", []), 1)
    )


def render_listening_surface(meta: dict, surface: str) -> str:
    if surface == "listening-part1-form-ledger":
        rows = meta.get("form_rows") or meta.get("rewrite_rows", [])
        items = "".join(
            f"""
            <article>
              <b>{esc(item.get('label', f'{idx:02d}'))}</b>
              <span>{inline_text(item.get('prompt', item.get('text', '')))}</span>
              {lines(int(item.get('lines', 1)))}
            </article>
            """
            for idx, item in enumerate(rows, 1)
        )
        return f'<section class="listening-form-ledger listening-role-surface" data-component="critical-thinking-strip"{surface_attrs("listening-review", surface)}>{items}</section>'
    if surface == "listening-part2-map-path-surface":
        path = meta.get("map_path") or meta.get("replay_map", [])
        nodes = "".join(
            f"""
            <article>
              <b>{esc(item.get('label', f'{idx:02d}'))}</b>
              <h2>{esc(item.get('title', item.get('place', 'Place')))}</h2>
              <p>{inline_text(item.get('text', item.get('prompt', '')))}</p>
            </article>
            """
            for idx, item in enumerate(path, 1)
        )
        return f"""
        <section class="listening-map-path listening-role-surface" data-component="critical-thinking-strip"{surface_attrs('listening-review', surface)}>
          <div class="map-path-field">{nodes}</div>
          <aside>
            <b>Pause & point</b>
            <span>{inline_text(meta.get('map_note', 'Trace the movement before choosing the option.'))}</span>
          </aside>
        </section>
        """
    if surface == "listening-part3-speaker-opinion-matrix":
        rows = meta.get("speaker_rows") or meta.get("replay_map", [])
        items = "".join(
            f"""
            <article>
              <b>{esc(item.get('speaker', item.get('label', f'S{idx}')))}</b>
              <span>{inline_text(item.get('view', item.get('title', 'View')))}</span>
              <p>{inline_text(item.get('evidence', item.get('text', '')))}</p>
            </article>
            """
            for idx, item in enumerate(rows, 1)
        )
        return f'<section class="speaker-opinion-matrix listening-role-surface" data-component="critical-thinking-strip"{surface_attrs("listening-review", surface)}>{items}</section>'
    if surface == "listening-part4-lecture-note-columns":
        columns = meta.get("lecture_columns") or meta.get("replay_map", [])
        items = "".join(
            f"""
            <article>
              <b>{esc(item.get('label', f'{idx:02d}'))}</b>
              <h2>{esc(item.get('title', 'Note'))}</h2>
              <p>{inline_text(item.get('text', ''))}</p>
              {lines(int(item.get('lines', 1)))}
            </article>
            """
            for idx, item in enumerate(columns, 1)
        )
        return f'<section class="lecture-note-columns listening-role-surface" data-component="critical-thinking-strip"{surface_attrs("listening-review", surface)}>{items}</section>'
    replay = "".join(
        f"""
        <article>
          <b>{esc(item.get('label', 'Step'))}</b>
          <h2>{esc(item.get('title', 'Replay'))}</h2>
          <p>{inline_text(item.get('text', ''))}</p>
        </article>
        """
        for item in meta.get("replay_map", [])
    )
    return f'<section class="listening-replay-map listening-role-surface" data-component="critical-thinking-strip"{surface_attrs("listening-review", surface)}>{replay}</section>'


def listening_record_cards(rows: list[dict], *, class_name: str) -> str:
    cards = "".join(
        f"""
        <article>
          <b>{esc(item.get('label', f'{idx:02d}'))}</b>
          <p>{inline_text(item.get('prompt', ''))}</p>
          {lines(int(item.get('lines', 1)))}
        </article>
        """
        for idx, item in enumerate(rows, 1)
    )
    return f'<section class="{class_name}" data-component="workbook-practice">{cards}</section>'


def listening_check_panel(meta: dict, *, class_name: str, title: str | None = None) -> str:
    checks = listening_checks(meta)
    return f"""
    <section class="{class_name}" data-component="editing-checklist">
      <h2>{esc(title or meta.get('check_label', 'Replay Check'))}</h2>
      <p>{inline_text(meta.get('check_note', 'Replay once. Stop when the cause is clear.'))}</p>
      <div>{checks}</div>
    </section>
    """


def listening_drill_panel(meta: dict, *, class_name: str, title: str | None = None) -> str:
    return f"""
    <section class="{class_name}">
      <h2>{esc(title or meta.get('action_label', 'Next Listening Drill'))}</h2>
      <div>{listening_action_rows(meta)}</div>
    </section>
    """


def render_listening_review_body(meta: dict, surface: str) -> str:
    focus_surface = render_listening_surface(meta, surface)
    rows = meta.get("rewrite_rows", [])
    if surface == "listening-part1-form-ledger":
        return f"""
        {focus_surface}
        <section class="listening-ledger-lower">
          <div>
            <h2>{esc(meta.get('record_label', 'Form Replay Ledger'))}</h2>
            {listening_record_cards(rows, class_name='part1-ledger-record')}
          </div>
          {listening_check_panel(meta, class_name='part1-ledger-check', title='Form Check')}
        </section>
        {listening_drill_panel(meta, class_name='part1-drill-strip')}
        """
    if surface == "listening-part2-map-path-surface":
        return f"""
        {focus_surface}
        <section class="map-route-notebook" data-component="workbook-practice">
          <div class="map-route-record">
            <h2>{esc(meta.get('record_label', 'Map Route Record'))}</h2>
            {listening_record_cards(rows, class_name='map-route-steps')}
          </div>
          <aside>
            {listening_check_panel(meta, class_name='map-route-check', title='Map Check')}
            {listening_drill_panel(meta, class_name='map-route-drill', title='Next Map Drill')}
          </aside>
        </section>
        """
    if surface == "listening-part3-speaker-opinion-matrix":
        return f"""
        {focus_surface}
        <section class="speaker-review-board">
          {listening_record_cards(rows, class_name='speaker-review-record')}
          <div class="speaker-review-side">
            {listening_check_panel(meta, class_name='speaker-review-check', title='Opinion Check')}
            {listening_drill_panel(meta, class_name='speaker-review-drill', title='Next Opinion Drill')}
          </div>
        </section>
        """
    if surface == "listening-part4-lecture-note-columns":
        return f"""
        {focus_surface}
        <section class="lecture-review-sheet">
          <div class="lecture-cornell">
            <h2>{esc(meta.get('record_label', 'Lecture Note Record'))}</h2>
            {listening_record_cards(rows, class_name='lecture-note-record')}
          </div>
          <div class="lecture-bottom-row">
            {listening_check_panel(meta, class_name='lecture-note-check', title='Lecture Check')}
            {listening_drill_panel(meta, class_name='lecture-note-drill', title='Next Lecture Drill')}
          </div>
        </section>
        """
    return f"""
    {focus_surface}
    {workbook_rows(rows, meta.get('record_label', 'Replay Record'), meta.get('record_note', 'answer type · signal · distractor'))}
    {listening_check_panel(meta, class_name='editing-checklist final-checklist')}
    {listening_drill_panel(meta, class_name='final-action-ticket listening-drill-ticket')}
    """


def render_listening_replay(meta: dict) -> str:
    variant = slugify(meta.get("variant"), "listening-replay-record")
    surface_map = {
        "listening-part-1-replay": "listening-part1-form-ledger",
        "listening-part-2-replay": "listening-part2-map-path-surface",
        "listening-part-3-replay": "listening-part3-speaker-opinion-matrix",
        "listening-part-4-replay": "listening-part4-lecture-note-columns",
    }
    surface = surface_map.get(variant, variant)
    return f"""
    <main class="body-page final-check-page listening-replay-page listening-surface-page"{surface_attrs('listening-review', surface)}>
      <div class="top-rule"></div>
      {section_ribbon(meta, 'Listening')}
      <h1>{esc(meta.get('heading', 'Listening Replay'))}</h1>
      <p class="lead listening-focus">{inline_text(meta.get('listening_focus', ''))}</p>
      {render_listening_review_body(meta, surface)}
    </main>
    """


def render_reading_close(meta: dict) -> str:
    surface = slugify(meta.get("variant"), "reading-line-evidence-close")
    checks_grid = "".join(
        f"""
        <article>
          <b>{esc(item.get('label', 'Check'))}</b>
          <p>{inline_text(item.get('text', ''))}</p>
        </article>
        """
        for item in meta.get("evidence_checks", [])
    )
    if surface == "reading-paraphrase-pair-close":
        pairs = meta.get("paraphrase_pairs") or meta.get("evidence_checks", [])
        checks_grid = "".join(
            f"""
            <article>
              <b>{esc(item.get('label', f'{idx:02d}'))}</b>
              <span>{inline_text(item.get('source', item.get('text', '')))}</span>
              <p>{inline_text(item.get('paraphrase', item.get('prompt', '')))}</p>
              <small>{inline_text(item.get('trap', ''))}</small>
            </article>
            """
            for idx, item in enumerate(pairs, 1)
        )
        surface_class = "reading-paraphrase-pairs"
    elif surface == "reading-transfer-ticket-close":
        transfer = meta.get("transfer_rows") or meta.get("evidence_checks", [])
        checks_grid = "".join(
            f"""
            <article>
              <b>{esc(item.get('label', f'{idx:02d}'))}</b>
              <h2>{esc(item.get('title', item.get('text', 'Transfer')))}</h2>
              <p>{inline_text(item.get('prompt', item.get('target', '')))}</p>
              {lines(int(item.get('lines', 1)))}
            </article>
            """
            for idx, item in enumerate(transfer, 1)
        )
        surface_class = "reading-transfer-ticket"
    else:
        surface = "reading-line-evidence-close" if surface.startswith("reading-passage-") else surface
        surface_class = "reading-close-grid"
    checks = "".join(
        f"<label><span class=\"check-mark\"></span>{inline_text(item, blank_mode='compact')}</label>"
        for item in meta.get("editing", [])
    )
    return f"""
    <main class="body-page final-check-page reading-close-page"{surface_attrs('reading-review', surface)}>
      <div class="top-rule"></div>
      {section_ribbon(meta, 'Reading')}
      <h1>{esc(meta.get('heading', 'Reading Evidence Close'))}</h1>
      <p class="lead reading-focus">{inline_text(meta.get('reading_focus', ''))}</p>
      <section class="{surface_class}" data-component="critical-thinking-strip"{surface_attrs('reading-review', surface)}>{checks_grid}</section>
      {workbook_rows(meta.get('rewrite_rows', []), meta.get('record_label', 'Reading Evidence Close'), meta.get('record_note', 'line · paraphrase · trap'))}
      <section class="editing-checklist final-checklist" data-component="editing-checklist">
        <h2>{esc(meta.get('check_label', 'Evidence Check'))}</h2>
        <p>{inline_text(meta.get('check_note', 'Keep the answer only if evidence can be named.'))}</p>
        <div>{checks}</div>
      </section>
    </main>
    """


def render_frontmatter_checkpoint(meta: dict) -> str:
    variant = re.sub(r"[^a-zA-Z0-9_-]+", "-", str(meta.get("variant") or "frontmatter-checkpoint")).strip("-").lower()
    steps = meta.get("thinking_steps", [])
    step_rows = "".join(
        f"""
        <article>
          <b>{esc(item.get('label', f'{idx:02d}'))}</b>
          <h2>{esc(item.get('title', 'Check'))}</h2>
          <p>{inline_text(item.get('text', ''))}</p>
        </article>
        """
        for idx, item in enumerate(steps, 1)
    )
    checks = "".join(
        f"<label><span class=\"check-mark\"></span>{inline_text(item, blank_mode='compact')}</label>"
        for item in meta.get("editing", [])
    )
    return f"""
    <main class="body-page final-check-page frontmatter-checkpoint-page frontmatter-{esc(variant)}"{surface_attrs('final-check', variant)}>
      <div class="top-rule"></div>
      {section_ribbon(meta, 'Start')}
      <h1>{esc(meta.get('heading', 'Start Check'))}</h1>
      {final_check_summary(meta.get('summary_checks', []))}
      <section class="frontmatter-check-grid" data-component="critical-thinking-strip"{surface_attrs('final-check', variant)}>{step_rows}</section>
      {workbook_rows(meta.get('rewrite_rows', []), meta.get('record_label', 'Start Record'), meta.get('record_note', 'time · evidence · next action'))}
      <section class="editing-checklist final-checklist" data-component="editing-checklist">
        <h2>{esc(meta.get('check_label', 'Start Check'))}</h2>
        <p>{inline_text(meta.get('check_note', 'Check the next practice.'))}</p>
        <div>{checks}</div>
      </section>
    </main>
    """


def render_final_check(meta: dict, book: dict, assets: dict) -> str:
    variant = str(meta.get("variant") or "")
    if variant.startswith("listening-"):
        return render_listening_replay(meta)
    if variant.startswith("reading-"):
        return render_reading_close(meta)
    if variant in {"weekend-mock-review", "book-learning-contract", "learning-data-record", "frontmatter-checkpoint"}:
        return render_frontmatter_checkpoint(meta)
    thinking_steps = meta.get(
        "thinking_steps",
        [
            {"label": "01", "title": "Before choosing", "text": "Mark the finite predicate first."},
            {"label": "02", "title": "During checking", "text": "Name the missing part or logic signal."},
            {"label": "03", "title": "After correcting", "text": "Write one next drill, not a general promise."},
        ],
    )
    strip = "".join(
        f"""
        <article>
          <b>{esc(item.get('label', f'{idx:02d}'))}</b>
          <h2>{esc(item.get('title', 'Check'))}</h2>
          <p>{inline_text(item.get('text', ''))}</p>
        </article>
        """
        for idx, item in enumerate(thinking_steps, 1)
    )
    checks = "".join(
        f"<label><span class=\"check-mark\"></span>{inline_text(item, blank_mode='compact')}</label>"
        for item in meta.get("editing", [])
    )
    action_rows = "".join(
        f"""
        <article>
          <b>{esc(item.get('label', f'{idx:02d}'))}</b>
          <p>{inline_text(item.get('prompt', ''))}</p>
          {lines(int(item.get('lines', 1)))}
        </article>
        """
        for idx, item in enumerate(meta.get("action_rows", []), 1)
    )
    action_panel = (
        f"""
        <section class="final-action-ticket">
          <h2>{esc(meta.get('action_label', 'Exit Ticket'))}</h2>
          <div>{action_rows}</div>
        </section>
        """
        if action_rows
        else ""
    )
    return f"""
    <main class="body-page final-check-page"{surface_attrs('final-check', variant or 'unit-final-check')}>
      <div class="top-rule"></div>
      {section_ribbon(meta, 'Final Check')}
      <h1>{esc(meta.get('heading', 'Final Check'))}</h1>
      {final_check_summary(meta.get('summary_checks', []))}
      <section class="critical-thinking-strip final-check-strip" data-component="critical-thinking-strip"{surface_attrs('final-check', variant or 'unit-final-check')}>
        {strip}
      </section>
      {workbook_rows(meta.get('rewrite_rows', []), meta.get('record_label', 'Next-Step Record'), meta.get('record_note', 'strength · weak point · next drill'))}
      <section class="editing-checklist final-checklist" data-component="editing-checklist">
        <h2>{esc(meta.get('check_label', 'Before The Next Set'))}</h2>
        <p>{inline_text(meta.get('check_note', 'Tick only what you can prove from this unit.'))}</p>
        <div>{checks}</div>
      </section>
      {action_panel}
    </main>
    """


def render_vocab_bank(meta: dict, book: dict, assets: dict) -> str:
    return f"""
    <main class="handbook-page vocab-bank-page" data-component="handbook-page">
      <div class="top-rule"></div>
      {section_ribbon(meta, 'Vocabulary')}
      <h1>{esc(meta.get('heading', 'Vocabulary Bank'))}</h1>
      {render_words_to_know(meta.get('items', []), meta.get('label', 'Vocabulary Bank'))}
      {table_html(meta.get('table', {}).get('headers', []), meta.get('table', {}).get('rows', []), component='handbook-table')}
    </main>
    """


def render_connector_index(meta: dict, book: dict, assets: dict) -> str:
    bank = "".join(
        f"<span class=\"word-box-item\">{inline_text(item, blank_mode='wordbox')}</span>"
        for item in meta.get("connectors", [])
    )
    return f"""
    <main class="handbook-page connector-index-page" data-component="handbook-page">
      <div class="top-rule"></div>
      {section_ribbon(meta, 'Index')}
      <h1>{esc(meta.get('heading', 'Connector Index'))}</h1>
      <div class="word-box connector-bank" data-component="practice-word-box">{bank}</div>
      {table_html(meta.get('table', {}).get('headers', []), meta.get('table', {}).get('rows', []), component='handbook-table')}
    </main>
    """


def render_teacher_answer_key(meta: dict, book: dict, assets: dict) -> str:
    body = render_answer_key(meta, book, assets)
    return body.replace('data-component="answer-key-page"', 'data-component="answer-key-page" data-teacher-only="true"', 1)


def render_teacher_guide_page(meta: dict, book: dict, assets: dict) -> str:
    meta_items = meta.get("meta_items") or ["Teacher Edition", "Guide", "Answer Focus"]
    meta_strip = "".join(f"<span>{esc(item)}</span>" for item in meta_items[:4])
    flow = "".join(
        f"""
        <article>
          <b>{esc(row.get('time', f'{idx:02d}'))}</b>
          <div>
            <h2>{esc(row.get('title', 'Teaching Move'))}</h2>
            <p>{inline_text(row.get('text', ''))}</p>
          </div>
        </article>
        """
        for idx, row in enumerate(meta.get("flow_rows", []), 1)
    )
    notes = "".join(
        f"""
        <article>
          <b>{esc(note.get('page', 'p'))}</b>
          <h2>{esc(note.get('title', 'Page Note'))}</h2>
          <p>{inline_text(note.get('focus', ''))}</p>
          <small>{inline_text(note.get('teacher_move', ''))}</small>
        </article>
        """
        for note in meta.get("page_notes", [])
    )
    board = "".join(f"<li>{inline_text(item)}</li>" for item in meta.get("board_notes", []))
    answer_groups = "".join(
        f"""
        <article class="answer-group">
          <h2><span>{idx:02d}</span>{esc(group.get('title', 'Answer Group'))}</h2>
          <p>{inline_text(group.get('note', ''))}</p>
          <table class="answer-table" data-component="answer-key-page" data-teacher-only="true">
            <tbody>{''.join(answer_row_markup(item) for item in (group.get('items') or group.get('answers') or []))}</tbody>
          </table>
        </article>
        """
        for idx, group in enumerate(normalized_answer_groups(meta), 1)
    )
    return f"""
    <main class="teacher-guide-page" data-component="teacher-guide-page" data-teacher-only="true">
      <div class="top-rule"></div>
      <h1>{esc(meta.get('heading', 'Teacher Guide'))}</h1>
      <div class="handbook-meta teacher-guide-meta">{meta_strip}</div>
      <p class="lead">{inline_text(meta.get('lead', meta.get('note', '')))}</p>
      <section class="teacher-guide-flow">{flow}</section>
      <section class="teacher-guide-notes">{notes}</section>
      <section class="teacher-board-notes"><h2>Board Notes</h2><ul>{board}</ul></section>
      <section class="answer-key-grid teacher-guide-answers">{answer_groups}</section>
    </main>
    """


RENDERERS = {
    "cover": render_cover,
    "title": render_title,
    "contents-route": render_contents_route,
    "diagnostic-entry": render_diagnostic_entry,
    "unit-opener": render_unit_opener,
    "article-opener": render_article_opener,
    "article-evidence": render_article_evidence,
    "skill-method": render_skill_method,
    "sentence-map": render_sentence_map,
    "elements": render_elements,
    "activity": render_activity,
    "categorizing-chart": render_categorizing_chart,
    "exam-mini-set": render_exam_mini_set,
    "paragraph-practice": render_paragraph_practice,
    "photo-passage": render_photo_passage,
    "writing-planner": render_writing_planner,
    "correction-rewrite": render_correction_rewrite,
    "final-check": render_final_check,
    "handbook": render_handbook,
    "vocab-bank": render_vocab_bank,
    "connector-index": render_connector_index,
    "answer-key": render_answer_key,
    "teacher-answer-key": render_teacher_answer_key,
    "teacher-guide-page": render_teacher_guide_page,
}


def css(book: dict, tokens: dict, profile: str) -> str:
    spec = book["profiles"][profile]
    width = spec["page_width_pt"]
    height = spec["page_height_pt"]
    return f"""
    @page {{ size: {width}pt {height}pt; margin: 0; }}
    :root {{
      --page-w: {width}pt;
      --page-h: {height}pt;
      --paper: {tokens['paper']};
      --ink: {tokens['ink']};
      --muted: {tokens['muted']};
      --teal: {tokens['teal']};
      --teal-dark: {tokens['teal_dark']};
      --teal-light: {tokens['teal_light']};
      --activity: {tokens['activity']};
      --green: {tokens['green']};
      --rust: {tokens['rust']};
      --backmatter: {tokens['blue_backmatter']};
      --table-line: {tokens['table_line']};
      --hairline: {tokens['hairline']};
      --texture: {tokens['paper_texture']};
      --font-display: {tokens['font_display']};
      --font-serif: {tokens['font_serif']};
      --font-sans: {tokens['font_sans']};
      --font-cn: {tokens.get('font_cn', tokens['font_sans'])};
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; padding: 0; background: #e9e9e9; color: var(--ink); }}
    body {{ font-family: var(--font-serif); }}
    .sheet {{
      width: var(--page-w);
      height: var(--page-h);
      position: relative;
      overflow: hidden;
      page-break-after: always;
      break-after: page;
      background: var(--paper);
      margin: 0 auto 18px;
    }}
    @media print {{ body {{ background: white; }} .sheet {{ margin: 0; }} }}
    img {{ display: block; max-width: 100%; }}
    h1, h2, h3, h4, p, ul, ol {{ margin-top: 0; }}
    .body-page {{
      position: absolute;
      inset: 31pt 81pt 52pt 81pt;
      font-size: 11pt;
      line-height: 1.36;
    }}
    .top-rule {{ height: 5pt; background: var(--teal); margin-bottom: 12pt; }}
    .body-page h1, .handbook-page h1, .answer-key-page h1 {{
      font-family: var(--font-sans);
      text-transform: uppercase;
      letter-spacing: 0;
      font-size: 22pt;
      line-height: 1;
      color: #2a6f95;
      font-weight: 500;
      border-bottom: 1.2pt solid var(--teal-light);
      padding-bottom: 8pt;
      margin-bottom: 16pt;
    }}
    .body-page h2 {{
      font-family: var(--font-sans);
      color: #266e95;
      font-size: 17pt;
      line-height: 1.1;
      font-weight: 500;
      margin-bottom: 6pt;
    }}
    .lead {{ font-size: 12pt; }}
    .section-ribbon {{
      display: inline-flex;
      align-items: center;
      gap: 8pt;
      margin: 0 0 8pt;
      font-family: var(--font-sans);
      font-size: 8.6pt;
      line-height: 1;
      color: #5d4c18;
      text-transform: uppercase;
      letter-spacing: 0;
    }}
    .section-ribbon b {{
      background: #f4d642;
      color: #3c3510;
      padding: 4.5pt 7pt 3.8pt;
      font-weight: 900;
    }}
    .section-ribbon span {{ color: var(--muted); text-transform: none; }}
    .skill-side-label {{
      position: absolute;
      left: -53pt;
      top: 92pt;
      width: 42pt;
      display: grid;
      gap: 5pt;
      font-family: var(--font-sans);
      font-size: 7.6pt;
      color: var(--teal-dark);
      text-align: right;
    }}
    .skill-side-label span {{
      border-right: 2pt solid rgba(16, 119, 143, .55);
      padding-right: 5pt;
      min-height: 13pt;
    }}
    .article-title-lockup h1 {{
      font-family: var(--font-sans);
      font-size: 29pt;
      line-height: 1.02;
      color: #214f68;
      letter-spacing: 0;
      margin-bottom: 5pt;
    }}
    .article-title-lockup p {{
      max-width: 320pt;
      font-family: var(--font-sans);
      color: #5d7377;
      line-height: 1.34;
    }}
    .article-flow {{
      display: grid;
      gap: 11pt;
      margin-top: 18pt;
    }}
    .lettered-paragraph {{
      display: grid;
      grid-template-columns: 28pt 1fr;
      gap: 12pt;
      break-inside: avoid;
    }}
    .lettered-paragraph b {{
      width: 22pt;
      height: 22pt;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      background: rgba(18,126,148,.12);
      color: var(--teal-dark);
      font-family: var(--font-sans);
      font-weight: 900;
    }}
    .lettered-paragraph p {{
      font-size: 11.4pt;
      line-height: 1.62;
      margin: 0;
    }}
    .definition-footnote {{
      margin-top: 14pt;
      display: grid;
      gap: 5pt;
      font-family: var(--font-sans);
      font-size: 8.8pt;
      color: #52696d;
      border-top: 0.75pt solid #c7d9d8;
      padding-top: 8pt;
    }}
    .evidence-visual {{
      float: right;
      width: 150pt;
      height: 140pt;
      margin: 0 0 12pt 16pt;
      overflow: hidden;
      border: 0.8pt solid #d1dcda;
    }}
    .evidence-visual img {{ width: 100%; height: 100%; object-fit: cover; }}
    .evidence-visual figcaption {{
      font-family: var(--font-sans);
      font-size: 7.8pt;
      color: var(--muted);
      margin-top: 3pt;
    }}
    .article-evidence-page .diagram-callout {{
      margin: 12pt 0 14pt;
      padding: 18pt 18pt 16pt;
      box-shadow: inset 0 0 0 0.75pt rgba(18,126,148,.10);
    }}
    .article-evidence-page .definition-footnote {{
      border-top: 1.1pt solid rgba(18,126,148,.30);
      padding-top: 10pt;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8pt;
      margin-top: 13pt;
      font-size: 8.7pt;
      line-height: 1.36;
    }}
    .article-evidence-page .definition-footnote span {{
      display: block;
      min-height: 46pt;
      padding: 7pt 8pt 6pt;
      background: rgba(235,245,243,.72);
      border-top: 1.4pt solid rgba(18,126,148,.45);
      box-shadow: inset 0 0 0 0.6pt rgba(18,126,148,.10);
    }}
    .article-evidence-page .workbook-record {{
      margin-top: 13pt;
      padding: 9pt 14pt 8pt;
    }}
    .article-evidence-page .record-row {{
      min-height: 42pt;
      padding: 6.2pt 0 4.5pt;
    }}
    .article-evidence-page .record-prompt {{
      font-size: 9.3pt;
      margin-bottom: 2pt;
    }}
    .evidence-flow {{
      display: grid;
      gap: 7.5pt;
      margin: 9pt 0 10pt;
      padding: 9pt 11pt 8pt;
      background:
        linear-gradient(90deg, rgba(238,248,246,.68), rgba(255,255,255,.72) 38%),
        #fbfbf8;
      box-shadow: inset 0 0 0 0.65pt rgba(18,126,148,.11);
    }}
    .evidence-flow .lettered-paragraph {{
      grid-template-columns: 24pt 1fr;
      gap: 8pt;
    }}
    .evidence-flow .lettered-paragraph b {{
      width: 18pt;
      height: 18pt;
      font-size: 8pt;
    }}
    .evidence-flow .lettered-paragraph p {{
      font-size: 9.45pt;
      line-height: 1.38;
      color: #2f4549;
    }}
    .evidence-cues {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 7pt;
      margin: 9pt 0 2pt;
      font-family: var(--font-sans);
    }}
    .evidence-cues article {{
      min-height: 44pt;
      padding: 6pt 7pt;
      border-top: 1.5pt solid rgba(194,70,124,.52);
      background: rgba(255,255,255,.72);
      box-shadow: inset 0 0 0 0.55pt rgba(18,126,148,.10);
    }}
    .evidence-cues b {{
      display: block;
      color: var(--teal-dark);
      font-size: 8.4pt;
      text-transform: uppercase;
      margin-bottom: 2.5pt;
    }}
    .evidence-cues span {{
      display: block;
      color: #53696d;
      font-size: 7.6pt;
      line-height: 1.28;
    }}
    .evidence-task-strip {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8pt;
      margin: 10pt 0 4pt;
      padding-top: 8pt;
      border-top: 1.15pt solid rgba(18,126,148,.28);
      font-family: var(--font-sans);
    }}
    .evidence-task-strip article {{
      display: grid;
      grid-template-columns: 28pt 1fr;
      column-gap: 7pt;
      align-items: start;
      min-height: 58pt;
      padding: 6.5pt 7pt 5.5pt;
      background:
        linear-gradient(180deg, rgba(250,251,247,.92), rgba(239,247,245,.74));
      box-shadow: inset 0 0 0 0.55pt rgba(18,126,148,.12);
    }}
    .evidence-task-strip b {{
      color: rgba(194,70,124,.78);
      font-size: 7.5pt;
      font-weight: 900;
      text-transform: uppercase;
    }}
    .evidence-task-strip h2 {{
      margin: 0 0 2pt;
      color: var(--teal-dark);
      font-size: 9pt;
      line-height: 1.1;
      font-weight: 850;
      border: 0;
      padding: 0;
    }}
    .evidence-task-strip p {{
      grid-column: 2;
      margin: 0 0 2pt;
      color: #3d5357;
      font-size: 7.55pt;
      line-height: 1.25;
    }}
    .evidence-task-strip .write-line {{
      grid-column: 2;
      height: 10.5pt;
      margin-top: 1pt;
      border-bottom-color: #9fa9a7;
    }}
    .method-card {{
      background: linear-gradient(180deg, #eef7f5, #fbfbf8);
      border-left: 4pt solid var(--teal);
      padding: 12pt 14pt;
      margin: 10pt 0 12pt;
      font-family: var(--font-sans);
      box-shadow: inset 0 0 0 0.6pt rgba(18,126,148,.14);
    }}
    .method-card h2 {{
      border: 0;
      padding: 0;
      margin-bottom: 5pt;
      font-size: 15pt;
    }}
    .method-application {{
      margin: 11pt 0 11pt;
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 8pt;
      font-family: var(--font-sans);
    }}
    .method-application article {{
      min-height: 54pt;
      padding: 7pt 8pt 6pt;
      background:
        linear-gradient(180deg, rgba(255,255,255,.76), rgba(238,248,246,.72));
      border-top: 1.3pt solid rgba(18,126,148,.40);
      box-shadow: inset 0 0 0 0.55pt rgba(18,126,148,.10);
    }}
    .method-application b {{
      display: block;
      color: rgba(194,70,124,.78);
      font-size: 7.5pt;
      font-weight: 900;
      margin-bottom: 3pt;
    }}
    .method-application h3 {{
      margin: 0 0 3pt;
      color: var(--teal-dark);
      font-size: 9.2pt;
      line-height: 1.12;
    }}
    .method-application p {{
      margin: 0;
      font-size: 8.05pt;
      line-height: 1.32;
      color: #435b5f;
    }}
    .diagram-callout {{
      margin: 14pt 0;
      padding: 15pt 16pt;
      border: 1pt solid #bed5d4;
      background:
        linear-gradient(90deg, rgba(19,126,148,.07), transparent 42%),
        #fbfbf8;
      font-family: var(--font-sans);
    }}
    .diagram-callout h2 {{ border: 0; padding: 0; margin-bottom: 8pt; }}
    .diagram-callout div {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 8pt;
      margin-bottom: 8pt;
    }}
    .diagram-callout div span {{
      min-height: 42pt;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      background: white;
      border: 0.8pt solid #d1dfdd;
      color: #29494d;
      padding: 6pt;
      font-size: 9pt;
      line-height: 1.25;
    }}
    .sentence-map-card-stack {{
      display: grid;
      gap: 8pt;
      margin: 10pt 0 12pt;
      font-family: var(--font-sans);
    }}
    .sentence-map-card-stack article {{
      display: grid;
      grid-template-columns: 26pt 1fr;
      gap: 7pt 9pt;
      padding: 8pt 10pt 8pt;
      background:
        linear-gradient(90deg, rgba(235,247,244,.75), rgba(255,255,255,.84) 38%),
        #fbfbf8;
      border-top: 1.1pt solid rgba(18,126,148,.36);
      box-shadow: inset 0 0 0 0.55pt rgba(18,126,148,.10);
      break-inside: avoid;
    }}
    .sentence-map-card-stack article > b {{
      grid-row: 1 / span 3;
      color: var(--activity);
      font-size: 8.2pt;
      font-weight: 900;
      letter-spacing: 0;
    }}
    .sentence-map-card-field {{
      display: grid;
      grid-template-columns: 64pt 1fr;
      gap: 7pt;
      align-items: start;
      border-bottom: 0.55pt solid rgba(18,126,148,.13);
      padding-bottom: 3pt;
    }}
    .sentence-map-card-field:last-child {{
      border-bottom: 0;
      padding-bottom: 0;
    }}
    .sentence-map-card-field span {{
      color: rgba(154,51,112,.86);
      font-size: 7.3pt;
      line-height: 1.15;
      font-weight: 900;
      text-transform: uppercase;
    }}
    .sentence-map-card-field p {{
      margin: 0;
      color: #30484e;
      font-size: 8.15pt;
      line-height: 1.32;
    }}
    .sentence-map-card-sentence p {{
      font-family: var(--font-serif);
      font-size: 8.8pt;
      line-height: 1.36;
      color: #243d42;
    }}
    .guided-mcq-set {{
      display: grid;
      gap: 9pt;
      margin: 12pt 0 14pt;
      font-family: var(--font-sans);
    }}
    .guided-mcq-set article {{
      display: grid;
      grid-template-columns: 28pt 1fr;
      gap: 10pt;
      border-top: 0.75pt solid #d3e1df;
      padding-top: 8pt;
      break-inside: avoid;
    }}
    .guided-mcq-set article > b {{
      color: var(--activity);
      font-size: 9pt;
      font-weight: 900;
    }}
    .guided-mcq-set p {{
      margin-bottom: 5pt;
      font-size: 9.6pt;
      line-height: 1.34;
    }}
    .guided-mcq-set p .exam-stem-slot {{
      display: inline-block;
      min-width: 42pt;
      height: .68em;
      line-height: 0;
      border-bottom: 0.82pt solid #6d7879;
      vertical-align: -0.12em;
      margin: 0 2.4pt;
    }}
    .guided-mcq-set p .exam-stem-slot-short {{ min-width: 34pt; }}
    .guided-mcq-set p .exam-stem-slot-wide {{ min-width: 60pt; }}
    .exam-stem-keep {{
      white-space: nowrap;
    }}
    .guided-mcq-set article div {{
      grid-column: 2;
      display: flex;
      flex-wrap: wrap;
      gap: 5pt;
    }}
    .guided-mcq-set article div span {{
      border: 0.75pt solid #cbd8d7;
      padding: 3.5pt 6pt;
      min-width: 40pt;
      background: rgba(255,255,255,.7);
      font-size: 8.6pt;
    }}
    .diagnostic-ladder {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 7pt;
      margin: 8pt 0 10pt;
      font-family: var(--font-sans);
    }}
    .diagnostic-ladder span {{
      display: grid;
      grid-template-columns: 19pt 1fr;
      gap: 5pt;
      align-items: baseline;
      padding: 5.5pt 7pt;
      background: rgba(234,246,243,.58);
      border-top: 1.3pt solid rgba(18,126,148,.42);
      font-size: 8.2pt;
      line-height: 1.25;
      color: #365357;
    }}
    .diagnostic-ladder b {{
      color: var(--activity);
      font-size: 7.2pt;
      font-weight: 900;
    }}
    .diagnostic-mini-note {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 7pt;
      margin: 10pt 0 0;
      font-family: var(--font-sans);
    }}
    .diagnostic-mini-note article {{
      min-height: 58pt;
      padding: 6.5pt 7pt 6pt;
      background: linear-gradient(180deg, rgba(255,255,255,.82), rgba(239,248,246,.72));
      box-shadow: inset 0 0 0 0.55pt rgba(18,126,148,.14);
    }}
    .diagnostic-mini-note b {{
      color: rgba(194,70,124,.76);
      font-size: 7.4pt;
      font-weight: 900;
    }}
    .diagnostic-mini-note h2 {{
      border: 0;
      padding: 0;
      margin: 2pt 0 3pt;
      font-size: 9.2pt;
      line-height: 1.08;
      font-weight: 820;
      color: var(--teal-dark);
    }}
    .diagnostic-mini-note p {{
      margin: 0;
      font-size: 7.6pt;
      line-height: 1.3;
      color: #53696d;
    }}
    .exam-timing-strip {{
      display: grid;
      grid-template-columns: 54pt 1fr;
      gap: 8pt;
      align-items: center;
      margin: -4pt 0 8pt;
      padding: 6pt 8pt;
      font-family: var(--font-sans);
      background: rgba(246,216,65,.23);
      border-top: 1.2pt solid rgba(225,195,55,.84);
    }}
    .exam-timing-strip b {{
      color: #806d11;
      text-transform: uppercase;
      font-size: 8pt;
      font-weight: 900;
    }}
    .exam-timing-strip span {{
      color: #41565d;
      font-size: 8.4pt;
      line-height: 1.28;
    }}
    .exam-pressure-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 7pt;
      margin: 8pt 0 9pt;
      font-family: var(--font-sans);
    }}
    .exam-pressure-grid article {{
      padding: 6.5pt 7pt 6pt;
      min-height: 58pt;
      background:
        linear-gradient(180deg, rgba(255,255,255,.86), rgba(238,248,246,.75));
      border-left: 1.8pt solid rgba(18,126,148,.48);
      box-shadow: inset 0 0 0 0.55pt rgba(18,126,148,.11);
    }}
    .exam-pressure-grid b {{
      color: rgba(194,70,124,.78);
      font-size: 7.5pt;
      font-weight: 900;
    }}
    .exam-pressure-grid h2 {{
      border: 0;
      padding: 0;
      margin: 1.5pt 0 2pt;
      color: var(--teal-dark);
      font-size: 9.3pt;
      font-weight: 850;
    }}
    .exam-pressure-grid p {{
      margin: 0 0 2pt;
      font-size: 7.7pt;
      line-height: 1.27;
      color: #364f53;
    }}
    .exam-pressure-grid small {{
      display: block;
      color: #66787b;
      font-size: 7.1pt;
      line-height: 1.22;
    }}
    .critical-thinking-strip {{
      display: grid;
      grid-template-columns: 58pt 1fr;
      gap: 10pt;
      align-items: stretch;
      margin-top: 12pt;
      background: rgba(246, 216, 65, .22);
      border-top: 1.3pt solid #e1c337;
      padding: 9pt 11pt;
      font-family: var(--font-sans);
    }}
    .critical-thinking-strip b {{
      color: #806d11;
      text-transform: uppercase;
      font-size: 9pt;
    }}
    .critical-thinking-strip div {{
      display: grid;
      gap: 4pt;
      font-size: 8.8pt;
      color: #3b4c4e;
    }}
    .contents-route {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      column-gap: 17pt;
      row-gap: 0;
      margin-top: 15pt;
      font-family: var(--font-sans);
      border-bottom: 0.75pt solid #c9dad8;
    }}
    .contents-route-page h1 {{ max-width: 374pt; }}
    .contents-route-page .lead {{
      font-size: 10.9pt;
      line-height: 1.55;
      max-width: 444pt;
      padding-bottom: 11pt;
      border-bottom: 0.75pt solid #d6e4e2;
      margin-bottom: 0;
    }}
    .contents-route article {{
      display: grid;
      grid-template-columns: 31pt 1fr;
      gap: 9pt;
      align-items: start;
      padding: 9.5pt 0 9pt;
      border-top: 0.75pt solid #c9dad8;
    }}
    .contents-route article b {{
      color: var(--teal);
      font-size: 14pt;
      line-height: 1;
    }}
    .contents-route h2 {{
      border: 0;
      padding: 0;
      margin: 0 0 3pt;
      font-size: 11.5pt;
    }}
    .contents-route p {{ margin: 0; font-size: 8.7pt; line-height: 1.34; color: #536b6f; }}
    .contents-scope-map {{
      margin-top: 12pt;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 5.5pt 14pt;
      font-family: var(--font-sans);
      border-top: 1.2pt solid rgba(18,126,148,.42);
      padding-top: 9pt;
    }}
    .contents-scope-map article {{
      display: grid;
      grid-template-columns: 82pt 42pt 1fr;
      gap: 6pt;
      align-items: baseline;
      min-height: 30pt;
      padding-bottom: 5pt;
      border-bottom: 0.65pt solid rgba(142,180,180,.46);
    }}
    .contents-scope-map b {{
      color: var(--teal-dark);
      font-size: 8.25pt;
      text-transform: uppercase;
      font-weight: 850;
    }}
    .contents-scope-map article > span {{
      color: var(--activity);
      font-size: 8pt;
      font-weight: 850;
    }}
    .contents-scope-map p {{
      margin: 0;
      font-size: 7.75pt;
      line-height: 1.24;
      color: #354f54;
    }}
    .contents-scope-map small {{
      grid-column: 3;
      margin-top: -2pt;
      font-size: 7.15pt;
      line-height: 1.22;
      color: #6a7b7d;
    }}
    .contents-page-index {{
      margin-top: 10pt;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 5pt 8pt;
      font-family: var(--font-sans);
    }}
    .contents-page-index article {{
      display: grid;
      grid-template-columns: 25pt 1fr;
      gap: 6pt;
      min-height: 30pt;
      padding: 5.5pt 6.5pt;
      background: linear-gradient(90deg, rgba(232,246,243,.58), rgba(255,255,255,.76));
      box-shadow: inset 0 0 0 0.55pt rgba(18,126,148,.12);
    }}
    .contents-page-index b {{
      color: rgba(194,70,124,.78);
      font-size: 8pt;
      font-weight: 900;
    }}
    .contents-page-index strong {{
      display: block;
      color: var(--teal-dark);
      font-size: 8.4pt;
      line-height: 1.1;
    }}
    .contents-page-index span {{
      display: block;
      color: #5f7174;
      font-size: 7.35pt;
      line-height: 1.23;
      margin-top: 1.5pt;
    }}
    .connector-bank {{
      grid-template-columns: repeat(4, minmax(0, 1fr));
      background: rgba(255,255,255,.5);
    }}
    .textbook-table {{
      width: 100%;
      border-collapse: collapse;
      margin: 13pt 0 14pt;
      font-family: var(--font-sans);
      font-size: 9.2pt;
      line-height: 1.24;
      border: 1pt solid var(--table-line);
    }}
    .textbook-table th {{
      background: var(--teal);
      color: white;
      text-align: left;
      text-transform: uppercase;
      font-size: 9.4pt;
      padding: 7pt 8pt;
      border-right: 1pt solid rgba(255,255,255,.35);
    }}
    .textbook-table td {{
      border: 0.7pt solid var(--table-line);
      padding: 6pt 8pt;
      vertical-align: top;
    }}
    .activity-block h3 {{
      font-family: var(--font-sans);
      color: var(--activity);
      font-size: 13.7pt;
      line-height: 1.16;
      margin: 13pt 0 5pt;
    }}
    .activity-block h3 span {{
      text-transform: uppercase;
      font-weight: 850;
      font-size: 10.8pt;
    }}
    .activity-block p {{ margin-bottom: 7pt; }}
    .activity-block ol {{ padding-left: 0; margin-left: 0; list-style: none; }}
    .activity-block li {{ margin: 12pt 0; font-size: 11.2pt; }}
    .activity-block li b {{ font-family: var(--font-sans); margin-right: 7pt; }}
    .word-box {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 7pt 13pt;
      border: 1.3pt solid var(--table-line);
      padding: 10pt 12pt;
      margin: 10pt 0 15pt;
      font-family: var(--font-sans);
      font-size: 9.5pt;
    }}
    .word-box-item {{
      white-space: nowrap;
      min-width: 0;
    }}
    .activity-page .activity-block.large h3 {{ margin-top: 7pt; margin-bottom: 6pt; }}
    .activity-page .activity-block.large p {{
      max-width: 405pt;
      line-height: 1.34;
      margin-bottom: 7pt;
    }}
    .activity-page .word-box {{
      margin: 8pt 0 10pt;
      padding: 8pt 11pt;
      gap: 6pt 12pt;
      font-size: 9.1pt;
      background: rgba(255,255,255,.36);
    }}
    .words-to-know {{
      display: grid;
      grid-template-columns: 92pt 1fr 1fr;
      gap: 8pt 14pt;
      border: 1pt solid #b8cbca;
      border-left: 4pt solid var(--green);
      padding: 8pt 10pt;
      margin: 12pt 0 18pt;
      font-family: var(--font-sans);
      font-size: 9.2pt;
      box-shadow: 0 1pt 3pt rgba(0,0,0,.08);
    }}
    .activity-page .words-to-know {{
      grid-template-columns: 86pt 1fr 1fr;
      margin: 9pt 0 15pt;
      padding: 7pt 9pt;
      font-size: 8.85pt;
      box-shadow: 0 0.6pt 2pt rgba(0,0,0,.06);
    }}
    .words-to-know h4 {{
      grid-column: 1 / -1;
      color: var(--green);
      text-transform: uppercase;
      font-size: 10.6pt;
      margin: 0;
      padding-bottom: 2pt;
      border-bottom: 0.65pt solid rgba(62, 143, 122, .34);
    }}
    .paragraph-practice {{
      position: relative;
      background:
        radial-gradient(circle at 8% 12%, rgba(0,0,0,.025), transparent 18%),
        radial-gradient(circle at 88% 18%, rgba(0,0,0,.018), transparent 19%),
        linear-gradient(180deg, #f9f8f4, var(--texture));
      border: 1pt solid #d4d9d8;
      padding: 31pt 31pt 25pt;
      margin-top: 16pt;
      box-shadow: inset 0 0 18pt rgba(0,0,0,.035);
    }}
    .activity-page .paragraph-practice {{
      margin-top: 13pt;
      padding: 28pt 30pt 22pt;
    }}
    .paragraph-practice .paragraph-label {{
      position: absolute;
      top: 0;
      left: 0;
      transform: translateY(-50%);
      background: var(--green);
      color: white;
      font-family: var(--font-sans);
      font-size: 9.3pt;
      font-weight: 850;
      text-transform: uppercase;
      padding: 5pt 10pt;
    }}
    .paragraph-practice h2 {{
      font-family: var(--font-serif);
      color: var(--ink);
      text-align: center;
      font-size: 17pt;
      font-weight: 700;
      border: none;
      margin-bottom: 14pt;
    }}
    .paragraph-practice p {{ text-align: left; font-size: 12pt; line-height: 1.82; }}
    .blank {{
      display: inline-block;
      min-width: 52pt;
      height: 0;
      line-height: 0;
      border-bottom: 0.9pt solid #8f8f8f;
      vertical-align: -0.82em;
      margin: 0 1.5pt;
      transform: none;
    }}
    .blank-short {{ min-width: 36pt; }}
    .blank-wide {{ min-width: 72pt; }}
    .cloze-keep {{
      white-space: nowrap;
    }}
    .paragraph-practice p .blank {{
      min-width: 44pt;
      border-bottom-width: 0.75pt;
      border-bottom-color: #a4aaa7;
      vertical-align: -0.22em;
      margin: 0 3pt;
    }}
    .paragraph-practice p .blank-short {{ min-width: 34pt; }}
    .paragraph-practice p .blank-wide {{ min-width: 60pt; }}
    .activity-block p .blank,
    .activity-block li .blank,
    .word-box .blank,
    .words-to-know .blank,
    .textbook-table td .blank,
    .review-rules .blank,
    .planner-prompt .blank,
    .editing-checklist label .blank,
    .handbook-page .blank,
    .answer-table .blank {{
      min-width: 54pt;
      border-bottom-width: 0.8pt;
      vertical-align: -0.30em;
      margin: 0 3.2pt;
      position: relative;
      top: -0.4pt;
    }}
    .activity-block p .blank-short,
    .activity-block li .blank-short,
    .word-box .blank-short,
    .words-to-know .blank-short,
    .textbook-table td .blank-short,
    .review-rules .blank-short,
    .planner-prompt .blank-short,
    .editing-checklist label .blank-short,
    .handbook-page .blank-short,
    .answer-table .blank-short {{ min-width: 38pt; }}
    .activity-block p .blank-wide,
    .activity-block li .blank-wide,
    .word-box .blank-wide,
    .words-to-know .blank-wide,
    .textbook-table td .blank-wide,
    .review-rules .blank-wide,
    .planner-prompt .blank-wide,
    .editing-checklist label .blank-wide,
    .handbook-page .blank-wide,
    .answer-table .blank-wide {{ min-width: 68pt; }}
    .word-box .blank {{
      min-width: 31pt;
      margin: 0 2pt;
      vertical-align: -0.26em;
      top: -0.25pt;
    }}
    .word-box .blank-short {{ min-width: 28pt; }}
    .word-box .blank-wide {{ min-width: 38pt; }}
    .question-lines .blank {{ vertical-align: -0.88em; }}
    .question-lines {{ font-size: 11.2pt; padding-left: 18pt; }}
    .question-lines li {{ margin: 13pt 0; }}
    .workbook-record {{
      margin-top: 16pt;
      border-top: 2pt solid var(--teal);
      background:
        linear-gradient(90deg, rgba(230,245,242,.55), rgba(255,255,255,.9) 31%),
        linear-gradient(180deg, #fbfbf8, #f5f3ee);
      box-shadow: inset 0 0 0 0.8pt #d3e2e2;
      padding: 11pt 16pt 10pt;
      font-family: var(--font-sans);
    }}
    .activity-page .workbook-record {{
      margin-top: 15pt;
      padding: 10pt 15pt 9pt;
      background:
        linear-gradient(90deg, rgba(230,245,242,.42), rgba(255,255,255,.93) 28%),
        linear-gradient(180deg, #fbfbf7, #f4f1ea);
    }}
    .record-head {{
      display: flex;
      justify-content: space-between;
      gap: 14pt;
      align-items: baseline;
      margin-bottom: 4pt;
      border-bottom: 0.8pt solid #c8dada;
      padding-bottom: 5pt;
    }}
    .record-head b {{
      color: var(--teal-dark);
      font-size: 10pt;
      text-transform: uppercase;
    }}
    .record-head span {{
      color: #647674;
      font-size: 8.7pt;
    }}
    .workbook-record article {{
      display: grid;
      grid-template-columns: 24pt 1fr;
      gap: 9pt;
      padding: 7.5pt 0 4pt;
      border-bottom: 0.6pt solid rgba(65, 121, 126, .2);
      break-inside: avoid;
    }}
    .workbook-record article:last-child {{ border-bottom: 0; }}
    .record-index {{
      width: 18pt;
      height: 18pt;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      background: rgba(174, 45, 116, .13);
      color: var(--activity);
      font-weight: 850;
      font-size: 8.4pt;
      margin-top: 1pt;
    }}
    .record-prompt {{
      margin: 0 0 4pt;
      font-size: 10pt;
      line-height: 1.42;
      color: #2b4042;
      font-weight: 560;
    }}
    .record-prompt .blank {{
      min-width: 56pt;
      border-bottom-width: 0.8pt;
      vertical-align: -0.32em;
      margin: 0 4pt;
      position: relative;
      top: -0.8pt;
    }}
    .record-lines .write-line {{
      height: 13.2pt;
      margin-top: 2pt;
      border-bottom-color: #a6adab;
    }}
    .write-line {{
      border-bottom: 0.8pt solid #989898;
      height: 17pt;
      margin-top: 4pt;
      font-family: var(--font-sans);
      font-size: 8.8pt;
      color: var(--muted);
    }}
    .photo-passage-page .activity-block h3 {{
      margin-top: 10pt;
      margin-bottom: 5pt;
    }}
    .photo-passage-page .activity-block p {{
      max-width: 470pt;
      margin-bottom: 6pt;
      line-height: 1.34;
    }}
    .photo-passage-page .workbook-record {{
      margin-top: 10pt;
      padding: 9pt 14pt 8pt;
    }}
    .photo-passage-page .workbook-record article {{
      min-height: 48pt;
      padding: 6pt 0 4pt;
    }}
    .photo-passage-page .record-lines .write-line {{
      height: 11.2pt;
      margin-top: 1.5pt;
    }}
    .photo-passage {{
      margin: 0 0 13pt;
      height: 272pt;
      position: relative;
      overflow: hidden;
    }}
    .photo-passage img {{ width: 100%; height: 100%; object-fit: cover; object-position: center 55%; }}
    .photo-passage figcaption {{
      position: absolute;
      left: 15pt;
      bottom: 13pt;
      color: white;
      font-family: var(--font-sans);
      font-weight: 800;
      width: 62%;
      text-shadow: 0 1pt 4pt rgba(0,0,0,.55);
    }}
    .planner-surface {{
      position: relative;
      margin: 11pt 0 10pt;
      padding: 27pt 19pt 14pt;
      border: 0.75pt solid #cfd9d6;
      background:
        linear-gradient(90deg, rgba(51,123,112,.055), rgba(51,123,112,0) 110pt),
        radial-gradient(circle at 12% 10%, rgba(0,0,0,.02), transparent 18%),
        radial-gradient(circle at 92% 20%, rgba(0,0,0,.015), transparent 20%),
        linear-gradient(180deg, #fbfaf6, var(--texture));
      box-shadow:
        inset 0 0 18pt rgba(0,0,0,.018),
        inset 0 3pt 0 rgba(19, 124, 145, .095),
        0 0.8pt 0 rgba(255,255,255,.7);
    }}
    .planner-surface .paragraph-label {{
      position: absolute;
      top: 0;
      left: 0;
      transform: translateY(-50%);
      background: var(--green);
      color: white;
      font-size: 8.7pt;
      font-weight: 850;
      padding: 5pt 10pt;
      font-family: var(--font-sans);
    }}
    .planner-note {{
      position: absolute;
      top: 7pt;
      right: 13pt;
      display: flex;
      gap: 7pt;
      align-items: baseline;
      font-family: var(--font-sans);
      font-size: 8.1pt;
      color: #55706d;
    }}
    .review-rules {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 7pt;
      margin-top: 7pt;
    }}
    .review-rules span {{
      display: block;
      border-top: 1.45pt solid rgba(18,126,148,.30);
      background: rgba(235,245,243,.74);
      padding: 5pt 8pt 4.6pt;
      min-height: 22pt;
      font-size: 8.45pt;
      line-height: 1.28;
      color: #273f42;
      box-shadow: inset 0 0 0 0.6pt rgba(18,126,148,.08);
    }}
    .planner-note b {{
      color: var(--green);
      text-transform: uppercase;
      letter-spacing: 0;
      font-weight: 900;
    }}
    .planner-rows {{
      width: 100%;
      margin: 0;
      font-family: var(--font-sans);
    }}
    .planner-row {{
      display: grid;
      grid-template-columns: 90pt 1fr;
      gap: 12pt;
      padding: 7.6pt 0 7.2pt;
      border-top: 0.75pt solid rgba(79,134,129,.28);
      break-inside: avoid;
    }}
    .planner-row:first-child {{ border-top: 0; padding-top: 0; }}
    .planner-key {{
      background:
        linear-gradient(180deg, rgba(219,239,234,.92), rgba(231,245,241,.78));
      border-left: 2.1pt solid rgba(50,144,120,.82);
      padding: 7pt 8pt 6.8pt 9pt;
      color: #2f685d;
      min-height: 50pt;
      box-shadow: inset 0 0 0 0.55pt rgba(65,139,130,.10);
    }}
    .planner-key span {{
      display: block;
      color: rgba(47,104,93,.56);
      font-size: 8pt;
      font-weight: 800;
      margin-bottom: 3pt;
    }}
    .planner-key b {{
      display: block;
      font-size: 12.4pt;
      line-height: 1.06;
      font-weight: 900;
      margin-bottom: 3.2pt;
    }}
    .planner-key small {{
      display: block;
      font-size: 7.4pt;
      line-height: 1.22;
      color: #5e736f;
    }}
    .planner-body {{
      padding: 2pt 0 0;
      font-size: 9.5pt;
    }}
    .planner-prompt {{
      margin: 0 0 4.8pt;
      font-weight: 680;
      line-height: 1.3;
      color: #24383b;
    }}
    .planner-row .write-line {{
      height: 12.8pt;
      border-bottom-color: #a4aaa8;
      margin-top: 1.7pt;
    }}
    .route-map-page h1,
    .daily-schedule-page h1,
    .task2-answer-sheet-page h1,
    .task1-visual-planner-page h1,
    .speaking-cue-page h1,
    .reading-evidence-planner-page h1 {{
      margin-bottom: 10pt;
    }}
    .route-map-surface,
    .daily-rhythm-grid,
    .answer-sheet-surface,
    .visual-planner-steps,
    .cue-card-surface,
    .reading-evidence-grid {{
      font-family: var(--font-sans);
      margin: 10pt 0;
      break-inside: avoid;
    }}
    .route-map-surface {{
      display: grid;
      grid-template-columns: 1fr 1fr 1fr 1fr;
      gap: 7pt;
      padding: 11pt 10pt;
      background:
        linear-gradient(180deg, rgba(251,250,246,.95), rgba(240,235,223,.88));
      border-top: 2.4pt solid rgba(47,104,93,.68);
      box-shadow: inset 0 0 0 .6pt rgba(47,104,93,.13);
    }}
    .route-map-surface article {{
      min-height: 110pt;
      padding: 8pt 8pt 7pt;
      background: rgba(255,255,255,.58);
      border-left: 2pt solid rgba(154,51,112,.50);
    }}
    .route-map-surface b,
    .daily-rhythm-grid b,
    .answer-sheet-key b {{
      display: block;
      color: rgba(154,51,112,.82);
      font-size: 8pt;
      font-weight: 900;
      text-transform: uppercase;
    }}
    .route-map-surface h2 {{
      color: var(--teal-dark);
      font-size: 10.5pt;
      line-height: 1.08;
      margin: 4pt 0;
      font-weight: 850;
    }}
    .route-map-surface p,
    .route-map-surface small {{
      display: block;
      color: #3d5153;
      font-size: 7.85pt;
      line-height: 1.28;
    }}
    .milestone-strip {{
      display: grid;
      grid-template-columns: 70pt 1fr;
      gap: 10pt;
      margin: 8pt 0 9pt;
      padding: 7pt 10pt;
      background: linear-gradient(90deg, rgba(236,246,243,.90), rgba(255,255,255,.65));
      border-top: 1.2pt solid rgba(18,126,148,.28);
      font-family: var(--font-sans);
    }}
    .milestone-strip b {{
      color: var(--teal-dark);
      font-size: 8.6pt;
      text-transform: uppercase;
    }}
    .milestone-strip ol {{
      columns: 2;
      margin: 0;
      padding-left: 14pt;
      font-size: 7.8pt;
      line-height: 1.3;
      color: #405557;
    }}
    .daily-rhythm-grid {{
      display: grid;
      grid-template-columns: repeat(7, 1fr);
      gap: 4.5pt;
      padding: 9pt;
      background:
        linear-gradient(180deg, rgba(234,245,242,.84), rgba(251,250,246,.92));
      box-shadow: inset 0 0 0 .6pt rgba(18,126,148,.12);
    }}
    .daily-rhythm-grid article {{
      min-height: 79pt;
      padding: 6pt 5pt;
      background: rgba(255,255,255,.66);
      border-top: 2pt solid rgba(18,126,148,.42);
    }}
    .daily-rhythm-grid h2 {{
      margin: 4pt 0 2pt;
      font-size: 8.3pt;
      line-height: 1.08;
      color: var(--teal-dark);
      font-weight: 850;
    }}
    .daily-rhythm-grid p,
    .daily-rhythm-grid small {{
      display: block;
      margin: 0;
      color: #41565a;
      font-size: 7.2pt;
      line-height: 1.25;
    }}
    .answer-sheet-head {{
      display: grid;
      grid-template-columns: 1fr 180pt;
      gap: 12pt;
      padding: 10pt 12pt;
      margin-bottom: 10pt;
      background: linear-gradient(90deg, rgba(251,250,246,.88), rgba(233,246,243,.72));
      border-left: 3pt solid rgba(194,70,124,.58);
      font-family: var(--font-sans);
    }}
    .answer-sheet-head h3 {{
      margin: 0;
      color: var(--teal-dark);
      font-size: 10.2pt;
      line-height: 1.15;
    }}
    .answer-sheet-head p {{
      margin: 0;
      color: #4f6466;
      font-size: 8.2pt;
      line-height: 1.25;
    }}
    .answer-sheet-head div {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 4pt;
    }}
    .answer-sheet-head div span {{
      border-top: 1pt solid rgba(18,126,148,.30);
      padding-top: 3pt;
      color: #3d5356;
      font-size: 7.5pt;
      line-height: 1.1;
    }}
    .answer-sheet-surface {{
      display: grid;
      gap: 5.5pt;
      padding: 12pt 14pt;
      background:
        linear-gradient(180deg, #fbfaf6, #f1ede4);
      box-shadow: inset 0 0 0 .75pt rgba(93,104,96,.17);
    }}
    .answer-sheet-surface article {{
      display: grid;
      grid-template-columns: 94pt 1fr;
      gap: 13pt;
      align-items: start;
      padding-bottom: 4pt;
      border-bottom: .65pt solid rgba(83,96,91,.20);
    }}
    .answer-sheet-surface article:last-child {{ border-bottom: 0; }}
    .answer-sheet-key small {{
      display: block;
      margin-top: 3pt;
      color: #5b6e6c;
      font-size: 7.4pt;
      line-height: 1.22;
    }}
    .answer-sheet-lines .write-line {{
      height: 12pt;
      margin-top: 1.2pt;
    }}
    .task2-printed-surface {{
      margin: 10pt 0;
      padding: 12pt 13pt;
      font-family: var(--font-sans);
      background:
        linear-gradient(90deg, rgba(255,255,255,.46), rgba(232,246,243,.70) 38%, rgba(251,250,246,.96)),
        linear-gradient(180deg, #fbfaf6, #f0ece3);
      box-shadow:
        inset 0 0 0 .65pt rgba(77,96,91,.15),
        inset 0 3pt 0 rgba(18,126,148,.08);
      break-inside: avoid;
    }}
    .task2-position-ladder {{
      display: grid;
      grid-template-columns: 1fr 1fr 1fr 1fr;
      gap: 6pt;
      padding-bottom: 9pt;
      border-bottom: .75pt solid rgba(69,95,92,.22);
    }}
    .task2-position-ladder article,
    .task2-body-lanes article,
    .task2-view-columns article,
    .task2-bridge-strip article,
    .task2-problem-matrix article,
    .task2-solution-lines article,
    .task2-balance-columns article,
    .task2-decision-strip article {{
      background: rgba(255,255,255,.60);
      box-shadow: inset 0 0 0 .5pt rgba(18,126,148,.09);
    }}
    .task2-position-ladder article {{
      min-height: 68pt;
      padding: 7pt 7pt 5pt;
      border-top: 2pt solid rgba(194,70,124,.44);
    }}
    .task2-body-lanes {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8pt;
      padding-top: 9pt;
    }}
    .task2-body-lanes article,
    .task2-solution-lines article,
    .task2-balance-columns article {{
      min-height: 96pt;
      padding: 8pt 9pt 6pt;
      border-left: 2.2pt solid rgba(18,126,148,.40);
    }}
    .task2-printed-surface b,
    .task2-booklet-surface b {{
      display: block;
      color: rgba(154,51,112,.84);
      font-size: 7.8pt;
      font-weight: 900;
      text-transform: uppercase;
    }}
    .task2-printed-surface p,
    .task2-printed-surface small {{
      display: block;
      margin: 3pt 0 4pt;
      color: #3f5558;
      font-size: 7.8pt;
      line-height: 1.24;
    }}
    .task2-printed-surface .write-line {{
      height: 11.7pt;
      margin-top: 1pt;
      border-bottom-color: #9aa7a5;
    }}
    .task2-view-columns,
    .task2-balance-columns {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 9pt;
    }}
    .task2-view-columns article,
    .task2-balance-columns article {{
      min-height: 122pt;
      padding: 9pt 10pt 7pt;
      border-top: 2pt solid rgba(18,126,148,.42);
    }}
    .task2-bridge-strip,
    .task2-decision-strip {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8pt;
      margin-top: 8pt;
      padding-top: 8pt;
      border-top: .75pt solid rgba(69,95,92,.22);
    }}
    .task2-bridge-strip article,
    .task2-decision-strip article {{
      min-height: 45pt;
      padding: 7pt 8pt 5pt;
      border-left: 2pt solid rgba(194,70,124,.38);
    }}
    .task2-problem-surface {{
      display: grid;
      grid-template-columns: 1fr 152pt;
      gap: 10pt;
    }}
    .task2-problem-matrix {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6pt;
    }}
    .task2-problem-matrix article {{
      min-height: 70pt;
      padding: 7pt 8pt 5pt;
      border-top: 2pt solid rgba(112,111,70,.42);
    }}
    .task2-solution-lines {{
      display: grid;
      gap: 7pt;
    }}
    .task2-balance-surface {{
      position: relative;
    }}
    .task2-balance-surface:before {{
      content: "";
      position: absolute;
      left: 50%;
      top: 13pt;
      bottom: 67pt;
      width: 1pt;
      background: rgba(18,126,148,.18);
    }}
    .task2-booklet-surface {{
      background:
        linear-gradient(90deg, rgba(255,255,255,.58), rgba(251,250,246,.95)),
        repeating-linear-gradient(180deg, rgba(18,126,148,.055) 0, rgba(18,126,148,.055) .6pt, transparent .6pt, transparent 24pt);
    }}
    .visual-planner-steps,
    .reading-evidence-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr 1fr 1fr;
      gap: 7pt;
    }}
    .visual-planner-steps article,
    .reading-evidence-grid article {{
      min-height: 74pt;
      padding: 8pt;
      background: linear-gradient(180deg, rgba(255,255,255,.78), rgba(235,246,243,.70));
      border-top: 2pt solid rgba(18,126,148,.42);
      box-shadow: inset 0 0 0 .5pt rgba(18,126,148,.10);
    }}
    .visual-planner-steps b,
    .reading-evidence-grid b {{
      color: rgba(154,51,112,.78);
      font-size: 8pt;
      text-transform: uppercase;
      font-weight: 900;
    }}
    .visual-planner-steps p,
    .reading-evidence-grid p,
    .reading-evidence-grid span {{
      display: block;
      margin: 4pt 0 0;
      color: #3c5357;
      font-size: 8pt;
      line-height: 1.28;
    }}
    .cue-card-surface {{
      display: grid;
      grid-template-columns: 188pt 1fr;
      gap: 12pt;
      padding: 12pt;
      background:
        radial-gradient(circle at 12% 0, rgba(246,216,65,.18), transparent 26%),
        linear-gradient(180deg, #fbfaf6, #f1ede4);
      box-shadow: inset 0 0 0 .7pt rgba(95,108,98,.16);
    }}
    .cue-card-surface aside {{
      padding: 11pt;
      background: rgba(255,255,255,.72);
      border-left: 3pt solid rgba(194,70,124,.56);
    }}
    .cue-card-surface aside b {{
      color: var(--teal-dark);
      font-size: 9pt;
      text-transform: uppercase;
    }}
    .cue-card-surface aside p {{
      margin: 7pt 0;
      font-size: 10pt;
      line-height: 1.35;
      color: #30484d;
    }}
    .cue-card-surface aside div {{
      display: grid;
      gap: 4pt;
      font-size: 7.8pt;
      color: #51686a;
    }}
    .speaking-ladder {{
      display: grid;
      gap: 7pt;
    }}
    .speaking-ladder article {{
      display: grid;
      grid-template-columns: 52pt 1fr;
      gap: 8pt;
      padding: 8pt 9pt;
      background: rgba(236,246,243,.72);
      border-top: 1pt solid rgba(18,126,148,.26);
    }}
    .speaking-ladder b {{
      color: rgba(154,51,112,.82);
      font-size: 8pt;
      font-weight: 900;
    }}
    .speaking-ladder p {{
      margin: 0;
      color: #3b5357;
      font-size: 8.4pt;
      line-height: 1.28;
    }}
    .editing-checklist {{
      display: grid;
      grid-template-columns: 102pt 1fr;
      column-gap: 17pt;
      border-top: 1pt solid rgba(18,126,148,.22);
      border-bottom: 0;
      background:
        linear-gradient(90deg, rgba(218,236,233,.74), rgba(241,248,247,.88) 112pt, rgba(241,248,247,.64));
      padding: 12pt 14pt 10.5pt;
      margin-top: 10pt;
      box-shadow: inset 0 0 0 0.55pt rgba(18,126,148,.08);
    }}
    .editing-checklist h2 {{
      font-size: 17pt;
      color: var(--teal-dark);
      text-transform: none;
      margin-bottom: 4pt;
      letter-spacing: 0;
      line-height: 1;
      font-weight: 430;
    }}
    .editing-checklist p {{ margin-bottom: 5pt; font-size: 8.9pt; line-height: 1.32; color: #4a6064; }}
    .editing-checklist div {{
      grid-column: 2;
      display: grid;
      grid-template-columns: 1fr 1fr;
      column-gap: 13pt;
    }}
    .editing-checklist label {{
      display: block;
      font-size: 8.7pt;
      line-height: 1.34;
      margin: 1.65pt 0;
      font-family: var(--font-sans);
    }}
    .editing-checklist .check-mark {{
      display: inline-block;
      width: 8pt;
      height: 8pt;
      border: 0.8pt solid #999;
      margin-right: 5pt;
      vertical-align: -1pt;
    }}
    .editing-checklist label .blank {{
      min-width: 28pt;
      margin: 0 1.8pt;
      vertical-align: -0.24em;
      top: -0.2pt;
    }}
    .editing-checklist label .blank-short {{ min-width: 24pt; }}
    .editing-checklist label .blank-wide {{ min-width: 34pt; }}
    .correction-rewrite-page h1 {{
      max-width: 390pt;
    }}
    .rewrite-note {{
      max-width: 420pt;
      margin-bottom: 9pt;
      padding-bottom: 7pt;
      border-bottom: 0.75pt solid rgba(154,51,112,.22);
    }}
    .rewrite-lens {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8pt;
      margin: 7pt 0 10pt;
      font-family: var(--font-sans);
    }}
    .rewrite-lens article {{
      min-height: 46pt;
      padding: 7pt 8pt 6pt;
      background:
        linear-gradient(180deg, rgba(255,255,255,.84), rgba(239,247,245,.72));
      border-top: 1.6pt solid rgba(18,126,148,.45);
      box-shadow: inset 0 0 0 0.55pt rgba(18,126,148,.10);
    }}
    .rewrite-lens b {{
      display: block;
      margin-bottom: 3pt;
      color: rgba(154,51,112,.82);
      font-size: 7.6pt;
      font-weight: 900;
      text-transform: uppercase;
    }}
    .rewrite-lens span {{
      display: block;
      color: #31494d;
      font-size: 8.2pt;
      line-height: 1.3;
    }}
    .correction-rewrite-page .workbook-record {{
      margin-top: 9pt;
      padding-top: 10pt;
      padding-bottom: 8.5pt;
      background:
        linear-gradient(90deg, rgba(230,245,242,.48), rgba(255,255,255,.92) 30%),
        linear-gradient(180deg, #fbfaf6, #f3f0e8);
    }}
    .correction-rewrite-page .workbook-record article {{
      padding: 7pt 0 4.8pt;
    }}
    .rewrite-micro-rules {{
      display: grid;
      grid-template-columns: 72pt 1fr;
      gap: 10pt;
      align-items: start;
      margin-top: 9pt;
      padding: 7pt 9pt;
      font-family: var(--font-sans);
      background:
        linear-gradient(90deg, rgba(246,216,65,.18), rgba(255,255,255,.70));
      border-top: 1pt solid rgba(194,70,124,.28);
      box-shadow: inset 0 0 0 0.55pt rgba(194,70,124,.08);
    }}
    .rewrite-micro-rules > b {{
      color: rgba(154,51,112,.86);
      font-size: 8.2pt;
      line-height: 1.1;
      text-transform: uppercase;
      font-weight: 900;
    }}
    .rewrite-micro-rules div {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 7pt;
    }}
    .rewrite-micro-rules span {{
      display: block;
      padding-left: 6pt;
      border-left: 1.5pt solid rgba(18,126,148,.34);
      color: #3d5357;
      font-size: 7.8pt;
      line-height: 1.27;
    }}
    .final-check-summary {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8pt;
      margin: 3pt 0 8pt;
      font-family: var(--font-sans);
    }}
    .final-check-summary article {{
      display: grid;
      grid-template-columns: 42pt 1fr;
      column-gap: 7pt;
      align-items: baseline;
      min-height: 36pt;
      padding: 6pt 7pt;
      background:
        linear-gradient(90deg, rgba(255,255,255,.70), rgba(235,246,244,.72));
      border-bottom: 1pt solid rgba(18,126,148,.30);
      box-shadow: inset 0 0 0 0.5pt rgba(18,126,148,.08);
    }}
    .final-check-summary b {{
      color: rgba(154,51,112,.80);
      font-size: 7.7pt;
      font-weight: 900;
      text-transform: uppercase;
    }}
    .final-check-summary span {{
      color: #30484e;
      font-size: 8pt;
      line-height: 1.25;
    }}
    .final-check-page .final-check-strip {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8pt;
      margin: 9pt 0 10pt;
      padding: 9pt 10pt;
      background:
        linear-gradient(90deg, rgba(233,246,243,.92), rgba(250,251,247,.72)),
        linear-gradient(180deg, rgba(255,255,255,.38), rgba(226,240,238,.42));
      border-top: 2pt solid var(--teal);
      box-shadow: inset 0 0 0 0.65pt rgba(18,126,148,.12);
    }}
    .final-check-strip article {{
      min-height: 55pt;
      padding: 7pt 8pt 6pt;
      background: rgba(255,255,255,.50);
      border-left: 2pt solid rgba(194,70,124,.52);
      box-shadow: inset 0 0 0 0.55pt rgba(18,126,148,.08);
    }}
    .final-check-strip b {{
      display: block;
      color: rgba(194,70,124,.76);
      font-size: 7.2pt;
      font-weight: 900;
      margin-bottom: 2pt;
    }}
    .final-check-strip h2 {{
      margin: 0 0 3pt;
      color: var(--teal-dark);
      font-size: 10.1pt;
      line-height: 1.05;
      font-weight: 850;
    }}
    .final-check-strip p {{
      margin: 0;
      font-size: 8.15pt;
      line-height: 1.34;
      color: #41565d;
    }}
    .final-check-page .workbook-record {{
      margin-top: 10pt;
      padding-top: 10pt;
      padding-bottom: 9pt;
    }}
    .final-check-page .record-row {{
      min-height: 52pt;
      padding: 8pt 0 7pt;
    }}
    .final-check-page .editing-checklist {{
      margin-top: 10pt;
      grid-template-columns: 120pt 1fr;
      padding: 11pt 13pt 10pt;
    }}
    .final-check-page .editing-checklist h2 {{
      font-size: 15.2pt;
      line-height: 1.05;
    }}
    .listening-replay-page h1,
    .reading-close-page h1,
    .frontmatter-checkpoint-page h1 {{
      margin-bottom: 8pt;
    }}
    .listening-focus,
    .reading-focus {{
      max-width: 360pt;
      margin-bottom: 9pt;
      color: #4d6265;
      font-family: var(--font-sans);
      font-size: 9.5pt;
    }}
    .variant-listening-part-1-replay {{ --listening-accent: #367c91; }}
    .variant-listening-part-2-replay {{ --listening-accent: #706f46; }}
    .variant-listening-part-3-replay {{ --listening-accent: #8d5c7b; }}
    .variant-listening-part-4-replay {{ --listening-accent: #526f88; }}
    .variant-listening-part1-form-ledger {{ --listening-accent: #367c91; }}
    .variant-listening-part2-map-path-surface {{ --listening-accent: #706f46; }}
    .variant-listening-part3-speaker-opinion-matrix {{ --listening-accent: #8d5c7b; }}
    .variant-listening-part4-lecture-note-columns {{ --listening-accent: #526f88; }}
    .listening-replay-map,
    .listening-role-surface,
    .reading-close-grid,
    .reading-paraphrase-pairs,
    .reading-transfer-ticket,
    .frontmatter-check-grid {{
      display: grid;
      gap: 7pt;
      margin: 8pt 0 10pt;
      font-family: var(--font-sans);
      break-inside: avoid;
    }}
    .listening-replay-map {{
      grid-template-columns: 1fr 1fr 1fr 1fr;
      padding: 10pt;
      background:
        linear-gradient(180deg, rgba(229,241,247,.82), rgba(251,250,246,.90));
      border-top: 2.2pt solid color-mix(in srgb, var(--listening-accent, #32677f) 76%, transparent);
      box-shadow: inset 0 0 0 .6pt rgba(50,103,127,.13);
    }}
    .listening-role-surface {{
      padding: 10pt;
      background:
        linear-gradient(180deg, rgba(229,241,247,.82), rgba(251,250,246,.90));
      border-top: 2.2pt solid color-mix(in srgb, var(--listening-accent, #32677f) 76%, transparent);
      box-shadow: inset 0 0 0 .6pt rgba(50,103,127,.13);
    }}
    .listening-form-ledger {{
      grid-template-columns: 1fr 1fr;
    }}
    .listening-form-ledger article {{
      display: grid;
      grid-template-columns: 44pt 1fr;
      gap: 7pt;
      min-height: 48pt;
      padding: 7pt 8pt 5pt;
      background: rgba(255,255,255,.62);
      border-left: 2pt solid color-mix(in srgb, var(--listening-accent, #32677f) 64%, transparent);
    }}
    .listening-form-ledger span {{
      font-size: 8pt;
      line-height: 1.24;
      color: #40565a;
    }}
    .listening-form-ledger .write-line {{
      grid-column: 2;
      height: 11pt;
      margin-top: 1pt;
    }}
    .listening-map-path {{
      grid-template-columns: 1fr 126pt;
      align-items: stretch;
    }}
    .map-path-field {{
      display: grid;
      grid-template-columns: 1fr 1fr 1fr 1fr;
      gap: 6pt;
      position: relative;
    }}
    .map-path-field:before {{
      content: "";
      position: absolute;
      left: 10%;
      right: 10%;
      top: 21pt;
      height: 1.2pt;
      background: color-mix(in srgb, var(--listening-accent, #32677f) 38%, transparent);
    }}
    .map-path-field article,
    .speaker-opinion-matrix article,
    .lecture-note-columns article {{
      min-height: 64pt;
      padding: 7pt 8pt;
      background: rgba(255,255,255,.62);
      box-shadow: inset 0 0 0 .5pt rgba(18,126,148,.10);
      border-left: 2pt solid color-mix(in srgb, var(--listening-accent, #32677f) 58%, transparent);
      position: relative;
    }}
    .listening-map-path aside {{
      padding: 9pt;
      background: rgba(255,255,255,.48);
      border-top: 2pt solid rgba(194,70,124,.36);
      color: #40565a;
      font-size: 8pt;
      line-height: 1.28;
    }}
    .listening-map-path aside b {{
      display: block;
      color: var(--teal-dark);
      font-size: 8.2pt;
      text-transform: uppercase;
      margin-bottom: 5pt;
    }}
    .speaker-opinion-matrix {{
      grid-template-columns: repeat(3, 1fr);
    }}
    .speaker-opinion-matrix article {{
      display: grid;
      grid-template-rows: auto auto 1fr;
      min-height: 82pt;
      border-top: 2pt solid color-mix(in srgb, var(--listening-accent, #32677f) 46%, transparent);
    }}
    .speaker-opinion-matrix span {{
      color: var(--teal-dark);
      font-size: 8.5pt;
      font-weight: 850;
      margin-bottom: 4pt;
    }}
    .lecture-note-columns {{
      grid-template-columns: 1fr 1fr 1fr 1fr;
    }}
    .lecture-note-columns article {{
      min-height: 88pt;
      background:
        linear-gradient(180deg, rgba(255,255,255,.70), rgba(242,247,246,.62));
    }}
    .lecture-note-columns .write-line {{
      height: 10.8pt;
      margin-top: 1pt;
      border-bottom-color: #9fa9a7;
    }}
    .listening-ledger-lower,
    .map-route-notebook,
    .speaker-review-board,
    .lecture-review-sheet {{
      margin-top: 9pt;
      font-family: var(--font-sans);
      break-inside: avoid;
    }}
    .listening-ledger-lower {{
      display: grid;
      grid-template-columns: 1.45fr .95fr;
      gap: 8pt;
      align-items: stretch;
    }}
    .listening-ledger-lower > div,
    .part1-ledger-check,
    .map-route-notebook,
    .speaker-review-board,
    .lecture-review-sheet {{
      background:
        linear-gradient(90deg, rgba(229,244,242,.62), rgba(255,255,255,.82) 45%),
        linear-gradient(180deg, #fbfbf8, #f4f3ee);
      box-shadow: inset 0 0 0 .7pt rgba(55,120,132,.18);
      border-top: 2pt solid color-mix(in srgb, var(--listening-accent, #32677f) 76%, transparent);
    }}
    .listening-ledger-lower h2,
    .map-route-record h2,
    .lecture-cornell h2 {{
      margin: 0 0 6pt;
      color: var(--teal-dark);
      font-size: 10.2pt;
      text-transform: uppercase;
      letter-spacing: 0;
    }}
    .listening-ledger-lower > div {{
      padding: 10pt 12pt 8pt;
    }}
    .part1-ledger-record {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 5pt;
    }}
    .part1-ledger-record article,
    .map-route-steps article,
    .speaker-review-record article,
    .lecture-note-record article {{
      display: grid;
      grid-template-columns: 25pt 1fr;
      column-gap: 8pt;
      padding: 5pt 0 4pt;
      border-bottom: .6pt solid rgba(56,109,116,.20);
    }}
    .part1-ledger-record article:last-child,
    .map-route-steps article:last-child,
    .speaker-review-record article:last-child,
    .lecture-note-record article:last-child {{
      border-bottom: 0;
    }}
    .part1-ledger-record b,
    .map-route-steps b,
    .speaker-review-record b,
    .lecture-note-record b {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 18pt;
      height: 18pt;
      border-radius: 50%;
      background: rgba(194,70,124,.14);
      color: var(--activity);
      font-size: 7.8pt;
      font-weight: 900;
    }}
    .part1-ledger-record p,
    .map-route-steps p,
    .speaker-review-record p,
    .lecture-note-record p {{
      margin: 0 0 2pt;
      color: #243f42;
      font-size: 9.2pt;
      font-weight: 700;
      line-height: 1.22;
    }}
    .part1-ledger-record .write-line,
    .map-route-steps .write-line,
    .speaker-review-record .write-line,
    .lecture-note-record .write-line {{
      grid-column: 2;
      height: 11.5pt;
      margin-top: 0;
      border-bottom-color: #9da9a7;
    }}
    .part1-ledger-check,
    .part1-drill-strip,
    .map-route-check,
    .map-route-drill,
    .speaker-review-check,
    .speaker-review-drill,
    .lecture-note-check,
    .lecture-note-drill {{
      padding: 9pt 10pt;
      font-family: var(--font-sans);
    }}
    .part1-ledger-check h2,
    .part1-drill-strip h2,
    .map-route-check h2,
    .map-route-drill h2,
    .speaker-review-check h2,
    .speaker-review-drill h2,
    .lecture-note-check h2,
    .lecture-note-drill h2 {{
      margin: 0 0 5pt;
      color: var(--teal-dark);
      font-size: 10pt;
      font-weight: 760;
    }}
    .part1-ledger-check p,
    .map-route-check p,
    .speaker-review-check p,
    .lecture-note-check p {{
      margin: 0 0 5pt;
      color: #58706f;
      font-family: var(--font-serif);
      font-size: 8.3pt;
      line-height: 1.3;
    }}
    .part1-ledger-check div,
    .map-route-check div,
    .speaker-review-check div,
    .lecture-note-check div {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 2pt;
    }}
    .part1-ledger-check label,
    .map-route-check label,
    .speaker-review-check label,
    .lecture-note-check label {{
      display: block;
      font-size: 8.2pt;
      line-height: 1.28;
    }}
    .part1-drill-strip {{
      margin-top: 7pt;
      display: grid;
      grid-template-columns: 96pt 1fr;
      gap: 8pt;
      align-items: start;
      background: linear-gradient(90deg, rgba(232,247,245,.78), rgba(255,255,255,.92));
      box-shadow: inset 0 0 0 .7pt rgba(55,120,132,.16);
    }}
    .part1-drill-strip > div,
    .map-route-drill > div,
    .speaker-review-drill > div,
    .lecture-note-drill > div {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8pt;
    }}
    .part1-drill-strip article,
    .map-route-drill article,
    .speaker-review-drill article,
    .lecture-note-drill article {{
      display: grid;
      grid-template-columns: 16pt 1fr;
      gap: 5pt;
      align-items: start;
    }}
    .part1-drill-strip article b,
    .map-route-drill article b,
    .speaker-review-drill article b,
    .lecture-note-drill article b {{
      color: var(--activity);
      font-size: 8pt;
    }}
    .part1-drill-strip article p,
    .map-route-drill article p,
    .speaker-review-drill article p,
    .lecture-note-drill article p {{
      margin: 0;
      font-family: var(--font-serif);
      font-size: 8.4pt;
      color: #3b5557;
    }}
    .part1-drill-strip .write-line,
    .map-route-drill .write-line,
    .speaker-review-drill .write-line,
    .lecture-note-drill .write-line {{ grid-column: 2; }}
    .map-route-notebook {{
      display: grid;
      grid-template-columns: 1.25fr .9fr;
      gap: 9pt;
      padding: 10pt 12pt;
    }}
    .map-route-steps {{
      display: grid;
      grid-template-columns: 1fr;
    }}
    .map-route-notebook aside {{
      display: grid;
      grid-template-rows: auto auto;
      gap: 7pt;
    }}
    .map-route-check,
    .map-route-drill {{
      background: rgba(255,255,255,.58);
      box-shadow: inset 0 0 0 .6pt rgba(55,120,132,.14);
    }}
    .speaker-review-board {{
      display: grid;
      grid-template-columns: 1.15fr .95fr;
      gap: 9pt;
      padding: 10pt 12pt;
    }}
    .speaker-review-record {{
      display: grid;
      gap: 4pt;
    }}
    .speaker-review-side {{
      display: grid;
      grid-template-rows: auto auto;
      gap: 7pt;
    }}
    .speaker-review-check,
    .speaker-review-drill {{
      background:
        linear-gradient(180deg, rgba(255,255,255,.62), rgba(247,242,246,.54));
      box-shadow: inset 0 0 0 .6pt rgba(142,83,122,.14);
    }}
    .lecture-review-sheet {{
      padding: 10pt 12pt 9pt;
    }}
    .lecture-cornell {{
      display: grid;
      grid-template-columns: 88pt 1fr;
      gap: 8pt;
      align-items: start;
    }}
    .lecture-cornell h2 {{
      padding-top: 4pt;
      border-top: 2pt solid rgba(82,111,136,.35);
    }}
    .lecture-note-record {{
      display: grid;
      grid-template-columns: 1fr;
    }}
    .lecture-bottom-row {{
      margin-top: 7pt;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8pt;
    }}
    .lecture-note-check,
    .lecture-note-drill {{
      background: rgba(255,255,255,.58);
      box-shadow: inset 0 0 0 .6pt rgba(82,111,136,.14);
    }}
    .listening-replay-map article,
    .reading-close-grid article,
    .reading-paraphrase-pairs article,
    .reading-transfer-ticket article,
    .frontmatter-check-grid article {{
      min-height: 72pt;
      padding: 7pt 8pt;
      background: rgba(255,255,255,.62);
      box-shadow: inset 0 0 0 .5pt rgba(18,126,148,.10);
    }}
    .listening-replay-map article {{
      border-left: 2pt solid color-mix(in srgb, var(--listening-accent, #32677f) 64%, transparent);
    }}
    .listening-replay-map b,
    .listening-role-surface b,
    .reading-close-grid b,
    .reading-paraphrase-pairs b,
    .reading-transfer-ticket b,
    .frontmatter-check-grid b {{
      display: block;
      color: rgba(154,51,112,.80);
      font-size: 7.5pt;
      font-weight: 900;
      text-transform: uppercase;
      margin-bottom: 3pt;
    }}
    .listening-replay-map h2,
    .listening-role-surface h2,
    .reading-transfer-ticket h2,
    .frontmatter-check-grid h2 {{
      margin: 0 0 3pt;
      color: var(--teal-dark);
      font-size: 9.2pt;
      line-height: 1.08;
      font-weight: 850;
    }}
    .listening-replay-map p,
    .listening-role-surface p,
    .reading-close-grid p,
    .reading-paraphrase-pairs p,
    .reading-transfer-ticket p,
    .frontmatter-check-grid p {{
      margin: 0;
      color: #40565a;
      font-size: 7.75pt;
      line-height: 1.3;
    }}
    .reading-close-grid {{
      grid-template-columns: 1fr 1fr 1fr 1fr;
      padding: 10pt;
      background:
        linear-gradient(90deg, rgba(230,240,225,.78), rgba(251,250,246,.92));
      border-top: 2.2pt solid rgba(95,128,97,.58);
      box-shadow: inset 0 0 0 .6pt rgba(95,128,97,.12);
    }}
    .reading-close-grid article {{
      border-left: 2pt solid rgba(95,128,97,.50);
    }}
    .reading-paraphrase-pairs {{
      grid-template-columns: repeat(3, 1fr);
      padding: 10pt;
      background:
        linear-gradient(90deg, rgba(231,241,226,.80), rgba(251,250,246,.94));
      border-top: 2.2pt solid rgba(95,128,97,.60);
      box-shadow: inset 0 0 0 .6pt rgba(95,128,97,.12);
    }}
    .reading-paraphrase-pairs article {{
      min-height: 95pt;
      border-left: 2pt solid rgba(95,128,97,.48);
    }}
    .reading-paraphrase-pairs span {{
      display: block;
      margin: 4pt 0;
      color: var(--teal-dark);
      font-size: 8pt;
      line-height: 1.25;
      font-weight: 820;
    }}
    .reading-paraphrase-pairs small {{
      display: block;
      margin-top: 4pt;
      color: rgba(154,51,112,.82);
      font-size: 7.4pt;
      line-height: 1.22;
    }}
    .reading-transfer-ticket {{
      grid-template-columns: 1fr 1fr;
      padding: 10pt;
      background:
        linear-gradient(180deg, rgba(251,250,246,.94), rgba(232,246,243,.76));
      border-top: 2.2pt solid rgba(18,126,148,.48);
      box-shadow: inset 0 0 0 .6pt rgba(18,126,148,.10);
    }}
    .reading-transfer-ticket article {{
      min-height: 72pt;
      border-left: 2pt solid rgba(18,126,148,.38);
    }}
    .reading-transfer-ticket .write-line {{
      height: 11.8pt;
      margin-top: 1.2pt;
    }}
    .frontmatter-check-grid {{
      grid-template-columns: repeat(3, 1fr);
      padding: 10pt;
      background:
        linear-gradient(180deg, rgba(251,250,246,.94), rgba(236,246,243,.78));
      border-top: 2pt solid rgba(18,126,148,.42);
      box-shadow: inset 0 0 0 .6pt rgba(18,126,148,.10);
    }}
    .frontmatter-book-learning-contract .frontmatter-check-grid {{
      grid-template-columns: 1fr;
      gap: 5pt;
      background:
        linear-gradient(90deg, rgba(251,250,246,.96), rgba(241,236,220,.90));
      border-top-color: rgba(127,91,46,.45);
    }}
    .frontmatter-book-learning-contract .frontmatter-check-grid article {{
      display: grid;
      grid-template-columns: 52pt 1fr;
      min-height: 38pt;
      align-items: start;
      border-left: 2pt solid rgba(127,91,46,.38);
    }}
    .frontmatter-book-learning-contract .frontmatter-check-grid h2 {{
      font-size: 9.4pt;
      margin: 0 0 2pt;
    }}
    .frontmatter-book-learning-contract .frontmatter-check-grid p {{
      grid-column: 2;
      max-width: 360pt;
    }}
    .frontmatter-learning-data-record .frontmatter-check-grid {{
      grid-template-columns: repeat(3, 1fr);
      background:
        linear-gradient(180deg, rgba(229,241,247,.82), rgba(255,255,255,.72));
      border-top-color: rgba(50,103,127,.50);
    }}
    .frontmatter-learning-data-record .frontmatter-check-grid article {{
      min-height: 58pt;
      border-left: 2pt solid rgba(50,103,127,.38);
    }}
    .frontmatter-learning-data-record .final-check-summary article {{
      background:
        linear-gradient(180deg, rgba(255,255,255,.78), rgba(229,241,247,.58));
      border-bottom-color: rgba(50,103,127,.28);
    }}
    .listening-replay-page .workbook-record,
    .reading-close-page .workbook-record,
    .frontmatter-checkpoint-page .workbook-record {{
      margin-top: 8pt;
      padding-top: 9pt;
      padding-bottom: 8pt;
    }}
    .listening-drill-ticket > div {{
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }}
    .final-action-ticket {{
      margin-top: 9pt;
      padding: 8pt 10pt 8pt;
      background: linear-gradient(90deg, rgba(255,255,255,.58), rgba(238,248,246,.76));
      border-top: 1.4pt solid rgba(18,126,148,.48);
      box-shadow: inset 0 0 0 0.55pt rgba(18,126,148,.11);
    }}
    .final-action-ticket h2 {{
      margin: 0 0 5pt;
      color: var(--teal-dark);
      font-size: 8.5pt;
      text-transform: uppercase;
      letter-spacing: 0;
    }}
    .final-action-ticket > div {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 8pt;
    }}
    .final-action-ticket article {{
      display: grid;
      grid-template-columns: 18pt 1fr;
      column-gap: 6pt;
      align-items: start;
    }}
    .final-action-ticket b {{
      color: rgba(194,70,124,.76);
      font-size: 8pt;
      font-weight: 900;
    }}
    .final-action-ticket p {{
      margin: 0 0 2pt;
      font-size: 8.45pt;
      line-height: 1.28;
      color: #30484e;
    }}
    .final-action-ticket .write-line {{
      grid-column: 2;
      height: 12pt;
      margin-top: 1pt;
      border-bottom-color: #9fa9a7;
    }}
    .cover-photo, .unit-photo {{ position: absolute; inset: 0; overflow: hidden; }}
    .cover-photo img, .unit-photo img {{ width: 100%; height: 100%; object-fit: cover; object-position: center; }}
    .cover-photo:before {{
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(90deg, rgba(0,0,0,.50), rgba(0,0,0,.18) 47%, rgba(0,0,0,.08) 78%);
      z-index: 1;
    }}
    .cover-photo:after, .unit-photo:after {{
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(180deg, rgba(0,0,0,.16), rgba(0,0,0,.04) 48%, rgba(0,0,0,.32));
      z-index: 2;
    }}
    .cover-photo img {{ position: relative; z-index: 0; }}
    .cover-top {{
      position: absolute;
      top: 37pt;
      left: 43pt;
      right: 43pt;
      color: white;
      display: flex;
      align-items: center;
      gap: 9pt;
      font-family: var(--font-sans);
      font-weight: 800;
      font-size: 9.3pt;
      text-transform: uppercase;
      z-index: 3;
    }}
    .series-box {{ width: 24pt; height: 34pt; border: 3pt solid #f2d000; display: inline-block; }}
    .cover-title {{
      position: absolute;
      color: white;
      text-shadow: 0 2pt 8pt rgba(0,0,0,.35);
      z-index: 3;
    }}
    .cover-title.title-stack {{
      left: 143pt;
      top: 178pt;
      width: 310pt;
    }}
    .cover-title.title-single {{
      left: 48pt;
      top: 205pt;
      width: 514pt;
    }}
    .cover-title h1 {{
      margin: 0;
      font-weight: 900;
      letter-spacing: 0;
    }}
    .cover-title.title-stack h1 {{
      font-family: var(--font-display);
      font-size: 74pt;
      line-height: .83;
      text-transform: uppercase;
    }}
    .cover-title.title-single h1 {{
      font-family: var(--font-sans);
      font-size: 46pt;
      line-height: 1;
      white-space: nowrap;
      word-break: keep-all;
      overflow-wrap: normal;
    }}
    .cover-title.title-single h1 span {{ display: inline; }}
    .cover-title.title-single .title-main,
    .cover-title.title-single .title-for {{ font-size: 1em; font-weight: inherit; }}
    .cover-title.title-single .title-for {{ margin-left: 8pt; font-size: 1em; font-weight: inherit; }}
    .cover-subtitle {{
      font-family: var(--font-sans);
      font-size: 13pt;
      margin-top: 12pt;
      font-weight: 700;
    }}
    .cover-subtitle span {{ display: block; }}
    .cover-subtitle-cn {{
      margin-top: 3pt;
      font-family: var(--font-cn);
      font-size: 12.2pt;
      font-weight: 850;
      word-break: keep-all;
      overflow-wrap: normal;
    }}
    .cover-brand {{
      position: absolute;
      right: 39pt;
      bottom: 40pt;
      color: white;
      font-family: var(--font-sans);
      text-align: right;
      font-size: 9.5pt;
      display: grid;
      gap: 2pt;
      padding: 7pt 9pt 6pt 18pt;
      background: linear-gradient(90deg, rgba(10,45,51,0), rgba(10,45,51,.64) 42%, rgba(10,45,51,.82));
      border-right: 2pt solid rgba(242,208,0,.76);
      text-shadow: 0 1pt 2.2pt rgba(0,0,0,.46);
      box-shadow: 0 6pt 20pt rgba(0,0,0,.10);
      z-index: 3;
    }}
    .cover-brand b {{ font-size: 10.5pt; letter-spacing: 0; }}
    .cover-brand span {{ opacity: .86; }}
    .title-page {{
      position: absolute;
      inset: 70pt 68pt 82pt;
      font-family: var(--font-sans);
      text-align: center;
      color: #25708d;
    }}
    .title-page .brand-mark {{
      width: 40pt;
      height: 40pt;
      border: 4pt solid #f2d000;
      margin: 26pt auto 56pt;
    }}
    .title-page h1.title-stack {{
      font-family: var(--font-display);
      font-size: 49pt;
      line-height: .9;
      letter-spacing: 0;
      text-transform: uppercase;
      margin: 0 0 12pt;
    }}
    .title-page h1.title-single {{
      font-family: var(--font-cn);
      font-size: 37pt;
      line-height: 1.05;
      letter-spacing: 0;
      font-weight: 900;
      white-space: nowrap;
      margin: 0 0 12pt;
    }}
    .title-page h1.title-single .title-main,
    .title-page h1.title-single .title-for {{ display: inline; }}
    .title-page h1.title-single .title-for {{ margin-left: 7pt; font-size: 1em; font-weight: inherit; }}
    .title-page p {{ color: var(--muted); font-size: 13pt; }}
    .title-page .title-cn {{
      margin-top: 7pt;
      color: var(--teal-dark);
      font-family: var(--font-cn);
      font-size: 15pt;
      font-weight: 850;
    }}
    .title-rule {{ width: 155pt; height: 1.5pt; background: var(--teal); margin: 28pt auto 23pt; }}
    .title-route {{
      width: 392pt;
      margin: 0 auto 27pt;
      border-top: 1pt solid var(--teal-light);
      border-bottom: 1pt solid var(--teal-light);
      text-align: left;
    }}
    .title-route article {{
      display: grid;
      grid-template-columns: 34pt 84pt 1fr;
      gap: 10pt;
      align-items: baseline;
      padding: 9pt 0;
      border-bottom: 0.7pt solid #d7e6e8;
      color: #2a6f95;
    }}
    .title-route article:last-child {{ border-bottom: none; }}
    .title-route b {{
      color: var(--activity);
      font-size: 9pt;
      font-weight: 900;
    }}
    .title-route span {{
      color: var(--teal-dark);
      font-weight: 850;
      font-size: 10pt;
    }}
    .title-route p {{
      margin: 0;
      color: #585858;
      font-size: 9.2pt;
      line-height: 1.3;
    }}
    .title-page section {{ display: grid; gap: 5pt; color: var(--muted); font-size: 9pt; }}
    .title-page small {{ position: absolute; bottom: 0; left: 0; right: 0; color: #777; }}
    .unit-lockup {{
      position: absolute;
      top: 45pt;
      left: 70pt;
      display: grid;
      grid-template-columns: auto 1pt auto;
      align-items: center;
      gap: 15pt;
      color: white;
      text-shadow: 0 2pt 10pt rgba(0,0,0,.58), 0 0 2pt rgba(0,0,0,.62);
      z-index: 3;
    }}
    .unit-lockup b {{
      font-family: var(--font-sans);
      font-size: 32pt;
      font-weight: 900;
    }}
    .unit-lockup span {{ height: 52pt; background: rgba(255,255,255,.75); width: 1pt; }}
    .unit-lockup h1 {{
      font-family: var(--font-serif);
      font-size: 31pt;
      font-weight: 400;
      margin: 0;
    }}
    .objectives-band {{
      position: absolute;
      left: 0;
      right: 0;
      bottom: 0;
      height: 139pt;
      background: var(--opener-band, var(--rust));
      color: white;
      display: grid;
      grid-template-columns: 170pt 1fr;
      gap: 22pt;
      align-items: center;
      padding: 24pt 80pt 22pt;
      font-family: var(--font-sans);
    }}
    .sheet[data-template="unit-opener"][data-opener-layout="side-panel"] .unit-lockup {{
      top: 78pt;
      left: 52pt;
      width: 262pt;
      grid-template-columns: 1fr;
      gap: 8pt;
      padding: 18pt 20pt 19pt;
      background: linear-gradient(135deg, rgba(0,0,0,.50), rgba(0,0,0,.18));
      box-shadow: inset 0 0 0 .65pt rgba(255,255,255,.20);
    }}
    .sheet[data-template="unit-opener"][data-opener-layout="side-panel"] .unit-lockup span {{
      width: 54pt;
      height: 2pt;
      background: var(--opener-soft, rgba(255,255,255,.76));
    }}
    .sheet[data-template="unit-opener"][data-opener-layout="side-panel"] .unit-lockup h1 {{
      font-size: 29pt;
      line-height: 1.05;
    }}
    .sheet[data-template="unit-opener"][data-opener-layout="side-panel"] .objectives-band {{
      left: auto;
      top: 0;
      right: 0;
      bottom: 0;
      width: 214pt;
      height: auto;
      grid-template-columns: 1fr;
      gap: 16pt;
      align-content: end;
      padding: 70pt 25pt 42pt;
      background:
        linear-gradient(180deg, color-mix(in srgb, var(--opener-band, var(--rust)) 86%, #111), var(--opener-band, var(--rust)));
    }}
    .sheet[data-template="unit-opener"][data-opener-layout="side-panel"] .objectives-list ul {{
      font-size: 9.1pt;
      line-height: 1.36;
    }}
    .sheet[data-template="unit-opener"][data-opener-layout="split-band"] .unit-lockup {{
      top: 54pt;
      left: 72pt;
      right: 80pt;
      grid-template-columns: auto 1pt 1fr;
    }}
    .sheet[data-template="unit-opener"][data-opener-layout="split-band"] .objectives-band {{
      height: 164pt;
      grid-template-columns: 232pt 1fr;
      gap: 24pt;
      padding: 24pt 78pt 22pt;
      background:
        linear-gradient(90deg, color-mix(in srgb, var(--opener-band, var(--rust)) 86%, #111) 0 38%, var(--opener-band, var(--rust)) 38% 100%);
    }}
    .sheet[data-template="unit-opener"][data-opener-layout="split-band"] .objectives-intro {{
      padding-right: 12pt;
      border-right: 1pt solid rgba(255,255,255,.28);
    }}
    .objectives-intro {{
      display: grid;
      gap: 8pt;
      align-content: start;
    }}
    .objectives-band h2 {{
      font-size: 12pt;
      text-transform: uppercase;
      margin: 0;
      padding-top: 0;
    }}
    .opener-prompt {{
      margin: 0;
      color: rgba(255,255,255,.88);
      font-size: 8.2pt;
      line-height: 1.28;
      font-weight: 650;
    }}
    .opener-prompt b {{
      display: block;
      margin-bottom: 3pt;
      color: rgba(255,255,255,.68);
      font-size: 7.1pt;
      line-height: 1;
      text-transform: uppercase;
    }}
    .opener-prompt span {{
      display: block;
    }}
    .objectives-list ul {{ margin: 0; padding-left: 14pt; font-size: 9.8pt; line-height: 1.32; }}
    .folio {{
      position: absolute;
      left: 31pt;
      right: 31pt;
      bottom: 22pt;
      display: flex;
      gap: 8pt;
      align-items: baseline;
      font-family: var(--font-sans);
      font-size: 8pt;
    }}
    .folio b {{ font-weight: 900; }}
    .folio span {{ font-weight: 850; }}
    .section-backmatter {{ background: var(--backmatter); }}
    .handbook-page, .answer-key-page {{
      position: absolute;
      inset: 31pt 67pt 52pt 67pt;
      font-family: var(--font-sans);
    }}
    .handbook-page h1 {{
      text-transform: none;
      letter-spacing: 0;
      line-height: 1.04;
      margin-bottom: 17pt;
    }}
    .handbook-index, .answer-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 8.75pt;
      margin: 5pt 0 11pt;
    }}
    .handbook-meta {{
      display: grid;
      grid-template-columns: 72pt 1fr 128pt;
      border-top: 0.75pt solid rgba(18,126,148,.18);
      border-bottom: 0.75pt solid rgba(18,126,148,.26);
      margin: -1pt 0 12pt;
      font-family: var(--font-sans);
      font-size: 7.8pt;
      color: #4c676d;
    }}
    .handbook-meta span {{
      padding: 4.5pt 7pt 4.2pt 0;
      border-right: 0.7pt solid rgba(18,126,148,.18);
    }}
    .handbook-meta span:first-child {{
      color: var(--teal-dark);
      text-transform: uppercase;
      font-weight: 850;
    }}
    .handbook-meta span:last-child {{
      border-right: 0;
      text-align: right;
      padding-right: 0;
    }}
    .handbook-lead {{
      font-size: 10.25pt;
      line-height: 1.48;
      color: #41565d;
      margin: 0 0 13.5pt;
      max-width: 410pt;
    }}
    .handbook-section {{
      margin-top: 10pt;
    }}
    .handbook-section h2 {{
      font-family: var(--font-sans);
      font-size: 8.2pt;
      text-transform: uppercase;
      letter-spacing: 0;
      color: var(--teal-dark);
      margin: 0 0 5pt;
      padding-top: 4.5pt;
      border-top: 1.15pt solid rgba(18,126,148,.52);
    }}
    .handbook-index th, .answer-table th {{
      text-align: left;
      width: 30%;
      padding: 4.2pt 7pt 4.2pt 0;
      font-weight: 820;
      color: #263f45;
      border-top: 0.7pt solid rgba(70,126,140,.24);
    }}
    .handbook-index td, .answer-table td {{
      padding: 4.2pt 0;
      text-align: left;
      color: var(--ink);
      border-top: 0.7pt solid rgba(70,126,140,.24);
    }}
    .handbook-index tr:nth-child(2n) th,
    .handbook-index tr:nth-child(2n) td {{
      background: rgba(255,255,255,.16);
    }}
    .handbook-index th span {{
      display: inline-block;
      width: 15pt;
      margin-right: 6pt;
      color: rgba(18,126,148,.62);
      font-size: 7.4pt;
      font-weight: 850;
    }}
    .handbook-rules {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 7pt;
      margin: 5pt 0 11pt;
    }}
    .handbook-rules article {{
      border-top: 2pt solid var(--teal);
      background: rgba(255,255,255,.28);
      padding: 5.5pt 7.5pt 6.5pt;
      min-height: 46pt;
      box-shadow: inset 0 0 0 0.65pt rgba(32,121,143,.17);
    }}
    .handbook-rules b {{
      display: block;
      font-size: 8.45pt;
      color: var(--teal-dark);
      margin-bottom: 3.2pt;
      text-transform: uppercase;
    }}
    .handbook-rules span {{
      display: block;
      font-size: 8.45pt;
      line-height: 1.35;
      color: #263f45;
    }}
    .handbook-rules .blank {{
      min-width: 28pt;
      margin: 0 1.8pt;
      vertical-align: -0.24em;
      top: -0.2pt;
    }}
    .handbook-rules .blank-short {{ min-width: 24pt; }}
    .handbook-rules .blank-wide {{ min-width: 34pt; }}
    .handbook-rhythm-section .textbook-table {{
      margin-top: 5pt;
      font-size: 8.35pt;
    }}
    .handbook-rhythm-section .textbook-table th {{
      padding: 5.5pt 8pt;
      font-size: 8.55pt;
    }}
    .handbook-rhythm-section .textbook-table td {{
      padding: 5.2pt 7pt;
      line-height: 1.34;
    }}
    .answer-key-page p {{
      font-family: var(--font-sans);
      font-size: 9.2pt;
      color: var(--muted);
      line-height: 1.42;
      padding: 6.5pt 0 8pt;
      margin: -4pt 0 7pt;
      border-top: 0.75pt solid rgba(18,126,148,.18);
      border-bottom: 0.75pt solid rgba(18,126,148,.24);
    }}
    .answer-key-page .answer-key-meta {{
      margin-bottom: 8pt;
    }}
    .answer-key-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 9pt 11pt;
      align-items: start;
    }}
    .answer-group {{
      break-inside: avoid;
      background: rgba(255,255,255,.24);
      border-top: 1.8pt solid rgba(18,126,148,.62);
      box-shadow: inset 0 0 0 0.65pt rgba(18,126,148,.13);
    }}
    .answer-group h2 {{
      display: flex;
      align-items: baseline;
      gap: 7pt;
      margin: 0;
      padding: 6.2pt 7pt 5pt;
      color: var(--teal-dark);
      font-size: 9.2pt;
      line-height: 1.1;
      font-weight: 880;
      text-transform: uppercase;
      letter-spacing: 0;
      border-bottom: 0.7pt solid rgba(18,126,148,.18);
    }}
    .answer-group h2 span {{
      color: rgba(194,70,124,.78);
      font-size: 7.2pt;
      font-weight: 900;
    }}
    .answer-group > p {{
      margin: 0;
      padding: 5pt 7pt 4.5pt;
      border: 0;
      color: #4c676d;
      background: rgba(255,255,255,.16);
      font-size: 7.85pt;
      line-height: 1.28;
    }}
    .answer-table {{
      margin: 0;
      background: rgba(255,255,255,.22);
      box-shadow: none;
    }}
    .answer-table th, .answer-table td {{
      border-top: 0.75pt solid rgba(87,126,139,.34);
      vertical-align: top;
      font-size: 8.25pt;
      line-height: 1.26;
      padding: 5pt 7pt;
    }}
    .answer-table tr:first-child th,
    .answer-table tr:first-child td {{
      border-top: 0;
    }}
    .answer-table th {{
      width: 80pt;
      color: #24464c;
      font-weight: 850;
      background: rgba(255,255,255,.16);
    }}
    .answer-main {{
      display: block;
      color: #1f3439;
      font-weight: 620;
    }}
    .answer-table small {{
      display: block;
      margin-top: 2pt;
      color: #5c7176;
      font-size: 7.2pt;
      line-height: 1.25;
    }}
    .answer-table tr:nth-child(2n) th,
    .answer-table tr:nth-child(2n) td {{
      background: rgba(255,255,255,.18);
    }}
    .teacher-margin-note {{
      position: absolute;
      right: 18pt;
      top: 108pt;
      width: 56pt;
      font-family: var(--font-sans);
      color: #355058;
      border-top: 1.3pt solid rgba(194,70,124,.66);
      padding-top: 5pt;
      background: rgba(255,255,255,.34);
    }}
    .teacher-margin-note b {{
      display: block;
      margin-bottom: 3pt;
      color: var(--magenta);
      font-size: 6.9pt;
      font-weight: 900;
      line-height: 1.05;
      text-transform: uppercase;
    }}
    .teacher-margin-note span {{
      display: block;
      font-size: 7.05pt;
      line-height: 1.25;
    }}
    .teacher-answer-strip {{
      position: absolute;
      left: 67pt;
      right: 67pt;
      bottom: 31pt;
      display: grid;
      grid-template-columns: 72pt 1fr;
      gap: 10pt;
      min-height: 30pt;
      padding: 5pt 8pt 5pt;
      font-family: var(--font-sans);
      background: rgba(255,255,255,.42);
      border-top: 1.1pt solid rgba(194,70,124,.44);
      box-shadow: inset 0 0 0 0.7pt rgba(194,70,124,.12);
    }}
    .teacher-answer-strip b {{
      color: var(--magenta);
      font-size: 7pt;
      line-height: 1.1;
      text-transform: uppercase;
    }}
    .teacher-answer-strip div {{
      display: flex;
      flex-wrap: wrap;
      gap: 3pt 7pt;
      align-items: start;
    }}
    .teacher-answer-strip span {{
      font-size: 7.4pt;
      line-height: 1.2;
      color: #263f45;
    }}
    .teacher-guide-page {{
      position: absolute;
      inset: 31pt 58pt 52pt 58pt;
      font-family: var(--font-sans);
    }}
    .teacher-guide-page h1 {{
      margin: 0 0 12pt;
      max-width: 380pt;
      font-size: 27pt;
      line-height: 1.02;
      color: var(--teal-dark);
    }}
    .teacher-guide-page .lead {{
      max-width: 430pt;
      margin: 0 0 11pt;
      padding: 0;
      border: 0;
      color: #41565d;
      font-size: 9.4pt;
      line-height: 1.38;
    }}
    .teacher-guide-meta {{
      grid-template-columns: repeat(4, 1fr);
      margin-bottom: 11pt;
    }}
    .teacher-guide-flow {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 7pt;
      margin-bottom: 10pt;
    }}
    .teacher-guide-flow article,
    .teacher-guide-notes article {{
      background: rgba(255,255,255,.30);
      border-top: 1.4pt solid rgba(18,126,148,.50);
      padding: 6pt 7pt;
      box-shadow: inset 0 0 0 0.65pt rgba(18,126,148,.12);
    }}
    .teacher-guide-flow b,
    .teacher-guide-notes b {{
      display: block;
      color: var(--magenta);
      font-size: 7pt;
      font-weight: 900;
      text-transform: uppercase;
    }}
    .teacher-guide-flow h2,
    .teacher-guide-notes h2,
    .teacher-board-notes h2 {{
      margin: 2pt 0 3pt;
      color: var(--teal-dark);
      font-size: 8.6pt;
      line-height: 1.1;
      text-transform: uppercase;
    }}
    .teacher-guide-flow p,
    .teacher-guide-notes p,
    .teacher-guide-notes small,
    .teacher-board-notes li {{
      margin: 0;
      color: #263f45;
      font-size: 7.6pt;
      line-height: 1.28;
    }}
    .teacher-guide-notes {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 7pt;
      margin-bottom: 10pt;
    }}
    .teacher-board-notes {{
      border-top: 1.2pt solid rgba(18,126,148,.48);
      margin-bottom: 10pt;
      padding-top: 5pt;
    }}
    .teacher-board-notes ul {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 5pt 10pt;
      margin: 0;
      padding-left: 12pt;
    }}
    .teacher-guide-answers {{
      grid-template-columns: repeat(3, 1fr);
      gap: 7pt;
    }}
    .profile-lesson-a4 .body-page {{ inset: 42pt 78pt 62pt 78pt; }}
    .profile-lesson-a4 .cover-title.title-stack h1 {{ font-size: 66pt; }}
    .profile-lesson-a4 .cover-title.title-single {{ top: 232pt; }}
    .profile-lesson-a4 .cover-title.title-single h1 {{ font-size: 44pt; }}
    .profile-lesson-a4 .objectives-band {{ height: 155pt; }}
    .profile-lesson-a4 .photo-passage {{ height: 318pt; }}
    """


def build(profile: str) -> Path:
    book = load_yaml(BOOK)
    tokens = json.loads(TOKENS.read_text(encoding="utf-8"))
    assets_data = json.loads((ROOT / "assets" / "manifest.json").read_text(encoding="utf-8"))
    assets = {item["id"]: item for item in assets_data["assets"]}
    pages = []
    page_no = 0
    for rel_path in book["pages"]:
        meta, body_md = parse_page(ROOT / rel_path)
        if not page_in_profile(meta, profile, book):
            continue
        page_no += 1
        template = meta.get("template")
        renderer = RENDERERS.get(template)
        if not renderer:
            raise ValueError(f"No renderer for template: {template}")
        body = renderer(meta, book, assets)
        if body_md.strip():
            body += f"<div class=\"markdown-body\">{md(body_md)}</div>"
        pages.append(page_shell(page_no, meta, book, body, profile))

    out_path = configured_output_path(book, profile, "html")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    title = str(book["title"])
    css_text = css(book, tokens, profile)
    if str((book.get("qa") or {}).get("output_mode", "")).strip().lower() == "a4-only":
        css_text = css_text.replace("book-trim", "lesson-a4")
    html_doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <style>{css_text}</style>
</head>
<body data-profile="{esc(profile)}">
  <main class="book">
    {''.join(pages)}
  </main>
</body>
</html>
"""
    out_path.write_text(html_doc, encoding="utf-8")
    print(out_path)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="book-trim")
    args = parser.parse_args()
    build(args.profile)


if __name__ == "__main__":
    main()
