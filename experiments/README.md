# Experiments

Use this directory for experimental work and results produced during *Beyond Brute Force*.

The intended layout is:

```text
experiments/
├── scripts/     experiment or analysis scripts that should be committed
├── results/     results that should be preserved with the project
└── local/       machine-local files that are intentionally NOT committed
```

## `scripts/`

Place team-created scripts used to run, summarize, or analyze experiments here. Files needed to reproduce important results should be committed to Git.

## `results/`

Place experimental results that are required by a checkpoint or needed to support and reproduce conclusions here. These files are part of the project repository and should be committed when appropriate.

## `local/`

Use `local/` only for disposable or machine-local intermediate files, such as very large temporary outputs that do not belong in the repository.

With the exception of `local/README.md`, files in `experiments/local/` are ignored by Git. They are therefore **not backed up by GitHub and are not included in normal repository submissions**.

Do not put required source code, benchmark instances, final results, checkpoint artifacts, or anything needed to reproduce your conclusions in `experiments/local/`.
