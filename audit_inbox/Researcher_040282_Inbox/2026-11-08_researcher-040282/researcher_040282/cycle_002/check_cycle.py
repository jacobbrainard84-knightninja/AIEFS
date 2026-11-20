"""Fresh Lean builds, axiom-footprint checks, and known-false controls.

This is a bounded research harness for the supplied closed proof file, not a
claim of a general-purpose secure Lean source parser or repository CI replacement.
No expected-failure is accepted unless its intended rejection reason is observed.
"""
from __future__ import annotations
import concurrent.futures
from fractions import Fraction as F
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time

ROOT=Path(__file__).resolve().parent
CACHE=Path(os.environ.get('R040282_CACHE',Path.home()/'.cache/researcher040282')).expanduser().resolve()
MATHLIB=Path(os.environ.get('R040282_MATHLIB',CACHE/'mathlib4')).expanduser().resolve()
# Preserve an elan wrapper's basename; resolving its symlink would invoke elan
# itself rather than lean. Query the version inside the pinned Mathlib project.
LEAN=Path(os.environ.get('R040282_LEAN_BIN',CACHE/'lean-4.33.1-linux/bin/lean')).expanduser().absolute()
LAKE=LEAN.parent/'lake'
MATHLIB_REVISION='0df444a360eaa60ab8c11dca51a86af692955474'
ALLOWED={'propext','Classical.choice','Quot.sound'}
SOURCE=ROOT/'GateFoundations.lean'
LOGS=ROOT/'checks';LOGS.mkdir(exist_ok=True)


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
    code=without_comments_and_strings(source)
    problems=[]
    if returncode!=0:problems.append('compiler_nonzero')
    if re.search(r'\bwarning\b',output,re.I):problems.append('compiler_warning')
    forbidden=sorted(set(re.findall(r'\b(?:sorry|admit|native_decide|axiom)\b',code)))
    if forbidden:problems.append('forbidden_source_token:'+','.join(forbidden))
    declarations=re.findall(r'(?m)^theorem\s+([A-Za-z0-9_]+)',code)
    requested=re.findall(r'(?m)^#print\s+axioms\s+([A-Za-z0-9_.]+)',code)
    if sorted(declarations)!=sorted(name.rsplit('.',1)[-1] for name in requested):
        problems.append('theorem_axiom_print_coverage')
    footprints={}
    for name,values in re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]",output):
        footprints[name]=[v.strip() for v in values.split(',') if v.strip()]
    for name in requested:
        if name not in footprints:problems.append('missing_axiom_output:'+name)
    for name,axioms in footprints.items():
        extra=set(axioms)-ALLOWED
        if extra:problems.append('unapproved_axioms:'+name+':'+','.join(sorted(extra)))
    return {'verified':not problems,'problems':problems,'theorem_count':len(declarations),
            'axiom_footprints':footprints,'allowed_axioms':sorted(ALLOWED)}


def compile_case(item):
    name,source,kind=item
    env=os.environ.copy();env['PATH']=str(LEAN.parent)+os.pathsep+env.get('PATH','')
    started=time.perf_counter()
    # Each run gets a fresh source/output directory; no old module result can
    # supply a successful exit or the printed footprint for this source text.
    CACHE.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='r040282-lean-'+name+'-',dir=CACHE) as tmp:
        directory=Path(tmp);path=directory/'Candidate.lean';path.write_text(source)
        command=[str(LAKE),'env','lean','--root='+str(directory),'-o',str(directory/'Candidate.olean'),str(path)]
        run=subprocess.run(command,cwd=MATHLIB,env=env,text=True,stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,timeout=120)
    (LOGS/(name+'.log')).write_text(run.stdout)
    checked=assess(source,run.returncode,run.stdout)
    math_error=bool(re.search(r'unsolved goals|type mismatch|tactic.*failed',run.stdout,re.I))
    import_error=bool(re.search(r'unknown module|unknown constant|unknown identifier|object file.*does not exist|failed to import',run.stdout,re.I))
    if kind=='positive':ok=run.returncode==0 and checked['verified']
    elif kind=='false_math':ok=run.returncode!=0 and math_error and not import_error and not checked['verified']
    elif kind=='sorry_payload':ok=run.returncode==0 and not checked['verified'] and any('sorryAx' in p for p in checked['problems'])
    elif kind=='extra_axiom_payload':ok=run.returncode==0 and not checked['verified'] and any('unapproved_axioms:' in p for p in checked['problems'])
    elif kind=='missing_footprint':ok=run.returncode==0 and not checked['verified'] and 'theorem_axiom_print_coverage' in checked['problems']
    else:raise ValueError(kind)
    return {'case':name,'kind':kind,'control_passed':ok,'raw_lean_exit':run.returncode,
            'elapsed_seconds':time.perf_counter()-started,'mathematical_error_observed':math_error,
            'dependency_error_observed':import_error,**checked}


def rational_controls():
    c=F(19,30);eps=F(1,10**12)
    def rows(w):return [sum(row,F(0)) for row in w]
    def apply(w,use_max=False):
        rs=rows(w)
        if all(r<=c for r in rs):return [row.copy() for row in w]
        s=[min(F(1),c/(r+eps)) for r in rs]
        operation=max if use_max else min
        return [[w[i][j]*operation(s[i],s[j]) for j in range(len(w))] for i in range(len(w))]
    # Nonzero active-gate witness; all retained hypotheses hold.
    star=[[F(0)]*3 for _ in range(3)]
    star[0][1]=star[1][0]=F(1,2);star[0][2]=star[2][0]=F(1,2)
    actual=apply(star);wrong=apply(star,use_max=True)
    assert all(x>=0 for row in star for x in row) and rows(star)[0]>c
    assert all(r<=c for r in rows(actual)) and any(x>0 for row in actual for x in row)
    assert rows(wrong)[0]>c
    # Negative entry, but all row sums remain nonnegative: shrinking negative
    # terms differently breaks the row-sum proof even without bad denominators.
    signed=[[F(0)]*5 for _ in range(5)]
    for i,j,w in [(0,1,F(1,2)),(0,2,F(1,2)),(0,3,F(-1,2)),(3,4,F(100))]:
        signed[i][j]=signed[j][i]=w
    assert all(r>=0 for r in rows(signed))
    signed_result=apply(signed)
    assert rows(signed_result)[0]==1-c/(199+2*eps)>c
    return [
        {'case':'nonzero_active_gate_witness','kind':'positive_exact','control_passed':True,
         'input_row_zero':str(rows(star)[0]),'output_row_zero':str(rows(actual)[0]),
         'capacity':str(c),'output_nonzero':True},
        {'case':'replace_endpoint_min_with_max','kind':'exact_counterexample','control_passed':True,
         'wrong_output_row_zero':str(rows(wrong)[0]),'capacity':str(c)},
        {'case':'drop_entrywise_nonnegativity','kind':'exact_counterexample','control_passed':True,
         'input_row_sums':[str(r) for r in rows(signed)],
         'output_row_zero':str(rows(signed_result)[0]),'capacity':str(c)}]


def main():
    # A blocked or failed rerun must not leave an old success JSON in place.
    (ROOT/'cycle_results.json').unlink(missing_ok=True)
    assert LEAN.is_file() and LAKE.is_file() and (MATHLIB/'lakefile.lean').is_file(), 'Set up the recorded compiler and mathlib first'
    version=subprocess.check_output([str(LEAN),'--version'],cwd=MATHLIB,text=True).strip()
    assert 'version 4.33.1,' in version
    revision=subprocess.check_output(['git','-C',str(MATHLIB),'rev-parse','HEAD'],text=True).strip()
    assert revision==MATHLIB_REVISION, 'Use the recorded Mathlib source'
    source=SOURCE.read_text()
    suffix='\nopen Researcher040282\n'
    cases=[('positive',source,'positive'),
      ('false_unconditional_idempotence',source+suffix+'''\nexample : ratKernel (19/30) (1/1000000000000)
  (ratKernel (19/30) (1/1000000000000) (19/30)) =
  ratKernel (19/30) (1/1000000000000) (19/30) := by
  norm_num [ratKernel]
''','false_math'),
      ('false_unrestricted_epsilon',source+suffix+'''\nexample : ratGate 1 (-1/2) (3/2) ≤ (1:ℚ) := by
  norm_num [ratGate, ratKernel]
''','false_math'),
      ('sorry_payload',source+'''\ntheorem falseWithHole : (0:ℚ) = 1 := by sorry
#print axioms falseWithHole
''','sorry_payload'),
      ('extra_axiom_payload',source+'''\naxiom injectedEquality : (0:ℚ) = 1
theorem falseWithAxiom : (0:ℚ) = 1 := injectedEquality
#print axioms falseWithAxiom
''','extra_axiom_payload'),
      ('missing_footprint',source.replace('#print axioms Researcher040282.kernel_feasible\n',''),'missing_footprint')]
    print('Compiling fresh proof and adversarial sources.',flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(compile_case,cases))
    results+=rational_controls()
    summary={'agent':'Researcher 040282','cycle':2,'compiler_version':version,
             'mathlib_revision':revision,
             'source_sha256':hashlib.sha256(source.encode()).hexdigest(),
             'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             'all_controls_passed':all(r['control_passed'] for r in results),
             'control_count':len(results),'controls':results,
             'scope':'local research proof/harness, not independent-seat review or repository integration'}
    (ROOT/'cycle_results.json').write_text(json.dumps(summary,indent=2)+'\n')
    for r in results:print(r['case'],'PASS' if r['control_passed'] else 'GAP',
        'raw_lean_exit='+str(r.get('raw_lean_exit','not applicable')),
        'verified='+str(r.get('verified','not applicable')),flush=True)
    print('All controls passed:',summary['all_controls_passed'],flush=True)
    return 0 if summary['all_controls_passed'] else 1


if __name__=='__main__':raise SystemExit(main())
