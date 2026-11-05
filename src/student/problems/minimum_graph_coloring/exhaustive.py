"""Minimum Graph Coloring — baseline exhaustive exact solver."""

# STUDENT IMPLEMENTATION FILE — Checkpoint 1
# Keep the required solve() signature and return structure.

from argparse import Namespace
from time import perf_counter

from course.common.graph import Graph
from .verifier import is_valid_coloring


def solve(instance: Graph, args: Namespace) -> tuple[dict, dict]:
    """Return a solution dictionary and a statistics dictionary."""
    start_time = perf_counter()
    candidates = 0

    # TODO: Implement the baseline exhaustive exact algorithm.
    # A candidate coloring can use k = len(set(colors)) when calling the verifier.
    colors: list[int] = []
    num_colors = 0

    solution = {
        "num_colors": num_colors,
        "colors": colors,
    }

    statistics = {
        "time": perf_counter() - start_time,
        "candidates": candidates,
    }


    return solution, statistics
