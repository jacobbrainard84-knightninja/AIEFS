"""Fresh topological pilot compilation; final adversarial harness is separate."""
from pathlib import Path
import json
import os
import re
import subprocess
import tempfile
import time

ROOT=Path(__file__).resolve().parent
CACHE=Path.home()/'.cache/researcher040282'
LEAN=CACHE/'lean-4.33.1-linux/bin/lean'
LAKE=LEAN.parent/'lake'
MATHLIB=CACHE/'mathlib4'
LOGS=ROOT/'pilot';LOGS.mkdir(exist_ok=True)
base_env=os.environ.copy();base_env['PATH']=str(LEAN.parent)+os.pathsep+base_env.get('PATH','')
env=json.loads(subprocess.check_output([str(LAKE),'env','python','-c',
    'import json,os; print(json.dumps(dict(os.environ)))'],cwd=MATHLIB,env=base_env,text=True))
results=[]
with tempfile.TemporaryDirectory(prefix='r040282-c003-pilot-',dir=CACHE) as tmp:
    directory=Path(tmp);env['LEAN_PATH']=str(directory)+os.pathsep+env.get('LEAN_PATH','')
    for name in ['GateFoundations','FreezeCore','GateProposalBridge']:
        source=(ROOT/(name+'.lean')).read_text();path=directory/(name+'.lean');path.write_text(source)
        started=time.perf_counter()
        run=subprocess.run([str(LEAN),'--root='+str(directory),'-o',str(directory/(name+'.olean')),str(path)],
            cwd=MATHLIB,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
        (LOGS/(name+'.log')).write_text(run.stdout)
        footprints=re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]",run.stdout)
        result={'module':name,'exit':run.returncode,'seconds':time.perf_counter()-started,
            'printed_footprints':len(footprints),'warnings':bool(re.search(r'warning:',run.stdout)),
            'extra_axioms':sorted({a.strip() for _,v in footprints for a in v.split(',') if a.strip()}-{'propext','Classical.choice','Quot.sound'})}
        results.append(result);print(json.dumps(result),flush=True)
        if run.returncode!=0:break
(ROOT/'pilot_results.json').write_text(json.dumps(results,indent=2)+'\n')
raise SystemExit(0 if len(results)==3 and all(r['exit']==0 and not r['warnings'] and not r['extra_axioms'] for r in results) else 1)
