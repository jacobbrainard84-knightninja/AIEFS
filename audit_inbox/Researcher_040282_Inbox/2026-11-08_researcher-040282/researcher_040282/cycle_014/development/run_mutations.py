"""Direct fixed candidate mutations only. No packet/security verifier claim."""
from pathlib import Path
import os,subprocess,concurrent.futures,json,datetime,time,re
here=Path(__file__).resolve().parents[1];cache=Path.home()/'.cache/researcher040282-cycle014';base=cache/'compile';bins=cache/'lean-4.33.1-linux/bin';ml=cache/'mathlib4';out=here/'development/mutations';out.mkdir(exist_ok=False)
env=dict(os.environ,PATH=str(bins)+os.pathsep+os.environ['PATH'],XDG_CACHE_HOME=str(cache/'xdg'),MATHLIB_CACHE_DIR=str(cache/'mathlib-downloads'),LAKE_HOME=str(cache/'lake-home'),ELAN_HOME=str(cache/'elan-home'))
paths=subprocess.check_output([str(bins/'lake'),'env','printenv','LEAN_PATH'],cwd=ml,env=env,text=True,timeout=60).strip();source=(here/'TrajectoryInvariants.lean').read_text()
old=': Weights V := stepM p D B'
cases=[('stale_weights',old,': Weights V := B','dirty_not_structural_and_dirty_start_repaired'),
 ('omit_clipping',old,': Weights V := Counterfactual.noClip p D B','noClip_negative'),
 ('omit_symmetrisation',old,': Weights V := Counterfactual.noSym p D B','noSym_asymmetric'),
 ('keep_diagonal',old,': Weights V := Counterfactual.noDiag p D B','noDiag_nonzero'),
 ('bypass_gate',old,': Weights V := Counterfactual.noGate p D B','noGate_over_capacity'),
 ('next_capacity_clock','Capacity.rowS (weightsTrace p F U initial (n + 1)) i ≤ (p n).cap','Capacity.rowS (weightsTrace p F U initial (n + 1)) i ≤ (p (n + 1)).cap','capacity_clock_refuted'),
 ('drop_initial_invariant','(hInit : Structural initial.2)','(hInit : True)','initial_time_refuted'),
 ('capacity_without_link','¬ Capacity.rowS (weightUpdate Capacity.pB (X 75) zeroB) 0 ≤ Capacity.pB.cap','Capacity.rowS (weightUpdate Capacity.pB (X 75) zeroB) 0 ≤ Capacity.pB.cap','main_Capacity.false_stepM_row_no_link')]

def run(case):
 name,find,replace,witness=case
 if find not in source:raise RuntimeError('Absent fixed target: '+name)
 text=source.replace(find,replace,1);work=cache/'mutants'/name;work.mkdir(parents=True);(work/'TrajectoryInvariants.lean').write_text(text);folder=out/name;folder.mkdir()
 (folder/'change.txt').write_text('TEMPORARY CANDIDATE ONLY; all imported main files unchanged\n'+find+'\n-> '+replace+'\n')
 e=dict(env,LEAN_PATH=str(work)+os.pathsep+str(base)+os.pathsep+paths);stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.perf_counter()
 r=subprocess.run([str(bins/'lean'),'--root='+str(work),'TrajectoryInvariants.lean'],cwd=work,env=e,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=300)
 (folder/'compiler.log').write_text(r.stdout);bad=bool(re.search(r'unknown identifier|unknown constant|unknown module|unknown namespace|unknown tactic|unexpected token|failed to synthesize|object file .* does not exist|maximum.*heartbeats|deterministic timeout',r.stdout,re.I))
 row={'mutation':name,'runtime_utc_start':stamp,'raw_compiler_returncode':r.returncode,'seconds':time.perf_counter()-t,'setup_or_name_failure':bad,'baseline_semantic_witness':witness,'first_errors':[s for s in r.stdout.splitlines() if 'error:' in s][:5]}
 (folder/'observation.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row),flush=True)
 if r.returncode==0 or bad:raise RuntimeError('Survived or blocked by setup/names: '+name)
 return row

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(run,cases))
(out/'observations.json').write_text(json.dumps({'scope':'Eight fixed implementation/statement mutations, direct compiler observations and separately compiled baseline counterexamples; not a general Lean verifier','rows':rows},indent=2)+'\n')
