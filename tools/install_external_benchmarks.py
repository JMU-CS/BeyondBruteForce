#!/usr/bin/env python3
"""Install optional public benchmark packs used by Beyond Brute Force.

Core CP4 does not require network access. This tool is for optional/extended
experiments with established public benchmark collections.
"""
from __future__ import annotations
import argparse, bz2, gzip, hashlib, io, json, math, tarfile, urllib.request, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def download(url):
    print('Downloading',url)
    with urllib.request.urlopen(url,timeout=60) as r: return r.read()

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

def nint(x): return int(math.floor(x+0.5))
def install_tsplib():
    names={'eil51':426,'berlin52':7542,'kroA100':21282,'a280':2579}
    out=ROOT/'benchmarks/traveling_salesperson/external/tsplib'; inst=out/'instances'; inst.mkdir(parents=True,exist_ok=True); rows=[]
    base='https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/'
    for name,opt in names.items():
        raw=gzip.decompress(download(base+name+'.tsp.gz')).decode('ascii','replace')
        hdr={}; coords=[]; in_coords=False
        for line in raw.splitlines():
            line=line.strip()
            if not line: continue
            if line=='NODE_COORD_SECTION': in_coords=True; continue
            if line=='EOF': break
            if in_coords:
                parts=line.split(); coords.append((float(parts[1]),float(parts[2]))); continue
            if ':' in line:
                k,v=line.split(':',1); hdr[k.strip()]=v.strip()
        if hdr.get('EDGE_WEIGHT_TYPE')!='EUC_2D': raise RuntimeError(f'{name}: only EUC_2D supported by installer')
        n=int(hdr['DIMENSION']); assert len(coords)==n
        weighted=[]
        for i in range(n):
            for j in range(i+1,n):
                dx=coords[i][0]-coords[j][0]; dy=coords[i][1]-coords[j][1]; weighted.append((i,j,nint(math.hypot(dx,dy))))
        dest=inst/f'{name}.txt'; dest.write_text(f'{n} {len(weighted)}\n'+''.join(f'{u} {v} {w}\n' for u,v,w in weighted))
        rows.append({'id':name,'file':f'instances/{dest.name}','n':n,'m':len(weighted),'known_optimum':opt,'algorithms':['heuristic1'],'timeout':20,'seeds':[11,29,47],'source':'TSPLIB95'})
    manifest={'schema_version':1,'problem':'traveling_salesperson','objective':'minimize','bound_kind':'lower','suites':{'tsplib':rows},'source_url':'https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/','optimum_source':'https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/TSP-BEST.html'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n'); print('Installed',len(rows),'TSPLIB instances')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('source',choices=['pace2019-vc','tsplib','all']); a=ap.parse_args()
    if a.source in ('pace2019-vc','all'): install_pace()
    if a.source in ('tsplib','all'): install_tsplib()
if __name__=='__main__': main()
