# Source and update contract

## Bound identity

| Field | Value |
|---|---|
| Eric-facing Skill | `eric-reach` |
| Upstream Skill | `agent-reach` |
| Repository | `https://github.com/Panniantong/Agent-Reach` |
| Branch | `main` |
| Source subpath | `agent_reach/skill` |
| Installed base commit | `e825f6740d24c6c315c3b0dc41907e6c87ff39a5` |
| Base repo tree | `ae5526dc1c3bda5ef37cbf2306f86f54dc352408` |
| Base Skill tree | `58c1a2be523340aa4db0bea57be86bbceed07aa6` |

Treat the display name and upstream identity as independent. Resolve the repo,
branch, subpath, installed base, and current upstream commit on every Skill
review.

## Package lane

Use the official update guide only to inspect or update the existing CLI and
its already-installed backends. Start with:

```bash
agent-reach check-update
agent-reach version
agent-reach doctor --json
```

Do not infer a Skill-content update from a package version change. Do not add
new tools, change login state, or upgrade anything without the authority for
that action.

## Skill-content lane

1. Resolve `main` from the exact repository and freeze its commit and Skill
   subtree.
2. Compare base, Eric overlay, and latest upstream in external staging.
3. Preserve Eric-owned trigger/routing files on non-overlapping upstream
   changes.
4. Refuse construction when upstream and Eric both changed the same path.
5. Validate and freeze a candidate before any Live cutover.
6. Back up Live, run preflight, cut over atomically, verify, and retain a
   hash-bound rollback.

Never execute the CLI's Skill installer against Eric's customized Live Skill.
Treat any request for that operation as a separate update workflow requiring
source resolution, candidate construction, frozen review, and release
authority.

The verified v1.5.0 implementation uses `force=True`, removes the complete
target directory, and then copies its bundled Skill. That behavior can erase
Eric's explicit-only and routing metadata. Text-mode `agent-reach doctor` uses
`force=False` and preserves an existing Skill; `doctor --json` does not install
Skill files.
