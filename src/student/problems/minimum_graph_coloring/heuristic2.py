"""Minimum Graph Coloring — second heuristic solver."""

# STUDENT IMPLEMENTATION FILE — Final Project for three-person teams
# Keep the required solve() signature and return structure.

from argparse import Namespace
from time import perf_counter

from course.common.graph import Graph


def solve(instance: Graph, args: Namespace) -> tuple[dict, dict]:
    """Return a solution dictionary and a statistics dictionary."""
    start_time = perf_counter()

    # TODO: Implement the second heuristic algorithm.
    colors: list[int] = []
    num_colors = 0

    solution = {
        "num_colors": num_colors,
        "colors": colors,
    }

    statistics = {
        "time": perf_counter() - start_time,
    }

    return solution, statistics
