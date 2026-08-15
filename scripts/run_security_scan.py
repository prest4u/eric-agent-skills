#!/usr/bin/env python3
"""Run a pinned SkillSpector executable over every public skill."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--executable", default="skillspector")
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    baseline_dir = repo / "security" / "skillspector-baselines"
    for skill in sorted(path for path in (repo / "skills").iterdir() if path.is_dir()):
        report = output / f"{skill.name}.json"
        command = [
            args.executable,
            "scan",
            str(skill),
            "--no-llm",
            "--format",
            "json",
            "--output",
            str(report),
        ]
        baseline = baseline_dir / f"{skill.name}.yaml"
        if baseline.is_file():
            command.extend(["--baseline", str(baseline)])
        print(f"+ {' '.join(command)}", flush=True)
        result = subprocess.run(command, cwd=repo, check=False)
        if result.returncode not in (0, 1):
            return result.returncode
        if not report.is_file():
            print(f"scanner did not produce {report}")
            return 2
    gate = repo / "scripts" / "check_skillspector_report.py"
    return subprocess.run(["python3", str(gate), str(output)], cwd=repo, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
