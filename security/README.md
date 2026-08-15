# Security review policy

CI scans every published Skill with the locked NVIDIA SkillSpector revision in `catalog/upstreams.lock.json`. The scan is static (`--no-llm`) and never executes Skill code.

`skillspector-baselines/` contains reviewer-approved version 2 exact fingerprints for findings that are expected in one of these bounded cases:

- inert negative-test fixtures for secret redaction or SSRF rejection;
- explicit-argument test subprocesses operating only on temporary files;
- source-hash-locked upstream documentation examples;
- licensed offline minified editor bundles;
- authorized local/CTF reverse-engineering reference material with the limits stated in that Skill.

Glob suppression rules are forbidden. A baseline fingerprint is tied to the scanner version, rule, file, and source evidence. A content change therefore becomes a new unsuppressed finding and blocks CI. Regenerate a baseline only after reviewing the changed immutable candidate and recording a narrow reason.

Baseline generation example:

```bash
skillspector baseline skills/<skill-name> \
  --output security/skillspector-baselines/<skill-name>.yaml \
  --no-llm \
  --reason "Reviewed reason tied to this candidate."
```

Never use a baseline to accept shipped bytecode, credential discovery, bulk environment harvesting, unreviewed upstream changes, or an unexplained high/critical result.
