# Beyond Brute Force starter-repo consistency patch (v14)

This patch is intended to be copied over the current starter repository. It does not include student algorithm files.

Changes:
- makes the four non-MVC public checkers enforce `statistics["candidates"]` consistently with MVC;
- improves solver CLI help so canonical problem IDs and short aliases are both clear;
- stores experiment output as one stable JSON/CSV pair per suite under `experiments/results/`, with timestamped copies;
- updates `validate_final_results.py` so the four required final suites may be run separately and validated from `experiments/results/`;
- updates experiment-related repository documentation to match the per-suite output layout;
- standardizes the setup-stage name to **Project Selection** (removing the older **Project Selection & Setup** wording);
- bumps the protected course infrastructure manifest to version 14 and regenerates its SHA-256 entries.
