# Course Benchmark Suites

The benchmark framework is **course infrastructure**. Students run it and analyze
its output; they are not expected to write timing, CSV, timeout, validation, or
benchmark-generation code.

Each implemented problem has a tracked manifest and course-provided instances:

```text
benchmarks/PROBLEM/manifest.json
benchmarks/PROBLEM/instances/
```

Larger public benchmark files are installed separately under:

```text
benchmarks/PROBLEM/external/
```

The external files are intentionally ignored by Git. Their provenance and any
published reference values belong in tracked benchmark metadata.

## Post-assignment setup

After the instructor assigns your team's problem and `assigned_problem` has been
set in `project.json`, run:

```bash
python tools/setup_project.py
```

The setup command determines your problem from `project.json` and installs the
external benchmark data configured for that problem. It is safe to run the command
again; files that are already installed are skipped unless `--force` is used.

`tools/install_external_benchmarks.py` is the lower-level installer. Normal student
use does not require arguments. Instructors can override the problem when debugging:

```bash
python tools/install_external_benchmarks.py --problem minimum_vertex_cover
python tools/install_external_benchmarks.py --all
```

## Required suites

- `readiness` — tiny Checkpoint 2 smoke test of improved exact, heuristic1, the bound,
  validation, timing, and result generation.
- `exact_frontier` — compare exhaustive and improved exact on increasingly
  challenging instances with known optima.
- `quality_known` — compare heuristic solution quality and bound quality when
  OPT is known.
- `heuristic_scale` — run heuristic(s) and the bound after exact computation is
  no longer practical; OPT may be unknown.
- `structure` — hold size approximately fixed while varying one course-selected
  structural characteristic.

Run, for example:

```bash
python tools/run_experiments.py --suite readiness
python tools/run_experiments.py --suite exact_frontier
python tools/run_experiments.py --all
```

Results are written to `experiments/latest.csv` and `experiments/latest.json`,
with timestamped copies retained as well.

## Known optimum versus computed bound

`known_optimum` is instructor metadata. It is present only when the course has a
source supporting the exact optimum for that benchmark. `bound_value` is computed
by the team's bound function. They are intentionally separate fields.

For a minimization problem with a lower bound, a large-instance result might be:

```text
bound_value = 117
objective   = 126
known_optimum = null
```

which certifies only `117 <= OPT <= 126`.

## Provenance for external benchmarks

Every externally sourced benchmark entry must identify where the instance came
from. The preferred manifest form is:

```json
{
  "id": "example-instance",
  "file": "external/example-instance.txt",
  "origin": "external",
  "known_optimum": null,
  "best_known": 317,
  "published_lower_bound": 302,
  "source": {
    "collection": "Benchmark Collection Name",
    "instance": "original-instance-name",
    "url": "https://example.org/instance",
    "citation": "Collection or paper citation"
  },
  "reference": {
    "best_known": {
      "url": "https://example.org/results",
      "citation": "Source establishing the best-known value"
    },
    "published_lower_bound": {
      "url": "https://example.org/results",
      "citation": "Source establishing the lower bound"
    }
  }
}
```

The `source` object describes the **instance itself**. The optional `reference`
object describes where a claimed optimum, best-known value, or published bound
came from when that evidence comes from a different source. Do not treat a
best-known feasible solution as an optimum unless the cited reference establishes
optimality.

For backward compatibility, the experiment runner also accepts the older flat
`source` and `source_url` fields. New external entries should use the structured
form above.

## Open challenge suites

Problems may also provide a `challenge_open` suite populated by
`tools/setup_project.py`. These externally sourced instances are intended for
heuristic improvement and leaderboard-style comparisons when the course is not
claiming a known optimum. Their tracked manifest entries identify the original
source and citation.

For an open challenge, report the best feasible objective found and the relevant
valid bound as separate quantities. Do not infer that an externally published or
class best-so-far value is optimal unless the manifest cites a source that proves
optimality.

## Optional `geng` suites

`geng` (from nauty) generates non-isomorphic graphs. It is useful for extensions
that examine *all* non-isomorphic graphs in a small size/edge range rather than
a random sample.

macOS:

```bash
brew install nauty
```

Ubuntu:

```bash
sudo apt install nauty
```

The course wrapper detects both the Homebrew command `geng` and Ubuntu's
`nauty-geng` command.

Example:

```bash
python tools/generate_geng_suite.py --n 9 --edges 12:20 --connected --limit 300
```

The command prints the corresponding `run_experiments.py` invocation. `geng` is
**not required for the core checkpoint**, because required instances are already
materialized in the repository.
