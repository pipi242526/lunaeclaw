#!/usr/bin/env python3
"""Run ruff only on changed Python files to enforce incremental cleanliness."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()


def changed_files(base: str) -> list[Path]:
    file_set: set[Path] = set()
    committed = _run(["git", "diff", "--name-only", f"{base}...HEAD"])
    for line in committed.splitlines():
        p = Path(line.strip())
        if p.suffix == ".py" and p.exists():
            file_set.add(p)
    # Also include local staged/unstaged changes for developer runs.
    local = _run(["git", "diff", "--name-only"])
    for line in local.splitlines():
        p = Path(line.strip())
        if p.suffix == ".py" and p.exists():
            file_set.add(p)
    # Include newly added untracked Python files.
    untracked = _run(["git", "ls-files", "--others", "--exclude-standard"])
    for line in untracked.splitlines():
        p = Path(line.strip())
        if p.suffix == ".py" and p.exists():
            file_set.add(p)
    return sorted(file_set)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="", help="git base ref for incremental lint")
    args = parser.parse_args()

    base = args.base.strip() or _resolve_default_base()
    files = changed_files(base)
    if not files:
        print("No changed Python files. Incremental lint passed.")
        return 0

    cmd = ["uv", "run", "ruff", "check", *[str(p) for p in files]]
    print(f"Base ref: {base}")
    print("Running:", " ".join(cmd))
    completed = subprocess.run(cmd)
    if completed.returncode != 0:
        print("\nIncremental lint failed.")
        return completed.returncode

    print("Incremental lint passed for changed files:")
    for p in files:
        print(f"- {p}")
    return 0


def _resolve_default_base() -> str:
    baseline_file = Path("release/lint-baseline.txt")
    if baseline_file.exists():
        value = baseline_file.read_text(encoding="utf-8").strip()
        if value:
            return value
    return "origin/main"


if __name__ == "__main__":
    sys.exit(main())
