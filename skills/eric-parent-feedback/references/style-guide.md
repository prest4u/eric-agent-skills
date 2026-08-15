# Parent Feedback Style Guide

Use this file when drafting or de-AI-polishing parent-facing TXT feedback.

## Tone

Good feedback sounds like a teacher who actually taught the class:

- specific, not decorative
- calm, not anxious
- honest, not harsh
- warm, not intimate
- professional, not template-like

Default register: concise Chinese, medium density, direct. The final text should look like a message a real teacher can paste into a parent group, not like a Markdown document.

## What Parents Need

Every feedback should answer only three questions:

1. 今天课上做了什么？
2. 孩子今天表现出什么稳定点和问题点？
3. 回去具体做什么？

Anything about future route, internal diagnosis, or teacher strategy belongs outside the parent-facing final.

## Section Guidance

### ①课上内容

Write what actually happened. Good ingredients:

- module or score scene
- concrete knowledge points
- actual practice type
- correction focus
- why this task matters for the exam or course stage

Avoid:

- copying the lesson plan mechanically
- listing too many internal activity names
- saying "系统化/全面/深度" without concrete content
- Markdown formatting such as `##`, horizontal rules, tables, or bold markers in the final TXT

### ②课上反馈

Write evidence-based performance.

Use:

- "今天比较稳定的是..."
- "目前还需要继续巩固的是..."
- "从课堂表现看..."
- "这说明前面训练已经有了一定积累..."
- "问题不在于完全不会，而是..."

But do not overuse these shells. Rewrite if every paragraph has the same pattern.

Avoid:

- "孩子表现非常棒" without evidence
- "基础很差" as a label
- vague comfort: "相信一定会越来越好"
- pressure language: "必须马上补上，否则..."
- private psychology: "说明孩子内心..."

### ③课后作业

Make homework executable:

- use numbered tasks
- include exact topic, page, file, or exercise type when known
- say what to check: 词性、时态、短语结构、证据定位、错题原因
- if homework is light, say "重点不是刷量，而是把今天的动作做稳"

Do not add a next-lesson plan. A homework check instruction is allowed only if it is framed as what the student should review, not what the next lesson will do.

## Anti-AI Repairs

Replace template language with observable classroom language:

| AI/template | Better direction |
|---|---|
| 本节课围绕...展开，进行了系统梳理 | 今天主要复习/训练了... |
| 学生整体表现良好 | 今天孩子能在...上跟住节奏 |
| 具有较强的学习能力 | 在...题型里，反应速度比之前更稳 |
| 需要进一步加强 | 还需要继续稳定... |
| 为后续学习打下坚实基础 | 这个动作稳定后，后面做...会更顺 |
| 望继续努力 | 删除，改成具体作业 |
| 下节课将继续 | 删除，不写下一课预告 |

Use the researched de-AI rules as a division of labor:

- `shuorenhua`: protect facts, terms, student evidence, and parent-facing register before rewriting.
- `deslop-zh`: final subtraction; delete empty summary, false uplift, and decorative transitions.
- `remove-ai-flavor` / `de-AI-writing`: patch repeated shells like `本节课围绕...展开`, `整体表现良好`, `进一步加强`.
- `qu-ai-wei`: do not sterilize Eric's real teacher voice; keep a little natural specificity.
- `humanizer-zh`: broad audit only; do not inject personal anecdotes or dramatic "soul".

## Forbidden Visible Content

Never include in parent-facing feedback:

- MBTI or personality typing
- Hermes, memory, internal project names
- "挖坑", "让学生先错", "教师动作", "预期回应"
- "心法", "出招", "拆招", "定招"
- T1/B01/B02 or any backend routing label
- "后台", "路由", "维修层", "validator", "生产"
- "下节课计划", "下节课会", "下一步课程安排", "后续路线"

## Quality Readback

Before finalizing:

1. Can a parent tell what happened today without seeing the lesson plan?
2. Is every praise connected to classroom evidence?
3. Is every problem written as an actionable learning task?
4. Is homework specific enough to execute?
5. Are there exactly three visible plain-text sections?
6. Can Eric copy the whole TXT directly into a parent group without deleting Markdown marks?
