#!/usr/bin/env python
"""Install or inspect ZKME git hook configuration."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Install ZKME pre-commit hook via git core.hooksPath.")
    parser.add_argument("--dry-run", action="store_true", help="Print the git config command without changing anything.")
    parser.add_argument("--unset", action="store_true", help="Unset core.hooksPath.")
    args = parser.parse_args()

    if args.unset:
        command = ["git", "config", "--unset", "core.hooksPath"]
    else:
        command = ["git", "config", "core.hooksPath", ".githooks"]

    if args.dry_run:
        print(" ".join(command))
        return
    subprocess.run(command, cwd=REPO_ROOT, check=True)
    print("ZKME git hook configuration updated.")


if __name__ == "__main__":
    main()
