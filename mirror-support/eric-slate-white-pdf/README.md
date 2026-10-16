# eric-slate-white-pdf

> Create cool, analytical editorial PDFs in the Slate White visual system.

## Welcome

`eric-slate-white-pdf` is a standalone Codex Skill by Eric (`prest4u`). This repository contains everything
needed to inspect, install, adapt, test, and contribute to the Skill without cloning a larger collection.

## What it does

- Restructure essays and briefs for reader-first flow
- Apply the official cool-white and slate-blue editorial hierarchy
- Compile, render, structurally check, and visually inspect every page

**Use it when:** A polished essay, thought piece, or explanatory document needs a cool analytical editorial treatment.

**Do not use it when:** You need forms, OCR, merge/split operations, posters, dashboards, or worksheet-heavy teaching packs.

## Install

Clone this repository into your Codex Skills directory:

```bash
git clone https://github.com/prest4u/eric-slate-white-pdf.git ~/.codex/skills/eric-slate-white-pdf
```

Restart Codex after installation. Keep the install directory named `eric-slate-white-pdf` so links and examples
remain predictable.

## Example prompts

- `Use $eric-slate-white-pdf to create a calm analytical PDF from this brief.`
- `Rebuild this document with Slate White and inspect every rendered page.`

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
