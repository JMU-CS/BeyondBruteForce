"""Polynomial-time certificate verifier for Longest Path.

STUDENT IMPLEMENTATION FILE — Checkpoint 1

The decision problem asks whether ``graph`` contains a simple path of length
at least ``k``.  ``vertices`` is the proposed certificate.
"""

from course.common.graph import Graph


def is_valid_path(graph: Graph, vertices: list[int], k: int) -> bool:
    """Return True exactly when ``vertices`` certifies a YES instance.

    Return True only when ``vertices`` is a valid simple path in ``graph``
    and its length (number of edges) is at least ``k``.
    """
    raise NotImplementedError("Implement is_valid_path().")
