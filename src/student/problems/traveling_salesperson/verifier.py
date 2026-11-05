"""Polynomial-time certificate verifier for Traveling Salesperson.

STUDENT IMPLEMENTATION FILE — Checkpoint 1

The decision problem asks whether ``graph`` contains a tour of total cost at
most ``k``.  ``tour`` is the proposed certificate.
"""

from course.common.weighted_graph import WeightedGraph


def is_valid_tour(graph: WeightedGraph, tour: list[int], k: int) -> bool:
    """Return True exactly when ``tour`` certifies a YES instance.

    Return True only when ``tour`` is a valid TSP tour of ``graph`` and the
    cost computed from the graph and tour is at most ``k``.  Do not trust a
    separately reported cost; compute the certificate's cost here.
    """
    raise NotImplementedError("Implement is_valid_tour().")
