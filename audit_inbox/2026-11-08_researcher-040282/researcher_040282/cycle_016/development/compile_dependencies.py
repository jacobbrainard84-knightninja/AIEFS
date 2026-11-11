from pathlib import Path
import os,subprocess,shutil,json,datetime,time
here=Path(__file__).resolve().parents[1];cache=Path.home()/'.cache/researcher040282-cycle016';work=cache/'compile';work.mkdir(exist_ok=True);bins=cache/'lean-4.33.1-linux/bin';ml=cache/'mathlib4';out=here/'development/dependency_compile';out.mkdir(exist_ok=True)
env=dict(os.environ,PATH=str(bins)+os.pathsep+os.environ['PATH'],XDG_CACHE_HOME=str(cache/'xdg'),MATHLIB_CACHE_DIR=str(cache/'mathlib-downloads'),LAKE_HOME=str(cache/'lake-home'),ELAN_HOME=str(cache/'elan-home'));env['LEAN_PATH']=str(work)+os.pathsep+subprocess.check_output([str(bins/'lake'),'env','printenv','LEAN_PATH'],cwd=ml,env=env,text=True,timeout=60).strip();rows=[]
for name in ('GateMap','MatrixForm','HistoryBuffer','PhaseIncrement','PhaseCoherence'):
 relative='AIEFGateCore/'+name+'.lean';source=here/'source_state/p5/lean/AIEFGateCore'/relative;target=work/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.perf_counter()
 r=subprocess.run([str(bins/'lean'),'--root='+str(work),'-o',str(target.with_suffix('.olean')),relative],cwd=work,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=300)
 (out/(name+'.log')).write_text(r.stdout);row={'branch_file':relative,'basis':'UNMERGEDteamP5@54037ea','runtime_utc_start':stamp,'returncode':r.returncode,'seconds':time.perf_counter()-t};rows.append(row);(out/'invocations.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
 if r.returncode:print(r.stdout,flush=True);raise SystemExit(r.returncode)
