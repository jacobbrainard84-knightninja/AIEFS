"""Exact focused Lean counterprobes for the fixed candidate, not a general verifier.
Candidate definition prefix is unchanged; only fixed bad implementations/claims vary.
"""
from pathlib import Path
import os,subprocess,concurrent.futures,json,datetime,time,re
here=Path(__file__).resolve().parents[1];cache=Path.home()/'.cache/researcher040282-cycle014';base=cache/'compile';bins=cache/'lean-4.33.1-linux/bin';ml=cache/'mathlib4';out=here/'development/mutations';out.mkdir(exist_ok=False)
env=dict(os.environ,PATH=str(bins)+os.pathsep+os.environ['PATH'],XDG_CACHE_HOME=str(cache/'xdg'),MATHLIB_CACHE_DIR=str(cache/'mathlib-downloads'),LAKE_HOME=str(cache/'lake-home'),ELAN_HOME=str(cache/'elan-home'))
paths=subprocess.check_output([str(bins/'lake'),'env','printenv','LEAN_PATH'],cwd=ml,env=env,text=True,timeout=60).strip();source=(here/'TrajectoryInvariants.lean').read_text()
prefix=source[:source.index('theorem weightsTrace_succ')]
fixtures=source[source.index('/-- Exact-real non-production witnesses'):source.index('theorem pWide_engine')]+source[source.index('abbrev X :='):source.index('theorem dirty_not_structural')]
for name in ('capSchedule','oneDrive','keepAux'):
 fixtures+='\n'+next(line for line in source.splitlines() if line.startswith('def '+name+' '))+'\n'
normal='weightUpdate, Counterfactual.noClip, Counterfactual.noSym, Counterfactual.noDiag, Counterfactual.noGate, Structural, weightsTrace, trajectory, feedbackStep, Capacity.gateM, Capacity.GateOnX, Capacity.rowS, stepM, GateOnM, rowM, symM, clipM, preM, scale, pWide, pTight, pQuarter, capSchedule, Capacity.pB, Capacity.Xo, zeroB, onesB, dirtyB, asymDrive, Fin.sum_univ_two, Fin.exists_fin_two, Fin.forall_fin_two'
old=': Weights V := stepM p D B'
probes=[('stale_weights',old,': Weights V := B','weightUpdate pWide (X 1) dirtyB 0 0 = 0','dirty_not_structural_and_dirty_start_repaired'),
 ('omit_clipping',old,': Weights V := Counterfactual.noClip p D B','0 ≤ weightUpdate pWide (X (-1)) zeroB 0 1','noClip_negative'),
 ('omit_symmetrisation',old,': Weights V := Counterfactual.noSym p D B','weightUpdate pWide asymDrive zeroB 0 1 = weightUpdate pWide asymDrive zeroB 1 0','noSym_asymmetric'),
 ('keep_diagonal',old,': Weights V := Counterfactual.noDiag p D B','weightUpdate pWide onesB zeroB 0 0 = 0','noDiag_nonzero'),
 ('bypass_gate',old,': Weights V := Counterfactual.noGate p D B','Capacity.rowS (weightUpdate pTight (X 3) zeroB) 0 ≤ pTight.cap','noGate_over_capacity'),
 ('next_capacity_clock','(capSchedule 0).cap','(capSchedule 1).cap','Capacity.rowS (weightUpdate (capSchedule 0) (X 1) zeroB) 0 ≤ (capSchedule 0).cap','capacity_clock_refuted'),
 ('drop_initial_invariant',None,None,'Structural (weightsTrace (fun _ => pWide) oneDrive keepAux ((),dirtyB) 0)','initial_time_refuted'),
 ('capacity_without_link',None,None,'Capacity.rowS (weightUpdate Capacity.pB (X 75) zeroB) 0 ≤ Capacity.pB.cap','main_Capacity.false_stepM_row_no_link')]
end='\nend\nend AIEFGate.TrajectorySafety\n'
# Common numeric normalisation suppresses only unused simp-argument lint in probes,
# not errors/heartbeats/hole warnings; the actual candidate stays lint-clean.
settings='\nset_option linter.unusedSimpArgs false\n'
positive=prefix+fixtures+settings
for i,(_,_,_,prop,_) in enumerate(probes[:6]):positive+='\ntheorem focusedPositive'+str(i)+' : '+prop+' := by\n  norm_num ['+normal+']\n'
positive+=end

def compile_text(name,text):
 work=cache/'focused'/name;work.mkdir(parents=True);(work/'Probe.lean').write_text(text);folder=out/name;folder.mkdir();(folder/'probe.lean').write_text(text)
 e=dict(env,LEAN_PATH=str(work)+os.pathsep+str(base)+os.pathsep+paths);stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.perf_counter()
 r=subprocess.run([str(bins/'lean'),'--root='+str(work),'Probe.lean'],cwd=work,env=e,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=240)
 (folder/'compiler.log').write_text(r.stdout);return r,stamp,time.perf_counter()-t

r,stamp,seconds=compile_text('positive_baselines',positive)
print(json.dumps({'positive_baselines':6,'returncode':r.returncode,'seconds':seconds}),flush=True)
if r.returncode:print(r.stdout,flush=True);raise RuntimeError('Positive concrete baseline failed, no negative credit')

def run(case):
 name,find,replacement,prop,witness=case;text=prefix+fixtures+settings+'\nexample : '+prop+' := by\n  norm_num ['+normal+']\n'+end
 if find:
  if find not in text:raise RuntimeError('Absent target')
  text=text.replace(find,replacement,1)
 r,stamp,seconds=compile_text(name,text);bad=bool(re.search(r'unknown identifier|unknown constant|unknown module|unknown namespace|unknown tactic|unexpected token|failed to synthesize|object file .* does not exist|maximum.*heartbeats|deterministic timeout',r.stdout,re.I))
 explicit=bool(re.search(r'⊢\s*False',r.stdout));row={'mutation':name,'runtime_utc_start':stamp,'raw_compiler_returncode':r.returncode,'seconds':seconds,'setup_or_name_failure':bad,
   'explicit_false_goal':explicit,'baseline_semantic_witness':witness,'scope':'Focused exact candidate definitions; held concrete property/known-false claim','first_errors':[s for s in r.stdout.splitlines() if 'error:' in s][:3]}
 (out/name/'observation.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row),flush=True)
 if r.returncode==0 or bad or not explicit:raise RuntimeError('Not explicit false mathematics: '+name)
 return row

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(run,probes))
(out/'observations.json').write_text(json.dumps({'method':'Focused exact semantic probes; whole-file heartbeat failures separately blocked/not credited','six_positive_baselines_returncode':0,'rows':rows},indent=2)+'\n')
