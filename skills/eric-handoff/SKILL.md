---
name: eric-handoff
description: 【任务交接】Create or consume a lightweight, evidence-backed Eric Handoff when Eric explicitly asks to transfer work to another Codex task, pause for later resumption, generate a project state snapshot, or continue from an existing Eric Handoff. Do not use for ordinary status reports, routine completion summaries, same-task context compaction, or merely because a task is long.
---

# Eric Handoff

Preserve momentum across tasks with the smallest useful transfer. Treat a handoff as a bridge, not a ceremony.

## Choose the operation

- **Create:** Eric explicitly asks for a handoff, transfer, pause-and-resume brief, or project state snapshot.
- **Resume:** Eric supplies an Eric Handoff or explicitly asks to continue from one.

Do not turn an ordinary wrap-up into a handoff. Codex context compaction inside the same task does not require one.

## Create

1. Identify the goal, completed state, first next action, essential constraints, and any blocker.
2. Inspect only evidence needed to resume safely. Prefer the relevant diff or artifact, current repository status when applicable, and already-recorded checks. Run a cheap read-only check only when it resolves a critical ambiguity.
3. Reuse durable paths, commits, plans, issues, or specifications instead of copying their contents.
4. Prepare one compact, paste-ready report. Return it in chat by default; when Eric explicitly asks to send it to a named task, use it as the single transfer payload and confirm the transfer concisely in the current task. Do not append a second continuation prompt that repeats it.
5. Save a file, create or message another Codex task, or invoke a native handoff action only when Eric explicitly requests that action. Do not create a new task unless he explicitly asks for one.

Do not rerun broad tests, repair unfinished work, create QA packets, or perform a general audit merely to improve the handoff. A handoff records the state; it does not delay the task to manufacture a cleaner state.

### Default report

Use this shape, omitting empty sections:

```markdown
# Eric Handoff: <workstream>

**Goal:** <one sentence>

**State**
- <up to five resumption-critical facts>

**Continue with**
1. <first imperative action>
2. <at most two additional actions>

**Evidence**
- `<path, commit, or exact command>` — <concise relevance or result>

**Watchouts**
- [UNVERIFIED] <only an uncertainty that can change the next action> — Verify with: <specific check>
```

Keep the default report to one screen: normally no more than eight bullets and three next steps. The handoff itself must tell the next task to continue the work; never begin it with `Use $eric-handoff`, which would create a handoff loop.

### Evidence depth

- Use plain factual bullets when current inspected evidence supports them.
- Mark only consequential uncertain claims `[UNVERIFIED]` and give the smallest concrete verification step.
- Describe a check as passing only when its exact command and result were inspected in the current task or exist in a clearly identified durable record. Otherwise say `not run` or `result not current`.
- Redact secrets, credentials, private URLs, and unnecessary personal data. Do not open secret stores for the handoff.
- For a formal, security-sensitive, migration, destructive, deployment, or publication transfer, include the exact artifact identity and missing mandatory evidence. Stay concise; the handoff does not itself authorize or sign off the action.

## Native task transfer

When Eric asks to send the handoff to a named Codex task, prefer the available native task handoff or messaging capability. Send the compact report once and avoid duplicating it in multiple tasks. If the destination is ambiguous, return the report in chat and identify the missing destination rather than guessing.

## Resume

1. Treat the supplied handoff as historical evidence, not automatically current truth.
2. Read the cited durable artifacts and verify only state that may have changed enough to affect the first action.
3. Start the recorded first action promptly. Do not rewrite the handoff, repeat completed work, or rerun every listed check by default.
4. Preserve stated constraints and unrelated user work. Ask only when a missing choice materially changes scope, cost, irreversibility, external impact, or the kind of result.

## No workflow tax

- Treat invocation as workflow guidance, not authority to act. Without separate authority in the active prompt, do not create, message, or archive a task; spawn agents or reviewers; enter Project mode; create Goals or reminders; write files; or take external action.
- Never issue proactive handoff reminders.
- Never create a Goal, enter Project mode, spawn agents, request review, write a workspace report, commit, push, publish, or send externally solely because this skill was invoked.
- Never require every sentence to carry a verification label or force empty template sections.
- Keep handoff preparation bounded; in Resume mode, continue with the first action promptly.
