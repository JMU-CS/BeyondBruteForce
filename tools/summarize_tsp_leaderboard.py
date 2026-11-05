#!/usr/bin/env python3
"""Summarize TSP leaderboard/reach results produced by run_experiments.py.

The summary intentionally aggregates randomized runs by instance before combining
instances, so one instance with many successful trials cannot dominate the score.
For known-optimum suites the reference is OPT.  For open reach instances the
reference is explicitly the published best-known tour, never an optimum.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path


def load_rows(path: Path):
    if path.suffix.lower()=='.json':
        obj=json.loads(path.read_text())
        return obj['rows'] if isinstance(obj,dict) and 'rows' in obj else obj
    with path.open(newline='',encoding='utf-8') as f:
        return list(csv.DictReader(f))


def num(x):
    if x in (None,'','None'): return None
    return float(x)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('results',type=Path,help='CSV or JSON output from tools/run_experiments.py')
    ap.add_argument('--suite',default='leaderboard_known',help='suite to summarize (default: leaderboard_known)')
    a=ap.parse_args()
    rows=[r for r in load_rows(a.results) if r.get('suite')==a.suite and r.get('algorithm') and str(r.get('status'))=='OK' and str(r.get('valid')).lower() in ('true','1')]
    if not rows:
        raise SystemExit(f'no successful valid rows found for suite {a.suite!r}')

    by_instance=defaultdict(list)
    for r in rows:
        gap=num(r.get('gap_percent_to_reference'))
        obj=num(r.get('objective'))
        wall=num(r.get('wall_time'))
        if gap is not None:
            by_instance[r['instance_id']].append((gap,obj,wall,r))

    summaries=[]
    for iid,vals in sorted(by_instance.items()):
        gaps=[v[0] for v in vals]
        objs=[v[1] for v in vals if v[1] is not None]
        times=[v[2] for v in vals if v[2] is not None]
        r=vals[0][3]
        summaries.append({
            'instance':iid,
            'reference_kind':r.get('reference_kind'),
            'reference_value':num(r.get('reference_value')),
            'trials':len(vals),
            'median_gap_percent':statistics.median(gaps),
            'best_gap_percent':min(gaps),
            'worst_gap_percent':max(gaps),
            'best_objective':min(objs) if objs else None,
            'median_runtime':statistics.median(times) if times else None,
        })

    overall=statistics.mean(x['median_gap_percent'] for x in summaries)
    print(f'TSP leaderboard summary: {a.suite}')
    print(f'Overall score (mean of per-instance median gaps): {overall:.6f}%  [lower is better]')
    print()
    hdr=f"{'instance':20} {'reference':>12} {'trials':>6} {'median gap':>12} {'best gap':>11} {'worst gap':>11} {'median s':>10}"
    print(hdr); print('-'*len(hdr))
    for x in summaries:
        ref=f"{x['reference_kind']}={x['reference_value']:g}" if x['reference_value'] is not None else str(x['reference_kind'])
        medt='-' if x['median_runtime'] is None else f"{x['median_runtime']:.4f}"
        print(f"{x['instance']:20} {ref:>12} {x['trials']:6d} {x['median_gap_percent']:11.5f}% {x['best_gap_percent']:10.5f}% {x['worst_gap_percent']:10.5f}% {medt:>10}")
    print('\nScoring rule: each instance contributes its median percent gap across fixed seeds; the overall score is the unweighted mean of those instance medians.')
    if any(x['reference_kind']=='best_known' for x in summaries):
        print('Open-instance gaps are to the published best-known tour, not to a proven optimum.')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
