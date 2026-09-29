# video-production-stack

> Route a video project to its next visible, verifiable production artifact.

## Welcome

`video-production-stack` is a standalone Codex Skill by Eric (`prest4u`). This repository contains everything
needed to inspect, install, adapt, test, and contribute to the Skill without cloning a larger collection.

## What it does

- Identify the current production stage and smallest useful next output
- Coordinate scripts, preproduction, composition, rendering, and QA without forcing the full chain
- Preserve rights, privacy, overwrite, and publication boundaries

**Use it when:** You explicitly invoke the Skill to move a real video project from its current artifact to the next visible stage.

**Do not use it when:** A single specialist stage already has a better owner or the request does not authorize file, account, paid, or publication actions.

## Install

Clone this repository into your Codex Skills directory:

```bash
git clone https://github.com/prest4u/video-production-stack.git ~/.codex/skills/video-production-stack
```

Restart Codex after installation. Keep the install directory named `video-production-stack` so links and examples
remain predictable.

## Example prompts

- `Use $video-production-stack to turn this approved script into the next inspectable preproduction artifact.`
- `Route this rendered video through QA and prepare—but do not publish—the release candidate.`

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
