from __future__ import annotations

import unittest
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
METADATA = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
FAILURE_PATTERNS = (ROOT / "references" / "failure-patterns.md").read_text(encoding="utf-8")
AUDIT_RUBRIC = (ROOT / "references" / "audit-rubric.md").read_text(encoding="utf-8")
VISUAL_LANGUAGE = (ROOT / "references" / "visual-language.md").read_text(encoding="utf-8")
RENDER_EVIDENCE = (ROOT / "references" / "render-and-evidence.md").read_text(encoding="utf-8")
TEMPLATE = (ROOT / "assets" / "soft-signal-template.typ").read_text(encoding="utf-8")


class SoftSignalOutputFirstTests(unittest.TestCase):
    def test_soft_signal_is_primary_for_eric_teaching_documents(self):
        self.assertIn("primary Skill", SKILL.split("---", 2)[1])
        self.assertIn("Route Eric's English teaching", SKILL)

    def test_pdf_word_routes_here_when_product_is_teaching_document(self):
        self.assertIn("Use even when the request says “PDF”", SKILL)

    def test_explicit_eric_pdf_adapter_is_not_default(self):
        self.assertIn("`$eric-pdf` as the explicit-only Typst A4 adapter/QA route", SKILL)

    def test_generic_pdf_is_narrow_support(self):
        self.assertIn("reading, extracting, merging, splitting, rotating, OCR, forms, or encryption", SKILL)

    def test_build_is_default_and_visible_first(self):
        self.assertIn("## BUILD: default", SKILL)
        self.assertIn("Produce the visible source/PDF first", SKILL)

    def test_draft_has_one_cheap_check(self):
        build = SKILL.split("## BUILD: default", 1)[1].split("## PROOF", 1)[0]
        self.assertIn("cheapest check", build)
        self.assertIn("same agent", build)

    def test_draft_has_no_formal_review_overhead(self):
        build = SKILL.split("## BUILD: default", 1)[1].split("## PROOF", 1)[0]
        for phrase in ("writer/reviewer handoff", "persistent QA packet", "dimension score", "formal verdict"):
            self.assertIn(phrase, build)

    def test_proof_is_one_representative_surface(self):
        proof = SKILL.split("## PROOF", 1)[1].split("## RELEASE", 1)[0]
        self.assertIn("one representative page", proof)
        self.assertIn("Show the proof before scaling", proof)

    def test_bundled_template_is_the_visual_source_of_truth(self):
        build = SKILL.split("## BUILD: default", 1)[1].split("## PROOF", 1)[0]
        self.assertIn("copy `assets/soft-signal-template.typ` verbatim", build)
        self.assertIn("Do not substitute a custom base theme", build)
        self.assertIn("do not recreate", SKILL)

    def test_reference_proof_checks_page_grammar_not_only_palette(self):
        proof = SKILL.split("## PROOF", 1)[1].split("## RELEASE", 1)[0]
        for phrase in ("dense explanation page", "exercise page", "transition", "teacher-facing page"):
            self.assertIn(phrase, proof)
        self.assertIn("not only its palette", proof)

    def test_editorial_mode_preserves_continuous_book_flow(self):
        for phrase in (
            "editorial self-study mode",
            "begin midway down a page",
            "55–80%",
            "not a card grid",
            "teacher guidance adjacent",
            "Do not copy every student-edition manual page break unchanged",
            "writing lines do not make a detached fragment acceptable",
        ):
            self.assertIn(phrase, VISUAL_LANGUAGE)

    def test_release_requires_full_render_inspection(self):
        release = SKILL.split("## RELEASE", 1)[1].split("## Bounded repair", 1)[0]
        self.assertIn("inspect the contact sheet and every page", release)

    def test_section_signature_and_sticky_pagination_are_frozen(self):
        self.assertIn("#let soft-section(num: none, title: none) = block(", TEMPLATE)
        section = TEMPLATE.split("#let soft-section(num: none, title: none)", 1)[1].split("#let soft-note", 1)[0]
        self.assertIn("breakable: false", section)
        self.assertIn("sticky: true", section)
        self.assertIn("frozen public signature and sticky page behavior", RENDER_EVIDENCE)
        self.assertIn("section title must travel with the first following content block", SKILL)

    def test_section_title_and_first_content_cross_page_together(self):
        typst = shutil.which("typst")
        pdftotext = shutil.which("pdftotext")
        if not typst or not pdftotext:
            self.skipTest("Typst and pdftotext are required for the pagination probe")

        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            source = temporary_path / "sticky-probe.typ"
            output = temporary_path / "sticky-probe.pdf"
            template_path = (ROOT / "assets" / "soft-signal-template.typ").as_posix()
            source.write_text(
                f'#import "{template_path}": *\n'
                '#soft-setup(title: [Probe])[\n'
                '  #v(250mm)\n'
                '  #soft-section(num: [01], title: [STICKY-TITLE])\n'
                '  [FIRST-CONTENT]\n'
                ']\n',
                encoding="utf-8",
            )
            subprocess.run([typst, "compile", "--root", "/", str(source), str(output)], check=True)
            page_one = subprocess.run(
                [pdftotext, "-f", "1", "-l", "1", str(output), "-"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            page_two = subprocess.run(
                [pdftotext, "-f", "2", "-l", "2", str(output), "-"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout

        self.assertNotIn("STICKY-TITLE", page_one)
        self.assertNotIn("FIRST-CONTENT", page_one)
        self.assertIn("STICKY-TITLE", page_two)
        self.assertIn("FIRST-CONTENT", page_two)

    def test_orphan_section_title_is_a_release_failure(self):
        self.assertIn("section title is stranded at the page foot", FAILURE_PATTERNS)
        self.assertIn("free of a section title stranded at the page foot", AUDIT_RUBRIC)

    def test_beginner_pronunciation_is_teach_before_use(self):
        for phrase in (
            "Appearance is not instruction",
            "cumulative taught-sound ledger",
            "student-visible articulation/auditory target",
            "teacher model",
            "word-level imitation or practice",
        ):
            self.assertIn(phrase, SKILL)
        grammar = (ROOT / "references" / "english-teaching-grammar.md").read_text(encoding="utf-8")
        self.assertIn("Before a new target can be independently heard, decoded, transcribed, blended, spelled from IPA, or scored", grammar)

    def test_carriers_blind_listening_and_variants_are_bounded(self):
        grammar = (ROOT / "references" / "english-teaching-grammar.md").read_text(encoding="utf-8")
        for phrase in (
            "untaught carrier",
            "ordinary spelling plus a teacher-modelled whole word or sentence",
            "Blind listening prompts show only numbers",
            "simple cycle cannot substitute for listening",
            "teacher's actual reading",
            "stable, documented accent variant",
        ):
            self.assertIn(phrase, grammar)
        self.assertIn("A beginner is asked to decode", FAILURE_PATTERNS)
        self.assertIn("Do blind listening tasks conceal their stimuli", AUDIT_RUBRIC)

    def test_release_has_at_most_one_independent_review(self):
        release = SKILL.split("## RELEASE", 1)[1].split("## Bounded repair", 1)[0]
        self.assertIn("at most one independent review", release)

    def test_repair_loop_is_bounded_without_json_fingerprint(self):
        repair = SKILL.split("## Bounded repair", 1)[1]
        self.assertIn("before a second correction", repair)
        self.assertIn("do not generate JSON fingerprints", repair)

    def test_failure_reference_uses_same_agent_targeted_repair(self):
        self.assertIn("same agent may repair and recheck", FAILURE_PATTERNS)
        self.assertIn("new diagnostic observation", FAILURE_PATTERNS)
        for legacy in ("CREATE_EDIT", "AUDIT_ONLY", "FINAL_REVIEW", "RECHECK", "fingerprint", "BLOCKED_REPAIR_BUDGET"):
            self.assertNotIn(legacy, FAILURE_PATTERNS)

    def test_formal_rubric_has_no_scoring_control_plane(self):
        self.assertIn("formal RELEASE sign-off", AUDIT_RUBRIC)
        self.assertIn("`READY`, `NOT READY`, or `INSUFFICIENT EVIDENCE`", AUDIT_RUBRIC)
        for legacy in ("AUDIT_ONLY", "FINAL_REVIEW", "RECHECK", "Rate dimensions", "every required dimension"):
            self.assertNotIn(legacy, AUDIT_RUBRIC)

    def test_metadata_declares_primary_creator(self):
        self.assertIn("Primary creator", METADATA)
        self.assertIn("allow_implicit_invocation: true", METADATA)


if __name__ == "__main__":
    unittest.main()
