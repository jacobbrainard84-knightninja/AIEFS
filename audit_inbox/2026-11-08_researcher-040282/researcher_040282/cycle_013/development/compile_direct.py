"""Direct compiler invocation for fixed owned sources, not a security verifier."""
from pathlib import Path
import os,subprocess,shutil,json,datetime,time
here=Path(__file__).resolve().parents[1];root=here.parent;cache=Path.home()/'.cache/researcher040282-cycle013';work=cache/'compile';work.mkdir(exist_ok=True)
bins=cache/'lean-4.33.1-linux/bin';ml=cache/'mathlib4'
env=dict(os.environ,PATH=str(bins)+os.pathsep+os.environ['PATH'],XDG_CACHE_HOME=str(cache/'xdg'),MATHLIB_CACHE_DIR=str(cache/'mathlib-downloads'),LAKE_HOME=str(cache/'lake-home'),ELAN_HOME=str(cache/'elan-home'),PYTHONDONTWRITEBYTECODE='1')
paths=subprocess.check_output([str(bins/'lake'),'env','printenv','LEAN_PATH'],cwd=ml,env=env,text=True,timeout=60).strip();env['LEAN_PATH']=str(work)+os.pathsep+paths
out=here/'development/initial_compile';out.mkdir(exist_ok=True);rows=[]
files=[('HistoryBuffer.lean',root/'cycle_011/proposal/HistoryBuffer.lean'),('PhaseIncrement.lean',root/'cycle_011/proposal/PhaseIncrement.lean'),
 ('AIEFGateCore/GateMap.lean',here/'source_state/main/lean/AIEFGateCore/AIEFGateCore/GateMap.lean'),('AIEFGateCore/MatrixForm.lean',here/'source_state/main/lean/AIEFGateCore/AIEFGateCore/MatrixForm.lean'),('PhaseCoherenceBridge.lean',here/'PhaseCoherenceBridge.lean')]
for relative,source in files:
 target=work/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);saved=out/relative;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,saved)
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.perf_counter();result=subprocess.run([str(bins/'lean'),'--root='+str(work),'-o',str(target.with_suffix('.olean')),relative],cwd=work,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=300)
 (out/(relative.replace('/','_')+'.log')).write_text(result.stdout);row={'file':relative,'runtime_utc_start':start,'returncode':result.returncode,'seconds':time.perf_counter()-t};rows.append(row);print(json.dumps(row),flush=True);print(result.stdout,flush=True)
 (out/'invocations.json').write_text(json.dumps(rows,indent=2)+'\n')
 if result.returncode:raise SystemExit(result.returncode)
