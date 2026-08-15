from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_quality_packet.py"
SPEC = importlib.util.spec_from_file_location("validate_quality_packet", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


VALID = MODULE.self_test_record()


class ReleaseRecordTests(unittest.TestCase):
    def codes(self, record: dict) -> set[str]:
        return {item["code"] for item in MODULE.validate_release_record(record)}

    def test_valid_release_record_passes(self):
        self.assertEqual(MODULE.validate_release_record(copy.deepcopy(VALID)), [])

    def test_schema_version_is_fixed(self):
        record = copy.deepcopy(VALID)
        record["schema_version"] = 2
        self.assertIn("SCHEMA_VERSION_INVALID", self.codes(record))

    def test_build_must_not_create_formal_record(self):
        record = copy.deepcopy(VALID)
        record["mode"] = "BUILD"
        self.assertIn("FORMAL_RECORD_RELEASE_ONLY", self.codes(record))

    def test_proof_must_not_create_formal_record(self):
        record = copy.deepcopy(VALID)
        record["mode"] = "PROOF"
        self.assertIn("FORMAL_RECORD_RELEASE_ONLY", self.codes(record))

    def test_artifact_object_is_required(self):
        record = copy.deepcopy(VALID)
        record.pop("artifact")
        self.assertIn("ARTIFACT_MISSING", self.codes(record))

    def test_artifact_target_is_required(self):
        record = copy.deepcopy(VALID)
        record["artifact"]["target"] = ""
        self.assertIn("ARTIFACT_TARGET_MISSING", self.codes(record))

    def test_frozen_identity_is_required(self):
        record = copy.deepcopy(VALID)
        record["artifact"]["identity"] = ""
        self.assertIn("ARTIFACT_IDENTITY_MISSING", self.codes(record))

    def test_authority_object_is_required(self):
        record = copy.deepcopy(VALID)
        record.pop("authority")
        self.assertIn("AUTHORITY_MISSING", self.codes(record))

    def test_authority_must_be_granted(self):
        record = copy.deepcopy(VALID)
        record["authority"]["status"] = "pending"
        self.assertIn("AUTHORITY_NOT_GRANTED", self.codes(record))

    def test_authority_grantor_is_required(self):
        record = copy.deepcopy(VALID)
        record["authority"]["by"] = ""
        self.assertIn("AUTHORITY_GRANTOR_MISSING", self.codes(record))

    def test_authority_scope_is_required(self):
        record = copy.deepcopy(VALID)
        record["authority"]["scope"] = ""
        self.assertIn("AUTHORITY_SCOPE_MISSING", self.codes(record))

    def test_recovery_object_is_required(self):
        record = copy.deepcopy(VALID)
        record.pop("recovery")
        self.assertIn("RECOVERY_MISSING", self.codes(record))

    def test_recovery_must_be_available(self):
        record = copy.deepcopy(VALID)
        record["recovery"]["available"] = False
        self.assertIn("RECOVERY_UNAVAILABLE", self.codes(record))

    def test_recovery_method_is_required(self):
        record = copy.deepcopy(VALID)
        record["recovery"]["method"] = ""
        self.assertIn("RECOVERY_METHOD_MISSING", self.codes(record))

    def test_recovery_evidence_is_required(self):
        record = copy.deepcopy(VALID)
        record["recovery"]["evidence"] = ""
        self.assertIn("RECOVERY_EVIDENCE_MISSING", self.codes(record))

    def test_at_least_one_check_is_required(self):
        record = copy.deepcopy(VALID)
        record["checks"] = []
        self.assertIn("CHECKS_MISSING", self.codes(record))

    def test_check_must_be_object(self):
        record = copy.deepcopy(VALID)
        record["checks"] = ["tests"]
        self.assertIn("CHECK_INVALID", self.codes(record))

    def test_check_name_is_required(self):
        record = copy.deepcopy(VALID)
        record["checks"][0]["name"] = ""
        self.assertIn("CHECK_NAME_MISSING", self.codes(record))

    def test_every_check_must_pass(self):
        record = copy.deepcopy(VALID)
        record["checks"][0]["status"] = "FAIL"
        self.assertIn("CHECK_NOT_PASSING", self.codes(record))

    def test_check_evidence_is_required(self):
        record = copy.deepcopy(VALID)
        record["checks"][0]["evidence"] = ""
        self.assertIn("CHECK_EVIDENCE_MISSING", self.codes(record))

    def test_review_object_is_required(self):
        record = copy.deepcopy(VALID)
        record.pop("review")
        self.assertIn("REVIEW_MISSING", self.codes(record))

    def test_producer_is_required(self):
        record = copy.deepcopy(VALID)
        record["review"]["producer"] = ""
        self.assertIn("PRODUCER_MISSING", self.codes(record))

    def test_reviewer_is_required(self):
        record = copy.deepcopy(VALID)
        record["review"]["reviewer"] = ""
        self.assertIn("REVIEWER_MISSING", self.codes(record))

    def test_review_must_be_independent(self):
        record = copy.deepcopy(VALID)
        record["review"]["independent"] = False
        self.assertIn("INDEPENDENCE_REQUIRED", self.codes(record))

    def test_same_agent_cannot_sign_off(self):
        record = copy.deepcopy(VALID)
        record["review"]["reviewer"] = "Writer"
        record["review"]["producer"] = " writer "
        self.assertIn("SAME_AGENT_SIGNOFF_FORBIDDEN", self.codes(record))

    def test_review_verdict_must_be_ready(self):
        record = copy.deepcopy(VALID)
        record["review"]["verdict"] = "NOT READY"
        self.assertIn("REVIEW_NOT_READY", self.codes(record))

    def test_findings_must_be_a_list(self):
        record = copy.deepcopy(VALID)
        record["findings"] = {}
        self.assertIn("FINDINGS_INVALID", self.codes(record))

    def test_open_p0_blocks_release(self):
        record = copy.deepcopy(VALID)
        record["findings"] = [{"severity": "P0", "status": "open"}]
        self.assertIn("OPEN_RELEASE_BLOCKER", self.codes(record))

    def test_open_p1_blocks_release(self):
        record = copy.deepcopy(VALID)
        record["findings"] = [{"severity": "P1", "status": "open"}]
        self.assertIn("OPEN_RELEASE_BLOCKER", self.codes(record))

    def test_open_p2_is_nonblocking(self):
        record = copy.deepcopy(VALID)
        record["findings"] = [{"severity": "P2", "status": "open"}]
        self.assertNotIn("OPEN_RELEASE_BLOCKER", self.codes(record))

    def test_closed_p1_is_nonblocking(self):
        record = copy.deepcopy(VALID)
        record["findings"] = [{"severity": "P1", "status": "closed"}]
        self.assertNotIn("OPEN_RELEASE_BLOCKER", self.codes(record))

    def test_invalid_severity_is_rejected(self):
        record = copy.deepcopy(VALID)
        record["findings"] = [{"severity": "critical", "status": "open"}]
        self.assertIn("FINDING_SEVERITY_INVALID", self.codes(record))

    def test_invalid_finding_status_is_rejected(self):
        record = copy.deepcopy(VALID)
        record["findings"] = [{"severity": "P2", "status": "waived"}]
        self.assertIn("FINDING_STATUS_INVALID", self.codes(record))

    def test_cli_json_output_is_machine_readable(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "release.json"
            path.write_text(json.dumps(VALID), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(path), "--json"],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["valid"])

    def test_cli_invalid_record_exits_one(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "release.json"
            path.write_text("{}", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(path), "--json"],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["valid"])

    def test_cli_malformed_json_exits_two(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "release.json"
            path.write_text("{", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 2)

    def test_cli_self_test_passes(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--self-test"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("VALID RELEASE RECORD", result.stdout)


if __name__ == "__main__":
    unittest.main()
