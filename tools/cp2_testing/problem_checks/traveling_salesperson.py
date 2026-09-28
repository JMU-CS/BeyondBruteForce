"""Public CP2 checks for Traveling Salesperson.

COURSE INFRASTRUCTURE
Students should not modify this file.
"""

VERIFIER_FUNCTION = "is_valid_tour"


def read_raw_graph(path):
    with open(path, "r", encoding="utf-8") as file:
        lines = [
            line.strip()
            for line in file
            if line.strip() and not line.lstrip().startswith("#")
        ]

    n, m = map(int, lines[0].split())
    weights = {}
    for line in lines[1:]:
        u, v, w = map(int, line.split())
        key = (u, v) if u < v else (v, u)
        weights[key] = w

    if len(lines) - 1 != m:
        raise ValueError("public weighted graph has inconsistent edge count")

    return n, weights


def check_solution(instance_path, solution, expected_optimum=None):
    if not isinstance(solution, dict):
        return False, "solution is not a dictionary"

    if "cost" not in solution or "tour" not in solution:
        return False, "solution must contain 'cost' and 'tour'"

    cost = solution["cost"]
    tour = solution["tour"]

    if isinstance(cost, bool) or not isinstance(cost, int):
        return False, "solution['cost'] must be an int"

    if not isinstance(tour, list):
        return False, "solution['tour'] must be a list"

    if any(isinstance(v, bool) or not isinstance(v, int) for v in tour):
        return False, "all returned tour entries must be ints"

    n, weights = read_raw_graph(instance_path)

    if len(tour) != n + 1:
        return False, f"tour must contain exactly {n + 1} entries"

    if tour[0] != tour[-1]:
        return False, "tour must return to its starting vertex"

    body = tour[:-1]
    if len(set(body)) != n or set(body) != set(range(n)):
        return False, "tour must visit every graph vertex exactly once"

    computed = 0
    for u, v in zip(tour, tour[1:]):
        key = (u, v) if u < v else (v, u)
        if key not in weights:
            return False, f"tour uses missing edge ({u}, {v})"
        computed += weights[key]

    if cost != computed:
        return False, f"reported cost {cost} does not match tour cost {computed}"

    if expected_optimum is not None and cost != expected_optimum:
        return False, f"expected optimum cost {expected_optimum}, got {cost}"

    return True, "ok"


def run_public_preflight(repo_root, algorithm, run_worker):
    result = run_worker(
        repo_root,
        "traveling_salesperson",
        "preflight",
        algorithm=algorithm,
        verifier_function=VERIFIER_FUNCTION,
        timeout=5,
    )
    return {
        "name": "Required files and functions import",
        "passed": bool(result.get("ok")),
        "message": (
            "ok"
            if result.get("ok")
            else result.get("error", "import/interface check failed")
        ),
    }


def run_public_verifier_test(repo_root, tests_root, test, run_worker):
    instance = tests_root / test["instance"]
    result = run_worker(
        repo_root,
        "traveling_salesperson",
        "verify",
        instance,
        certificate=test["tour"],
        verifier_function=VERIFIER_FUNCTION,
        k=test["k"],
        timeout=test.get("timeout", 5),
    )

    name = f"verifier: {test['name']}"
    if not result.get("ok"):
        return {
            "name": name,
            "passed": False,
            "message": result.get("error", "verifier failed"),
        }

    passed = result["valid"] is test["expected"]
    return {
        "name": name,
        "passed": passed,
        "message": (
            "ok"
            if passed
            else f"expected {test['expected']}, got {result['valid']}"
        ),
    }


def run_public_solver_test(repo_root, tests_root, test, algorithm, run_worker):
    instance = tests_root / test["instance"]
    result = run_worker(
        repo_root,
        "traveling_salesperson",
        "solve",
        instance,
        algorithm=algorithm,
        timeout=test.get("timeout", 10),
    )

    if not result.get("ok"):
        return {
            "name": test["name"],
            "passed": False,
            "message": result.get("error", "solver failed"),
        }

    statistics = result.get("statistics")
    if not isinstance(statistics, dict):
        return {
            "name": test["name"],
            "passed": False,
            "message": "statistics must be a dictionary",
        }

    elapsed = statistics.get("time")
    if (
        isinstance(elapsed, bool)
        or not isinstance(elapsed, (int, float))
        or elapsed < 0
    ):
        return {
            "name": test["name"],
            "passed": False,
            "message": "statistics['time'] must be a non-negative number measured in seconds",
        }

    passed, message = check_solution(
        instance,
        result["solution"],
        test.get("expected_optimum"),
    )
    return {
        "name": test["name"],
        "passed": passed,
        "message": message if not passed else "ok (student verifier not used)",
    }
