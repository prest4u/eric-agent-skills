---
name: building-validators
description: Build or revise a project-native executable Validator for a recurring check. Use only when Eric explicitly asks for a Validator、验证、验收门禁 or QA rule and wants a repeated failure mode encoded as durable project policy; do not use for ordinary QA, a one-off review, or general test-and-fix work.
---

# Building Validators

Encode one recurring, objectively testable failure mode as the smallest project-native validator.

## Workflow

1. Confirm that the requested check is recurring. If it is a one-off review or ordinary acceptance test, stop and use the project's normal QA path instead.
2. Inspect the project before designing anything: applicable `AGENTS.md`, existing test/lint/schema frameworks, validator entry points, dependencies, and dirty work. Extend the native framework when it can express the rule cleanly.
3. State the executable contract:
   - input root and files;
   - invariant and exact failure condition;
   - machine-checkable scope versus remaining human judgment;
   - exit semantics and allowed outputs.
4. For an unfamiliar validator or bundle, inspect it statically before execution. Check its entry point, dependencies, subprocess/network use, write paths, path resolution, and fixture commands. Do not execute it until that inspection establishes a safe boundary.
5. Implement the narrowest check. Keep validation read-only against project artifacts by default. If evidence output is requested, confine it to an explicit path inside the project root.
6. Reject absolute rule paths, parent traversal, and symlink escapes. Resolve every configured input or output against the declared root before reading or writing it. Provide a no-write mode when the validator otherwise supports reports or caches.
7. Exercise temporary fixtures:
   - a good fixture passes;
   - a bad fixture fails for the intended rule, not setup noise;
   - a malformed or escaping path fails closed when paths are configurable.
8. Enforce strict exits: zero only when the encoded gate passes; nonzero for gate failure, invalid configuration, or internal error. Preserve distinct exit codes when the project's native framework already defines them.
9. Report the command, fixture evidence, changed files, and the strongest honest conclusion. A machine pass covers only the encoded invariant; it does not certify visual quality, correctness beyond the fixtures, or human approval.

## Boundaries

- Do not build a universal validator, scaffold unrelated gate families, or require a report packet.
- Do not replace a mature project-native framework with a custom harness without a concrete need.
- Do not mutate source artifacts in order to make validation pass.
- Do not weaken an existing failing check or accept a bad fixture that fails for the wrong reason.
- Do not add the validator to CI, hooks, `AGENTS.md`, release workflows, or scheduled automation without separate explicit authority.
- Treat integration as a separate change: identify the exact integration point and leave it unmodified unless the active request authorizes it.

## Completion

Return the validator path, commands run, good/bad/boundary fixture results, exit behavior, machine-versus-human limits, and any unperformed integration dependency.
