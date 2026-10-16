# Source and update contract

## Bound identity

| Field | Value |
|---|---|
| Eric-facing Skill | `eric-reach` |
| Upstream Skill | `agent-reach` |
| Repository | `https://github.com/Panniantong/Agent-Reach` |
| Branch | `main` |
| Source subpath | `agent_reach/skill` |
| Installed base commit | `da5044d26fc6adddb6554d5679c94ac22e76e428` |
| Base repo tree | `e83408fd641475489c283537dc85da38af666810` |
| Base Skill tree | `5095f2b6ccc6a0cdda1ad4cbf067ad279a418d95` |

Treat the display name and upstream identity as independent. Resolve the repo,
branch, subpath, installed base, and current upstream commit when reviewing
upstream provenance or integrating an upstream update. A local Eric-owned
wording, routing, or runtime fix does not require fetching the latest upstream
or starting the package/Skill upgrade lane. Validate its affected behavior and
preserve the bound provenance until an actual update changes it.

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
4. Three-way merge using the previous upstream, current Eric overlay, and
   latest upstream. Eric explicitly authorized matching and merging local
   customizations on 2026-09-06. Same-path changes require semantic comparison,
   not automatic rejection. Preserve local triggers, language, privacy rules,
   read-only access, local ASR, and runtime locks. Resolve compatible changes;
   stop only for an unresolved substantive conflict. Never replace the whole
   directory with upstream defaults.
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

The Eric overlay also owns `references/douyin.md` and
`scripts/douyin_intake.py`. Future upstream comparisons must retain this
fixed-domain, headless Chromium, local MLX Whisper route unless Eric explicitly
retires it. An upstream generic downloader does not replace its host checks,
access-block stop conditions, local-model requirement, or no-Chrome-app rule.

The Douyin route was added after reviewing two MIT-licensed public Skills:
`LiuZheng60/douyin-transcribe-lz` at
`632ebb1af805ddb57ac748d824c78b6254a5f6ce` and
`crazyooo/douyin-video-downloader-skill` at
`5fb8169bee07b8b56cc1122ebf9ae2fa7b70b9d3`. The Eric implementation uses its
own fixed host checks and existing Python Playwright/MLX runtimes; it excludes
the first repository's automatic model/browser installation and retries, and
the second repository's Chrome app launch and npm installation.

## Integration record (2026-09-06)

The bound commit is the upstream reviewed for this customized integration, not
an assertion that every upstream file was copied. The local overlay retains
its single English Skill entrypoint, connector-first routing, strict account
policy and local video pipeline. It incorporates upstream's truthful video
verification guidance and shell-safe Exa invocation. Upstream's cloud-ASR,
credential import, extra retries, new finance route and automatic installation
behavior remain excluded by the Eric overlay. Career and social routing keep
the current installed-adapter contract. Save the full three-way comparison,
frozen candidate hashes, runtime versions, checks and rollback next to each
local maintenance transaction; advance the successful baseline only after
verification.
