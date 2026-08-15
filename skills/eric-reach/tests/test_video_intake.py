from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("video_intake", ROOT / "scripts" / "video_intake.py")
assert SPEC and SPEC.loader
video_intake = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = video_intake
SPEC.loader.exec_module(video_intake)
LOCAL_SPEC = importlib.util.spec_from_file_location("local_transcribe", ROOT / "scripts" / "local_transcribe.py")
assert LOCAL_SPEC and LOCAL_SPEC.loader
local_transcribe = importlib.util.module_from_spec(LOCAL_SPEC)
sys.modules[LOCAL_SPEC.name] = local_transcribe
LOCAL_SPEC.loader.exec_module(local_transcribe)


class UrlTests(unittest.TestCase):
    def test_sensitive_key_classifier_handles_camel_pascal_digits_and_separators(self):
        sensitive = (
            "accessToken", "AccessToken", "sessionToken", "oauthCode", "signatureV4",
            "credentialValue", "clientSecret", "refreshToken", "xAmzCredential",
            "access.token", "session-token", "refresh_token", "X-Amz-Credential",
            "ID_TOKEN", "oauth.code", "client-secret", "credential_value",
        )
        for key in sensitive:
            with self.subTest(key=key):
                self.assertTrue(video_intake.is_sensitive_key(key))
        for key in ("video_id", "page", "list", "title", "monkey", "codec", "sessionLength"):
            with self.subTest(key=key):
                self.assertFalse(video_intake.is_sensitive_key(key))

    def test_classifies_supported_and_short_links(self):
        cases = {
            "https://www.youtube.com/watch?v=x": "youtube",
            "https://youtu.be/x": "youtube",
            "https://www.bilibili.com/video/BV1xx411c7mD": "bilibili",
            "https://b23.tv/abc": "bilibili",
            "https://www.xiaohongshu.com/explore/x": "xiaohongshu",
            "https://xhslink.com/abc": "xiaohongshu",
            "https://videos.example.org/x.mp4": "generic",
        }
        for url, expected in cases.items():
            with self.subTest(url=url):
                self.assertEqual(video_intake.classify_url(url)["platform"], expected)

    def test_rejects_non_public_url_shapes(self):
        for url in (
            "file:///etc/passwd",
            "http://localhost/video",
            "http://127.0.0.1/video",
            "http://169.254.169.254/latest/meta-data",
            "https://user:secret@example.com/video",
            "https://service.internal/video",
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                video_intake.classify_url(url)

    def test_display_url_redacts_secrets_but_fetch_url_is_exact(self):
        original = (
            "https://www.xiaohongshu.com/explore/note?xsec_token=SECRET&foo=keep&signature=SIG"
            "&session_token=SESSION&X-Amz-Credential=CRED&jwt=JWT&code=CODE"
            "&access_token=ACCESS&refresh_token=REFRESH&id_token=ID&client_secret=CLIENT"
        )
        info = video_intake.classify_url(original)
        self.assertEqual(info["fetch_url"], original)
        for secret in ("SECRET", "SIG", "SESSION", "CRED", "JWT", "CODE", "ACCESS", "REFRESH", "ID", "CLIENT"):
            self.assertNotIn(f"={secret}", info["url"])
        self.assertIn("foo=keep", info["url"])
        youtube = video_intake.classify_url("https://www.youtube.com/watch?v=abc&list=PL1&page=2&token=SECRET")
        self.assertIn("v=abc", youtube["url"])
        self.assertIn("list=PL1", youtube["url"])
        self.assertIn("page=2", youtube["url"])
        self.assertNotIn("SECRET", youtube["url"])

    def test_url_and_nested_payload_use_same_sensitive_key_classifier(self):
        pairs = {
            "accessToken": "URL_ACCESS_101",
            "sessionToken": "URL_SESSION_102",
            "oauthCode": "URL_OAUTH_103",
            "signatureV4": "URL_SIG_104",
            "credentialValue": "URL_CRED_105",
            "clientSecret": "URL_CLIENT_106",
            "refreshToken": "URL_REFRESH_107",
            "xAmzCredential": "URL_AMZ_108",
        }
        query = "&".join(f"{key}={value}" for key, value in pairs.items()) + "&v=keep"
        cleaned = video_intake.sanitize_display_url("https://example.com/video?" + query)
        self.assertIn("v=keep", cleaned)
        for secret in pairs.values():
            self.assertNotIn(secret, cleaned)
        payload = {"outer": [{key: value} for key, value in pairs.items()], "title": "ordinary prose"}
        rendered = json.dumps(video_intake.redact_sensitive_payload(payload))
        for secret in pairs.values():
            self.assertNotIn(secret, rendered)
        self.assertIn("ordinary prose", rendered)

    def test_display_url_sanitizes_sensitive_path_segments(self):
        raw = (
            "https://www.youtube.com/video/BV1ordinary/accessToken=PATHSECRET501/"
            "accessToken/PATHSECRET502/accessToken%3DPATHSECRET503/"
            "accessToken%253DPATHSECRET504/final-id?v=keep"
        )
        cleaned = video_intake.sanitize_display_url(raw)
        for marker in ("PATHSECRET501", "PATHSECRET502", "PATHSECRET503", "PATHSECRET504"):
            self.assertNotIn(marker, cleaned)
        self.assertIn("BV1ordinary", cleaned)
        self.assertIn("final-id", cleaned)
        self.assertIn("v=keep", cleaned)

    def test_fixed_point_redaction_covers_double_encoding_and_cookie_headers(self):
        probes = (
            ("https://example.com/watch?access%2554oken=DOUBLE_QUERY_SECRET&v=keep", "DOUBLE_QUERY_SECRET"),
            ("https://example.com/accessToken%2FENCODEDSLASHSECRET/video?v=keep", "ENCODEDSLASHSECRET"),
            ("https://example.com/watch?next=accessToken%253DNONURLNESTEDSECRET&v=keep", "NONURLNESTEDSECRET"),
        )
        for raw_url, secret in probes:
            with self.subTest(raw_url=raw_url):
                cleaned = video_intake.sanitize_display_url(raw_url)
                self.assertNotIn(secret, cleaned)
                self.assertIn("v=keep", cleaned)
        cleaned_header = video_intake.redact_sensitive_text(
            "Cookie: SID=COOKIE_ONE; csrftoken=COOKIE_TWO"
        )
        self.assertNotIn("COOKIE_ONE", cleaned_header)
        self.assertNotIn("COOKIE_TWO", cleaned_header)

    def test_resolution_rejects_private_answer(self):
        def resolver(*args, **kwargs):
            return [(None, None, None, None, ("10.0.0.5", 443))]

        with self.assertRaises(ValueError):
            video_intake.assert_public_resolution("example.com", resolver=resolver)

    def test_resolution_allows_public_answer(self):
        def resolver(*args, **kwargs):
            return [(None, None, None, None, ("93.184.216.34", 443))]

        video_intake.assert_public_resolution("example.com", resolver=resolver)

    def test_proxy_synthetic_range_allowed_only_for_supported_platform_host(self):
        def resolver(*args, **kwargs):
            return [(None, None, None, None, ("198.18.0.42", 443))]

        video_intake.assert_public_resolution("www.youtube.com", platform="youtube", resolver=resolver)
        with self.assertRaises(ValueError):
            video_intake.assert_public_resolution("videos.example.org", platform="generic", resolver=resolver)
        with self.assertRaises(ValueError):
            video_intake.assert_public_resolution("videos.example.org", platform="youtube", resolver=resolver)

    def test_supported_platform_still_rejects_ordinary_private_ranges(self):
        for raw_address in ("10.0.0.1", "127.0.0.1", "169.254.169.254"):
            def resolver(*args, **kwargs):
                return [(None, None, None, None, (raw_address, 443))]

            with self.subTest(address=raw_address), self.assertRaises(ValueError):
                video_intake.assert_public_resolution("www.youtube.com", platform="youtube", resolver=resolver)

    def test_exact_proxy_synthetic_ipv6_allowed_only_for_supported_platform(self):
        def mixed_resolver(*args, **kwargs):
            return [
                (None, None, None, None, ("69.171.235.22", 443)),
                (None, None, None, None, ("2001::1", 443, 0, 0)),
            ]

        video_intake.assert_public_resolution("www.youtube.com", platform="youtube", resolver=mixed_resolver)
        with self.assertRaises(ValueError):
            video_intake.assert_public_resolution("videos.example.org", platform="generic", resolver=mixed_resolver)
        with self.assertRaises(ValueError):
            video_intake.assert_public_resolution("videos.example.org", platform="youtube", resolver=mixed_resolver)

    def test_other_ipv6_benchmark_addresses_remain_blocked(self):
        for raw_address in ("2001::2", "2001:0:ffff::1"):
            def resolver(*args, **kwargs):
                return [(None, None, None, None, (raw_address, 443, 0, 0))]

            with self.subTest(address=raw_address), self.assertRaises(ValueError):
                video_intake.assert_public_resolution("www.youtube.com", platform="youtube", resolver=resolver)


class PolicyTests(unittest.TestCase):
    def test_visual_auto_policy(self):
        self.assertEqual(video_intake.decide_visual("只要字幕", "auto", "ok", 0.9)[0], False)
        self.assertEqual(video_intake.decide_visual("分析图表", "auto", "ok", 0.9)[0], True)
        self.assertEqual(video_intake.decide_visual("总结", "auto", "unavailable", 0.0)[0], True)
        self.assertEqual(video_intake.decide_visual("分析画面", "never", "unavailable", 0.0)[0], False)
        self.assertEqual(video_intake.decide_visual("只要字幕", "always", "ok", 1.0)[0], True)

    def test_backend_plans_are_free_only_and_have_no_paid_services(self):
        banned = {"agentkey", "groq", "openai", "mcp"}
        for platform in ("youtube", "bilibili", "xiaohongshu", "generic"):
            plan = video_intake.backend_plan({"platform": platform, "host": "example.com", "url": "https://example.com/v"}, "auto")
            self.assertTrue(plan)
            self.assertTrue(all(step["free_only"] is True for step in plan))
            rendered = json.dumps(plan).lower()
            self.assertFalse(any(word in rendered for word in banned))

    def test_prompt_corpus(self):
        corpus = json.loads((ROOT / "tests" / "test-prompts.json").read_text(encoding="utf-8"))
        for case in corpus:
            with self.subTest(case=case["id"]):
                self.assertEqual(video_intake.should_route_video(case["prompt"]), case["route"])

    def test_packet_schema_and_frame_cap(self):
        packet = {
            "schema_version": "1.0.0",
            "free_only": True,
            "source_categories": [
                "manual_subtitle", "auto_subtitle", "local_asr", "on_screen_ocr", "visual_observation", "platform_ai_summary"
            ],
            "source": {},
            "request": {"visual_mode": "auto"},
            "transcript": {"source_type": "local_asr"},
            "visual": {"frames": [str(i) for i in range(24)]},
            "analysis_inputs": {},
            "provenance": [],
            "limitations": [],
        }
        video_intake.validate_packet(packet)
        packet["visual"]["frames"].append("overflow")
        with self.assertRaises(ValueError):
            video_intake.validate_packet(packet)

    def test_packet_requires_all_evidence_source_categories(self):
        packet = {
            "schema_version": "1.0.0",
            "free_only": True,
            "source_categories": ["manual_subtitle"],
            "source": {},
            "request": {"visual_mode": "auto"},
            "transcript": {"source_type": "manual_subtitle"},
            "visual": {"frames": []},
            "analysis_inputs": {},
            "provenance": [],
            "limitations": [],
        }
        with self.assertRaises(ValueError):
            video_intake.validate_packet(packet)

    def test_subtitle_priority_is_manual_then_auto(self):
        both = {
            "subtitles": {"en": [{"url": "manual"}]},
            "automatic_captions": {"en": [{"url": "auto"}]},
        }
        self.assertEqual(video_intake.choose_subtitle(both), ("en", "manual_subtitle"))
        self.assertEqual(
            video_intake.choose_subtitle({"automatic_captions": both["automatic_captions"]}),
            ("en", "auto_subtitle"),
        )

    def test_local_asr_runs_only_after_subtitle_chain_is_empty(self):
        source = {"url": "https://youtu.be/x", "platform": "youtube", "id": "x", "title": "T", "author": "A", "duration": 1.0, "published_at": None}
        manual = {"status": "ok", "source_type": "manual_subtitle", "language": "en", "segments": [{"start": 0.0, "end": 1.0, "text": "hello"}], "coverage": 1.0, "file": None, "text_file": None}
        unavailable = {"status": "unavailable", "source_type": None, "language": None, "segments": [], "coverage": 0.0, "file": None, "text_file": None}
        local = {**manual, "source_type": "local_asr"}
        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw)
            media = output / "media.mp4"
            media.write_bytes(b"video")
            intake = video_intake.VideoIntake(
                {"platform": "youtube", "url": source["url"], "host": "youtu.be"}, "只要字幕", "auto", None, output
            )
            with mock.patch.object(intake, "acquire_metadata", return_value=source), mock.patch.object(
                intake, "acquire_transcript", return_value=manual
            ), mock.patch.object(intake, "download_media") as download, mock.patch.object(intake, "local_asr") as local_asr:
                intake.execute()
            download.assert_not_called()
            local_asr.assert_not_called()

            intake2 = video_intake.VideoIntake(
                {"platform": "youtube", "url": source["url"], "host": "youtu.be"}, "只要字幕", "auto", None, output
            )
            with mock.patch.object(intake2, "acquire_metadata", return_value=source), mock.patch.object(
                intake2, "acquire_transcript", return_value=unavailable
            ), mock.patch.object(intake2, "download_media", return_value=media), mock.patch.object(
                intake2, "local_asr", return_value=local
            ) as local_asr, mock.patch.object(intake2, "media_duration", return_value=1.0):
                packet = intake2.execute()
            local_asr.assert_called_once_with(media, 1.0)
            self.assertEqual(packet["transcript"]["source_type"], "local_asr")

    def test_bilibili_subtitle_defaults_auto_without_explicit_manual_marker(self):
        ordinary = [{"from": 0, "to": 1, "content": "hello"}]
        explicit = {"language": "zh-CN", "is_ai": False, "segments": ordinary}
        self.assertEqual(video_intake.bilibili_subtitle_source(ordinary), "auto_subtitle")
        self.assertEqual(video_intake.bilibili_subtitle_source(explicit), "manual_subtitle")

    def test_failure_sanitization(self):
        text = video_intake.sanitize_text(
            'Authorization: supersecret session_token=SESSION X-Amz-Credential=CRED jwt:JWT code=CODE '
            'https://example.com/v?refresh_token=REFRESH&foo=ok /Users/test/file'
        )
        self.assertNotIn("supersecret", text)
        for secret in ("SESSION", "CRED", "JWT", "CODE", "REFRESH"):
            self.assertNotIn(secret, text)

    def test_natural_language_and_json_secret_forms_are_redacted(self):
        forms = (
            "cookie is REVIEWCOOKIE001",
            "secret is REVIEWSECRET000",
            "token is REVIEWTOKEN001",
            "apiToken is REVIEWAPITOKEN001",
            "ApiToken is REVIEWAPITOKEN002",
            "code is REVIEWSECRET001",
            "accessToken is REVIEWSECRET002",
            r'\{\"accessToken\":\"REVIEWSECRET003\"\}',
            "accessToken=CAMEL_EQ_201",
            '"accessToken":"JSON_CAMEL_202"',
            "access token: NATURAL_COLON_203",
            "access token is NATURAL_IS_204",
            "OAuth code is OAUTH_IS_205",
            "session token SESSION_BARE_206",
            "session token lowercasesecret",
            "signatureV4=SIG_V4_207",
            "credential value: CRED_VALUE_208",
            "clientSecret=CLIENT_SECRET_209",
            "xAmzCredential=AMZ_CRED_210",
        )
        ordinary = "The session length is thirty minutes and the video codec is H.264."
        cleaned = video_intake.redact_sensitive_text(" | ".join(forms) + " | " + ordinary)
        for secret in (
            "REVIEWCOOKIE001", "REVIEWSECRET000", "REVIEWTOKEN001", "REVIEWAPITOKEN001", "REVIEWAPITOKEN002",
            "REVIEWSECRET001", "REVIEWSECRET002", "REVIEWSECRET003",
            "CAMEL_EQ_201", "JSON_CAMEL_202", "NATURAL_COLON_203", "NATURAL_IS_204",
            "OAUTH_IS_205", "SESSION_BARE_206", "SIG_V4_207", "CRED_VALUE_208",
            "CLIENT_SECRET_209", "AMZ_CRED_210", "lowercasesecret",
        ):
            self.assertNotIn(secret, cleaned)
        self.assertIn(ordinary, cleaned)

    def test_failure_fingerprint_normalizes_volatile_node_and_pid_tokens(self):
        first = video_intake.failure_fingerprint(
            video_intake.BackendFailure("metadata", "opencli-bilibili", 1, "(node:12345) BROWSER_CONNECT PID 901 failed")
        )
        second = video_intake.failure_fingerprint(
            video_intake.BackendFailure("metadata", "opencli-bilibili", 1, "(node:67890) BROWSER_CONNECT PID: 222 failed")
        )
        self.assertEqual(first["fingerprint"], second["fingerprint"])
        self.assertEqual(first["detail"], second["detail"])


class RuntimeTests(unittest.TestCase):
    def test_runtime_preflight_missing_and_ready(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            lock = {
                "asr": {
                    "package": "mlx-whisper",
                    "version": "0.4.3",
                    "venv_python": str(root / "venv" / "python"),
                    "model_repo": "mlx-community/whisper-large-v3-turbo",
                    "model_revision": "abc123",
                    "model_dir": str(root / "model"),
                    "revision_marker": ".model-revision",
                }
            }
            self.assertFalse(video_intake.local_runtime_preflight(lock)["ready"])
            (root / "venv").mkdir()
            (root / "venv" / "python").write_text("", encoding="utf-8")
            (root / "model").mkdir()
            (root / "model" / ".model-revision").write_text("abc123\n", encoding="utf-8")
            self.assertTrue(video_intake.local_runtime_preflight(lock)["ready"])

    def test_runtime_preflight_enforces_required_model_file_hashes(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            python = root / "venv" / "python"
            model = root / "model"
            python.parent.mkdir()
            python.write_text("", encoding="utf-8")
            model.mkdir()
            (model / ".model-revision").write_text("rev123\n", encoding="utf-8")
            weights = b"small-test-weights"
            config = b'{"model":"test"}'
            (model / "weights.safetensors").write_bytes(weights)
            (model / "config.json").write_bytes(config)
            lock = {
                "asr": {
                    "package": "mlx-whisper",
                    "version": "0.4.3",
                    "venv_python": str(python),
                    "model_repo": "test/model",
                    "model_revision": "rev123",
                    "model_dir": str(model),
                    "revision_marker": ".model-revision",
                    "required_files": {
                        "weights.safetensors": __import__("hashlib").sha256(weights).hexdigest(),
                        "config.json": __import__("hashlib").sha256(config).hexdigest(),
                    },
                }
            }
            self.assertTrue(video_intake.local_runtime_preflight(lock)["ready"])
            (model / "config.json").write_bytes(b"tampered")
            result = video_intake.local_runtime_preflight(lock)
            self.assertFalse(result["ready"])
            self.assertIn("model_hash:config.json", result["missing"])
            (model / "weights.safetensors").unlink()
            result = video_intake.local_runtime_preflight(lock)
            self.assertIn("model_file:weights.safetensors", result["missing"])

    def test_local_adapter_rejects_hash_mismatch_before_import(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            audio = root / "audio.wav"
            model = root / "model"
            model.mkdir()
            audio.write_bytes(b"audio")
            (model / ".model-revision").write_text("rev123\n", encoding="utf-8")
            (model / "config.json").write_bytes(b"tampered")
            config = {
                "asr": {
                    "package": "mlx-whisper",
                    "version": "0.4.3",
                    "model_revision": "rev123",
                    "model_dir": str(model),
                    "revision_marker": ".model-revision",
                    "required_files": {"config.json": "0" * 64},
                }
            }
            config_path = root / "lock.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            stdout = io.StringIO()
            with mock.patch.object(sys, "argv", ["local_transcribe.py", str(audio), "--config", str(config_path)]), contextlib.redirect_stdout(stdout), mock.patch.object(
                local_transcribe.importlib.metadata, "version", side_effect=AssertionError("package import must not occur")
            ):
                status = local_transcribe.main()
        self.assertEqual(status, 2)
        self.assertIn("hash mismatch", stdout.getvalue())

    def test_runner_never_uses_shell(self):
        completed = subprocess.CompletedProcess(["tool"], 0, "ok", "")
        with mock.patch.object(video_intake.subprocess, "run", return_value=completed) as called:
            literal = "https://example.com/video.mp4?x=$(touch /tmp/nope);echo=pwned"
            result = video_intake.Runner().run(["tool", literal], stage="test", backend="fake")
        self.assertEqual(result, "ok")
        self.assertIs(called.call_args.kwargs["shell"], False)
        self.assertEqual(called.call_args.args[0][1], literal)

    def test_tmp_output_safety(self):
        with self.assertRaises(ValueError):
            video_intake.safe_output_dir("relative/path")
        with self.assertRaises(ValueError):
            video_intake.safe_output_dir("/etc/video-intake")
        path = video_intake.safe_output_dir(None)
        self.assertTrue(path.is_dir())
        self.assertEqual(Path(tempfile.gettempdir()).resolve(), path.parent.resolve())
        with tempfile.TemporaryDirectory(prefix="eric-reach-unit-test-", dir="/tmp") as raw:
            explicit = video_intake.safe_output_dir(raw)
            self.assertEqual(Path(raw).resolve(), explicit)
        with tempfile.TemporaryDirectory(prefix="eric-reach-unit-test-", dir="/tmp") as raw:
            (Path(raw) / "stale.txt").write_text("stale", encoding="utf-8")
            with self.assertRaises(ValueError):
                video_intake.safe_output_dir(raw)

    def test_dry_run_is_mocked_and_has_no_acquisition(self):
        stdout = io.StringIO()
        with mock.patch.object(video_intake, "assert_public_resolution"), mock.patch.object(
            video_intake.VideoIntake, "execute", side_effect=AssertionError("must not acquire")
        ), contextlib.redirect_stdout(stdout):
            status = video_intake.main(["https://youtu.be/test", "--dry-run"])
        self.assertEqual(status, 0)
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["free_only"])
        self.assertTrue(payload["planned_steps"])

    def test_dry_run_never_prints_private_fetch_url_or_token(self):
        original = "https://www.xiaohongshu.com/explore/note?xsec_token=TOPSECRET&foo=keep"
        stdout = io.StringIO()
        with mock.patch.object(video_intake, "assert_public_resolution"), contextlib.redirect_stdout(stdout):
            status = video_intake.main([original, "--dry-run"])
        self.assertEqual(status, 0)
        rendered = stdout.getvalue()
        self.assertNotIn("TOPSECRET", rendered)
        self.assertNotIn("fetch_url", rendered)
        self.assertIn("foo=keep", rendered)

    def test_missing_runtime_preflight_has_no_side_effects(self):
        lock = {
            "asr": {
                "package": "mlx-whisper",
                "version": "0.4.3",
                "venv_python": "/tmp/definitely-missing-eric-reach/python",
                "model_repo": "mlx-community/whisper-large-v3-turbo",
                "model_revision": "locked",
                "model_dir": "/tmp/definitely-missing-eric-reach/model",
                "revision_marker": ".model-revision",
            }
        }
        with mock.patch.object(video_intake.subprocess, "run") as called:
            result = video_intake.local_runtime_preflight(lock)
        self.assertFalse(result["ready"])
        called.assert_not_called()
        self.assertIn("never install or download", result["action"])

    def test_post_download_one_gib_cap_removes_media(self):
        class OversizeRunner:
            def __init__(self, output):
                self.output = output

            def run(self, argv, **kwargs):
                media = self.output / "media.mp4"
                with media.open("wb") as handle:
                    handle.truncate(1073741825)
                return ""

        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw)
            intake = video_intake.VideoIntake(
                {"platform": "youtube", "url": "https://youtu.be/x", "host": "youtu.be"},
                "",
                "auto",
                None,
                output,
                runner=OversizeRunner(output),
            )
            result = intake.download_media(want_video=True, height=720)
            self.assertIsNone(result)
            self.assertFalse((output / "media.mp4").exists())
            self.assertTrue(any(item.get("stage") == "media_size" for item in intake.limitations))


class BackendBehaviorTests(unittest.TestCase):
    class RecordingRunner:
        def __init__(self, responses=None, callback=None):
            self.calls = []
            self.responses = list(responses or [])
            self.callback = callback

        def run(self, argv, **kwargs):
            self.calls.append(list(argv))
            if self.callback:
                return self.callback(argv, kwargs)
            return self.responses.pop(0) if self.responses else "[]"

    def test_generic_redirect_or_rebinding_target_never_reaches_backend(self):
        class ForbiddenRunner:
            def run(self, argv, **kwargs):
                raise AssertionError(f"generic target reached backend: {argv}")

        raw_url = "https://redirect.example/video.mp4?url=http%3A%2F%2F127.0.0.1%2Fadmin&session_token=SECRET"
        info = video_intake.classify_url(raw_url)
        with tempfile.TemporaryDirectory() as raw:
            intake = video_intake.VideoIntake(info, raw_url, "always", None, Path(raw), runner=ForbiddenRunner())
            packet = intake.execute()
            self.assertIsNone(intake.acquire_metadata()["title"])
            self.assertEqual(intake.acquire_transcript(None)["status"], "unavailable")
            self.assertIsNone(intake.download_media(want_video=True, height=720))
            self.assertIsNone(intake.discover_generic_opencli())
        self.assertEqual(packet["limitations"][0]["code"], "SECURITY_BLOCK")
        self.assertEqual(packet["provenance"][0]["backend"], "generic-network-disabled")
        self.assertNotIn("SECRET", json.dumps(packet))
        self.assertEqual(packet["transcript"]["status"], "unavailable")

    def test_adversarial_natural_intent_secrets_never_persist_in_packet(self):
        secrets = {
            "CAMEL": "PACKET_CAMEL_301",
            "JSON": "PACKET_JSON_302",
            "COLON": "PACKET_COLON_303",
            "IS": "PACKET_IS_304",
            "OAUTH": "PACKET_OAUTH_305",
            "SESSION": "PACKET_SESSION_306",
            "SIG": "PACKET_SIG_307",
            "CRED": "PACKET_CRED_308",
            "CLIENT": "PACKET_CLIENT_309",
            "REFRESH": "PACKET_REFRESH_310",
            "AMZ": "PACKET_AMZ_311",
            "CODE_IS": "REVIEWSECRET001",
            "CAMEL_IS": "REVIEWSECRET002",
            "ESCAPED": "REVIEWSECRET003",
            "NESTED": "REVIEWNESTED004",
            "COOKIE_IS": "REVIEWCOOKIE601",
            "SECRET_IS": "REVIEWSECRET602",
            "TOKEN_IS": "REVIEWTOKEN603",
            "API_TOKEN_IS": "REVIEWAPITOKEN604",
            "PATH_EQ": "REVIEWPATH605",
            "PATH_NEXT": "REVIEWPATH606",
        }
        intent = (
            f"cookie is {secrets['COOKIE_IS']} secret is {secrets['SECRET_IS']} "
            f"token is {secrets['TOKEN_IS']} apiToken is {secrets['API_TOKEN_IS']} "
            f"code is {secrets['CODE_IS']} accessToken is {secrets['CAMEL_IS']} "
            + r'\{\"accessToken\":\"' + secrets["ESCAPED"] + r'\"\} '
            f"accessToken={secrets['CAMEL']} "
            f'\"accessToken\":\"{secrets["JSON"]}\" '
            f"access token: {secrets['COLON']} access token is {secrets['IS']} "
            f"OAuth code is {secrets['OAUTH']} session token {secrets['SESSION']} "
            f"signatureV4={secrets['SIG']} credential value: {secrets['CRED']} "
            f"clientSecret={secrets['CLIENT']} refreshToken={secrets['REFRESH']} "
            f"xAmzCredential={secrets['AMZ']}"
        )
        info = video_intake.classify_url(
            f"https://generic.example/accessToken={secrets['PATH_EQ']}/accessToken/{secrets['PATH_NEXT']}/video.mp4"
            f"?accessToken={secrets['CAMEL']}&sessionToken={secrets['SESSION']}"
            f"&next=https%253A%252F%252Fnested.example%252Fcb%253FaccessToken%253D{secrets['NESTED']}&v=keep"
        )
        with tempfile.TemporaryDirectory() as raw:
            packet = video_intake.VideoIntake(info, intent, "always", None, Path(raw), runner=self.RecordingRunner()).execute()
        rendered = json.dumps(packet, ensure_ascii=False)
        for secret in secrets.values():
            self.assertNotIn(secret, rendered)
        self.assertIn("v=keep", packet["source"]["url"])
        self.assertEqual(packet["limitations"][0]["code"], "SECURITY_BLOCK")

    def test_fixed_point_secret_probes_never_persist_in_serialized_packet(self):
        secrets = (
            "DOUBLE_QUERY_SECRET", "ENCODEDSLASHSECRET", "NONURLNESTEDSECRET",
            "COOKIE_ONE", "COOKIE_TWO",
        )
        raw_url = (
            "https://generic.example/accessToken%2FENCODEDSLASHSECRET/video.mp4"
            "?access%2554oken=DOUBLE_QUERY_SECRET"
            "&next=accessToken%253DNONURLNESTEDSECRET&v=keep"
        )
        info = video_intake.classify_url(raw_url)
        intent = "Cookie: SID=COOKIE_ONE; csrftoken=COOKIE_TWO"
        with tempfile.TemporaryDirectory() as raw:
            packet = video_intake.VideoIntake(
                info, intent, "never", None, Path(raw), runner=self.RecordingRunner()
            ).execute()
        rendered = json.dumps(packet, ensure_ascii=False)
        for secret in secrets:
            self.assertNotIn(secret, rendered)
        self.assertIn("v=keep", packet["source"]["url"])

    def test_execute_finally_removes_nested_raw_subtitle_after_media_failure(self):
        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw)

            def callback(argv, kwargs):
                if argv[:3] == ["opencli", "bilibili", "video"]:
                    return json.dumps([
                        {"field": "bvid", "value": "BV1test"},
                        {"field": "标题", "value": "Visual demo"},
                        {"field": "时长", "value": "00:30"},
                    ], ensure_ascii=False)
                if argv[:3] == ["opencli", "bilibili", "subtitle"]:
                    return "[]"
                if argv[:3] == ["opencli", "bilibili", "download"]:
                    nested = output / "nested" / "backend"
                    nested.mkdir(parents=True, exist_ok=True)
                    (nested / "backend-output.srt").write_text(
                        "RAW_BACKEND_SUBTITLE_SECRET", encoding="utf-8"
                    )
                    raise video_intake.BackendFailure(
                        kwargs["stage"], kwargs["backend"], 1, "media failed"
                    )
                raise AssertionError(argv)

            intake = video_intake.VideoIntake(
                {
                    "platform": "bilibili",
                    "url": "https://www.bilibili.com/video/BV1test",
                    "host": "www.bilibili.com",
                },
                "分析画面",
                "always",
                None,
                output,
                runner=self.RecordingRunner(callback=callback),
            )
            packet = intake.execute()
            self.assertFalse(packet["visual"]["performed"])
            self.assertTrue(any(item.get("stage") == "media_download" for item in packet["limitations"]))
            for path in output.rglob("*"):
                if path.is_file():
                    self.assertNotIn(path.suffix.lower(), video_intake.RAW_SUBTITLE_SUFFIXES)

    def test_raw_subtitle_artifacts_are_removed_after_sanitized_normalization(self):
        secret = "RAW_SUBTITLE_SECRET_401"
        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw)

            def callback(argv, kwargs):
                if argv[0] == "yt-dlp":
                    (output / "source.en.vtt").write_text(
                        f"WEBVTT\n\n00:00:00.000 --> 00:00:01.000\naccessToken={secret}\n",
                        encoding="utf-8",
                    )
                    (output / "source.en.srt").write_text(f"1\n00:00:00,000 --> 00:00:01,000\n{secret}\n", encoding="utf-8")
                    return ""
                raise AssertionError(argv)

            intake = video_intake.VideoIntake(
                {"platform": "youtube", "url": "https://youtu.be/x", "host": "youtu.be"},
                "只要字幕", "never", None, output, runner=self.RecordingRunner(callback=callback),
            )
            intake.meta = {"subtitles": {"en": [{"url": "manual"}]}}
            transcript = intake.acquire_transcript(1.0)
            self.assertEqual(Path(transcript["file"]).name, "transcript.json")
            self.assertFalse(any(path.name.startswith("source") for path in output.iterdir()))
            for path in output.rglob("*"):
                if path.is_file():
                    self.assertNotIn(secret, path.read_text(encoding="utf-8", errors="replace"))

    def test_nested_raw_subtitles_removed_on_empty_malformed_and_failure(self):
        prohibited = video_intake.RAW_SUBTITLE_SUFFIXES

        def run_case(raises):
            marker = "RAW_NESTED_SECRET_701" if not raises else "RAW_FAILURE_SECRET_702"
            with tempfile.TemporaryDirectory() as raw:
                output = Path(raw)

                def callback(argv, kwargs):
                    if argv[0] == "yt-dlp":
                        nested = output / "nested" / "deeper"
                        nested.mkdir(parents=True)
                        (nested / "empty.vtt").write_text("", encoding="utf-8")
                        (nested / "bad.srt").write_text(marker, encoding="utf-8")
                        (nested / "bad.json3").write_text("{malformed " + marker, encoding="utf-8")
                        if raises:
                            raise video_intake.BackendFailure(kwargs["stage"], kwargs["backend"], 1, "subtitle failure")
                        return ""
                    return "[]"

                intake = video_intake.VideoIntake(
                    {"platform": "youtube", "url": "https://youtu.be/x", "host": "youtu.be"},
                    "只要字幕", "never", None, output, runner=self.RecordingRunner(callback=callback),
                )
                intake.meta = {"subtitles": {"en": [{"url": "manual"}]}}
                transcript = intake.acquire_transcript(1.0)
                self.assertEqual(transcript["status"], "unavailable")
                for path in output.rglob("*"):
                    if path.is_file():
                        self.assertNotIn(path.suffix.lower(), prohibited)
                        self.assertNotIn(marker, path.read_text(encoding="utf-8", errors="replace"))

        run_case(False)
        run_case(True)

    def test_every_ytdlp_call_uses_neutral_configuration_prefix(self):
        calls = []

        def make_runner(output):
            def callback(argv, kwargs):
                calls.append(list(argv))
                if "--dump-single-json" in argv:
                    return "{}"
                if "--skip-download" in argv:
                    (output / "source.en.vtt").write_text(
                        "WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nhello\n", encoding="utf-8"
                    )
                    return ""
                target = output / ("media.wav" if "-x" in argv else "media.mp4")
                target.write_bytes(b"media")
                return ""
            return self.RecordingRunner(callback=callback)

        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw)
            intake = video_intake.VideoIntake(
                {"platform": "youtube", "url": "https://youtu.be/x", "host": "youtu.be"},
                "", "never", None, output, runner=make_runner(output),
            )
            intake.acquire_metadata()
            intake.meta = {"subtitles": {"en": [{"url": "manual"}]}}
            intake.acquire_transcript(1.0)
            intake.download_media(want_video=True, height=720)
        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw)
            intake = video_intake.VideoIntake(
                {"platform": "youtube", "url": "https://youtu.be/x", "host": "youtu.be"},
                "", "never", None, output, runner=make_runner(output),
            )
            intake.download_media(want_video=False, height=720)
        self.assertEqual(len(calls), 4)
        for argv in calls:
            self.assertEqual(argv[: len(video_intake.YTDLP_NEUTRAL_PREFIX)], video_intake.YTDLP_NEUTRAL_PREFIX)
            self.assertNotIn("--cookies", argv)
            self.assertNotIn("--cookies-from-browser", argv)

    def test_bilibili_page_propagates_to_metadata_and_subtitle(self):
        metadata = json.dumps([
            {"field": "标题", "value": "Demo"},
            {"field": "UP主", "value": "Eric"},
            {"field": "时长", "value": "01:30"},
        ])
        subtitle = json.dumps([{"from": 0, "to": 1, "content": "hello"}])
        runner = self.RecordingRunner([metadata, subtitle])
        with tempfile.TemporaryDirectory() as raw:
            intake = video_intake.VideoIntake(
                {"platform": "bilibili", "url": "https://www.bilibili.com/video/BV1xx411c7mD", "host": "bilibili.com"},
                "",
                "never",
                3,
                Path(raw),
                runner=runner,
            )
            source = intake.acquire_metadata()
            transcript = intake.acquire_transcript(source["duration"])
        self.assertEqual(source["title"], "Demo")
        self.assertEqual(source["author"], "Eric")
        self.assertEqual(source["duration"], 90.0)
        self.assertEqual(transcript["source_type"], "auto_subtitle")
        self.assertTrue(all(call[call.index("--page") + 1] == "3" for call in runner.calls if "--page" in call))
        self.assertEqual(sum("--page" in call for call in runner.calls), 2)

    def test_opencli_field_value_metadata_normalization(self):
        bili = [
            {"field": "bvid", "value": "BV123"},
            {"field": "标题", "value": "B title"},
            {"field": "UP主", "value": "B author"},
            {"field": "时长", "value": "12:34"},
            {"field": "发布时间", "value": "2026-07-18"},
        ]
        xhs = [
            {"field": "笔记ID", "value": "note123"},
            {"field": "笔记标题", "value": "X title"},
            {"field": "博主", "value": "X author"},
            {"field": "视频时长", "value": "00:45"},
            {"field": "发布日期", "value": "2026-07-17"},
        ]
        b_source = video_intake.source_from_metadata("bilibili", "https://bilibili.com", video_intake.normalize_opencli_metadata("bilibili", bili))
        x_source = video_intake.source_from_metadata("xiaohongshu", "https://xiaohongshu.com", video_intake.normalize_opencli_metadata("xiaohongshu", xhs))
        self.assertEqual((b_source["id"], b_source["title"], b_source["author"], b_source["duration"], b_source["published_at"]), ("BV123", "B title", "B author", 754.0, "2026-07-18"))
        self.assertEqual((x_source["id"], x_source["title"], x_source["author"], x_source["duration"], x_source["published_at"]), ("note123", "X title", "X author", 45.0, "2026-07-17"))

    def test_xiaohongshu_exit_zero_login_wall_is_auth_limitation(self):
        wall = json.dumps([
            {"field": "标题", "value": "手机号登录"},
            {"field": "内容", "value": ""},
            {"field": "点赞", "value": 0},
            {"field": "评论", "value": 0},
        ], ensure_ascii=False)
        runner = self.RecordingRunner([wall])
        with tempfile.TemporaryDirectory() as raw:
            intake = video_intake.VideoIntake(
                {"platform": "xiaohongshu", "url": "https://www.xiaohongshu.com/explore/expired", "host": "xiaohongshu.com"},
                "",
                "never",
                None,
                Path(raw),
                runner=runner,
            )
            source = intake.acquire_metadata()
        self.assertIsNone(source["title"])
        self.assertEqual(intake.platform_text, "")
        self.assertTrue(any("AUTH_REQUIRED" in item.get("detail", "") for item in intake.limitations))
        self.assertFalse(any(item["outcome"] == "ok" for item in intake.provenance))
        self.assertEqual(intake.provenance[-1], {"stage": "metadata", "backend": "opencli-xiaohongshu", "outcome": "failed"})
        self.assertEqual(intake.platform_access_blocked, "AUTH_REQUIRED")
        calls_before = len(runner.calls)
        self.assertIsNone(intake.download_media(want_video=True, height=720))
        self.assertEqual(len(runner.calls), calls_before)

    def test_xiaohongshu_substantive_note_may_mention_login(self):
        note = json.dumps([
            {"field": "笔记标题", "value": "账号安全经验"},
            {"field": "内容", "value": "这是一篇完整的账号安全经验分享，登录之后要检查设备列表并及时更换密码。"},
            {"field": "博主", "value": "Alice"},
        ], ensure_ascii=False)
        runner = self.RecordingRunner([note])
        with tempfile.TemporaryDirectory() as raw:
            intake = video_intake.VideoIntake(
                {"platform": "xiaohongshu", "url": "https://www.xiaohongshu.com/explore/valid", "host": "xiaohongshu.com"},
                "",
                "never",
                None,
                Path(raw),
                runner=runner,
            )
            source = intake.acquire_metadata()
        self.assertEqual(source["title"], "账号安全经验")
        self.assertEqual(source["author"], "Alice")
        self.assertIn("登录之后", intake.platform_text)
        self.assertFalse(intake.limitations)
        self.assertEqual(intake.provenance[-1]["outcome"], "ok")

    def test_xiaohongshu_packet_redacts_tokens_but_backend_gets_exact_url(self):
        original = (
            "https://www.xiaohongshu.com/accessToken=PATHFETCHSECRET/explore/valid"
            "?xsec_token=TOPSECRET&foo=keep&signature=SIGSECRET&accessToken=FETCHONLYSECRET"
        )
        info = video_intake.classify_url(original)
        note = json.dumps([
            {"field": "笔记标题", "value": "Valid note"},
            {"field": "内容", "value": "完整内容包含普通说明，以及链接 https://example.com/path?token=INNERSECRET&foo=ok"},
            {"field": "博主", "value": "Alice"},
            {"field": "xsec_token", "value": "PAYLOADSECRET"},
            {"field": "cookie", "value": "COOKIESECRET"},
            {
                "authorization": "AUTHSECRET", "signature": "PAYLOADSIG", "password": "PASSSECRET",
                "secret": "PLAINSECRET", "session_token": "PAYLOADSESSION", "X-Amz-Credential": "AMZCRED",
                "jwt": "PAYLOADJWT", "code": "PAYLOADCODE", "access_token": "PAYLOADACCESS",
                "refresh_token": "PAYLOADREFRESH", "id_token": "PAYLOADID",
            },
        ], ensure_ascii=False)
        runner = self.RecordingRunner([note])
        unavailable = {"status": "unavailable", "source_type": None, "language": None, "segments": [], "coverage": 0.0, "file": None, "text_file": None}
        with tempfile.TemporaryDirectory() as raw:
            intent = "只要字幕 " + original + " session_token=INTENTSESSION X-Amz-Credential=INTENTCRED jwt=INTENTJWT code=INTENTCODE"
            intake = video_intake.VideoIntake(info, intent, "never", None, Path(raw), runner=runner)
            with mock.patch.object(intake, "acquire_transcript", return_value=unavailable), mock.patch.object(
                intake, "download_media", return_value=None
            ):
                packet = intake.execute()
        self.assertEqual(runner.calls[0][3], original)
        rendered = json.dumps(packet, ensure_ascii=False)
        for secret in (
            "TOPSECRET", "SIGSECRET", "INNERSECRET", "PAYLOADSECRET", "COOKIESECRET", "AUTHSECRET",
            "PAYLOADSIG", "PASSSECRET", "INTENTSESSION", "INTENTCRED", "INTENTJWT", "INTENTCODE",
            "PLAINSECRET", "PAYLOADSESSION", "AMZCRED", "PAYLOADJWT", "PAYLOADCODE", "PAYLOADACCESS",
            "PAYLOADREFRESH", "PAYLOADID", "FETCHONLYSECRET", "PATHFETCHSECRET",
        ):
            self.assertNotIn(secret, rendered)
        self.assertIn("foo=keep", packet["source"]["url"])
        self.assertNotIn("xsec_token", packet["source"]["url"])
        self.assertIn("<redacted>", packet["analysis_inputs"]["platform_text"])

    def test_all_executable_ytdlp_doc_examples_are_neutralized(self):
        required = set(video_intake.YTDLP_NEUTRAL_PREFIX[1:])
        for doc in ROOT.rglob("*.md"):
            lines = doc.read_text(encoding="utf-8").splitlines()
            index = 0
            while index < len(lines):
                stripped = lines[index].strip()
                if stripped.startswith("yt-dlp "):
                    command = stripped
                    while command.rstrip().endswith("\\") and index + 1 < len(lines):
                        index += 1
                        command += " " + lines[index].strip()
                    with self.subTest(doc=str(doc), command=command):
                        self.assertTrue(required.issubset(set(command.replace("\\", " ").split())))
                index += 1

    def test_bilibili_subtitle_auth_does_not_block_public_media_local_asr(self):
        class SubtitleAuthRunner:
            def __init__(self, output):
                self.output = output
                self.calls = []

            def run(self, argv, **kwargs):
                self.calls.append(list(argv))
                if argv[:3] == ["opencli", "bilibili", "video"]:
                    return json.dumps([
                        {"field": "标题", "value": "Public video"},
                        {"field": "时长", "value": "00:30"},
                    ])
                if argv[:3] == ["opencli", "bilibili", "subtitle"]:
                    raise video_intake.BackendFailure(
                        kwargs["stage"], kwargs["backend"], 1, "AUTH_REQUIRED: subtitle track requires account"
                    )
                if argv[:3] == ["opencli", "bilibili", "download"]:
                    (self.output / "media.mp4").write_bytes(b"public-media")
                    return "{}"
                raise AssertionError(argv)

        unavailable_local = {
            "status": "ok", "source_type": "local_asr", "language": "zh", "coverage": 1.0,
            "segments": [{"start": 0.0, "end": 30.0, "text": "local transcript"}],
            "file": None, "text_file": None,
        }
        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw)
            runner = SubtitleAuthRunner(output)
            intake = video_intake.VideoIntake(
                {"platform": "bilibili", "url": "https://www.bilibili.com/video/BV1xx411c7mD", "host": "bilibili.com"},
                "只要字幕", "auto", None, output, runner=runner,
            )
            with mock.patch.object(intake, "local_asr", return_value=unavailable_local) as local_asr:
                packet = intake.execute()
        self.assertEqual([call[2] for call in runner.calls], ["video", "subtitle", "download"])
        self.assertNotIn("platform", intake.access_blocks)
        self.assertEqual(intake.access_blocks["subtitle"], "AUTH_REQUIRED")
        local_asr.assert_called_once()
        self.assertEqual(packet["transcript"]["source_type"], "local_asr")

    def test_opencli_access_boundary_stops_subtitle_and_download(self):
        class DisconnectedRunner:
            def __init__(self):
                self.calls = []

            def run(self, argv, **kwargs):
                self.calls.append(list(argv))
                raise video_intake.BackendFailure(
                    kwargs["stage"], kwargs["backend"], 1, "(node:12345) BROWSER_CONNECT: bridge disconnected"
                )

        runner = DisconnectedRunner()
        with tempfile.TemporaryDirectory() as raw:
            intake = video_intake.VideoIntake(
                {"platform": "bilibili", "url": "https://www.bilibili.com/video/BV1xx411c7mD", "host": "bilibili.com"},
                "分析画面",
                "always",
                None,
                Path(raw),
                runner=runner,
            )
            packet = intake.execute()
        self.assertEqual(len(runner.calls), 1)
        self.assertEqual(runner.calls[0][:3], ["opencli", "bilibili", "video"])
        self.assertEqual(intake.platform_access_blocked, "BROWSER_CONNECT")
        self.assertEqual(len(packet["limitations"]), 1)
        self.assertTrue(packet["limitations"][0]["non_retryable"])

    def test_failed_visual_chain_has_at_most_two_unique_media_attempts(self):
        class FailingMediaRunner:
            def __init__(self):
                self.calls = []

            def run(self, argv, **kwargs):
                self.calls.append(list(argv))
                raise video_intake.BackendFailure(kwargs["stage"], kwargs["backend"], 1, "download failed")

        runner = FailingMediaRunner()
        source = {"url": "https://youtu.be/x", "platform": "youtube", "id": "x", "title": "T", "author": "A", "duration": 10.0, "published_at": None}
        unavailable = {"status": "unavailable", "source_type": None, "language": None, "segments": [], "coverage": 0.0, "file": None, "text_file": None}
        with tempfile.TemporaryDirectory() as raw:
            intake = video_intake.VideoIntake(
                {"platform": "youtube", "url": source["url"], "host": "youtu.be"},
                "分析画面",
                "always",
                None,
                Path(raw),
                runner=runner,
            )
            with mock.patch.object(intake, "acquire_metadata", return_value=source), mock.patch.object(
                intake, "acquire_transcript", return_value=unavailable
            ):
                intake.execute()
        self.assertEqual(len(runner.calls), 2)
        formats = [call[call.index("-f") + 1] for call in runner.calls]
        self.assertEqual(formats, ["bv*[height<=720]+ba/b[height<=720]", "bv*[height<=480]+ba/b[height<=480]"])
        self.assertEqual(intake.media_attempts, {(True, 720), (True, 480)})


class ParsingTests(unittest.TestCase):
    def test_contact_sheet_geometry_is_compact_and_bounded(self):
        self.assertEqual(video_intake.contact_sheet_geometry(3), (3, 1))
        self.assertEqual(video_intake.contact_sheet_geometry(24), (4, 6))
        self.assertEqual(video_intake.contact_sheet_geometry(99), (4, 6))

    def test_vtt_parser_deduplicates_repeated_cues(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "sample.vtt"
            path.write_text(
                "WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nHello\n\n00:00:01.000 --> 00:00:02.000\nHello\n\n00:00:02.000 --> 00:00:03.000\nWorld\n",
                encoding="utf-8",
            )
            segments = video_intake.parse_vtt(path)
        self.assertEqual([item["text"] for item in segments], ["Hello", "World"])
        self.assertEqual(segments[0]["end"], 2.0)

    def test_frame_times_respect_absolute_cap(self):
        with tempfile.TemporaryDirectory() as raw:
            intake = video_intake.VideoIntake(
                {"platform": "youtube", "url": "https://youtu.be/x", "host": "youtu.be"},
                "inspect visuals",
                "always",
                None,
                Path(raw),
            )
            transcript = {"segments": [{"start": float(i), "end": float(i + 1), "text": "x"} for i in range(100)]}
            self.assertLessEqual(len(intake.frame_times(3600, transcript)), 24)


if __name__ == "__main__":
    unittest.main()
