# hub-v1.0.0 acceptance record

Date: 2026-08-15

This record describes the local release candidate. The annotated release tag must point to the exact commit reviewed for publication; the commit SHA and tree hash are recorded in the reviewer report and GitHub release notes after the candidate is frozen.

## Passed gates

| Surface | Evidence | Result |
| --- | --- | --- |
| Repository contract | `scripts/validate_repo.py` | PASS |
| Open Agent Skills format | OpenAI `quick_validate.py`, all 29 directories | PASS (29/29) |
| Independent installation unit | copy-and-hash test for every catalog entry | PASS (29/29) |
| Bundled Skill tests | `scripts/run_skill_tests.py`, all catalog entries | PASS (29/29) |
| Repository maintenance tests | upstream tree integrity, target/id traversal, mirror divergence, pre-push tag identity, atomic publication, license, conflict, and security-gate tests | PASS (21/21) |
| Security | NVIDIA SkillSpector 2.9.4, pinned commit `5680c2c3008e63c9979bbbe08221ee4c2dcd17ee`, `--no-llm` | PASS: no unsuppressed High/Critical findings |
| Native manifests | Codex validator, `claude plugin validate --strict`, JSON/YAML parsing | PASS |
| Upstream lock | local snapshot tree hashes plus `scripts/sync_upstreams.py check` against GitHub HEAD | PASS: no drift and no updates |
| Mirror generation | `scripts/export_mirrors.py --check` | PASS (18/18) |
| Private extension harness | JSON Schema, exact inventory, empty-placeholder enforcement, boolean authorization, path containment, synthetic fixtures, and public-repository integration | PASS (8/8 plus extended integration) |
| Standalone designed-PDF gate | copied `eric-designed-pdf` without sibling PDF Skills or private Golden fixtures; generated v1/v2 and student/teacher PDFs | PASS: P0/P1 = 0 |

The SkillSpector result is a pinned static scan, not a proof that arbitrary model output is safe. Exact-fingerprint baselines are repository-controlled and are rejected if the scanner version or finding fingerprint changes.

## Artifact acceptance

- `eric-designed-pdf`: anonymous 24-page PDF; render, text, overflow report, page images, and contact sheet inspected.
- `eric-pdf`: anonymous 2-page PDF; render, extraction, pagination, and page images checked.
- `eric-moss-ivory-pdf`: anonymous 8-page PDF; first and final pages visually inspected.
- `eric-slate-white-pdf`: anonymous 8-page PDF; first and final pages visually inspected.
- `eric-pdf-vocabulary`: anonymous 3-page PDF; first and final pages visually inspected.
- `eric-ppt-skill`: editable 2-slide OOXML generated without the optional third-party editor; reopened through `python-pptx`, rendered by LibreOffice, and both rendered pages inspected.
- Teaching, website, video, and workflow representatives completed end-to-end synthetic checks.

The five PDF Skills remain five self-contained directories and five catalog versions. The `pdf` collection is metadata only and introduces no cross-dependency.

## Harness matrix

| Harness | Installer ID accepted | Skill discovery and invocation | Status |
| --- | --- | --- | --- |
| Codex | `codex` | Real invocation returned the documented relative command | PASS |
| OpenCode 1.14.48 | `opencode` | Real invocation completed; an acceptance-only temporary name confirmed same-name precedence behavior | PASS |
| Cursor | `cursor` | Real application discovery and invocation completed from `.agents/skills`; an acceptance-only temporary name confirmed same-name precedence behavior | PASS |
| Claude Code 2.1.211 | `claude-code` | Installation and strict plugin validation passed; bounded real invocation did not complete with the current CLI authentication/runtime state | BLOCKED FOR RELEASE TAG |
| Kimi Code CLI 0.31.1 | `kimi-code-cli` | Installation and `--skills-dir` parsing passed; real invocation requires `/login` or a configured `default_model` | BLOCKED FOR RELEASE TAG |

The public repository and mirror pull requests may be published as reviewed source candidates, but `hub-v1.0.0` must not be tagged as accepted until the two blocked real invocations pass against the frozen candidate.

## Privacy and license boundary

- Public history contains no authorized real student, client, or enterprise fixture.
- The private fixture repository starts with schemas and synthetic data only; its manifest keeps `approved_real_data: false`.
- Local absolute paths, credentials, cookies, nested repositories, caches, build output, and unexplained large files are blocked by repository validation.
- Redistributable fonts retain their OFL license and source records.
- The PPT workflow uses repository-owned portable OOXML generation. The third-party presentation frontend, WASM, and product assets are excluded; its upstream is link-only provenance.
- Anthropic source-available document Skills are referenced but not copied or relicensed.

## Publication rules

1. Freeze and independently review one immutable public and private candidate.
2. Publish the public candidate and synthetic-only private fixture repository without force-push.
3. Open bootstrap pull requests for existing mirrors; create the two new PDF mirrors from generated output.
4. Do not add the release tag until Claude Code and Kimi Code CLI real invocation gates pass.
5. Do not upload real fixtures without a precise file manifest and separate explicit approval.
