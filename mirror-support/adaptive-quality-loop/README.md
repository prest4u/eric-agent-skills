# adaptive-quality-loop

> Match implementation rigor to BUILD, PROOF, or RELEASE risk.

## Welcome

`adaptive-quality-loop` is a standalone Codex Skill by Eric (`prest4u`). This repository contains everything
needed to inspect, install, adapt, test, and contribute to the Skill without cloning a larger collection.

## What it does

- Keep ordinary work output-first and lightweight
- Use reversible proofs when one assumption could cause material rework
- Require frozen identities and independent review for external or high-impact releases

**Use it when:** A durable implementation, multi-file change, formal validation, migration, deployment, or publication needs proportionate quality gates.

**Do not use it when:** You only need advice, explanation, status, or a narrow read-only answer.

## Install

Clone this repository into your Codex Skills directory:

```bash
git clone https://github.com/prest4u/adaptive-quality-loop.git ~/.codex/skills/adaptive-quality-loop
```

Restart Codex after installation. Keep the install directory named `adaptive-quality-loop` so links and examples
remain predictable.

## Example prompts

- `Use $adaptive-quality-loop to implement this change with the smallest sufficient verification.`
- `Prepare this exact commit for release and keep reviewer sign-off separate from publication.`

## Current invocation

Invoke this Skill explicitly for a consequential uncertainty, missing verification, or repeated failure. Ordinary implementation tasks do not invoke it automatically. Host and task policy controls authorization, review, and completion.

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
