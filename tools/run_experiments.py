#!/usr/bin/env python3
"""Run course-provided Beyond Brute Force benchmark suites.

Students run this tool; they do not edit it. Results are written to experiments/.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, subprocess, sys, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from course.problems import canonical_problem_id
WORKER=ROOT/'tools/experiment_framework/worker.py'


def assigned_problem():
    p=ROOT/'project.json'
    if not p.exists(): return None
    try: return json.loads(p.read_text()).get('assigned_problem') or None
    except Exception: return None


def run_worker(problem,instance,mode,timeout,algorithm=None,seed=None):
    cmd=[sys.executable,str(WORKER),'--repo-root',str(ROOT),'--problem',problem,'--instance',str(instance),'--mode',mode]
    if algorithm: cmd += ['--algorithm',algorithm]
    if seed is not None: cmd += ['--seed',str(seed)]
    start=time.perf_counter()
    try:
        cp=subprocess.run(cmd,text=True,capture_output=True,timeout=timeout)
    except subprocess.TimeoutExpired:
        return {'status':'TIMEOUT','wall_time':time.perf_counter()-start}
    lines=[x for x in cp.stdout.splitlines() if x.strip()]
    if not lines: return {'status':'ERROR','error':cp.stderr.strip() or 'worker produced no JSON','wall_time':time.perf_counter()-start}
    try: data=json.loads(lines[-1])
    except Exception: return {'status':'ERROR','error':'worker output was not valid JSON','raw_stdout':cp.stdout[-1000:],'wall_time':time.perf_counter()-start}
    data['wall_time_parent']=time.perf_counter()-start
    return data


def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''): h.update(chunk)
    return h.hexdigest()


def reference_for(item):
    if item.get('known_optimum') is not None:
        return 'optimal', item['known_optimum']
    if item.get('best_known') is not None:
        return 'best_known', item['best_known']
    return 'unknown', None


def gap_percent(objective, reference, objective_kind):
    if objective is None or reference in (None,0): return None
    if objective_kind == 'minimize':
        return 100.0*(objective-reference)/reference
    return 100.0*(reference-objective)/reference


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--suite',help='benchmark suite name')
    ap.add_argument('--all',action='store_true')
    ap.add_argument('--problem',help='override project.json assigned_problem')
    ap.add_argument('--list-suites',action='store_true')
    ap.add_argument('--output-dir',default='experiments')
    ap.add_argument('--manifest',help='use an alternate benchmark manifest')
    timeout_group=ap.add_mutually_exclusive_group()
    timeout_group.add_argument('--timeout',type=float,help='override every manifest timeout for this local run')
    timeout_group.add_argument('--timeout-scale',type=float,help='multiply each manifest timeout by this factor for this local run')
    a=ap.parse_args(); problem=a.problem or assigned_problem()
    if problem: problem=canonical_problem_id(problem)
    if not problem: ap.error('no problem selected; set assigned_problem in project.json or pass --problem')
    manifest_path=(ROOT/a.manifest).resolve() if a.manifest else ROOT/'benchmarks'/problem/'manifest.json'
    if not manifest_path.exists(): ap.error(f'no benchmark manifest for {problem}: {manifest_path}')
    manifest=json.loads(manifest_path.read_text()); suites=manifest['suites']
    if a.list_suites:
        print('\n'.join(suites)); return 0
    selected=list(suites) if a.all else [a.suite or 'readiness']
    bad=[s for s in selected if s not in suites]
    if bad: ap.error(f'unknown suite(s): {bad}; available: {list(suites)}')
    outdir=(ROOT/a.output_dir).resolve(); outdir.mkdir(parents=True,exist_ok=True)
    rows=[]; objective_kind=manifest.get('objective','minimize')
    print(f'Problem: {problem}')

    # A timed-out algorithm can be retired from later, larger instances in the
    # same frontier group.  This keeps frontier experiments from spending many
    # repeated timeouts once the practical boundary has already been crossed.
    retired:set[tuple[str,str,str]] = set()

    for suite in selected:
        print(f'\n== {suite} ==')
        for item in suites[suite]:
            instance=(manifest_path.parent/item['file']).resolve()
            if not instance.exists():
                if item.get('optional_external'):
                    print(f"{item['id']:28} MISSING  install optional external benchmark first")
                    rows.append({
                        'problem':problem,'suite':suite,'instance_id':item['id'],'instance_file':str(instance.relative_to(ROOT)),
                        'instance_sha256':None,'n':item.get('n'),'m':item.get('m'),'structure_name':item.get('structure_name'),'structure_value':item.get('structure_value'),
                        'algorithm':None,'seed':None,'repeat':None,'status':'MISSING','valid':None,'objective':None,
                        'known_optimum':item.get('known_optimum'),'best_known':item.get('best_known'),'published_lower_bound':item.get('published_lower_bound'),
                        'reference_kind':reference_for(item)[0],'reference_value':reference_for(item)[1],'gap_percent_to_reference':None,
                        'bound_kind':manifest.get('bound_kind'),'bound_value':None,'bound_valid_when_opt_known':None,
                        'wall_time':None,'student_time':None,'statistics_json':'{}','message':'optional external benchmark is not installed',
                        'source':item.get('source'),'source_url':item.get('source_url')
                    })
                    continue
                raise FileNotFoundError(f'required benchmark instance is missing: {instance}')

            timeout=float(item.get('timeout',10))
            if a.timeout is not None:
                if a.timeout <= 0: ap.error('--timeout must be > 0')
                timeout=float(a.timeout)
            elif a.timeout_scale is not None:
                if a.timeout_scale <= 0: ap.error('--timeout-scale must be > 0')
                timeout*=float(a.timeout_scale)
            known=item.get('known_optimum')
            ref_kind,ref_value=reference_for(item)
            b=run_worker(problem,instance,'bound',timeout=max(2,timeout))
            bound=b.get('bound_value') if b.get('status')=='OK' else None
            bk=manifest.get('bound_kind'); bound_valid=None
            if known is not None and bound is not None:
                bound_valid=(bound<=known) if bk=='lower' else (bound>=known)

            algorithms=item.get('algorithms',['heuristic1']); seeds=item.get('seeds',[None])
            repeats=max(1,int(item.get('repeats',1)))
            frontier_group=str(item.get('frontier_group',''))
            for alg in algorithms:
                key=(suite,frontier_group,alg)
                if frontier_group and key in retired:
                    print(f"{item['id']:28} {alg:10} SKIP    earlier timeout in frontier group {frontier_group}")
                    continue
                alg_seeds=seeds if alg.startswith('heuristic') else [None]
                timed_out=False
                for seed in alg_seeds:
                    for repeat in range(1,repeats+1):
                        r=run_worker(problem,instance,'solver',timeout,algorithm=alg,seed=seed)
                        row={
                          'problem':problem,'suite':suite,'instance_id':item['id'],'instance_file':str(instance.relative_to(ROOT)),
                          'instance_sha256':sha256(instance),'n':item.get('n'),'m':item.get('m'),'structure_name':item.get('structure_name'),'structure_value':item.get('structure_value'),
                          'algorithm':alg,'seed':seed,'repeat':repeat,'status':r.get('status'),'valid':r.get('valid'),'objective':r.get('objective'),
                          'known_optimum':known,'best_known':item.get('best_known'),'published_lower_bound':item.get('published_lower_bound'),
                          'reference_kind':ref_kind,'reference_value':ref_value,'gap_percent_to_reference':gap_percent(r.get('objective'),ref_value,objective_kind),
                          'bound_kind':bk,'bound_value':bound,'bound_valid_when_opt_known':bound_valid,'wall_time':r.get('wall_time_parent',r.get('wall_time')),
                          'student_time':(r.get('statistics') or {}).get('time') if isinstance(r.get('statistics'),dict) else None,
                          'statistics_json':json.dumps(r.get('statistics') or {},sort_keys=True),'message':r.get('validation_message') or r.get('error') or '',
                          'source':item.get('source'),'source_url':item.get('source_url')
                        }
                        rows.append(row)
                        print(f"{item['id']:28} {alg:10} seed={str(seed):>4} rep={repeat} {row['status']:7} obj={str(row['objective']):>10} ref={str(ref_value):>10} gap={str(None if row['gap_percent_to_reference'] is None else round(row['gap_percent_to_reference'],4)):>8}")
                        if row['status']=='TIMEOUT':
                            timed_out=True
                            break
                    if timed_out: break
                if timed_out and frontier_group and item.get('stop_after_timeout',False):
                    retired.add(key)

    stamp=time.strftime('%Y%m%d-%H%M%S')
    json_path=outdir/f'results-{problem}-{stamp}.json'; csv_path=outdir/f'results-{problem}-{stamp}.csv'
    json_path.write_text(json.dumps({'manifest':str(manifest_path.relative_to(ROOT)),'rows':rows},indent=2)+'\n')
    fields=list(rows[0]) if rows else []
    with csv_path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    (outdir/'latest.json').write_text(json_path.read_text()); (outdir/'latest.csv').write_text(csv_path.read_text())
    def disp(path):
        try: return str(path.relative_to(ROOT))
        except ValueError: return str(path)
    print(f'\nWrote {disp(csv_path)} and {disp(json_path)}')
    return 0
if __name__=='__main__': raise SystemExit(main())
