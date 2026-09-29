"""Public Checkpoint 1/Checkpoint 2 checks for Maximum Clique.

COURSE INFRASTRUCTURE
Students should not modify this file.

The public solver checks intentionally reuse the student's independently tested
certificate verifier. Private Gradescope checks validate returned cliques with
an instructor implementation.
"""

VERIFIER_FUNCTION = "is_clique"


def check_solution_shape(solution):
    if not isinstance(solution, dict):
        return False, "solution is not a dictionary"
    if "size" not in solution or "vertices" not in solution:
        return False, "solution must contain 'size' and 'vertices'"

    size = solution["size"]
    vertices = solution["vertices"]
    if isinstance(size, bool) or not isinstance(size, int):
        return False, "solution['size'] must be an int"
    if size < 0:
        return False, "solution['size'] must be non-negative"
    if not isinstance(vertices, list):
        return False, "solution['vertices'] must be a list"
    if any(isinstance(v, bool) or not isinstance(v, int) for v in vertices):
        return False, "all returned vertices must be ints"
    if len(vertices) != len(set(vertices)):
        return False, "returned vertex list contains duplicates"
    if size != len(vertices):
        return False, "solution['size'] must equal len(solution['vertices'])"
    return True, "ok"


def run_public_preflight(repo_root, algorithm, run_worker):
    result = run_worker(
        repo_root,
        "maximum_clique",
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
        "maximum_clique",
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
        "message": "ok" if passed else f"expected {test['expected']}, got {result['valid']}",
    }


def run_public_solver_test(repo_root, tests_root, test, algorithm, run_worker):
    instance = tests_root / test["instance"]
    result = run_worker(
        repo_root,
        "maximum_clique",
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

    solution = result["solution"]
    ok, message = check_solution_shape(solution)
    if not ok:
        return {"name": test["name"], "passed": False, "message": message}

    expected = test.get("expected_optimum")
    if expected is not None and solution["size"] != expected:
        return {
            "name": test["name"],
            "passed": False,
            "message": f"expected optimum size {expected}, got {solution['size']}",
        }

    minimum = test.get("min_size")
    if minimum is not None and solution["size"] < minimum:
        known = test.get("known_optimum")
        extra = f"; known OPT is {known}" if known is not None else ""
        return {
            "name": test["name"],
            "passed": False,
            "message": f"clique size {solution['size']} is below the public quality floor {minimum}{extra}",
        }

    verification = run_worker(
        repo_root,
        "maximum_clique",
        "verify",
        instance,
        certificate=solution["vertices"],
        verifier_function=VERIFIER_FUNCTION,
        k=solution["size"],
        timeout=test.get("timeout", 10),
    )
    if not verification.get("ok"):
        return {
            "name": test["name"],
            "passed": False,
            "message": "student verifier failed while checking the returned clique: "
            + verification.get("error", "unknown error"),
        }
    if not verification["valid"]:
        return {
            "name": test["name"],
            "passed": False,
            "message": "student verifier says returned vertices are not a valid clique at the reported size",
        }

    known = test.get("known_optimum")
    if known is not None and known > 0:
        gap = 100.0 * (known - solution["size"]) / known
        msg = f"ok (size={solution['size']}, known OPT={known}, gap={gap:.2f}%)"
    else:
        msg = f"ok (size={solution['size']})"
    return {"name": test["name"], "passed": True, "message": msg}
