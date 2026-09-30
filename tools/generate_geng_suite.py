#!/usr/bin/env python3
"""Materialize an optional non-isomorphic graph suite using nauty/geng."""
from __future__ import annotations
import argparse, json, shutil, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def find_geng():
    for name in ('geng','nauty-geng'):
        p=shutil.which(name)
        if p: return p
    return None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--n',type=int,required=True); ap.add_argument('--edges',help='geng edge range, e.g. 10:18')
    ap.add_argument('--connected',action='store_true'); ap.add_argument('--limit',type=int,default=250)
    ap.add_argument('--problem',default='minimum_vertex_cover'); ap.add_argument('--name',default=None)
    a=ap.parse_args(); exe=find_geng()
    if not exe:
        raise SystemExit('geng not found. macOS: brew install nauty. Ubuntu: sudo apt install nauty (binary is usually nauty-geng).')
    cmd=[exe,'-q'] + (['-c'] if a.connected else []) + [str(a.n)] + ([a.edges] if a.edges else [])
    cp=subprocess.Popen(cmd,stdout=subprocess.PIPE,text=True)
    suite=a.name or f'geng_n{a.n}'; out=ROOT/'benchmarks'/a.problem/'external/geng'/suite; inst=out/'instances'; inst.mkdir(parents=True,exist_ok=True)
    rows=[]
    for i,line in enumerate(cp.stdout):
        if i>=a.limit: break
        line=line.strip()
        if not line: continue
        f=inst/f'g{i:04d}.g6'; f.write_text(line+'\n')
        rows.append({'id':f'{suite}_g{i:04d}','file':f'instances/{f.name}','n':a.n,'m':None,'known_optimum':None,'algorithms':['heuristic1'],'timeout':5,'seeds':[11,29,47],'structure_name':'nonisomorphic_graph','structure_value':suite})
    cp.kill(); cp.wait()
    manifest={'schema_version':1,'problem':a.problem,'objective':'minimize' if a.problem in ('minimum_vertex_cover','minimum_graph_coloring') else 'maximize','bound_kind':'lower' if a.problem in ('minimum_vertex_cover','minimum_graph_coloring') else 'upper','suites':{suite:rows},'generated_by':'geng','geng_command':cmd}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Generated {len(rows)} non-isomorphic graphs.')
    print(f'Run: python tools/run_experiments.py --problem {a.problem} --manifest {out.relative_to(ROOT)}/manifest.json --suite {suite}')
if __name__=='__main__': main()
