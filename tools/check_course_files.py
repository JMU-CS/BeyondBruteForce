#!/usr/bin/env python3
"""Check that course-owned repository files have not been changed."""
from pathlib import Path
import sys

from course_file_integrity import is_clean, load_manifest, verify_course_files


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    manifest = load_manifest(repo_root)
    result = verify_course_files(repo_root)

    print(f"Course infrastructure version: {manifest['infrastructure_version']}")
    if is_clean(result):
        print("Course infrastructure check: PASSED")
        print("All protected course-owned files match the supplied SHA-256 manifest.")
        return 0

    print("Course infrastructure check: FAILED")
    for category in ("missing", "modified", "unexpected"):
        for path in result[category]:
            print(f"  - {category}: {path}")
    print("\nRestore the affected course-owned files before submitting.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
