#!/usr/bin/env python3
"""Mechanical validation of experiment output before CP4 submission."""
from __future__ import annotations
import argparse, json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REQUIRED={'exact_frontier','quality_known','heuristic_scale','structure'}
RANDOMIZED_SUITES={'quality_known','heuristic_scale','structure'}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('file',nargs='?',default='experiments/latest.json'); a=ap.parse_args()
    path=(ROOT/a.file).resolve(); data=json.loads(path.read_text()); rows=data.get('rows',[])
    suites={r.get('suite') for r in rows}; missing=REQUIRED-suites
    problems=[]
    if missing: problems.append('missing suites: '+', '.join(sorted(missing)))
    invalid=[r for r in rows if r.get('status')=='OK' and r.get('valid') is False]
    if invalid: problems.append(f'{len(invalid)} successful runs contain invalid solutions')
    crossed=[r for r in rows if r.get('bound_valid_when_opt_known') is False]
    if crossed: problems.append(f'{len(crossed)} bound results cross a known optimum in the wrong direction')

    # Required randomized suites should preserve multiple fixed-seed trials.
    seeds=defaultdict(set)
    for r in rows:
        if r.get('suite') in RANDOMIZED_SUITES and str(r.get('algorithm','')).startswith('heuristic') and r.get('status') in {'OK','TIMEOUT','ERROR'}:
            seeds[(r.get('suite'),r.get('instance_id'),r.get('algorithm'))].add(r.get('seed'))
    too_few=[k for k,v in seeds.items() if len({x for x in v if x is not None}) < 3]
    if too_few:
        problems.append(f'{len(too_few)} randomized benchmark/algorithm combinations contain fewer than 3 distinct seeds')

    if problems:
        print('CP4 result validation: FAIL')
        for p in problems: print(' -',p)
        return 1
    print('CP4 result validation: PASS')
    print(f'Rows: {len(rows)}; suites: {", ".join(sorted(suites))}')
    return 0
if __name__=='__main__': raise SystemExit(main())
