"""Fresh complex-EMA/drive builds and bounded adversarial controls.

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


def compile_case(item,dependencies,env):
    name,source,kind=item
    with tempfile.TemporaryDirectory(prefix='r040282-c004-'+name+'-',dir=CACHE) as tmp:
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


# Independent exact Gaussian-rational arithmetic, not NumPy/cmath or Lean evaluation.
def gadd(z,w):return (z[0]+w[0],z[1]+w[1])
def gsub(z,w):return (z[0]-w[0],z[1]-w[1])
def gscale(a,z):return (a*z[0],a*z[1])
def normsq(z):return z[0]*z[0]+z[1]*z[1]
def step(a,c,z):return gadd(gscale(a,c),gscale(1-a,z))
ZERO=(F(0),F(0));ONE=(F(1),F(0));NEGONE=(F(-1),F(0))
POINTS=[ONE,NEGONE,(F(0),F(1)),(F(0),F(-1)),(F(3,5),F(4,5)),(F(-3,5),F(4,5)),(F(5,13),F(-12,13))]
ALPHAS=[F(0),F(1),F(1,4),F(1,2),F(9,10),F(1,10**6),1-F(1,10**6)]


def exact_controls():
    rng=random.Random(20260904);disk_checks=0;difference_checks=0;fixed_checks=0
    for k in range(64):
        a=ALPHAS[k%len(ALPHAS)]
        c0=gscale(F(rng.randrange(21),20),rng.choice(POINTS));d0=gscale(F(rng.randrange(21),20),rng.choice(POINTS))
        c,d=c0,d0
        for n in range(17):
            assert normsq(c)<=1 and normsq(d)<=1;disk_checks+=2
            assert gsub(c,d)==gscale(a**n,gsub(c0,d0));difference_checks+=1
            assert normsq(gsub(c,d))==a**(2*n)*normsq(gsub(c0,d0))
            if n<16:
                z=rng.choice(POINTS);assert normsq(z)==1
                c,d=step(a,c,z),step(a,d,z)
    for k in range(64):
        a=ALPHAS[k%len(ALPHAS)];z=rng.choice(POINTS)
        c0=gscale(F(rng.randrange(21),20),rng.choice(POINTS));c=c0;zero_path=ZERO
        for n in range(17):
            assert c==gadd(z,gscale(a**n,gsub(c0,z)))
            assert normsq(gsub(c,z))==a**(2*n)*normsq(gsub(c0,z))
            assert normsq(c)<=1 and normsq(zero_path)==(1-a**n)**2;fixed_checks+=1
            if n<16:c,zero_path=step(a,c,z),step(a,zero_path,z)
    matrix_count=0;tight_rows=0;nodes=[1,2,3,6,12]
    for k in range(120):
        n=nodes[k%len(nodes)];eta=rng.choice([F(0),F(1,25),F(1)])
        mu=rng.choice([F(0),F(3,100),F(2)]);gamma=rng.choice([F(3,200),F(1,10),F(1)])
        R=[[F(0) for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for j in range(i):R[i][j]=R[j][i]=F(1) if k%3==0 else F(rng.randrange(21),20)
        # These R are realized by real nonnegative off-diagonal C, with arbitrary
        # disk-valued complex diagonal subsequently masked only by the readout.
        C=[[(R[i][j],F(0)) if i!=j else (F(1,2),F(0)) for j in range(n)] for i in range(n)]
        assert all(normsq(x)<=1 for row in C for x in row)
        observed_R=[[F(0) if i==j else (abs(C[i][j][0])+abs(C[j][i][0]))/2 for j in range(n)] for i in range(n)]
        assert R==observed_R
        u=[[((eta+mu)*R[i][j]-mu)/gamma for j in range(n)] for i in range(n)]
        assert all(-mu/gamma<=x<=eta/gamma for row in u for x in row)
        for i in range(n):
            assert u[i][i]==-mu/gamma
            row=sum((max(F(0),u[i][j]) for j in range(n) if i!=j),F(0))
            assert row<=(n-1)*eta/gamma
            tight_rows+=int(row==(n-1)*eta/gamma)
            assert all(u[i][j]==u[j][i] for j in range(n))
        matrix_count+=1
    assert normsq(step(F(2),ONE,NEGONE))==9
    assert normsq(step(F(-1),ONE,NEGONE))==9
    assert normsq(step(F(1,2),ZERO,(F(4),F(0))))==4
    forced=gsub(step(F(1,2),ZERO,ONE),step(F(1,2),ZERO,NEGONE));assert forced==ONE
    mean_of_norms=F(1);norm_of_mean=F(0);assert mean_of_norms!=norm_of_mean
    complex_diag=step(F(1,2),ZERO,ONE);assert complex_diag==(F(1,2),F(0)) and complex_diag!=ZERO
    retained=ZERO
    for _ in range(16):retained=step(F(1),retained,ONE);assert retained==ZERO
    assert normsq(NEGONE)==1 and step(F(1,2),NEGONE,NEGONE)==NEGONE
    # A coarse global range is not itself the sharp lower-band ON certificate.
    c=F(19,30);eps=F(1,10**12);h=F(3,20000);L=F(8,3);S=11*L
    M=(1-h)*c+h*S;kappa=min(F(1),c/(M+eps));share=kappa*h*L/(1-kappa*(1-h))
    assert 0<kappa<=1 and share<F(3,25)
    return [
        {'case':'exact_shared_input_paths','kind':'positive_exact','control_passed':True,'trajectories':64,'updates_each':16,'disk_checks':disk_checks,'difference_checks':difference_checks},
        {'case':'exact_fixed_input_paths','kind':'positive_exact','control_passed':True,'trajectories':64,'updates_each':16,'closed_form_checks':fixed_checks},
        {'case':'exact_reported_drive_matrices','kind':'positive_exact','control_passed':True,'matrices':matrix_count,'tight_row_bounds':tight_rows,'N_values':nodes,'coarse_default_ON_comparison_point':str(share),'threshold':'3/25','coarse_range_alone_not_ON_certificate':True},
        {'case':'exact_adversarial_witnesses','kind':'exact_counterexample','control_passed':True,'witnesses':{
            'drop_alpha_upper_norm_squared':'9','drop_alpha_lower_norm_squared':'9','drop_input_bound_norm_squared':'4',
            'different_input_nonzero_next_difference':'1','mean_of_norms_vs_norm_of_mean':['1','0'],
            'complex_diagonal_vs_reported_diagonal':['1/2','0'],'alpha_one_retains_initial':'0 for every recurrence step',
            'antiphase_unit_magnitude_vs_cosine':['1','-1']}}]


def optimization_control():
    run=subprocess.run([sys.executable,'-O',str(Path(__file__).resolve()),'--assertions-only'],
        text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=20)
    return {'case':'python_optimization_mode','kind':'policy_negative','control_passed':
        run.returncode==2 and 'assertions must be enabled' in run.stdout,
        'raw_python_exit':run.returncode,'observed_output':run.stdout.strip()}


def cases():
    header='import CoherenceEMA\nopen Researcher040282.EMA\n'
    false=[
      ('false_disk_without_alpha_upper','''example : (emaStep 2 1 (-1)).re ≤ 1 := by
  norm_num [emaStep]
'''),
      ('false_disk_without_alpha_lower','''example : -(emaStep (-1) 1 (-1)).re ≤ 1 := by
  norm_num [emaStep]
'''),
      ('false_disk_without_input_bound','''example : (emaStep (1/2) 0 4).re ≤ 1 := by
  norm_num [emaStep]
'''),
      ('false_unforced_difference','''example : (emaStep (1/2) 0 1 - emaStep (1/2) 0 (-1)).re = 0 := by
  norm_num [emaStep]
'''),
      ('false_complex_average_readout','''example : reportedR (fun i j : Fin 2 => if i=j then 0 else if i=0 then 1 else -1) 0 1 = 0 := by
  norm_num [reportedR]
'''),
      ('false_complex_zero_diagonal','''example : (coherenceUpdate (1/2) (fun _ _ : Fin 1 => 0) (fun _ => 0)
    (fun _ => 0) (fun _ => 0) 1 0 0).re = 0 := by
  norm_num [coherenceUpdate, phaseInput, emaStep]
'''),
      ('false_strict_decay_at_alpha_one','''example : ‖emaTrajectory 1 0 (fun _ => 1) 8 - 1‖ < 1 := by
  norm_num [emaTrajectory, emaStep]
'''),
      ('false_coherence_equals_cosine','''example : reportedR (fun _ _ : Fin 2 => (-1 : ℂ)) 0 1 = (-1 : ℝ) := by
  norm_num [reportedR]
''')]
    result=[(name,header+source,'false_math') for name,source in false]
    result += [
      ('sorry_payload',header+'''theorem falseWithEMAHole : (0 : ℚ) = 1 := by sorry
#print axioms falseWithEMAHole
''','sorry_payload'),
      ('extra_axiom_payload',header+'''axiom injectedEMAEquality : (0 : ℚ) = 1
theorem falseWithEMAAxiom : (0 : ℚ) = 1 := injectedEMAEquality
#print axioms falseWithEMAAxiom
''','extra_axiom_payload'),
      ('missing_footprint',header+'''theorem footprintProbe : (0 : ℚ) = 0 := by norm_num
''','missing_footprint')]
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--exact-only',action='store_true');args=parser.parse_args()
    started=time.perf_counter()
    if args.exact_only:
        controls=exact_controls()+[optimization_control()]
        result={'agent':'Researcher 040282','cycle':4,'scope':'exact finite/policy controls only; no Lean invocation',
            'control_count':len(controls),'all_controls_passed':all(c['control_passed'] for c in controls),'controls':controls}
        (ROOT/'exact_results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
        return 0 if result['all_controls_passed'] else 1
    (ROOT/'cycle_results.json').unlink(missing_ok=True)
    assert LEAN.is_file() and LAKE.is_file() and (MATHLIB/'lakefile.lean').is_file()
    version=subprocess.check_output([str(LEAN),'--version'],cwd=MATHLIB,text=True).strip()
    assert 'version 4.33.1,' in version
    revision=subprocess.check_output(['git','-C',str(MATHLIB),'rev-parse','HEAD'],text=True).strip();assert revision==REVISION
    sources={name:(ROOT/name).read_text() for name in FILES}
    base=os.environ.copy();base['PATH']=str(LEAN.parent)+os.pathsep+base.get('PATH','')
    env=json.loads(subprocess.check_output([str(LAKE),'env','python','-c',
        'import json,os; print(json.dumps(dict(os.environ)))'],cwd=MATHLIB,env=base,text=True))
    CACHE.mkdir(parents=True,exist_ok=True);LOGS.mkdir(exist_ok=True);builds=[];controls=[]
    print('Fresh reused dependency and new component/bridge builds, then isolated controls.',flush=True)
    with tempfile.TemporaryDirectory(prefix='r040282-c004-dependencies-',dir=CACHE) as tmp:
        dependencies=Path(tmp);dep_env=env.copy();dep_env['LEAN_PATH']=str(dependencies)+os.pathsep+env.get('LEAN_PATH','')
        for filename in FILES:
            name=Path(filename).stem;run,seconds=compile_one(name,sources[filename],dependencies,dep_env)
            checked=assess(sources[filename],run.returncode,run.stdout)
            row={'module':name,'raw_lean_exit':run.returncode,'seconds':seconds,**checked}
            if not checked['verified']:print(run.stdout,flush=True);raise RuntimeError('Positive module rejected: '+name)
            if name in ['CoherenceEMA','CoherenceDriveBridge']:
                controls.append({'case':'positive_'+name,'kind':'positive','control_passed':True,**row})
            else:builds.append(row)
            print(name,'PASS','declarations',checked['declaration_count'],flush=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            controls+=list(pool.map(lambda item:compile_case(item,dependencies,env),cases()))
    controls+=exact_controls()+[optimization_control()]
    for c in controls:print(c['case'],'PASS' if c['control_passed'] else 'FAIL','raw_lean_exit='+str(c.get('raw_lean_exit','not applicable')),flush=True)
    result={'agent':'Researcher 040282','cycle':4,'compiler_version':version,'mathlib_revision':revision,
        'source_files':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in sources.items()},
        'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'dependency_builds':builds,'controls':controls,'control_count':len(controls),
        'all_controls_passed':all(c['control_passed'] for c in controls),'elapsed_seconds':time.perf_counter()-started}
    (ROOT/'cycle_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print('All controls passed:',result['all_controls_passed'],flush=True)
    return 0 if result['all_controls_passed'] else 1


if __name__=='__main__':raise SystemExit(main())
