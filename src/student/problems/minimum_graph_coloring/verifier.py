"""Polynomial-time certificate verifier for Minimum Graph Coloring.

STUDENT IMPLEMENTATION FILE — Checkpoint 1

The decision problem asks whether ``graph`` can be properly colored using at
most ``k`` colors.  ``colors`` is the proposed certificate.
"""

from course.common.graph import Graph


def is_valid_coloring(graph: Graph, colors: list[int], k: int) -> bool:
    """Return True exactly when ``colors`` certifies a YES instance.

    Return True only when ``colors`` is a proper coloring of ``graph`` and
    uses at most ``k`` distinct colors.
    """
    raise NotImplementedError("Implement is_valid_coloring().")
