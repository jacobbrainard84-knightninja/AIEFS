"""Focused exact counterprobes of fixed ClosedLoopCore definitions. No generic
Lean/security verifier or packet certification claim. Imports/main stay fixed."""
from pathlib import Path
import os,subprocess,concurrent.futures,json,datetime,time,re
here=Path(__file__).resolve().parents[1];cache=Path.home()/'.cache/researcher040282-cycle015';base=cache/'compile';bins=cache/'lean-4.33.1-linux/bin';ml=cache/'mathlib4';out=here/'development/counterprobes';out.mkdir(exist_ok=False)
env=dict(os.environ,PATH=str(bins)+os.pathsep+os.environ['PATH'],XDG_CACHE_HOME=str(cache/'xdg'),MATHLIB_CACHE_DIR=str(cache/'mathlib-downloads'),LAKE_HOME=str(cache/'lake-home'),ELAN_HOME=str(cache/'elan-home'))
paths=subprocess.check_output([str(bins/'lake'),'env','printenv','LEAN_PATH'],cwd=ml,env=env,text=True,timeout=60).strip();source=(here/'ClosedLoopCore.lean').read_text()
prefix=source[:source.index('/-- Held source-order interface')]
common=source[source.index('section Probes'):source.index('theorem probe_R_matrix')]
extra=source[source.index('theorem probe_R_matrix'):source.index('theorem probe_B_new')]
wrap=source[source.index('private theorem wrap_two_thirds'):source.index('theorem probe_theta_new')]
readdefs=source[source.index('/-- Explicit current/oldest argument probe'):source.index('theorem probe_oldest_input')]+source[source.index('def offsetConfig'):source.index('theorem probe_frequency_offset')]
end='\nend Probes\nend Finite\nend\nend AIEFGate.ClosedLoop\n';settings='\nset_option linter.unusedSimpArgs false\n'
normal='usedIncrement, sourceIncrement, TrajectorySafety.sineCoupling, probeAux, initialAux, probeTheta, probeConfig, probeParams, Capacity.Xo, zeroB, Fin.sum_univ_two, probe_unprojected'
step='''  simp only [prepareDrive,drive,newR,probe_C_matrix]
  norm_num [probeConfig,probeAux,initialAux,zeroC,PhaseCoherence.reported,complexMeanWrong,Complex.norm_def,Complex.normSq]
'''
used='  norm_num ['+normal+']\n'
history='''  norm_num [updateAux,Researcher040282.Delay.shiftAppend,nextTheta,'''+normal+''',wrap_two_thirds]
'''
read='''  have he := exp_left_half
  push_cast at he
  norm_num [rawInput,probeConfig,readProbe,he,Complex.ext_iff]
'''
offset='''  have he := exp_left_neg_pi
  push_cast at he
  simp only [mul_neg] at he
  norm_num [rawInput,offsetConfig,offsetAux,initialAux,he,Complex.ext_iff]
'''
newR='PhaseCoherence.reported (newC c a)';newU='sourceIncrement c a Bnew'
cases=[('old_C_for_R',newR,'PhaseCoherence.reported a.C','prepareDrive probeConfig 0 probeAux zeroB 0 1 = 2',step,False,'probe_C_matrix/probe_drive_matrix'),
 ('complex_mean_before_abs',newR,'complexMeanWrong (newC c a)','prepareDrive probeConfig 0 probeAux zeroB 0 1 = 2',step,False,'C01=-I/2,C10=I/2,correctR=1/2'),
 ('phase_uses_old_B',newU,'sourceIncrement c a _Bold','usedIncrement probeConfig probeAux zeroB (Capacity.Xo (2/3)) 0 = 2/3',used,True,'old_B_increment_zero'),
 ('phase_uses_unprojected_B',newU,'sourceIncrement c a (unprojected c a _Bold)','usedIncrement probeConfig probeAux zeroB (Capacity.Xo (2/3)) 0 = 2/3',used,True,'unprojected_increment_two'),
 ('history_appends_old_theta','Researcher040282.Delay.shiftAppend d a.history (nextTheta c a Bold Bnew)','Researcher040282.Delay.shiftAppend d a.history a.theta','(updateAux probeConfig 0 probeAux zeroB (Capacity.Xo (2/3))).history ⟨1,by decide⟩ 0 = 2/3',history,True,'probe_theta_new/probe_history_newest'),
 ('input_reads_newest','a.history ⟨0, Nat.zero_lt_succ d⟩ j','a.history ⟨d, Nat.lt_succ_self d⟩ j','rawInput probeConfig readProbe 0 1 = Complex.I',read,True,'probe_oldest_input'),
 ('input_drops_frequency_tau','((c.omega i + c.omega j) / 2) * c.tau','0','rawInput offsetConfig offsetAux 0 1 = -1',offset,True,'probe_frequency_offset')]

def compile_text(name,text):
 work=cache/'counterprobes'/name;work.mkdir(parents=True);(work/'Probe.lean').write_text(text);folder=out/name;folder.mkdir();(folder/'probe.lean').write_text(text)
 e=dict(env,LEAN_PATH=str(work)+os.pathsep+str(base)+os.pathsep+paths);stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.perf_counter()
 r=subprocess.run([str(bins/'lean'),'--root='+str(work),'Probe.lean'],cwd=work,env=e,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=300)
 (folder/'compiler.log').write_text(r.stdout);return r,stamp,time.perf_counter()-t

positive=prefix+common+extra+wrap+readdefs+settings
for i,(_,_,_,prop,proof,_,_) in enumerate(cases):positive+='\ntheorem positive'+str(i)+' : '+prop+' := by\n'+proof
positive+=end
r,stamp,seconds=compile_text('positive_baselines',positive);print(json.dumps({'positive_baselines':7,'returncode':r.returncode,'runtime_utc_start':stamp,'seconds':seconds}),flush=True)
if r.returncode:print(r.stdout,flush=True);raise RuntimeError('Positive exact baseline blocked, no negative credit')

def run(case):
 name,find,replace,prop,proof,extras,witness=case
 text=prefix+common+(extra if extras else '')+wrap+readdefs+settings+'\nexample : '+prop+' := by\n'+proof+end
 if find not in text:raise RuntimeError('Absent implementation target: '+name)
 text=text.replace(find,replace,1)
 r,stamp,seconds=compile_text(name,text);bad=bool(re.search(r'unknown identifier|unknown constant|unknown module|unknown namespace|unknown tactic|unexpected token|failed to synthesize|object file .* does not exist|maximum.*heartbeats|deterministic timeout',r.stdout,re.I));explicit=bool(re.search(r'⊢\s*False',r.stdout))
 row={'change':name,'runtime_utc_start':stamp,'raw_compiler_returncode':r.returncode,'seconds':seconds,'setup_or_name_failure':bad,'explicit_false_goal':explicit,'baseline_semantic_witness':witness,'first_errors':[line for line in r.stdout.splitlines() if 'error:' in line][:3]}
 (out/name/'observation.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row),flush=True)
 if r.returncode==0 or bad or not explicit:raise RuntimeError('Not explicit false mathematics: '+name)
 return row

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(run,cases))
(out/'observations.json').write_text(json.dumps({'method':'Exact fixed definition-prefix probes; same main imports, no source execution/security-verifier claim','positive_baselines':7,'positive_returncode':0,'rows':rows},indent=2)+'\n')
