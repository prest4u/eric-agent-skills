#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("validate_fusion_bundle.py")
DNA_KEYS = [
    "visual_style", "component_structure", "composition", "shot_and_lens", "lighting",
    "color_science", "medium_texture", "mood", "rendering_feel", "era_culture",
    "spatial_logic", "density_blank_space", "dynamic_state", "post_processing", "signature_traits",
]


class FusionValidatorTests(unittest.TestCase):
    def make_bundle(self, root: Path, external_url: bool = False, unverified: bool = False) -> None:
        (root / "design").mkdir()
        (root / "src").mkdir()
        (root / "production").mkdir()
        references = [
            {"id": "A", "adopted": True, "license_status": "user-owned", "inspected_evidence": "render.png"},
            {"id": "B", "adopted": True, "license_status": "unverified" if unverified else "verified", "inspected_evidence": "repo+license"},
        ]
        brief = {
            "schema_version": 1,
            "references": references,
            "visual_dna": {key: "not_applicable" if key in {"shot_and_lens", "lighting"} else "concrete rule" for key in DNA_KEYS},
            "document_extension": {key: "concrete rule" for key in ("information_hierarchy", "pagination", "data_visualization", "iconography", "accessibility", "medium_translation")},
            "originality": {"transformations": ["structure", "type", "palette", "geometry", "assets"], "excluded": ["logos", "copy", "imagery", "full_composition"]},
        }
        (root / "design/brief.json").write_text(json.dumps(brief), encoding="utf-8")
        (root / "design/tokens.css").write_text(":root { --fusion-paper:#fff; --fusion-ink:#111; }", encoding="utf-8")
        (root / "src/index.html").write_text(f"<main><p>Original</p>{'<img src=\"https://example.com/a.png\">' if external_url else ''}</main>", encoding="utf-8")
        (root / "src/styles.css").write_text("@page { size: A4; margin: 0; } * { print-color-adjust: exact; }", encoding="utf-8")
        ledger = "| ref_id | source | author | source_class | license | license_status | attribution | adopted_rules | excluded_elements | verified_at |\n|---|---|---|---|---|---|---|---|---|---|\n"
        (root / "production/reference-ledger.md").write_text(ledger, encoding="utf-8")
        (root / "production/THIRD_PARTY_NOTICES.md").write_text("Notices", encoding="utf-8")
        manifest = {
            "expected_pages": 1,
            "required_tokens": ["--fusion-paper", "--fusion-ink"],
            "forbidden_public_terms": [],
            "files": {
                "brief": "design/brief.json", "tokens": "design/tokens.css",
                "reference_ledger": "production/reference-ledger.md",
                "third_party_notices": "production/THIRD_PARTY_NOTICES.md",
                "source_html": "src/index.html", "source_css": "src/styles.css"
            },
        }
        (root / "fusion-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    def run_validator(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(root), "--structure-only", "--no-write", "--strict"],
            text=True, capture_output=True, check=False,
        )

    def test_good_fixture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_bundle(root)
            result = self.run_validator(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "pass")

    def test_external_url_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_bundle(root, external_url=True)
            result = self.run_validator(root)
            self.assertNotEqual(result.returncode, 0)
            codes = {issue["code"] for issue in json.loads(result.stdout)["issues"]}
            self.assertIn("EXTERNAL_RUNTIME_URL", codes)

    def test_unverified_adoption_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_bundle(root, unverified=True)
            result = self.run_validator(root)
            self.assertNotEqual(result.returncode, 0)
            codes = {issue["code"] for issue in json.loads(result.stdout)["issues"]}
            self.assertIn("UNVERIFIED_ADOPTION", codes)

    def test_escaping_path_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_bundle(root)
            manifest = json.loads((root / "fusion-manifest.json").read_text())
            manifest["files"]["brief"] = "../outside.json"
            (root / "fusion-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            result = self.run_validator(root)
            self.assertNotEqual(result.returncode, 0)
            codes = {issue["code"] for issue in json.loads(result.stdout)["issues"]}
            self.assertIn("UNSAFE_PATH", codes)


if __name__ == "__main__":
    unittest.main()
