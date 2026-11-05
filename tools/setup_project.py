#!/usr/bin/env python3
"""Perform one-time post-assignment setup for Beyond Brute Force.

Run this after the instructor has populated/announced your team's assigned problem::

    python tools/setup_project.py

The command validates project.json, determines the assigned problem, and installs
that problem's external benchmark data. It is safe to run again later.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from install_external_benchmarks import install_for_problem
from project_validation import (
    flatten_messages,
    load_project,
    load_valid_projects,
    validate_project_data,
)

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="redownload external benchmark files even when already installed",
    )
    args = parser.parse_args()

    valid = load_valid_projects(ROOT / "tools" / "valid_projects.json")
    project, errors = load_project(ROOT / "project.json")
    if errors or project is None:
        for error in errors:
            print(f"ERROR: {error}")
        return 2

    grouped = validate_project_data(project, set(valid), require_assigned=True)
    errors = flatten_messages(grouped)
    if errors:
        print("project.json is not ready for post-assignment setup:")
        for error in errors:
            print(f"  - {error}")
        return 2

    problem = project["assigned_problem"].strip()
    print(f"Project: {valid[problem]} ({problem})")
    count = install_for_problem(problem, force=args.force)
    print(f"Benchmark setup complete. External instances available/configured: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
