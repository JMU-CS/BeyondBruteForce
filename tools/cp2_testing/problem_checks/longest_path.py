"""Public CP2/CP3 checks for Longest Path.

COURSE INFRASTRUCTURE
Students should not modify this file.

The public solver checks intentionally reuse the student's independently tested
certificate verifier.  Private Gradescope checks validate returned paths with
an instructor implementation.
"""

VERIFIER_FUNCTION = "is_valid_path"


def check_solution_shape(solution):
    if not isinstance(solution, dict):
        return False, "solution is not a dictionary"

    if "length" not in solution or "vertices" not in solution:
        return False, "solution must contain 'length' and 'vertices'"

    length = solution["length"]
    vertices = solution["vertices"]

    if isinstance(length, bool) or not isinstance(length, int):
        return False, "solution['length'] must be an int"
    if length < 0:
        return False, "solution['length'] must be non-negative"

    if not isinstance(vertices, list):
        return False, "solution['vertices'] must be a list"
    if any(isinstance(v, bool) or not isinstance(v, int) for v in vertices):
        return False, "all returned path entries must be ints"
    if not vertices:
        return False, "solution['vertices'] must contain at least one vertex"
    if length != len(vertices) - 1:
        return False, "solution['length'] must equal len(solution['vertices']) - 1"

    return True, "ok"


def run_public_preflight(repo_root, algorithm, run_worker):
    result = run_worker(
        repo_root,
        "longest_path",
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
        "longest_path",
        "verify",
        instance,
        certificate=test["vertices"],
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
        "longest_path",
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
    if expected_optimum is not None and solution["length"] != expected_optimum:
        return {
            "name": test["name"],
            "passed": False,
            "message": (
                f"expected optimum length {expected_optimum}, "
                f"got {solution['length']}"
            ),
        }

    min_length = test.get("min_length")
    if min_length is not None and solution["length"] < min_length:
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
                f"path length {solution['length']} is below the public "
                f"quality floor {min_length}{extra}"
            ),
        }

    verification = run_worker(
        repo_root,
        "longest_path",
        "verify",
        instance,
        certificate=solution["vertices"],
        verifier_function=VERIFIER_FUNCTION,
        k=solution["length"],
        timeout=test.get("timeout", 10),
    )

    if not verification.get("ok"):
        return {
            "name": test["name"],
            "passed": False,
            "message": (
                "student verifier failed while checking the returned path: "
                + verification.get("error", "unknown error")
            ),
        }

    if not verification["valid"]:
        return {
            "name": test["name"],
            "passed": False,
            "message": "student verifier says returned vertices are not a valid path at the reported length",
        }

    known_optimum = test.get("known_optimum")
    if known_optimum is not None and known_optimum > 0:
        gap = 100.0 * (known_optimum - solution["length"]) / known_optimum
        message = (
            f"ok (length={solution['length']}, known OPT={known_optimum}, "
            f"gap={gap:.2f}%)"
        )
    else:
        message = f"ok (length={solution['length']})"

    return {"name": test["name"], "passed": True, "message": message}
