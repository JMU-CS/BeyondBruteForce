#!/usr/bin/env python3
"""Run public Checkpoint 3 tests."""
import argparse
import json
from pathlib import Path
import sys

TOOLS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_DIR))

from cp2_testing.runner import run_bound_suite, run_suite


def assigned(repo):
    data = json.loads((repo / "project.json").read_text())
    return data.get("assigned_problem", "")


def show(title, groups, quiet=False):
    print(f"\n{title}\n" + "-" * len(title))
    for result in groups:
        mark = "PASS" if result["passed"] else "FAIL"
        print(f"{mark:4}  {result['name']}")
        if result.get("message") and result["message"] != "ok":
            message_lines = str(result["message"]).splitlines()
            if quiet:
                message_lines = message_lines[:1]
            for line in message_lines:
                print(f"      {line}")


def run_one(repo, manifest, algorithm, jobs):
    pre, verifier, solver = run_suite(repo, manifest, algorithm, jobs)
    return pre + verifier + solver


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument(
        "--quiet",
        action="store_true",
        help=(
            "show compact failure messages only; by default, exceptions in "
            "student code include the student file, line number, and source line"
        ),
    )
    ns = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    problem = assigned(repo)
    supported = {"minimum_vertex_cover", "traveling_salesperson", "longest_path", "maximum_clique", "minimum_graph_coloring"}
    if problem not in supported:
        raise SystemExit(
            f"Public CP3 tests are currently available for: {sorted(supported)}; "
            f"assigned_problem is {problem!r}."
        )

    root = repo / "tests/public" / problem
    improved = run_one(
        repo, root / "cp3_improved_manifest.json", "improved", max(1, ns.jobs)
    )
    bounds = run_bound_suite(
        repo, root / "cp3_bound_manifest.json", max(1, ns.jobs)
    )
    heuristic1 = run_one(
        repo, root / "cp3_heuristic_manifest.json", "heuristic1", max(1, ns.jobs)
    )

    show("Improved exact", improved, ns.quiet)
    show("Polynomial-time bound", bounds, ns.quiet)
    show("Heuristic 1", heuristic1, ns.quiet)

    all_results = improved + bounds + heuristic1
    passed = sum(result["passed"] for result in all_results)
    total = len(all_results)
    print(f"\n{passed}/{total} tests passed")
    raise SystemExit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
