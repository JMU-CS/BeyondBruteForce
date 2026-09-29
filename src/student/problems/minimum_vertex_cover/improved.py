"""Minimum Vertex Cover — improved exact solver."""

# STUDENT IMPLEMENTATION FILE — Checkpoint 2
# Keep the required solve() signature and return structure.

from argparse import Namespace
from time import perf_counter

from course.common.graph import Graph


def solve(instance: Graph, args: Namespace) -> tuple[dict, dict]:
    """Return an optimal cover using a selective exact-search strategy."""
    start_time = perf_counter()

    # TODO: Implement the improved exact algorithm.
    # Unlike Checkpoint 1, this solver should use information from partial
    # solutions/subproblems to avoid substantial complete-candidate work.
    # MVC supports a natural branch on an uncovered edge {u,v}: every cover
    # must contain u or v. Bounds, reductions, and improved branching may be
    # added as long as the method remains exact.
    vertices: list[int] = []

    solution = {
        "size": len(vertices),
        "vertices": vertices,
    }

    statistics = {
        "time": perf_counter() - start_time,
        # Add one or more clearly defined work counters useful for your report.
    }

    return solution, statistics
