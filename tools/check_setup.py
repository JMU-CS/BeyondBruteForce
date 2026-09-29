#!/usr/bin/env python3
"""Run the Beyond Brute Force Project Selection & Setup checks locally."""
from pathlib import Path
import sys

from course_file_integrity import is_clean, verify_course_files
from project_validation import (
    flatten_messages,
    load_project,
    load_valid_projects,
    validate_project_data,
    validate_repository_structure,
)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    catalog_path = Path(__file__).resolve().parent / "valid_projects.json"

    try:
        catalog = load_valid_projects(catalog_path)
    except ValueError as exc:
        print(f"Setup check configuration error: {exc}")
        return 2

    data, load_errors = load_project(repo_root / "project.json")
    structure_errors = validate_repository_structure(repo_root)
    integrity = verify_course_files(repo_root)

    if data is None:
        messages = load_errors + structure_errors
    else:
        grouped = validate_project_data(data, set(catalog), require_unassigned=True)
        messages = load_errors + structure_errors + flatten_messages(grouped)

    if not is_clean(integrity):
        for category in ("missing", "modified", "unexpected"):
            for path in integrity[category]:
                messages.append(f"Course infrastructure {category}: {path}")

    if messages:
        print("Project Selection & Setup check: FAILED")
        for message in messages:
            print(f"  - {message}")
        print("\nAllowed project identifiers in project.json:")
        for project_id, display_name in catalog.items():
            print(f"  - {project_id}: {display_name}")
        return 1

    print("Project Selection & Setup check: PASSED")
    print("project.json, repository structure, and course-owned files look valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
