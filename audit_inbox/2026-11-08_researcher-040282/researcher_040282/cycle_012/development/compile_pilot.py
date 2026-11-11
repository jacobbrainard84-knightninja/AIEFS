from pathlib import Path
import json,os,subprocess,shutil,time
here=Path(__file__).resolve().parents[1];cache=Path.home()/'.cache/researcher040282-cycle012';bins=cache/'lean-4.33.1-linux/bin';ml=cache/'mathlib4';work=cache/'pilot';work.mkdir(exist_ok=True)
env=dict(os.environ,PATH=str(bins)+os.pathsep+os.environ['PATH'],XDG_CACHE_HOME=str(cache/'xdg'),MATHLIB_CACHE_DIR=str(cache/'mathlib-downloads'),LAKE_HOME=str(cache/'lake-home'),ELAN_HOME=str(cache/'elan-home'),PYTHONDONTWRITEBYTECODE='1')
paths=subprocess.check_output([str(bins/'lake'),'env','printenv','LEAN_PATH'],cwd=ml,env=env,text=True,timeout=60).strip();env['LEAN_PATH']=str(work)+os.pathsep+paths
out=here/'development/initial_proof';records=[]
for name in ('HistoryBuffer','PhaseIncrement','CoherenceEMA','EMATracking'):
 source=here/'proposal'/(name+'.lean');shutil.copy2(source,out/source.name);shutil.copy2(source,work/source.name);start=time.perf_counter()
 run=subprocess.run([str(bins/'lean'),'--root='+str(work),'-o',str(work/(name+'.olean')),name+'.lean'],cwd=work,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=240)
 (out/(name+'.log')).write_text(run.stdout);records.append({'module':name,'returncode':run.returncode,'elapsed_seconds':time.perf_counter()-start});print(json.dumps(records[-1]),flush=True);print(run.stdout,flush=True)
 if run.returncode:raise SystemExit(run.returncode)
(out/'compile_receipt.json').write_text(json.dumps(records,indent=2)+'\n')
