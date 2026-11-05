"""Course-owned problem dispatch for Beyond Brute Force."""

from importlib import import_module

PROBLEMS = {
    "traveling_salesperson": "course.problems.traveling_salesperson",
    "minimum_graph_coloring": "course.problems.minimum_graph_coloring",
    "minimum_vertex_cover": "course.problems.minimum_vertex_cover",
    "longest_path": "course.problems.longest_path",
    "maximum_clique": "course.problems.maximum_clique",
}

SHORT_PROBLEM_IDS = {
    "tsp": "traveling_salesperson",
    "mgc": "minimum_graph_coloring",
    "mvc": "minimum_vertex_cover",
    "lp": "longest_path",
    "mc": "maximum_clique",
}

CANONICAL_TO_SHORT = {value: key for key, value in SHORT_PROBLEM_IDS.items()}


def canonical_problem_id(problem_id: str) -> str:
    """Return the canonical identifier for a short or canonical problem ID."""
    if problem_id in SHORT_PROBLEM_IDS:
        return SHORT_PROBLEM_IDS[problem_id]
    if problem_id in PROBLEMS:
        return problem_id
    valid = ", ".join(
        f"{canonical} ({short})"
        for canonical, short in CANONICAL_TO_SHORT.items()
    )
    raise ValueError(
        f"Unknown problem '{problem_id}'. Use a canonical ID or short alias: {valid}"
    )


def short_problem_id(problem_id: str) -> str:
    canonical = canonical_problem_id(problem_id)
    return CANONICAL_TO_SHORT[canonical]


def get_problem(problem_id: str):
    """Return the course adapter for a short or canonical problem ID."""
    canonical = canonical_problem_id(problem_id)
    return import_module(PROBLEMS[canonical])
