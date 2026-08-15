from __future__ import annotations

import importlib.util
import re
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "account_safety_video_intake", ROOT / "scripts" / "video_intake.py"
)
assert SPEC and SPEC.loader
video_intake = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = video_intake
SPEC.loader.exec_module(video_intake)


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def bash_commands(markdown: str) -> list[str]:
    blocks = re.findall(r"```bash\n(.*?)```", markdown, flags=re.DOTALL)
    return [
        line.strip()
        for block in blocks
        for line in block.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


class AccountSafetyContractTests(unittest.TestCase):
    def test_skill_requires_strict_policy_before_login_backed_acquisition(self):
        skill = read("SKILL.md")
        self.assertIn("references/account-safety.md", skill)
        self.assertIn("completely read", skill)
        self.assertIn("account_safety=strict", skill)
        self.assertRegex(skill, r"takes precedence over ordinary\s+fallback and retry")

    def test_policy_locks_serial_single_target_non_evasion_contract(self):
        policy = read("references/account-safety.md")
        compact = " ".join(policy.split())
        for required in (
            "does not promise zero account risk",
            "One link or one exact target",
            "serially",
            "concurrently",
            "No batch acquisition",
            "monitoring",
            "polling",
            "background jobs",
            "scheduled tasks",
            "anti-detection",
            "fingerprint spoofing",
            "random \"humanized\"",
            "switch backend, account, IP address, proxy",
        ):
            with self.subTest(required=required):
                self.assertIn(required, compact)

    def test_policy_risk_signals_are_non_retryable_with_one_local_exception(self):
        policy = read("references/account-safety.md")
        for signal in (
            "CAPTCHA", "429", "412", "access too frequent", "SECURITY_BLOCK",
            "account anomaly", "login challenge", "verification challenge",
        ):
            with self.subTest(signal=signal):
                self.assertIn(signal, policy)
        self.assertIn("Stop immediately and do not retry", policy)
        self.assertIn("confirmed local daemon failure", policy)
        self.assertIn("request was never sent", policy)
        self.assertIn("exactly one retry", policy)

    def test_policy_preserves_evidence_links_and_non_safe_threshold_limit(self):
        policy = read("references/account-safety.md")
        for url in (
            "https://www.bilibili.com/blackboard/user-rule-linux.html?night=1&padding=0",
            "https://security.bilibili.com/static/docs/BILISRC_V1.3.pdf",
            "https://agree.xiaohongshu.com/h5/terms/ZXXY20220331001/-1",
            "https://github.com/jackwener/opencli",
            "https://github.com/jackwener/opencli/blob/main/clis/xiaohongshu/search.js",
            "https://www.thepaper.cn/newsDetail_forward_32741496",
        ):
            with self.subTest(url=url):
                self.assertIn(url, policy)
        compact = " ".join(policy.split())
        self.assertIn("not a platform safe threshold", compact)
        self.assertIn("reduces but cannot eliminate account risk", compact)

    def test_single_video_read_once_is_a_bounded_three_stage_chain(self):
        policy = " ".join(read("references/account-safety.md").split())
        for clause in (
            "one metadata/note read",
            "one subtitle read",
            "one media download only",
            "Do not retry any of those stages",
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, policy)

    def test_social_search_and_comment_examples_are_bounded_to_five(self):
        social = read("references/social.md")
        commands = bash_commands(social)
        bounded = [line for line in commands if re.search(r"\b(search|comments)\b", line)]
        self.assertTrue(bounded)
        for command in bounded:
            with self.subTest(command=command):
                match = re.search(r"(?:--limit|-n)\s+(\d+)", command)
                self.assertIsNotNone(match)
                self.assertLessEqual(int(match.group(1)), 5)
        self.assertIn("only when Eric explicitly requests comments", social)
        self.assertIn("--with-replies false", social)
        self.assertIn("search once → exact read once", social)
        self.assertNotRegex(social, r"(?m)^xhs\s")
        self.assertNotRegex(social, r"(?m)^(?:twitter|bili|rdt)\s")

    def test_social_examples_exclude_ordinary_account_surface_crawling(self):
        commands = [
            command
            for command in bash_commands(read("references/social.md"))
            if not command.startswith("curl ")
        ]
        forbidden = re.compile(
            r"\b(feed|history|saved|liked|profile|user-posts|hot|rank|subreddit|sub|user)\b"
        )
        for command in commands:
            with self.subTest(command=command):
                self.assertIsNone(forbidden.search(command))

    def test_video_exact_link_and_visual_minimization_contract(self):
        video = read("references/video-understanding.md")
        self.assertIn("single exact video link, do not search first", video)
        self.assertIn("Reliable subtitles that satisfy the", video)
        self.assertIn("do not download the picture track", video)
        self.assertIn("strict circuit breaker overrides", video)
        self.assertIn("playlist or batch request is refused", video)
        self.assertIn("one exact video at a time", video)

    def test_login_backed_visual_failure_does_not_retry_media_download(self):
        source = {
            "url": "https://www.bilibili.com/video/BV1strict",
            "platform": "bilibili",
            "id": "BV1strict",
            "title": "demo",
            "author": None,
            "duration": 30.0,
            "published_at": None,
        }
        unavailable = {
            "status": "unavailable", "source_type": None, "language": None,
            "segments": [], "coverage": 0.0, "file": None, "text_file": None,
        }
        with tempfile.TemporaryDirectory() as raw:
            intake = video_intake.VideoIntake(
                {
                    "platform": "bilibili",
                    "url": source["url"],
                    "host": "www.bilibili.com",
                },
                "分析画面",
                "always",
                None,
                Path(raw),
            )
            with mock.patch.object(intake, "acquire_metadata", return_value=source), mock.patch.object(
                intake, "acquire_transcript", return_value=unavailable
            ), mock.patch.object(intake, "download_media", return_value=None) as download:
                packet = intake.execute()
        self.assertFalse(packet["visual"]["performed"])
        download.assert_called_once_with(want_video=True, height=720)

    def test_bilibili_metadata_risk_stops_before_subtitle_and_media(self):
        cases = (
            (429, "HTTP 429 Too Many Requests", "HTTP_429"),
            (1, "CAPTCHA challenge required", "CAPTCHA"),
            (1, "访问频繁，请稍后再试", "ACCESS_TOO_FREQUENT"),
        )
        for status, detail, expected_code in cases:
            with self.subTest(detail=detail), tempfile.TemporaryDirectory() as raw:
                class RiskRunner:
                    def __init__(self):
                        self.calls = []

                    def run(self, argv, **kwargs):
                        self.calls.append(list(argv))
                        raise video_intake.BackendFailure(
                            kwargs["stage"], kwargs["backend"], status, detail
                        )

                runner = RiskRunner()
                intake = video_intake.VideoIntake(
                    {
                        "platform": "bilibili",
                        "url": "https://www.bilibili.com/video/BV1risk",
                        "host": "www.bilibili.com",
                    },
                    "分析画面", "always", None, Path(raw), runner=runner,
                )
                packet = intake.execute()
                self.assertEqual([call[2] for call in runner.calls], ["video"])
                self.assertEqual(intake.access_blocks, {"platform": expected_code})
                self.assertEqual(intake.platform_access_blocked, expected_code)
                self.assertTrue(packet["limitations"][0]["non_retryable"])
                self.assertEqual(packet["limitations"][0]["access_scope"], "platform")

    def test_bilibili_subtitle_risk_stops_before_media(self):
        cases = (
            ("verification challenge required", "VERIFICATION_CHALLENGE"),
            ("login challenge required", "LOGIN_CHALLENGE"),
            ("SECURITY_BLOCK: platform policy refused the request", "SECURITY_BLOCK"),
        )
        for detail, expected_code in cases:
            with self.subTest(detail=detail), tempfile.TemporaryDirectory() as raw:
                class SubtitleRiskRunner:
                    def __init__(self):
                        self.calls = []

                    def run(self, argv, **kwargs):
                        self.calls.append(list(argv))
                        if argv[:3] == ["opencli", "bilibili", "video"]:
                            return '[{"field":"标题","value":"demo"}]'
                        if argv[:3] == ["opencli", "bilibili", "subtitle"]:
                            raise video_intake.BackendFailure(
                                kwargs["stage"], kwargs["backend"], 1, detail
                            )
                        raise AssertionError(argv)

                runner = SubtitleRiskRunner()
                intake = video_intake.VideoIntake(
                    {
                        "platform": "bilibili",
                        "url": "https://www.bilibili.com/video/BV1risk",
                        "host": "www.bilibili.com",
                    },
                    "分析画面", "always", None, Path(raw), runner=runner,
                )
                packet = intake.execute()
                self.assertEqual([call[2] for call in runner.calls], ["video", "subtitle"])
                self.assertEqual(intake.access_blocks, {"platform": expected_code})
                limitation = next(item for item in packet["limitations"] if item.get("code") == expected_code)
                self.assertTrue(limitation["non_retryable"])
                self.assertEqual(limitation["access_scope"], "platform")

    def test_xiaohongshu_metadata_risk_stops_before_media(self):
        cases = (
            (412, "HTTP 412 precondition failed", "HTTP_412"),
            (1, "account anomaly detected", "ACCOUNT_ANOMALY"),
            (1, "登录挑战：请完成验证", "LOGIN_CHALLENGE"),
        )
        for status, detail, expected_code in cases:
            with self.subTest(detail=detail), tempfile.TemporaryDirectory() as raw:
                class RiskRunner:
                    def __init__(self):
                        self.calls = []

                    def run(self, argv, **kwargs):
                        self.calls.append(list(argv))
                        raise video_intake.BackendFailure(
                            kwargs["stage"], kwargs["backend"], status, detail
                        )

                runner = RiskRunner()
                intake = video_intake.VideoIntake(
                    {
                        "platform": "xiaohongshu",
                        "url": "https://www.xiaohongshu.com/explore/risk",
                        "host": "www.xiaohongshu.com",
                    },
                    "分析画面", "always", None, Path(raw), runner=runner,
                )
                packet = intake.execute()
                self.assertEqual([call[2] for call in runner.calls], ["note"])
                self.assertEqual(intake.access_blocks, {"platform": expected_code})
                self.assertEqual(intake.platform_access_blocked, expected_code)
                self.assertTrue(packet["limitations"][0]["non_retryable"])
                self.assertEqual(packet["limitations"][0]["access_scope"], "platform")


if __name__ == "__main__":
    unittest.main()
