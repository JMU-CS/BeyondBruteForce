"""Minimum Vertex Cover — first heuristic solver."""

# STUDENT IMPLEMENTATION FILE — Checkpoint 3
# Keep the required solve() signature and return structure.

from argparse import Namespace
from time import perf_counter

from course.common.graph import Graph


def solve(instance: Graph, args: Namespace) -> tuple[dict, dict]:
    """Return a valid, polynomial-time heuristic vertex cover."""
    start_time = perf_counter()

    # TODO: Implement heuristic1.
    # Checkpoint 3 requires a randomized component, repeated attempts/restarts,
    # best-so-far retention, and reproducibility from args.seed.  The default
    # amount of work must remain polynomial in the input size.
    vertices: list[int] = []

    solution = {
        "size": len(vertices),
        "vertices": vertices,
    }

    statistics = {
        "time": perf_counter() - start_time,
    }

    return solution, statistics
