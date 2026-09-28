"""Maximum Clique — baseline exhaustive exact solver."""

# STUDENT IMPLEMENTATION FILE — Checkpoint 2
# Keep the required solve() signature and return structure.

from argparse import Namespace
from time import perf_counter

from course.common.graph import Graph
from .verifier import is_clique


def solve(instance: Graph, args: Namespace) -> tuple[dict, dict]:
    """Return a solution dictionary and a statistics dictionary."""
    start_time = perf_counter()

    # TODO: Implement the baseline exhaustive exact algorithm.
    # A candidate clique C can be checked with is_clique(instance, C, len(C)).
    vertices: list[int] = []

    solution = {
        "size": len(vertices),
        "vertices": vertices,
    }

    statistics = {
        "time": perf_counter() - start_time,
    }

    return solution, statistics
