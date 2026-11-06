# Beyond Brute Force

This repository is the starting point for your team's **Beyond Brute Force** project.

The repository has a deliberate ownership boundary:

- `src/course/` contains **course-owned infrastructure**. Do not modify it.
- `src/student/` contains **student-owned implementations**. Your team's algorithms live here.

Course infrastructure may be updated during the semester without overwriting files under `src/student/`.

## Quick Start

**Requirements:** Python **3.10 or newer**, Git, and Internet access when
installing external benchmark data. Use `python3` in the commands below;
on some computers the executable is named `python` instead.

Run all commands from the **root of your team's repository** (the directory
containing `README.md` and `project.json`). Start by accepting the course's
repository assignment, then clone **your team's** repository:

```bash
git clone YOUR_TEAM_REPOSITORY_URL
cd YOUR_TEAM_REPOSITORY_DIRECTORY
python3 --version
```

Do not clone the instructor's starter repository in place of your assigned
team repository. Make sure every team member can clone, commit, and push.

### A. Before your problem is assigned (project selection)

Edit `project.json` to enter your team name, 1–3 member names, and three
**distinct** problem preferences. Leave `"assigned_problem": ""` until the
instructor announces assignments. Then verify the selection-stage metadata:

```bash
python3 tools/check_setup.py --phase selection
```

A blank starter `project.json` is intentionally **not** ready for setup or
submission; fill in its team fields first.

### B. After your problem is assigned

Set `assigned_problem` in `project.json` to the exact canonical problem ID
announced by the instructor (see [Problem IDs](#problem-ids)). Keep the team's
other metadata and preferences intact. Then run:

```bash
python3 tools/check_setup.py --phase assigned
python3 tools/setup_project.py
python3 tools/check_course_files.py
```

The setup script is **`tools/setup_project.py`**; there is no separate
root-level `setup.sh` to run. It downloads the external benchmarks for your
**assigned** problem into Git-ignored directories. Some collections are large;
Internet access is required on the first run. Setup reports the number of
installed/configured external instances and can safely be run again: files
already installed are reused. The integrity check should report `PASSED`.

If `check_setup.py --phase assigned` fails, inspect `project.json` first;
`setup_project.py` cannot install a problem while `assigned_problem` is blank.
See [Post-Assignment Benchmark Setup](#post-assignment-benchmark-setup)
for details.

### C. Start implementing and testing

Your algorithms belong under `src/student/`. Once you begin implementing the
first checkpoint, run its public tests:

```bash
python3 tools/run_cp1_tests.py
```

**A failure is expected with the untouched student stubs**, because these
functions are intentionally not implemented. A failing algorithm test does not
mean the repository setup or benchmark downloads failed. Follow the course
project website for checkpoint requirements and exact interfaces.

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
python3 tools/migrate_project_json.py          # preview only
python3 tools/migrate_project_json.py --apply  # save a .bak backup and migrate
python3 tools/check_setup.py --phase assigned
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
python3 src/solve.py tests/public/minimum_vertex_cover/instances/cycle5.txt \
    --problem mvc --algorithm exhaustive
```

## Post-Assignment Benchmark Setup

External benchmark files are not committed to the repository. After your team's
assigned problem is populated in `project.json`, run the three post-assignment
commands in [Quick Start](#b-after-your-problem-is-assigned). The installer is:

```bash
python3 tools/setup_project.py
```

It reads `assigned_problem`, installs the external collections configured for
that problem, and skips files already installed. Downloaded data lives under
`benchmarks/<problem>/external/` and is ignored by Git; do **not** commit it.
A repeated setup normally reports that the instances are already installed.
You do not need to know or pass the original benchmark collection names.

Only if you deliberately need to redownload external data, use
`python3 tools/setup_project.py --force` (this may take significant time).

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
python3 tools/check_course_files.py
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
python3 tools/run_cp1_tests.py
python3 tools/run_cp2_tests.py
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
