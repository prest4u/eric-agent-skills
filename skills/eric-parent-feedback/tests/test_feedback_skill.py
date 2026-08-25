"""Maintenance tests for the parent-feedback editorial contract."""

from __future__ import annotations

import json
import stat
import sys
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from validate_feedback import lint_style, validate  # noqa: E402


CLEAN_FEEDBACK = """学生：学生A
日期：2026年8月25日
课次 / 主题：短段写作

①课上内容

1. 完成一段校园活动短写
2. 使用 because 连接两句话

②课上反馈

今天能够独立写出短段，主要意思表达清楚。

目前句子结构还比较简单，独立组织完整句子时不够稳定，这是现阶段需要继续练习的一项。

③课后作业

1. 回看今天完成的短段并订正标记处。
"""


class FeedbackValidatorTests(unittest.TestCase):
    def test_clean_formal_feedback_passes_without_warnings(self) -> None:
        self.assertEqual([], validate(CLEAN_FEEDBACK))
        self.assertEqual([], lint_style(CLEAN_FEEDBACK))

    def test_colloquial_and_scolding_language_warns(self) -> None:
        text = CLEAN_FEEDBACK.replace(
            "今天能够独立写出短段，主要意思表达清楚。",
            "今天状态还行，表现挺好，作业要抓紧，不能请假就不做。",
        )
        warnings = "\n".join(lint_style(text))
        for marker in ("状态还行", "挺好", "抓紧", "训话"):
            self.assertIn(marker, warnings)

    def test_bureaucratic_or_inflated_language_warns(self) -> None:
        text = CLEAN_FEEDBACK.replace(
            "今天能够独立写出短段，主要意思表达清楚。",
            "本次课堂投入度良好，但写作仍有提升空间，需要切实下功夫。",
        )
        warnings = "\n".join(lint_style(text))
        for marker in ("课堂投入度", "提升空间", "切实下功夫"):
            self.assertIn(marker, warnings)

    def test_repeated_need_language_warns_inside_feedback_only(self) -> None:
        text = CLEAN_FEEDBACK.replace(
            "目前句子结构还比较简单，独立组织完整句子时不够稳定，这是现阶段需要继续练习的一项。",
            "写作仍需要继续练习，还需要在更多情境中练习。",
        )
        self.assertIn("重复使用", "\n".join(lint_style(text)))

    def test_next_lesson_preview_is_a_hard_error(self) -> None:
        text = CLEAN_FEEDBACK.replace(
            "③课后作业",
            "下节课将继续训练写作。\n\n③课后作业",
        )
        self.assertTrue(any("Forbidden" in error for error in validate(text)))

    def test_no_homework_sentence_passes_without_invented_task(self) -> None:
        text = CLEAN_FEEDBACK.replace(
            "1. 回看今天完成的短段并订正标记处。",
            "本次课无额外作业。",
        )
        self.assertEqual([], validate(text))
        self.assertEqual([], lint_style(text))

    def test_all_markdown_heading_levels_are_hard_errors(self) -> None:
        for heading in ("# 家长配合", "### 家长配合", "###### 家长配合"):
            with self.subTest(heading=heading):
                text = CLEAN_FEEDBACK + "\n" + heading + "\n请配合复习。\n"
                self.assertTrue(any("Markdown" in error for error in validate(text)))

    def test_common_fourth_section_variants_are_hard_errors(self) -> None:
        for heading in (
            "④ 家长配合",
            "四）家长配合",
            "4. 家长配合",
            "4．家长配合",
            "家长配合：",
            "补充说明：",
        ):
            with self.subTest(heading=heading):
                text = CLEAN_FEEDBACK + "\n" + heading + "\n请配合复习。\n"
                self.assertTrue(any("fourth" in error for error in validate(text)))

    def test_fourth_numbered_homework_task_is_allowed(self) -> None:
        text = CLEAN_FEEDBACK.replace(
            "1. 回看今天完成的短段并订正标记处。",
            "① 回看今天完成的短段。\n② 订正标记处。\n③ 朗读订正后的短段。\n④ 完成练习册第4页。",
        )
        self.assertEqual([], validate(text))

    def test_metadata_must_precede_first_section(self) -> None:
        text = CLEAN_FEEDBACK.replace("学生：学生A\n", "").replace(
            "1. 回看今天完成的短段并订正标记处。",
            "1. 回看今天完成的短段并订正标记处。\n学生：学生A",
        )
        errors = "\n".join(validate(text))
        self.assertIn("misplaced metadata", errors)

    def test_legitimate_industrial_production_content_is_allowed(self) -> None:
        text = CLEAN_FEEDBACK.replace("短段写作", "工业生产词汇")
        self.assertEqual([], validate(text))

    def test_internal_production_workflow_label_is_rejected(self) -> None:
        text = CLEAN_FEEDBACK.replace("短段写作", "内部生产备注")
        self.assertTrue(any("Forbidden" in error for error in validate(text)))

    def test_named_class_requires_class_metadata(self) -> None:
        text = CLEAN_FEEDBACK.replace("学生：学生A", "学生：学生A\n课程：暑假班")
        self.assertTrue(any("班级" in error for error in validate(text)))


class FeedbackSkillContractTests(unittest.TestCase):
    def test_skill_is_self_contained_and_routes_to_two_references(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/editorial-judgment.md", skill)
        self.assertIn("references/style-guide.md", skill)
        self.assertNotRegex(skill, r"(?:Route to|Use \$)[a-z0-9-]+")
        self.assertNotIn("Borrow the de-AI stack", skill)
        self.assertIn("本次课无额外作业", skill)
        self.assertIn("one verified issue per named student", skill)

    def test_validator_remains_directly_executable(self) -> None:
        mode = (SKILL_DIR / "scripts" / "validate_feedback.py").stat().st_mode
        self.assertTrue(mode & stat.S_IXUSR)

    def test_regression_prompts_are_anonymized_and_decision_based(self) -> None:
        cases = json.loads((SKILL_DIR / "test-prompts.json").read_text(encoding="utf-8"))
        self.assertEqual(5, len(cases))
        self.assertEqual({"id", "prompt", "expected"}, set(cases[0]))
        self.assertIn("anonymous", cases[1]["prompt"].lower())
        self.assertTrue(all("student" in case["prompt"].lower() for case in cases))


if __name__ == "__main__":
    unittest.main()
