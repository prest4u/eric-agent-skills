# Repository Rules

- `skills/` is the canonical source for every published skill.
- Keep every skill independently installable. Do not create mandatory cross-skill runtime dependencies.
- Never merge the five PDF skills. Collections are metadata only.
- Do not commit personal paths, credentials, student/client identities, private fixtures, or unlicensed assets.
- Edit upstream-managed material only through `scripts/sync_upstreams.py`; local policy remains outside `references/upstream/`.
- Mirror repositories are generated one-way from this repository. Bring manual mirror changes back here first.
- Run `python3 scripts/validate_repo.py` before committing.
