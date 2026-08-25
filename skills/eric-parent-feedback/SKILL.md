---
name: eric-parent-feedback
description: "【家长反馈】Write, revise, audit, or save Eric's evidence-calibrated parent-facing post-class feedback for one-to-one, class/group, and trial lessons as copy-ready Chinese TXT. Trigger for 课后反馈, 家长反馈, 学生反馈, 班课反馈, 一对一反馈, 试听课反馈, 课后总结发家长, 去 AI 味反馈, and lesson notes converted into a parent message. Course type—not attendance count—decides the format. Enforce exactly three visible sections: ①课上内容, ②课上反馈, ③课后作业."
---

# Eric Parent Feedback

Produce a calm, credible message that lets a parent quickly understand:

1. what happened in class;
2. what the student can do now;
3. the one main difficulty, if one genuinely appeared, and how serious it is;
4. what to do after class.

Prioritize accurate judgment first, relationship warmth second, and visible teacher professionalism third. Show professionalism through calibrated decisions, not long knowledge lists or multiple diagnoses.

## Output Contract

The visible final must be plain TXT with exactly these sections:

```text
①课上内容
②课上反馈
③课后作业
```

No Markdown headings. No fourth section. No next-lesson preview. No internal teaching labels.

Course type decides the format; headcount never does:

- one-to-one course → individual format;
- class/group course → class format, even when one student enrolled or attended;
- trial lesson → individual metadata with trial-specific diagnostic weighting.

Treat labels such as `班课`, `暑假班`, `寒假班`, `春季班`, `秋季班`, `预科班`, `小班`, and `集体课` as strong class-format signals.

## Required Judgment Pass

Before drafting or revising, read [references/editorial-judgment.md](references/editorial-judgment.md). Silently build its private decision card:

- overall mastery;
- one or two observable classroom results;
- one primary issue for the feedback unit, only if it genuinely matters;
- severity;
- independent performance versus response after a reminder;
- lower-priority observations;
- homework status.

Do not print the card or the word “证据” as a framework. It exists only to control emphasis.

Use today's facts in authority order: Eric's explicit description, actual student work from today, same-lesson observation records, then earlier feedback for verified comparison. A lesson plan establishes what was taught, never what the student mastered.

If the main mastery level or severity remains unknown after inspecting available files, ask one decisive question, such as:

> 今天这部分是能够独立完成，还是提醒后才能完成？

Do not send a questionnaire. Do not infer mastery from the handout. Do not manufacture a weakness when the lesson went well.

## Visible Shapes

One-to-one:

```text
学生：
日期：
课次 / 主题：

①课上内容

[2–4 concrete items; stop after the actual content]

②课上反馈

[overall mastery plus one or two observable classroom results]

[one calibrated primary issue only when one exists]

③课后作业

[numbered executable tasks, or a factual no-homework sentence]
```

Class/group, including a class with one student:

```text
班级：
学生：
日期：
课次 / 主题：

①课上内容

[shared content completed]

②课上反馈

[shared result once]

[student A：verified individual difference]

[student B：verified individual difference]

③课后作业

[shared numbered tasks and verified make-up work, or a factual no-homework sentence]
```

For a trial lesson, use the individual shape. Give the main learning need most of the diagnostic space; keep no more than two secondary observations visibly lighter. Do not use a problem list to simulate expertise.

## Drafting Rules

- `①课上内容`: two to four concrete items. Do not add empty summaries such as `这三类题都做了`.
- `②课上反馈`: let a parent cold-read 会不会、卡在哪里、严不严重、是否能独立完成.
- One-to-one feedback normally uses two short paragraphs in section ②.
- Class feedback states shared mastery once, then applies the one-primary-issue budget separately to each named student. Distinct verified difficulties for different students may all appear; never suppress one student to satisfy a message-wide limit. Never repeat generic praise to fill space.
- Shared homework belongs in section ③. Mention partial or missing work under a student only when verified and in neutral language.
- `③课后作业`: write numbered executable tasks when work is assigned. If none is assigned, write one factual sentence such as `本次课无额外作业。`; never invent review work to fill the section. Do not add encouragement, course planning, or the teacher's next move.
- Never invent performance, scores, homework, sources, family details, or student details.

## Tone Pass

Before finalizing, read [references/style-guide.md](references/style-guide.md).

Target register: mostly plain, direct professional Chinese with a smaller amount of restrained written Chinese. It should sound more formal than casual conversation and less bureaucratic than a school report.

Remove:

- chatty filler, scolding, or face-to-face teacher talk;
- administrative abstractions and inflated conclusions;
- repeated `需要 / 仍需 / 还需要` sentence shells;
- knowledge-point repetition inside section ②;
- a minor issue promoted above the overall result.

## Validation

When a feedback file exists, run from this Skill directory:

```bash
python3 scripts/validate_feedback.py path/to/feedback.txt
```

The validator reports hard errors separately from style warnings. Revise every warning unless the exact phrase is deliberately justified by the facts and register. Use `--strict-style` when warnings should fail the command:

```bash
python3 scripts/validate_feedback.py --strict-style path/to/feedback.txt
```

For chat-only output, apply the same checks mentally.

## File Handling

Inside Eric's teaching workspace, prefer the existing:

```text
teaching-workspace/projects/english-courses/feedback/<course-folder>/
```

Use the existing course or student folder when present. Preferred filename:

```text
EC-xxx-name-feedback-YYYY-MM-DD-topic.txt
```

After saving, paste the complete final TXT back into chat unless Eric explicitly asks not to.

## Hard Gates

Revise before final when any gate fails:

- exactly the three required visible plain-text sections;
- metadata matches course type, not attendance count;
- no Markdown headings or fourth section;
- no next-lesson preview or internal route;
- no MBTI, memory-system, internal production-workflow, validator, or teacher-tactic labels;
- no invented claims or AI-detection promise;
- today's mastery is not inferred from content merely taught;
- one main problem at most per feedback unit, with severity supported by today's facts: one for a one-to-one or trial student; for a class, one shared class issue plus at most one verified issue per named student.

## Package Maintenance

- [references/editorial-judgment.md](references/editorial-judgment.md): source authority, private decision card, severity ladder, prominence, and mode rules.
- [references/style-guide.md](references/style-guide.md): register, repair patterns, and final readback.
- `test-prompts.json`: anonymized behavioral regressions; expected results describe decisions, not fixed wording.
- `tests/test_feedback_skill.py`: validator and package-contract tests.
