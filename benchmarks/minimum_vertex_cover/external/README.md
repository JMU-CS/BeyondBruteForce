# External benchmark data — Minimum Vertex Cover

After project assignment, run:

```bash
python tools/setup_project.py
```

For this problem the setup tool downloads the official **PACE 2019 Vertex Cover
Exact** archive from its Zenodo record and extracts/converts the 20 challenge
instances selected in the tracked manifest.

The source dataset is:

- *PACE2019: Track 1 - Vertex Cover Instances*, Zenodo record 3368306,
  DOI `10.5281/zenodo.3368306`.

The challenge selection is based on the detailed result tables in Hespe, Lamm,
Schulz, and Strash, *WeGotYouCovered: The Winning Solver from the PACE 2019
Implementation Challenge, Vertex Cover Track*. For each selected row, that report
leaves the minimum-cover column blank because none of the listed exact
configurations solved the instance in the reported experiment. The course
therefore records `known_optimum = null` rather than asserting an optimum.

Downloaded files under this directory are intentionally ignored by Git; this
README and the problem manifest remain tracked so source/provenance information
travels with the repository.
