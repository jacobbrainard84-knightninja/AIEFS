"""Fresh guarded-weight bridge builds and bounded adversarial controls.

This closed-file research harness is not a secure general Lean parser/executor
or a replacement for the receiving seat's trusted compiler and repository CI.
"""
from __future__ import annotations
import sys
if not __debug__:
    print('Python assertions must be enabled; do not use -O/-OO.', file=sys.stderr)
    raise SystemExit(2)
import argparse
import concurrent.futures
from fractions import Fraction as F
import hashlib
import json
import os
from pathlib import Path
import random
import re
import subprocess
import tempfile
import time

ROOT=Path(__file__).resolve().parent
CACHE=Path(os.environ.get('R040282_CACHE',Path.home()/'.cache/researcher040282')).expanduser().resolve()
MATHLIB=Path(os.environ.get('R040282_MATHLIB',CACHE/'mathlib4')).expanduser().resolve()
LEAN=Path(os.environ.get('R040282_LEAN_BIN',CACHE/'lean-4.33.1-linux/bin/lean')).expanduser().absolute()
LAKE=LEAN.parent/'lake'
REVISION='0df444a360eaa60ab8c11dca51a86af692955474'
ALLOWED={'propext','Classical.choice','Quot.sound'}
FILES=['GateFoundations.lean','FreezeCore.lean','GateProposalBridge.lean','CoherenceEMA.lean','CoherenceDriveBridge.lean']
LOGS=ROOT/'pilot'


def without_comments_and_strings(text):
    result=[];i=0;depth=0;string=False
    while i<len(text):
        if depth:
            if text.startswith('/-',i):depth+=1;result.extend('  ');i+=2
            elif text.startswith('-/',i):depth-=1;result.extend('  ');i+=2
            else:result.append('\n' if text[i]=='\n' else ' ');i+=1
        elif string:
            if text[i]=='\\' and i+1<len(text):result.extend('  ');i+=2
            elif text[i]=='"':string=False;result.append(' ');i+=1
            else:result.append('\n' if text[i]=='\n' else ' ');i+=1
        elif text.startswith('/-',i):depth=1;result.extend('  ');i+=2
        elif text.startswith('--',i):
            end=text.find('\n',i)
            if end<0:end=len(text)
            result.extend(' '*(end-i));i=end
        elif text[i]=='"':string=True;result.append(' ');i+=1
        else:result.append(text[i]);i+=1
    if depth or string:raise ValueError('Unterminated source comment or string')
    return ''.join(result)


def assess(source,returncode,output):
    code=without_comments_and_strings(source);problems=[]
    if returncode!=0:problems.append('compiler_nonzero')
    if re.search(r'\bwarning\b',output,re.I):problems.append('compiler_warning')
    forbidden=sorted(set(re.findall(r'\b(?:sorry|admit|native_decide|axiom|unsafe)\b',code)))
    if forbidden:problems.append('forbidden_source_token:'+','.join(forbidden))
    declarations=re.findall(r'(?m)^(?:theorem|lemma)\s+([A-Za-z0-9_]+)',code)
    requested=re.findall(r'(?m)^#print\s+axioms\s+([A-Za-z0-9_.]+)',code)
    if sorted(declarations)!=sorted(n.rsplit('.',1)[-1] for n in requested):
        problems.append('theorem_axiom_print_coverage')
    footprints={name:[v.strip() for v in values.split(',') if v.strip()]
        for name,values in re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]",output)}
    for name in re.findall(r"'([^']+)' does not depend on any axioms",output):footprints[name]=[]
    for name in requested:
        if name not in footprints:problems.append('missing_axiom_output:'+name)
    for name,values in footprints.items():
        if set(values)-ALLOWED:problems.append('unapproved_axioms:'+name+':'+','.join(sorted(set(values)-ALLOWED)))
    return {'verified':not problems,'problems':problems,'declaration_count':len(declarations),
            'axiom_footprints':footprints}


def compile_one(name,source,directory,env,log_name=None):
    path=directory/(name+'.lean');path.write_text(source);started=time.perf_counter()
    run=subprocess.run([str(LEAN),'--root='+str(directory),'-o',str(directory/(name+'.olean')),str(path)],
        cwd=MATHLIB,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
    elapsed=time.perf_counter()-started
    (LOGS/((log_name or name)+'.log')).write_text(run.stdout)
    return run,elapsed


def main():
    LOGS.mkdir(exist_ok=True);CACHE.mkdir(parents=True,exist_ok=True)
    base=os.environ.copy();base['PATH']=str(LEAN.parent)+os.pathsep+base.get('PATH','')
    env=json.loads(subprocess.check_output([str(LAKE),'env','python','-c','import json,os; print(json.dumps(dict(os.environ)))'],cwd=MATHLIB,env=base,text=True))
    results=[]
    with tempfile.TemporaryDirectory(prefix='r040282-c004-pilot-',dir=CACHE) as tmp:
        directory=Path(tmp);env['LEAN_PATH']=str(directory)+os.pathsep+env.get('LEAN_PATH','')
        for filename in FILES:
            source=(ROOT/filename).read_text();run,elapsed=compile_one(Path(filename).stem,source,directory,env)
            check=assess(source,run.returncode,run.stdout)
            row={'module':Path(filename).stem,'raw_lean_exit':run.returncode,'seconds':elapsed,**check};results.append(row)
            print(row['module'],'raw',run.returncode,'verified',check['verified'],'declarations',check['declaration_count'],'problems',check['problems'],flush=True)
            if not check['verified']:
                print(run.stdout,flush=True);break
    (ROOT/'pilot_results.json').write_text(json.dumps(results,indent=2)+'\n')
    return 0 if len(results)==len(FILES) and all(r['verified'] for r in results) else 1

if __name__=='__main__':raise SystemExit(main())
