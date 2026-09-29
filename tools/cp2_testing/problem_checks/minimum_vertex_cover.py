"""Public CP2 checks for Minimum Vertex Cover.

COURSE INFRASTRUCTURE
Students should not modify this file.

The public solver checks intentionally reuse the student's already-tested
certificate verifier. Independent solution validation is reserved for the
private Gradescope grader so the public repository does not expose a second
implementation of the verifier students are asked to write.
"""

VERIFIER_FUNCTION = "is_vertex_cover"


def run_public_preflight(repo_root, algorithm, run_worker):
    result = run_worker(
        repo_root,
        "minimum_vertex_cover",
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


def check_solution_shape(solution):
    if not isinstance(solution, dict):
        return False, "solution is not a dictionary"

    if "size" not in solution or "vertices" not in solution:
        return False, "solution must contain 'size' and 'vertices'"

    if isinstance(solution["size"], bool) or not isinstance(solution["size"], int):
        return False, "solution['size'] must be an int"

    if not isinstance(solution["vertices"], list):
        return False, "solution['vertices'] must be a list"

    if any(isinstance(v, bool) or not isinstance(v, int) for v in solution["vertices"]):
        return False, "all returned vertices must be ints"

    if len(solution["vertices"]) != len(set(solution["vertices"])):
        return False, "returned vertex list contains duplicates"

    if solution["size"] != len(solution["vertices"]):
        return False, "solution['size'] != len(solution['vertices'])"

    return True, "ok"


def run_public_verifier_test(repo_root, tests_root, test, run_worker):
    instance = tests_root / test["instance"]

    result = run_worker(
        repo_root,
        "minimum_vertex_cover",
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
        "minimum_vertex_cover",
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

    solution = result["solution"]
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

    if algorithm == "exhaustive":
        candidates = statistics.get("candidates")
        if (
            isinstance(candidates, bool)
            or not isinstance(candidates, int)
            or candidates < 0
        ):
            return {
                "name": test["name"],
                "passed": False,
                "message": (
                    "statistics['candidates'] must be a non-negative int "
                    "counting complete candidates examined"
                ),
            }

    ok, message = check_solution_shape(solution)
    if not ok:
        return {"name": test["name"], "passed": False, "message": message}

    expected_optimum = test.get("expected_optimum")
    if expected_optimum is not None and solution["size"] != expected_optimum:
        return {
            "name": test["name"],
            "passed": False,
            "message": (
                f"expected optimum size {expected_optimum}, "
                f"got {solution['size']}"
            ),
        }

    max_size = test.get("max_size")
    if max_size is not None and solution["size"] > max_size:
        return {
            "name": test["name"],
            "passed": False,
            "message": (
                f"cover size {solution['size']} exceeds the public "
                f"nontriviality limit {max_size}"
            ),
        }

    verification = run_worker(
        repo_root,
        "minimum_vertex_cover",
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
            "message": (
                "student verifier failed while checking the returned cover: "
                + verification.get("error", "unknown error")
            ),
        }

    if not verification["valid"]:
        return {
            "name": test["name"],
            "passed": False,
            "message": "student verifier says returned vertices are not a valid cover",
        }

    return {"name": test["name"], "passed": True, "message": "ok"}
