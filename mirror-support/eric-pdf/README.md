# eric-pdf

> Adapt defined classroom content into freshly verified Typst A4 PDFs.

## Welcome

`eric-pdf` is a standalone Codex Skill by Eric (`prest4u`). This repository contains everything
needed to inspect, install, adapt, test, and contribute to the Skill without cloning a larger collection.

## What it does

- Start from the bundled restrained A4 Typst adapter
- Compile a fresh PDF and check profile-specific text leaks
- Render and inspect cover, body, dense, and final pages

**Use it when:** You explicitly want the Eric Typst A4 adapter or QA pass for an already-defined classroom document.

**Do not use it when:** You need teaching-content authorship, a long textbook system, or generic PDF manipulation.

## Install

Clone this repository into your Codex Skills directory:

```bash
git clone https://github.com/prest4u/eric-pdf.git ~/.codex/skills/eric-pdf
```

Restart Codex after installation. Keep the install directory named `eric-pdf` so links and examples
remain predictable.

## Example prompts

- `Use $eric-pdf to adapt this completed worksheet into an A4 Typst PDF.`
- `Run the Eric PDF QA workflow on this Typst source and inspect the required pages.`

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
- `assets/` and `templates/` — reusable source assets when present; bundled demo PDFs and rendered previews are included; user-generated deliverables are excluded.

## Validation

Before changing the Skill, run the package's existing tests and validators. At minimum, validate `SKILL.md`
structure and confirm every local reference exists. A passing script does not replace visual, runtime, source,
or independent-review evidence when the Skill explicitly requires those gates.

## Safety and privacy

Do not commit credentials, account state, private task transcripts, personal records, student/customer data,
local absolute paths, caches, or user-generated deliverables. Invocation guides workflow; it does not grant authority
to publish, deploy, spend money, overwrite files, access accounts, or perform destructive actions.

## Contributing

Issues and pull requests are welcome. Describe observable behavior, use synthetic fixtures, preserve public
triggers unless a breaking change is intentional, and include the smallest check that proves the change.

## License

MIT — see [`LICENSE`](LICENSE).
