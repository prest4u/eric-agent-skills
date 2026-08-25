# Eric Agent Skills

[简体中文](README.zh-CN.md)

Eric Agent Skills is the canonical, cross-harness home for 64 independently installable workflows covering educational and business documents, PDF design, presentations, websites, video, advisory materials, and delivery quality.

The five PDF skills remain separate packages. Collections only make bulk installation easier; they do not merge behavior or introduce mandatory dependencies.

## Install one skill

Use the open-source `skills` installer and select the target agent id:

```bash
npx -y skills@latest add prest4u/eric-agent-skills \
  --skill eric-pdf \
  --agent codex \
  --copy \
  --yes
```

Validated agent ids are `codex`, `claude-code`, `kimi-code-cli`, `opencode`, and `cursor`. Replace `eric-pdf` with any name in [`catalog/skills.yaml`](catalog/skills.yaml).

Copy mode is the portability default so installation does not depend on symlink support.

If an older global Skill has the same name, some harnesses prefer the global copy over a project-local copy. Remove or upgrade that older copy before acceptance testing; do not create a permanent alias because the machine name is part of the stable API. `skills-lock.json` records the installed source and content hash.

## Native plugin entry points

- Codex: `.codex-plugin/plugin.json`
- Kimi Code CLI: `kimi.plugin.json`
- Claude Code marketplace: `.claude-plugin/marketplace.json`
- OpenCode and Cursor: install individual skills through `npx skills` or copy a skill directory into the product's Agent Skills directory.

## Collections

Eight metadata-only collections are defined in [`catalog/collections.yaml`](catalog/collections.yaml): PDF, professional PDF series, Qingyun PDF series, education, documents, web, video, and workflow.

The `pdf` collection installs five directories, `professional-pdf-series` installs eight, and `qingyun-pdf-series` installs twenty-three standalone document and visual-skin workflows. Collections do not merge behavior or create runtime dependencies. Claude exposes all eight collections as marketplace plugins. For other harnesses, run the fixed install command once per Skill listed in the collection.

## One source across local agents

Use the repository's local sync command to make this checkout the single physical source for Codex, Kimi Code, Kimi Desktop, Cursor, Claude Code, Hermes Agent, OpenCode, Zed, Roo Code, and Cline:

```bash
python3 scripts/sync_user_install.py --apply
```

The command backs up conflicting copies, links the shared `~/.agents/skills/` entries to this checkout, removes higher-priority duplicates, and wires product-specific discovery where needed. Run with `--check` for a non-mutating drift audit or `--update --apply` to fast-forward from GitHub before reconciling the local agent surfaces.

For another Agent Skills-compatible product, register its global Skill root once and rerun the sync:

```bash
python3 skills/eric-catalog/scripts/register_tool_surface.py \
  --name my-agent --mode links --skills-root ~/.my-agent/skills
python3 scripts/sync_user_install.py --apply
```

Use `links` when the product requires its own Skill root. Use `shadows` when it already reads `~/.agents/skills` and its product root should only be checked for higher-priority duplicates. Machine-specific roots stay in `~/.config/eric-agent-skills/tool-surfaces.json`, outside the public repository.

Catalog versions identify the latest **validated** release of each Skill. A newer filesystem timestamp does not win by itself: local paths, private fixtures, unlicensed assets, and regressions are rejected before a version is promoted.

## Maintenance

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate_repo.py
python3 scripts/sync_upstreams.py check
python3 scripts/export_mirrors.py --check
```

Vendored upstream references are pinned by commit and tree hash. Weekly automation can open an update PR, but upstream changes are never merged automatically.

Release, upstream, mirror, and private-fixture procedures are documented in [`docs/maintenance.md`](docs/maintenance.md).
The v1.0 candidate gate matrix is tracked in [`docs/release/hub-v1.0.0-acceptance.md`](docs/release/hub-v1.0.0-acceptance.md).
The cross-agent latest-valid-version decisions for this release are recorded in [`docs/release/v1.2.0-version-audit.md`](docs/release/v1.2.0-version-audit.md).
The extensible tool-surface architecture is recorded in [`docs/release/v1.3.0-tool-authority.md`](docs/release/v1.3.0-tool-authority.md).

## Privacy and licensing

The public repository contains only code, redistributable assets, and anonymized fixtures. Real student or client regression material belongs in the separate private fixture repository and is never required to install a skill.

Original and third-party notices are retained in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md). The repository's original code is MIT licensed; files carrying their own license remain under that license.
