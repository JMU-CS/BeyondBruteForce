"""Public Checkpoint 1/Checkpoint 2 checks for Minimum Graph Coloring.

COURSE INFRASTRUCTURE
Students should not modify this file.

The public solver checks intentionally reuse the student's independently tested
certificate verifier. Private Gradescope checks validate returned colorings with
an instructor implementation.
"""

VERIFIER_FUNCTION = "is_valid_coloring"


def check_solution_shape(solution):
    if not isinstance(solution, dict):
        return False, "solution is not a dictionary"
    if "num_colors" not in solution or "colors" not in solution:
        return False, "solution must contain 'num_colors' and 'colors'"

    num_colors = solution["num_colors"]
    colors = solution["colors"]
    if isinstance(num_colors, bool) or not isinstance(num_colors, int):
        return False, "solution['num_colors'] must be an int"
    if num_colors < 0:
        return False, "solution['num_colors'] must be non-negative"
    if not isinstance(colors, list):
        return False, "solution['colors'] must be a list"
    if any(isinstance(c, bool) or not isinstance(c, int) for c in colors):
        return False, "all color labels must be ints"
    if any(c < 0 for c in colors):
        return False, "solution color labels must be non-negative"

    distinct = set(colors)
    if num_colors != len(distinct):
        return False, "solution['num_colors'] must equal the number of distinct colors"
    if num_colors > 0 and distinct != set(range(num_colors)):
        return False, "solver output must normalize colors to 0,1,...,num_colors-1"
    return True, "ok"


def run_public_preflight(repo_root, algorithm, run_worker):
    result = run_worker(
        repo_root,
        "minimum_graph_coloring",
        "preflight",
        algorithm=algorithm,
        verifier_function=VERIFIER_FUNCTION,
        timeout=5,
    )
    return {
        "name": "Required files and functions import",
        "passed": bool(result.get("ok")),
        "message": "ok" if result.get("ok") else result.get("error", "import/interface check failed"),
    }


def run_public_verifier_test(repo_root, tests_root, test, run_worker):
    instance = tests_root / test["instance"]
    result = run_worker(
        repo_root,
        "minimum_graph_coloring",
        "verify",
        instance,
        certificate=test["colors"],
        verifier_function=VERIFIER_FUNCTION,
        k=test["k"],
        timeout=test.get("timeout", 5),
    )
    name = f"verifier: {test['name']}"
    if not result.get("ok"):
        return {"name": name, "passed": False, "message": result.get("error", "verifier failed")}
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
        "minimum_graph_coloring",
        "solve",
        instance,
        algorithm=algorithm,
        timeout=test.get("timeout", 10),
    )
    if not result.get("ok"):
        return {"name": test["name"], "passed": False, "message": result.get("error", "solver failed")}

    statistics = result.get("statistics")
    if not isinstance(statistics, dict):
        return {"name": test["name"], "passed": False, "message": "statistics must be a dictionary"}
    elapsed = statistics.get("time")
    if isinstance(elapsed, bool) or not isinstance(elapsed, (int, float)) or elapsed < 0:
        return {"name": test["name"], "passed": False, "message": "statistics['time'] must be a non-negative number measured in seconds"}

    solution = result["solution"]
    ok, message = check_solution_shape(solution)
    if not ok:
        return {"name": test["name"], "passed": False, "message": message}

    expected = test.get("expected_optimum")
    if expected is not None and solution["num_colors"] != expected:
        return {"name": test["name"], "passed": False, "message": f"expected optimum {expected} colors, got {solution['num_colors']}"}

    maximum = test.get("max_num_colors")
    if maximum is not None and solution["num_colors"] > maximum:
        known = test.get("known_optimum")
        extra = f"; known OPT is {known}" if known is not None else ""
        return {"name": test["name"], "passed": False, "message": f"coloring uses {solution['num_colors']} colors, exceeding the public quality cap {maximum}{extra}"}

    verification = run_worker(
        repo_root,
        "minimum_graph_coloring",
        "verify",
        instance,
        certificate=solution["colors"],
        verifier_function=VERIFIER_FUNCTION,
        k=solution["num_colors"],
        timeout=test.get("timeout", 10),
    )
    if not verification.get("ok"):
        return {"name": test["name"], "passed": False, "message": "student verifier failed while checking returned coloring: " + verification.get("error", "unknown error")}
    if not verification["valid"]:
        return {"name": test["name"], "passed": False, "message": "student verifier says returned assignment is not a valid coloring at the reported threshold"}

    known = test.get("known_optimum")
    if known is not None and known > 0:
        gap = 100.0 * (solution["num_colors"] - known) / known
        msg = f"ok (colors={solution['num_colors']}, known OPT={known}, gap={gap:.2f}%)"
    else:
        msg = f"ok (colors={solution['num_colors']})"
    return {"name": test["name"], "passed": True, "message": msg}
