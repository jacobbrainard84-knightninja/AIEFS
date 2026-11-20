from pathlib import Path
import os,subprocess,shutil,datetime,json,time
here=Path(__file__).resolve().parents[1];cache=Path.home()/'.cache/researcher040282-cycle013';work=cache/'compile';bins=cache/'lean-4.33.1-linux/bin';ml=cache/'mathlib4';out=here/'development/final_compile';out.mkdir(exist_ok=False)
env=dict(os.environ,PATH=str(bins)+os.pathsep+os.environ['PATH'],XDG_CACHE_HOME=str(cache/'xdg'),MATHLIB_CACHE_DIR=str(cache/'mathlib-downloads'),LAKE_HOME=str(cache/'lake-home'),ELAN_HOME=str(cache/'elan-home'))
env['LEAN_PATH']=str(work)+os.pathsep+subprocess.check_output([str(bins/'lake'),'env','printenv','LEAN_PATH'],cwd=ml,env=env,text=True,timeout=60).strip()
name='PhaseCoherenceBridge.lean';shutil.copy2(here/name,work/name);shutil.copy2(here/name,out/name);t=time.perf_counter();stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
r=subprocess.run([str(bins/'lean'),'--root='+str(work),'-o',str(work/'PhaseCoherenceBridge.olean'),name],cwd=work,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=300)
(out/'compiler.log').write_text(r.stdout);record={'runtime_utc_start':stamp,'seconds':time.perf_counter()-t,'returncode':r.returncode};(out/'invocation.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record));print(r.stdout);raise SystemExit(r.returncode)
