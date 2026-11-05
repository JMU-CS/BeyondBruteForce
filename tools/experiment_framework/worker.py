"""Subprocess worker used by run_experiments.py.

This file is course infrastructure. It isolates student code so the parent can
apply a wall-clock timeout to each algorithm or bound invocation.
"""
from __future__ import annotations
import argparse, json, sys, time, traceback
from argparse import Namespace
from pathlib import Path


def _mvc_validate(graph, solution):
    try:
        vertices=solution["vertices"]; size=solution["size"]
        if not isinstance(vertices,list) or not all(isinstance(v,int) for v in vertices): return False,None,"vertices must be a list of ints"
        if len(vertices)!=len(set(vertices)) or size!=len(vertices): return False,None,"size/vertices mismatch or duplicate vertex"
        s=set(vertices)
        if any(v<0 or v>=graph.num_vertices for v in s): return False,None,"out-of-range vertex"
        if not all(u in s or v in s for u,v in graph.edges): return False,None,"returned set is not a vertex cover"
        return True,size,None
    except Exception as exc: return False,None,str(exc)


def _tsp_validate(graph, solution):
    try:
        tour=solution["tour"]; reported=solution["cost"]; n=graph.num_vertices
        if not isinstance(tour,list) or len(tour)!=n+1 or tour[0]!=tour[-1]: return False,None,"tour must contain n+1 vertices and return to its start"
        body=tour[:-1]
        if len(set(body))!=n or set(body)!=set(range(n)): return False,None,"tour must visit every vertex exactly once"
        cost=sum(graph.weight(tour[i],tour[i+1]) for i in range(n))
        if reported!=cost: return False,None,f"reported cost {reported} != computed cost {cost}"
        return True,cost,None
    except Exception as exc: return False,None,str(exc)


def _lp_validate(graph, solution):
    try:
        vertices=solution["vertices"]; reported=solution["length"]
        if not isinstance(vertices,list) or not vertices:
            return False,None,"vertices must be a nonempty list"
        if not all(isinstance(v,int) and not isinstance(v,bool) for v in vertices):
            return False,None,"vertices must be a list of ints"
        if len(vertices)!=len(set(vertices)):
            return False,None,"path repeats a vertex"
        if any(v<0 or v>=graph.num_vertices for v in vertices):
            return False,None,"path contains an out-of-range vertex"
        if any(not graph.has_edge(vertices[i],vertices[i+1]) for i in range(len(vertices)-1)):
            return False,None,"consecutive vertices are not joined by an edge"
        length=len(vertices)-1
        if reported!=length:
            return False,None,f"reported length {reported} != computed length {length}"
        return True,length,None
    except Exception as exc: return False,None,str(exc)


def _mc_validate(graph, solution):
    try:
        vertices=solution["vertices"]; reported=solution["size"]
        if not isinstance(vertices,list): return False,None,"vertices must be a list"
        if not all(isinstance(v,int) and not isinstance(v,bool) for v in vertices): return False,None,"vertices must be a list of ints"
        if len(vertices)!=len(set(vertices)): return False,None,"clique repeats a vertex"
        if any(v<0 or v>=graph.num_vertices for v in vertices): return False,None,"clique contains an out-of-range vertex"
        if reported!=len(vertices): return False,None,f"reported size {reported} != number of vertices {len(vertices)}"
        for i,u in enumerate(vertices):
            for v in vertices[i+1:]:
                if not graph.has_edge(u,v): return False,None,f"({u}, {v}) is not an edge"
        return True,reported,None
    except Exception as exc: return False,None,str(exc)


def _mgc_validate(graph, solution):
    try:
        colors=solution["colors"]; reported=solution["num_colors"]; n=graph.num_vertices
        if not isinstance(colors,list) or len(colors)!=n: return False,None,"colors must contain exactly one entry per vertex"
        if not all(isinstance(c,int) and not isinstance(c,bool) and c>=0 for c in colors): return False,None,"colors must be non-negative ints"
        distinct=set(colors)
        if reported!=len(distinct): return False,None,f"reported num_colors {reported} != distinct color count {len(distinct)}"
        if reported>0 and distinct!=set(range(reported)): return False,None,"solver output colors must be normalized to 0..num_colors-1"
        for u,v in graph.edges:
            if colors[u]==colors[v]: return False,None,f"edge ({u}, {v}) has equal endpoint colors"
        return True,reported,None
    except Exception as exc: return False,None,str(exc)

VALIDATORS={"minimum_vertex_cover":_mvc_validate,"traveling_salesperson":_tsp_validate,"longest_path":_lp_validate,"maximum_clique":_mc_validate,"minimum_graph_coloring":_mgc_validate}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo-root',required=True); ap.add_argument('--problem',required=True); ap.add_argument('--instance',required=True)
    ap.add_argument('--mode',choices=['solver','bound'],required=True); ap.add_argument('--algorithm'); ap.add_argument('--seed',type=int)
    a=ap.parse_args()
    root=Path(a.repo_root).resolve(); sys.path.insert(0,str(root/'src'))
    try:
        from course.problems import get_problem
        problem=get_problem(a.problem)
        instance=problem.read_instance(a.instance, Namespace(seed=a.seed))
        start=time.perf_counter()
        if a.mode=='bound':
            value=problem.get_bound()(instance); elapsed=time.perf_counter()-start
            if not isinstance(value,(int,float)) or isinstance(value,bool): raise TypeError('bound must return int or float')
            payload={'status':'OK','bound_value':value,'wall_time':elapsed}
        else:
            solver=problem.get_solver(a.algorithm); solution,statistics=solver(instance,Namespace(seed=a.seed)); elapsed=time.perf_counter()-start
            validator=VALIDATORS.get(a.problem)
            if validator is None: raise NotImplementedError(f'experiment validator not yet implemented for {a.problem}')
            valid,obj,msg=validator(instance,solution)
            payload={'status':'OK','solution':solution,'statistics':statistics,'valid':valid,'objective':obj,'validation_message':msg,'wall_time':elapsed}
        print(json.dumps(payload,separators=(',',':')))
    except Exception as exc:
        print(json.dumps({'status':'ERROR','error':f'{type(exc).__name__}: {exc}','traceback':traceback.format_exc(limit=5)}))
        return 1
    return 0
if __name__=='__main__': raise SystemExit(main())
