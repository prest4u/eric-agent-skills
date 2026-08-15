#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))

import qa_textbook_pdf as qa_module  # noqa: E402
import audit_v2_completion as audit_module  # noqa: E402
import validate_skill_gates as gate_module  # noqa: E402
from qa_textbook_pdf import (  # noqa: E402
    ASSET_MODE_FINAL,
    STARTER_SAMPLE_TITLE,
    a4_only_profile_policy,
    a4_sentence_map_surface_policy,
    asset_metadata_policy,
    asset_usage_policy,
    blank_baseline_css_checks,
    checklist_control_css_checks,
    configured_answer_visibility,
    configured_source_input_paths,
    cover_brand_checks,
    duplicated_question_blank_hits,
    exam_stem_slot_policy,
    generic_book_identity_policy,
    inactive_page_source_files,
    literal_underscore_runs,
    page_family_coverage_policy,
    page_role_rhythm_policy,
    page_role_variant_policy,
    rendered_page_records,
    page_structure_variant_library_policy,
    cloze_blank_label_language_policy,
    parse_human_review,
    planner_surface_checks,
    qa_evidence_conflict_files,
    rendered_artifact_freshness_checks,
    renderer_ui_label_language_policy,
    rendered_page_count_checks,
    rendered_page_filename_checks,
    source_output_freshness_checks,
    starter_residue_hits,
    stale_duplicate_page_files,
    student_prompt_language_policy,
    student_forbidden_hits,
    teacher_book_integrity_policy,
    title_lockup_css_checks,
    unit_opener_composition_checks,
    unit_opener_variation_checks,
    workbook_record_checks,
    write_reports,
)


PRIVATE_VALIDATION_CORPUS = Path(__file__).resolve().parents[1] / "references" / "validation-corpus-v2.json"
requires_private_validation_corpus = unittest.skipUnless(
    PRIVATE_VALIDATION_CORPUS.is_file(),
    "extended release evidence belongs in the authorized private fixture repository",
)


class V2CompletionAuditTest(unittest.TestCase):
    @requires_private_validation_corpus
    def test_current_skill_repo_has_independent_v2_branch_baseline(self) -> None:
        audit = audit_module.audit_skill(Path(__file__).resolve().parents[1])
        item = audit_module.item_by_id(audit, "isolated_git_repo")

        self.assertEqual(audit["status"], "complete")
        self.assertEqual(item["state"], "proven", item)
        self.assertEqual(item["evidence"]["branch"], "v2-full-coverage")
        if item["evidence"]["mode"] == "independent_repo":
            self.assertGreaterEqual(item["evidence"]["commit_count"], 1)
        else:
            self.assertTrue(item["evidence"]["content_digest_verified"])

    def test_export_mirror_digest_fails_closed_after_content_change(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "reports").mkdir()
            (root / "payload.txt").write_text("frozen\n", encoding="utf-8")
            provenance = {
                "schema": "eric-designed-pdf-export-v1",
                "export_repo": "codex-skills-sync",
                "source_branch": "v2-full-coverage",
                "source_baseline_commit": "d" * 40,
                "content_sha256": audit_module.mirror_content_digest(root),
            }
            (root / "reports/export-provenance.json").write_text(
                json.dumps(provenance), encoding="utf-8"
            )
            self.assertEqual(audit_module.audit_git_repo(root)["state"], "proven")

            (root / "payload.txt").write_text("changed\n", encoding="utf-8")
            item = audit_module.audit_git_repo(root)
            self.assertEqual(item["state"], "incomplete")
            self.assertFalse(item["evidence"]["content_digest_verified"])

    def test_export_mirror_rejects_unbound_or_fake_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "reports").mkdir()
            (root / "payload.txt").write_text("frozen\n", encoding="utf-8")
            (root / "reports/export-provenance.json").write_text(
                json.dumps({
                    "schema": "eric-designed-pdf-export-v1",
                    "export_repo": "codex-skills-sync",
                    "source_branch": "v2-full-coverage",
                    "source_baseline_commit": "not-a-git-object-id",
                    "content_sha256": "0" * 64,
                }),
                encoding="utf-8",
            )
            item = audit_module.audit_git_repo(root)
            self.assertEqual(item["state"], "incomplete")
            self.assertFalse(item["evidence"]["content_digest_verified"])

    @requires_private_validation_corpus
    def test_current_v2_audit_has_formal_release_and_final_report_evidence(self) -> None:
        audit = audit_module.audit_skill(Path(__file__).resolve().parents[1])
        release_item = audit_module.item_by_id(audit, "formal_visual_release")
        final_report_item = audit_module.item_by_id(audit, "final_report_evidence")

        self.assertEqual(audit["status"], "complete")
        self.assertEqual(release_item["state"], "proven", release_item)
        self.assertEqual(final_report_item["state"], "proven", final_report_item)

    @requires_private_validation_corpus
    def test_audit_summary_counts_real_machine_clean_cases(self) -> None:
        audit = audit_module.audit_skill(Path(__file__).resolve().parents[1])

        self.assertGreaterEqual(audit["summary"]["real_machine_clean_cases"], 3)
        self.assertTrue(audit["summary"]["complete"])

    @requires_private_validation_corpus
    def test_skill_gate_tracks_completion_audit_as_required_evidence(self) -> None:
        self.assertIn("scripts/audit_v2_completion.py", gate_module.REQUIRED_FILES)

        issues, evidence = gate_module.validate_static(Path(__file__).resolve().parents[1])

        self.assertIn("v2_completion_audit", evidence)
        self.assertEqual(evidence["v2_completion_audit"]["status"], "complete")
        self.assertFalse(any(row["code"] == "V2_COMPLETION_AUDIT_SCRIPT_MISSING" for row in issues))

    def test_audit_final_assets_and_release_skip_superseded_archive_cases(self) -> None:
        corpus = {
            "cases": [
                {
                    "id": "active-final",
                    "asset_mode": "final-assets",
                    "machine_gate": {"P0": 0, "P1": 0},
                    "visual_review": {
                        "status": "PASS",
                        "score": 9.6,
                        "reviewer": "independent-review",
                        "release_eligible": True,
                    },
                },
                {
                    "id": "old-final",
                    "status": "superseded_archive",
                    "evidence_policy": "superseded_archive",
                    "asset_mode": "final-assets",
                    "machine_gate": {"P0": 0, "P1": 0},
                    "visual_review": {
                        "status": "PASS",
                        "score": 9.8,
                        "reviewer": "independent-review",
                        "release_eligible": True,
                    },
                },
            ]
        }

        final_item = audit_module.audit_final_assets(corpus)
        release_item = audit_module.audit_release(corpus)

        self.assertEqual(final_item["evidence"]["final_assets_machine_clean_cases"], ["active-final"])
        self.assertEqual(release_item["evidence"]["release_eligible_cases"], ["active-final"])


class StudentForbiddenVisibleTextTest(unittest.TestCase):
    def test_detects_student_profile_teacher_script_and_python_list_residue(self) -> None:
        hits = student_forbidden_hits("['Currently锁定现在'] 执行时先给学生观察。教师聚焦反馈：答案为B，因此选B。")

        self.assertIn("['", hits)
        self.assertIn("执行时先给学生", hits)
        self.assertIn("教师", hits)
        self.assertIn("答案为", hits)
        self.assertIn("因此选", hits)

    def test_detects_design_system_language_in_student_copy(self) -> None:
        hits = student_forbidden_hits("Each part uses its own page rhythm and surface family.")

        self.assertIn("page rhythm", hits)
        self.assertIn("surface family", hits)

    def test_detects_ai_flavored_student_heading_language(self) -> None:
        hits = student_forbidden_hits("Lesson Route / Lesson Rhythm / Micro Skills")

        self.assertIn("Lesson Route", hits)
        self.assertIn("Lesson Rhythm", hits)
        self.assertIn("Micro Skills", hits)


class A4LessonPackRegressionTest(unittest.TestCase):
    def test_exam_stem_policy_rejects_generic_blank_inside_guided_mcq(self) -> None:
        raw_html = """
        <style>
        .guided-mcq-set p .exam-stem-slot { border-bottom: 1px solid #000; }
        .exam-stem-keep { white-space: nowrap; }
        </style>
        <section class="sheet" data-page="13" data-template="exam-mini-set">
          <section class="guided-mcq-set"><article><p>On no account <span class="blank"></span> use this.</p></article></section>
        </section>
        """
        result = exam_stem_slot_policy(BeautifulSoup(raw_html, "html.parser"), raw_html)

        self.assertFalse(result["ok"], result)
        self.assertEqual(result["generic_blank_hits"][0]["page"], "13")

    def test_exam_stem_policy_accepts_dedicated_slot_and_keep_rule(self) -> None:
        raw_html = """
        <style>
        .guided-mcq-set p .exam-stem-slot { border-bottom: 1px solid #000; vertical-align: -0.12em; }
        .exam-stem-keep { white-space: nowrap; }
        </style>
        <section class="sheet" data-page="18" data-template="exam-mini-set">
          <section class="guided-mcq-set"><article><p>The answer is <span class="exam-stem-keep"><span class="exam-stem-slot"></span>&#8288;.</span></p></article></section>
        </section>
        """
        result = exam_stem_slot_policy(BeautifulSoup(raw_html, "html.parser"), raw_html)

        self.assertTrue(result["ok"], result)
        self.assertEqual(result["slot_count"], 1)

    def test_a4_sentence_map_rejects_wide_table_surface(self) -> None:
        raw_html = """
        <section class="sheet" data-page="16" data-template="sentence-map">
          <table class="textbook-table" data-component="categorizing-chart"><tr><td>long sentence</td></tr></table>
        </section>
        """
        result = a4_sentence_map_surface_policy(BeautifulSoup(raw_html, "html.parser"), "student-lesson-a4")

        self.assertFalse(result["ok"], result)
        self.assertEqual(result["wide_table_hits"][0]["page"], "16")

    def test_a4_sentence_map_accepts_card_stack_surface(self) -> None:
        raw_html = """
        <section class="sheet" data-page="16" data-template="sentence-map">
          <section class="sentence-map-card-stack" data-surface-family="sentence-map" data-surface="a4-card-stack"></section>
        </section>
        """
        result = a4_sentence_map_surface_policy(BeautifulSoup(raw_html, "html.parser"), "student-lesson-a4")

        self.assertTrue(result["ok"], result)

    def test_a4_only_profile_policy_rejects_book_trim_residue(self) -> None:
        book = {
            "qa": {"output_mode": "a4-only"},
            "profiles": {
                "student-lesson-a4": {"output_pdf": "outputs/lesson-01-student-a4.pdf"},
                "student-book-trim": {"output_pdf": "outputs/lesson-01-student-book-trim.pdf"},
            },
        }
        result = a4_only_profile_policy(book)

        self.assertFalse(result["ok"], result)
        self.assertIn("student-book-trim", result["profile_hits"])

    def test_a4_only_profile_policy_rejects_book_trim_html_residue(self) -> None:
        book = {
            "qa": {"output_mode": "a4-only"},
            "profiles": {
                "student-lesson-a4": {"output_pdf": "outputs/lesson-01-student-a4.pdf"},
                "teacher-lesson-a4": {"output_pdf": "outputs/lesson-01-teacher-a4.pdf"},
            },
        }
        result = a4_only_profile_policy(book, "<style>.profile-student-book-trim {}</style>")

        self.assertFalse(result["ok"], result)
        self.assertEqual(result["html_hits"], ["book-trim"])

    def test_a4_only_profile_policy_rejects_visible_course_residue(self) -> None:
        book = {
            "qa": {"output_mode": "a4-only"},
            "profiles": {
                "student-lesson-a4": {"output_pdf": "outputs/lesson-01-student-a4.pdf"},
                "teacher-lesson-a4": {"output_pdf": "outputs/lesson-01-teacher-a4.pdf"},
            },
        }
        raw_html = "<h1>第本课程</h1><p>回看22讲能力工具</p><h2>第 06 讲 天津卷单选综合</h2>"
        result = a4_only_profile_policy(book, raw_html)

        self.assertFalse(result["ok"], result)
        self.assertEqual(result["html_hits"], ["22讲", "第本课程", "第N讲"])

    def test_teacher_book_policy_rejects_appendix_only_teacher_book(self) -> None:
        html = "".join(
            f'<section class="sheet" data-page="{idx}" data-template="exam-mini-set"><p>Student page {idx}</p></section>'
            for idx in range(1, 36)
        )
        html += """
        <section class="sheet" data-page="36" data-template="teacher-answer-key" data-section="backmatter">
          <main data-component="answer-key-page"><h1>Teacher Guide · Lesson 01</h1><p>Student profile excludes this page</p></main>
        </section>
        <section class="sheet" data-page="37" data-template="teacher-answer-key" data-section="backmatter">
          <main data-component="answer-key-page"><h1>Teacher Key · Lesson 01</h1></main>
        </section>
        """
        policy = teacher_book_integrity_policy(
            BeautifulSoup(html, "html.parser"),
            html,
            profile="teacher-lesson-a4",
            mode="teacher",
        )

        self.assertFalse(policy["ok"], policy)
        self.assertTrue(policy["appendix_only_risk"])
        self.assertFalse(policy["checks"]["teacher_guide_not_answer_key_shell"])

    def test_teacher_book_policy_accepts_integrated_teacher_edition(self) -> None:
        html = "".join(
            f"""
            <section class="sheet" data-page="{idx}" data-template="exam-mini-set">
              <aside data-component="teacher-page-note" data-teacher-only="true">Teacher note</aside>
              <aside data-component="teacher-answer-strip" data-teacher-only="true">Q{idx} A</aside>
            </section>
            """
            for idx in range(1, 6)
        )
        html += """
        <section class="sheet" data-page="6" data-template="teacher-guide-page" data-section="backmatter">
          <main data-component="teacher-guide-page" data-teacher-only="true"><h1>Teacher Guide · Lesson Overview</h1></main>
        </section>
        <section class="sheet" data-page="7" data-template="teacher-answer-key" data-section="backmatter">
          <main data-component="answer-key-page" data-teacher-only="true"><h1>Teacher Key · Lesson 01</h1></main>
        </section>
        """
        policy = teacher_book_integrity_policy(
            BeautifulSoup(html, "html.parser"),
            html,
            profile="teacher-lesson-a4",
            mode="teacher",
        )

        self.assertTrue(policy["ok"], policy)

    def test_detects_stale_duplicate_page_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pages = root / "pages"
            pages.mkdir()
            (pages / "0001-cover.md").write_text("---\ntemplate: cover\n---\n", encoding="utf-8")
            (pages / "0001-cover 2.md").write_text("---\ntemplate: cover\n---\n", encoding="utf-8")

            result = stale_duplicate_page_files(root)

        self.assertEqual(result["count"], 1)
        self.assertEqual(result["files"], ["pages/0001-cover 2.md"])

    def test_detects_qa_evidence_conflict_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            qa = root / "_qa"
            qa.mkdir()
            (qa / "contact-sheet-book-trim.png").write_bytes(b"png")
            (qa / "contact-sheet-book-trim 2.png").write_bytes(b"png")
            (qa / "review-sheet-book-trim-key-pages 3.png").write_bytes(b"png")

            result = qa_evidence_conflict_files(root)

        self.assertEqual(result["count"], 2)
        self.assertEqual(
            result["files"],
            ["_qa/contact-sheet-book-trim 2.png", "_qa/review-sheet-book-trim-key-pages 3.png"],
        )

    def test_detects_inactive_page_source_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pages = root / "pages"
            pages.mkdir()
            (pages / "0001-cover.md").write_text("---\ntemplate: cover\n---\n", encoding="utf-8")
            (pages / "0099-old-page.md").write_text("---\ntemplate: activity\n---\n", encoding="utf-8")

            result = inactive_page_source_files(root, {"pages": ["pages/0001-cover.md"]})

        self.assertEqual(result["count"], 1)
        self.assertEqual(result["files"], ["pages/0099-old-page.md"])

    def test_starter_residue_scan_ignores_inactive_pages(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pages = root / "pages"
            pages.mkdir()
            (root / "book.yaml").write_text("title: Custom Course\n", encoding="utf-8")
            (pages / "0001-cover.md").write_text("---\ntemplate: cover\n---\nCustom Course\n", encoding="utf-8")
            (pages / "0002-old.md").write_text("Pathways to Better Writing\n", encoding="utf-8")

            result = starter_residue_hits(
                root,
                {"title": "Custom Course", "pages": ["pages/0001-cover.md"]},
                {},
                "Custom Course",
                "Custom Course",
            )

        self.assertEqual(result, {})


class GaokaoWorkbookVisibleLanguageTest(unittest.TestCase):
    def test_rejects_renderer_injected_chinese_ui_labels(self) -> None:
        html = """
        <section class="sheet" data-template="contents-route">
          <footer><span>本讲路线 • Lesson 10 · 阅读 I</span></footer>
        </section>
        <section class="sheet" data-template="contents-route">
          <footer><span>Lesson Map • 天津高考英语一轮复习</span></footer>
        </section>
        <section class="exam-timing-strip"><b>时间</b><span>Answer + evidence.</span></section>
        """
        policy = renderer_ui_label_language_policy(
            html,
            {"title": "天津高考英语一轮复习", "identity": {"audience": "Gaokao students"}},
            html,
            answer_visibility="student",
        )

        self.assertFalse(policy["ok"])
        self.assertEqual(len(policy["hits"]), 3)

    def test_accepts_english_renderer_ui_labels(self) -> None:
        html = """
        <section class="sheet" data-template="contents-route">
          <footer><span>Lesson Map • Lesson 10 · Reading Evidence</span></footer>
        </section>
        <section class="exam-timing-strip"><b>Time</b><span>Answer + evidence.</span></section>
        """
        policy = renderer_ui_label_language_policy(
            html,
            {"title": "天津高考英语一轮复习", "identity": {"audience": "Gaokao students"}},
            html,
            answer_visibility="student",
        )

        self.assertTrue(policy["ok"])
        self.assertEqual(policy["hits"], [])

    def test_rejects_student_prompt_language_drift_inside_workbook_bodies(self) -> None:
        soup = BeautifulSoup(
            """
            <section class="sheet" data-template="activity" data-page="12">
              <div class="activity-block">
                <p>接下来我们完成本页回收。</p>
                <ul><li>复盘记录：write one sentence.</li></ul>
              </div>
            </section>
            <section class="sheet" data-template="writing-planner" data-page="13">
              <p class="planner-prompt">完成前检查：mark your evidence.</p>
            </section>
            """,
            "html.parser",
        )

        policy = student_prompt_language_policy(
            soup,
            {"title": "天津高考英语一轮复习", "identity": {"audience": "Gaokao students"}},
            soup.get_text(" "),
            answer_visibility="student",
        )

        self.assertFalse(policy["ok"])
        self.assertGreaterEqual(len(policy["hits"]), 2)

    def test_rejects_chinese_cloze_and_choose_prompt_drift(self) -> None:
        soup = BeautifulSoup(
            """
            <section class="sheet" data-template="exam-mini-set" data-page="27">
              <ol class="question-lines">
                <li>完形填空第 16 空：根据全文选择最符合语境的一项。</li>
              </ol>
            </section>
            """,
            "html.parser",
        )

        policy = student_prompt_language_policy(
            soup,
            {"title": "天津高考英语一轮复习", "identity": {"audience": "Gaokao students"}},
            soup.get_text(" "),
            answer_visibility="student",
        )

        self.assertFalse(policy["ok"])
        self.assertTrue(any("cloze" in hit["term"].lower() or "blank" in hit["term"].lower() for hit in policy["hits"]))

    def test_rejects_chinese_source_type_prefix_inside_article_body(self) -> None:
        soup = BeautifulSoup(
            """
            <section class="sheet" data-template="article-opener" data-page="333">
              <section class="article-flow">
                <article class="lettered-paragraph"><p>完形填空 Life is a road full of setbacks.</p></article>
              </section>
            </section>
            """,
            "html.parser",
        )

        policy = student_prompt_language_policy(
            soup,
            {"title": "天津高考英语一轮复习", "identity": {"audience": "Gaokao students"}},
            soup.get_text(" "),
            answer_visibility="student",
        )

        self.assertFalse(policy["ok"])
        self.assertEqual(policy["hits"][0]["term"], "Chinese source-type prefix in article body")

    def test_rejects_trailing_chinese_source_section_marker_inside_article_body(self) -> None:
        soup = BeautifulSoup(
            """
            <section class="sheet" data-template="article-opener" data-page="336">
              <section class="article-flow">
                <article class="lettered-paragraph"><p>the final answer is version 三、</p></article>
              </section>
            </section>
            """,
            "html.parser",
        )

        policy = student_prompt_language_policy(
            soup,
            {"title": "天津高考英语一轮复习", "identity": {"audience": "Gaokao students"}},
            soup.get_text(" "),
            answer_visibility="student",
        )

        self.assertFalse(policy["ok"])
        self.assertEqual(policy["hits"][0]["term"], "Chinese trailing source section marker in article body")

    def test_rejects_cloze_article_body_ocr_blank_damage(self) -> None:
        soup = BeautifulSoup(
            """
            <section class="sheet" data-template="article-opener" data-page="333">
              <section class="article-flow">
                <article class="lettered-paragraph"><p>whenI__18 the A team and my __19 onthe team; ev- ery Situation ,is hard.</p></article>
              </section>
            </section>
            <section class="sheet" data-template="article-opener" data-page="390">
              <section class="article-flow">
                <article class="lettered-paragraph"><p>He __ 24 _ the reason. It was ready 30___ flights.</p></article>
              </section>
            </section>
            <section class="sheet" data-template="article-opener" data-page="391">
              <section class="article-flow">
                <article class="lettered-paragraph"><p>the lack of bikes was Covid-<span class="blank"></span> related, and a person— something changed. I wanted to bea leader.</p></article>
              </section>
            </section>
            """,
            "html.parser",
        )

        policy = student_prompt_language_policy(
            soup,
            {"title": "天津高考英语一轮复习", "identity": {"audience": "Gaokao students"}},
            soup.get_text(" "),
            answer_visibility="student",
        )

        self.assertFalse(policy["ok"])
        terms = {hit["term"] for hit in policy["hits"]}
        self.assertIn("raw cloze underscore marker in article body", terms)
        self.assertIn("OCR split word in article body", terms)
        self.assertIn("OCR fused word in article body", terms)
        self.assertIn("OCR punctuation spacing in article body", terms)

    def test_rejects_renderer_default_chinese_workbook_prompts(self) -> None:
        soup = BeautifulSoup(
            """
            <section class="sheet" data-template="writing-planner" data-page="71">
              <p class="planner-prompt">进入下一页前，先确认这一页能直接使用。</p>
            </section>
            <section class="sheet" data-template="final-check" data-page="89">
              <p class="record-prompt">下次先改哪一类题？</p>
            </section>
            """,
            "html.parser",
        )

        policy = student_prompt_language_policy(
            soup,
            {"title": "天津高考英语一轮复习", "identity": {"audience": "Gaokao students"}},
            soup.get_text(" "),
            answer_visibility="student",
        )

        self.assertFalse(policy["ok"])
        self.assertEqual({hit["term"] for hit in policy["hits"]}, {"进入下一页前", "先确认这一页", "下次先改哪一类题"})

    def test_rejects_chinese_blank_label_across_teacher_or_student_release_text(self) -> None:
        policy = cloze_blank_label_language_policy(
            "Teacher Key: 第16空先不看选项，确认空格描述年初进展状态。",
            {"title": "天津高考英语一轮复习", "identity": {"audience": "Gaokao students"}},
        )

        self.assertFalse(policy["ok"])
        self.assertEqual(policy["hits"][0]["term"], "第16空")

    def test_accepts_english_blank_label_across_teacher_or_student_release_text(self) -> None:
        policy = cloze_blank_label_language_policy(
            "Teacher Key: Blank 16 first checks the sentence logic.",
            {"title": "天津高考英语一轮复习", "identity": {"audience": "Gaokao students"}},
        )

        self.assertTrue(policy["ok"])

    def test_rejects_chinese_inner_workbook_headings(self) -> None:
        soup = BeautifulSoup(
            """
            <section class="sheet" data-template="paragraph-practice" data-page="19">
              <h1>段落诊断：原因展开</h1>
            </section>
            <section class="sheet" data-template="article-opener" data-page="20">
              <h1>校园科学展</h1>
              <p>Reading Text</p>
            </section>
            """,
            "html.parser",
        )

        policy = qa_module.visible_heading_language_policy(
            soup,
            {"title": "天津高考英语一轮复习", "identity": {"audience": "Gaokao students"}},
            soup.get_text(" "),
            answer_visibility="student",
        )

        self.assertFalse(policy["ok"])
        self.assertEqual(len(policy["workbook_cjk_heading_hits"]), 2)
        self.assertEqual(len(policy["reading_cjk_heading_hits"]), 1)

    def test_rejects_ai_flavored_english_workbook_headings(self) -> None:
        soup = BeautifulSoup(
            """
            <section class="sheet" data-template="writing-planner" data-page="12">
              <h1>Today On The Page</h1>
            </section>
            <section class="sheet" data-template="article-evidence" data-page="13">
              <h1>Evidence Pause</h1>
            </section>
            <section class="sheet" data-template="skill-method" data-page="14">
              <h1>Method Model</h1>
            </section>
            """,
            "html.parser",
        )

        policy = qa_module.visible_heading_language_policy(
            soup,
            {"title": "天津高考英语一轮复习", "identity": {"audience": "Gaokao students"}},
            soup.get_text(" "),
            answer_visibility="student",
        )

        self.assertFalse(policy["ok"])
        self.assertEqual({hit["term"] for hit in policy["ai_heading_hits"]}, {"Today On The Page", "Evidence Pause", "Method Model"})

    def test_rejects_degenerated_record_prompts_and_zero_minute_routes(self) -> None:
        soup = BeautifulSoup(
            """
            <section class="sheet" data-template="writing-planner" data-page="31">
              <p class="planner-prompt">Record / Record</p>
              <p class="planner-prompt">Preview todays steps and complete the record.</p>
            </section>
            <section class="sheet" data-template="article-opener" data-page="54">
              <section class="evidence-task-strip">
                <article><p>about 0 min · Preview today's steps.</p></article>
              </section>
            </section>
            """,
            "html.parser",
        )

        policy = student_prompt_language_policy(
            soup,
            {"title": "天津高考英语一轮复习", "identity": {"audience": "Gaokao students"}},
            soup.get_text(" "),
            answer_visibility="student",
        )

        self.assertFalse(policy["ok"])
        terms = " ".join(hit["term"] for hit in policy["hits"])
        self.assertIn("Record/Record", terms)
        self.assertIn("zero-minute", terms)
        self.assertIn("today", terms)

    def test_accepts_english_forward_workbook_prompts(self) -> None:
        soup = BeautifulSoup(
            """
            <section class="sheet" data-template="activity" data-page="12">
              <div class="activity-block">
                <p>Mark the clue before choosing.</p>
                <ul><li>Answer + evidence: write one short note.</li></ul>
              </div>
            </section>
            <section class="sheet" data-template="writing-planner" data-page="13">
              <p class="planner-prompt">Before you continue, check the evidence line.</p>
            </section>
            """,
            "html.parser",
        )

        policy = student_prompt_language_policy(
            soup,
            {"title": "天津高考英语一轮复习", "identity": {"audience": "Gaokao students"}},
            soup.get_text(" "),
            answer_visibility="student",
        )

        self.assertTrue(policy["ok"], policy)
        self.assertEqual(policy["hits"], [])


class VisualReviewContractTest(unittest.TestCase):
    def parse(self, body: str) -> dict:
        with tempfile.TemporaryDirectory(prefix="eric-pdf-review-") as tmp:
            path = Path(tmp) / "visual-review-book-trim.md"
            path.write_text(body.strip() + "\n", encoding="utf-8")
            return parse_human_review(path)

    def test_rejects_self_signed_visual_pass(self) -> None:
        review = self.parse(
            """
            FINAL_VISUAL_REVIEW: PASS
            Reviewer: agent-self
            Score: 9.8/10
            P0: 0
            P1: 0
            Checked: cover, unit opener, dense practice, workbook page, handbook
            Contact sheet: _qa/contact-sheet-book-trim.png
            Key pages: _qa/rendered-pages/book-trim-p001.png, _qa/rendered-pages/book-trim-p002.png, _qa/rendered-pages/book-trim-p006.png, _qa/rendered-pages/book-trim-p010.png
            Canon comparison: compared against golden p1, p3, p4, p6, p9.
            Reject patterns checked: thin-cover-type, dashboard-panel, ui-number-block.
            Font decision: B primary, C fallback.
            Visual diagnosis: Publication-grade.
            Weak pages: None.
            Remaining risk: None.
            """
        )

        self.assertFalse(review["ok"])
        self.assertTrue(review["forbidden_reviewer"])

    def test_rejects_codex_desk_visual_pass_without_independence_label(self) -> None:
        review = self.parse(
            """
            FINAL_VISUAL_REVIEW: PASS
            Reviewer: Codex visual review desk
            Score: 9.8/10
            P0: 0
            P1: 0
            Checked: cover, unit opener, dense practice, workbook page, handbook
            Contact sheet: _qa/contact-sheet-book-trim.png
            Key pages: _qa/rendered-pages/book-trim-p001.png, _qa/rendered-pages/book-trim-p002.png, _qa/rendered-pages/book-trim-p006.png, _qa/rendered-pages/book-trim-p010.png
            Canon comparison: compared against golden p1, p3, p4, p6, p9.
            Reject patterns checked: thin-cover-type, dashboard-panel, ui-number-block.
            Font decision: B primary, C fallback.
            Visual diagnosis: Publication-grade.
            Weak pages: None.
            Remaining risk: None.
            """
        )

        self.assertFalse(review["ok"])
        self.assertFalse(review["allowed_reviewer"])

    def test_rejects_pass_without_render_evidence(self) -> None:
        review = self.parse(
            """
            FINAL_VISUAL_REVIEW: PASS
            Reviewer: independent-review
            Score: 9.6/10
            P0: 0
            P1: 0
            Checked: cover, unit opener, dense practice, workbook page, handbook
            Visual diagnosis: Publication-grade.
            Weak pages: None.
            Remaining risk: None.
            """
        )

        self.assertFalse(review["ok"])
        self.assertFalse(review["has_render_evidence"])

    def test_rejects_pass_without_canon_transfer_fields(self) -> None:
        review = self.parse(
            """
            FINAL_VISUAL_REVIEW: PASS
            Reviewer: independent-review
            Score: 9.6/10
            P0: 0
            P1: 0
            Checked: cover, unit opener, dense practice, workbook page, handbook
            Contact sheet: _qa/contact-sheet-book-trim.png
            Key pages: _qa/rendered-pages/book-trim-p001.png, _qa/rendered-pages/book-trim-p002.png, _qa/rendered-pages/book-trim-p006.png, _qa/rendered-pages/book-trim-p010.png
            Visual diagnosis: Publication-grade.
            Weak pages: None.
            Remaining risk: None.
            """
        )

        self.assertFalse(review["ok"])
        self.assertFalse(review["has_canon_comparison"])
        self.assertFalse(review["has_reject_patterns"])
        self.assertFalse(review["has_font_decision"])

    def test_accepts_independent_review_with_render_evidence(self) -> None:
        review = self.parse(
            """
            FINAL_VISUAL_REVIEW: PASS
            Reviewer: independent-review
            Score: 9.7/10
            P0: 0
            P1: 0
            Checked: cover, unit opener, dense practice, workbook page, handbook
            Contact sheet: _qa/contact-sheet-book-trim.png
            Key pages: _qa/rendered-pages/book-trim-p001.png, _qa/rendered-pages/book-trim-p002.png, _qa/rendered-pages/book-trim-p006.png, _qa/rendered-pages/book-trim-p010.png
            Canon comparison: compared against golden p1 cover, p3 opener, p4 elements, p6 paragraph practice, p9 handbook.
            Reject patterns checked: thin-cover-type, dashboard-panel, ui-number-block, component-collage, patch-drift, form-repeat.
            Font decision: B modern sans primary; C system clean fallback.
            Visual diagnosis: Cover, opener, practice, writing, and handbook roles are visually distinct.
            Weak pages: None.
            Remaining risk: None.
            """
        )

        self.assertTrue(review["ok"])
        self.assertEqual(review["status"], "PASS")
        self.assertTrue(review["has_render_evidence"])
        self.assertTrue(review["has_canon_comparison"])
        self.assertTrue(review["has_reject_patterns"])
        self.assertTrue(review["has_font_decision"])
        self.assertEqual(review["key_page_count"], 4)

    def test_rejects_review_with_missing_or_wrong_profile_key_page_paths(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eric-pdf-review-paths-") as tmp:
            root = Path(tmp)
            qa = root / "_qa"
            rendered = qa / "rendered-pages"
            rendered.mkdir(parents=True)
            (qa / "contact-sheet-book-trim.png").write_bytes(b"png")
            for page in (1, 2, 6):
                (rendered / f"book-trim-page-{page:03d}.png").write_bytes(b"png")
            (rendered / "lesson-a4-page-010.png").write_bytes(b"png")
            review_path = qa / "visual-review-book-trim.md"
            review_path.write_text(
                """
                FINAL_VISUAL_REVIEW: PASS
                Reviewer: independent-review
                Score: 9.7/10
                P0: 0
                P1: 0
                Checked: cover, unit opener, dense practice, workbook page, handbook
                Contact sheet: _qa/contact-sheet-book-trim.png
                Key pages: _qa/rendered-pages/book-trim-page-001.png, _qa/rendered-pages/book-trim-page-002.png, _qa/rendered-pages/book-trim-page-006.png, _qa/rendered-pages/lesson-a4-page-010.png
                Canon comparison: compared against golden p1 cover, p3 opener, p4 elements, p6 paragraph practice, p9 handbook.
                Reject patterns checked: thin-cover-type, dashboard-panel, ui-number-block, component-collage, patch-drift, form-repeat.
                Font decision: B modern sans primary; C system clean fallback.
                Visual diagnosis: Cover, opener, practice, writing, and handbook roles are visually distinct.
                Weak pages: None.
                Remaining risk: None.
                """.strip()
                + "\n",
                encoding="utf-8",
            )

            review = parse_human_review(review_path, root=root, profile="book-trim")

        self.assertFalse(review["ok"], review)
        self.assertFalse(review["review_paths_ok"])
        self.assertFalse(review["artifact_evidence"]["key_pages_profile_match"])

    def test_accepts_four_digit_rendered_key_page_paths_for_large_books(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eric-pdf-review-large-pages-") as tmp:
            root = Path(tmp)
            qa = root / "_qa"
            rendered = qa / "rendered-pages"
            rendered.mkdir(parents=True)
            (qa / "contact-sheet-teacher-book-trim.png").write_bytes(b"png")
            for page in (998, 999, 1000, 1156):
                (rendered / f"teacher-book-trim-page-{page:03d}.png").write_bytes(b"png")
            review_path = qa / "visual-review-teacher-book-trim.md"
            review_path.write_text(
                """
                FINAL_VISUAL_REVIEW: PASS
                Reviewer: independent-review
                Score: 9.7/10
                P0: 0
                P1: 0
                Checked: cover, unit opener, teacher key, dense practice, handbook
                Contact sheet: _qa/contact-sheet-teacher-book-trim.png
                Key pages: _qa/rendered-pages/teacher-book-trim-page-998.png, _qa/rendered-pages/teacher-book-trim-page-999.png, _qa/rendered-pages/teacher-book-trim-page-1000.png, _qa/rendered-pages/teacher-book-trim-page-1156.png
                Canon comparison: compared against golden p1 cover, p3 opener, p4 elements, p6 paragraph practice, p9 handbook.
                Reject patterns checked: thin-cover-type, dashboard-panel, ui-number-block, component-collage, patch-drift, form-repeat.
                Font decision: B modern sans primary; C system clean fallback.
                Visual diagnosis: Large teacher-book key pages remain inside the rendered evidence set.
                Weak pages: None.
                Remaining risk: None.
                """.strip()
                + "\n",
                encoding="utf-8",
            )

            review = parse_human_review(review_path, root=root, profile="teacher-book-trim")

        self.assertTrue(review["ok"], review)
        self.assertTrue(review["review_paths_ok"])
        self.assertTrue(review["artifact_evidence"]["key_pages_profile_match"])

    def test_rejects_stale_pass_review_older_than_current_render_artifacts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eric-pdf-review-fresh-") as tmp:
            root = Path(tmp)
            qa = root / "_qa"
            rendered = qa / "rendered-pages"
            rendered.mkdir(parents=True)
            contact = qa / "contact-sheet-book-trim.png"
            contact.write_bytes(b"png")
            key_pages = []
            for page in (1, 2, 6, 10):
                key = rendered / f"book-trim-page-{page:03d}.png"
                key.write_bytes(b"png")
                key_pages.append(key)
            review_path = qa / "visual-review-book-trim.md"
            review_path.write_text(
                """
                FINAL_VISUAL_REVIEW: PASS
                Reviewer: independent-review
                Score: 9.7/10
                P0: 0
                P1: 0
                Checked: cover, unit opener, dense practice, workbook page, handbook
                Contact sheet: _qa/contact-sheet-book-trim.png
                Key pages: _qa/rendered-pages/book-trim-page-001.png, _qa/rendered-pages/book-trim-page-002.png, _qa/rendered-pages/book-trim-page-006.png, _qa/rendered-pages/book-trim-page-010.png
                Canon comparison: compared against golden p1 cover, p3 opener, p4 elements, p6 paragraph practice, p9 handbook.
                Reject patterns checked: thin-cover-type, dashboard-panel, ui-number-block, component-collage, patch-drift, form-repeat.
                Font decision: B modern sans primary; C system clean fallback.
                Visual diagnosis: Cover, opener, practice, writing, and handbook roles are visually distinct.
                Weak pages: None.
                Remaining risk: None.
                """.strip()
                + "\n",
                encoding="utf-8",
            )
            import os

            old_time = 1_700_000_000
            new_time = 1_700_000_100
            os.utime(review_path, (old_time, old_time))
            os.utime(contact, (new_time, new_time))
            for key in key_pages:
                os.utime(key, (new_time, new_time))

            review = parse_human_review(review_path, root=root, profile="book-trim")

        self.assertFalse(review["ok"], review)
        self.assertFalse(review["review_paths_ok"])
        self.assertFalse(review["artifact_evidence"]["review_fresh_after_artifacts"])

    def test_parses_formal_fail_as_reviewed_but_not_releasable(self) -> None:
        review = self.parse(
            """
            FINAL_VISUAL_REVIEW: FAIL
            Reviewer: formal-human-visual-review
            Score: 9.1/10
            P0: 0
            P1: 1
            P2: 2
            Checked: cover, navigation, opener, workbook, planner, handbook
            Contact sheet: _qa/contact-sheet-book-trim.png
            Key pages: _qa/rendered-pages/book-trim-p001.png, _qa/rendered-pages/book-trim-p002.png, _qa/rendered-pages/book-trim-p005.png, _qa/rendered-pages/book-trim-p006.png
            Canon comparison: compared against golden p1 cover, p3 opener, p5 workbook, p8 planner, p9 handbook.
            Reject patterns checked: diagnostic-form-drift, patch-drift.
            Font decision: B modern sans primary.
            Visual diagnosis: Inspected and found below release threshold.
            Weak pages: p5, p6.
            Remaining risk: Needs redesign pass.
            """
        )

        self.assertFalse(review["ok"])
        self.assertEqual(review["status"], "FAIL")
        self.assertTrue(review["formal_fail"])
        self.assertEqual(review["score"], 9.1)
        self.assertEqual(review["p1"], 1)
        self.assertTrue(review["has_render_evidence"])


class ReportOutputContractTest(unittest.TestCase):
    def test_release_gate_report_does_not_overwrite_machine_qa_report(self) -> None:
        base_report = {
            "status": "warn",
            "summary": {"counts": {"P0": 0, "P1": 0, "P2": 1, "P3": 0}, "strict_fail_severities": ["P0", "P1"]},
            "issues": [{"severity": "P2", "code": "HUMAN_VISUAL_REVIEW_PENDING", "detail": "pending"}],
            "evidence": {"mode": "machine"},
            "next_action": "Proceed to human visual review before formal handoff.",
        }
        release_report = {
            "status": "fail",
            "summary": {"counts": {"P0": 0, "P1": 1, "P2": 0, "P3": 0}, "strict_fail_severities": ["P0", "P1"]},
            "issues": [{"severity": "P1", "code": "HUMAN_VISUAL_REVIEW_MISSING_OR_FAILED", "detail": "failed"}],
            "evidence": {"mode": "release"},
            "next_action": "Fix blocking issues and rerun the validator.",
        }

        with tempfile.TemporaryDirectory(prefix="eric-pdf-report-paths-") as tmp:
            root = Path(tmp)
            write_reports(root, "book-trim", base_report)
            write_reports(root, "book-trim", release_report, release_gate=True)

            self.assertTrue((root / "_qa" / "textbook-qa-book-trim.json").exists())
            self.assertTrue((root / "_qa" / "textbook-qa-book-trim-release.json").exists())
            self.assertIn('"mode": "machine"', (root / "_qa" / "textbook-qa-book-trim.json").read_text(encoding="utf-8"))
            self.assertIn('"mode": "release"', (root / "_qa" / "textbook-qa-book-trim-release.json").read_text(encoding="utf-8"))


class ValidationCorpusContractTest(unittest.TestCase):
    @requires_private_validation_corpus
    def test_v2_validation_corpus_records_required_real_cases_and_valid_release_pass(self) -> None:
        skill_dir = Path(__file__).resolve().parents[1]
        corpus_path = skill_dir / "references" / "validation-corpus-v2.json"
        self.assertTrue(corpus_path.exists(), "v2 validation corpus ledger must exist")

        corpus = gate_module.load_validation_corpus(corpus_path)
        result = gate_module.validation_corpus_contract(corpus)

        self.assertTrue(result["ok"], result)
        self.assertTrue(result["checks"]["required_cases_present"])
        self.assertGreaterEqual(len(result["machine_clean_real_cases"]), 3)
        self.assertIn("gaokao-final-assets-candidate", result["release_pass_cases"])
        self.assertEqual(result["incorrect_release_pass_cases"], [])
        self.assertFalse(result["checks"]["incorrect_final_release_pass"])
        self.assertIn("level1-form-abstraction", result["case_ids"])
        self.assertIn("gaokao-summer-grammar", result["case_ids"])
        self.assertIn("sample-student-clause-linker", result["case_ids"])
        self.assertIn("sample-learner-ielts-regression", result["case_ids"])


class GenericIdentityAndRhythmTest(unittest.TestCase):
    def test_rejects_final_generic_book_with_functional_title_only(self) -> None:
        result = generic_book_identity_policy(
            {
                "title": "IELTS备考计划",
                "subtitle": "Student workbook and A4 lesson pack",
            },
            asset_mode=ASSET_MODE_FINAL,
            starter_sample=False,
        )

        self.assertFalse(result["ok"], result)
        self.assertFalse(result["checks"]["identity_block_present"])
        self.assertFalse(result["checks"]["cover_title_not_only_functional"])

    def test_rejects_functional_visible_cover_title_even_when_internal_title_is_publishable(self) -> None:
        result = generic_book_identity_policy(
            {
                "title": "Evidence Before Score",
                "subtitle": "IELTS Academic",
                "identity": {
                    "cover_title": "IELTS备考计划",
                    "positioning": "A generic IELTS workbook that turns score anxiety into daily proof.",
                    "audience": "IELTS Academic students",
                    "front_matter_role": "establishes book identity, scope, and practice rhythm",
                },
            },
            asset_mode=ASSET_MODE_FINAL,
            starter_sample=False,
        )

        self.assertFalse(result["ok"], result)
        self.assertIn("备考计划", result["functional_hits"])

    def test_accepts_final_generic_book_with_publishable_identity(self) -> None:
        result = generic_book_identity_policy(
            {
                "title": "Evidence Before Score",
                "subtitle": "IELTS 30-Day Evidence Workbook",
                "identity": {
                    "cover_title": "Evidence Before Score",
                    "positioning": "A generic IELTS workbook that turns score anxiety into daily proof.",
                    "audience": "IELTS Academic students",
                    "front_matter_role": "establishes book identity, scope, and practice rhythm",
                },
            },
            asset_mode=ASSET_MODE_FINAL,
            starter_sample=False,
        )

        self.assertTrue(result["ok"], result)

    def test_configured_answer_visibility_matches_builder_profile_precedence(self) -> None:
        book = {"qa": {"answer_visibility": "student"}}
        spec = {"answer_visibility": "teacher"}

        self.assertEqual(configured_answer_visibility(book, spec), "teacher")

    def test_configured_answer_visibility_infers_student_from_profile_name(self) -> None:
        self.assertEqual(configured_answer_visibility({}, {}, profile="student-book-trim"), "student")
        self.assertEqual(configured_answer_visibility({}, {}, profile="student-lesson-a4"), "student")

    def test_configured_answer_visibility_infers_teacher_from_profile_name(self) -> None:
        self.assertEqual(configured_answer_visibility({}, {}, profile="teacher-book-trim"), "teacher")

    def test_student_profile_inference_keeps_answer_key_gate_enabled(self) -> None:
        mode = configured_answer_visibility({}, {}, profile="student-book-trim")
        result = qa_module.answer_visibility_policy(
            BeautifulSoup(
                """
                <section class="sheet" data-template="teacher-answer-key">
                  <main data-component="answer-key-page" data-teacher-only="true"></main>
                </section>
                """,
                "html.parser",
            ),
            mode=mode,
        )

        self.assertFalse(result["ok"], result)
        self.assertEqual(result["mode"], "student")

    def test_rendered_artifact_freshness_rejects_pngs_older_than_current_pdf(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eric-pdf-render-fresh-") as tmp:
            root = Path(tmp)
            html = root / "book.html"
            pdf = root / "book.pdf"
            contact = root / "contact.png"
            page = root / "book-trim-page-001.png"
            for path in (html, pdf, contact, page):
                path.write_bytes(b"x")
            old_time = 1_700_000_000
            new_time = 1_700_000_100
            import os

            os.utime(html, (new_time, new_time))
            os.utime(pdf, (new_time, new_time))
            os.utime(contact, (new_time, new_time))
            os.utime(page, (old_time, old_time))

            result = rendered_artifact_freshness_checks([page], html_path=html, pdf_path=pdf, contact_path=contact)

        self.assertFalse(result["ok"], result)
        self.assertEqual(result["stale_rendered_count"], 1)

    def test_source_output_freshness_rejects_pdf_older_than_source_page(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eric-pdf-source-fresh-") as tmp:
            root = Path(tmp)
            (root / "pages").mkdir()
            (root / "outputs").mkdir()
            (root / "book.yaml").write_text("title: Sample\n", encoding="utf-8")
            page = root / "pages" / "001-cover.md"
            page.write_text("---\ntemplate: cover\n---\n", encoding="utf-8")
            html = root / "outputs" / "book.html"
            pdf = root / "outputs" / "book.pdf"
            html.write_bytes(b"html")
            pdf.write_bytes(b"pdf")
            import os

            old_time = 1_700_000_000
            new_time = 1_700_000_100
            os.utime(html, (old_time, old_time))
            os.utime(pdf, (old_time, old_time))
            os.utime(page, (new_time, new_time))

            result = source_output_freshness_checks(root, html_path=html, pdf_path=pdf)

        self.assertFalse(result["ok"], result)
        self.assertEqual(sorted(result["stale_outputs"]), ["html", "pdf"])

    def test_configured_upstream_source_inputs_reject_stale_outputs(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eric-pdf-upstream-fresh-") as tmp:
            root = Path(tmp) / "project"
            upstream = Path(tmp) / "external" / "outputs" / "course"
            root.mkdir()
            upstream.mkdir(parents=True)
            (root / "outputs").mkdir()
            (root / "book.yaml").write_text("title: Sample\n", encoding="utf-8")
            source = upstream / "lesson_plan.json"
            source.write_text('{"lesson": 1}\n', encoding="utf-8")
            html = root / "outputs" / "book.html"
            pdf = root / "outputs" / "book.pdf"
            html.write_bytes(b"html")
            pdf.write_bytes(b"pdf")
            import os

            old_time = 1_700_000_000
            new_time = 1_700_000_100
            os.utime(html, (old_time, old_time))
            os.utime(pdf, (old_time, old_time))
            os.utime(source, (new_time, new_time))

            inputs = [str(upstream / "*.json")]
            resolved = configured_source_input_paths(root, inputs)
            result = source_output_freshness_checks(
                root,
                html_path=html,
                pdf_path=pdf,
                configured_inputs=inputs,
            )

        self.assertEqual(resolved, [source.resolve()])
        self.assertFalse(result["ok"], result)
        self.assertEqual(result["configured_source_count"], 1)
        self.assertEqual(sorted(result["stale_outputs"]), ["html", "pdf"])

    def test_page_role_rhythm_flags_long_form_run(self) -> None:
        pages = [{"template": "cover"}] + [{"template": "writing-planner"} for _ in range(23)] + [{"template": "handbook"}]
        result = page_role_rhythm_policy(pages, page_family_mode="v2-full", asset_mode=ASSET_MODE_FINAL)

        self.assertFalse(result["ok"], result)
        self.assertGreater(result["max_form_run"], result["warning_threshold"])

    def test_page_role_rhythm_accepts_editorial_anchors(self) -> None:
        templates = [
            "cover",
            "title",
            "contents-route",
            "diagnostic-entry",
            "unit-opener",
            "skill-method",
            "sentence-map",
            "activity",
            "article-evidence",
            "writing-planner",
            "final-check",
            "handbook",
            "unit-opener",
            "article-opener",
            "skill-method",
            "categorizing-chart",
            "exam-mini-set",
            "photo-passage",
            "correction-rewrite",
            "final-check",
            "handbook",
            "vocab-bank",
            "connector-index",
            "answer-key",
        ]
        result = page_role_rhythm_policy(
            [{"template": template} for template in templates],
            page_family_mode="v2-full",
            asset_mode=ASSET_MODE_FINAL,
        )

        self.assertTrue(result["ok"], result)

    def test_page_role_variant_policy_flags_missing_and_dense_variants(self) -> None:
        pages = [{"template": "cover"}]
        pages += [{"template": "writing-planner", "variant": ""} for _ in range(4)]
        pages += [{"template": "final-check", "variant": "same-final"} for _ in range(4)]
        pages += [{"template": "activity"} for _ in range(45)]

        result = page_role_variant_policy(pages, page_family_mode="v2-full", asset_mode=ASSET_MODE_FINAL)

        self.assertFalse(result["ok"], result)
        self.assertGreaterEqual(len(result["missing_variant_pages"]), 4)
        self.assertTrue(result["dense_variant_windows"], result)

    def test_page_role_variant_policy_accepts_distinct_long_book_roles(self) -> None:
        pages = [{"template": "cover"}]
        pages += [
            {"template": "writing-planner", "variant": "book-roadmap-planner"},
            {"template": "writing-planner", "variant": "daily-practice-schedule"},
            {"template": "writing-planner", "variant": "task2-answer-sheet-practice-1"},
            {"template": "writing-planner", "variant": "task2-answer-sheet-practice-2"},
            {"template": "final-check", "variant": "weekend-mock-review"},
            {"template": "final-check", "variant": "listening-part-1-replay"},
            {"template": "final-check", "variant": "listening-part-2-replay"},
            {"template": "final-check", "variant": "reading-passage-1-evidence-close"},
        ]
        pages += [{"template": "activity"} for _ in range(45)]

        result = page_role_variant_policy(pages, page_family_mode="v2-full", asset_mode=ASSET_MODE_FINAL)

        self.assertTrue(result["ok"], result)

    def test_page_structure_variant_library_flags_repeated_plain_activity_family(self) -> None:
        pages = [{"template": "cover"}]
        pages += [{"template": "activity", "variant": ""} for _ in range(8)]
        pages += [{"template": "skill-method", "variant": "same-method"} for _ in range(4)]
        pages += [{"template": "handbook", "variant": "lookup-index"} for _ in range(2)]
        pages += [{"template": "photo-passage"} for _ in range(40)]

        result = page_structure_variant_library_policy(
            pages,
            page_family_mode="v2-full",
            asset_mode=ASSET_MODE_FINAL,
        )

        self.assertFalse(result["ok"], result)
        self.assertTrue(result["weak_template_groups"], result)
        self.assertGreaterEqual(len(result["missing_variant_pages"]), 8)

    def test_page_structure_variant_library_flags_three_plain_handbook_pages(self) -> None:
        pages = [{"template": "cover"}]
        pages += [{"template": "handbook", "variant": ""} for _ in range(3)]
        pages += [{"template": "photo-passage"} for _ in range(47)]

        result = page_structure_variant_library_policy(
            pages,
            page_family_mode="v2-full",
            asset_mode=ASSET_MODE_FINAL,
        )

        self.assertFalse(result["ok"], result)
        self.assertEqual(result["weak_template_groups"][0]["template"], "handbook")

    def test_page_structure_variant_library_normalizes_numbered_same_shell_variants(self) -> None:
        pages = [{"template": "cover"}]
        pages += [
            {"template": "writing-planner", "variant": "task2-answer-sheet-practice-1"},
            {"template": "writing-planner", "variant": "task2-answer-sheet-practice-2"},
            {"template": "writing-planner", "variant": "task2-answer-sheet-practice-3"},
            {"template": "writing-planner", "variant": "task2-answer-sheet-practice-4"},
        ]
        pages += [{"template": "photo-passage"} for _ in range(50)]

        result = page_structure_variant_library_policy(
            pages,
            page_family_mode="v2-full",
            asset_mode=ASSET_MODE_FINAL,
        )

        self.assertFalse(result["ok"], result)
        self.assertEqual(
            result["template_variant_counts"]["writing-planner"],
            {"task2-answer-sheet": 4},
        )
        self.assertTrue(result["metadata_only_surface_pages"], result)

    def test_page_structure_variant_library_rejects_metadata_only_rendered_surfaces(self) -> None:
        pages = [{"template": "cover"}]
        pages += [
            {"template": "writing-planner", "variant": "task2-agree-disagree-answer-ladder"},
            {"template": "writing-planner", "variant": "task2-discussion-two-view-bridge"},
            {"template": "writing-planner", "variant": "task2-problem-solution-matrix"},
            {"template": "writing-planner", "variant": "task2-advantage-balance-scale"},
        ]
        pages += [{"template": "photo-passage"} for _ in range(50)]

        result = page_structure_variant_library_policy(
            pages,
            page_family_mode="v2-full",
            asset_mode=ASSET_MODE_FINAL,
        )

        self.assertFalse(result["ok"], result)
        self.assertEqual(len(result["metadata_only_surface_pages"]), 4)

    def test_page_structure_variant_library_accepts_distinct_rendered_surfaces(self) -> None:
        pages = [{"template": "cover"}]
        pages += [
            {
                "template": "writing-planner",
                "variant": "task2-practice-1",
                "surface": "task2-agree-disagree-answer-ladder",
                "surface_family": "task2-writing",
            },
            {
                "template": "writing-planner",
                "variant": "task2-practice-2",
                "surface": "task2-discussion-two-view-bridge",
                "surface_family": "task2-writing",
            },
            {
                "template": "writing-planner",
                "variant": "task2-practice-3",
                "surface": "task2-problem-solution-matrix",
                "surface_family": "task2-writing",
            },
            {
                "template": "writing-planner",
                "variant": "task2-practice-4",
                "surface": "task2-advantage-balance-scale",
                "surface_family": "task2-writing",
            },
        ]
        pages += [{"template": "photo-passage"} for _ in range(50)]

        result = page_structure_variant_library_policy(
            pages,
            page_family_mode="v2-full",
            asset_mode=ASSET_MODE_FINAL,
        )

        self.assertTrue(result["ok"], result)
        self.assertEqual(
            result["template_surface_counts"]["writing-planner"],
            {
                "task2-writing:task2-agree-disagree-answer-ladder": 1,
                "task2-writing:task2-discussion-two-view-bridge": 1,
                "task2-writing:task2-problem-solution-matrix": 1,
                "task2-writing:task2-advantage-balance-scale": 1,
            },
        )

    def test_page_structure_variant_library_rejects_surface_without_family(self) -> None:
        pages = [{"template": "cover"}]
        pages += [
            {
                "template": "writing-planner",
                "variant": "task2-practice-1",
                "surface": "task2-agree-disagree-answer-ladder",
            },
            {
                "template": "writing-planner",
                "variant": "task2-practice-2",
                "surface": "task2-discussion-two-view-bridge",
            },
            {
                "template": "writing-planner",
                "variant": "task2-practice-3",
                "surface": "task2-problem-solution-matrix",
            },
            {
                "template": "writing-planner",
                "variant": "task2-practice-4",
                "surface": "task2-advantage-balance-scale",
            },
        ]
        pages += [{"template": "photo-passage"} for _ in range(50)]

        result = page_structure_variant_library_policy(
            pages,
            page_family_mode="v2-full",
            asset_mode=ASSET_MODE_FINAL,
        )

        self.assertFalse(result["ok"], result)
        self.assertEqual(len(result["missing_surface_family_pages"]), 4)

    def test_rendered_page_records_extracts_inner_surface_marker(self) -> None:
        soup = BeautifulSoup(
            """
            <section class="sheet" data-page="23" data-template="writing-planner" data-variant="task2-practice-1">
              <main data-surface-family="task2-writing" data-surface="task2-agree-disagree-answer-ladder"></main>
            </section>
            """,
            "html.parser",
        )

        records = rendered_page_records(soup)

        self.assertEqual(records[0]["surface"], "task2-agree-disagree-answer-ladder")
        self.assertEqual(records[0]["surface_family"], "task2-writing")

    def test_page_structure_variant_library_accepts_declared_optional_structures(self) -> None:
        pages = [{"template": "cover"}]
        pages += [
            {"template": "activity", "variant": "word-box-controlled-practice"},
            {"template": "activity", "variant": "evidence-choice-practice"},
            {"template": "activity", "variant": "sentence-repair-practice"},
            {"template": "activity", "variant": "timed-transfer-practice"},
            {"template": "skill-method", "variant": "rule-table-method"},
            {"template": "skill-method", "variant": "worked-example-method"},
            {"template": "skill-method", "variant": "guided-discovery-method"},
            {"template": "skill-method", "variant": "contrast-cue-method"},
        ]
        pages += [{"template": "photo-passage"} for _ in range(45)]

        result = page_structure_variant_library_policy(
            pages,
            page_family_mode="v2-full",
            asset_mode=ASSET_MODE_FINAL,
        )

        self.assertTrue(result["ok"], result)

    def test_validation_corpus_contract_rejects_fake_release_pass(self) -> None:
        corpus = {
            "minimum_machine_clean_real_cases": 1,
            "required_real_case_ids": ["fake-pass"],
            "cases": [
                {
                    "id": "fake-pass",
                    "family": "unit-test",
                    "real_material": True,
                    "status": "release_pass",
                    "release_status": "pass",
                    "project_path": "/tmp/fake-pass",
                    "profiles": ["book-trim", "lesson-a4"],
                    "asset_mode": "final-assets",
                    "machine_gate": {"P0": 0, "P1": 0, "P2": 0, "P3": 0},
                    "visual_review": {
                        "status": "PASS",
                        "score": {"book-trim": 9.7, "lesson-a4": 9.6},
                        "reviewer": "same-agent-internal-review",
                        "P0": 0,
                        "P1": 0,
                        "release_eligible": True,
                    },
                    "source_boundary": "unit test",
                    "evidence": {
                        "book_trim_pdf": "outputs/book.pdf",
                        "lesson_a4_pdf": "outputs/a4.pdf",
                        "book_trim_contact_sheet": "_qa/contact-sheet-book-trim.png",
                        "lesson_a4_contact_sheet": "_qa/contact-sheet-lesson-a4.png",
                        "book_trim_qa": "_qa/textbook-qa-book-trim.json",
                        "lesson_a4_qa": "_qa/textbook-qa-lesson-a4.json",
                        "book_trim_release_qa": "_qa/textbook-qa-book-trim-release.json",
                        "lesson_a4_release_qa": "_qa/textbook-qa-lesson-a4-release.json",
                        "book_trim_visual_review": "_qa/visual-review-book-trim.md",
                        "lesson_a4_visual_review": "_qa/visual-review-lesson-a4.md",
                    },
                    "known_gaps": [],
                    "next_action": "unit test",
                }
            ],
        }

        result = gate_module.validation_corpus_contract(corpus)

        self.assertFalse(result["ok"], result)
        self.assertEqual(result["incorrect_release_pass_cases"], ["fake-pass"])

    @requires_private_validation_corpus
    def test_v2_validation_corpus_matches_real_project_evidence_and_qa_json(self) -> None:
        skill_dir = Path(__file__).resolve().parents[1]
        corpus_path = skill_dir / "references" / "validation-corpus-v2.json"
        corpus = gate_module.load_validation_corpus(corpus_path)

        result = gate_module.validation_corpus_evidence_contract(corpus)

        self.assertTrue(result["ok"], result)
        self.assertEqual(result["missing_project_paths"], [])
        self.assertEqual(result["missing_evidence_files"], [])
        self.assertEqual(result["qa_mismatches"], [])
        self.assertGreaterEqual(len(result["machine_clean_real_cases_from_reports"]), 3)

    def test_validation_corpus_evidence_contract_allows_explicit_superseded_archive(self) -> None:
        corpus = {
            "minimum_machine_clean_real_cases": 0,
            "required_real_case_ids": ["old-case"],
            "cases": [
                {
                    "id": "old-case",
                    "family": "unit-test",
                    "real_material": True,
                    "status": "superseded_archive",
                    "release_status": "superseded",
                    "evidence_policy": "superseded_archive",
                    "project_path": "/tmp/eric-designed-pdf-definitely-missing-old-case",
                    "profiles": ["book-trim", "lesson-a4"],
                    "asset_mode": "final-assets",
                    "page_family_mode": "v2-full",
                    "machine_gate": {"P0": 0, "P1": 0, "P2": 0, "P3": 0},
                    "visual_review": {"status": "PASS", "score": 9.6, "reviewer": "user-confirmed", "release_eligible": True},
                    "source_boundary": "superseded by a newer release root; preserved for history only",
                    "evidence": {
                        "book_trim_pdf": "outputs/old-book.pdf",
                        "lesson_a4_pdf": "outputs/old-a4.pdf",
                        "book_trim_contact_sheet": "_qa/contact-sheet-book-trim.png",
                        "lesson_a4_contact_sheet": "_qa/contact-sheet-lesson-a4.png",
                        "book_trim_qa": "_qa/textbook-qa-book-trim.json",
                        "lesson_a4_qa": "_qa/textbook-qa-lesson-a4.json",
                        "book_trim_visual_review": "_qa/visual-review-book-trim.md",
                        "lesson_a4_visual_review": "_qa/visual-review-lesson-a4.md",
                    },
                    "known_gaps": ["project archive was intentionally removed from active storage"],
                    "next_action": "use newer release evidence instead of this superseded case",
                }
            ],
        }

        result = gate_module.validation_corpus_evidence_contract(corpus)

        self.assertTrue(result["ok"], result)
        self.assertEqual(result["missing_project_paths"], [])
        self.assertEqual(result["skipped_superseded_cases"], ["old-case"])
        self.assertEqual(result["machine_clean_real_cases_from_reports"], [])

        contract = gate_module.validation_corpus_contract(corpus)

        self.assertEqual(contract["machine_clean_real_cases"], [])
        self.assertEqual(contract["release_pass_cases"], [])

    def test_validation_corpus_evidence_contract_rejects_stale_machine_gate_counts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eric-pdf-corpus-evidence-") as tmp:
            project = Path(tmp) / "case"
            (project / "_qa").mkdir(parents=True)
            (project / "outputs").mkdir()
            for rel in [
                "outputs/book.pdf",
                "outputs/a4.pdf",
                "_qa/contact-sheet-book-trim.png",
                "_qa/contact-sheet-lesson-a4.png",
                "_qa/visual-review-book-trim.md",
                "_qa/visual-review-lesson-a4.md",
            ]:
                (project / rel).write_text("x", encoding="utf-8")
            qa_payload = {
                "summary": {"counts": {"P0": 0, "P1": 1, "P2": 0, "P3": 0}},
                "evidence": {
                    "qa_config": {"asset_mode": "final-assets", "page_family_mode": "v2-full"},
                    "pdf": "outputs/book.pdf",
                    "contact_sheet": "_qa/contact-sheet-book-trim.png",
                    "human_visual_review": {"status": "FAIL", "score": 9.0, "reviewer": "same-agent-internal-review"},
                },
            }
            (project / "_qa" / "textbook-qa-book-trim.json").write_text(json.dumps(qa_payload), encoding="utf-8")
            qa_payload["evidence"]["pdf"] = "outputs/a4.pdf"
            qa_payload["evidence"]["contact_sheet"] = "_qa/contact-sheet-lesson-a4.png"
            (project / "_qa" / "textbook-qa-lesson-a4.json").write_text(json.dumps(qa_payload), encoding="utf-8")

            corpus = {
                "minimum_machine_clean_real_cases": 1,
                "required_real_case_ids": ["stale-case"],
                "cases": [
                    {
                        "id": "stale-case",
                        "family": "unit-test",
                        "real_material": True,
                        "status": "machine_clean_visual_pending",
                        "release_status": "not_release",
                        "project_path": str(project),
                        "profiles": ["book-trim", "lesson-a4"],
                        "asset_mode": "final-assets",
                        "page_family_mode": "v2-full",
                        "machine_gate": {"P0": 0, "P1": 0, "P2": 0, "P3": 0},
                        "visual_review": {"status": "FAIL", "score": 9.0, "reviewer": "same-agent-internal-review", "release_eligible": False},
                        "source_boundary": "unit test",
                        "evidence": {
                            "book_trim_pdf": "outputs/book.pdf",
                            "lesson_a4_pdf": "outputs/a4.pdf",
                            "book_trim_contact_sheet": "_qa/contact-sheet-book-trim.png",
                            "lesson_a4_contact_sheet": "_qa/contact-sheet-lesson-a4.png",
                            "book_trim_qa": "_qa/textbook-qa-book-trim.json",
                            "lesson_a4_qa": "_qa/textbook-qa-lesson-a4.json",
                            "book_trim_visual_review": "_qa/visual-review-book-trim.md",
                            "lesson_a4_visual_review": "_qa/visual-review-lesson-a4.md",
                        },
                        "known_gaps": ["unit test"],
                        "next_action": "unit test",
                    }
                ],
            }

            result = gate_module.validation_corpus_evidence_contract(corpus)

        self.assertFalse(result["ok"], result)
        self.assertIn("stale-case", result["qa_mismatches"][0]["case"])

    def test_validation_corpus_evidence_contract_rejects_stale_rendered_page_files(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eric-pdf-corpus-rendered-pages-") as tmp:
            project = Path(tmp) / "case"
            (project / "_qa" / "rendered-pages").mkdir(parents=True)
            (project / "outputs").mkdir()
            for rel in [
                "outputs/book.pdf",
                "outputs/a4.pdf",
                "_qa/contact-sheet-book-trim.png",
                "_qa/contact-sheet-lesson-a4.png",
                "_qa/visual-review-book-trim.md",
                "_qa/visual-review-lesson-a4.md",
                "_qa/rendered-pages/book-trim-page-001.png",
                "_qa/rendered-pages/book-trim-page-002.png",
                "_qa/rendered-pages/book-trim-page-002 2.png",
                "_qa/rendered-pages/lesson-a4-page-001.png",
                "_qa/rendered-pages/lesson-a4-page-002.png",
                "_qa/rendered-pages/lesson-a4-page-002 2.png",
            ]:
                (project / rel).write_text("x", encoding="utf-8")
            qa_payload = {
                "summary": {"counts": {"P0": 0, "P1": 0, "P2": 0, "P3": 0}},
                "evidence": {
                    "qa_config": {"asset_mode": "final-assets", "page_family_mode": "v2-full"},
                    "pdf": "outputs/book.pdf",
                    "contact_sheet": "_qa/contact-sheet-book-trim.png",
                    "page_count": 2,
                    "rendered_pages": {"count": 2, "expected": 2},
                    "human_visual_review": {"status": "FAIL", "score": 9.0, "reviewer": "same-agent-internal-review"},
                },
            }
            (project / "_qa" / "textbook-qa-book-trim.json").write_text(json.dumps(qa_payload), encoding="utf-8")
            qa_payload["evidence"]["pdf"] = "outputs/a4.pdf"
            qa_payload["evidence"]["contact_sheet"] = "_qa/contact-sheet-lesson-a4.png"
            (project / "_qa" / "textbook-qa-lesson-a4.json").write_text(json.dumps(qa_payload), encoding="utf-8")

            corpus = {
                "minimum_machine_clean_real_cases": 1,
                "required_real_case_ids": ["stale-render-case"],
                "cases": [
                    {
                        "id": "stale-render-case",
                        "family": "unit-test",
                        "real_material": True,
                        "status": "machine_clean_visual_pending",
                        "release_status": "not_release",
                        "project_path": str(project),
                        "profiles": ["book-trim", "lesson-a4"],
                        "asset_mode": "final-assets",
                        "page_family_mode": "v2-full",
                        "machine_gate": {"P0": 0, "P1": 0, "P2": 0, "P3": 0},
                        "visual_review": {"status": "FAIL", "score": 9.0, "reviewer": "same-agent-internal-review", "release_eligible": False},
                        "source_boundary": "unit test",
                        "evidence": {
                            "book_trim_pdf": "outputs/book.pdf",
                            "lesson_a4_pdf": "outputs/a4.pdf",
                            "book_trim_contact_sheet": "_qa/contact-sheet-book-trim.png",
                            "lesson_a4_contact_sheet": "_qa/contact-sheet-lesson-a4.png",
                            "book_trim_qa": "_qa/textbook-qa-book-trim.json",
                            "lesson_a4_qa": "_qa/textbook-qa-lesson-a4.json",
                            "book_trim_visual_review": "_qa/visual-review-book-trim.md",
                            "lesson_a4_visual_review": "_qa/visual-review-lesson-a4.md",
                        },
                        "known_gaps": ["unit test"],
                        "next_action": "unit test",
                    }
                ],
            }

            result = gate_module.validation_corpus_evidence_contract(corpus)

        self.assertFalse(result["ok"], result)
        self.assertEqual(result["stale_rendered_page_files"][0]["case"], "stale-render-case")
        self.assertEqual(result["stale_rendered_page_files"][0]["actual"], 2)
        self.assertIn("book-trim-page-002 2.png", result["stale_rendered_page_files"][0]["filename_checks"]["conflict_files"])


class StarterResidueContractTest(unittest.TestCase):
    def test_flags_starter_identity_in_custom_project_source(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eric-pdf-residue-") as tmp:
            root = Path(tmp)
            (root / "tools").mkdir()
            (root / "pages").mkdir()
            (root / "tools" / "build.py").write_text("series = 'English Writing System'\n", encoding="utf-8")
            (root / "pages" / "01-cover.md").write_text("title: IELTS备考计划 for Sample Learner\n", encoding="utf-8")

            hits = starter_residue_hits(root, {"title": "IELTS备考计划 for Sample Learner"}, {}, "", "")

        self.assertIn("English Writing System", hits)
        self.assertEqual(hits["English Writing System"]["locations"][0]["file"], "tools/build.py")

    def test_allows_starter_identity_for_the_starter_sample(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eric-pdf-residue-") as tmp:
            root = Path(tmp)
            (root / "tools").mkdir()
            (root / "tools" / "build.py").write_text("series = 'English Writing System'\n", encoding="utf-8")

            hits = starter_residue_hits(root, {"title": STARTER_SAMPLE_TITLE}, {}, "", "")

        self.assertEqual(hits, {})


class CoverBrandContractTest(unittest.TestCase):
    def test_accepts_studio_brand_at_bottom_right_without_cover_level_badge(self) -> None:
        result = cover_brand_checks(
            """
            <style>
            .cover-brand { position: absolute; right: 39pt; bottom: 40pt; background: rgba(8,42,48,.62); text-shadow: 0 1pt 2pt rgba(0,0,0,.42); }
            </style>
            <section class="sheet template-cover" data-template="cover">
              <div class="cover-top"><span>Grammar Transition</span></div>
              <div class="cover-brand"><b>Eric Teaching Studio</b><span>Student Book</span></div>
            </section>
            """,
            {"level": "高二升高三"},
        )

        self.assertTrue(result["ok"], result)

    def test_rejects_course_stage_on_cover_top(self) -> None:
        result = cover_brand_checks(
            """
            <style>
            .cover-brand { position: absolute; right: 39pt; bottom: 40pt; background: rgba(8,42,48,.62); text-shadow: 0 1pt 2pt rgba(0,0,0,.42); }
            </style>
            <section class="sheet template-cover" data-template="cover">
              <div class="cover-top"><span>Grammar Transition</span><b>高二升高三</b></div>
              <div class="cover-brand"><b>Eric Teaching Studio</b></div>
            </section>
            """,
            {"level": "高二升高三"},
        )

        self.assertFalse(result["ok"], result)
        self.assertFalse(result["checks"]["cover_top_level_badge_absent"])

    def test_rejects_cover_brand_without_photo_contrast_treatment(self) -> None:
        result = cover_brand_checks(
            """
            <style>
            .cover-brand { position: absolute; right: 39pt; bottom: 40pt; color: #184b54; }
            </style>
            <section class="sheet template-cover" data-template="cover">
              <div class="cover-top"><span>Grammar Transition</span></div>
              <div class="cover-brand"><b>Eric Teaching Studio</b><span>Student Book</span></div>
            </section>
            """,
            {"level": "高二升高三"},
        )

        self.assertFalse(result["ok"], result)
        self.assertFalse(result["checks"]["brand_contrast_css"])


class AssetPolicyContractTest(unittest.TestCase):
    def test_accepts_single_use_visual_assets_with_allowed_templates(self) -> None:
        result = asset_usage_policy(
            [
                {"id": "unit-cover", "path": "assets/generated/unit-cover.png", "role": "cover_hero", "allowed_templates": ["cover"]},
                {"id": "unit-opener", "path": "assets/generated/unit-opener.png", "role": "unit_opener", "allowed_templates": ["unit-opener"]},
                {"id": "unit-passage", "path": "assets/generated/unit-passage.png", "role": "photo_passage", "allowed_templates": ["photo-passage"]},
            ],
            [
                {"id": "unit-cover", "page": "pages/01-cover.md", "template": "cover", "section": "front"},
                {"id": "unit-opener", "page": "pages/03-unit-opener.md", "template": "unit-opener", "section": "unit"},
                {"id": "unit-passage", "page": "pages/07-photo-passage.md", "template": "photo-passage", "section": "unit"},
            ],
        )

        self.assertTrue(result["ok"], result)

    def test_rejects_cover_asset_reused_inside_book(self) -> None:
        result = asset_usage_policy(
            [
                {"id": "clause-cover", "path": "assets/generated/clause-cover.png", "role": "cover_hero"},
            ],
            [
                {"id": "clause-cover", "page": "pages/01-cover.md", "template": "cover", "section": "front"},
                {"id": "clause-cover", "page": "pages/03-unit-opener.md", "template": "unit-opener", "section": "unit"},
            ],
        )

        self.assertFalse(result["ok"], result)
        self.assertFalse(result["checks"]["asset_refs_single_use"])
        self.assertFalse(result["checks"]["cover_assets_not_used_inside"])

    def test_rejects_two_asset_ids_using_same_image_path(self) -> None:
        result = asset_usage_policy(
            [
                {"id": "cover-a", "path": "assets/generated/shared.png", "role": "cover_hero"},
                {"id": "opener-a", "path": "assets/generated/shared.png", "role": "unit_opener"},
            ],
            [
                {"id": "cover-a", "page": "pages/01-cover.md", "template": "cover", "section": "front"},
                {"id": "opener-a", "page": "pages/03-unit-opener.md", "template": "unit-opener", "section": "unit"},
            ],
        )

        self.assertFalse(result["ok"], result)
        self.assertFalse(result["checks"]["manifest_paths_unique"])


class AnswerVisibilityContractTest(unittest.TestCase):
    def policy(self, html: str, mode: str) -> dict:
        self.assertTrue(
            hasattr(qa_module, "answer_visibility_policy"),
            "qa_textbook_pdf must expose answer_visibility_policy",
        )
        soup = BeautifulSoup(html, "html.parser")
        return qa_module.answer_visibility_policy(soup, mode=mode)

    def test_student_profile_rejects_answer_key_and_teacher_key_pages(self) -> None:
        result = self.policy(
            """
            <section class="sheet" data-template="activity"></section>
            <section class="sheet" data-template="answer-key">
              <main data-component="answer-key-page"></main>
            </section>
            <section class="sheet" data-template="teacher-answer-key">
              <main data-component="answer-key-page" data-teacher-only="true"></main>
            </section>
            """,
            mode="student",
        )

        self.assertFalse(result["ok"], result)
        self.assertIn("answer-key", result["blocked_templates"])
        self.assertIn("teacher-answer-key", result["blocked_templates"])
        self.assertEqual(result["teacher_only_nodes"], 1)

    def test_student_with_answer_key_allows_student_key_but_rejects_teacher_only(self) -> None:
        result = self.policy(
            """
            <section class="sheet" data-template="answer-key">
              <main data-component="answer-key-page"></main>
            </section>
            <section class="sheet" data-template="teacher-answer-key">
              <main data-component="answer-key-page" data-teacher-only="true"></main>
            </section>
            """,
            mode="student-with-answer-key",
        )

        self.assertFalse(result["ok"], result)
        self.assertNotIn("answer-key", result["blocked_templates"])
        self.assertIn("teacher-answer-key", result["blocked_templates"])

    def test_teacher_profile_allows_teacher_key_pages(self) -> None:
        result = self.policy(
            """
            <section class="sheet" data-template="teacher-answer-key">
              <main data-component="answer-key-page" data-teacher-only="true"></main>
            </section>
            """,
            mode="teacher",
        )

        self.assertTrue(result["ok"], result)


class V2PageFamilyCoverageContractTest(unittest.TestCase):
    def test_accepts_full_v2_page_family_matrix(self) -> None:
        result = page_family_coverage_policy(
            [
                {"template": "cover"},
                {"template": "contents-route"},
                {"template": "diagnostic-entry"},
                {"template": "unit-opener"},
                {"template": "article-opener"},
                {"template": "article-evidence"},
                {"template": "skill-method"},
                {"template": "sentence-map"},
                {"template": "activity"},
                {"template": "categorizing-chart"},
                {"template": "exam-mini-set"},
                {"template": "photo-passage"},
                {"template": "correction-rewrite"},
                {"template": "writing-planner"},
                {"template": "final-check"},
                {"template": "handbook"},
                {"template": "vocab-bank"},
                {"template": "teacher-answer-key"},
            ],
            mode="v2-full",
        )

        self.assertTrue(result["ok"], result)
        self.assertEqual(result["missing_families"], [])

    def test_accepts_student_answer_key_as_backmatter_key(self) -> None:
        result = page_family_coverage_policy(
            [
                {"template": "cover"},
                {"template": "contents-route"},
                {"template": "diagnostic-entry"},
                {"template": "unit-opener"},
                {"template": "article-opener"},
                {"template": "article-evidence"},
                {"template": "skill-method"},
                {"template": "sentence-map"},
                {"template": "activity"},
                {"template": "categorizing-chart"},
                {"template": "exam-mini-set"},
                {"template": "photo-passage"},
                {"template": "correction-rewrite"},
                {"template": "writing-planner"},
                {"template": "final-check"},
                {"template": "handbook"},
                {"template": "vocab-bank"},
                {"template": "answer-key"},
            ],
            mode="v2-full",
        )

        self.assertTrue(result["ok"], result)
        self.assertEqual(result["missing_families"], [])

    def test_student_book_mode_checks_v2_families_without_requiring_answer_key(self) -> None:
        result = page_family_coverage_policy(
            [
                {"template": "cover"},
                {"template": "contents-route"},
                {"template": "diagnostic-entry"},
                {"template": "unit-opener"},
                {"template": "article-opener"},
                {"template": "article-evidence"},
                {"template": "skill-method"},
                {"template": "sentence-map"},
                {"template": "activity"},
                {"template": "categorizing-chart"},
                {"template": "exam-mini-set"},
                {"template": "photo-passage"},
                {"template": "correction-rewrite"},
                {"template": "writing-planner"},
                {"template": "final-check"},
                {"template": "handbook"},
                {"template": "vocab-bank"},
            ],
            mode="student-book",
            answer_visibility="student",
        )

        self.assertTrue(result["checked"], result)
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["missing_families"], [])

    def test_student_book_mode_accepts_paragraph_practice_as_writing_output_surface(self) -> None:
        result = page_family_coverage_policy(
            [
                {"template": "cover"},
                {"template": "contents-route"},
                {"template": "diagnostic-entry"},
                {"template": "unit-opener"},
                {"template": "article-opener"},
                {"template": "article-evidence"},
                {"template": "skill-method"},
                {"template": "sentence-map"},
                {"template": "activity"},
                {"template": "categorizing-chart"},
                {"template": "exam-mini-set"},
                {"template": "photo-passage"},
                {"template": "paragraph-practice"},
                {"template": "writing-planner"},
                {"template": "final-check"},
                {"template": "handbook"},
                {"template": "vocab-bank"},
            ],
            mode="student-book",
            answer_visibility="student",
        )

        self.assertTrue(result["checked"], result)
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["missing_families"], [])

    def test_teacher_book_mode_checks_v2_families_and_requires_key_backmatter(self) -> None:
        result = page_family_coverage_policy(
            [
                {"template": "cover"},
                {"template": "contents-route"},
                {"template": "diagnostic-entry"},
                {"template": "unit-opener"},
                {"template": "article-opener"},
                {"template": "article-evidence"},
                {"template": "skill-method"},
                {"template": "sentence-map"},
                {"template": "activity"},
                {"template": "categorizing-chart"},
                {"template": "exam-mini-set"},
                {"template": "photo-passage"},
                {"template": "correction-rewrite"},
                {"template": "writing-planner"},
                {"template": "final-check"},
                {"template": "handbook"},
                {"template": "vocab-bank"},
            ],
            mode="teacher-book",
            answer_visibility="teacher",
        )

        self.assertTrue(result["checked"], result)
        self.assertFalse(result["ok"], result)
        self.assertIn("back-matter", result["missing_families"])

    def test_rejects_v1_sample_when_v2_full_coverage_is_required(self) -> None:
        result = page_family_coverage_policy(
            [
                {"template": "cover"},
                {"template": "title"},
                {"template": "unit-opener"},
                {"template": "elements"},
                {"template": "activity"},
                {"template": "paragraph-practice"},
                {"template": "photo-passage"},
                {"template": "writing-planner"},
                {"template": "handbook"},
                {"template": "answer-key"},
            ],
            mode="v2-full",
        )

        self.assertFalse(result["ok"], result)
        self.assertIn("front-matter", result["missing_families"])
        self.assertIn("teaching-core", result["missing_families"])
        self.assertIn("practice", result["missing_families"])
        self.assertIn("reading-transfer", result["missing_families"])

    def test_accepts_final_imagegen_visual_asset_with_prompt(self) -> None:
        result = asset_metadata_policy(
            {
                "id": "anonymous-learner-cover-hero-v1",
                "path": "assets/generated/anonymous-learner-cover-hero-v1.png",
                "kind": "imagegen",
                "role": "cover_hero",
                "status": "approved_final",
                "text_policy": "no visible text; not used to carry teaching body, questions, or answers",
                "source_note": "Generated with ImageGen for this project.",
                "focus": "upper-left writing desk with calm negative space",
                "prompt": "Editorial writing desk image with no text.",
                "content_brief": "IELTS writing plan for an anonymous learner, focused on essay planning and evidence selection.",
                "visual_direction": "Personal study desk with layered planning papers and calm teal editorial light.",
                "uniqueness_note": "Designed as a personalized IELTS planning cover, distinct from grammar or workbook covers.",
            },
            asset_mode=ASSET_MODE_FINAL,
            is_visual_ref=True,
        )

        self.assertTrue(result["ok"], result)
        self.assertTrue(result["checks"]["final_kind_allowed"])
        self.assertTrue(result["checks"]["imagegen_prompt_recorded"])
        self.assertTrue(result["checks"]["final_cover_content_concept_recorded"])
        self.assertTrue(result["checks"]["final_cover_uniqueness_recorded"])

    def test_accepts_final_imagegen_nature_wildlife_asset_preference(self) -> None:
        result = asset_metadata_policy(
            {
                "id": "grammar-wetland-cover-final",
                "path": "assets/generated/grammar-wetland-cover-final.png",
                "kind": "imagegen",
                "role": "cover_hero",
                "status": "approved_final",
                "text_policy": "no visible text; not used to carry teaching body, questions, or answers",
                "source_note": "Generated with ImageGen for this project.",
                "focus": "cranes and open river valley in the upper third",
                "prompt": "Quiet nature scene in a misty wetland, with red-crowned cranes moving through reeds beside a river valley; no signs, no letters, no numbers.",
                "content_brief": "Grammar transition book about noticing how clauses connect across a sentence.",
                "visual_direction": "Nature and wildlife cover direction: calm wetland, river light, real birds, open air, and enough quiet space for a textbook title.",
                "uniqueness_note": "Distinct from prior exam-grammar covers through wetland cranes, river light, and open natural air.",
            },
            asset_mode=ASSET_MODE_FINAL,
            is_visual_ref=True,
        )

        self.assertTrue(result["ok"], result)
        self.assertTrue(result["checks"]["final_visual_asset_interpretable_scene"])
        self.assertIn("nature", result["scene_policy"]["real_world_hits"])
        self.assertIn("wildlife", result["scene_policy"]["real_world_hits"])
        self.assertTrue(result["checks"]["nature_first_family_or_rationale"])

    def test_flags_learning_life_asset_without_nature_first_rationale(self) -> None:
        result = asset_metadata_policy(
            {
                "id": "grammar-library-cover-final",
                "path": "assets/generated/grammar-library-cover-final.png",
                "kind": "imagegen",
                "role": "cover_hero",
                "status": "approved_final",
                "text_policy": "no visible text; not used to carry teaching body, questions, or answers",
                "source_note": "Generated with ImageGen for this project.",
                "focus": "library window and study table with clean title space",
                "prompt": "Photorealistic modern library study scene with a student notebook on a desk; no signs, no letters, no numbers.",
                "content_brief": "Grammar transition book about noticing how clauses connect across a sentence.",
                "visual_direction": "Campus library study scene with warm window light and quiet space for a textbook title.",
                "uniqueness_note": "Distinct from prior grammar covers through a library window and quiet study desk.",
            },
            asset_mode=ASSET_MODE_FINAL,
            is_visual_ref=True,
        )

        self.assertTrue(result["ok"], result)
        self.assertFalse(result["checks"]["nature_first_family_or_rationale"])
        self.assertEqual(result["nature_first_policy"]["severity"], "P2")

    def test_rejects_abstract_symbolic_imagegen_asset_in_final_mode(self) -> None:
        result = asset_metadata_policy(
            {
                "id": "grammar-evidence-board-final",
                "path": "assets/generated/grammar-evidence-board-final.png",
                "kind": "imagegen",
                "role": "unit_opener",
                "status": "approved_final",
                "text_policy": "no visible text; not used to carry teaching body, questions, or answers",
                "source_note": "Generated with ImageGen for this project.",
                "focus": "center evidence board",
                "prompt": "Abstract paper decision map with floating blank strips, symbolic grammar tokens, arrows, and a conceptual evidence board.",
                "content_brief": "Grammar decision training for a senior-high exam prep lesson.",
                "visual_direction": "Symbolic paper sculpture with blank cards and abstract clause evidence strips.",
                "uniqueness_note": "Distinct from a generic desk image.",
            },
            asset_mode=ASSET_MODE_FINAL,
            is_visual_ref=True,
        )

        self.assertFalse(result["ok"], result)
        self.assertFalse(result["checks"]["final_visual_asset_interpretable_scene"])
        self.assertIn("abstract", result["scene_policy"]["abstract_hits"])

    def test_rejects_cartoon_mascot_animal_asset_in_final_mode(self) -> None:
        result = asset_metadata_policy(
            {
                "id": "grammar-animal-mascot-cover-final",
                "path": "assets/generated/grammar-animal-mascot-cover-final.png",
                "kind": "imagegen",
                "role": "cover_hero",
                "status": "approved_final",
                "text_policy": "no visible text; not used to carry teaching body, questions, or answers",
                "source_note": "Generated with ImageGen for this project.",
                "focus": "cute animal mascot in the center",
                "prompt": "Cute cartoon animal mascot holding a workbook in a bright sticker style; no signs, no letters, no numbers.",
                "content_brief": "Grammar transition book about noticing how clauses connect across a sentence.",
                "visual_direction": "Animal cover direction with a playful mascot character and sticker-like shapes.",
                "uniqueness_note": "Distinct from prior grammar covers through a cartoon animal character.",
            },
            asset_mode=ASSET_MODE_FINAL,
            is_visual_ref=True,
        )

        self.assertFalse(result["ok"], result)
        self.assertFalse(result["checks"]["final_visual_asset_interpretable_scene"])
        self.assertIn("mascot", result["scene_policy"]["style_drift_hits"])

    def test_rejects_proof_placeholder_in_final_asset_mode(self) -> None:
        result = asset_metadata_policy(
            {
                "id": "sample-learner-writing-desk",
                "path": "assets/generated/sample-learner-writing-desk.png",
                "kind": "procedural-raster",
                "role": "cover_and_unit_opener",
                "status": "original_for_cold_start_proof",
                "text_policy": "no visible text, not used to carry questions or answers",
                "source_note": "Generated locally as a proof placeholder.",
                "focus": "center",
            },
            asset_mode=ASSET_MODE_FINAL,
            is_visual_ref=True,
        )

        self.assertFalse(result["ok"], result)
        self.assertFalse(result["checks"]["final_kind_allowed"])
        self.assertFalse(result["checks"]["final_cover_content_concept_recorded"])
        self.assertFalse(result["checks"]["final_cover_uniqueness_recorded"])
        self.assertFalse(result["checks"]["final_not_placeholder"])
        self.assertFalse(result["checks"]["final_status_approved"])

    def test_rejects_final_imagegen_asset_without_prompt(self) -> None:
        result = asset_metadata_policy(
            {
                "id": "sample-learner-cover-hero-v1",
                "path": "assets/generated/sample-learner-cover-hero-v1.png",
                "kind": "imagegen",
                "role": "cover_hero",
                "status": "approved_final",
                "text_policy": "no visible text; not used to carry teaching body, questions, or answers",
                "source_note": "Generated with ImageGen for this project.",
                "focus": "upper-left writing desk with calm negative space",
            },
            asset_mode=ASSET_MODE_FINAL,
            is_visual_ref=True,
        )

        self.assertFalse(result["ok"], result)
        self.assertFalse(result["checks"]["imagegen_prompt_recorded"])

    def test_rejects_image_text_policy_that_allows_teaching_text(self) -> None:
        result = asset_metadata_policy(
            {
                "id": "unit-opener",
                "path": "assets/generated/unit-opener.png",
                "kind": "imagegen",
                "role": "unit_opener",
                "status": "approved_final",
                "text_policy": "image may include title text",
                "source_note": "Generated with ImageGen.",
                "focus": "center",
                "prompt": "A quiet desk.",
            },
            asset_mode=ASSET_MODE_FINAL,
            is_visual_ref=True,
        )

        self.assertFalse(result["ok"], result)
        self.assertFalse(result["checks"]["text_policy_blocks_image_text"])


class BlankRenderingContractTest(unittest.TestCase):
    def test_flags_literal_underscore_runs_in_generated_output(self) -> None:
        hits = literal_underscore_runs(
            {
                "generated-html": "<li>Because the claim is ___.</li>",
                "pdf-text": "No literal blank here.",
            }
        )

        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["source"], "generated-html")
        self.assertEqual(hits[0]["length"], 3)

    def test_ignores_short_non_blank_underscores(self) -> None:
        hits = literal_underscore_runs({"generated-html": "unit_01 and item_2 are internal ids."})

        self.assertEqual(hits, [])

    def test_accepts_lower_edge_blank_css(self) -> None:
        result = blank_baseline_css_checks(
            """
            <style>
            .blank { height: 0; border-bottom: 0.9pt solid #8f8f8f; vertical-align: -0.82em; }
            .paragraph-practice p .blank { vertical-align: -0.22em; }
            .question-lines .blank { vertical-align: -0.88em; }
            .record-prompt .blank { vertical-align: -0.32em; }
            .activity-block p .blank,
            .activity-block li .blank,
            .word-box .blank,
            .words-to-know .blank,
            .textbook-table td .blank,
            .review-rules .blank,
            .planner-prompt .blank,
            .editing-checklist label .blank,
            .handbook-page .blank,
            .answer-table .blank { vertical-align: -0.30em; }
            .cloze-keep { white-space: nowrap; }
            .word-box { grid-template-columns: repeat(3, minmax(0, 1fr)); }
            .word-box-item { white-space: nowrap; }
            .word-box .blank { vertical-align: -0.26em; }
            .handbook-rules .blank { vertical-align: -0.24em; }
            </style>
            """
        )

        self.assertTrue(result["ok"], result)
        self.assertTrue(result["checks"]["compact_phrase_blank_adjustments"])
        self.assertTrue(result["compact_phrase_blank"]["word_box_phrase_items_no_wrap"])

    def test_rejects_missing_model_paragraph_blank_adjustment(self) -> None:
        result = blank_baseline_css_checks(
            """
            <style>
            .blank { height: 0; border-bottom: 0.9pt solid #8f8f8f; vertical-align: -0.82em; }
            .question-lines .blank { vertical-align: -0.88em; }
            </style>
            """
        )

        self.assertFalse(result["ok"], result)
        self.assertFalse(result["checks"]["model_paragraph_blank_adjustment"])

    def test_rejects_missing_inline_cloze_blank_adjustments(self) -> None:
        result = blank_baseline_css_checks(
            """
            <style>
            .blank { height: 0; border-bottom: 0.9pt solid #8f8f8f; vertical-align: -0.82em; }
            .paragraph-practice p .blank { vertical-align: -0.22em; }
            .question-lines .blank { vertical-align: -0.88em; }
            .record-prompt .blank { vertical-align: -0.32em; }
            </style>
            """
        )

        self.assertFalse(result["ok"], result)
        self.assertFalse(result["checks"]["inline_cloze_context_adjustments"])
        self.assertFalse(result["inline_cloze_selectors"][".activity-block li .blank"])

    def test_rejects_missing_compact_phrase_blank_adjustments(self) -> None:
        result = blank_baseline_css_checks(
            """
            <style>
            .blank { height: 0; border-bottom: 0.9pt solid #8f8f8f; vertical-align: -0.82em; }
            .paragraph-practice p .blank { vertical-align: -0.22em; }
            .question-lines .blank { vertical-align: -0.88em; }
            .record-prompt .blank { vertical-align: -0.32em; }
            .activity-block p .blank,
            .activity-block li .blank,
            .word-box .blank,
            .words-to-know .blank,
            .textbook-table td .blank,
            .review-rules .blank,
            .planner-prompt .blank,
            .editing-checklist label .blank,
            .handbook-page .blank,
            .answer-table .blank { vertical-align: -0.30em; }
            </style>
            """
        )

        self.assertFalse(result["ok"], result)
        self.assertFalse(result["checks"]["compact_phrase_blank_adjustments"])
        self.assertFalse(result["compact_phrase_blank"]["cloze_keep_no_wrap"])

    def test_rejects_previous_middle_blank_css(self) -> None:
        result = blank_baseline_css_checks(
            """
            <style>
            .blank { height: 0; border-bottom: 0.9pt solid #8f8f8f; vertical-align: -0.64em; }
            .question-lines .blank { vertical-align: -0.68em; }
            </style>
            """
        )

        self.assertFalse(result["ok"], result)
        self.assertFalse(result["checks"]["legacy_middle_align_rejected"])


class QuestionLineBlankContractTest(unittest.TestCase):
    def hits(self, body: str) -> list[dict[str, str]]:
        return duplicated_question_blank_hits(BeautifulSoup(body, "html.parser"))

    def test_rejects_inline_blank_when_question_already_has_write_line(self) -> None:
        hits = self.hits(
            """
            <section class="sheet" data-page="7">
              <ol class="question-lines">
                <li>Better: <span class="blank"></span>.<div class="write-line"></div></li>
              </ol>
            </section>
            """
        )

        self.assertEqual(len(hits), 1, hits)
        self.assertEqual(hits[0]["page"], "7")

    def test_accepts_question_line_with_dedicated_write_line_only(self) -> None:
        hits = self.hits(
            """
            <section class="sheet" data-page="8">
              <ol class="question-lines">
                <li>Better:<div class="write-line"></div></li>
              </ol>
            </section>
            """
        )

        self.assertEqual(hits, [])


class MixedTitleLockupContractTest(unittest.TestCase):
    def test_accepts_same_scale_title_for_suffix(self) -> None:
        result = title_lockup_css_checks(
            """
            <style>
            .title-page h1.title-single { white-space: nowrap; }
            .title-page h1.title-single .title-for { margin-left: 7pt; font-size: 1em; font-weight: inherit; }
            </style>
            <main class="title-page"><h1 class="title-single"><span class="title-main">IELTS备考计划</span><span class="title-for">for Sample Learner</span></h1></main>
            """
        )

        self.assertTrue(result["ok"], result)
        self.assertTrue(result["checks"]["title_for_same_optical_scale"])

    def test_rejects_shrunk_title_for_suffix(self) -> None:
        result = title_lockup_css_checks(
            """
            <style>
            .title-page h1.title-single { white-space: nowrap; }
            .title-page h1.title-single .title-for { margin-left: 6pt; font-size: .86em; }
            </style>
            <main class="title-page"><h1 class="title-single"><span class="title-main">IELTS备考计划</span><span class="title-for">for Sample Learner</span></h1></main>
            """
        )

        self.assertFalse(result["ok"], result)
        self.assertFalse(result["checks"]["title_for_same_optical_scale"])
        self.assertFalse(result["checks"]["legacy_title_for_shrink_rejected"])

    def test_accepts_same_scale_cover_for_suffix(self) -> None:
        result = title_lockup_css_checks(
            """
            <style>
            .cover-title.title-single h1 { white-space: nowrap; }
            .cover-title.title-single .title-for { margin-left: 8pt; font-size: 1em; font-weight: inherit; }
            </style>
            <div class="cover-title title-single"><h1><span class="title-main">IELTS备考计划</span><span class="title-for">for Sample Learner</span></h1></div>
            """
        )

        self.assertTrue(result["ok"], result)
        self.assertTrue(result["checks"]["cover_title_for_same_optical_scale"])

    def test_rejects_shrunk_cover_for_suffix(self) -> None:
        result = title_lockup_css_checks(
            """
            <style>
            .cover-title.title-single h1 { white-space: nowrap; }
            .cover-title.title-single .title-for { margin-left: 8pt; font-size: 34pt; font-weight: 850; }
            </style>
            <div class="cover-title title-single"><h1><span class="title-main">IELTS备考计划</span><span class="title-for">for Sample Learner</span></h1></div>
            """
        )

        self.assertFalse(result["ok"], result)
        self.assertFalse(result["checks"]["cover_title_for_same_optical_scale"])
        self.assertFalse(result["checks"]["cover_title_for_weight_not_demoted"])


class ChecklistControlContractTest(unittest.TestCase):
    def test_accepts_isolated_check_mark_control(self) -> None:
        result = checklist_control_css_checks(
            """
            <style>
            .editing-checklist .check-mark { display: inline-block; border: 0.8pt solid #999; }
            .editing-checklist label .blank { vertical-align: -0.24em; }
            </style>
            <section class="editing-checklist">
              <label><span class="check-mark"></span>The evidence is concrete: <span class="blank"></span>.</label>
            </section>
            """
        )

        self.assertTrue(result["ok"], result)
        self.assertTrue(result["checks"]["generic_label_span_selector_rejected"])

    def test_rejects_generic_label_span_control_selector(self) -> None:
        result = checklist_control_css_checks(
            """
            <style>
            .editing-checklist label span { display: inline-block; border: 0.8pt solid #999; }
            </style>
            <section class="editing-checklist">
              <label><span></span>The evidence is concrete: <span class="blank"></span>.</label>
            </section>
            """
        )

        self.assertFalse(result["ok"], result)
        self.assertFalse(result["checks"]["generic_label_span_selector_rejected"])
        self.assertFalse(result["checks"]["check_mark_nodes_present"])

    def test_rejects_missing_checklist_compact_blank_override(self) -> None:
        result = checklist_control_css_checks(
            """
            <style>
            .editing-checklist .check-mark { display: inline-block; border: 0.8pt solid #999; }
            </style>
            <section class="editing-checklist">
              <label><span class="check-mark"></span>The evidence is concrete: <span class="blank"></span>.</label>
            </section>
            """
        )

        self.assertFalse(result["ok"], result)
        self.assertFalse(result["checks"]["checklist_blank_compact_override"])


class UnitOpenerCompositionContractTest(unittest.TestCase):
    def test_accepts_prompt_integrated_into_objectives_band(self) -> None:
        result = unit_opener_composition_checks(
            """
            <style>
            .objectives-intro { display: grid; }
            .opener-prompt { font-size: 8.2pt; }
            .objectives-list ul { margin: 0; }
            </style>
            <section class="sheet" data-template="unit-opener" data-page="13">
              <div class="unit-photo"></div>
              <section class="objectives-band" data-component="objectives-band">
                <div class="objectives-intro">
                  <h2>Objectives</h2>
                  <p class="opener-prompt"><b>Before You Begin</b><span>Before the unit begins, write one sentence.</span></p>
                </div>
                <div class="objectives-list"><ul><li>Name the task.</li></ul></div>
              </section>
            </section>
            """
        )

        self.assertTrue(result["ok"], result)
        self.assertEqual(result["floating_caption_pages"], [])
        self.assertEqual(result["prompt_missing_from_band"], [])

    def test_rejects_floating_photo_caption_prompt_above_objectives_band(self) -> None:
        result = unit_opener_composition_checks(
            """
            <style>
            .objectives-band ul { margin: 0; }
            .photo-caption { position: absolute; bottom: 156pt; }
            </style>
            <section class="sheet" data-template="unit-opener" data-page="13">
              <aside class="photo-caption">Before the unit begins, write one sentence.</aside>
              <section class="objectives-band" data-component="objectives-band">
                <h2>Objectives</h2>
                <ul><li>Name the task.</li></ul>
              </section>
            </section>
            """
        )

        self.assertFalse(result["ok"], result)
        self.assertEqual(result["floating_caption_pages"], ["13"])
        self.assertEqual(result["prompt_missing_from_band"], ["13"])


class UnitOpenerVariationContractTest(unittest.TestCase):
    def test_rejects_long_book_openers_with_one_color_and_one_layout(self) -> None:
        openers = "\n".join(
            f"""
            <section class="sheet" data-template="unit-opener" data-page="{idx}" data-variant="same"
              data-opener-layout="bottom-band" data-opener-accent="#8a4f27">
              <section class="objectives-band"></section>
            </section>
            """
            for idx in [13, 33, 47, 63, 77, 102]
        )

        result = unit_opener_variation_checks(openers)

        self.assertFalse(result["ok"], result)
        self.assertFalse(result["checks"]["multiple_layouts_present"])
        self.assertFalse(result["checks"]["multiple_accents_present"])

    def test_accepts_per_unit_opener_layout_and_accent_variation(self) -> None:
        openers = "\n".join(
            f"""
            <section class="sheet" data-template="unit-opener" data-page="{page}" data-variant="{variant}"
              data-opener-layout="{layout}" data-opener-accent="{accent}">
              <section class="objectives-band"></section>
            </section>
            """
            for page, variant, layout, accent in [
                (13, "forest-bottom-band", "bottom-band", "#8a4f27"),
                (33, "lake-side-panel", "side-panel", "#216f83"),
                (47, "deer-split-band", "split-band", "#526f4b"),
                (63, "lake-bottom-band", "bottom-band", "#285970"),
                (77, "mountain-side-panel", "side-panel", "#5c724c"),
                (102, "connected-lakes-split-band", "split-band", "#465f78"),
            ]
        )

        result = unit_opener_variation_checks(openers)

        self.assertTrue(result["ok"], result)
        self.assertGreaterEqual(len(result["layouts"]), 2)
        self.assertGreaterEqual(len(result["accents"]), 3)


class PlannerSurfaceContractTest(unittest.TestCase):
    def test_accepts_row_card_planner_surface(self) -> None:
        result = planner_surface_checks(
            """
            <div class="review-rules"><span>one focus</span></div>
            <div class="planner-rows" data-component="writing-planner">
              <article class="planner-row">
                <div class="planner-key"></div>
                <div class="planner-body"></div>
              </article>
            </div>
            <table class="mechanics-table"></table>
            """
        )

        self.assertTrue(result["ok"], result)

    def test_accepts_named_variant_planner_surface(self) -> None:
        result = planner_surface_checks(
            """
            <section class="answer-sheet-head"></section>
            <section class="answer-sheet-surface" data-component="writing-planner">
              <article>
                <div class="answer-sheet-key"></div>
                <div class="answer-sheet-lines"></div>
              </article>
            </section>
            """
        )

        self.assertTrue(result["ok"], result)
        self.assertTrue(result["checks"]["planner_role_texture_present"])

    def test_accepts_task2_printed_surface(self) -> None:
        result = planner_surface_checks(
            """
            <section class="answer-sheet-head"></section>
            <section class="task2-ladder-surface task2-printed-surface" data-component="writing-planner">
              <div class="task2-position-ladder">
                <article><b>Position</b><p>clear answer</p></article>
              </div>
              <div class="task2-body-lanes">
                <article><b>Body 1</b><p>reason and evidence</p></article>
              </div>
            </section>
            """
        )

        self.assertTrue(result["ok"], result)
        self.assertTrue(result["checks"]["planner_role_texture_present"])

    def test_rejects_legacy_table_planner(self) -> None:
        result = planner_surface_checks(
            """
            <section class="planner-surface">
              <table class="planner-table" data-component="writing-planner"></table>
            </section>
            """
        )

        self.assertFalse(result["ok"], result)
        self.assertFalse(result["checks"]["legacy_table_planner_rejected"])


class WorkbookRecordContractTest(unittest.TestCase):
    def test_accepts_cohesive_workbook_record_surface(self) -> None:
        result = workbook_record_checks(
            """
            <section class="workbook-record" data-component="workbook-practice">
              <div class="record-head"><b>Diagnostic Record</b><span>one skill</span></div>
              <article>
                <span class="record-index">01</span>
                <div><p class="record-prompt">One proof.</p><div class="record-lines"></div></div>
              </article>
            </section>
            """
        )

        self.assertTrue(result["ok"], result)

    def test_rejects_loose_question_lines_as_workbook_tail(self) -> None:
        result = workbook_record_checks(
            """
            <ol class="question-lines">
              <li>What should Sample Learner do next?<div class="write-line"></div></li>
            </ol>
            """
        )

        self.assertFalse(result["ok"], result)
        self.assertFalse(result["checks"]["workbook_practice_component_present"])


class RenderedPageCountContractTest(unittest.TestCase):
    def test_accepts_exact_rendered_page_count(self) -> None:
        result = rendered_page_count_checks(7, 7)

        self.assertTrue(result["ok"], result)
        self.assertTrue(result["checks"]["rendered_page_count_exact"])

    def test_rejects_missing_rendered_pages(self) -> None:
        result = rendered_page_count_checks(6, 7)

        self.assertFalse(result["ok"], result)
        self.assertTrue(result["checks"]["rendered_pages_missing"])

    def test_rejects_stale_extra_rendered_pages(self) -> None:
        result = rendered_page_count_checks(24, 7)

        self.assertFalse(result["ok"], result)
        self.assertTrue(result["checks"]["rendered_pages_stale"])

    def test_rejects_conflicted_rendered_page_files(self) -> None:
        result = rendered_page_filename_checks(
            [
                "student-book-trim-page-001.png",
                "student-book-trim-page-002.png",
                "student-book-trim-page-002 2.png",
                "student-book-trim-page-003.png",
            ],
            "student-book-trim",
            3,
        )

        self.assertFalse(result["ok"], result)
        self.assertEqual(result["conflict_files"], ["student-book-trim-page-002 2.png"])

    def test_rejects_missing_canonical_rendered_sequence(self) -> None:
        result = rendered_page_filename_checks(
            [
                "student-book-trim-page-001.png",
                "student-book-trim-page-003.png",
            ],
            "student-book-trim",
            3,
        )

        self.assertFalse(result["ok"], result)
        self.assertEqual(result["missing_files"], ["student-book-trim-page-002.png"])


class StarterV2ProfileFilteringContractTest(unittest.TestCase):
    def test_starter_v2_filters_teacher_only_pages_before_rendering_profiles(self) -> None:
        skill_dir = Path(__file__).resolve().parents[1]
        starter = skill_dir / "assets" / "starter-project-v2"
        build_text = (starter / "tools" / "build.py").read_text(encoding="utf-8")
        render_text = (starter / "tools" / "render_pdf.py").read_text(encoding="utf-8")
        validate_text = (starter / "tools" / "validate.py").read_text(encoding="utf-8")
        teacher_page = (starter / "pages" / "24-teacher-guide.md").read_text(encoding="utf-8")
        gate_text = (skill_dir / "scripts" / "validate_skill_gates.py").read_text(encoding="utf-8")
        skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        workflow_text = (skill_dir / "references" / "production-workflow.md").read_text(encoding="utf-8")

        self.assertTrue(
            "def page_in_profile" in build_text,
            "starter v2 build.py must define page_in_profile()",
        )
        self.assertTrue(
            "if not page_in_profile(meta, profile, book):" in build_text,
            "starter v2 build loop must skip pages excluded from the active profile",
        )
        self.assertTrue("page_no = 0" in build_text, "filtered builds must renumber visible pages")
        self.assertTrue("audience: teacher" in teacher_page, "teacher guide page must declare audience: teacher")
        self.assertTrue("template: teacher-guide-page" in teacher_page, "teacher sample must use a real teacher guide page")
        self.assertTrue("teacher_page_layer" in build_text, "starter v2 must render integrated teacher notes, not only backmatter")
        self.assertNotIn('choices=["book-trim", "lesson-a4"]', build_text)
        self.assertNotIn('choices=["book-trim", "lesson-a4"]', render_text)
        self.assertNotIn('choices=["book-trim", "lesson-a4"]', validate_text)
        self.assertTrue(
            "starter_v2_profile_filtering" in gate_text,
            "validate_skill_gates.py must report starter_v2_profile_filtering evidence",
        )
        self.assertTrue(
            all(token in skill_text for token in ["audience: teacher", "include_profiles", "exclude_profiles"]),
            "SKILL.md must document profile-level page filtering frontmatter",
        )
        self.assertTrue(
            all(token in workflow_text for token in ["audience: teacher", "include_profiles", "exclude_profiles"]),
            "production-workflow.md must document profile-level page filtering frontmatter",
        )

        spec = importlib.util.spec_from_file_location("starter_v2_build", starter / "tools" / "build.py")
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        teacher_meta = {"template": "teacher-answer-key", "audience": "teacher"}
        student_book = {"qa": {"answer_visibility": "student"}, "profiles": {"student-book-trim": {}}}
        teacher_book = {"qa": {"answer_visibility": "student"}, "profiles": {"teacher-book-trim": {"qa": {"answer_visibility": "teacher"}}}}
        gallery_book = {"qa": {}, "profiles": {"book-trim": {}}}

        self.assertFalse(module.page_in_profile(teacher_meta, "student-book-trim", student_book))
        self.assertTrue(module.page_in_profile(teacher_meta, "teacher-book-trim", teacher_book))
        self.assertTrue(module.page_in_profile(teacher_meta, "book-trim", gallery_book))


class NewProjectProfileScaffoldContractTest(unittest.TestCase):
    def test_new_project_can_scaffold_student_and_teacher_profiles(self) -> None:
        skill_dir = Path(__file__).resolve().parents[1]
        starter = skill_dir / "assets" / "starter-project-v2"
        script = skill_dir / "scripts" / "new_project.py"
        gate_text = (skill_dir / "scripts" / "validate_skill_gates.py").read_text(encoding="utf-8")

        spec = importlib.util.spec_from_file_location("new_project_module", script)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        profiles = module.parse_profiles("student-book-trim,teacher-book-trim")
        self.assertEqual(profiles, ["student-book-trim", "teacher-book-trim"])

        with tempfile.TemporaryDirectory(prefix="eric-pdf-profile-scaffold-") as tmp:
            target = Path(tmp)
            shutil.copy2(starter / "book.yaml", target / "book.yaml")
            module.customize_book(target, "Profile Separation Proof", profiles)
            data = module.yaml.safe_load((target / "book.yaml").read_text(encoding="utf-8"))

        self.assertEqual(data["profile_default"], "student-book-trim")
        self.assertEqual(set(data["profiles"]), {"student-book-trim", "teacher-book-trim"})
        self.assertIn("student-book-trim", data["profiles"])
        self.assertIn("teacher-book-trim", data["profiles"])
        self.assertEqual(data["profiles"]["student-book-trim"]["qa"]["answer_visibility"], "student")
        self.assertEqual(data["profiles"]["teacher-book-trim"]["qa"]["answer_visibility"], "teacher")
        self.assertNotIn("teacher-answer-key", data["profiles"]["student-book-trim"]["qa"]["required_templates"])
        self.assertNotIn("answer-key-page", data["profiles"]["student-book-trim"]["qa"]["required_components"])
        self.assertTrue(
            "new_project_dynamic_profiles" in gate_text,
            "validate_skill_gates.py must report new_project_dynamic_profiles evidence",
        )
        self.assertTrue(
            "dynamic_profile_pdf_smoke" in gate_text
            and "student_pdf_excludes_teacher_key" in gate_text
            and "teacher_pdf_includes_teacher_key" in gate_text,
            "validate_skill_gates.py must run a dynamic student/teacher PDF separation smoke",
        )


class StarterV2VisualDensityContractTest(unittest.TestCase):
    def test_starter_v2_guided_mcq_accepts_real_material_question_field(self) -> None:
        skill_dir = Path(__file__).resolve().parents[1]
        starter = skill_dir / "assets" / "starter-project-v2"
        build_text = (starter / "tools" / "build.py").read_text(encoding="utf-8")

        self.assertTrue(
            'item.get("prompt", item.get("question", ""))' in build_text,
            "starter v2 guided_mcq must accept real-material `question:` fallback",
        )

    def test_starter_v2_weak_pages_have_editorial_density_markers(self) -> None:
        skill_dir = Path(__file__).resolve().parents[1]
        starter = skill_dir / "assets" / "starter-project-v2"
        build_text = (starter / "tools" / "build.py").read_text(encoding="utf-8")
        page_text = "\n".join(
            (starter / rel).read_text(encoding="utf-8")
            for rel in [
                "pages/03-contents-route.md",
                "pages/04-diagnostic-entry.md",
                "pages/07-article-evidence.md",
                "pages/14-exam-mini-set.md",
                "pages/19-correction-rewrite.md",
                "pages/20-final-check.md",
            ]
        )

        required_renderer_markers = [
            "contents-scope-map",
            "contents-page-index",
            "diagnostic-ladder",
            "diagnostic-mini-note",
            "evidence-flow",
            "evidence-cues",
            "evidence-task-strip",
            "exam-pressure-grid",
            "exam-timing-strip",
            "rewrite-lens",
            "rewrite-micro-rules",
            "final-check-summary",
        ]
        required_page_fields = [
            "scope_rows:",
            "page_index:",
            "diagnostic_notes:",
            "evidence_paragraphs:",
            "evidence_cues:",
            "evidence_task_rows:",
            "pressure_rows:",
            "timing_note:",
            "lens:",
            "micro_rules:",
            "summary_checks:",
        ]

        for marker in required_renderer_markers:
            self.assertIn(marker, build_text)
        for field in required_page_fields:
            self.assertIn(field, page_text)


if __name__ == "__main__":
    unittest.main()
