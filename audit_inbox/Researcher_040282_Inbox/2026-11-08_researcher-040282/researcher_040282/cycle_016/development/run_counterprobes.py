"""Exact fixed value/false-claim probes on the approved unmerged P5 API.
No generic verifier, main integration or coupled016probe claim."""
from pathlib import Path
import os,subprocess,concurrent.futures,json,datetime,time,re
here=Path(__file__).resolve().parents[1];cache=Path.home()/'.cache/researcher040282-cycle016';base=cache/'compile';bins=cache/'lean-4.33.1-linux/bin';ml=cache/'mathlib4';out=here/'development/counterprobes';out.mkdir(exist_ok=False)
env=dict(os.environ,PATH=str(bins)+os.pathsep+os.environ['PATH'],XDG_CACHE_HOME=str(cache/'xdg'),MATHLIB_CACHE_DIR=str(cache/'mathlib-downloads'),LAKE_HOME=str(cache/'lake-home'),ELAN_HOME=str(cache/'elan-home'));paths=subprocess.check_output([str(bins/'lake'),'env','printenv','LEAN_PATH'],cwd=ml,env=env,text=True,timeout=60).strip()
source=(here/'CoherenceMotion.lean').read_text()
prefix=source[:source.index('/-- Pure norm inequality')]+source[source.index('/-- Observable wrapper only'):source.index('theorem trace_step_bounds')]
helpers=source[source.index('section ValueProbes'):source.index('private theorem value_r0')]
helpers+=source[source.index('private theorem value_second'):source.index('theorem probe_two_step')]
helpers+=source[source.index('/-- Probe shorthand only'):source.index('theorem probe_half_drop')]
# Reference calculations state the existing P5operator at a FIXED time, not the
# observable rTrace whose clock is under test.
helpers+='''
private theorem fixed_R0 (alpha : ℝ) (c : ℂ) :
    PhaseCoherence.reported (PhaseCoherence.coherenceTrace alpha (valueC c) 1 valueX valueU valueOmega Real.pi 0) (0 : Fin 2) 1 = ‖c‖ := by
  change PhaseCoherence.reported (valueC c) (0 : Fin 2) 1 = _
  rw [PhaseCoherence.reported_offdiag _ (by decide)]
  unfold valueC
  ring
private theorem fixed_R1 (alpha : ℝ) (c : ℂ) :
    PhaseCoherence.reported (PhaseCoherence.coherenceTrace alpha (valueC c) 1 valueX valueU valueOmega Real.pi 1) (0 : Fin 2) 1 = ‖(alpha : ℂ)*c-((1-alpha : ℝ):ℂ)‖ := by
  rw [PhaseCoherence.reported_offdiag _ (by decide),value_first,value_first]
  ring
private theorem fixed_R2 :
    PhaseCoherence.reported (PhaseCoherence.coherenceTrace (3/4) (valueC 1) 1 valueX valueU valueOmega Real.pi 2) (0 : Fin 2) 1 = 1/8 := by
  rw [PhaseCoherence.reported_offdiag _ (by decide),value_second,value_second]
  norm_num [Complex.norm_def,Complex.normSq]
'''
settings='\nset_option linter.unusedSimpArgs false\n';end='\nend ValueProbes\nend\nend AIEFGate.CoherenceMotion\n'
normal='Rval,rTrace,fixed_R0,fixed_R1,fixed_R2,Complex.norm_def,Complex.normSq'
positives=['Rval (1/2) 1 0 = 1','Rval (1/2) 1 1 = 0','Rval (1/2) 0 1 = 1/2','Rval (-1) 1 1 = 3','Rval 2 0 1 = 1','Rval (1/2) 3 0 = 3 ∧ Rval (1/2) 3 1 = 1','Rval (3/4) 1 2 = 1/8']
cases=[('factor_two_dropped','|Rval (1/2) 1 1-Rval (1/2) 1 0| ≤ 1-(1/2 : ℝ)',None,None,'factor_one_refuted'),
 ('increase_envelope_for_abs','|Rval (1/2) 1 1-Rval (1/2) 1 0| ≤ (1-(1/2 : ℝ))*(1-Rval (1/2) 1 0)',None,None,'increase_only_abs_refuted'),
 ('negative_alpha_allowed','Rval (-1) 1 1 ≤ (-1 : ℝ)*Rval (-1) 1 0 + (1-(-1 : ℝ))',None,None,'negative_alpha_upper_refuted'),
 ('alpha_gt_one_allowed','Rval 2 0 1 ≤ (2 : ℝ)*Rval 2 0 0 + (1-(2 : ℝ))',None,None,'alpha_gt_one_upper_refuted'),
 ('unitdisk_initial_omitted','|Rval (1/2) 3 1-Rval (1/2) 3 0| ≤ 2*(1-(1/2 : ℝ))',None,None,'nonunit_initial_refuted'),
 ('two_steps_one_allowance','|Rval (3/4) 1 2-Rval (3/4) 1 0| ≤ 2*(1-(3/4 : ℝ))',None,None,'two_step_one_allowance_refuted'),
 ('observable_shifted','Rval (1/2) 1 0 = 1','omega tau n) i j','omega tau (n+1)) i j','probe_half_drop')]

def compile_text(name,text):
 work=cache/'counterprobes'/name;work.mkdir(parents=True);(work/'Probe.lean').write_text(text);folder=out/name;folder.mkdir();(folder/'probe.lean').write_text(text)
 e=dict(env,LEAN_PATH=str(work)+os.pathsep+str(base)+os.pathsep+paths);stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.perf_counter()
 r=subprocess.run([str(bins/'lean'),'--root='+str(work),'Probe.lean'],cwd=work,env=e,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=240)
 (folder/'compiler.log').write_text(r.stdout);return r,stamp,time.perf_counter()-t
positive=prefix+helpers+settings
for i,prop in enumerate(positives):positive+='\ntheorem positive'+str(i)+' : '+prop+' := by\n  norm_num ['+normal+']\n'
positive+=end
r,stamp,seconds=compile_text('positive_baselines',positive);print(json.dumps({'positive_baselines':7,'returncode':r.returncode,'runtime_utc_start':stamp,'seconds':seconds}),flush=True)
if r.returncode:print(r.stdout,flush=True);raise RuntimeError('Positive exact baseline blocked')

def run(case):
 name,prop,find,replace,witness=case;actualprefix=prefix
 if find:
  if find not in actualprefix:raise RuntimeError('Clock target not found')
  actualprefix=actualprefix.replace(find,replace,1)
 text=actualprefix+helpers+settings+'\nexample : '+prop+' := by\n  norm_num ['+normal+']\n'+end
 r,stamp,seconds=compile_text(name,text);bad=bool(re.search(r'unknown identifier|unknown constant|unknown module|unknown namespace|unknown tactic|unexpected token|failed to synthesize|object file .* does not exist|maximum.*heartbeats|deterministic timeout',r.stdout,re.I));explicit=bool(re.search(r'⊢\s*False',r.stdout))
 row={'case':name,'runtime_utc_start':stamp,'raw_compiler_returncode':r.returncode,'seconds':seconds,'setup_name_or_timeout_failure':bad,'explicit_false_goal':explicit,'baseline_semantic_witness':witness,'first_errors':[s for s in r.stdout.splitlines() if 'error:' in s][:3]};(out/name/'observation.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row),flush=True)
 if r.returncode==0 or bad or not explicit:raise RuntimeError('Not explicit false mathematics: '+name)
 return row
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(run,cases))
# Legitimate observable +0 equivalence, evaluated by the same independent values.
find='PhaseCoherence.reported (PhaseCoherence.coherenceTrace alpha C0 d x0 u omega tau n) i j'
if find not in positive:raise RuntimeError('Equivalence target absent')
equivalent=positive.replace(find,'('+find+') + 0',1)
r,stamp,seconds=compile_text('equivalence_plus_zero',equivalent);equiv={'runtime_utc_start':stamp,'returncode':r.returncode,'seconds':seconds,'meaning':'Legitimate +0observable equivalence, seven fixed values held'};print(json.dumps(equiv),flush=True)
if r.returncode:print(r.stdout,flush=True);raise RuntimeError('Legitimate equivalence rejected')
(out/'observations.json').write_text(json.dumps({'basis':'UNMERGEDteamP5@54037ea,userapprovedbranchcomponentonly','positive_baselines':7,'positive_returncode':0,'rows':rows,'equivalence_control':equiv,'scope':'Fixed exact value/false-claim probes, not a generic verifier or coupledmodel015test'},indent=2)+'\n')
