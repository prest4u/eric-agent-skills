#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("build_eric_pdf.py")
spec = importlib.util.spec_from_file_location("build_eric_pdf", SCRIPT_PATH)
build_eric_pdf = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(build_eric_pdf)


class EricPdfBuildSafetyTests(unittest.TestCase):
    def test_validate_output_paths_refuses_existing_pdf_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eric-pdf-test-") as tmp:
            root = Path(tmp)
            source = root / "source.md"
            source.write_text("# Title\n", encoding="utf-8")
            output = root / "out.pdf"
            output.write_bytes(b"old")

            with self.assertRaisesRegex(FileExistsError, "refusing to overwrite"):
                build_eric_pdf.validate_output_paths(source, output, overwrite=False)

            self.assertEqual(output.read_bytes(), b"old")

    def test_validate_output_paths_refuses_existing_typ_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eric-pdf-test-") as tmp:
            root = Path(tmp)
            source = root / "source.md"
            source.write_text("# Title\n", encoding="utf-8")
            output = root / "out.pdf"
            typ = root / "out.typ"
            typ.write_text("old", encoding="utf-8")

            with self.assertRaisesRegex(FileExistsError, "refusing to overwrite"):
                build_eric_pdf.validate_output_paths(source, output, overwrite=False)

            self.assertEqual(typ.read_text(encoding="utf-8"), "old")

    def test_validate_output_paths_allows_overwrite_after_flag(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eric-pdf-test-") as tmp:
            root = Path(tmp)
            source = root / "source.md"
            source.write_text("# Title\n", encoding="utf-8")
            output = root / "out.pdf"
            output.write_bytes(b"old")

            typ = build_eric_pdf.validate_output_paths(source, output, overwrite=True)

            self.assertEqual(typ, root / "out.typ")


if __name__ == "__main__":
    unittest.main()
