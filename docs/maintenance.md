# Maintenance and release

The hub repository is the only editable source. Mirror repositories are generated outputs.

## Upstream updates

`catalog/upstreams.lock.json` records source paths, exact commits, tree hashes, license evidence hashes, sync mode, and target skills. Machine-managed snapshots live only under `references/upstream/<source>/`; an update never rewrites Eric-owned `SKILL.md` files.

The weekly workflow creates a review-only pull request after repository validation and a pinned SkillSpector scan. It blocks path escapes, symlinks, large files, local snapshot drift, changed license evidence, and high or critical security findings. It never auto-merges. When license evidence is a README, only the License section is hashed, so unrelated README edits do not fail the job.

## Mirror bootstrap and sync

Generate one candidate with:

```bash
python3 scripts/export_mirrors.py --skill eric-pdf --output ./mirror-candidates
```

The first import into an existing mirror must be reviewed as a pull request and applied with `scripts/apply_mirror.py --bootstrap`. Later release automation omits `--bootstrap`; it verifies every previously managed file against `.mirror-manifest.json` and fails on drift. It does not force-push.

Create a fine-grained `MIRROR_PUSH_TOKEN` only after all 18 bootstrap PRs have merged. Limit it to Contents write access on those exact mirror repositories.

## Release identities

- Hub tags: `hub-vX.Y.Z`
- Skill versions: independent SemVer entries in `catalog/skills.yaml`
- Mirror tags: `vX.Y.Z` from the matching skill version

Freeze and review the exact candidate commit before creating a public tag.

## Private fixtures

The public repository never receives credentials for the private fixture repository. Private CI checks out the public hub and runs extended tests in the private repository. Real student or enterprise material may be added only from an exact, explicitly approved file manifest.
