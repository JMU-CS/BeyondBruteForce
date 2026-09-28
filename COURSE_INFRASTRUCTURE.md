# Course Infrastructure

The repository separates course-owned and student-owned source code.

- `src/course/` and `src/solve.py` are course-owned.
- `src/student/` is student-owned.
- `tests/public/` and `benchmarks/` are course-owned.
- `tests/student/`, `experiments/`, `reports/`, and `presentation/` are student-owned.

Run `python tools/check_course_files.py` to compare protected course files against the supplied SHA-256 manifest.

Gradescope should not trust the submitted manifest as its source of truth; the autograder should carry its own canonical hashes for the infrastructure version required by that checkpoint.
