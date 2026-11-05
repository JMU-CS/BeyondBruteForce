# Beyond Brute Force

This repository is the starting point for your team's **Beyond Brute Force** project.

The repository has a deliberate ownership boundary:

- `src/course/` contains **course-owned infrastructure**. Do not modify it.
- `src/student/` contains **student-owned implementations**. Your team's algorithms live here.

Course infrastructure may be updated during the semester without overwriting files under `src/student/`.

## First Steps

1. Update the team metadata in `project.json` (see below), including your team's
   assigned problem once assignments are announced. One, two, or three students
   are allowed, and each member has a `name` field only (no GitHub username).
2. Make sure every team member can clone, edit, commit, and push.
3. Before project selection, run `python tools/check_setup.py --phase selection`.
   After the problem is assigned, run `python tools/check_setup.py --phase assigned`.
   Plain `python tools/check_setup.py` accepts **either** phase.
4. Once `assigned_problem` is populated, run `python tools/setup_project.py`
   to install the external benchmark data for your assigned problem. Re-running
   setup is safe; previously downloaded data is reused by default.
5. Use the project website as the source of truth for checkpoint requirements
   and interfaces.

## Team configuration (`project.json`)

The root `project.json` must contain **exactly these top-level fields**:

- `team_name`: a nonempty team name;
- `team_members`: a list of **1–3 distinct students**, each with only a
  nonempty `name` field;
- `project_preferences`: **three different** canonical problem identifiers,
  ordered by preference;
- `assigned_problem`: initially `""` for Project Selection; after assignments,
  the canonical identifier of the team's assigned problem. This assignment does
  not have to be one of the team's three preferences.

For example, a two-person team assigned Minimum Vertex Cover would use:

```json
{
  "team_name": "Example Team",
  "team_members": [
    {"name": "First Student"},
    {"name": "Second Student"}
  ],
  "project_preferences": [
    "minimum_vertex_cover",
    "maximum_clique",
    "minimum_graph_coloring"
  ],
  "assigned_problem": "minimum_vertex_cover"
}
```

The distributed template includes **one blank member entry**. Add another
`{"name": "..."}` object for a two- or three-person team; do not leave unused
empty member entries. Keep preferences intact after assignment, unless the
instructor directs otherwise.

`project.json` is **team-owned data**: future course infrastructure patches
must not overwrite your team's metadata or assigned problem. The setup checker
validates the schema; it cannot determine whether the instructor assigned the
correct problem to your particular team.

If you already completed a `project.json` using the older format with a `github`
field for each member, **do not replace the file with the starter template**.
The migration utility removes only those obsolete fields and preserves the
team's existing values:

```bash
python tools/migrate_project_json.py          # preview only
python tools/migrate_project_json.py --apply  # save a .bak backup and migrate
python tools/check_setup.py --phase assigned
```

The `.bak` backup is ignored by Git; keep it privately until your corrected
`project.json` is committed. Course patches must never include `project.json`.

## Problem IDs

`project.json`, benchmark manifests, and result metadata use the canonical problem IDs:

- `minimum_vertex_cover`
- `traveling_salesperson`
- `minimum_graph_coloring`
- `longest_path`
- `maximum_clique`

For the command line, `src/solve.py` accepts either the canonical IDs above or these short aliases:

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

## Post-Assignment Benchmark Setup

External benchmark files are not committed to the repository. After your assigned problem appears in `project.json`, run:

```bash
python tools/setup_project.py
```

The setup tool reads `assigned_problem`, installs the benchmark collection configured for that problem, and skips files that are already present. Downloaded files live under `benchmarks/<problem>/external/` and are ignored by Git. You do not need to know or pass the names of the original benchmark collections.

## Decision-Problem Verifiers

Checkpoint 1 connects the implementation directly to the NP decision problem. Each
student verifier receives the problem instance, a proposed certificate, and the
decision threshold `k`. It returns `True` exactly when that certificate proves a YES
instance.

The threshold direction depends on the problem:

| Problem | Verifier threshold |
|---|---|
| Minimum Vertex Cover | cover size `<= k` |
| Minimum Graph Coloring | number of colors `<= k` |
| Traveling Salesperson | tour cost `<= k` |
| Longest Path | path length `>= k` |
| Maximum Clique | clique size `>= k` |

The optimization solvers may reuse these functions. For example, a candidate MVC
cover `C` can be checked with `is_vertex_cover(graph, C, len(C))`. The problem
specification on the course website gives the exact required signature and semantics
for each verifier.

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
experiments/                 # STUDENT experiment materials/results
reports/                     # STUDENT
presentation/                # STUDENT
```


## Experiment Files

Use the experiment directories as follows:

```text
experiments/
├── scripts/     # commit scripts needed to reproduce your work
├── results/     # commit results needed for checkpoints/analysis
└── local/       # machine-local files; NOT tracked by Git
```

Everything under `experiments/local/` except its README is intentionally ignored by Git. Files placed there are **not backed up by GitHub and are not included in normal repository submissions**. Do not place required code, benchmark instances, checkpoint results, or anything needed to reproduce your conclusions in `experiments/local/`.

## Local Testing

Checkpoint-specific public runners live in `tools/`. For example:

```bash
python tools/run_cp1_tests.py
python tools/run_cp2_tests.py
```

Local test runners show detailed diagnostics by default when student code raises
an exception, including the student file and line number when available. Add
`--quiet` for compact failure messages.

For Checkpoint 1, the public solver tests first test your verifier directly and then
reuse that verifier to validate certificates returned by your exhaustive solver. If
the verifier tests fail, dependent solver tests are skipped to avoid misleading
follow-on errors. Gradescope performs its own independent private validation and does
not rely on your verifier when determining whether a solver result is correct.

The public-test coverage grows as the project progresses. Gradescope may use additional hidden tests that follow the documented interfaces and input formats.

## Responsibility for Submitted Work

Regardless of which tools or resources contributed to the project, your team is responsible for the contents of the repository. Team members should be prepared to explain submitted code, verify that it is correct, modify it when necessary, and defend conclusions based on its output.
