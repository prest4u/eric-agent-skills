import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "douyin_intake.py"
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
            "https://douyin.com.evil.test/video/1",
            "https://example.com/video/1",
        )
        for url in rejected:
            with self.subTest(url=url), self.assertRaises(ValueError):
                MODULE.validate_page_url(url)

        rejected_media = (
            "http://v11-weba.douyinvod.com/video.mp4",
            "https://douyinvod.com.evil.test/video.mp4",
            "https://example.com/video.mp4",
        )
        for url in rejected_media:
            with self.subTest(url=url), self.assertRaises(ValueError):
                MODULE.validate_media_url(url)


if __name__ == "__main__":
    unittest.main()
