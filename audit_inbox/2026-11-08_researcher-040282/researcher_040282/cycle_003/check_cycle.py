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
FILES=['GateFoundations.lean','FreezeCore.lean','GateProposalBridge.lean']
LOGS=ROOT/'checks'


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


def compile_case(item,dependencies,env):
    name,source,kind=item
    with tempfile.TemporaryDirectory(prefix='r040282-c003-'+name+'-',dir=CACHE) as tmp:
        directory=Path(tmp);local_env=env.copy()
        local_env['LEAN_PATH']=str(directory)+os.pathsep+str(dependencies)+os.pathsep+env.get('LEAN_PATH','')
        run,elapsed=compile_one('Candidate',source,directory,local_env,log_name=name)
    # Each case has its own source, output module and durable log.
    checked=assess(source,run.returncode,run.stdout)
    math_error=bool(re.search(r'unsolved goals|type mismatch|tactic.*failed',run.stdout,re.I))
    dependency_error=bool(re.search(r'unknown module|unknown constant|unknown identifier|object file.*does not exist|failed to import|synthInstanceFailed',run.stdout,re.I))
    if kind=='positive':ok=run.returncode==0 and checked['verified']
    elif kind=='false_math':ok=run.returncode!=0 and math_error and not dependency_error and not checked['verified']
    elif kind=='sorry_payload':ok=run.returncode==0 and not checked['verified'] and any('sorryAx' in p for p in checked['problems'])
    elif kind=='extra_axiom_payload':ok=run.returncode==0 and not checked['verified'] and any('unapproved_axioms:' in p for p in checked['problems'])
    elif kind=='missing_footprint':ok=run.returncode==0 and not checked['verified'] and 'theorem_axiom_print_coverage' in checked['problems']
    else:raise ValueError(kind)
    return {'case':name,'kind':kind,'control_passed':ok,'raw_lean_exit':run.returncode,
            'seconds':elapsed,'mathematical_error_observed':math_error,
            'dependency_error_observed':dependency_error,**checked}


def rows(w):return [sum(row,F(0)) for row in w]
def zeros(n):return [[F(0) for _ in range(n)] for _ in range(n)]
def positive_rows(u):return [sum((max(F(0),x) for j,x in enumerate(row) if i!=j),F(0)) for i,row in enumerate(u)]
def propose(h,b,u):
    return [[F(0) if i==j else max(F(0),(1-h)*b[i][j]+h*u[i][j])
        for j in range(len(b))] for i in range(len(b))]
def gate_info(c,eps,w):
    rs=rows(w);candidate=[min(F(1),c/(r+eps)) for r in rs];active=any(r>c for r in rs)
    applied=candidate if active else [F(1)]*len(w)
    result=[[w[i][j]*min(applied[i],applied[j]) for j in range(len(w))] for i in range(len(w))]
    return result,applied,candidate,active

def floor(c,eps,m):return min(F(1),c/(m+eps))
def envelope(c,h,s):return (1-h)*c+h*s

def exact_controls():
    rng=random.Random(20261107);counts={'cases':384,'active':0,'inactive':0,'capacity_zero':0,'zero_rows':0}
    for case in range(counts['cases']):
        n=rng.choice([1,2,3,4,6,12]);c=rng.choice([F(0),F(19,30),F(1),F(3)])
        h=rng.choice([F(0),F(1,10),F(1,2),F(1)]);eps=rng.choice([F(1,10**12),F(1,10),F(2)])
        b=zeros(n);u=zeros(n)
        for i in range(n):
            u[i][i]=F(rng.randint(-20,20),6)
            for j in range(i):
                b[i][j]=b[j][i]=F(rng.randint(0,20),20)
                u[i][j]=u[j][i]=F(rng.randint(-20,20),6)
        factor=c/(1+max(rows(b),default=F(0)))
        b=[[x*factor for x in row] for row in b]
        assert all(r<=c for r in rows(b))
        p=propose(h,b,u);sp=positive_rows(u);ms=[envelope(c,h,s) for s in sp]
        out,applied,_,active=gate_info(c,eps,p)
        counts['active' if active else 'inactive']+=1;counts['capacity_zero']+=int(c==0)
        counts['zero_rows']+=sum(r==0 for r in rows(p))
        assert all(x>=0 for row in out for x in row) and all(r<=c for r in rows(out))
        assert all(out[i][i]==0 for i in range(n))
        assert all(out[i][j]==out[j][i] for i in range(n) for j in range(n))
        for i,r in enumerate(rows(p)):
            assert r<=(1-h)*rows(b)[i]+h*sp[i]<=ms[i]
            assert 0<=applied[i]<=1 and applied[i]*r<=c
            if r>0:assert applied[i]<=c/r
            assert floor(c,eps,ms[i])<=applied[i]
            for j in range(n):
                kappa=floor(c,eps,max(ms[i],ms[j]))
                assert 0<=kappa<=min(applied[i],applied[j])<=1
                if c>0:assert kappa>0
    assert counts['active']>0 and counts['inactive']>0 and counts['capacity_zero']>0 and counts['zero_rows']>0
    # Configured exact-rational constants, K3 padded to twelve nodes.
    c=F(19,30);eps=F(1,10**12);h=F(3,20000);b=zeros(12);u=[[F(-2)]*12 for _ in range(12)]
    for i in range(3):
        for j in range(i):b[i][j]=b[j][i]=c/2;u[i][j]=u[j][i]=F(8,3)
    p=propose(h,b,u);out,app,_,active=gate_info(c,eps,p);s=positive_rows(u)[0]
    kappa=floor(c,eps,envelope(c,h,s));share=kappa*h*F(8,3)/(1-kappa*(1-h));bc=F(3,25)
    assert all(r<=c for r in rows(b)) and active and out[0][1]>0
    assert 0<kappa<=app[0]<=1 and 1-kappa*(1-h)>0 and share>bc
    default_witness={'c':str(c),'epsilon':str(eps),'h':str(h),'endpoint_drive_bound':str(s),
        'kappa':str(kappa),'comparison_fixed_point':str(share),'threshold':str(bc),
        'proposal_row_0':str(rows(p)[0]),'output_row_0':str(rows(out)[0]),'active':active}
    # A distinct initial-OFF example turns ON, then uses an active gate.
    b=zeros(2);u=[[F(0),F(2)],[F(2),F(0)]];statuses=[False];active_steps=[]
    for _ in range(4):
        b,_,_,act=gate_info(F(1),eps,propose(F(1,2),b,u))
        statuses.append(b[0][1]>F(1,2));active_steps.append(act)
    assert statuses[1:] == [True]*4 and active_steps[0] is False and active_steps[1] is True
    # Inactive all-zero input: c=1, epsilon=2, applied=1 but candidate=1/2.
    z=zeros(12);_,app,can,act=gate_info(F(1),F(2),z)
    assert not act and app[0]==1 and can[0]==F(1,2)
    # Dropping epsilon defeats the floor on a globally active, valid proposal.
    b=zeros(4);u=zeros(4)
    for i,j,x in [(0,1,F(1)),(2,3,F(1))]:b[i][j]=b[j][i]=x
    u[0][1]=u[1][0]=F(1);u[2][3]=u[3][2]=F(3)
    p=propose(F(1,2),b,u);_,app,_,act=gate_info(F(1),eps,p)
    assert all(r<=1 for r in rows(b)) and rows(p)[0]==1 and act
    assert app[0]==floor(F(1),eps,F(1))<floor(F(1),F(0),F(1))==1
    epsilon_witness={'actual_local_factor':str(app[0]),'epsilon_free_floor':'1','previous_rows':[str(r) for r in rows(b)],'proposal_rows':[str(r) for r in rows(p)]}
    # Strictly positive factor floors cannot be demanded at capacity zero.
    b=zeros(2);u=[[F(0),F(1)],[F(1),F(0)]];p=propose(F(1,2),b,u)
    out,app,_,act=gate_info(F(0),eps,p)
    assert act and app[0]==0 and all(x==0 for row in out for x in row)
    assert floor(F(0),eps,envelope(F(0),F(1,2),F(1)))==0
    # Real symmetrization is not the identity without the drive symmetry premise.
    b=zeros(2);u=[[F(0),F(2)],[F(0),F(0)]];p=propose(F(1,2),b,u)
    sym=[[F(0) if i==j else (p[i][j]+p[j][i])/2 for j in range(2)] for i in range(2)]
    assert p[0][1]==1 and sym[0][1]==F(1,2) and p!=sym
    # A diagonal-only positive forcing must not create self-edges or drive rows.
    b=zeros(3);u=zeros(3)
    for i in range(3):u[i][i]=F(10)
    p=propose(F(1,2),b,u)
    assert p==zeros(3) and positive_rows(u)==[F(0)]*3
    return [
      {'case':'exact_fraction_suite','kind':'positive_exact','control_passed':True,**counts},
      {'case':'nonvacuous_on_active_and_turn_on','kind':'positive_exact','control_passed':True,'default_active_witness':default_witness,'from_empty_statuses':statuses,'from_empty_active_steps':active_steps},
      {'case':'inactive_zero_row_witness','kind':'positive_exact','control_passed':True,'applied_factor':'1','candidate_scale':'1/2'},
      {'case':'drop_epsilon_from_floor','kind':'exact_counterexample','control_passed':True,**epsilon_witness},
      {'case':'strict_positive_floor_at_zero_capacity','kind':'exact_counterexample','control_passed':True,'actual_factor':'0','floor':'0','output_all_zero':True},
      {'case':'drop_symmetry_from_source_identification','kind':'exact_counterexample','control_passed':True,'masked_proposal_01':'1','symmetrized_source_01':'1/2'},
      {'case':'diagonal_mask_witness','kind':'positive_exact','control_passed':True,'diagonal_drive':'10','proposal_all_zero':True,'positive_drive_rows_all_zero':True}]


def optimization_control():
    run=subprocess.run([sys.executable,'-O',str(Path(__file__).resolve()),'--assertions-only'],
        text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=20)
    return {'case':'python_optimization_mode','kind':'policy_negative','control_passed':
        run.returncode==2 and 'assertions must be enabled' in run.stdout,
        'raw_python_exit':run.returncode,'observed_output':run.stdout.strip()}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--exact-only',action='store_true');args=parser.parse_args()
    started=time.perf_counter()
    if args.exact_only:
        controls=exact_controls()+[optimization_control()]
        result={'agent':'Researcher 040282','cycle':3,'scope':'exact controls only; no Lean invocation',
            'all_controls_passed':all(r['control_passed'] for r in controls),'controls':controls}
        (ROOT/'exact_results.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result,indent=2));return 0 if result['all_controls_passed'] else 1
    (ROOT/'cycle_results.json').unlink(missing_ok=True)
    assert LEAN.is_file() and LAKE.is_file() and (MATHLIB/'lakefile.lean').is_file()
    version=subprocess.check_output([str(LEAN),'--version'],cwd=MATHLIB,text=True).strip()
    assert 'version 4.33.1,' in version
    revision=subprocess.check_output(['git','-C',str(MATHLIB),'rev-parse','HEAD'],text=True).strip();assert revision==REVISION
    sources={name:(ROOT/name).read_text() for name in FILES}
    base_env=os.environ.copy();base_env['PATH']=str(LEAN.parent)+os.pathsep+base_env.get('PATH','')
    env=json.loads(subprocess.check_output([str(LAKE),'env','python','-c',
        'import json,os; print(json.dumps(dict(os.environ)))'],cwd=MATHLIB,env=base_env,text=True))
    CACHE.mkdir(parents=True,exist_ok=True);LOGS.mkdir(exist_ok=True)
    builds=[];bridge=sources['GateProposalBridge.lean'];suffix='\nopen Researcher040282\n'
    cases=[('positive',bridge,'positive'),
      ('false_previous_row_bound',bridge+suffix+'''\nexample : max 0 ((1-(1/2:ℚ))*3+(1/2)*0) ≤ (1-(1/2:ℚ))*1+(1/2)*0 := by
  norm_num
''','false_math'),
      ('false_without_h_lower',bridge+suffix+'''\nexample : max 0 ((1-(-1:ℚ))*1+(-1)*(-2)) ≤ (1-(-1:ℚ))*1+(-1)*0 := by
  norm_num
''','false_math'),
      ('false_without_h_upper',bridge+suffix+'''\nexample : max 0 ((1-(2:ℚ))*0+2*0) ≤ (1-(2:ℚ))*1+2*0 := by
  norm_num
''','false_math'),
      ('false_zero_row_ratio',bridge+suffix+'''\nexample : appliedNodeScale (fun _ : Fin 12 => (1:ℝ)) 1 (fun _ _ => 0) 0 ≤ (1:ℝ)/0 := by
  norm_num [appliedNodeScale, feasible, rowSum]
''','false_math'),
      ('false_candidate_equals_applied',bridge+suffix+'''\nexample : appliedNodeScale (fun _ : Fin 12 => (1:ℝ)) 2 (fun _ _ => 0) 0 =
    nodeScale (fun _ : Fin 12 => (1:ℝ)) 2 (fun _ _ => 0) 0 := by
  norm_num [appliedNodeScale, nodeScale, feasible, rowSum]
''','false_math'),
      ('sorry_payload',bridge+'''\ntheorem falseWithBridgeHole : (0:ℚ) = 1 := by sorry
#print axioms falseWithBridgeHole
''','sorry_payload'),
      ('extra_axiom_payload',bridge+'''\naxiom injectedBridgeEquality : (0:ℚ) = 1
theorem falseWithBridgeAxiom : (0:ℚ) = 1 := injectedBridgeEquality
#print axioms falseWithBridgeAxiom
''','extra_axiom_payload'),
      ('missing_footprint',bridge.replace('#print axioms Researcher040282.weightStep_factor_lower_of_drive_bounds\n',''),'missing_footprint')]
    print('Fresh dependency builds, then fresh bridge/control sources.',flush=True)
    with tempfile.TemporaryDirectory(prefix='r040282-c003-dependencies-',dir=CACHE) as tmp:
        dependencies=Path(tmp);dep_env=env.copy();dep_env['LEAN_PATH']=str(dependencies)+os.pathsep+env.get('LEAN_PATH','')
        for filename in FILES[:2]:
            name=Path(filename).stem;run,elapsed=compile_one(name,sources[filename],dependencies,dep_env)
            checked=assess(sources[filename],run.returncode,run.stdout)
            builds.append({'module':name,'raw_lean_exit':run.returncode,'seconds':elapsed,**checked})
            assert checked['verified'], 'Dependency proof build failed: '+name
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            controls=list(pool.map(lambda case:compile_case(case,dependencies,env),cases))
    (LOGS/'Candidate.log').unlink(missing_ok=True)
    controls+=exact_controls()+[optimization_control()]
    result={'agent':'Researcher 040282','cycle':3,'compiler_version':version,'mathlib_revision':revision,
        'source_files':{name:hashlib.sha256(text.encode()).hexdigest() for name,text in sources.items()},
        'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'dependency_builds':builds,'controls':controls,'control_count':len(controls),
        'all_controls_passed':all(r['control_passed'] for r in controls),
        'elapsed_seconds':time.perf_counter()-started,
        'scope':'local closed-file proof/exact harness; no independent-seat approval, engine linkage, or integration'}
    (ROOT/'cycle_results.json').write_text(json.dumps(result,indent=2)+'\n')
    for r in controls:print(r['case'],'PASS' if r['control_passed'] else 'GAP',
        'raw_lean_exit='+str(r.get('raw_lean_exit','not applicable')),
        'verified='+str(r.get('verified','not applicable')),flush=True)
    print('All controls passed:',result['all_controls_passed'],flush=True)
    return 0 if result['all_controls_passed'] else 1


if __name__=='__main__':raise SystemExit(main())
