# Course Infrastructure

The repository separates course-owned and student-owned source code.

- `src/course/` and `src/solve.py` are course-owned.
- `src/student/` is student-owned.
- `tests/public/` and `benchmarks/` are course-owned.
- `tests/student/`, `experiments/`, `reports/`, and `presentation/` are student-owned.

Run `python tools/check_course_files.py` to compare protected course files against the supplied SHA-256 manifest.

Gradescope should not trust the submitted manifest as its source of truth; the autograder should carry its own canonical hashes for the infrastructure version required by that checkpoint.

Current infrastructure version: **17** (v16 benchmark source repairs retained; precise SNAP source-edge validation with self-loops, including `as_20000102`).

For SNAP external benchmark graphs, `source_m` is the number of distinct source edges **including self-loops**. Installed instances contain simple, undirected graphs, with duplicate/reverse edges and self-loops removed. Where `m` is explicitly specified, it is the exact number of normalized edges. These values need not equal `source_m`.
