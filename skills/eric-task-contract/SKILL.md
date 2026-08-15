---
name: eric-task-contract
description: Manually compile Eric's intent into a bounded Codex task brief or, only when the active prompt explicitly authorizes it, a native task/thread dispatch message. Use only through explicit $eric-task-contract invocation for drafting a reusable execution brief, creating a new Codex task, or updating an identified existing task. Do not use for handoffs or resumption snapshots, ordinary prompt writing, status reports, or direct implementation requests.
---

# Eric Task Contract

Turn settled intent into a compact, copy-ready task brief. Normally return one screen.

## Respect the action boundary

Treat invocation as authority to compile, not to act elsewhere.

- **Brief:** Draft and return the contract. Never create or message a task merely because Eric asked for a prompt or brief.
- **New task:** Create or dispatch only when the active prompt explicitly asks for that action.
- **Existing task:** Message only the identified task when the active prompt explicitly asks. Classify the payload as `ADDENDUM` or `SUPERSEDE` before sending.

Use the current host-provided task/thread capability at action time. Treat “task,” “thread,” and “chat” as surface-dependent names for the conversational unit. Do not emit raw UI directives or invent a successful action. If an explicitly requested native action or required target is unavailable, return the compiled brief and name the capability or identity gap.

## Keep neighboring work separate

- For a transfer or resumption snapshot of work already in progress, use Eric Handoff.
- For ordinary writing prompts, write the prompt normally.
- For a request to implement, inspect, explain, or report in the current task, do that work directly; do not add task-contract ceremony.
- Do not turn a task brief into durable `AGENTS.md` policy or Project structure. Those require separate intent and authority.

If explicit invocation conflicts with one of these boundaries, explain the mismatch briefly and follow the correct surface. Ask one focused question only when a missing choice materially changes the outcome, owned artifact, authority, or destination.

## Compile the brief

Derive settled details from the request and authoritative workspace context. Never return a blank intake form. Include:

```text
Outcome: <one observable end condition>

Authoritative inputs: <governing sources and target context>

Owned deliverable: <one inspectable artifact, workstream, or target task>

Boundaries:
- Allowed: <minimum reads, writes, tools, and messages needed>
- Do not touch: <unrelated files, systems, identities, and external actions>

Done evidence: <smallest checks that prove the exact deliverable meets the request>

Return: <concise status, artifact references, evidence, and unresolved gaps>
```

Keep only details that change execution. Preserve exact paths, frozen identities, permissions, and explicit exclusions. Do not add model or effort choices, controller/writer roles, review chains, recovery fingerprints, mandatory planning, or automatic task creation unless the active prompt or governing instructions independently require them.

## Message an existing task

- Use `ADDENDUM` when the current outcome remains valid and the message clarifies or narrows it. Preserve existing boundaries and authority unless Eric explicitly changes them.
- Use `SUPERSEDE` only when Eric explicitly replaces prior instructions. State that the prior conflicting instruction is revoked, then provide the complete replacement brief.

If a proposed message conflicts with the existing task and Eric has not made replacement intent clear, ask whether to add or supersede instead of guessing.

After an authorized native action, report the task identity or message result once. Do not duplicate the full payload unless the action failed.
