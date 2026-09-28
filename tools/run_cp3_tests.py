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


def show(title, groups):
    print(f"\n{title}\n" + "-" * len(title))
    for result in groups:
        mark = "PASS" if result["passed"] else "FAIL"
        print(f"{mark:4}  {result['name']}")
        if result.get("message") and result["message"] != "ok":
            print(f"      {result['message']}")


def run_one(repo, manifest, algorithm, jobs):
    pre, verifier, solver = run_suite(repo, manifest, algorithm, jobs)
    return pre + verifier + solver


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobs", type=int, default=1)
    ns = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    problem = assigned(repo)
    if problem != "minimum_vertex_cover":
        raise SystemExit(
            "Public CP3 tests are currently wired for minimum_vertex_cover only."
        )

    root = repo / "tests/public/minimum_vertex_cover"
    improved = run_one(
        repo, root / "cp3_improved_manifest.json", "improved", max(1, ns.jobs)
    )
    bounds = run_bound_suite(
        repo, root / "cp3_bound_manifest.json", max(1, ns.jobs)
    )
    heuristic1 = run_one(
        repo, root / "cp3_heuristic_manifest.json", "heuristic1", max(1, ns.jobs)
    )

    show("Improved exact", improved)
    show("Polynomial-time bound", bounds)
    show("Heuristic 1", heuristic1)

    all_results = improved + bounds + heuristic1
    passed = sum(result["passed"] for result in all_results)
    total = len(all_results)
    print(f"\n{passed}/{total} tests passed")
    raise SystemExit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
