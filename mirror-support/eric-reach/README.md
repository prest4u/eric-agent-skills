# eric-reach

> Safely acquire public web, social, video, and development sources for downstream work.

## Welcome

`eric-reach` is a standalone Codex Skill by Eric (`prest4u`). This repository contains everything
needed to inspect, install, adapt, test, and contribute to the Skill without cloning a larger collection.

## What it does

- Route public URLs to the safest available retrieval method
- Normalize video intake while redacting sensitive query parameters
- Separate source acquisition from later research judgment

**Use it when:** You need to open, retrieve, inspect, or understand a public URL or video before analyzing it.

**Do not use it when:** The task is local-only synthesis, requires unauthorized account access, or asks to bypass platform controls.

## Install

Clone this repository into your Codex Skills directory:

```bash
git clone https://github.com/prest4u/eric-reach.git ~/.codex/skills/eric-reach
```

Restart Codex after installation. Keep the install directory named `eric-reach` so links and examples
remain predictable.

## Example prompts

- `Use $eric-reach to retrieve this public video and return a source packet.`
- `Open these public URLs, preserve provenance, and report access limitations.`

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
