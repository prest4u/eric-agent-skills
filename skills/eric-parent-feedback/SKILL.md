---
name: eric-parent-feedback
description: 'Use when writing, revising, auditing, or saving Eric''s parent-facing post-class feedback for one-to-one or class/group courses as copy-ready TXT. Trigger for 课后反馈, 家长反馈, 学生反馈, 班课反馈, 一对一反馈, 试听课反馈, 课后总结发家长, 去 AI 味反馈, and converting lesson notes into a polished Chinese parent message. Determine the format from the course type, never the number attending: a class course with only one student still uses class metadata and structure. Must enforce exactly three visible plain-text sections: ①课上内容, ②课上反馈, ③课后作业, with no Markdown headings, no fourth section, no next-lesson preview, and no internal teaching labels.'
---

# Eric Parent Feedback

Write parent-facing post-class feedback that is concrete, calm, credible, and ready to paste into a parent group.

This skill is not a general article polish skill. It protects Eric's feedback contract:

```text
①课上内容
②课上反馈
③课后作业
```

No Markdown headings. No fourth section. No next-lesson direction or preview. No internal teaching labels.

## First Move

Classify the course before drafting. The governing rule is:

> Course type decides the format; attendance count does not. A one-to-one course uses the individual format. A class/group course uses the class format even when only one student is enrolled or present that day.

Use explicit course labels such as `班课`, `暑假班`, `寒假班`, `春季班`, `秋季班`, `预科班`, `小班`, or `集体课` as strong class-format signals. Do not reinterpret a named class as one-to-one merely because only one student is listed.

Then classify the task:

| Task | Action |
|---|---|
| One-to-one course feedback | Use `学生：` metadata and write that student's lesson content, performance, and homework |
| Class/group course feedback | Use `班级：` plus `学生：` metadata; write shared course content, then give each student's情况说明 inside `②课上反馈`. Keep this format even when there is only one student. |
| Raw lesson notes -> feedback | Build a clean parent-facing draft |
| Existing feedback -> 去 AI 味 | Preserve facts and structure; remove template tone |
| Feedback audit | Check structure, forbidden terms, specificity, tone |
| Save feedback file | Save a copy-ready `.txt` record in the existing student feedback folder |

If local paths are relevant, inspect the actual lesson notes, worksheets, prior feedback, or student folder before writing. Do not rely on memory alone when files are available.

## Required Output Shape

Default output is plain TXT, not Markdown. First decide whether the course itself is one-to-one or class/group. Never decide from the number of students named in the lesson record.

One-to-one course lesson:

```text
学生：
日期：
课次 / 主题：

①课上内容

[2-4 natural paragraphs or short bullets about what was actually done]

②课上反馈

[specific student performance: strengths, real problems, learning state, what is becoming more stable]

③课后作业

[numbered homework tasks, written so parent/student can execute]
```

Class/group course lesson, including a class with one student:

```text
班级：
学生：
日期：
课次 / 主题：

①课上内容

[shared class content actually completed]

②课上反馈

[student A：specific情况说明]

[student B：specific情况说明]

[optional short whole-class note if it adds real information]

③课后作业

[numbered homework tasks, written so parent/student can execute]
```

Use this exact visible section structure. Do not output Markdown `##`, `一、课程内容`, `二、学生表现`, `下节课安排`, `内部路由`, `老师观察`, `补充建议`, or any fourth section in the parent-facing final.

## Workflow

1. **Gather facts**
   - course type: one-to-one or class/group; treat explicit class naming as authoritative
   - class name when the course is class/group, even if only one student attended
   - student name / EC id if known
   - date
   - class topic
   - completed content
   - student performance evidence
   - homework
   - source files or raw notes used

2. **Separate visible vs internal**
   - Visible: what was learned, how the student performed, what to do after class.
   - Internal only: teacher moves, diagnostic traps, route labels, MBTI, "挖坑", production notes, future lesson strategy.

3. **Write with parent-facing specificity**
   - Name the exact skill or score scene: 完成句子、单项选择、词形变化、阅读证据定位、主谓宾、主系表.
   - Convert problems into stable learning actions: "还需要继续稳定..." instead of harsh labels.
   - Tie praise to evidence: "能先判断词性再看上下文" instead of "表现很好".

4. **De-AI pass**
   - Read `references/style-guide.md` for tone and anti-template rules.
   - Borrow the de-AI stack as roles: `shuorenhua` for scene and protected spans, `deslop-zh` for final subtraction, `remove-ai-flavor/de-AI-writing` for local sentence shells, `qu-ai-wei` for not damaging real teacher voice, and `humanizer-zh` only as broad audit.
   - Remove empty summary, grand claims, fake warmth, and repeated route markers.
   - Keep language natural but not chatty; parent feedback should feel professional and human.

5. **Validate before final**
   - If a file exists or is created, run:

```bash
python3 ./scripts/validate_feedback.py path/to/feedback.txt
```

   - If only replying in chat, mentally apply the same checks and say if anything is missing.

## File Handling

When saving a new feedback file, prefer the existing feedback root:

```text
<project-dir> Course/teaching-workspace/projects/english-courses/feedback
```

Use the existing student folder when present. File name pattern:

```text
EC-xxx-name-feedback-YYYY-MM-DD-lesson.txt
```

The saved `.txt` is the sending record: Eric should be able to open it, copy all text, and paste directly into the parent group. If the student folder or EC id is unclear, ask only if saving depends on it; otherwise draft in chat as copy-ready TXT.

After saving a copy-ready `.txt`, always paste the full final TXT content back into chat so Eric can copy it directly, unless he explicitly says not to paste it.

## Hard Gates

Reject or revise before final if any gate fails:

- Exactly three visible plain-text sections: `①课上内容`, `②课上反馈`, `③课后作业`.
- Metadata matches the course type, not headcount: one-to-one feedback uses `学生：`; class/group feedback uses `班级：` and `学生：`, with per-student情况说明 under `②课上反馈`.
- A named class/group course must never be downgraded to one-to-one format because only one student is enrolled, listed, or present.
- No Markdown headings such as `##`.
- No fourth section after homework.
- No next-lesson preview, route, or "下节课会..." in the parent-facing final.
- No internal labels: MBTI, Hermes, T1/B01/B02, 后台, 路由, 维修层, validator, teacher moves.
- No teacher-tactic wording: `挖坑`, `让学生先错`, `教师动作`, `预期回应`, `心法`, `出招`, `拆招`, `定招`.
- No invented performance, homework, scores, sources, or family/student details.
- No AI-detection promise.

## References

- `references/style-guide.md`: parent-facing tone, anti-AI wording, common repairs.
- `scripts/validate_feedback.py`: deterministic structure and forbidden-term validator.
