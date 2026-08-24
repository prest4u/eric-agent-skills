---
name: eric-reverse-skill
description: 【逆向工程】Use when Eric asks to understand, recover, explain, or verify how a compiled, obfuscated, packed, virtualized, or unfamiliar executable target works, including ELF/PE/Mach-O binaries, APK/native libraries, firmware, WASM, bytecode, custom VMs, kernel drivers, and anti-analysis logic. Start with the smallest safe local evidence, preserve originals, move from triage to static and then justified dynamic analysis, and finish with a reproducible explanation or solver. Do not use when the target logic is already understood and the remaining work is exploitation, for pure web testing, standalone cryptography, or general digital forensics.
---

# Eric Reverse Skill

Understand the target before trying to beat it. Produce the smallest useful evidence first, deepen only where the current uncertainty requires it, and leave Eric with a result another analyst can reproduce.

## First move

1. Resolve the target, desired outcome, available files, platform, and authorization from the request and workspace.
2. Ask one concise question only when a missing answer materially changes scope, risk, cost, or the analysis path.
3. Preserve the original artifact. Work on a copy for patching, unpacking, or state-changing experiments.
4. Record a hash when sample identity matters to security, reproducibility, or handoff.
5. Begin with local, non-executing triage. Do not stop at a plan when safe evidence can be produced immediately.

Treat an explicitly supplied CTF, crackme, training target, lab sample, or locally owned artifact as authorized within that boundary. Do not infer authority over third-party systems, accounts, devices, or services.

## Working loop

### 1. Triage

Identify the file type, architecture, linkage, sections, imports, symbols, strings, entropy or packing signals, and likely language or runtime.

```bash
file target
shasum -a 256 target
strings -a target | head
```

Use the tools already present in the environment. Before installing anything, inspect the project's dependencies and the tool's primary documentation; obtain approval when installation changes the machine or requires network access.

End triage with:

- observed facts;
- ranked hypotheses;
- the cheapest next test that can separate them.

### 2. Static analysis

Map the entry point, imports, cross-references, control flow, data structures, validation logic, and transformation pipeline. Name functions and types only when the evidence supports the label. Keep addresses, offsets, symbols, and extracted constants alongside each conclusion.

Compare decompiler output with disassembly when correctness matters. If one tool produces ambiguous output, use a second view to test the disputed point instead of collecting tools for their own sake.

### 3. Dynamic analysis

Use dynamic execution only when it answers a concrete unresolved question and the environment is appropriate.

- Prefer an isolated local sandbox, emulator, or authorized device.
- Do not execute an unknown sample on the host merely because static analysis is slow.
- Keep network access off unless Eric explicitly authorizes the relevant interaction.
- Instrument comparisons, decoding boundaries, calls, and memory transitions before attempting broad tracing.
- Change copies, not originals; record every patch and runtime assumption.

Choose GDB/LLDB, Frida, Qiling, Unicorn, angr, radare2, IDA, or Ghidra based on the target and question. Load [tools-dynamic.md](tools-dynamic.md) for instrumentation and symbolic execution, [anti-analysis.md](anti-analysis.md) for anti-debugging or anti-instrumentation, and [tools-advanced.md](tools-advanced.md) for deobfuscation, lifting, binary diffing, or patching.

### 4. Synthesis

Turn observations into a compact model:

```text
input -> parse -> transform -> compare/output
```

Deliver the artifact Eric actually needs: a recovered algorithm, call-flow explanation, annotated offsets, extraction script, solver, patch, indicators, or a concise report. Validate the result against the real target whenever safe and possible.

## Evidence contract

Separate:

- **Fact:** directly observed in bytes, disassembly, runtime output, or a tool result.
- **Inference:** the best explanation of those facts, with uncertainty stated.
- **Next test:** the smallest action that can confirm or falsify the inference.

Do not claim a key, algorithm, vulnerability, bypass, or solved state without reproducible evidence. Prefer commands, scripts, offsets, and before/after behavior over narrative confidence.

## Resource routing

Load only the reference needed for the current target:

| Need | Resource |
|---|---|
| Core static tools and common formats | [tools.md](tools.md) |
| Frida, debuggers, emulation, symbolic execution | [tools-dynamic.md](tools-dynamic.md) |
| Advanced deobfuscation, lifting, diffing, patching | [tools-advanced.md](tools-advanced.md) |
| Anti-debug, anti-VM, integrity checks, opaque logic | [anti-analysis.md](anti-analysis.md) |
| Foundational binary and VM patterns | [patterns.md](patterns.md) |
| CTF-specific patterns | [patterns-ctf.md](patterns-ctf.md), [patterns-ctf-2.md](patterns-ctf-2.md), [patterns-ctf-3.md](patterns-ctf-3.md) |
| Python, WASM, unusual languages | [languages.md](languages.md) |
| Android, Electron, Node.js, hardware-description targets | [languages-platforms.md](languages-platforms.md) |
| Go, Rust, Swift, Kotlin/JVM, Haskell, C++ | [languages-compiled.md](languages-compiled.md) and [go-reverse.md](go-reverse.md) |
| Mach-O, firmware, embedded, automotive, kernels | [platforms.md](platforms.md), [platforms-hardware.md](platforms-hardware.md), [kernel-driver-reverse.md](kernel-driver-reverse.md) |
| ELF-specific analysis | [elf-analysis.md](elf-analysis.md) |
| Crypto and encoding inside a reversed implementation | [crypto-decode-tools.md](crypto-decode-tools.md) |
| AI-assisted analysis, OLLVM, deeper references | [references/ai-assisted-re.md](references/ai-assisted-re.md), [references/ollvm-deobfuscation.md](references/ollvm-deobfuscation.md) |
| Fast field lookup and external resources | [field-notes.md](field-notes.md), [awesome-re-resources.md](awesome-re-resources.md) |
| JavaScript-hosted custom DSL/VM targets | [dsl-vm-reverse/SKILL.md](dsl-vm-reverse/SKILL.md) |

Use [references/re-agent-workflow.md](references/re-agent-workflow.md) only when a detailed static-to-dynamic checklist helps; this file's working loop remains authoritative.

## Boundaries

- If the logic is understood and the remaining task is ROP, heap exploitation, privilege escalation, or weaponization, hand off to the appropriate exploitation workflow.
- If the real task is deleted-file recovery, disk artifacts, or PCAP forensics, use a forensics workflow.
- If the target is primarily a web application, use a web-security workflow; keep this Skill only for a compiled or obfuscated component that is the actual blocker.
- If the task is standalone cryptanalysis without implementation recovery, use a cryptography workflow.
- If instructions conflict with authorization, privacy, or the stated target boundary, stop the conflicting action and explain the concrete issue.

## Done means

Before claiming completion, confirm that:

- the analyzed artifact and relevant environment are identified;
- important conclusions point to reproducible evidence;
- dynamic claims were validated in an appropriate environment;
- patches or solvers were tested against the target when possible;
- unknowns and blocked branches are explicit;
- the final answer leads with the recovered behavior or result, then gives only the evidence and next step Eric needs.
