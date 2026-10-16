# eric-handoff

> Create compact, evidence-backed handoffs between Codex tasks.

## Welcome

`eric-handoff` is a standalone Codex Skill by Eric (`prest4u`). This repository contains everything
needed to inspect, install, adapt, test, and contribute to the Skill without cloning a larger collection.

## What it does

- Capture the goal, current state, first next action, and real blockers
- Reference durable files, commits, and checks instead of copying long context
- Resume from a handoff without repeating completed work

**Use it when:** You explicitly need to transfer work, pause for later, or resume from an existing Eric Handoff.

**Do not use it when:** You only need an ordinary status update, completion summary, or same-task context compaction.

## Install

Clone this repository into your Codex Skills directory:

```bash
git clone https://github.com/prest4u/eric-handoff-skill.git ~/.codex/skills/eric-handoff
```

Restart Codex after installation. Keep the install directory named `eric-handoff` so links and examples
remain predictable.

## Example prompts

- `Use $eric-handoff to prepare a one-screen handoff for this workstream.`
- `Resume from this Eric Handoff and start with its first verified next action.`

## How it works

Read [`SKILL.md`](SKILL.md) for the authoritative trigger boundary, workflow, stop conditions, and completion
contract. The Skill loads only the references required by the active task and uses bundled scripts or templates
where they provide reproducible behavior.

## Repository guide

- `SKILL.md` — authoritative agent instructions.
- `agents/openai.yaml` — discoverability metadata when present.
- `references/` — focused operating guidance loaded only when relevant.
- `scripts/` — validators, builders, or deterministic helpers when present.
- `tests/` and `test-prompts.json` — contract and regression coverage when present.
- `assets/` and `templates/` — reusable source assets when present; generated deliverables are excluded.

## Validation

Before changing the Skill, run the package's existing tests and validators. At minimum, validate `SKILL.md`
structure and confirm every local reference exists. A passing script does not replace visual, runtime, source,
or independent-review evidence when the Skill explicitly requires those gates.

## Safety and privacy

Do not commit credentials, account state, private task transcripts, personal records, student/customer data,
local absolute paths, caches, or generated deliverables. Invocation guides workflow; it does not grant authority
to publish, deploy, spend money, overwrite files, access accounts, or perform destructive actions.

## Contributing

Issues and pull requests are welcome. Describe observable behavior, use synthetic fixtures, preserve public
triggers unless a breaking change is intentional, and include the smallest check that proves the change.

## License

MIT — see [`LICENSE`](LICENSE).
