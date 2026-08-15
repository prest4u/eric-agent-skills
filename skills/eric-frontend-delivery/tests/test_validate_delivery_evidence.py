import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import unicodedata
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_DIR / "scripts" / "validate_delivery_evidence.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("delivery_validator", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def good_packet():
    state_ids = ["default", "loading", "empty", "error", "success", "keyboard-focus"]
    return {
        "schema_version": 1,
        "delivery_id": "dashboard-final-2026-07-12",
        "route": "production_create",
        "artifact": {
            "targets": ["src/Dashboard.tsx", "src/dashboard.css"],
            "source_identity": "git:abc123",
            "build_identity": "sha256:build123",
            "runtime": "http://127.0.0.1:4173/dashboard",
        },
        "q0": {
            "outcome": "Users complete the dashboard triage flow without layout or state failures.",
            "primary_flow": ["open dashboard", "filter incidents", "inspect incident"],
            "source_of_truth": ["product brief", "current repository"],
            "non_goals": ["backend redesign", "marketing landing page"],
            "product_surface": "authenticated React dashboard",
            "framework": "React with the existing Vite setup",
            "design_system": "reuse existing tokens and components",
            "asset_policy": "reuse local approved assets",
            "dependency_policy": "no new dependencies",
            "design_direction": "dense operational clarity with restrained amber accents",
            "viewports": [
                {"id": "desktop", "width": 1440, "height": 900},
                {"id": "mobile", "width": 390, "height": 844},
            ],
            "states": [{"id": state_id, "required": True} for state_id in state_ids],
            "accessibility": ["keyboard", "visible focus", "labels", "basic contrast"],
            "acceptance_evidence": ["build", "runtime", "desktop", "mobile", "states"],
        },
        "stages": {
            "q1": {
                "owner": "frontend-design",
                "status": "pass",
                "evidence": ["src/Dashboard.tsx"],
            },
            "q2": {
                "status": "pass",
                "commands": [
                    {"command": "npm run build", "status": "pass", "evidence": "qa/logs/build.txt"},
                    {"command": "npm run test", "status": "pass", "evidence": "qa/logs/test.txt"},
                ],
            },
            "q3": {
                "owner": "eric-review",
                "mode": "RECHECK",
                "status": "pass",
                "build_identity": "sha256:build123",
                "runtime_evidence": "qa/runtime/dashboard-loaded.json",
                "viewports": [
                    {"id": "desktop", "evidence": "qa/renders/dashboard-desktop.png"},
                    {"id": "mobile", "evidence": "qa/renders/dashboard-mobile.png"},
                ],
                "states": [
                    {"id": state_id, "evidence": f"qa/states/{state_id}.png"}
                    for state_id in state_ids
                ],
                "reviewer_provenance": "same_agent",
            },
            "q4": {
                "owner": "eric-review",
                "status": "pending",
                "reviewer_provenance": "fresh_independent_required",
                "verdict": "PENDING INDEPENDENT REVIEW",
            },
        },
        "permissions": {
            "inspect": True,
            "edit": True,
            "external_mutation": False,
            "publish_send": False,
        },
        "verdict": "PENDING INDEPENDENT REVIEW",
        "next_action": "Send the exact build identity and evidence matrix to a fresh eric-review reviewer.",
    }


class DeliveryEvidenceValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = load_validator()

    def assert_codes(self, packet, *codes):
        found = {item["code"] for item in self.validator.validate(packet)}
        for code in codes:
            self.assertIn(code, found)

    def test_good_candidate_packet_passes(self):
        self.assertEqual([], self.validator.validate(good_packet()))

    def test_missing_runtime_evidence_fails(self):
        packet = good_packet()
        del packet["stages"]["q3"]["runtime_evidence"]
        self.assert_codes(packet, "Q3_RUNTIME_EVIDENCE_MISSING")

    def test_runtime_accepts_only_strict_loopback_http_urls(self):
        accepted = (
            "http://localhost/",
            "http://localhost:4173/dashboard",
            "http://localhost:1/",
            "http://localhost:65535/",
            "https://127.0.0.1/app",
            "http://127.255.10.9:8080/app",
            "http://[::1]:3000/app",
            "http://[0:0:0:0:0:0:0:1]:3000/app",
        )
        self.assertEqual(8, len(accepted))
        for runtime in accepted:
            with self.subTest(runtime=runtime):
                packet = good_packet()
                packet["artifact"]["runtime"] = runtime
                codes = {item["code"] for item in self.validator.validate(packet)}
                self.assertNotIn("RUNTIME_URL_INVALID", codes)

        rejected = (
            "https://example.com/app",
            "http://127.0.0.1.evil.test/app",
            "http://user@127.0.0.1/app",
            "ftp://127.0.0.1/app",
            "file:///tmp/app.html",
            "http://127.0.0.1:bad/app",
            "http://[::1/app",
            "http://localhost/%zz",
            "//127.0.0.1/app",
            "http://127.1/app",
            "http://[::ffff:127.0.0.1]/",
            "http://localhost:0/",
            "http://127.0.0.1:00000/",
            "http://localhost:/",
            "http://localhost:65536/",
            "http://0x7f000001/",
            "http://2130706433/",
            f"http://localhost:{'9' * 4301}/",
        )
        self.assertEqual(18, len(rejected))
        for runtime in rejected:
            with self.subTest(runtime=runtime):
                packet = good_packet()
                packet["artifact"]["runtime"] = runtime
                self.assert_codes(packet, "RUNTIME_URL_INVALID")

    def test_port_validation_is_bounded_before_integer_conversion(self):
        for port in ("", "0", "00000", "65536", "0" * 4301, "9" * 4301):
            with self.subTest(port_length=len(port)):
                self.assertFalse(self.validator.valid_port(port))
        for port in ("1", "65535"):
            with self.subTest(port=port):
                self.assertTrue(self.validator.valid_port(port))

    def test_cli_rejects_extreme_numeric_port_with_json_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            packet = Path(tmp) / "oversized-port.json"
            broken = good_packet()
            broken["artifact"]["runtime"] = f"http://localhost:{'9' * 4301}/"
            packet.write_text(json.dumps(broken), encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(packet), "--json", "--no-write"],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(1, result.returncode)
            payload = json.loads(result.stdout)
            self.assertEqual("FAIL", payload["status"])
            self.assertIn("RUNTIME_URL_INVALID", {item["code"] for item in payload["findings"]})
            self.assertNotIn("Traceback", result.stdout + result.stderr)

    def test_all_evidence_locators_require_portable_contained_paths(self):
        mutations = (
            ("artifact.targets[0]", lambda p: p["artifact"]["targets"].__setitem__(0, "https://example.com/private.png")),
            ("stages.q1.evidence[0]", lambda p: p["stages"]["q1"]["evidence"].__setitem__(0, "file://<user-home>/private.png")),
            ("stages.q2.commands[0].evidence", lambda p: p["stages"]["q2"]["commands"][0].__setitem__("evidence", "data:text/plain,secret")),
            ("stages.q3.runtime_evidence", lambda p: p["stages"]["q3"].__setitem__("runtime_evidence", "C:<user-home>/private.png")),
            ("stages.q3.viewports[0].evidence", lambda p: p["stages"]["q3"]["viewports"][0].__setitem__("evidence", "C:relative.png")),
            ("stages.q3.states[0].evidence", lambda p: p["stages"]["q3"]["states"][0].__setitem__("evidence", "//server/share/state.png")),
            ("stages.q3.states[1].evidence", lambda p: p["stages"]["q3"]["states"][1].__setitem__("evidence", r"\\server\share\state.png")),
            ("stages.q3.states[2].evidence", lambda p: p["stages"]["q3"]["states"][2].__setitem__("evidence", r"qa\..\private.png")),
        )
        for field, mutate in mutations:
            with self.subTest(field=field):
                packet = good_packet()
                mutate(packet)
                findings = self.validator.validate(packet)
                self.assertIn(("EVIDENCE_PATH_ESCAPE", field), {(item["code"], item["field"]) for item in findings})
                self.assertNotIn("private.png", json.dumps(findings))

    def test_all_six_locator_fields_share_raw_percent_and_nfkc_canonical_matrix(self):
        locator_fields = (
            ("artifact.targets[0]", lambda p, value: p["artifact"]["targets"].__setitem__(0, value)),
            ("stages.q1.evidence[0]", lambda p, value: p["stages"]["q1"]["evidence"].__setitem__(0, value)),
            ("stages.q2.commands[0].evidence", lambda p, value: p["stages"]["q2"]["commands"][0].__setitem__("evidence", value)),
            ("stages.q3.runtime_evidence", lambda p, value: p["stages"]["q3"].__setitem__("runtime_evidence", value)),
            ("stages.q3.viewports[0].evidence", lambda p, value: p["stages"]["q3"]["viewports"][0].__setitem__("evidence", value)),
            ("stages.q3.states[0].evidence", lambda p, value: p["stages"]["q3"]["states"][0].__setitem__("evidence", value)),
        )
        raw_invalid = (
            "", "/private/evidence.png", "~/private.png", "C:/private.png", "C:private.png",
            "//server/share.png", r"\\server\share.png", r"qa\private.png",
            "qa//private.png", "qa/./private.png", "qa/../private.png", "./qa/private.png",
            "../qa/private.png", "qa/private.png/", "https://example.test/private.png",
            "qa/secret\x00.png", "qa/secret\x1f.png", "qa/secret\x7f.png", "qa/secret\u0085.png",
        )
        percent_invalid = (
            "qa/%2e%2e/private.png", "qa/%252e/private.png", "qa/100%25.png", "qa/100%.png",
        )
        nfkc_invalid = (
            "ｑａ/private.png", "qa/①-private.png", "qa／private.png", "Ｃ:private.png",
        )
        for field, mutate in locator_fields:
            for family, values in (
                ("raw", raw_invalid), ("percent", percent_invalid), ("nfkc", nfkc_invalid)
            ):
                for value in values:
                    with self.subTest(field=field, family=family, value=repr(value)):
                        self.assertNotEqual(value, "证据/首页.png")
                        if family == "nfkc":
                            self.assertNotEqual(value, unicodedata.normalize("NFKC", value))
                        packet = good_packet()
                        mutate(packet, value)
                        findings = self.validator.validate(packet)
                        self.assertIn(
                            ("EVIDENCE_PATH_ESCAPE", field),
                            {(item["code"], item["field"]) for item in findings},
                        )
                        if value:
                            self.assertNotIn(value, json.dumps(findings, ensure_ascii=False))

    def test_portable_relative_evidence_paths_remain_valid(self):
        self.assertTrue(self.validator.relative_path("screenshots/home.png"))
        self.assertTrue(self.validator.relative_path("qa/evidence/state.json"))
        self.assertTrue(self.validator.relative_path("证据/首页.png"))

    def test_q3_reviewer_provenance_is_required_and_role_bounded(self):
        packet = good_packet()
        del packet["stages"]["q3"]["reviewer_provenance"]
        self.assert_codes(packet, "Q3_REVIEWER_PROVENANCE_MISSING")

        for invalid in ("fresh_independent_required", "fresh_independent", "unknown", 3):
            with self.subTest(provenance=invalid):
                packet = good_packet()
                packet["stages"]["q3"]["reviewer_provenance"] = invalid
                self.assert_codes(packet, "Q3_REVIEWER_PROVENANCE_INVALID")

        for valid in ("same_agent", "independent_agent", "eric"):
            with self.subTest(provenance=valid):
                packet = good_packet()
                packet["stages"]["q3"]["reviewer_provenance"] = valid
                codes = {item["code"] for item in self.validator.validate(packet)}
                self.assertNotIn("Q3_REVIEWER_PROVENANCE_INVALID", codes)

    def test_missing_mobile_and_required_state_fails(self):
        packet = good_packet()
        packet["stages"]["q3"]["viewports"] = packet["stages"]["q3"]["viewports"][:1]
        packet["stages"]["q3"]["states"] = packet["stages"]["q3"]["states"][:-1]
        self.assert_codes(packet, "Q3_VIEWPORT_COVERAGE_MISSING", "Q3_STATE_COVERAGE_MISSING")

    def test_declared_viewport_and_state_entries_require_strict_unique_shapes(self):
        mutations = (
            ("Q0_VIEWPORT_DUPLICATE", lambda p: p["q0"]["viewports"].append(dict(p["q0"]["viewports"][0]))),
            ("Q0_VIEWPORT_INVALID", lambda p: p["q0"]["viewports"].append({"id": "tablet", "width": True, "height": 800})),
            ("Q0_VIEWPORT_INVALID", lambda p: p["q0"]["viewports"].append({"id": "tablet", "width": 800, "height": 1000, "extra": "no"})),
            ("Q0_STATE_DUPLICATE", lambda p: p["q0"]["states"].append(dict(p["q0"]["states"][0]))),
            ("Q0_STATE_INVALID", lambda p: p["q0"]["states"].append({"id": "disabled"})),
            ("Q0_STATE_INVALID", lambda p: p["q0"]["states"].append({"id": "disabled", "required": "yes"})),
        )
        for code, mutate in mutations:
            with self.subTest(code=code, mutation=mutate):
                packet = good_packet()
                mutate(packet)
                self.assert_codes(packet, code)

    def test_observed_viewport_and_state_entries_require_strict_unique_shapes(self):
        mutations = (
            ("Q3_VIEWPORT_DUPLICATE", lambda p: p["stages"]["q3"]["viewports"].append(dict(p["stages"]["q3"]["viewports"][0]))),
            ("Q3_VIEWPORT_INVALID", lambda p: p["stages"]["q3"]["viewports"].append({"id": "tablet"})),
            ("Q3_VIEWPORT_UNDECLARED", lambda p: p["stages"]["q3"]["viewports"].append({"id": "tablet", "evidence": "qa/renders/tablet.png"})),
            ("Q3_STATE_DUPLICATE", lambda p: p["stages"]["q3"]["states"].append(dict(p["stages"]["q3"]["states"][0]))),
            ("Q3_STATE_INVALID", lambda p: p["stages"]["q3"]["states"].append({"id": "disabled"})),
            ("Q3_STATE_UNDECLARED", lambda p: p["stages"]["q3"]["states"].append({"id": "disabled", "evidence": "qa/states/disabled.png"})),
        )
        for code, mutate in mutations:
            with self.subTest(code=code, mutation=mutate):
                packet = good_packet()
                mutate(packet)
                self.assert_codes(packet, code)

    def test_same_agent_ready_is_rejected(self):
        packet = good_packet()
        packet["stages"]["q4"] = {
            "owner": "eric-review",
            "status": "pass",
            "reviewer_provenance": "same_agent",
            "verdict": "READY",
        }
        packet["verdict"] = "READY"
        self.assert_codes(packet, "SAME_AGENT_READY_FORBIDDEN")

    def test_complete_q4_verdict_status_provenance_matrix(self):
        compatibility = {
            "READY": (("pass", "fresh_independent"), ("pass", "eric")),
            "READY WITH MINOR FOLLOW-UPS": (("pass", "fresh_independent"), ("pass", "eric")),
            "PENDING INDEPENDENT REVIEW": (("pending", "fresh_independent_required"),),
            "NOT READY": (("fail", "same_agent"), ("fail", "fresh_independent"), ("fail", "eric")),
            "INSUFFICIENT EVIDENCE": (("blocked", "same_agent"), ("blocked", "fresh_independent"), ("blocked", "eric")),
            "BLOCKED_REPAIR_BUDGET": (("blocked", "same_agent"), ("blocked", "fresh_independent"), ("blocked", "eric")),
        }
        statuses = ("pass", "pending", "fail", "blocked")
        provenances = ("same_agent", "fresh_independent_required", "fresh_independent", "eric")
        for verdict, allowed in compatibility.items():
            for status in statuses:
                for provenance in provenances:
                    with self.subTest(verdict=verdict, status=status, provenance=provenance):
                        packet = good_packet()
                        packet["verdict"] = verdict
                        packet["stages"]["q4"].update(
                            {"status": status, "reviewer_provenance": provenance, "verdict": verdict}
                        )
                        q4_codes = {
                            item["code"] for item in self.validator.validate(packet)
                            if item["field"].startswith("stages.q4")
                        }
                        if (status, provenance) in allowed:
                            self.assertEqual(set(), q4_codes)
                        else:
                            self.assertTrue(q4_codes)

            for missing, code in (
                ("status", "Q4_STATUS_MISSING"),
                ("reviewer_provenance", "Q4_REVIEWER_PROVENANCE_MISSING"),
            ):
                with self.subTest(verdict=verdict, missing=missing):
                    packet = good_packet()
                    packet["verdict"] = verdict
                    packet["stages"]["q4"].update(
                        {"status": allowed[0][0], "reviewer_provenance": allowed[0][1], "verdict": verdict}
                    )
                    del packet["stages"]["q4"][missing]
                    self.assert_codes(packet, code)

    def test_path_escape_is_rejected(self):
        packet = good_packet()
        packet["stages"]["q3"]["runtime_evidence"] = "../private/runtime.json"
        self.assert_codes(packet, "EVIDENCE_PATH_ESCAPE")

    def test_cli_emits_json_and_human_next_action_with_strict_exits(self):
        with tempfile.TemporaryDirectory() as tmp:
            good = Path(tmp) / "good.json"
            bad = Path(tmp) / "bad.json"
            good.write_text(json.dumps(good_packet()), encoding="utf-8")
            broken = copy.deepcopy(good_packet())
            del broken["stages"]["q3"]["runtime_evidence"]
            bad.write_text(json.dumps(broken), encoding="utf-8")

            passed = subprocess.run(
                [sys.executable, str(SCRIPT), str(good), "--json", "--no-write"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, passed.returncode, passed.stderr)
            self.assertEqual("PASS", json.loads(passed.stdout)["status"])

            failed = subprocess.run(
                [sys.executable, str(SCRIPT), str(bad), "--no-write"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(1, failed.returncode)
            self.assertIn("next_action:", failed.stdout)

    def test_cli_rejects_every_raw_c0_and_del_without_traceback_in_json_and_human_modes(self):
        with tempfile.TemporaryDirectory() as tmp:
            packet_path = Path(tmp) / "raw-control-url.json"
            for codepoint in (*range(0x20), 0x7F):
                runtime = f"http://local{chr(codepoint)}host:4173/dashboard"
                for mode in ("json", "human"):
                    with self.subTest(codepoint=codepoint, mode=mode):
                        packet = good_packet()
                        packet["artifact"]["runtime"] = runtime
                        packet_path.write_text(json.dumps(packet), encoding="utf-8")
                        command = [sys.executable, str(SCRIPT), str(packet_path), "--no-write"]
                        if mode == "json":
                            command.append("--json")
                        result = subprocess.run(command, check=False, capture_output=True, text=True)
                        self.assertEqual(1, result.returncode)
                        self.assertNotIn("Traceback", result.stdout + result.stderr)
                        if mode == "json":
                            payload = json.loads(result.stdout)
                            self.assertIn("RUNTIME_URL_INVALID", {item["code"] for item in payload["findings"]})
                        else:
                            self.assertIn("RUNTIME_URL_INVALID", result.stdout)

    def test_documented_relative_invocation_works_from_skill_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            packet = Path(tmp) / "packet.json"
            packet.write_text(json.dumps(good_packet()), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "./scripts/validate_delivery_evidence.py", str(packet), "--json", "--no-write"],
                cwd=SKILL_DIR,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual("PASS", json.loads(result.stdout)["status"])


if __name__ == "__main__":
    unittest.main()
