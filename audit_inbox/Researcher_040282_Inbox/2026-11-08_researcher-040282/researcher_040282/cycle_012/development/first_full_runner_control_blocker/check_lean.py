"""Compile012 causal EMA tracker +28explicit reused named dependencies.
Eight strict mathematical/integrity controls; setup/identifier/runtime/timeout
failures NEVER detections. Closed-owned-file policy, NOT general Lean sandbox.
"""
import argparse
import concurrent.futures
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

HERE=Path(__file__).resolve().parent
ALLOWED={'propext','Classical.choice','Quot.sound'}
NAMES={'Researcher040282.Tracking.tracking_error_step','Researcher040282.Tracking.tracking_error_budget','Researcher040282.Tracking.delayed_phase_tracking_budget'}
DEPENDENCY_COUNTS={'HistoryBuffer':3,'PhaseIncrement':3,'CoherenceEMA':22}

def require(condition,message):
    if not condition:raise RuntimeError(message)


def save(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def source_without_comments(text):
    # Fixed owned files have no nested block comments or command-bearing strings.
    return re.sub(r'--[^\n]*','',re.sub(r'/-.*?-/', '', text,flags=re.S))


def assess(text,output,returncode):
    source=source_without_comments(text);reasons=[]
    declarations=re.findall(r'^\s*(?:theorem|lemma)\s+([\w.]+)',source,re.M)
    requests=re.findall(r'^\s*#print\s+axioms\s+([\w.]+)\s*$',source,re.M)
    footprints={};seen=[]
    for name,body in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",output):
        seen.append(name);footprints[name]=sorted(value.strip() for value in body.split(',') if value.strip())
    for name in re.findall(r"'([^']+)' does not depend on any axioms",output):
        seen.append(name);footprints[name]=[]
    if returncode!=0:reasons.append('compiler_nonzero')
    if re.search(r'\bwarning\s*:',output,re.I):reasons.append('compiler_warning')
    if re.search(r'\berror\s*:',output,re.I):reasons.append('compiler_error')
    forbidden=sorted(set(re.findall(r'\b(?:sorry|admit|axiom|native_decide|unsafe|run_tac|elab|macro|initialize)\b',source)))
    if forbidden:reasons.append('forbidden_source:'+','.join(forbidden))
    if any(line.lstrip().startswith('#') and not line.lstrip().startswith('#print axioms ') for line in source.splitlines()):
        reasons.append('unexpected_metacommand')
    declaration_bases=sorted(name.rsplit('.',1)[-1] for name in declarations)
    request_bases=sorted(name.rsplit('.',1)[-1] for name in requests)
    if (not declarations or declaration_bases!=request_bases or len(set(requests))!=len(requests)
        or set(requests)!=set(footprints) or len(seen)!=len(requests)):
        reasons.append('axiom_print_coverage')
    bad={name:sorted(set(values)-ALLOWED) for name,values in footprints.items() if set(values)-ALLOWED}
    if bad:reasons.append('unapproved_axiom_footprint')
    return {'accepted':not reasons,'reasons':reasons,'named_declarations':declarations,
            'requested_axiom_prints':requests,'footprints':footprints,'unapproved_axioms':bad,
            'raw_compiler_returncode':returncode}


def proof_environment(compiler,mathlib):
    manifest=json.loads((HERE/'source_modules.json').read_text());cache=mathlib.parent
    require(compiler.is_file() and (compiler.parent/'lake').is_file() and (mathlib/'lakefile.lean').is_file(),'Compiler/Mathlib setup blocker')
    revision=subprocess.check_output(['git','-C',str(mathlib),'rev-parse','HEAD'],text=True,timeout=30).strip()
    require(revision==manifest['mathlib']['revision'],'Wrong prescribed Mathlib: setup blocker')
    version=subprocess.check_output([str(compiler),'--version'],text=True,timeout=20).strip()
    require('version '+manifest['lean_toolchain']['toolchain'].rsplit(':v',1)[1]+',' in version,'Wrong prescribed compiler')
    env=dict(os.environ,PATH=str(compiler.parent)+os.pathsep+os.environ.get('PATH',''),PYTHONDONTWRITEBYTECODE='1',GIT_TERMINAL_PROMPT='0',
             XDG_CACHE_HOME=str(cache/'xdg'),MATHLIB_CACHE_DIR=str(cache/'mathlib-downloads'),LAKE_HOME=str(cache/'lake-home'),ELAN_HOME=str(cache/'elan-home'))
    env['LEAN_PATH']=subprocess.check_output([str(compiler.parent/'lake'),'env','printenv','LEAN_PATH'],cwd=mathlib,env=env,text=True,timeout=60).strip()
    return env,version,revision


CONTROL_HEADER='''import EMATracking
open Researcher040282.EMA Researcher040282.Tracking
noncomputable def controlZ (n : ℕ) : ℂ := if n = 0 then 1 else -1
noncomputable def controlLateZ (n : ℕ) : ℂ := if n < 2 then 1 else -1
'''


def controls():
    zero=CONTROL_HEADER+'''theorem controlAlphaZero : emaTrajectory 0 1 controlZ 1 - controlZ 1 = 2 := by
  norm_num [emaTrajectory, emaStep, controlZ]
#print axioms controlAlphaZero
'''
    one=CONTROL_HEADER+'''theorem controlAlphaOne : emaTrajectory 1 1 controlZ 3 - controlZ 3 = 2 := by
  norm_num [emaTrajectory, emaStep, controlZ]
#print axioms controlAlphaOne
'''
    beta=CONTROL_HEADER+'''example : emaTrajectory (1/2) 1 controlZ 1 - controlZ 1 = 1 := by
  norm_num [emaTrajectory, emaStep, controlZ, Complex.ext_iff]
'''
    reversed_weights=CONTROL_HEADER+'''example : ‖emaTrajectory (1/2) 1 controlLateZ 2 - controlLateZ 2‖ ≤ (1 : ℝ) := by
  have h : emaTrajectory (1/2) 1 controlLateZ 2 - controlLateZ 2 = (2 : ℂ) := by
    norm_num [emaTrajectory, emaStep, controlLateZ]
  rw [h, Complex.norm_of_nonneg (by norm_num : (0 : ℝ) ≤ 2)]
  norm_num
'''
    negative=CONTROL_HEADER+'''example : ‖emaTrajectory (-1) 0 (fun _ => 1) 1 - 1‖ ≤ (-1 : ℝ) := by
  norm_num [emaTrajectory, emaStep]
'''
    sorry=CONTROL_HEADER+'''theorem controlSorry : False := by sorry
#print axioms controlSorry
'''
    axiom=CONTROL_HEADER+'''axiom injectedFalse : False
theorem controlExtraAxiom : False := injectedFalse
#print axioms controlExtraAxiom
'''
    omitted=CONTROL_HEADER+'''theorem controlNoPrint : True := by trivial
'''
    return (('positive_alpha0_nonzero','positive',zero,None),('positive_alpha1_nonzero','positive',one,None),
            ('false_beta_scaled_drift','false_math',beta,None),('false_reverse_weights','false_math',reversed_weights,None),
            ('false_drop_nonnegative_alpha','false_math',negative,None),('compiling_sorry','integrity',sorry,'forbidden_source:sorry'),
            ('compiling_extra_axiom','integrity',axiom,'unapproved_axiom_footprint'),('omitted_axiom_print','integrity',omitted,'axiom_print_coverage'))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--lean',type=Path,required=True);parser.add_argument('--mathlib',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    try:
        compiler=args.lean.resolve();env,version,revision=proof_environment(compiler,args.mathlib.resolve())
        sources=args.output/'compiled_sources';logs=args.output/'compiler_logs';sources.mkdir(exist_ok=True);logs.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='r040282-012-lean-') as temporary:
            work=Path(temporary);env['LEAN_PATH']=str(work)+os.pathsep+env['LEAN_PATH']
            def compile_one(name,text,produce=False):
                filename=name+'.lean';(work/filename).write_text(text);(sources/filename).write_text(text)
                command=[str(compiler),'--root='+str(work)]+(['-o',str(work/(name+'.olean'))] if produce else [])+[filename]
                run=subprocess.run(command,cwd=work,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=240)
                (logs/(name+'.log')).write_text(run.stdout)
                if re.search(r'unknown module|object file .* does not exist|failed to import|cannot open shared object|unknown namespace|unknown identifier|unknown constant|unknown tactic|failed to synthesize|maximum.*(?:recursion|heartbeats)|deterministic timeout|unexpected token|invalid field',run.stdout,re.I):
                    raise RuntimeError('Setup/import/parse/elaboration/runtime blocker, never mathematical detection: '+name)
                return run,assess(text,run.stdout,run.returncode)
            dependencies=[]
            for name,count in DEPENDENCY_COUNTS.items():
                text=(HERE/(name+'.lean')).read_text();_,policy=compile_one(name,text,True)
                expected=set(re.findall(r'^#print axioms ([\w.]+)',text,re.M))
                require(policy['accepted'] and len(policy['named_declarations'])==count and len(expected)==count and set(policy['footprints'])==expected,'Reused dependency rejected: '+name)
                dependencies.append({'module':name,'reused_named_claims_not_new_labels':count,'policy':policy})
            _,main_policy=compile_one('EMATracking',(HERE/'EMATracking.lean').read_text(),True)
            require(main_policy['accepted'] and len(main_policy['named_declarations'])==3 and set(main_policy['footprints'])==NAMES,'New main theorem acceptance failed: '+json.dumps(main_policy))
            def evaluate(item):
                name,kind,text,intended=item;run,policy=compile_one(name,text)
                if kind=='positive':require(run.returncode==0 and policy['accepted'],'Nonzero endpoint positive failed: '+name)
                elif kind=='false_math':require(run.returncode!=0 and not policy['accepted'] and re.search('unsolved goals',run.stdout,re.I) and re.search(r'⊢\s*False',run.stdout),'False math not explicit mathematical False: '+name)
                else:require(run.returncode==0 and not policy['accepted'] and intended in policy['reasons'],'Compiling payload wrong refusal: '+name)
                return {'control':name,'kind':kind,'expected_mechanism':intended,'expected_outcome_observed':True,'policy':policy,'setup_errors_credited':0}
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:records=list(pool.map(evaluate,controls()))
        require(len(records)==8,'Formal inventory incomplete')
        value={'compiler_version':version,'mathlib_revision':revision,'Mathlib_used':True,'dependencies':dependencies,'main':main_policy,
               'new_named_declarations_compiled':3,'reused_named_declarations_recompiled_not_new_labels':28,'formal_controls':8,'positive_controls_accepted':2,
               'false_math_witnesses_rejected_by_compiler':3,'compiling_integrity_payloads_rejected_by_policy':3,'controls':records,
               'setup_errors_credited':0,'all_preregistered_formal_conditions_met':True,
               'scope':'Exact-real causal moving-input EMA error and finite weighted budget, composed with prior phase/history; not floating FFI/full coupled map/locking; alpha>=0finite, no hidden alpha<1 assumption; fixed-owned-source policy not generic sandbox'}
        save(args.output/'result.json',value);print(json.dumps(value,indent=2));return 0
    except Exception as problem:
        save(args.output/'failure.json',{'type':type(problem).__name__,'message':str(problem),'semantic_negative_detection_credited':False});raise

if __name__=='__main__':raise SystemExit(main())
