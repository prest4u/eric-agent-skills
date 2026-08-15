#!/usr/bin/env python3
"""Validate visible teaching material for internal/AI-flavored wording."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


HARD_PATTERNS = {
    "hidden_memory_or_project_label": r"\b(MBTI|Hermes|validator|production|agent)\b|记忆系统|跨项目记忆",
    "teacher_tactic": r"挖坑|让学生先错|教师动作|预期回应|教学上抓|教学上|教学口径",
    "move_jargon": r"心法|出招|拆招|定招",
    "routing_backend": r"后台|路由|维修层|短程维修|内部记录",
    "raw_route_code": r"(?<![A-Za-z0-9])(?:[A-Z]\d{2,}|T\d+)(?![A-Za-z0-9])",
    "ai_detection": r"AI检测|检测率|绕过检测|规避检测",
}

SOFT_PATTERNS = {
    "visible_version_or_course_label": r"学生版|教师版|教师用|22讲|第\s*\d{1,2}\s*(?:[-–—]\s*\d{1,2}\s*)?讲|前[一二三四五六七八九十0-9]+讲",
    "course_map_visible": r"课程地图|全课程路线|22讲路线|Course\s+Map|Lesson\s+Map",
    "student_source_label_leak": r"(?m)source[_\s-]*id|TJGK-PAPER|SIM-\d+|天津高考真题(?:节选|改编)?|原创天津高考仿真|原创仿真|真题改编|真题[/／]改编|真题精拆|真题限时|真题审题|完整仿真篇章|仿真任务|复用材料|回看材料|\b\d{4}\s*·\s*(?:reading_expression|reading|cloze)\b|^\s*(?-i:reading_expression|cloze)\s*$",
    "student_sequence_field_leak": r"source[_\s-]*unit[_\s-]*no|reader[_\s-]*order|build[_\s-]*order|canonical[_\s-]*id|golden\s+sample|thick\s+unit|quality\s+gate",
    "raw_source_question_code": r"TJGK-\d{4}[A-Z]?-[A-Z0-9-]+|(?:CLOZE|READ)-\d{1,2}|L\d{2}-EC0?\d{1,2}|(?<![A-Za-z0-9])(?:B|G)\d{1,2}(?![A-Za-z0-9])",
    "pipeline_words": r"入口|回收|动作链|得分动作|动作卡|自检卡|得分卡|工具卡|任务卡|私人自检|优先动作卡|班级动作热区|score\s*moves|scorecard|self-check\s*card|得分场景|能力场景|机制",
    "student_schedule_leak": r"课堂安排|课堂动作|教师节奏|学生产出|时间安排|课堂中必须保留|不可被课堂核对占用|讲评|本阶段分钟",
    "answer_leak": r"参考答案|答案解析|正确答案|答案\s*[:：]|解析\s*[:：]",
    "internal_taxonomy": r"\bSOLO\b",
    "production_markers": r"\bprototype\b|\bdrafts?\b|/Users/",
    "student_production_frontmatter": r"\bSoft\s+Signal\b|\bpublication\s+edition\b|\blesson\s+pack\b|\bcombined\s+book\b|\bgenerated\s+from\b|A4\s+(?:student\s+|teacher\s+)?total\s+book|stage\s+openers\s+and\s+lesson\s+bodies|\bfront\s+matter\b|\bEnglish-forward\b|\bLearning\s+object\b|\bexam-style\s+reading\b",
    "student_navigation_production_wording": r"内部查找|内部翻找|本讲内部",
    "corporate_ai_words": r"闭环|抓手|沉淀|赋能|拉通|对齐|颗粒度|路径|矩阵",
    "template_shells": r"本节课围绕|系统化梳理|通过本节课|打下坚实基础|真正重要的是|接下来我们|下面来看|课堂路线",
    "teacher_sample_control": r"样文只能|教师样文|示范样文只能",
    "english_reading_surface": r"Evidence链|第本阶段讲|圈\s*(?:but|however|instead|yet)|[\u4e00-\u9fff]{2,}\s*第\s*\d{1,2}\s*空|阅读细节定位\s*[:：]\s*题干关键词",
    "ocr_or_pdf_noise": r"ev-\s*ery|a-\s*gainshe|whenI__\d{1,2}|onthe\b|However-I|of\*Pirates|confusio\b|expectationoi\b|fourweek\b",
    "cloze_placeholder_content": r"备用题要求先写证据再选答案|A\.\s*evidence\s+B\.\s*guess\s+C\.\s*habit\s+D\.\s*noise",
    "student_tool_language": r"调用工具|高错工具|前序工具|关键工具|工具调用|阅读工具|工具选择|工具阶段|工具带走|五类工具|\d+\s*类工具|训练工具|高错|Tool\s+to\s+use|tool\s+selection",
    "student_backstop_language": r"\bBackup\b|备用阅读|备用完整篇章|备用任务|备用挑战|备用补测",
    "student_tiering_or_scheduling": r"A轨|B轨|C轨|基础差|差生版|快班|慢班|补测|分层补测|Track\s*[ABC]|[ABC]\s*Track|Foundation\s+Track|Core\s+Track|Advanced\s+Track|剩余\s*\d+\s*分钟|Record the homework requirement|No Immediate Review",
    "reused_as_unseen": r"Unseen\s+Full\s+Practice",
    "machine_replacement_residue": r"今天承接今天|今天把今天|合格我的作答|Blanks\s+本阶段|Objectivequestion|\bfour\s+week\b|Sprint\s+High-Score\s+Sprint\s+Setup|第本课程|加练加练|内部翻找",
    "teacher_bilingual_template_glue": r"先(?:让)?学生(?:口头)?说出\s+[A-Z][A-Za-z+ /\-]{6,}|先让学生口头说出\s+Use\s+[A-Za-z]",
    "teacher_generic_helper_residue": r"顺利学生做；若(?:低错|证据|句子|答案形式|表达)不稳，退回\s*(?:core|line band|简单句|06)",
    "teacher_tone_generic_residue": r"(?:词义|态度|语气)[^。\n]{0,18}找证据即可|态度不稳[^。\n]{0,18}退回\s*line\s*band|Start\s*\+\s*(?:mood\s+labels|handle\s+rows)|Line-Band\s+Rescue|line\s+band\s*\+\s*one\s+evidence\s+word",
    "main_idea_line_band_residue": r"(?:主旨|结构|Main\s+idea)[^。\n]{0,40}(?:Line-Band|line\s+band|找证据即可|evidence\s+lines)|Line-Band\s+Rescue",
    "reading_set_line_band_residue": r"(?:组合限时|Reading\s+Set|reading\s+set|timed\s+reading)[^。\n]{0,80}(?:Line-Band|line\s+band|找证据即可|answer\s+in\s+order)|Line-Band\s+Rescue\s+Plan",
    "objective_reading_line_band_residue": r"(?:综合客观阅读|客观题综合|Objective\s+Reading|objective\s+reading)[^。\n]{0,120}(?:Line-Band|line\s+band|找证据即可|退回\s*line\s*band|generic\s+evidence|only\s+line\s+locating)",
    "reading_response_line_bank_residue": r"(?:阅读表达|Reading\s+Response|reading\s+response|short\s+response)[^。\n]{0,100}(?:Line-Band|line\s+band|Line\s+Bank|line\s+bank|找证据即可|copy\s+full\s+sentence|full\s+sentence\s+copy)|Line\s+Band\s+Rescue",
    "open_response_line_bank_residue": r"(?:开放回答|开放题|Open\s+Response|open\s+response|open[-\s]answer|open[-\s]reading[-\s]response)[^。\n]{0,120}(?:Line-Band|line\s+band|Line\s+Bank|line\s+bank|找证据即可|copy\s+facts?|retell\s+the\s+whole\s+story|no\s+answer\s+position|personal\s+opinion\s+first)",
    "paragraph_expansion_prompt_only_residue": r"(?:段落展开|Paragraph\s+Expansion|paragraph\s+expansion|Paragraph\s+Development|paragraph\s+development)[^。\n]{0,140}(?:reader\s*/\s*purpose|reader/purpose|Prompt\s+card\s*\+\s*rescue|只拆\s*reader\s*/\s*purpose|退回简单句)",
    "sentence_upgrade_prompt_only_residue": r"(?:句式升级|Sentence\s+Upgrade|sentence\s+upgrade)[^。\n]{0,160}(?:reader\s*/\s*purpose|reader/purpose|Prompt\s+card\s*\+\s*rescue|只拆\s*reader\s*/\s*purpose|退回简单句|顺利学生做；若句子不稳)",
    "timed_writing_prompt_only_residue": r"(?:限时写作|Timed\s+Writing|timed\s+writing)[^。\n]{0,160}(?:reader\s*/\s*purpose\s+only|reader/purpose\s+only|Prompt\s+card\s*\+\s*rescue|只拆\s*reader\s*/\s*purpose|退回简单句|顺利学生做；若句子不稳)",
    "final_review_prompt_shell_residue": r"(?:(?:Final\s+Review|final\s+review|最终复盘|综合实战主观复盘)[^。\n]{0,160}(?:Plan\s+Before\s+Writing|Tiny\s+Prompt\s+Repeat|Low-Risk\s+Writing\s+Extension|reader\s*/\s*purpose\s*/\s*required\s+points|全卷讲评|be\s+careful|退回简单句)|Low-Risk\s+Writing\s+Extension[^。\n]{0,120}(?:全卷讲评|退回简单句))",
    "teacher_numeric_route_residue": r"(?:Start|Core route|Rescue route|Cut-time|Quick route|Close route|Route|路径|路线)[^\n]{0,100}\b\d{2}\s*(?:[-–]\s*\d{2}|\+\s*\d{2})\b|\b\d{2}\s*\+\s*\d{2}\s+(?:one row|first item)\b",
    "release_teacher_surface_residue": r"(?:Line[-\s]?Band(?:s)?|line[-\s]?band(?:s)?|Line[-\s]?Band\s+Rescue|Line[-\s]?Band\s+Rescue\s+Plan)|(?:教师版|教师用)[^。\n]{0,80}(?:保留答案|保留.*证据|总册|讲评)|讲评总册|课堂使用\s*/\s*讲评",
    "total_book_tail_page_residue": r"(?:total\s+book|总册|combined\s+book)[^。\n]{0,160}(?:three\s+exit\s+rows\s+only|only\s+contains\s+a\s+three-row\s+exit\s+table|no\s+transfer\s+check|单课封面.*跳过.*尾页|跳过.*单课封面.*薄页)",
    "total_book_frontmatter_label_collision": r"RoutinePage\s+Routine|Page\s+RoutinePage|A4\s+teacher\s+total\s+book|Front\s+matter\s+plus\s+classroom\s+guide\s+bodies|Teacher\s+Control",
    "abstract_track_cover_chips": r"Small\s+Step\s*/?\s*Evidence\s*/?\s*Low\s+Error|Timed\s*/?\s*Risk\s*/?\s*Transfer",
    "isolated_teacher_cue_residue": r"(?:Review\s+cue|Teaching\s+cue)[^\n]{0,180}(?:After\s+the\s+key\s+table|ask\s+students\s+to\s+name|one[-\s]sentence|stands?\s+alone|单独成页|孤立)",
    "publication_layout_rationale_residue": r"(?:This\s+page\s+)?breaks?\s+the\s+(?:answer[-\s]?key|table)\s+rhythm|breaks?\s+the\s+answer[-\s]?key\s+rhythm|打断(?:答案|表格|answer[-\s]?key)[^。\n]{0,20}(?:节奏|连页)|版式修复|页面节奏修复",
    "overstrong_inference_wording": r"What\s+must\s+be\s+true(?:\s+in\s+the\s+text)?|Which\s+line\s+must\s+be\s+true|Find\s+one\s+line\s+that\s+must\s+be\s+true",
    "fake_exam_blank_placeholder": r"\(blank\)",
    "student_stage_meta_label": r"\bStage\s+[1-4]\b|\bUnit\s+Review\b",
}


def line_for_pos(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def scan(text: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for name, pattern in HARD_PATTERNS.items():
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            line = line_for_pos(text, match.start())
            errors.append(f"{name}: line {line}: {match.group(0)}")

    for name, pattern in SOFT_PATTERNS.items():
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            line = line_for_pos(text, match.start())
            warnings.append(f"{name}: line {line}: {match.group(0)}")

    has_schedule_context = re.search(
        SOFT_PATTERNS["student_schedule_leak"], text, flags=re.IGNORECASE
    )
    minute_range_number = r"(?:0|0?[1-9]|[1-9]\d|1[01]\d|120)"
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not re.fullmatch(fr"{minute_range_number}\s*[-–—]\s*{minute_range_number}", stripped):
            continue
        warnings.append(f"student_schedule_leak: line {line_no}: {stripped}")

    return errors, warnings


def read_input(path_arg: str) -> str:
    if path_arg == "-":
        return sys.stdin.read()
    return Path(path_arg).read_text(encoding="utf-8")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="File to validate, or '-' for stdin")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    args = parser.parse_args(argv[1:])

    text = read_input(args.path)
    errors, warnings = scan(text)

    if errors:
        print("FAIL")
        for error in errors:
            print(f"- ERROR {error}")
        for warning in warnings:
            print(f"- WARN {warning}")
        return 1

    if warnings:
        label = "FAIL" if args.strict else "PASS_WITH_WARNINGS"
        print(label)
        for warning in warnings:
            print(f"- WARN {warning}")
        return 1 if args.strict else 0

    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
