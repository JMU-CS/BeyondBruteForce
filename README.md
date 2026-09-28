# Beyond Brute Force

This repository is the starting point for your team's **Beyond Brute Force** project.

The repository has a deliberate ownership boundary:

- `src/course/` contains **course-owned infrastructure**. Do not modify it.
- `src/student/` contains **student-owned implementations**. Your team's algorithms live here.

Course infrastructure may be updated during the semester without overwriting files under `src/student/`.

## First Steps

1. Complete the root-level `project.json`.
2. Make sure every team member can clone, edit, commit, and push.
3. Run `python tools/check_setup.py` before submitting Checkpoint 1.
4. Use the project website as the source of truth for checkpoint requirements and interfaces.

## Problem IDs

`project.json`, benchmark manifests, and result metadata use the canonical problem IDs:

- `minimum_vertex_cover`
- `traveling_salesperson`
- `minimum_graph_coloring`
- `longest_path`
- `maximum_clique`

For the command line, `src/solve.py` accepts short names:

| Short name | Problem |
|---|---|
| `mvc` | Minimum Vertex Cover |
| `tsp` | Traveling Salesperson |
| `mgc` | Minimum Graph Coloring |
| `lp` | Longest Path |
| `mc` | Maximum Clique |

For example:

```bash
python src/solve.py tests/public/minimum_vertex_cover/instances/cycle5.txt \
    --problem mvc --algorithm exhaustive
```

## Course File Integrity

Course-owned files are recorded in `tools/course_file_manifest.json` with SHA-256 hashes.
Run:

```bash
python tools/check_course_files.py
```

to detect accidental changes to protected course infrastructure. The local manifest is a convenience check; Gradescope should verify protected files against an independent canonical manifest.

The protected areas include `src/course/`, `src/solve.py`, public tests, benchmark collections, and course testing/experiment tools. Student-owned source under `src/student/` is never included in the protected-file manifest.

## Repository Layout

```text
src/
├── solve.py                 # COURSE
├── course/                  # COURSE
│   ├── driver.py
│   ├── common/
│   └── problems/
└── student/                 # STUDENT
    └── problems/
        ├── minimum_vertex_cover/
        ├── traveling_salesperson/
        ├── minimum_graph_coloring/
        ├── longest_path/
        └── maximum_clique/

tests/
├── public/                  # COURSE
└── student/                 # STUDENT

benchmarks/                  # COURSE core benchmark suites
tools/                       # COURSE testing/experiment tools
experiments/                 # STUDENT/generated results
reports/                     # STUDENT
presentation/                # STUDENT
```

## Local Testing

Checkpoint-specific public runners live in `tools/`. For example:

```bash
python tools/run_cp2_tests.py
python tools/run_cp3_tests.py
```

The public-test coverage grows as the project progresses. Gradescope may use additional hidden tests that follow the documented interfaces and input formats.

## Responsibility for Submitted Work

Regardless of which tools or resources contributed to the project, your team is responsible for the contents of the repository. Team members should be prepared to explain submitted code, verify that it is correct, modify it when necessary, and defend conclusions based on its output.
