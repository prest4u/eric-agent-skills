# eric-teaching-polish

> Revise classroom language and explicitly requested exercises while preserving meaning and answer accuracy.

## Welcome

`eric-teaching-polish` is a standalone Codex Skill by Eric (`prest4u`). This repository contains everything
needed to inspect, install, adapt, test, and contribute to the Skill without cloning a larger collection.

## Current scope

Apply local wording corrections to the supplied sentence, activity, page or pack. When the user explicitly requests an exercise-quality rebuild, revise prompts, answers and teacher guidance together while retaining the learning target and suitable difficulty. Read SKILL.md for the current scope and checks.

## What it does

- Protect real teaching facts while rewriting visible language
- Keep student, parent, teacher, and public surfaces appropriately separated
- Validate teaching text for internal labels, production residue, and cross-package leaks

**Use it when:** A supplied teaching text needs clearer classroom language, or you explicitly request an exercise-quality rebuild with matching answers and teacher guidance.

**Do not use it when:** The request is pure parent post-class feedback or requires inventing unsupported teaching facts.

## Install

Clone this repository into your Codex Skills directory:

```bash
git clone https://github.com/prest4u/eric-teaching-polish.git ~/.codex/skills/eric-teaching-polish
```

Restart Codex after installation. Keep the install directory named `eric-teaching-polish` so links and examples
remain predictable.

## Example prompts

- `Use $eric-teaching-polish to remove backstage language from this student handout.`
- `Polish this teacher-generated draft and run the strict visible-language validator.`

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
