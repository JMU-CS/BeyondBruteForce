#!/usr/bin/env python3
"""Common command-line driver for Beyond Brute Force.

COURSE INFRASTRUCTURE -- students should not modify this file.
"""

import argparse
import json
import sys
from pathlib import Path

from course.problems import (
    SHORT_PROBLEM_IDS,
    canonical_problem_id,
    get_problem,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

ALGORITHM_IDS = (
    "exhaustive",
    "improved",
    "heuristic1",
    "heuristic2",
)


def parse_problem_id(value: str) -> str:
    """argparse converter: accept short IDs and normalize to canonical IDs."""
    try:
        return canonical_problem_id(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def build_parser():
    parser = argparse.ArgumentParser(description="Run a Beyond Brute Force solver.")
    parser.add_argument(
        "input_file",
        type=Path,
        help="file containing one problem instance",
    )
    parser.add_argument(
        "--problem",
        required=True,
        type=parse_problem_id,
        metavar="{mvc,tsp,mgc,lp,mc}",
        help="problem: mvc, tsp, mgc, lp, or mc",
    )
    parser.add_argument(
        "--algorithm",
        required=True,
        choices=ALGORITHM_IDS,
        help="algorithm to execute",
    )
    parser.add_argument(
        "--instance",
        help="override the default instance identifier",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="random seed for randomized algorithms",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="also write the JSON result to this file",
    )
    return parser


def get_preliminary_args(argv):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("input_file", nargs="?")
    parser.add_argument("--problem")
    parser.add_argument("--algorithm")
    args, _ = parser.parse_known_args(argv)
    return args


def validate_assigned_problem(problem_id: str):
    project_file = REPO_ROOT / "project.json"
    with project_file.open("r", encoding="utf-8") as infile:
        project = json.load(infile)

    assigned_problem = project.get("assigned_problem")
    if not assigned_problem:
        raise ValueError("project.json does not contain an assigned problem")

    assigned_canonical = canonical_problem_id(assigned_problem)
    requested_canonical = canonical_problem_id(problem_id)
    if assigned_canonical != requested_canonical:
        raise ValueError(
            f"--problem specifies '{requested_canonical}', but project.json "
            f"assigns this team '{assigned_canonical}'"
        )


def make_instance_id(input_file: Path, explicit_id):
    return explicit_id if explicit_id is not None else input_file.stem


def write_result(result, output_file=None):
    text = json.dumps(result, indent=2)
    print(text)
    if output_file is not None:
        output_file.write_text(text + "\n", encoding="utf-8")


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    preliminary = get_preliminary_args(argv)
    parser = build_parser()

    if preliminary.problem and preliminary.algorithm:
        problem = get_problem(preliminary.problem)
        if hasattr(problem, "register_arguments"):
            problem.register_arguments(parser, preliminary.algorithm)

    args = parser.parse_args(argv)
    # parse_problem_id has already normalized the CLI value to the canonical ID.
    validate_assigned_problem(args.problem)
    problem = get_problem(args.problem)
    instance = problem.read_instance(args.input_file, args)
    solver = problem.get_solver(args.algorithm)
    solution, statistics = solver(instance, args)

    if not isinstance(solution, dict):
        raise TypeError("solve() must return solution as a dictionary")
    if not isinstance(statistics, dict):
        raise TypeError("solve() must return statistics as a dictionary")

    result = {
        "problem": args.problem,
        "algorithm": args.algorithm,
        "instance": make_instance_id(args.input_file, args.instance),
        "solution": solution,
        "statistics": statistics,
    }
    write_result(result, args.output)


if __name__ == "__main__":
    main()
