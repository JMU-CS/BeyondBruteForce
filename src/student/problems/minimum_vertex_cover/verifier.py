"""Polynomial-time certificate verifier for Minimum Vertex Cover.

STUDENT IMPLEMENTATION FILE — Checkpoint 2

The decision problem asks whether ``graph`` has a vertex cover of size at most
``k``.  ``vertices`` is the proposed certificate.
"""

from course.common.graph import Graph


def is_vertex_cover(graph: Graph, vertices: list[int], k: int) -> bool:
    """Return True exactly when ``vertices`` certifies a YES instance.

    Return True only when ``vertices`` is a valid vertex cover of ``graph``
    and the cover contains at most ``k`` vertices.
    """
    raise NotImplementedError("Implement is_vertex_cover().")
