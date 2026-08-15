#!/usr/bin/env python3
import base64
import sys
import tempfile
import unittest
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import export_pptx as EXPORT  # noqa: E402
import portable_ooxml as PORTABLE  # noqa: E402
ONE_PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9ZQMcAAAAASUVORK5CYII="
)


class PortableOoxmlTests(unittest.TestCase):
    def test_common_pptd_elements_export_as_editable_ooxml(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "pages").mkdir()
            (root / "media").mkdir()
            (root / "media" / "pixel.png").write_bytes(ONE_PIXEL_PNG)
            (root / "deck.pptd").write_text(
                """version: v2
title: Portable acceptance
size: [960, 540]
theme:
  colors: {primary: \"#2563EB\", accent: \"#F59E0B\"}
pages: [pages/01.page]
""",
                encoding="utf-8",
            )
            (root / "pages" / "01.page").write_text(
                """background: {type: solid, color: \"#F8FAFC\"}
elements:
  - elementId: title
    elementType: text
    bounds: [40, 30, 880, 60]
    content:
      text: '<p><strong>Editable</strong> <span style="color:$primary;font-size:30px">PPTX</span></p>'
  - elementId: card
    elementType: shape
    bounds: [40, 120, 240, 120]
    shapeName: roundRect
    fill: {type: solid, color: \"#FFFFFF\"}
    border: {width: 1, color: \"#CBD5E1\"}
  - elementId: arrow
    elementType: line
    bounds: [300, 175, 100, 1]
    viewBox: [1, 1]
    points: \"0,0 1,1\"
    arrow: [null, arrow]
    border: {width: 2, color: \"$primary\"}
  - elementId: picture
    elementType: image
    bounds: [420, 120, 120, 120]
    src: media/pixel.png
  - elementId: table
    elementType: table
    bounds: [40, 280, 420, 180]
    columnWidths: [0.5, 0.5]
    rowHeights: [0.5, 0.5]
    rows:
      - [{text: Metric, bold: true}, {text: Value, bold: true}]
      - [{text: Quality}, {text: 100}]
  - elementId: chart
    elementType: chart
    bounds: [500, 280, 420, 180]
    title: Scores
    data:
      cols: [label, value]
      rows: [[A, 10], [B, 20]]
    series: [{type: bar}]
""",
                encoding="utf-8",
            )
            output = root / "deck.pptx"
            PORTABLE.export_pptd(root / "deck.pptd", output)
            EXPORT.patch_transitions(output, "fade")
            with zipfile.ZipFile(output) as archive:
                self.assertIsNone(archive.testzip())
                slide = archive.read("ppt/slides/slide1.xml")
                ET.fromstring(slide)
                self.assertIn(b"Editable", slide)
                self.assertIn(b"PPTX", slide)
                self.assertIn(b"<p:pic>", slide)
                self.assertIn(b"<p:sp>", slide)
                self.assertIn(b"<p:cxnSp>", slide)
                self.assertIn(b"<p:fade/>", slide)
                self.assertIn("ppt/media/image1.png", archive.namelist())
                self.assertGreater(slide.count(b"<p:sp>"), 8)

    def test_remote_images_are_rejected_without_overwriting(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "pages").mkdir()
            (root / "deck.pptd").write_text(
                "version: v2\nsize: [960, 540]\npages: [pages/01.page]\n",
                encoding="utf-8",
            )
            (root / "pages" / "01.page").write_text(
                "elements:\n  - {elementId: image, elementType: image, bounds: [0, 0, 10, 10], src: 'https://example.com/a.png'}\n",
                encoding="utf-8",
            )
            output = root / "deck.pptx"
            output.write_bytes(b"preserve")
            staged = root / ".deck.tmp.pptx"
            with self.assertRaisesRegex(PORTABLE.PortableExportError, "must be downloaded"):
                PORTABLE.export_pptd(root / "deck.pptd", staged)
            self.assertEqual(output.read_bytes(), b"preserve")
            self.assertFalse(staged.exists())


if __name__ == "__main__":
    unittest.main()
