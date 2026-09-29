"""Minimum Vertex Cover — baseline exhaustive exact solver."""

# STUDENT IMPLEMENTATION FILE — Checkpoint 1
# Keep the required solve() signature and return structure.

from argparse import Namespace
from time import perf_counter

from course.common.graph import Graph
from .verifier import is_vertex_cover


def solve(instance: Graph, args: Namespace) -> tuple[dict, dict]:
    """Return a minimum vertex cover and baseline-search statistics.

    Checkpoint 1 requires complete-candidate enumeration: try candidate sizes
    from small to large and test each completed vertex subset with the verifier.
    Do not use backtracking, pruning, memoization, dynamic programming, or
    branch-and-bound in this baseline.
    """
    start_time = perf_counter()
    candidates = 0

    # TODO: Implement the baseline exhaustive exact algorithm.
    # Each time a complete subset C is tested, increment ``candidates`` once.
    # A candidate can be checked with:
    #     is_vertex_cover(instance, C, len(C))
    vertices: list[int] = []

    solution = {
        "size": len(vertices),
        "vertices": vertices,
    }

    statistics = {
        "time": perf_counter() - start_time,
        "candidates": candidates,
    }

    return solution, statistics
