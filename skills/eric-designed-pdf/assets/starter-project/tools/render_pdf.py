#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
QA = ROOT / "_qa"
SCREENSHOTS = QA / "screenshots"
RENDERED = QA / "rendered-pages"


def load_book() -> dict:
    import yaml

    return yaml.safe_load((ROOT / "book.yaml").read_text(encoding="utf-8"))


def configured_output_path(book: dict, profile: str, kind: str) -> Path:
    spec = book.get("profiles", {}).get(profile, {})
    nested = spec.get("outputs") or {}
    configured = spec.get(f"output_{kind}") or nested.get(kind)
    if configured:
        path = Path(configured)
        return path if path.is_absolute() else ROOT / path
    return OUT / f"textbook-template-sample-{profile}.{kind}"


def render_pdf(profile: str) -> Path:
    book = load_book()
    html_path = configured_output_path(book, profile, "html")
    if not html_path.exists():
        raise FileNotFoundError(f"Missing HTML. Run tools/build.py first: {html_path}")
    QA.mkdir(parents=True, exist_ok=True)
    pdf_path = configured_output_path(book, profile, "pdf")
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        launch_options = {
            "headless": True,
            "timeout": 15000,
            "args": ["--disable-gpu", "--no-first-run", "--no-default-browser-check"],
        }
        browser = p.chromium.launch(**launch_options)
        page = browser.new_page(viewport={"width": 900, "height": 1200}, device_scale_factor=1)
        page.set_default_timeout(15000)
        page.set_default_navigation_timeout(15000)
        page.goto(html_path.resolve().as_uri(), wait_until="load")
        page.emulate_media(media="print")
        overflows = page.eval_on_selector_all(
            ".sheet",
            """sheets => sheets.map(sheet => ({
              page: Number(sheet.dataset.page),
              template: sheet.dataset.template,
              clientHeight: Math.round(sheet.clientHeight),
              scrollHeight: Math.round(sheet.scrollHeight),
              clientWidth: Math.round(sheet.clientWidth),
              scrollWidth: Math.round(sheet.scrollWidth),
              verticalOverflow: Math.max(0, Math.round(sheet.scrollHeight - sheet.clientHeight)),
              horizontalOverflow: Math.max(0, Math.round(sheet.scrollWidth - sheet.clientWidth))
            }))""",
        )
        (QA / f"layout-overflow-{profile}.json").write_text(json.dumps(overflows, ensure_ascii=False, indent=2), encoding="utf-8")
        page.pdf(path=str(pdf_path), print_background=True, prefer_css_page_size=True)
        browser.close()
    print(pdf_path)
    return pdf_path


def render_pages(profile: str, pdf_path: Path) -> None:
    import fitz
    from PIL import Image, ImageDraw

    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    RENDERED.mkdir(parents=True, exist_ok=True)
    for stale in RENDERED.glob(f"{profile}-page-*.png"):
        stale.unlink()
    contact = QA / f"contact-sheet-{profile}.png"
    if contact.exists():
        contact.unlink()
    doc = fitz.open(pdf_path)
    thumbs = []
    for idx, page in enumerate(doc, 1):
        pix = page.get_pixmap(matrix=fitz.Matrix(1.45, 1.45), alpha=False)
        page_path = RENDERED / f"{profile}-page-{idx:03d}.png"
        pix.save(page_path)
        im = Image.open(page_path).convert("RGB")
        im.thumbnail((150, 220), Image.Resampling.LANCZOS)
        cell = Image.new("RGB", (160, 245), "white")
        cell.paste(im, ((160 - im.width) // 2, 6))
        d = ImageDraw.Draw(cell)
        d.text((8, 226), f"p{idx}", fill=(20, 20, 20))
        thumbs.append(cell)

    cols = 5
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 160, rows * 245), (238, 238, 238))
    for i, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((i % cols) * 160, (i // cols) * 245))
    sheet.save(contact, quality=95)
    print(contact)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=["book-trim", "lesson-a4"], default="book-trim")
    args = parser.parse_args()
    pdf_path = render_pdf(args.profile)
    render_pages(args.profile, pdf_path)


if __name__ == "__main__":
    main()
