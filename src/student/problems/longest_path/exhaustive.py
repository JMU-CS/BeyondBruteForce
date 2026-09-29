"""Longest Path — baseline exhaustive exact solver."""

# STUDENT IMPLEMENTATION FILE — Checkpoint 1
# Keep the required solve() signature and return structure.

from argparse import Namespace
from time import perf_counter

from course.common.graph import Graph
from .verifier import is_valid_path


def solve(instance: Graph, args: Namespace) -> tuple[dict, dict]:
    """Return a solution dictionary and a statistics dictionary."""
    start_time = perf_counter()

    # TODO: Implement the baseline exhaustive exact algorithm.
    # A candidate path P can be checked with k = max(0, len(P) - 1).
    vertices: list[int] = []
    length = 0

    solution = {
        "length": length,
        "vertices": vertices,
    }

    statistics = {
        "time": perf_counter() - start_time,
    }

    return solution, statistics
