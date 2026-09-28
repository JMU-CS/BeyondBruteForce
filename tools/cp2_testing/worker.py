#!/usr/bin/env python3
"""Run one student CP2 function in an isolated process.

COURSE INFRASTRUCTURE
Students should not modify this file.
"""

import argparse
import contextlib
import io
import inspect
import json
from pathlib import Path
import sys
import traceback


def build_args(problem: str, algorithm: str, input_file: str | None):
    return argparse.Namespace(
        problem=problem,
        algorithm=algorithm,
        input=input_file,
        stats=None,
        progress=None,
        seed=0,
        test_mode=True,
    )




def format_student_exception(exc: Exception, repo_root: Path) -> str:
    """Return a concise diagnostic focused on frames in student-owned code."""
    lines = [f"{type(exc).__name__}: {exc}"]
    student_locations = []

    # SyntaxError stores its most useful location directly on the exception.
    if isinstance(exc, SyntaxError) and exc.filename and exc.lineno:
        try:
            rel = Path(exc.filename).resolve().relative_to(repo_root)
        except (OSError, ValueError):
            rel = None
        if rel is not None and rel.parts[:2] == ("src", "student"):
            student_locations.append(
                (rel.as_posix(), exc.lineno, "<module>", (exc.text or "").strip())
            )

    for frame in traceback.extract_tb(exc.__traceback__):
        try:
            rel = Path(frame.filename).resolve().relative_to(repo_root)
        except (OSError, ValueError):
            continue
        if rel.parts[:2] != ("src", "student"):
            continue
        location = (rel.as_posix(), frame.lineno, frame.name, (frame.line or "").strip())
        if location not in student_locations:
            student_locations.append(location)

    if student_locations:
        lines.append("Student code:")
        for filename, lineno, function, source in student_locations:
            lines.append(f"  {filename}:{lineno} in {function}")
            if source:
                lines.append(f"    {source}")

    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--problem", required=True)
    parser.add_argument(
        "--action",
        choices=["preflight", "solve", "verify", "bound_preflight", "bound"],
        required=True,
    )
    parser.add_argument("--algorithm", default="exhaustive")
    parser.add_argument("--input")
    parser.add_argument("--certificate-json")
    parser.add_argument("--verifier-function")
    parser.add_argument("--k", type=int)
    ns = parser.parse_args()

    repo_root = Path(ns.repo_root).resolve()
    sys.path.insert(0, str(repo_root / "src"))
    captured = io.StringIO()

    try:
        with contextlib.redirect_stdout(captured):
            from course.problems import canonical_problem_id, get_problem

            canonical = canonical_problem_id(ns.problem)
            problem = get_problem(canonical)

            if ns.action == "preflight":
                if not hasattr(problem, "read_instance"):
                    raise AttributeError(
                        f"course adapter for {canonical} has no read_instance()"
                    )
                if not hasattr(problem, "get_solver"):
                    raise AttributeError(
                        f"course adapter for {canonical} has no get_solver()"
                    )

                # This imports the exhaustive module and catches errors such as
                # missing Namespace imports before graph tests begin.
                solver = problem.get_solver(ns.algorithm)
                if not callable(solver):
                    raise TypeError("get_solver() did not return a callable")

                if ns.verifier_function:
                    module_name = f"student.problems.{canonical}.verifier"
                    verifier_module = __import__(
                        module_name, fromlist=[ns.verifier_function]
                    )
                    verifier = getattr(
                        verifier_module, ns.verifier_function
                    )
                    if not callable(verifier):
                        raise TypeError(
                            f"{ns.verifier_function} is not callable"
                        )
                    parameters = list(inspect.signature(verifier).parameters)
                    if len(parameters) != 3:
                        raise TypeError(
                            f"{ns.verifier_function} must accept exactly three "
                            "parameters: the instance, the certificate, and k"
                        )

                payload = {"ok": True}

            elif ns.action == "bound_preflight":
                if not hasattr(problem, "read_instance"):
                    raise AttributeError(
                        f"course adapter for {canonical} has no read_instance()"
                    )
                if not hasattr(problem, "get_bound"):
                    raise AttributeError(
                        f"course adapter for {canonical} has no get_bound()"
                    )
                bound_function = problem.get_bound()
                if not callable(bound_function):
                    raise TypeError("get_bound() did not return a callable")
                bound_kind = getattr(problem, "BOUND_KIND", None)
                if bound_kind not in ("lower", "upper"):
                    raise ValueError(
                        "problem package must define BOUND_KIND as 'lower' or 'upper'"
                    )
                payload = {"ok": True, "bound_kind": bound_kind}

            else:
                if not ns.input:
                    raise ValueError("--input is required for solve/verify/bound")

                call_args = build_args(
                    ns.problem, ns.algorithm, ns.input
                )
                instance = problem.read_instance(ns.input, call_args)

                if ns.action == "bound":
                    if not hasattr(problem, "get_bound"):
                        raise AttributeError(
                            f"course adapter for {canonical} has no get_bound()"
                        )
                    bound_function = problem.get_bound()
                    if not callable(bound_function):
                        raise TypeError("get_bound() did not return a callable")
                    bound_kind = getattr(problem, "BOUND_KIND", None)
                    if bound_kind not in ("lower", "upper"):
                        raise ValueError(
                            "problem package must define BOUND_KIND as 'lower' or 'upper'"
                        )
                    value = bound_function(instance)
                    if isinstance(value, bool) or not isinstance(value, (int, float)):
                        raise TypeError("bound function must return a numeric value")
                    payload = {
                        "ok": True,
                        "bound": value,
                        "bound_kind": bound_kind,
                    }

                elif ns.action == "solve":
                    solver = problem.get_solver(ns.algorithm)
                    result = solver(instance, call_args)

                    if not isinstance(result, tuple) or len(result) != 2:
                        raise TypeError(
                            "solve() must return "
                            "(solution_dict, statistics_dict)"
                        )

                    solution, statistics = result

                    if not isinstance(solution, dict):
                        raise TypeError(
                            "solve() must return solution as a dictionary"
                        )
                    if not isinstance(statistics, dict):
                        raise TypeError(
                            "solve() must return statistics as a dictionary"
                        )

                    payload = {
                        "ok": True,
                        "solution": solution,
                        "statistics": statistics,
                    }

                else:
                    if not ns.verifier_function:
                        raise ValueError(
                            "--verifier-function is required for verify"
                        )

                    module_name = f"student.problems.{canonical}.verifier"
                    verifier_module = __import__(
                        module_name, fromlist=[ns.verifier_function]
                    )
                    verifier = getattr(
                        verifier_module, ns.verifier_function
                    )
                    if ns.k is None:
                        raise ValueError("--k is required for verify")
                    certificate = json.loads(ns.certificate_json)
                    valid = verifier(instance, certificate, ns.k)

                    if not isinstance(valid, bool):
                        raise TypeError("verifier must return bool")

                    payload = {"ok": True, "valid": valid}

    except Exception as exc:
        payload = {
            "ok": False,
            "error_type": type(exc).__name__,
            "error": format_student_exception(exc, repo_root),
            "traceback": traceback.format_exc(),
        }

    payload["captured_stdout"] = captured.getvalue()
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
