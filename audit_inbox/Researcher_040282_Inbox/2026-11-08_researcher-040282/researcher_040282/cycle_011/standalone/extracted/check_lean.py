"""Compile owned phase bridge + reused history with targeted prescribed Mathlib.
Eight closed-file controls; imports/timeouts/setup never semantic detections.
This fixed-owned-source integrity policy is NOT a general Lean sandbox/parser.
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
NAMES={'Researcher040282.Phase.phasor_wrap','Researcher040282.Phase.delayed_input_step',
       'Researcher040282.Phase.delayed_input_chord_bound'}
DEPENDENCIES={'Researcher040282.Delay.historyTrace_index','Researcher040282.Delay.historyTrace_oldest',
              'Researcher040282.Delay.historyTrace_newest'}

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


CONTROL_HEADER='''import PhaseIncrement
open Researcher040282.Phase
noncomputable def controlX0 (_ : Unit) : ℝ := 0
noncomputable def controlOmega (_ : Unit) : ℝ := 0
noncomputable def controlU (n : ℕ) (_ : Unit) : ℝ := if n = 0 then Real.pi / 2 else Real.pi
'''
Z='inputPhasor 1 controlX0 controlU controlOmega 1'
STARTUP='''  have h0 : inputPhasor 1 controlX0 controlU controlOmega 1 0 () () = 1 := by
    simp [inputPhasor, Researcher040282.Delay.historyTrace, phaseTrace, controlX0, controlOmega, phasor]
  have hd : delayedIncrement 1 controlU 0 () = 0 := by simp [delayedIncrement]
  have hi : phasor (controlU 0 ()) = Complex.I := by simp [controlU, phasor]
  have h := delayed_input_step 1 controlX0 controlU controlOmega 1 0 () ()
  rw [h0, hd, sub_zero, one_mul, hi] at h
  exact h
'''
LIVE='''  have hs : inputPhasor 1 controlX0 controlU controlOmega 1 1 () () = Complex.I := by
'''+''.join('  '+line+'\n' for line in STARTUP.splitlines())+'''  have hi : phasor (controlU 1 () - delayedIncrement 1 controlU 1 ()) = Complex.I := by
    have hd : controlU 1 () - delayedIncrement 1 controlU 1 () = Real.pi / 2 := by
      dsimp [controlU, delayedIncrement]
      ring
    rw [hd]
    simp [phasor]
  have h := delayed_input_step 1 controlX0 controlU controlOmega 1 1 () ()
  rw [hs, hi, Complex.I_mul_I] at h
  exact h
'''


def indent(text):return ''.join('  '+line+'\n' for line in text.splitlines())


def controls():
    startup=CONTROL_HEADER+'theorem controlStartup : '+Z+' 1 () () = Complex.I := by\n'+STARTUP+'#print axioms controlStartup\n'
    live=CONTROL_HEADER+'theorem controlLive : '+Z+' 2 () () = -1 := by\n'+LIVE+'#print axioms controlLive\n'
    no_wrap=CONTROL_HEADER+'''example : wrapPhase (2 * Real.pi) = 2 * Real.pi := by
  norm_num [wrapPhase, Real.pi_ne_zero]
'''
    early=CONTROL_HEADER+'example : '+Z+' 1 () () = '+Z+' 0 () () * phasor (controlU 0 () - controlU 0 ()) := by\n'+\
        '  have hs : '+Z+' 1 () () = Complex.I := by\n'+indent(STARTUP)+\
        '''  rw [hs]
  norm_num [inputPhasor, Researcher040282.Delay.historyTrace, phaseTrace, controlX0, controlOmega, phasor, Complex.ext_iff]
'''
    wrong_age=CONTROL_HEADER+'example : '+Z+' 2 () () = '+Z+' 1 () () * phasor (controlU 1 () - controlU 1 ()) := by\n'+\
        '  have hs : '+Z+' 1 () () = Complex.I := by\n'+indent(STARTUP)+\
        '  have hl : '+Z+' 2 () () = -1 := by\n'+indent(LIVE)+'''  rw [hl, hs]
  norm_num [phasor, Complex.ext_iff]
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
    return (('positive_startup_nonzero','positive',startup,None),('positive_live_nonzero','positive',live,None),
            ('false_no_wrap','false_math',no_wrap,None),('false_startup_delayed_increment','false_math',early,None),
            ('false_current_instead_of_aged','false_math',wrong_age,None),
            ('compiling_sorry','integrity',sorry,'forbidden_source:sorry'),
            ('compiling_extra_axiom','integrity',axiom,'unapproved_axiom_footprint'),
            ('omitted_axiom_print','integrity',omitted,'axiom_print_coverage'))


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


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--lean',type=Path,required=True)
    parser.add_argument('--mathlib',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    try:
        compiler=args.lean.resolve();mathlib=args.mathlib.resolve();env,version,revision=proof_environment(compiler,mathlib)
        sources=args.output/'compiled_sources';sources.mkdir(exist_ok=True);logs=args.output/'compiler_logs';logs.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='r040282-011-lean-') as temporary:
            work=Path(temporary);env['LEAN_PATH']=str(work)+os.pathsep+env['LEAN_PATH']
            def compile_one(name,text,produce=False):
                filename=name+'.lean';(work/filename).write_text(text);(sources/filename).write_text(text)
                command=[str(compiler),'--root='+str(work)]+(['-o',str(work/(name+'.olean'))] if produce else [])+[filename]
                run=subprocess.run(command,cwd=work,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
                (logs/(name+'.log')).write_text(run.stdout)
                if re.search(r'unknown module|object file .* does not exist|failed to import|cannot open shared object|unknown namespace|unknown identifier|unknown constant|unknown tactic|failed to synthesize|maximum.*(?:recursion|heartbeats)|deterministic timeout|unexpected token|invalid field',run.stdout,re.I):
                    raise RuntimeError('Import/parse/elaboration/runtime blocker, never mathematical detection: '+name)
                return run,assess(text,run.stdout,run.returncode)
            _,dependency=compile_one('HistoryBuffer',(HERE/'HistoryBuffer.lean').read_text(),True)
            require(dependency['accepted'] and set(dependency['footprints'])==DEPENDENCIES and len(dependency['named_declarations'])==3,'Reused history dependency failed')
            _,main_policy=compile_one('PhaseIncrement',(HERE/'PhaseIncrement.lean').read_text(),True)
            require(main_policy['accepted'] and set(main_policy['footprints'])==NAMES and len(main_policy['named_declarations'])==3,
                    'Main theorem acceptance failed: '+json.dumps(main_policy))
            def evaluate(item):
                name,kind,text,intended=item;run,policy=compile_one(name,text)
                if kind=='positive':require(run.returncode==0 and policy['accepted'],'Nonzero positive rejected: '+name)
                elif kind=='false_math':
                    require(run.returncode!=0 and not policy['accepted'] and re.search(r'unsolved goals',run.stdout,re.I) and
                            re.search(r'⊢\s*False',run.stdout),'False math witness did not reduce to explicit False: '+name)
                else:require(run.returncode==0 and not policy['accepted'] and intended in policy['reasons'],'Integrity payload wrong rejection mechanism: '+name)
                return {'control':name,'kind':kind,'expected_mechanism':intended,'expected_outcome_observed':True,'policy':policy,'setup_errors_credited':0}
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:records=list(pool.map(evaluate,controls()))
        require(len(records)==8,'Formal control inventory incomplete')
        value={'compiler_version':version,'mathlib_revision':revision,'Mathlib_used':True,'dependency':dependency,'main':main_policy,
               'new_named_declarations_compiled':3,'reused_named_history_declarations_recompiled_not_new_labels':3,'formal_controls':8,
               'positive_controls_accepted':2,'false_math_witnesses_rejected_by_compiler':3,'compiling_integrity_payloads_rejected_by_policy':3,
               'controls':records,'setup_errors_credited':0,'all_preregistered_formal_conditions_met':True,
               'scope':'Exact-real floor modulo/complex input identity and signed-increment chord bound, not Python/float FFI, full coupled dynamics or locking; fixed-file policy not general sandbox'}
        save(args.output/'result.json',value);print(json.dumps(value,indent=2));return 0
    except Exception as problem:
        save(args.output/'failure.json',{'type':type(problem).__name__,'message':str(problem),'semantic_negative_detection_credited':False});raise

if __name__=='__main__':raise SystemExit(main())
