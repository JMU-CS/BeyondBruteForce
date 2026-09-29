"""Shared public milestone test runner.

COURSE INFRASTRUCTURE
Students should not modify this file.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
import importlib
import json
import math
from pathlib import Path
import subprocess
import sys


def run_worker(
    repo_root: Path,
    problem: str,
    action: str,
    instance: Path | None = None,
    *,
    algorithm: str = "exhaustive",
    certificate=None,
    verifier_function=None,
    k: int | None = None,
    timeout: float = 10.0,
):
    worker = repo_root / "tools" / "public_testing" / "worker.py"
    cmd = [
        sys.executable,
        str(worker),
        "--repo-root", str(repo_root),
        "--problem", problem,
        "--action", action,
        "--algorithm", algorithm,
    ]

    if instance is not None:
        cmd += ["--input", str(instance)]

    if certificate is not None:
        cmd += ["--certificate-json", json.dumps(certificate)]

    if verifier_function is not None:
        cmd += ["--verifier-function", verifier_function]

    if k is not None:
        cmd += ["--k", str(k)]

    try:
        completed = subprocess.run(
            cmd,
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "error_type": "Timeout",
            "error": f"test exceeded {timeout:.1f} seconds",
        }

    if completed.returncode != 0:
        return {
            "ok": False,
            "error_type": "WorkerFailure",
            "error": completed.stderr.strip() or "worker exited nonzero",
        }

    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {
            "ok": False,
            "error_type": "InvalidWorkerOutput",
            "error": completed.stdout[-1000:],
        }


def load_manifest(path: Path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_checker(problem: str):
    return importlib.import_module(f"public_testing.problem_checks.{problem}")


def run_suite(
    repo_root: Path,
    manifest_path: Path,
    algorithm: str,
    jobs: int,
    name_filter=None,
):
    manifest = load_manifest(manifest_path)
    problem = manifest["problem"]
    checker = load_checker(problem)
    tests_root = manifest_path.parent

    # Import/interface check first.
    preflight = checker.run_public_preflight(
        repo_root, algorithm, run_worker
    )
    if not preflight["passed"]:
        return [preflight], [], []

    # Then test the certificate verifier independently.
    verifier_results = []
    for test in manifest.get("verifier_tests", []):
        if name_filter and name_filter not in test["name"]:
            continue

        verifier_results.append(
            checker.run_public_verifier_test(
                repo_root, tests_root, test, run_worker
            )
        )

    verifier_ok = all(
        result["passed"] for result in verifier_results
    )

    solver_tests = [
        test
        for test in manifest.get("solver_tests", [])
        if not name_filter or name_filter in test["name"]
    ]

    solver_results = []

    # Public solver checks reuse the student's verifier after testing it
    # independently above. If the verifier is broken, running the solver tests
    # would only create repetitive or misleading failures. The private
    # Gradescope grader validates solver certificates independently.
    runnable = []
    for test in solver_tests:
        if not verifier_ok:
            solver_results.append({
                "name": test["name"],
                "passed": False,
                "skipped": True,
                "message": (
                    "skipped because one or more verifier tests failed"
                ),
            })
        else:
            runnable.append(test)

    if jobs <= 1:
        for test in runnable:
            solver_results.append(
                checker.run_public_solver_test(
                    repo_root,
                    tests_root,
                    test,
                    algorithm,
                    run_worker,
                )
            )
    else:
        with ThreadPoolExecutor(max_workers=jobs) as pool:
            futures = {
                pool.submit(
                    checker.run_public_solver_test,
                    repo_root,
                    tests_root,
                    test,
                    algorithm,
                    run_worker,
                ): test["name"]
                for test in runnable
            }

            for future in as_completed(futures):
                solver_results.append(future.result())

    order = {test["name"]: i for i, test in enumerate(solver_tests)}
    solver_results.sort(key=lambda result: order[result["name"]])

    return [preflight], verifier_results, solver_results


def run_bound_suite(repo_root: Path, manifest_path: Path, jobs: int = 1):
    """Run the public polynomial-time bound tests for Checkpoint 2."""
    manifest = load_manifest(manifest_path)
    problem = manifest["problem"]
    tests_root = manifest_path.parent
    expected_kind = manifest["bound_kind"]

    pre = run_worker(
        repo_root,
        problem,
        "bound_preflight",
        timeout=5,
    )
    if not pre.get("ok"):
        return [{
            "name": "bound imports/interface",
            "passed": False,
            "message": pre.get("error", "bound preflight failed"),
        }]

    if pre.get("bound_kind") != expected_kind:
        return [{
            "name": "bound imports/interface",
            "passed": False,
            "message": (
                f"expected {expected_kind} bound, problem package reports "
                f"{pre.get('bound_kind')!r}"
            ),
        }]

    results = [{
        "name": "bound imports/interface",
        "passed": True,
        "message": "ok",
    }]

    def one(test):
        instance = tests_root / test["instance"]
        execution = run_worker(
            repo_root,
            problem,
            "bound",
            instance,
            timeout=test.get("timeout", 5),
        )
        name = f"bound: {test['name']}"
        if not execution.get("ok"):
            return {
                "name": name,
                "passed": False,
                "message": execution.get("error", "bound execution failed"),
            }

        value = execution.get("bound")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return {"name": name, "passed": False, "message": "bound must be numeric"}
        if not math.isfinite(float(value)):
            return {"name": name, "passed": False, "message": "bound must be finite"}
        if test.get("integer", False) and not float(value).is_integer():
            return {"name": name, "passed": False, "message": "bound must be an integer"}

        optimum = test.get("known_optimum")
        if optimum is not None:
            if expected_kind == "lower" and value > optimum:
                return {
                    "name": name,
                    "passed": False,
                    "message": f"lower bound {value} exceeds known optimum {optimum}",
                }
            if expected_kind == "upper" and value < optimum:
                return {
                    "name": name,
                    "passed": False,
                    "message": f"upper bound {value} is below known optimum {optimum}",
                }

        if "expected_min" in test and value < test["expected_min"]:
            return {
                "name": name,
                "passed": False,
                "message": f"bound {value} is weaker than required minimum {test['expected_min']}",
            }
        if "expected_max" in test and value > test["expected_max"]:
            return {
                "name": name,
                "passed": False,
                "message": f"bound {value} is weaker than required maximum {test['expected_max']}",
            }

        return {"name": name, "passed": True, "message": f"ok (bound={value})"}

    tests = manifest.get("bound_tests", [])
    if jobs <= 1:
        results.extend(one(test) for test in tests)
    else:
        with ThreadPoolExecutor(max_workers=jobs) as pool:
            futures = {pool.submit(one, test): i for i, test in enumerate(tests)}
            ordered = [None] * len(tests)
            for future in as_completed(futures):
                ordered[futures[future]] = future.result()
            results.extend(ordered)

    return results
