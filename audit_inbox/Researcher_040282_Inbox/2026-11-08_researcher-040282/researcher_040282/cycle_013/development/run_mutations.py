"""Fixed temporary implementation mutations; direct Lean logs, not a general
Lean security verifier or a packet-certification/check_cycle replacement."""
from pathlib import Path
import concurrent.futures,datetime,json,os,re,subprocess,time
here=Path(__file__).resolve().parents[1];cache=Path.home()/'.cache/researcher040282-cycle013';base=cache/'compile';bins=cache/'lean-4.33.1-linux/bin';ml=cache/'mathlib4'
env=dict(os.environ,PATH=str(bins)+os.pathsep+os.environ['PATH'],XDG_CACHE_HOME=str(cache/'xdg'),MATHLIB_CACHE_DIR=str(cache/'mathlib-downloads'),LAKE_HOME=str(cache/'lake-home'),ELAN_HOME=str(cache/'elan-home'))
paths=subprocess.check_output([str(bins/'lake'),'env','printenv','LEAN_PATH'],cwd=ml,env=env,text=True,timeout=60).strip()
source=(here/'PhaseCoherenceBridge.lean').read_text();out=here/'development/mutations';out.mkdir(exist_ok=False)
old='Researcher040282.Phase.inputPhasor d x0 u omega tau n i j'
cases=[('delay_extra',old,'Researcher040282.Phase.inputPhasor (d + 1) x0 u omega tau n i j','wrong_delay_refuted'),
 ('younger_slot',old,'Researcher040282.Phase.inputPhasor (d - 1) x0 u omega tau n i j','wrong_younger_refuted'),
 ('current_newest',old,'Researcher040282.Phase.inputPhasor 0 x0 u omega tau n i j','wrong_current_refuted'),
 ('drop_frequency_tau',old,'Researcher040282.Phase.inputPhasor d x0 u omega 0 n i j','wrong_offset_refuted'),
 ('phase_constant_zero',old,'Complex.exp 0','constant_phase_refuted'),
 ('complex_input_zero',old,'0','input_norm_and_probe_coherence_values'),
 ('startup_one_early','if n < d then 0 else u (n - d) j','if n + 1 < d then 0 else u (n - d) j','early_start_nonzero_and_probe_late_start'),
 ('drop_eta','(eta + mu) * reported C i j - mu','mu * reported C i j - mu','missing_eta_refuted')]

def run(case):
 name,find,replace,refutation=case
 if find not in source:raise RuntimeError('Mutation target absent: '+name)
 text=source.replace(find,replace,1);work=cache/'mutants'/name;work.mkdir(parents=True);(work/'PhaseCoherenceBridge.lean').write_text(text)
 directory=out/name;directory.mkdir();(directory/'change.txt').write_text('IMPLEMENTATION ONLY; statements/reference/probes/main imports held fixed\n'+find+'\n-> '+replace+'\n')
 e=dict(env,LEAN_PATH=str(work)+os.pathsep+str(base)+os.pathsep+paths);stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.perf_counter()
 r=subprocess.run([str(bins/'lean'),'--root='+str(work),'PhaseCoherenceBridge.lean'],cwd=work,env=e,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=300)
 (directory/'compiler.log').write_text(r.stdout)
 bad=re.search(r'unknown identifier|unknown constant|unknown module|unknown namespace|unexpected token|failed to synthesize|unknown tactic|object file .* does not exist|maximum.*heartbeats|deterministic timeout',r.stdout,re.I)
 row={'mutation':name,'runtime_utc_start':stamp,'raw_compiler_returncode':r.returncode,'seconds':time.perf_counter()-t,'setup_or_name_error':bool(bad),
      'independent_baseline_refutation':refutation,'first_errors':[line for line in r.stdout.splitlines() if 'error:' in line][:5]}
 (directory/'observation.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row),flush=True)
 if r.returncode==0 or bad:raise RuntimeError('Mutation survived or failed only for a blocker: '+name)
 return row

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(run,cases))
(out/'observations.json').write_text(json.dumps({'scope':'Eight fixed implementation mutations; direct compiler observations +separately compiled baseline semantic refutations, not a general verifier','rows':rows},indent=2)+'\n')
