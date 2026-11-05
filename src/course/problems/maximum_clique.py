"""Maximum Clique course adapter.

COURSE INFRASTRUCTURE
Students should not modify this file.
"""

from importlib import import_module

from course.common.graph_io import read_graph


BOUND_KIND = "upper"
BOUND_FUNCTION = "upper_bound"

ALGORITHMS = {
    "exhaustive": "exhaustive",
    "improved": "improved",
    "heuristic1": "heuristic1",
    "heuristic2": "heuristic2",
}


def read_instance(filename, args=None):
    """Read one Maximum Clique instance."""
    return read_graph(filename)


def get_solver(algorithm: str):
    """Return the solve() function for the requested algorithm."""
    try:
        module_name = ALGORITHMS[algorithm]
    except KeyError as exc:
        valid = ", ".join(sorted(ALGORITHMS))
        raise ValueError(
            f"Unknown algorithm '{algorithm}'. Valid algorithms are: {valid}"
        ) from exc

    module = import_module(f"student.problems.maximum_clique.{module_name}")
    return module.solve


def get_bound():
    """Return the required polynomial-time bound function."""
    module = import_module("student.problems.maximum_clique.bound")
    return getattr(module, BOUND_FUNCTION)
