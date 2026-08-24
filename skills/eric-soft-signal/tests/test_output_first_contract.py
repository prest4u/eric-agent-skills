from __future__ import annotations

import sys
import unittest
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
try:
    import check_layout
except ImportError:
    check_layout = None
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

    def test_written_response_and_passage_components_exist_with_guards(self):
        for signature in (
            "#let soft-task(prompt, lines: 2, preset: none",
            "#let soft-passage(body, label: none, title: none",
            "#let soft-exercise-group(body)",
        ):
            self.assertIn(signature, TEMPLATE)
        task = TEMPLATE.split("#let soft-task(", 1)[1].split("#let soft-passage", 1)[0]
        self.assertIn("breakable: false", task)
        passage = TEMPLATE.split("#let soft-passage(", 1)[1].split("#let soft-exercise-group", 1)[0]
        self.assertIn("sticky: true", passage)
        group = TEMPLATE.split("#let soft-exercise-group", 1)[1]
        self.assertIn("breakable: false", group)

    def test_print_size_floor_is_enforced_in_template(self):
        self.assertIn("10pt print floor", TEMPLATE)
        self.assertIn("8.5pt print floor", TEMPLATE)

    def test_mcq_four_box_is_a_hard_build_rule(self):
        self.assertIn("## HARD: 单项选择 / MCQ surface", SKILL)
        self.assertIn("exactly 4", SKILL)
        self.assertIn("inline-mcq", SKILL)
        self.assertIn("only MCQ surface", RENDER_EVIDENCE)
        self.assertIn("exactly four choices", (ROOT / "references" / "english-teaching-grammar.md").read_text(encoding="utf-8"))
        self.assertIn("Multiple-choice surface", VISUAL_LANGUAGE)
        self.assertIn("inline A. B. C. instead of the 2×2 four-box", FAILURE_PATTERNS)
        self.assertIn("`soft-question` four-box", AUDIT_RUBRIC)
        self.assertIn("only student-facing choice surface", TEMPLATE)

    def test_latin_cover_title_contract(self):
        self.assertIn("## HARD: 标题字体", SKILL)
        self.assertIn("Libertinus Serif", SKILL)
        self.assertIn("soft-latin-title-font", SKILL)
        self.assertIn("latin: true", SKILL)
        self.assertIn("Libertinus Serif", VISUAL_LANGUAGE)
        self.assertIn("Default Chinese covers stay Zhuque", VISUAL_LANGUAGE)
        self.assertIn('#let soft-latin-title-font = ("Libertinus Serif", "New Computer Modern")', TEMPLATE)
        self.assertIn("#let soft-cover-title-face(title, latin: auto)", TEMPLATE)
        self.assertIn("#let soft-cover-display-title(title, latin: auto", TEMPLATE)
        self.assertIn("title-rest: none, latin: auto) = [", TEMPLATE)
        self.assertIn("soft-cover-title(title-prefix, title-rest, latin: latin)", TEMPLATE)
        sources = (ROOT / "assets" / "fonts" / "SOURCES.md").read_text(encoding="utf-8")
        self.assertIn("Libertinus Serif", sources)
        self.assertIn("SIL Open Font License", sources)

    def test_binding_density_and_layout_check_rules_are_documented(self):
        for phrase in (
            "one unbreakable block",
            "soft-exercise-group",
            "soft-passage",
            "print-size floor",
            "check_layout.py",
        ):
            self.assertIn(phrase, RENDER_EVIDENCE)
        self.assertIn("binding block", FAILURE_PATTERNS)
        self.assertIn("orphaned from their passage", FAILURE_PATTERNS)
        self.assertIn("check_layout.py", SKILL)
        self.assertIn("content-height ratio", VISUAL_LANGUAGE)

    def _compile_probe(self, source_text):
        typst = shutil.which("typst")
        pdftotext = shutil.which("pdftotext")
        if not typst or not pdftotext:
            self.skipTest("Typst and pdftotext are required for pagination probes")
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        temporary_path = Path(temporary.name)
        source = temporary_path / "probe.typ"
        output = temporary_path / "probe.pdf"
        template_path = (ROOT / "assets" / "soft-signal-template.typ").as_posix()
        source.write_text(
            f'#import "{template_path}": *\n' + source_text,
            encoding="utf-8",
        )
        build = subprocess.run(
            [typst, "compile", "--root", "/", str(source), str(output)],
            capture_output=True,
            text=True,
        )
        return build, output

    def _page_text(self, pdf, page):
        return subprocess.run(
            ["pdftotext", "-f", str(page), "-l", str(page), str(pdf), "-"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout

    def test_soft_task_binds_prompt_to_writing_lines(self):
        build, output = self._compile_probe(
            '#soft-setup(title: [Probe])[\n'
            '  #v(242mm)\n'
            '  #soft-task([TASKPROMPT Rewrite the sentence.], preset: "rewrite")\n'
            ']\n'
        )
        self.assertEqual(build.returncode, 0, build.stderr)
        self.assertNotIn("TASKPROMPT", self._page_text(output, 1))
        self.assertIn("TASKPROMPT", self._page_text(output, 2))

    def test_body_size_below_print_floor_fails_compile(self):
        build, _ = self._compile_probe(
            '#soft-setup(title: [Probe], body-size: 9pt)[ text ]\n'
        )
        self.assertNotEqual(build.returncode, 0)
        self.assertIn("print floor", build.stderr)

    def test_exercise_group_keeps_passage_and_questions_together(self):
        build, output = self._compile_probe(
            '#soft-setup(title: [Probe])[\n'
            '  #v(215mm)\n'
            '  #soft-exercise-group[\n'
            '    #soft-passage([PASSAGETEXT The cat sat. ] * 40)\n'
            '    #soft-question(stem: [(1) GROUPQ choose.], choices: ("a", "b", "c", "d"), evidence-label: none)\n'
            '  ]\n'
            ']\n'
        )
        self.assertEqual(build.returncode, 0, build.stderr)
        page_one = self._page_text(output, 1)
        self.assertNotIn("PASSAGETEXT", page_one)
        self.assertNotIn("GROUPQ", page_one)
        page_two = self._page_text(output, 2)
        self.assertIn("PASSAGETEXT", page_two)
        self.assertIn("GROUPQ", page_two)


@unittest.skipIf(check_layout is None, "check_layout.py or PIL is unavailable")
class CheckLayoutTests(unittest.TestCase):
    def _page_image(self, directory, name, fill_rows=None):
        from PIL import Image, ImageDraw

        image = Image.new("RGB", (100, 200), check_layout.SOFT_PAPER)
        if fill_rows:
            draw = ImageDraw.Draw(image)
            for top, bottom in fill_rows:
                draw.rectangle([0, top, 99, bottom], fill=(33, 27, 23))
        path = directory / name
        image.save(path)
        return path

    def _analyze(self, pages):
        return check_layout.analyze_pages(
            pages,
            set(),
            check_layout.NEAR_EMPTY,
            check_layout.SPARSE,
            check_layout.LOW_DENSITY_HEIGHT,
            check_layout.LOW_DENSITY_INK,
            check_layout.DENSE_HEIGHT,
            check_layout.DENSE_INK,
        )

    def test_blank_page_is_a_near_empty_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            page = self._page_image(Path(temporary), "page-1.png")
            _, findings, summary = self._analyze([page])
        self.assertEqual(summary["errors"], 1)
        self.assertEqual(findings[0]["category"], "near-empty")

    def test_occupied_page_is_clean(self):
        with tempfile.TemporaryDirectory() as temporary:
            page = self._page_image(Path(temporary), "page-1.png", fill_rows=[(10, 149)])
            _, findings, summary = self._analyze([page])
        self.assertEqual(findings, [])
        self.assertTrue(summary["clean"])

    def test_tall_but_thin_page_is_a_low_density_warning(self):
        with tempfile.TemporaryDirectory() as temporary:
            page = self._page_image(Path(temporary), "page-1.png", fill_rows=[(180, 181)])
            _, findings, _ = self._analyze([page])
        categories = {finding["category"] for finding in findings}
        self.assertIn("low-density-tall-page", categories)
        self.assertNotIn("near-empty", categories)

    def test_source_lint_flags_manual_density_tuning(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "dense.typ"
            source.write_text("#pagebreak()\n" * 4 + "#v(5pt)\n" * 31, encoding="utf-8")
            flagged = check_layout.source_lint(source, 3, 30)
            source.write_text("#pagebreak()\ntext\n#v(5pt)\n", encoding="utf-8")
            clean = check_layout.source_lint(source, 3, 30)
        self.assertFalse(flagged["clean"])
        self.assertEqual(flagged["findings"][0]["category"], "suspected-manual-density-tuning")
        self.assertTrue(clean["clean"])

    def test_source_lint_flags_inline_mcq_and_spares_four_box(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "mcq.typ"
            source.write_text(
                "#soft-question(\n"
                '  stem: [(1) Choose.],\n'
                '  choices: ("desk", "cloud", "sing", "carefully"),\n'
                ")\n"
                "A. bought  B. had  C. buy  D. have\n"
                "1. She lives here. （A. lives B. live C. living）\n"
                "soft-choice(label: [A.], body: [desk], correct: false)\n"
                "// Never write dotted A/B/C runs inline\n"
                "#tnote([怎么讲], [\n"
                "  A. when the train leaves B. invert C. invert\n"
                "])\n"
                "[序号], [A.], [改对],\n",
                encoding="utf-8",
            )
            result = check_layout.source_lint(source, 3, 30)
        categories = [finding["category"] for finding in result["findings"]]
        self.assertEqual(categories.count("inline-mcq"), 2)
        self.assertEqual(result["inline_mcq_count"], 2)
        self.assertFalse(result["clean"])
        self.assertTrue(any(f["severity"] == "error" for f in result["findings"]))

    def test_leak_pattern_matches_teacher_markers_only(self):
        for leaked in ("TEACHER EDITION", "教师版", "correct-index: 0", "/Users/example/x"):
            self.assertRegex(leaked, check_layout.LEAK_PATTERN)
        for safe in ("teacher model", "教师用书以外", "soft-question"):
            self.assertNotRegex(safe, check_layout.LEAK_PATTERN)

    def test_pages_command_exit_code_follows_errors(self):
        if shutil.which("python3") is None:
            self.skipTest("python3 is required")
        script = ROOT / "scripts" / "check_layout.py"
        with tempfile.TemporaryDirectory() as temporary:
            renders = Path(temporary)
            bad = self._page_image(renders, "page-1.png")
            bad_run = subprocess.run(
                ["python3", str(script), "pages", str(renders)],
                capture_output=True,
            )
            good = self._page_image(renders, "page-1.png", fill_rows=[(10, 149)])
            good_run = subprocess.run(
                ["python3", str(script), "pages", str(renders)],
                capture_output=True,
            )
        self.assertEqual(bad_run.returncode, 1, bad_run.stderr.decode())
        self.assertEqual(good_run.returncode, 0, good_run.stderr.decode())


if __name__ == "__main__":
    unittest.main()
