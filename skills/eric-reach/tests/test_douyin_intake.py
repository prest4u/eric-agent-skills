import importlib.util
import unittest
import sys
import tempfile
from unittest.mock import patch
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "douyin_intake.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("douyin_intake", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class DouyinUrlTests(unittest.TestCase):
    def test_accepts_exact_public_page_and_media_hosts(self):
        MODULE.validate_page_url("https://v.douyin.com/example/")
        MODULE.validate_page_url("https://www.douyin.com/video/1234567890123456789")
        MODULE.validate_media_url("https://v11-weba.douyinvod.com/path/video.mp4")

    def test_rejects_lookalike_insecure_and_unrelated_hosts(self):
        rejected = (
            "http://v.douyin.com/example/",
            "https://user:private_password@v.douyin.com/example/",
            "https://douyin.com.evil.test/video/1",
            "https://example.com/video/1",
        )
        for url in rejected:
            with self.subTest(url=url), self.assertRaises(ValueError):
                MODULE.validate_page_url(url)

        rejected_media = (
            "http://v11-weba.douyinvod.com/video.mp4",
            "https://user:private_password@v11-weba.douyinvod.com/video.mp4",
            "https://douyinvod.com.evil.test/video.mp4",
            "https://example.com/video.mp4",
        )
        for url in rejected_media:
            with self.subTest(url=url), self.assertRaises(ValueError):
                MODULE.validate_media_url(url)


class DouyinRedactionTests(unittest.TestCase):
    def test_written_transcript_metadata_redacts_signed_links(self):
        fake = type("Whisper", (), {"transcribe": staticmethod(lambda *a, **k: {"text": "公开内容", "segments": []})})
        with tempfile.TemporaryDirectory() as raw, patch.dict(sys.modules, {"mlx_whisper": fake}):
            folder = Path(raw)
            metadata = {"title": "video token=secret_title_123", "source_url": "https://v.douyin.com/id/?token=secret_source_123", "video_id": "123"}
            MODULE.transcribe(folder / "input.mp4", folder, metadata, folder / "model")
            draft = (folder / "口播整理稿.md").read_text()
            self.assertNotIn("secret_source_123", draft)
            self.assertNotIn("secret_title_123", draft)
            self.assertIn("公开内容", draft)
            self.assertIn("secret_source_123", metadata["source_url"])

    def test_persistence_gate_redacts_urls_and_errors_without_mutation(self):
        data = {"source_url": "https://user:private_password@v.douyin.com/id/?token=private_token_123", "resolved_url": "https://www.douyin.com/video/123?code=private_code_123", "error": "failed https://v11.douyinvod.com/clip.mp4?signature=private_signature_123"}
        clean = MODULE.final_redaction_gate(data)
        for value in ("private_password", "private_token_123", "private_code_123", "private_signature_123"):
            self.assertNotIn(value, str(clean))
        self.assertIn("private_token_123", data["source_url"])


if __name__ == "__main__":
    unittest.main()
