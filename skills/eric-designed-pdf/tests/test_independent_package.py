from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location("validate_skill_gates", SCRIPTS / "validate_skill_gates.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class IndependentPackageTest(unittest.TestCase):
    def test_eric_pdf_adapter_is_optional_when_not_explicitly_configured(self) -> None:
        previous = os.environ.pop("ERIC_PDF_SKILL_DIR", None)
        try:
            with tempfile.TemporaryDirectory() as temp:
                standalone = Path(temp) / "eric-designed-pdf"
                standalone.mkdir()
                adapter, explicitly_configured = MODULE.find_eric_pdf_qa(standalone)
                self.assertIsNone(adapter)
                self.assertFalse(explicitly_configured)
        finally:
            if previous is not None:
                os.environ["ERIC_PDF_SKILL_DIR"] = previous

    def test_invalid_explicit_adapter_is_distinguishable(self) -> None:
        previous = os.environ.get("ERIC_PDF_SKILL_DIR")
        try:
            with tempfile.TemporaryDirectory() as temp:
                os.environ["ERIC_PDF_SKILL_DIR"] = str(Path(temp) / "missing")
                adapter, explicitly_configured = MODULE.find_eric_pdf_qa(Path(temp) / "standalone")
                self.assertIsNone(adapter)
                self.assertTrue(explicitly_configured)
        finally:
            if previous is None:
                os.environ.pop("ERIC_PDF_SKILL_DIR", None)
            else:
                os.environ["ERIC_PDF_SKILL_DIR"] = previous

    def test_public_package_does_not_require_private_regression_fixtures(self) -> None:
        issues, evidence = MODULE.validate_static(SKILL)
        blocking_codes = {row["code"] for row in issues if row["severity"] in MODULE.STRICT}
        self.assertNotIn("VALIDATION_CORPUS_V2_MISSING", blocking_codes)
        self.assertNotIn("GOLDEN_RENDERED_PAGES_TOO_FEW", blocking_codes)
        self.assertNotIn("GOLDEN_V2_RENDERED_PAGES_TOO_FEW", blocking_codes)
        self.assertEqual(evidence["validation_corpus_v2"]["status"], "skipped")
        self.assertEqual(evidence["golden_rendered_pages"]["status"], "skipped")
        self.assertEqual(evidence["golden_rendered_pages_v2"]["status"], "skipped")


if __name__ == "__main__":
    unittest.main()
