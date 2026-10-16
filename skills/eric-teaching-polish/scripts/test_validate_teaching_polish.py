import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name('validate_teaching_polish.py')
spec = importlib.util.spec_from_file_location('teaching_polish', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TeachingPolishAudienceTests(unittest.TestCase):
    def test_teacher_support_is_valid_only_on_teacher_surface(self):
        text = '教师版\n课堂安排\n0-10\n教师动作：展示例句。\n参考答案：She does not play tennis.'
        self.assertEqual(module.scan(text, 'teacher'), ([], []))
        self.assertEqual(module.scan(text, 'internal'), ([], []))
        errors, warnings = module.scan(text)
        self.assertTrue(errors)
        self.assertTrue(any('answer_leak' in x for x in warnings))

    def test_ordinary_english_is_preserved(self):
        for text in ['Read about a travel agent and food production, then write your first draft.', 'The travel agent notes each request.', 'Check the production status before shipment.']:
            with self.subTest(text=text):
                self.assertEqual(module.scan(text), ([], []))

    def test_recycling_in_environmental_material_is_preserved(self):
        self.assertEqual(module.scan('塑料在每轮收集结束后被回收处理。'), ([], []))
        for text in ['知识点回收动作', '回收任务写在教师流程里']:
            with self.subTest(text=text):
                self.assertTrue(module.scan(text)[1])

    def test_actual_production_labels_still_fail(self):
        for text in ['agent: reviewer', 'production: draft', 'Codex agent', 'validator', '/Users/example/book', 'production draft']:
            with self.subTest(text=text):
                errors, warnings = module.scan(text)
                self.assertTrue(errors or warnings)

    def test_internal_headings_and_versioned_draft_labels_fail(self):
        for text in ['Production Notes', 'Agent Review Notes', 'Internal agent notes', 'Draft 1', 'Draft v2', '# Draft 1: lesson']:
            with self.subTest(text=text):
                errors, warnings = module.scan(text)
                self.assertTrue(errors or warnings, text)
                result = subprocess.run([sys.executable, '-B', str(SCRIPT), '--strict', '-'], input=text, text=True, capture_output=True)
                self.assertEqual(result.returncode, 1, result.stdout)

    def test_source_exemption_is_explicit_and_line_scoped(self):
        text = 'Hermes appears in this verified passage.\nagent: reviewer\n'
        errors, warnings = module.scan(text, source_lines=((1, 1),))
        self.assertEqual(len(errors), 1)
        self.assertIn('line 2', errors[0])
        self.assertTrue(module.scan(text)[0])

    def test_source_exemption_never_hides_student_answer_leak(self):
        errors, warnings = module.scan('参考答案：A', source_lines=((1, 1),))
        self.assertTrue(any('answer_leak' in x for x in warnings))

    def test_parent_and_public_keep_answer_and_internal_label_checks(self):
        for audience in ['parent', 'public']:
            errors, warnings = module.scan('agent: reviewer\n参考答案：A', audience)
            self.assertTrue(errors)
            self.assertTrue(warnings)

    def test_invalid_context_is_rejected(self):
        for ranges in [((0, 1),), ((2, 1),), ((1, 3),)]:
            with self.assertRaises(ValueError):
                module.scan('one line', source_lines=ranges)
        with self.assertRaises(ValueError):
            module.scan('text', audience='unknown')

    def test_cli_strict_teacher_and_default_student(self):
        for args, expected in [(['--audience', 'teacher'], 0), ([], 1)]:
            result = subprocess.run([sys.executable, '-B', str(SCRIPT), '--strict', *args, '-'], input='参考答案：She does not play tennis.', text=True, capture_output=True)
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)

    def test_cli_source_ranges_and_errors(self):
        for value, expected in [('1:1', 0), ('1:9', 2), ('0:1', 2), ('2:1', 2)]:
            result = subprocess.run([sys.executable, '-B', str(SCRIPT), '--strict', '--source-lines', value, '-'], input='Hermes in a verified passage.', text=True, capture_output=True)
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)


class PlainLanguageTests(unittest.TestCase):
    def test_named_words_fail_for_every_audience_without_strict(self):
        for audience in module.AUDIENCES:
            for text in ['请先明确边界。', '我们要保留证据。']:
                with self.subTest(audience=audience, text=text):
                    self.assertTrue(module.scan(text, audience)[0])

    def test_contrast_and_stock_forms_fail(self):
        for text in ['这不是速度问题，而是流程问题。', '并非功能不足，而是使用方式不同。', '不在于数量，而在于质量。', '不是要写更多，是要写清楚。', '不仅要会做，更要理解。', 'This is not about speed, but about quality.', "This isn't about speed. It's about quality.", '综上所述，我们需要行动。']:
            with self.subTest(text=text):
                self.assertTrue(module.scan(text, language_only=True)[0])

    def test_ordinary_prose_and_useful_lists_pass(self):
        for text in ['文章第二段写了作者离开的原因。', '这份数据只到 2024 年。新版还没测。', '1. 打开文件。\n2. 修改标题。\n3. 保存文件。', 'Report available from [the source](https://example.invalid/report).', 'The travel agent notes each request. Check the production status before shipment.']:
            with self.subTest(text=text):
                self.assertEqual(module.scan(text, language_only=True), ([], []))

    def test_quotation_marks_do_not_automatically_exempt_generated_prose(self):
        self.assertTrue(module.scan('“证据”', language_only=True)[0])

    def test_verified_source_lines_preserve_exact_text_and_other_line_numbers(self):
        text = '原文：证据不足。\n自己写的边界。'
        errors, _ = module.scan(text, source_lines=((1, 1),), language_only=True)
        self.assertEqual(len(errors), 1)
        self.assertIn('line 2', errors[0])
        self.assertEqual(module.scan(text, source_lines=((1, 2),), language_only=True), ([], []))
        self.assertEqual(text, '原文：证据不足。\n自己写的边界。')

    def test_language_only_is_not_teaching_acceptance(self):
        text = '参考答案：A\n0-10'
        self.assertEqual(module.scan(text, language_only=True), ([], []))
        self.assertTrue(module.scan(text)[1])

    def test_fixed_patterns_are_cli_errors_without_strict(self):
        for args in [[], ['--language-only'], ['--audience', 'teacher']]:
            result = subprocess.run([sys.executable, '-B', str(SCRIPT), *args, '-'], input='不是速度，而是质量。', text=True, capture_output=True)
            self.assertEqual(result.returncode, 1, result.stdout)

    def test_generic_cli_uses_verified_source_exclusions(self):
        result = subprocess.run([sys.executable, '-B', str(SCRIPT), '--language-only', '--source-lines', '1:1', '-'], input='原文：证据不足。', text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == '__main__':
    unittest.main()
