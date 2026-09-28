"""Traveling Salesperson — baseline exhaustive exact solver."""

# STUDENT IMPLEMENTATION FILE — Checkpoint 2
# Keep the required solve() signature and return structure.

from argparse import Namespace
from time import perf_counter

from course.common.weighted_graph import WeightedGraph
from .verifier import is_valid_tour


def solve(instance: WeightedGraph, args: Namespace) -> tuple[dict, dict]:
    """Return a solution dictionary and a statistics dictionary."""
    start_time = perf_counter()

    # TODO: Implement the baseline exhaustive exact algorithm.
    tour: list[int] = []
    cost = 0

    solution = {
        "cost": cost,
        "tour": tour,
    }

    statistics = {
        "time": perf_counter() - start_time,
    }

    return solution, statistics
