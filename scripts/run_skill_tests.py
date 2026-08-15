#!/usr/bin/env python3
"""Run the tests bundled with one independently installable skill."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run(command: list[str], cwd: Path) -> int:
    print(f"+ {' '.join(command)}", flush=True)
    return subprocess.run(command, cwd=cwd, check=False).returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", required=True)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--static-only", action="store_true")
    args = parser.parse_args()
    skill = (args.repo / "skills" / args.skill).resolve()
    if not skill.is_dir() or skill.parent != (args.repo / "skills").resolve():
        parser.error(f"unknown skill: {args.skill}")

    validator = args.repo / "scripts" / "validate_repo.py"
    if run([sys.executable, str(validator), "--repo", str(args.repo), "--skill", args.skill], args.repo):
        return 1
    if args.static_only:
        return 0

    commands: list[tuple[list[str], Path]] = []
    tests_dir = skill / "tests"
    if tests_dir.is_dir() and any(tests_dir.glob("test*.py")):
        commands.append(([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test*.py", "-v"], skill))
    for script in sorted((skill / "scripts").glob("test_*.py")) if (skill / "scripts").is_dir() else []:
        commands.append(([sys.executable, str(script)], skill))
    if not commands:
        print("No executable unit tests; static validation is the acceptance check.")
        return 0
    env = os.environ.copy()
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    for command, cwd in commands:
        print(f"+ {' '.join(command)}", flush=True)
        result = subprocess.run(command, cwd=cwd, env=env, check=False)
        if result.returncode:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
