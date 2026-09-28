"""Polynomial-time certificate verifier for Maximum Clique.

STUDENT IMPLEMENTATION FILE — Checkpoint 2

The decision problem asks whether ``graph`` contains a clique of size at least
``k``.  ``vertices`` is the proposed certificate.
"""

from course.common.graph import Graph


def is_clique(graph: Graph, vertices: list[int], k: int) -> bool:
    """Return True exactly when ``vertices`` certifies a YES instance.

    Return True only when ``vertices`` forms a clique in ``graph`` and the
    clique contains at least ``k`` vertices.
    """
    raise NotImplementedError("Implement is_clique().")
