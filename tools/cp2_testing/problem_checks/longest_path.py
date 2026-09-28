"""Public CP2 checker scaffold for longest_path.

COURSE INFRASTRUCTURE
Students should not modify this file.

The shared runner already dispatches to this module. Add the problem-specific
public checks once this problem's CP2 solution dictionary is finalized.
"""


def run_public_verifier_test(repo_root, tests_root, test, run_worker):
    return {
        "name": f"verifier: {test['name']}",
        "passed": False,
        "message": "public checker not finalized for longest_path",
    }


def run_public_solver_test(
    repo_root, tests_root, test, algorithm, run_worker
):
    return {
        "name": test["name"],
        "passed": False,
        "message": "public checker not finalized for longest_path",
    }


def run_public_preflight(repo_root, algorithm, run_worker):
    result = run_worker(
        repo_root,
        "longest_path",
        "preflight",
        algorithm=algorithm,
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
