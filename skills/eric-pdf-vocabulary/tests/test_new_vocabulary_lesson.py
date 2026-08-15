from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "new_vocabulary_lesson.py"
SPEC = importlib.util.spec_from_file_location("new_vocabulary_lesson", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class NewVocabularyLessonTest(unittest.TestCase):
    def test_creates_standalone_source_and_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "lesson"
            target = MODULE.create_project(output, "Vocabulary Learning", ["evidence", "context"])
            text = target.read_text(encoding="utf-8")
            self.assertIn("Vocabulary Learning", text)
            self.assertIn("evidence", text)
            with self.assertRaises(FileExistsError):
                MODULE.create_project(output, "Again", ["word"])

    def test_standalone_source_contains_public_identity(self) -> None:
        source = MODULE.build_source("Anonymous Vocabulary Lesson", ["evidence"])
        self.assertIn("Vocabulary Learning", source)
        self.assertIn("Memory Chain Lesson", source)
        self.assertNotIn("Sample Lesson", source)


if __name__ == "__main__":
    unittest.main()
