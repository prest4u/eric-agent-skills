# eric-review

> Review, repair, or formally sign off real artifacts with clear provenance.

## Welcome

`eric-review` is a standalone Codex Skill by Eric (`prest4u`). This repository contains everything
needed to inspect, install, adapt, test, and contribute to the Skill without cloning a larger collection.

## What it does

- Run concise read-only reviews focused on correctness and usability
- Review and fix an authorized artifact in one bounded loop
- Provide independent formal sign-off for frozen high-impact candidates

**Use it when:** You explicitly ask to review, audit, critique, review-and-fix, or formally sign off an existing artifact.

**Do not use it when:** No inspectable artifact exists or review was not requested.

## Install

Clone this repository into your Codex Skills directory:

```bash
git clone https://github.com/prest4u/eric-review.git ~/.codex/skills/eric-review
```

Restart Codex after installation. Keep the install directory named `eric-review` so links and examples
remain predictable.

## Example prompts

- `Use $eric-review to review this implementation and lead with P0/P1 findings.`
- `Formally sign off this frozen release candidate without publishing it.`

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
