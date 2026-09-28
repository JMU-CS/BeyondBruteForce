#!/usr/bin/env python3
"""Install optional public benchmark packs used by Beyond Brute Force.

Core checkpoint work does not require network access. This tool installs
optional/leaderboard instances from established public benchmark collections.
"""
from __future__ import annotations

import argparse, bz2, gzip, hashlib, io, json, shutil, tarfile, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def download(url: str) -> bytes:
    print('Downloading',url)
    req=urllib.request.Request(url,headers={'User-Agent':'JMU-CS412-Beyond-Brute-Force/1.0'})
    with urllib.request.urlopen(req,timeout=90) as r:
        return r.read()


def install_pace():
    url='https://pacechallenge.org/files/pace2019-vc-exact-public-v2.tar.bz2'
    expected='e7ca305528a0257235a95c41742f2b3431e1e485'
    data=download(url); got=hashlib.sha1(data).hexdigest()
    if got!=expected: raise RuntimeError(f'PACE archive SHA1 mismatch: {got}')
    out=ROOT/'benchmarks/minimum_vertex_cover/external/pace2019'; inst=out/'instances'; inst.mkdir(parents=True,exist_ok=True)
    wanted={'001','051','101','151','199'}; rows=[]
    with tarfile.open(fileobj=io.BytesIO(data),mode='r:bz2') as tf:
        members={Path(m.name).name:m for m in tf.getmembers() if m.isfile()}
        for idx in sorted(wanted):
            candidates=[n for n in members if f'_{idx}.' in n]
            if not candidates: print('warning: could not find PACE',idx); continue
            raw=tf.extractfile(members[candidates[0]]).read().decode('utf-8')
            n=None; edges=set(); loop=False
            for line in raw.splitlines():
                line=line.strip()
                if not line or line.startswith('c'): continue
                if line.startswith('p'):
                    parts=line.split(); n=int(parts[-2]); continue
                u,v=map(int,line.split()[:2]); u-=1; v-=1
                if u==v: loop=True; break
                edges.add((min(u,v),max(u,v)))
            if loop or n is None:
                print('warning: skipping PACE',idx,'because it has a loop or malformed header'); continue
            dest=inst/f'pace_vc_{idx}.txt'; ed=sorted(edges)
            dest.write_text(f'{n} {len(ed)}\n'+''.join(f'{u} {v}\n' for u,v in ed))
            rows.append({'id':f'pace_vc_{idx}','file':f'instances/{dest.name}','n':n,'m':len(ed),'known_optimum':None,'algorithms':['heuristic1'],'timeout':20,'seeds':[11,29,47],'source':'PACE 2019 Vertex Cover Exact'})
    manifest={'schema_version':1,'problem':'minimum_vertex_cover','objective':'minimize','bound_kind':'lower','suites':{'pace2019':rows},'source_url':'https://pacechallenge.org/2019/vc/vc_exact/','source_archive_sha1':expected}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n'); print('Installed',len(rows),'PACE instances')


def install_tsplib_classic():
    """Install a small classic TSPLIB pack without expanding O(n^2) edges."""
    names={'eil51':426,'berlin52':7542,'kroA100':21282,'a280':2579,'pr1002':259045,'pcb3038':137694}
    out=ROOT/'benchmarks/traveling_salesperson/external/tsplib'; inst=out/'instances'; inst.mkdir(parents=True,exist_ok=True); rows=[]
    base='https://softlib.rice.edu/pub/tsplib/tsp/'
    for name,opt in names.items():
        raw=gzip.decompress(download(base+name+'.tsp.gz'))
        dest=inst/f'{name}.tsp'; dest.write_bytes(raw)
        rows.append({'id':name,'file':f'instances/{dest.name}','n':None,'m':None,'known_optimum':opt,'algorithms':['heuristic1'],'timeout':30,'seeds':[11,29,47,71,101],'source':'TSPLIB95'})
    manifest={'schema_version':2,'problem':'traveling_salesperson','objective':'minimize','bound_kind':'lower','suites':{'tsplib':rows},'source_url':'https://softlib.rice.edu/pub/tsplib/tsp/','optimum_source':'https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/TSP-BEST.html'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n'); print('Installed',len(rows),'classic TSPLIB instances')


def install_waterloo_tsp(suites: list[str] | None = None):
    """Install optional National TSP leaderboard/reach instances in place."""
    manifest_path=ROOT/'benchmarks/traveling_salesperson/manifest.json'
    manifest=json.loads(manifest_path.read_text())
    chosen=suites or ['leaderboard_known']
    dest_dir=manifest_path.parent/'external'; dest_dir.mkdir(parents=True,exist_ok=True)
    count=0
    for suite in chosen:
        if suite not in ('leaderboard_known','reach_known','reach_open'):
            raise ValueError(f'not a Waterloo TSP suite: {suite}')
        print(f'\n== {suite} ==')
        for item in manifest['suites'][suite]:
            target=manifest_path.parent/item['file']
            raw=download(item['source_url'])
            target.write_bytes(raw)
            print('Wrote',target.relative_to(ROOT),f'({len(raw):,} bytes)')
            count+=1
    print('Installed',count,'Waterloo National TSP instances')


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('source',choices=['pace2019-vc','tsplib','waterloo-tsp','all'])
    ap.add_argument('--suite',action='append',choices=['leaderboard_known','reach_known','reach_open'],help='Waterloo TSP suite to install; may be repeated')
    a=ap.parse_args()
    if a.source in ('pace2019-vc','all'): install_pace()
    if a.source in ('tsplib','all'): install_tsplib_classic()
    if a.source in ('waterloo-tsp','all'): install_waterloo_tsp(a.suite)


if __name__=='__main__': main()
