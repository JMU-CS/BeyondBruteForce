#!/usr/bin/env python3
"""Generate deterministic Minimum Graph Coloring course benchmarks.

Every generated family has a chromatic number known by construction. Planted
k-colorable graphs contain an explicit K_k while all other edges run between
known color classes, proving chi(G)=k without an offline exact solver.
"""
from __future__ import annotations
import json, random
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BENCH=ROOT/'benchmarks'/'minimum_graph_coloring'
INST=BENCH/'instances'
SEEDS=[11,29,47,71,101]


def write_graph(path,n,edges):
    es=sorted({(min(u,v),max(u,v)) for u,v in edges if u!=v})
    path.write_text(f"{n} {len(es)}\n"+''.join(f"{u} {v}\n" for u,v in es),encoding='utf-8')
    return len(es)


def relabel(n,edges,seed):
    rng=random.Random(seed); p=list(range(n)); rng.shuffle(p)
    return [(p[u],p[v]) for u,v in edges]


def complete(n): return [(u,v) for u in range(n) for v in range(u+1,n)]
def cycle(n): return [(i,(i+1)%n) for i in range(n)]

def complete_multipartite(parts):
    cls=[]
    for i,s in enumerate(parts): cls += [i]*s
    n=len(cls)
    return [(u,v) for u in range(n) for v in range(u+1,n) if cls[u]!=cls[v]]


def planted(n,k,seed,p=None,target_degree=None):
    rng=random.Random(seed)
    cls=list(range(k))+[rng.randrange(k) for _ in range(k,n)]
    edges={(u,v) for u in range(k) for v in range(u+1,k)}
    if p is not None:
        for u in range(n):
            for v in range(u+1,n):
                if cls[u]!=cls[v] and rng.random()<p: edges.add((u,v))
    if target_degree is not None:
        by=[[] for _ in range(k)]
        for v,c in enumerate(cls): by[c].append(v)
        for u in range(n):
            candidates=[v for c in range(k) if c!=cls[u] for v in by[c]]
            for v in rng.sample(candidates,min(target_degree,len(candidates))):
                edges.add((min(u,v),max(u,v)))
    return relabel(n,list(edges),seed+777777)


def add(suites,suite,*,item_id,filename,n,m,opt,algorithms,timeout,seeds=None,structure_name=None,structure_value=None,frontier_group=None,stop=False):
    x={'id':item_id,'file':f'instances/{filename}','n':n,'m':m,'known_optimum':opt,'algorithms':algorithms,'timeout':timeout}
    if seeds is not None: x['seeds']=seeds
    if structure_name is not None: x['structure_name']=structure_name; x['structure_value']=structure_value
    if frontier_group is not None: x['frontier_group']=frontier_group
    if stop: x['stop_after_timeout']=True
    suites.setdefault(suite,[]).append(x)


def main():
    INST.mkdir(parents=True,exist_ok=True)
    for f in INST.glob('*.txt'): f.unlink()
    suites={}

    # readiness
    specs=[('ready_c5','ready_c5.txt',5,cycle(5),3,'odd_cycle'),('ready_k5','ready_k5.txt',5,complete(5),5,'complete'),('ready_3part','ready_3part.txt',9,complete_multipartite([3,3,3]),3,'complete_multipartite')]
    for iid,fn,n,e,opt,fam in specs:
        m=write_graph(INST/fn,n,e); add(suites,'readiness',item_id=iid,filename=fn,n=n,m=m,opt=opt,algorithms=['exhaustive'],timeout=15,structure_name='graph_family',structure_value=fam)

    # exact frontier 1: odd cycles; chi=3
    for n in (7,9,11,13,15,17):
        e=relabel(n,cycle(n),1000+n); fn=f'frontier_odd_cycle_{n}.txt'; m=write_graph(INST/fn,n,e)
        add(suites,'exact_frontier',item_id=f'odd_cycle_{n}',filename=fn,n=n,m=m,opt=3,algorithms=['exhaustive','improved'],timeout=900,structure_name='graph_family',structure_value='odd_cycle',frontier_group='odd_cycle',stop=True)

    # exact frontier 2: complete graphs; chi=n
    for n in (4,5,6,7,8):
        e=relabel(n,complete(n),2000+n); fn=f'frontier_complete_{n}.txt'; m=write_graph(INST/fn,n,e)
        add(suites,'exact_frontier',item_id=f'complete_{n}',filename=fn,n=n,m=m,opt=n,algorithms=['exhaustive','improved'],timeout=900,structure_name='graph_family',structure_value='complete_graph',frontier_group='complete_graph',stop=True)

    # exact frontier 3: planted 4-color graphs; chi=4
    for n in (7,9,11,13,15):
        e=planted(n,4,3000+n,p=.35); fn=f'frontier_planted4_n{n}.txt'; m=write_graph(INST/fn,n,e)
        add(suites,'exact_frontier',item_id=f'planted4_n{n}',filename=fn,n=n,m=m,opt=4,algorithms=['exhaustive','improved'],timeout=900,structure_name='graph_family',structure_value='planted_four_color',frontier_group='planted_four_color',stop=True)

    # quality known
    for n,k,p,seed in ((120,6,.08,4101),(200,8,.10,4102),(300,10,.06,4103)):
        e=planted(n,k,seed,p=p); fn=f'quality_planted{k}_n{n}.txt'; m=write_graph(INST/fn,n,e)
        add(suites,'quality_known',item_id=f'quality_planted{k}_n{n}',filename=fn,n=n,m=m,opt=k,algorithms=['heuristic1'],timeout=60,seeds=SEEDS,structure_name='graph_family',structure_value='planted_k_colorable')

    # scale
    for n,k,d,seed in ((500,10,10,5101),(2000,15,12,5102),(5000,20,15,5103)):
        e=planted(n,k,seed,target_degree=d); fn=f'scale_planted{k}_n{n}.txt'; m=write_graph(INST/fn,n,e)
        add(suites,'heuristic_scale',item_id=f'scale_planted{k}_n{n}',filename=fn,n=n,m=m,opt=k,algorithms=['heuristic1'],timeout=60,seeds=SEEDS,structure_name='graph_family',structure_value='sparse_planted_k_colorable')

    # structure: n=300 and chi=8 fixed; vary only cross-class edge probability.
    for label,p in [('sparse',.03),('medium',.12),('dense',.35)]:
        for rep in range(1,4):
            seed=6100+{'sparse':0,'medium':100,'dense':200}[label]+rep
            e=planted(300,8,seed,p=p); fn=f'structure_{label}_r{rep}.txt'; m=write_graph(INST/fn,300,e)
            density=2.0*m/(300*299)
            add(suites,'structure',item_id=f'{label}_r{rep}',filename=fn,n=300,m=m,opt=8,algorithms=['heuristic1'],timeout=60,seeds=SEEDS,structure_name='edge_density',structure_value=round(density,6))

    manifest={'schema_version':1,'problem':'minimum_graph_coloring','objective':'minimize','bound_kind':'lower','description':'Course-provided Minimum Graph Coloring Checkpoint 1 readiness and Final Project experiment suites.','suites':suites}
    (BENCH/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(f"Wrote {sum(len(v) for v in suites.values())} manifest entries to {BENCH}")

if __name__=='__main__': main()
