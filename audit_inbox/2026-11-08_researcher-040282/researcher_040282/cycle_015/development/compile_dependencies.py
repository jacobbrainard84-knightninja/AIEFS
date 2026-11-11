from pathlib import Path
import os,subprocess,shutil,json,datetime,time
here=Path(__file__).resolve().parents[1];root=here.parent;cache=Path.home()/'.cache/researcher040282-cycle015';work=cache/'compile';work.mkdir(exist_ok=True);bins=cache/'lean-4.33.1-linux/bin';ml=cache/'mathlib4';out=here/'development/dependency_compile';out.mkdir(exist_ok=True)
env=dict(os.environ,PATH=str(bins)+os.pathsep+os.environ['PATH'],XDG_CACHE_HOME=str(cache/'xdg'),MATHLIB_CACHE_DIR=str(cache/'mathlib-downloads'),LAKE_HOME=str(cache/'lake-home'),ELAN_HOME=str(cache/'elan-home'));env['LEAN_PATH']=str(work)+os.pathsep+subprocess.check_output([str(bins/'lake'),'env','printenv','LEAN_PATH'],cwd=ml,env=env,text=True,timeout=60).strip()
files=[('AIEFGateCore/'+name+'.lean',here/'source_state/main/lean/AIEFGateCore/AIEFGateCore'/(name+'.lean')) for name in ('GateMap','K3','RedTeam','EngineWitness','MatrixForm','Capacity')]
files += [('HistoryBuffer.lean',root/'cycle_011/proposal/HistoryBuffer.lean'),('PhaseIncrement.lean',root/'cycle_011/proposal/PhaseIncrement.lean'),('PhaseCoherenceBridge.lean',root/'cycle_013/PhaseCoherenceBridge.lean'),('TrajectoryInvariants.lean',root/'cycle_014/TrajectoryInvariants.lean')]
rows=[]
for relative,source in files:
 target=work/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.perf_counter()
 r=subprocess.run([str(bins/'lean'),'--root='+str(work),'-o',str(target.with_suffix('.olean')),relative],cwd=work,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=300)
 (out/(relative.replace('/','_')+'.log')).write_text(r.stdout);row={'file':relative,'runtime_utc_start':stamp,'returncode':r.returncode,'seconds':time.perf_counter()-t};rows.append(row);(out/'invocations.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
 if r.returncode:print(r.stdout,flush=True);raise SystemExit(r.returncode)
