#!/usr/bin/env python3
"""Mechanical validation of experiment output before the Final Project submission."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {'exact_frontier', 'quality_known', 'heuristic_scale', 'structure'}
RANDOMIZED_SUITES = {'quality_known', 'heuristic_scale', 'structure'}


def load_rows(path: Path):
    """Load required final-project rows from a result directory or JSON file."""
    if path.is_file():
        data = json.loads(path.read_text(encoding='utf-8'))
        return data.get('rows', []), []

    missing_files = []
    rows = []
    for suite in sorted(REQUIRED):
        suite_path = path / f'{suite}.json'
        if not suite_path.is_file():
            missing_files.append(suite_path)
            continue
        data = json.loads(suite_path.read_text(encoding='utf-8'))
        suite_rows = data.get('rows', [])
        rows.extend(suite_rows)
    return rows, missing_files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        'path',
        nargs='?',
        default='experiments/results',
        help=(
            'directory containing exact_frontier.json, quality_known.json, '
            'heuristic_scale.json, and structure.json; a combined JSON file is '
            'also accepted for backward compatibility'
        ),
    )
    a = ap.parse_args()
    path = (ROOT / a.path).resolve()

    rows, missing_files = load_rows(path)
    problems = []
    if missing_files:
        problems.append(
            'missing result files: '
            + ', '.join(str(p.relative_to(ROOT)) for p in missing_files)
        )

    suites = {r.get('suite') for r in rows}
    missing = REQUIRED - suites
    if missing:
        problems.append('missing suites: ' + ', '.join(sorted(missing)))

    invalid = [r for r in rows if r.get('status') == 'OK' and r.get('valid') is False]
    if invalid:
        problems.append(f'{len(invalid)} successful runs contain invalid solutions')

    crossed = [r for r in rows if r.get('bound_valid_when_opt_known') is False]
    if crossed:
        problems.append(
            f'{len(crossed)} bound results cross a known optimum in the wrong direction'
        )

    # Required randomized suites should preserve multiple fixed-seed trials.
    seeds = defaultdict(set)
    for r in rows:
        if (
            r.get('suite') in RANDOMIZED_SUITES
            and str(r.get('algorithm', '')).startswith('heuristic')
            and r.get('status') in {'OK', 'TIMEOUT', 'ERROR'}
        ):
            seeds[(r.get('suite'), r.get('instance_id'), r.get('algorithm'))].add(
                r.get('seed')
            )
    too_few = [
        key for key, values in seeds.items()
        if len({value for value in values if value is not None}) < 3
    ]
    if too_few:
        problems.append(
            f'{len(too_few)} randomized benchmark/algorithm combinations '
            'contain fewer than 3 distinct seeds'
        )

    # Three-person teams must include heuristic2 in each required heuristic-analysis suite.
    try:
        project = json.loads((ROOT / 'project.json').read_text(encoding='utf-8'))
        team_members = project.get('team_members', [])
    except Exception:
        team_members = []
    if isinstance(team_members, list) and len(team_members) == 3:
        required_h2 = {'quality_known', 'heuristic_scale', 'structure'}
        h2_suites = {r.get('suite') for r in rows if r.get('algorithm') == 'heuristic2'}
        missing_h2 = required_h2 - h2_suites
        if missing_h2:
            problems.append(
                'three-person team is missing heuristic2 results for suites: '
                + ', '.join(sorted(missing_h2))
            )

    if problems:
        print('Final Project result validation: FAIL')
        for problem in problems:
            print(' -', problem)
        return 1

    print('Final Project result validation: PASS')
    print(f'Rows: {len(rows)}; suites: {", ".join(sorted(suites))}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
