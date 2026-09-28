#!/usr/bin/env python3
"""Run public CP2 correctness tests."""

# ----------------------------------------------------------------------
# COURSE INFRASTRUCTURE
# Students should not modify this file.
# ----------------------------------------------------------------------

import argparse
import json
from pathlib import Path
import sys

TOOLS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_DIR))
REPO_ROOT = TOOLS_DIR.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from course.problems import canonical_problem_id
from cp2_testing.runner import run_suite


VALID_PROBLEMS = {
    "traveling_salesperson",
    "minimum_graph_coloring",
    "minimum_vertex_cover",
    "longest_path",
    "maximum_clique",
}


def get_assigned_problem(repo_root: Path):
    project_file = repo_root / "project.json"

    with project_file.open("r", encoding="utf-8") as file:
        project = json.load(file)

    problem = project.get("assigned_problem", "")

    if problem not in VALID_PROBLEMS:
        raise ValueError(
            "project.json does not contain a valid assigned_problem; "
            "pass --problem explicitly"
        )

    return problem


def print_results(title, results):
    if not results:
        return

    print(f"\n{title}")
    print("-" * len(title))

    for result in results:
        if result.get("skipped"):
            mark = "SKIP"
        else:
            mark = "PASS" if result["passed"] else "FAIL"

        print(f"{mark:4}  {result['name']}")

        if result.get("message") and result["message"] != "ok":
            print(f"      {result['message']}")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Run the public Checkpoint 2 tests on your local machine."
        )
    )
    parser.add_argument("--problem", default="auto")
    parser.add_argument("--algorithm", default="exhaustive")
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument(
        "--test",
        help="run only tests whose name contains this text",
    )
    ns = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]

    problem = (
        get_assigned_problem(repo_root)
        if ns.problem == "auto"
        else ns.problem
    )

    try:
        problem = canonical_problem_id(problem)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    if problem not in VALID_PROBLEMS:
        raise SystemExit(f"Unknown problem: {problem}")

    manifest = (
        repo_root
        / "tests"
        / "public"
        / problem
        / "manifest.json"
    )

    if not manifest.exists():
        raise SystemExit(
            f"No public CP2 manifest exists yet for '{problem}': {manifest}"
        )

    preflight_results, verifier_results, solver_results = run_suite(
        repo_root,
        manifest,
        ns.algorithm,
        max(1, ns.jobs),
        ns.test,
    )

    print_results("Interface check", preflight_results)
    print_results("Verifier tests", verifier_results)
    print_results("Solver tests", solver_results)

    counted = [
        result
        for result in (
            preflight_results + verifier_results + solver_results
        )
        if not result.get("skipped")
    ]
    passed = sum(result["passed"] for result in counted)
    total = len(counted)
    skipped = sum(
        1
        for result in solver_results
        if result.get("skipped")
    )

    print(f"\n{passed}/{total} executed tests passed")
    if skipped:
        print(f"{skipped} dependent solver tests skipped")

    raise SystemExit(0 if passed == total and skipped == 0 else 1)


if __name__ == "__main__":
    main()
