#!/usr/bin/env python3
"""Portable PPTD v2 to editable PPTX exporter.

This exporter is deliberately self-contained: it writes standards-based OOXML
with Python's standard library and uses PyYAML only for PPTD parsing. It does
not bundle, download, or execute a proprietary presentation editor.

The portable renderer covers the common authoring surface used by this Skill:
text boxes (including basic rich text), editable preset shapes, lines, local
PNG/JPEG/GIF images, editable table cells, and a conservative editable chart
fallback. Unsupported decoration is omitted instead of becoming executable or
remote content.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
import zipfile
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised by the wrapper's dependency check
    raise SystemExit(
        "PyYAML 6.0.3 is required. Install it explicitly, then retry: "
        f"{sys.executable} -m pip install --user PyYAML==6.0.3"
    ) from exc


EMU_PER_POINT = 12700
NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CONTENT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
IMAGE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
SLIDE_LAYOUT_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout"
SLIDE_MASTER_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster"
SLIDE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"
THEME_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme"
OFFICE_DOC_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
CORE_REL = "http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties"
APP_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties"
PPTX_MAIN = "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"


class PortableExportError(RuntimeError):
    pass


def x(value: Any) -> str:
    return html.escape(str(value), quote=True)


def emu(value: Any) -> int:
    try:
        return max(0, round(float(value) * EMU_PER_POINT))
    except (TypeError, ValueError):
        return 0


def clamp(value: Any, low: float, high: float, default: float) -> float:
    try:
        return min(high, max(low, float(value)))
    except (TypeError, ValueError):
        return default


def normalize_hex(value: Any, colors: Mapping[str, Any], default: str = "000000") -> Tuple[str, int]:
    raw = str(value or "").strip()
    if raw.startswith("$"):
        raw = str(colors.get(raw[1:], ""))
    raw = raw.lstrip("#")
    if re.fullmatch(r"[0-9A-Fa-f]{3}", raw):
        raw = "".join(char * 2 for char in raw)
    if re.fullmatch(r"[0-9A-Fa-f]{8}", raw):
        rgb, alpha = raw[:6], int(raw[6:], 16)
        return rgb.upper(), round(alpha / 255 * 100000)
    if re.fullmatch(r"[0-9A-Fa-f]{6}", raw):
        return raw.upper(), 100000
    return default, 100000


def solid_fill(value: Any, colors: Mapping[str, Any], *, default: Optional[str] = None) -> str:
    if isinstance(value, Mapping):
        fill_type = str(value.get("type") or "solid")
        if fill_type != "solid":
            stops = value.get("stops")
            if isinstance(stops, list) and stops and isinstance(stops[0], Mapping):
                value = stops[0].get("color")
            else:
                value = None
        else:
            value = value.get("color")
    if not value and default is None:
        return "<a:noFill/>"
    rgb, alpha = normalize_hex(value, colors, default or "FFFFFF")
    alpha_xml = "" if alpha >= 100000 else f'<a:alpha val="{alpha}"/>'
    return f'<a:solidFill><a:srgbClr val="{rgb}">{alpha_xml}</a:srgbClr></a:solidFill>'


def line_xml(border: Any, colors: Mapping[str, Any]) -> str:
    if not isinstance(border, Mapping):
        return '<a:ln><a:noFill/></a:ln>'
    width = emu(border.get("width", 1))
    dash = {"dash": "dash", "dot": "sysDot"}.get(str(border.get("style") or "solid"), "solid")
    return (
        f'<a:ln w="{width}">{solid_fill(border.get("color"), colors, default="000000")}'
        f'<a:prstDash val="{dash}"/></a:ln>'
    )


def font_family(value: Any, default: str = "Aptos") -> Tuple[str, str]:
    if isinstance(value, Mapping):
        return str(value.get("latin") or default), str(value.get("ea") or value.get("latin") or default)
    family = str(value or default).split(",", 1)[0].strip().strip('"\'')
    return family or default, family or default


def parse_css(value: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for item in value.split(";"):
        if ":" not in item:
            continue
        key, raw = (part.strip() for part in item.split(":", 1))
        key = key.lower()
        if key == "font-size":
            match = re.search(r"-?\d+(?:\.\d+)?", raw)
            if match:
                result["fontSize"] = float(match.group())
        elif key == "color":
            result["color"] = raw
        elif key == "font-family":
            result["fontFamily"] = raw
        elif key == "font-weight":
            result["bold"] = raw.lower() in {"bold", "bolder", "600", "700", "800", "900"}
        elif key == "font-style":
            result["italic"] = raw.lower() in {"italic", "oblique"}
        elif key == "text-decoration":
            result["underline"] = "underline" in raw.lower()
            result["strike"] = "line-through" in raw.lower()
        elif key == "text-align":
            result["align"] = raw.lower()
        elif key == "margin-top":
            match = re.search(r"-?\d+(?:\.\d+)?", raw)
            if match:
                result["marginTop"] = float(match.group())
    return result


@dataclass
class Run:
    text: str
    style: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Paragraph:
    runs: List[Run] = field(default_factory=list)
    style: Dict[str, Any] = field(default_factory=dict)
    bullet: Optional[str] = None


class RichTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.paragraphs: List[Paragraph] = []
        self.current: Optional[Paragraph] = None
        self.styles: List[Dict[str, Any]] = [{}]
        self.list_stack: List[str] = []

    def ensure_paragraph(self) -> Paragraph:
        if self.current is None:
            self.current = Paragraph()
            self.paragraphs.append(self.current)
        return self.current

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        tag = tag.lower()
        if tag in {"p", "li"}:
            style = parse_css(values.get("style", ""))
            bullet = None
            if tag == "li":
                bullet = "ordered" if self.list_stack and self.list_stack[-1] == "ol" else "bullet"
            self.current = Paragraph(style=style, bullet=bullet)
            self.paragraphs.append(self.current)
        elif tag in {"ul", "ol"}:
            self.list_stack.append(tag)
        elif tag == "br":
            self.ensure_paragraph().runs.append(Run("\n", dict(self.styles[-1])))

        inherited = dict(self.styles[-1])
        inherited.update(parse_css(values.get("style", "")))
        if tag == "strong":
            inherited["bold"] = True
        elif tag == "em":
            inherited["italic"] = True
        elif tag == "u":
            inherited["underline"] = True
        elif tag == "s":
            inherited["strike"] = True
        elif tag == "sup":
            inherited["baseline"] = 30000
        elif tag == "sub":
            inherited["baseline"] = -25000
        elif tag == "a" and values.get("href"):
            inherited["color"] = "#0563C1"
            inherited["underline"] = True
        self.styles.append(inherited)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if len(self.styles) > 1:
            self.styles.pop()
        if tag in {"p", "li"}:
            self.current = None
        elif tag in {"ul", "ol"} and self.list_stack:
            self.list_stack.pop()

    def handle_data(self, data: str) -> None:
        if not data:
            return
        self.ensure_paragraph().runs.append(Run(data, dict(self.styles[-1])))


def rich_text(value: Any) -> List[Paragraph]:
    text = str(value or "")
    if "<" not in text or ">" not in text:
        return [Paragraph(runs=[Run(line)]) for line in text.splitlines() or [""]]
    parser = RichTextParser()
    parser.feed(text)
    return parser.paragraphs or [Paragraph(runs=[Run("")])]


def resolve_text_style(content: Mapping[str, Any], theme: Mapping[str, Any]) -> Dict[str, Any]:
    style: Dict[str, Any] = {}
    reference = content.get("style")
    if isinstance(reference, str) and reference.startswith("$"):
        text_styles = theme.get("textStyles") if isinstance(theme.get("textStyles"), Mapping) else {}
        candidate = text_styles.get(reference[1:])
        if isinstance(candidate, Mapping):
            style.update(candidate)
    for key in (
        "color", "fontSize", "fontFamily", "bold", "italic", "lineHeight",
        "lineHeightPx", "letterSpacing", "marginTop", "backgroundColor",
    ):
        if key in content:
            style[key] = content[key]
    return style


def run_properties(style: Mapping[str, Any], colors: Mapping[str, Any]) -> str:
    size = round(clamp(style.get("fontSize", 18), 1, 400, 18) * 100)
    latin, east_asian = font_family(style.get("fontFamily"))
    attrs = [f'lang="en-US"', f'sz="{size}"']
    if style.get("bold"):
        attrs.append('b="1"')
    if style.get("italic"):
        attrs.append('i="1"')
    if style.get("underline"):
        attrs.append('u="sng"')
    if style.get("strike"):
        attrs.append('strike="sngStrike"')
    if style.get("baseline") is not None:
        attrs.append(f'baseline="{int(style["baseline"])}"')
    return (
        f'<a:rPr {" ".join(attrs)}>{solid_fill(style.get("color"), colors, default="000000")}'
        f'<a:latin typeface="{x(latin)}"/><a:ea typeface="{x(east_asian)}"/>'
        f'<a:cs typeface="{x(latin)}"/></a:rPr>'
    )


def text_body(content: Mapping[str, Any], theme: Mapping[str, Any]) -> str:
    colors = theme.get("colors") if isinstance(theme.get("colors"), Mapping) else {}
    base = resolve_text_style(content, theme)
    align = content.get("align") if isinstance(content.get("align"), list) else ["left", "top"]
    horizontal = str(align[0] if align else "left")
    vertical = str(align[1] if len(align) > 1 else "top")
    align_map = {"left": "l", "center": "ctr", "right": "r", "justify": "just", "distributed": "dist"}
    anchor_map = {"top": "t", "middle": "ctr", "bottom": "b"}
    wrap = "square" if content.get("wrap", True) else "none"
    body_pr = f'<a:bodyPr wrap="{wrap}" anchor="{anchor_map.get(vertical, "t")}" lIns="0" tIns="0" rIns="0" bIns="0"/>'
    paragraphs_xml: List[str] = []
    for paragraph in rich_text(content.get("text")):
        paragraph_style = dict(base)
        paragraph_style.update(paragraph.style)
        paragraph_align = align_map.get(str(paragraph_style.get("align") or horizontal), "l")
        ppr_parts = [f'algn="{paragraph_align}"']
        if paragraph_style.get("marginTop"):
            ppr_parts.append(f'befSpc="{round(float(paragraph_style["marginTop"]) * 100)}"')
        bullet_xml = ""
        if paragraph.bullet == "bullet":
            bullet_xml = '<a:buChar char="•"/>'
        elif paragraph.bullet == "ordered":
            bullet_xml = '<a:buAutoNum type="arabicPeriod"/>'
        runs_xml: List[str] = []
        for run in paragraph.runs or [Run("")]:
            style = dict(paragraph_style)
            style.update(run.style)
            fragments = run.text.split("\n")
            for index, fragment in enumerate(fragments):
                if fragment:
                    preserve = ' xml:space="preserve"' if fragment[:1].isspace() or fragment[-1:].isspace() else ""
                    runs_xml.append(f'<a:r>{run_properties(style, colors)}<a:t{preserve}>{x(fragment)}</a:t></a:r>')
                if index < len(fragments) - 1:
                    runs_xml.append('<a:br/>')
        end_style = run_properties(paragraph_style, colors).replace("<a:rPr", "<a:endParaRPr", 1).replace("</a:rPr>", "</a:endParaRPr>", 1)
        paragraphs_xml.append(f'<a:p><a:pPr {" ".join(ppr_parts)}>{bullet_xml}</a:pPr>{"".join(runs_xml)}{end_style}</a:p>')
    return f'<p:txBody>{body_pr}<a:lstStyle/>{"".join(paragraphs_xml)}</p:txBody>'


def transform(bounds: Sequence[Any], element: Mapping[str, Any]) -> str:
    x0, y0, width, height = (list(bounds) + [0, 0, 0, 0])[:4]
    attrs: List[str] = []
    rotation = clamp(element.get("rotation", 0), -360, 360, 0)
    if rotation:
        attrs.append(f'rot="{round(rotation * 60000)}"')
    flip = element.get("flip") if isinstance(element.get("flip"), list) else []
    if flip and flip[0]:
        attrs.append('flipH="1"')
    if len(flip) > 1 and flip[1]:
        attrs.append('flipV="1"')
    return (
        f'<a:xfrm {" ".join(attrs)}><a:off x="{emu(x0)}" y="{emu(y0)}"/>'
        f'<a:ext cx="{emu(width)}" cy="{emu(height)}"/></a:xfrm>'
    )


PRESET_SHAPES = {
    "rect", "roundRect", "ellipse", "triangle", "diamond", "homePlate", "chevron",
    "donut", "star5", "rightArrow", "wedgeRectCallout", "bracePair", "parallelogram",
    "hexagon", "octagon", "pie", "arc", "leftArrow", "upArrow", "downArrow",
    "leftRightArrow", "upDownArrow", "cloud", "heart", "lightningBolt", "moon", "sun",
}


def shape_xml(element: Mapping[str, Any], shape_id: int, theme: Mapping[str, Any], *, text: Optional[Mapping[str, Any]] = None) -> str:
    colors = theme.get("colors") if isinstance(theme.get("colors"), Mapping) else {}
    name = str(element.get("elementId") or f"Shape {shape_id}")
    preset = str(element.get("shapeName") or "rect")
    if preset not in PRESET_SHAPES:
        preset = "rect"
    txbox = ' txBox="1"' if text is not None and not element.get("shapeName") else ""
    body = text_body(text, theme) if text is not None else ""
    return (
        f'<p:sp><p:nvSpPr><p:cNvPr id="{shape_id}" name="{x(name)}"/>'
        f'<p:cNvSpPr{txbox}/><p:nvPr/></p:nvSpPr><p:spPr>{transform(element.get("bounds") or [], element)}'
        f'<a:prstGeom prst="{x(preset)}"><a:avLst/></a:prstGeom>'
        f'{solid_fill(element.get("fill"), colors)}{line_xml(element.get("border"), colors)}</p:spPr>{body}</p:sp>'
    )


def text_xml(element: Mapping[str, Any], shape_id: int, theme: Mapping[str, Any]) -> str:
    copy = dict(element)
    copy["shapeName"] = ""
    return shape_xml(copy, shape_id, theme, text=element.get("content") or {})


def line_element_xml(element: Mapping[str, Any], shape_id: int, theme: Mapping[str, Any]) -> str:
    colors = theme.get("colors") if isinstance(theme.get("colors"), Mapping) else {}
    name = str(element.get("elementId") or f"Line {shape_id}")
    border = element.get("border") if isinstance(element.get("border"), Mapping) else {"color": "#000000", "width": 1}
    arrow = element.get("arrow") if isinstance(element.get("arrow"), list) else []
    line = line_xml(border, colors)
    if arrow:
        start = '<a:headEnd type="triangle"/>' if arrow[0] else ""
        end = '<a:tailEnd type="triangle"/>' if len(arrow) > 1 and arrow[1] else ""
        line = line.replace("</a:ln>", f"{start}{end}</a:ln>")
    return (
        f'<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="{shape_id}" name="{x(name)}"/>'
        f'<p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr><p:spPr>{transform(element.get("bounds") or [], element)}'
        f'<a:prstGeom prst="line"><a:avLst/></a:prstGeom>{line}</p:spPr></p:cxnSp>'
    )


def image_type(path: Path) -> Tuple[str, str]:
    suffix = path.suffix.lower()
    mapping = {
        ".png": ("png", "image/png"),
        ".jpg": ("jpeg", "image/jpeg"),
        ".jpeg": ("jpeg", "image/jpeg"),
        ".gif": ("gif", "image/gif"),
    }
    if suffix not in mapping:
        raise PortableExportError(f"portable exporter supports local PNG/JPEG/GIF images only: {path}")
    return mapping[suffix]


@dataclass
class MediaPart:
    relationship_id: str
    archive_name: str
    extension: str
    content_type: str
    data: bytes


def image_xml(element: Mapping[str, Any], shape_id: int, rel_id: str) -> str:
    name = str(element.get("elementId") or f"Picture {shape_id}")
    return (
        f'<p:pic><p:nvPicPr><p:cNvPr id="{shape_id}" name="{x(name)}"/>'
        f'<p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
        f'<p:blipFill><a:blip r:embed="{x(rel_id)}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
        f'<p:spPr>{transform(element.get("bounds") or [], element)}'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>'
    )


def merge_style(*values: Any) -> Dict[str, Any]:
    merged: Dict[str, Any] = {}
    for value in values:
        if isinstance(value, Mapping):
            merged.update(value)
    return merged


def table_elements(element: Mapping[str, Any], start_id: int, theme: Mapping[str, Any]) -> Tuple[List[str], int]:
    bounds = list(element.get("bounds") or [0, 0, 0, 0])
    x0, y0, width, height = (bounds + [0, 0, 0, 0])[:4]
    col_widths = element.get("columnWidths") if isinstance(element.get("columnWidths"), list) else []
    row_heights = element.get("rowHeights") if isinstance(element.get("rowHeights"), list) else []
    rows = element.get("rows") if isinstance(element.get("rows"), list) else []
    if not col_widths:
        count = max((len(row) for row in rows if isinstance(row, list)), default=1)
        col_widths = [1 / count] * count
    if not row_heights:
        count = max(1, len(rows))
        row_heights = [1 / count] * count
    col_total = sum(float(item or 0) for item in col_widths) or 1
    row_total = sum(float(item or 0) for item in row_heights) or 1
    col_edges = [float(x0)]
    row_edges = [float(y0)]
    for item in col_widths:
        col_edges.append(col_edges[-1] + float(width) * float(item or 0) / col_total)
    for item in row_heights:
        row_edges.append(row_edges[-1] + float(height) * float(item or 0) / row_total)

    table_style: Dict[str, Any] = {}
    style_ref = element.get("style")
    table_styles = theme.get("tableStyles") if isinstance(theme.get("tableStyles"), Mapping) else {}
    if isinstance(style_ref, str) and style_ref.startswith("$") and isinstance(table_styles.get(style_ref[1:]), Mapping):
        table_style = dict(table_styles[style_ref[1:]])
    elif isinstance(style_ref, Mapping):
        table_style = dict(style_ref)
    baseline = merge_style(table_style.get("cellStyle"), {"fill": element.get("fill")})
    occupied: set[Tuple[int, int]] = set()
    output: List[str] = []
    current_id = start_id
    for row_index, row in enumerate(rows):
        if not isinstance(row, list) or row_index >= len(row_heights):
            continue
        column = 0
        for cell in row:
            while (row_index, column) in occupied:
                column += 1
            if column >= len(col_widths):
                break
            cell = cell if isinstance(cell, Mapping) else {"text": str(cell or "")}
            row_span = max(1, int(cell.get("rowSpan", 1)))
            col_span = max(1, int(cell.get("colSpan", 1)))
            end_row = min(len(row_edges) - 1, row_index + row_span)
            end_col = min(len(col_edges) - 1, column + col_span)
            for rr in range(row_index, end_row):
                for cc in range(column, end_col):
                    if rr != row_index or cc != column:
                        occupied.add((rr, cc))
            category: Dict[str, Any] = {}
            body_styles = table_style.get("bodyStyles")
            if row_index > 0 and isinstance(body_styles, list) and body_styles:
                candidate = body_styles[(row_index - 1) % len(body_styles)]
                if isinstance(candidate, Mapping):
                    category.update(candidate)
            if row_index == 0:
                category.update(table_style.get("firstRowStyle") or {})
            if row_index == len(rows) - 1:
                category.update(table_style.get("lastRowStyle") or {})
            if column == 0:
                category.update(table_style.get("firstColumnStyle") or {})
            if end_col == len(col_widths):
                category.update(table_style.get("lastColumnStyle") or {})
            style = merge_style(baseline, category, cell)
            cell_element = {
                "elementId": f"{element.get('elementId', 'table')}-r{row_index + 1}c{column + 1}",
                "bounds": [col_edges[column], row_edges[row_index], col_edges[end_col] - col_edges[column], row_edges[end_row] - row_edges[row_index]],
                "shapeName": "rect",
                "fill": style.get("fill") or {"type": "solid", "color": "#FFFFFF"},
                "border": style.get("border") if isinstance(style.get("border"), Mapping) else {"width": 1, "color": "#D1D5DB"},
            }
            content = {
                key: style[key]
                for key in ("color", "fontSize", "fontFamily", "bold", "italic", "align", "textStyle")
                if key in style
            }
            if "textStyle" in content:
                content["style"] = content.pop("textStyle")
            content["text"] = cell.get("text", "")
            content.setdefault("align", ["center", "middle"])
            output.append(shape_xml(cell_element, current_id, theme, text=content))
            current_id += 1
            column = end_col
    return output, current_id


def chart_elements(element: Mapping[str, Any], start_id: int, theme: Mapping[str, Any]) -> Tuple[List[str], int]:
    """Render an editable, dependency-free chart fallback from tabular data."""
    bounds = list(element.get("bounds") or [0, 0, 0, 0])
    x0, y0, width, height = (bounds + [0, 0, 0, 0])[:4]
    frame = {
        "elementId": f"{element.get('elementId', 'chart')}-frame",
        "bounds": bounds,
        "shapeName": "rect",
        "fill": element.get("fill") or {"type": "solid", "color": "#FFFFFF"},
        "border": element.get("border") or {"width": 1, "color": "#D1D5DB"},
    }
    output = [shape_xml(frame, start_id, theme)]
    current_id = start_id + 1
    data = element.get("data") if isinstance(element.get("data"), Mapping) else {}
    cols = data.get("cols") if isinstance(data.get("cols"), list) else []
    rows = data.get("rows") if isinstance(data.get("rows"), list) else []
    numeric: List[Tuple[str, float]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, list):
            continue
        label = str(row[0]) if row else f"{index + 1}"
        value = next((float(item) for item in row[1:] if isinstance(item, (int, float))), None)
        if value is not None:
            numeric.append((label, value))
    if numeric:
        max_value = max(abs(value) for _, value in numeric) or 1
        gap = 8.0
        chart_left = float(x0) + float(width) * 0.22
        chart_width = float(width) * 0.70
        row_height = max(8.0, (float(height) - 50 - gap * (len(numeric) + 1)) / len(numeric))
        for index, (label, value) in enumerate(numeric):
            top = float(y0) + 35 + gap + index * (row_height + gap)
            label_element = {
                "elementId": f"chart-label-{index + 1}",
                "bounds": [float(x0) + 8, top, float(width) * 0.20 - 12, row_height],
                "content": {"text": label, "fontSize": 10, "align": ["right", "middle"], "color": "#374151"},
            }
            output.append(text_xml(label_element, current_id, theme))
            current_id += 1
            bar = {
                "elementId": f"chart-value-{index + 1}",
                "bounds": [chart_left, top, chart_width * abs(value) / max_value, row_height],
                "shapeName": "rect",
                "fill": {"type": "solid", "color": "$primary"},
            }
            output.append(shape_xml(bar, current_id, theme))
            current_id += 1
    title = element.get("title")
    if isinstance(title, Mapping):
        title = title.get("text")
    title = title or (cols[0] if cols else "Chart")
    title_element = {
        "elementId": "chart-title",
        "bounds": [float(x0) + 12, float(y0) + 6, float(width) - 24, 24],
        "content": {"text": str(title), "fontSize": 14, "bold": True, "align": ["left", "middle"], "color": "#111827"},
    }
    output.append(text_xml(title_element, current_id, theme))
    return output, current_id + 1


def page_background(page: Mapping[str, Any], theme: Mapping[str, Any]) -> str:
    colors = theme.get("colors") if isinstance(theme.get("colors"), Mapping) else {}
    background = page.get("background")
    if not background:
        background = {"type": "solid", "color": "#FFFFFF"}
    return f'<p:bg><p:bgPr>{solid_fill(background, colors, default="FFFFFF")}<a:effectLst/></p:bgPr></p:bg>'


def slide_xml(page: Mapping[str, Any], theme: Mapping[str, Any], project_root: Path, slide_number: int, media_counter: int) -> Tuple[str, str, List[MediaPart], int]:
    shapes: List[str] = []
    relationships = [f'<Relationship Id="rId1" Type="{SLIDE_LAYOUT_REL}" Target="../slideLayouts/slideLayout1.xml"/>']
    media: List[MediaPart] = []
    shape_id = 2
    rel_index = 2
    for element in page.get("elements") or []:
        if not isinstance(element, Mapping):
            continue
        element_type = str(element.get("elementType") or "")
        if element_type == "text":
            shapes.append(text_xml(element, shape_id, theme))
            shape_id += 1
        elif element_type == "shape":
            shapes.append(shape_xml(element, shape_id, theme))
            shape_id += 1
        elif element_type == "line":
            shapes.append(line_element_xml(element, shape_id, theme))
            shape_id += 1
        elif element_type == "image":
            source = str(element.get("src") or "")
            if source.startswith(("http://", "https://", "data:")):
                raise PortableExportError(
                    f"slide {slide_number}: remote/data images must be downloaded into the PPTD project before portable export: {source[:80]}"
                )
            image_path = (project_root / source).resolve()
            try:
                image_path.relative_to(project_root)
            except ValueError as exc:
                raise PortableExportError(f"slide {slide_number}: image escapes project directory: {source}") from exc
            if not image_path.is_file():
                raise PortableExportError(f"slide {slide_number}: missing image: {source}")
            extension, content_type = image_type(image_path)
            rel_id = f"rId{rel_index}"
            archive_name = f"ppt/media/image{media_counter}.{extension}"
            media.append(MediaPart(rel_id, archive_name, extension, content_type, image_path.read_bytes()))
            relationships.append(f'<Relationship Id="{rel_id}" Type="{IMAGE_REL}" Target="../media/{Path(archive_name).name}"/>')
            shapes.append(image_xml(element, shape_id, rel_id))
            shape_id += 1
            rel_index += 1
            media_counter += 1
        elif element_type == "table":
            output, shape_id = table_elements(element, shape_id, theme)
            shapes.extend(output)
        elif element_type == "chart":
            output, shape_id = chart_elements(element, shape_id, theme)
            shapes.extend(output)
        elif element_type == "icon":
            fallback = {
                "elementId": element.get("elementId") or f"Icon {shape_id}",
                "bounds": element.get("bounds") or [0, 0, 32, 32],
                "content": {
                    "text": str(element.get("iconName") or "icon").split(":")[-1],
                    "fontSize": min(float((element.get("bounds") or [0, 0, 24, 24])[3]), 18),
                    "bold": True,
                    "color": (element.get("fill") or {}).get("color", "#111827") if isinstance(element.get("fill"), Mapping) else "#111827",
                    "align": ["center", "middle"],
                },
            }
            shapes.append(text_xml(fallback, shape_id, theme))
            shape_id += 1

    shape_tree = (
        '<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/>'
        '</p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
        '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
        + "".join(shapes)
        + "</p:spTree>"
    )
    slide = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<p:sld xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}">'
        f'{page_background(page, theme)}<p:cSld>{shape_tree}</p:cSld>'
        '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'
    )
    rels = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="{REL_NS}">{"".join(relationships)}</Relationships>'
    return slide, rels, media, media_counter


def read_mapping(path: Path) -> Dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise PortableExportError(f"cannot read PPTD YAML {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PortableExportError(f"expected YAML mapping: {path}")
    return value


def find_manifest(source: Path) -> Path:
    source = source.resolve()
    if source.is_file() and source.suffix == ".pptd":
        return source
    if not source.is_dir():
        raise PortableExportError(f"PPTD source not found: {source}")
    manifests = sorted(source.glob("*.pptd"))
    if len(manifests) != 1:
        raise PortableExportError(f"expected exactly one .pptd in {source}; found {len(manifests)}")
    return manifests[0]


def content_types(slide_count: int, media: Iterable[MediaPart]) -> str:
    defaults = {
        "rels": "application/vnd.openxmlformats-package.relationships+xml",
        "xml": "application/xml",
    }
    for item in media:
        defaults[item.extension] = item.content_type
    default_xml = "".join(f'<Default Extension="{x(ext)}" ContentType="{x(kind)}"/>' for ext, kind in sorted(defaults.items()))
    overrides = [
        f'<Override PartName="/ppt/presentation.xml" ContentType="{PPTX_MAIN}"/>',
        '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>',
        '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>',
        '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>',
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>',
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>',
        '<Override PartName="/customXml/provenance.xml" ContentType="application/xml"/>',
    ]
    overrides.extend(
        f'<Override PartName="/ppt/slides/slide{index}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for index in range(1, slide_count + 1)
    )
    return f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="{CONTENT_NS}">{default_xml}{"".join(overrides)}</Types>'


def theme_xml(theme: Mapping[str, Any]) -> str:
    colors = theme.get("colors") if isinstance(theme.get("colors"), Mapping) else {}
    palette = [normalize_hex(colors.get(name), colors, default)[0] for name, default in (
        ("primary", "2563EB"), ("accent", "F59E0B"), ("secondary", "10B981"),
        ("text", "1F2937"), ("muted", "6B7280"), ("light", "F3F4F6"),
    )]
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="{NS_A}" name="Eric PPTD Portable Theme"><a:themeElements>
<a:clrScheme name="Eric"><a:dk1><a:sysClr val="windowText" lastClr="000000"/></a:dk1><a:lt1><a:sysClr val="window" lastClr="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="1F2937"/></a:dk2><a:lt2><a:srgbClr val="F3F4F6"/></a:lt2>
<a:accent1><a:srgbClr val="{palette[0]}"/></a:accent1><a:accent2><a:srgbClr val="{palette[1]}"/></a:accent2><a:accent3><a:srgbClr val="{palette[2]}"/></a:accent3><a:accent4><a:srgbClr val="{palette[3]}"/></a:accent4><a:accent5><a:srgbClr val="{palette[4]}"/></a:accent5><a:accent6><a:srgbClr val="{palette[5]}"/></a:accent6><a:hlink><a:srgbClr val="0563C1"/></a:hlink><a:folHlink><a:srgbClr val="954F72"/></a:folHlink></a:clrScheme>
<a:fontScheme name="Eric"><a:majorFont><a:latin typeface="Aptos Display"/><a:ea typeface="Aptos Display"/><a:cs typeface="Aptos Display"/></a:majorFont><a:minorFont><a:latin typeface="Aptos"/><a:ea typeface="Aptos"/><a:cs typeface="Aptos"/></a:minorFont></a:fontScheme>
<a:fmtScheme name="Eric"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln w="12700"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:prstDash val="solid"/></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme>
</a:themeElements><a:objectDefaults/><a:extraClrSchemeLst/></a:theme>'''


SLIDE_MASTER_XML = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMap accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" bg1="lt1" bg2="lt2" folHlink="folHlink" hlink="hlink" tx1="dk1" tx2="dk2"/><p:sldLayoutIdLst><p:sldLayoutId id="1" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle><a:lvl1pPr algn="l"><a:defRPr sz="3200"/></a:lvl1pPr></p:titleStyle><p:bodyStyle><a:lvl1pPr algn="l"><a:defRPr sz="1800"/></a:lvl1pPr></p:bodyStyle><p:otherStyle><a:defPPr><a:defRPr lang="en-US"/></a:defPPr></p:otherStyle></p:txStyles></p:sldMaster>'''

SLIDE_LAYOUT_XML = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}" type="blank" preserve="1"><p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>'''


def export_pptd(source: Path, output: Path) -> Dict[str, Any]:
    manifest_path = find_manifest(source)
    manifest = read_mapping(manifest_path)
    if manifest.get("version") != "v2":
        raise PortableExportError("portable exporter requires PPTD version: v2")
    pages_value = manifest.get("pages")
    if not isinstance(pages_value, list) or not pages_value:
        raise PortableExportError("PPTD manifest.pages must be a non-empty array")
    project_root = manifest_path.parent.resolve()
    pages: List[Dict[str, Any]] = []
    for relative in pages_value:
        page_path = (project_root / str(relative)).resolve()
        try:
            page_path.relative_to(project_root)
        except ValueError as exc:
            raise PortableExportError(f"page escapes project directory: {relative}") from exc
        pages.append(read_mapping(page_path))
    size = manifest.get("size") if isinstance(manifest.get("size"), list) else [960, 540]
    width, height = (size + [960, 540])[:2]
    theme = manifest.get("theme") if isinstance(manifest.get("theme"), Mapping) else {}

    slide_parts: List[Tuple[str, str]] = []
    all_media: List[MediaPart] = []
    media_counter = 1
    for slide_number, page in enumerate(pages, start=1):
        slide, rels, media, media_counter = slide_xml(page, theme, project_root, slide_number, media_counter)
        slide_parts.append((slide, rels))
        all_media.extend(media)

    slide_ids = "".join(f'<p:sldId id="{255 + index}" r:id="rId{index + 1}"/>' for index in range(1, len(pages) + 1))
    presentation = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<p:presentation xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}">'
        f'<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst><p:sldIdLst>{slide_ids}</p:sldIdLst>'
        f'<p:sldSz cx="{emu(width)}" cy="{emu(height)}" type="custom"/><p:notesSz cx="{emu(height)}" cy="{emu(width)}"/>'
        '<p:defaultTextStyle><a:defPPr><a:defRPr lang="en-US"/></a:defPPr></p:defaultTextStyle></p:presentation>'
    )
    presentation_rels = [f'<Relationship Id="rId1" Type="{SLIDE_MASTER_REL}" Target="slideMasters/slideMaster1.xml"/>']
    presentation_rels.extend(
        f'<Relationship Id="rId{index + 1}" Type="{SLIDE_REL}" Target="slides/slide{index}.xml"/>'
        for index in range(1, len(pages) + 1)
    )
    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<Relationships xmlns="{REL_NS}"><Relationship Id="rId1" Type="{OFFICE_DOC_REL}" Target="ppt/presentation.xml"/>'
        f'<Relationship Id="rId2" Type="{CORE_REL}" Target="docProps/core.xml"/><Relationship Id="rId3" Type="{APP_REL}" Target="docProps/app.xml"/></Relationships>'
    )
    title = str(manifest.get("title") or manifest_path.stem)
    core = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>{x(title)}</dc:title><dc:creator>Eric PPT Skill</dc:creator><cp:lastModifiedBy>Eric PPT Skill</cp:lastModifiedBy></cp:coreProperties>'''
    app = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>Eric PPT Skill</Application><PresentationFormat>Custom</PresentationFormat><Slides>{len(pages)}</Slides><Notes>0</Notes><HiddenSlides>0</HiddenSlides><Company></Company><AppVersion>1.0</AppVersion></Properties>'''
    provenance = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><provenance xmlns="urn:eric:pptd:provenance"><producer>Eric PPT Skill</producer><statement>Built by Eric PPT Skill with PPTD</statement><exporter>portable-ooxml</exporter></provenance>'

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types(len(pages), all_media))
        archive.writestr("_rels/.rels", root_rels)
        archive.writestr("docProps/core.xml", core)
        archive.writestr("docProps/app.xml", app)
        archive.writestr("customXml/provenance.xml", provenance)
        archive.writestr("ppt/presentation.xml", presentation)
        archive.writestr(
            "ppt/_rels/presentation.xml.rels",
            f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="{REL_NS}">{"".join(presentation_rels)}</Relationships>',
        )
        archive.writestr("ppt/theme/theme1.xml", theme_xml(theme))
        archive.writestr("ppt/slideMasters/slideMaster1.xml", SLIDE_MASTER_XML)
        archive.writestr(
            "ppt/slideMasters/_rels/slideMaster1.xml.rels",
            f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="{REL_NS}"><Relationship Id="rId1" Type="{SLIDE_LAYOUT_REL}" Target="../slideLayouts/slideLayout1.xml"/><Relationship Id="rId2" Type="{THEME_REL}" Target="../theme/theme1.xml"/></Relationships>',
        )
        archive.writestr("ppt/slideLayouts/slideLayout1.xml", SLIDE_LAYOUT_XML)
        archive.writestr(
            "ppt/slideLayouts/_rels/slideLayout1.xml.rels",
            f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="{REL_NS}"><Relationship Id="rId1" Type="{SLIDE_MASTER_REL}" Target="../slideMasters/slideMaster1.xml"/></Relationships>',
        )
        for index, (slide, rels) in enumerate(slide_parts, start=1):
            archive.writestr(f"ppt/slides/slide{index}.xml", slide)
            archive.writestr(f"ppt/slides/_rels/slide{index}.xml.rels", rels)
        for item in all_media:
            archive.writestr(item.archive_name, item.data)
    return {"output": str(output.resolve()), "slides": len(pages), "media": len(all_media), "exporter": "portable-ooxml"}


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="PPTD manifest or project directory")
    parser.add_argument("-o", "--output", required=True, type=Path, help="PPTX output path")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        result = export_pptd(args.source, args.output)
    except PortableExportError as exc:
        print(f"portable export failed: {exc}", file=sys.stderr)
        return 2
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
