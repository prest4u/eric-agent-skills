#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("qa_eric_pdf.py")
spec = importlib.util.spec_from_file_location("qa_eric_pdf", SCRIPT_PATH)
qa_eric_pdf = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(qa_eric_pdf)


class EricPdfQaGateTests(unittest.TestCase):
    def test_visual_check_gate_requires_core_categories(self):
        result = qa_eric_pdf.manual_visual_review_check({"cover", "first-body", "final"}, require=True)
        self.assertFalse(result["ok"])
        self.assertIn("dense", result["missing_any_group"][0])

        result = qa_eric_pdf.manual_visual_review_check(
            {"cover", "first-body", "dense", "final"},
            require=True,
        )
        self.assertTrue(result["ok"])

    def test_visual_check_parser_accepts_commas_and_spaces(self):
        self.assertEqual(
            qa_eric_pdf.parse_visual_checks(["cover,first-body", "dense final"]),
            {"cover", "first-body", "dense", "final"},
        )

    def test_student_profile_catches_rendered_teacher_leaks(self):
        hits = qa_eric_pdf.semantic_profile_hits("教师解析 本题评分点如下", "student")
        self.assertIn("教师解析", hits)
        self.assertIn("评分点", hits)

    def test_student_profile_allows_student_answer_labels(self):
        hits = qa_eric_pdf.semantic_profile_hits("答案记录表 最终答案区 错因总结", "student")
        self.assertEqual(hits, [])

    def test_missing_source_fails_delivery_leak_gate_by_default(self):
        result = qa_eric_pdf.scan_leaks(None)
        self.assertFalse(result["ok"])
        self.assertIn("source file", result["reason"])

        result = qa_eric_pdf.scan_leaks(None, allow_missing_source=True)
        self.assertTrue(result["ok"])
        self.assertFalse(result["delivery_gate_eligible"])

    def test_allow_missing_source_returns_smoke_status_not_delivery_pass(self):
        with tempfile.TemporaryDirectory(prefix="eric-pdf-test-") as tmp:
            root = Path(tmp)
            pdf_path = root / "sample.pdf"
            doc = qa_eric_pdf.fitz.open()
            page = doc.new_page(width=qa_eric_pdf.A4_WIDTH, height=qa_eric_pdf.A4_HEIGHT)
            page.insert_text((72, 72), "Smoke QA sample")
            doc.set_metadata({"creator": "Typst"})
            doc.save(pdf_path)
            doc.close()

            result = qa_eric_pdf.qa(
                pdf_path,
                source=None,
                out_dir=root / "pages",
                allow_missing_source=True,
            )

            self.assertEqual(result["status"], "smoke-pass")
            self.assertFalse(result["delivery_gate_eligible"])
            self.assertTrue(result["checks"]["leak_scan"]["skipped"])

    def test_prepare_render_dir_refuses_stale_pages_without_overwrite(self):
        with tempfile.TemporaryDirectory(prefix="eric-pdf-test-") as tmp:
            out_dir = Path(tmp) / "pages"
            out_dir.mkdir()
            stale = out_dir / "page-01.png"
            stale.write_text("old", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "already contains page PNGs"):
                qa_eric_pdf.prepare_render_dir(out_dir)

            self.assertTrue(stale.exists())

    def test_prepare_render_dir_rejects_non_render_files_even_with_overwrite(self):
        with tempfile.TemporaryDirectory(prefix="eric-pdf-test-") as tmp:
            out_dir = Path(tmp) / "pages"
            out_dir.mkdir()
            protected = out_dir / "notes.txt"
            protected.write_text("keep", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "non-render files"):
                qa_eric_pdf.prepare_render_dir(out_dir, overwrite_rendered_pages=True)

            self.assertTrue(protected.exists())

    def test_prepare_render_dir_overwrite_only_removes_page_pngs(self):
        with tempfile.TemporaryDirectory(prefix="eric-pdf-test-") as tmp:
            out_dir = Path(tmp) / "pages"
            out_dir.mkdir()
            (out_dir / "page-01.png").write_text("old", encoding="utf-8")

            qa_eric_pdf.prepare_render_dir(out_dir, overwrite_rendered_pages=True)

            self.assertEqual(list(out_dir.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
