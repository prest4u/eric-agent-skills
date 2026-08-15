#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


def load(name: str):
    path = Path(__file__).with_name(name + ".py")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


init_a4 = load("init_a4")
qa = load("qa_typst_a4")


class InitA4Tests(unittest.TestCase):
    def test_creates_fresh_typst_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "lesson.typ"
            self.assertEqual(init_a4.initialize(target), target.resolve())
            self.assertIn('#set page(', target.read_text(encoding="utf-8"))

    def test_refuses_overwrite_and_non_typ_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "lesson.typ"
            target.write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                init_a4.initialize(target)
            with self.assertRaises(ValueError):
                init_a4.initialize(Path(tmp) / "lesson.pdf")


class QaUnitTests(unittest.TestCase):
    def test_visual_gate_requires_core_and_dense_category(self):
        self.assertFalse(qa.visual_gate({"cover", "first-body", "final"}, True)["ok"])
        self.assertTrue(qa.visual_gate({"cover", "first-body", "dense", "final"}, True)["ok"])

    def test_missing_typst_fails_clearly(self):
        with mock.patch.object(qa.shutil, "which", return_value=None):
            with self.assertRaisesRegex(qa.DependencyError, "Typst executable not found"):
                qa.require_dependencies("missing-typst")

    def test_existing_outputs_are_safe(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "lesson.typ"
            source.write_text("hello", encoding="utf-8")
            pdf = root / "lesson.pdf"
            pdf.write_bytes(b"keep")
            with self.assertRaisesRegex(FileExistsError, "refusing to overwrite"):
                qa.validate_paths(source, pdf, root / "pages", overwrite=False)

    def test_render_dir_rejects_unrelated_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / "notes.txt").write_text("keep", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "non-page files"):
                qa.prepare_render_dir(out, overwrite=True)


if __name__ == "__main__":
    unittest.main()
