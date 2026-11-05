"""Traveling Salesperson course adapter.

COURSE INFRASTRUCTURE
Students should not modify this file.
"""

from importlib import import_module

from course.common.weighted_graph_io import read_weighted_graph


BOUND_KIND = "lower"
BOUND_FUNCTION = "lower_bound"

ALGORITHMS = {
    "exhaustive": "exhaustive",
    "improved": "improved",
    "heuristic1": "heuristic1",
    "heuristic2": "heuristic2",
}


def read_instance(filename, args=None):
    """Read a complete weighted TSP instance."""
    graph = read_weighted_graph(filename)
    if graph.num_vertices < 2:
        raise ValueError("TSP instances must contain at least two vertices")
    if not graph.is_complete:
        raise ValueError("TSP instances must be complete weighted graphs")
    return graph


def get_solver(algorithm: str):
    """Return the solve() function for the requested algorithm."""
    try:
        module_name = ALGORITHMS[algorithm]
    except KeyError as exc:
        valid = ", ".join(sorted(ALGORITHMS))
        raise ValueError(
            f"Unknown algorithm '{algorithm}'. Valid algorithms are: {valid}"
        ) from exc

    module = import_module(f"student.problems.traveling_salesperson.{module_name}")
    return module.solve


def get_bound():
    """Return the required polynomial-time lower-bound function."""
    module = import_module("student.problems.traveling_salesperson.bound")
    return getattr(module, BOUND_FUNCTION)
