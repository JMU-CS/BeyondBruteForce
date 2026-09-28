"""Public CP2 checks for Traveling Salesperson.

COURSE INFRASTRUCTURE
Students should not modify this file.

The public solver checks intentionally reuse the student's already-tested
certificate verifier. Independent solution validation is reserved for the
private Gradescope grader so the public repository does not expose a second
implementation of the verifier students are asked to write.
"""

VERIFIER_FUNCTION = "is_valid_tour"


def check_solution_shape(solution):
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
            "message": (
                "statistics['time'] must be a non-negative number "
                "measured in seconds"
            ),
        }

    solution = result["solution"]
    ok, message = check_solution_shape(solution)
    if not ok:
        return {"name": test["name"], "passed": False, "message": message}

    expected_optimum = test.get("expected_optimum")
    if expected_optimum is not None and solution["cost"] != expected_optimum:
        return {
            "name": test["name"],
            "passed": False,
            "message": (
                f"expected optimum cost {expected_optimum}, "
                f"got {solution['cost']}"
            ),
        }

    max_cost = test.get("max_cost")
    if max_cost is not None and solution["cost"] > max_cost:
        known_optimum = test.get("known_optimum")
        extra = (
            f"; known OPT is {known_optimum}"
            if known_optimum is not None
            else ""
        )
        return {
            "name": test["name"],
            "passed": False,
            "message": (
                f"tour cost {solution['cost']} exceeds the public "
                f"quality cap {max_cost}{extra}"
            ),
        }

    verification = run_worker(
        repo_root,
        "traveling_salesperson",
        "verify",
        instance,
        certificate=solution["tour"],
        verifier_function=VERIFIER_FUNCTION,
        k=solution["cost"],
        timeout=test.get("timeout", 10),
    )

    if not verification.get("ok"):
        return {
            "name": test["name"],
            "passed": False,
            "message": (
                "student verifier failed while checking the returned tour: "
                + verification.get("error", "unknown error")
            ),
        }

    if not verification["valid"]:
        return {
            "name": test["name"],
            "passed": False,
            "message": "student verifier says returned tour is not valid at its reported cost",
        }

    known_optimum = test.get("known_optimum")
    if known_optimum is not None:
        gap = 100.0 * (solution["cost"] - known_optimum) / known_optimum
        message = (
            f"ok (cost={solution['cost']}, known OPT={known_optimum}, "
            f"gap={gap:.2f}%)"
        )
    else:
        message = f"ok (cost={solution['cost']})"

    return {"name": test["name"], "passed": True, "message": message}
