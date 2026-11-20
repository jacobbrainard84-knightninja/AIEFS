"""Compile the owned Std-only history module and eight closed-file controls.
Checks survive Python -O. Compiler/import/timeouts are blockers, not falsifiers.
This is a reproducibility/integrity harness for these fixed sources, NOT a secure
parser/sandbox for arbitrary Lean submissions or untrusted compiler plugins.
"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

HERE=Path(__file__).resolve().parent
ALLOWED={'propext','Classical.choice','Quot.sound'}
NAMES={'Researcher040282.Delay.historyTrace_index','Researcher040282.Delay.historyTrace_oldest',
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


def controls():
    header='import HistoryBuffer\nopen Researcher040282.Delay\n\n'
    nonzero=header+'''theorem controlNonzero : historyTrace 2 (fun n : Nat => n) 4 ⟨0, by decide⟩ = 2 := by decide
#print axioms controlNonzero
'''
    zero=header+'''theorem controlAbstractZero : historyTrace 0 (fun n : Nat => 2*n+3) 7 ⟨0, by decide⟩ = 17 := by decide
#print axioms controlAbstractZero
'''
    youngest=header+'''example : historyTrace 2 (fun n : Nat => n) 4 ⟨0, by decide⟩ = 4 := by decide
'''
    extra=header+'''example : historyTrace 2 (fun n : Nat => n) 4 ⟨0, by decide⟩ = 1 := by decide
'''
    append_old=header+'''example : historyTrace 2 (fun n : Nat => n) 4 ⟨2, by decide⟩ = 3 := by decide
'''
    sorry=header+'''theorem controlSorry : False := by sorry
#print axioms controlSorry
'''
    axiom=header+'''axiom injectedFalse : False
theorem controlExtraAxiom : False := injectedFalse
#print axioms controlExtraAxiom
'''
    omitted=header+'''theorem controlNoPrint : True := by trivial
'''
    return (('positive_nonzero','positive',nonzero,None),('positive_abstract_D0','positive',zero,None),
            ('false_youngest_read','false_math',youngest,None),('false_extra_delay','false_math',extra,None),
            ('false_append_old','false_math',append_old,None),('compiling_sorry','integrity',sorry,'forbidden_source:sorry'),
            ('compiling_extra_axiom','integrity',axiom,'unapproved_axiom_footprint'),
            ('omitted_axiom_print','integrity',omitted,'axiom_print_coverage'))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--lean',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    try:
        compiler=args.lean.resolve();require(compiler.is_file(),'Core compiler missing: setup blocker')
        version=subprocess.check_output([str(compiler),'--version'],text=True,timeout=20).strip()
        manifest=json.loads((HERE/'source_modules.json').read_text())
        require('version '+manifest['lean_toolchain']['toolchain'].rsplit(':v',1)[1]+',' in version,'Wrong compiler: setup blocker')
        sources=args.output/'compiled_sources';sources.mkdir(exist_ok=True);logs=args.output/'compiler_logs';logs.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='r040282-010-lean-') as temporary:
            work=Path(temporary);env=dict(os.environ,LEAN_PATH=str(work))
            def compile_one(name,text,produce_object=False):
                filename=name+'.lean';(work/filename).write_text(text);(sources/filename).write_text(text)
                command=[str(compiler),'--root='+str(work)]+(['-o',str(work/'HistoryBuffer.olean')] if produce_object else [])+[filename]
                run=subprocess.run(command,cwd=work,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
                (logs/(name+'.log')).write_text(run.stdout)
                if re.search(r'unknown module|object file .* does not exist|failed to import|cannot open shared object|unknown namespace',run.stdout,re.I):
                    raise RuntimeError('Import/runtime blocker, never a successful control: '+name)
                return run,assess(text,run.stdout,run.returncode)
            main_run,main_policy=compile_one('HistoryBuffer',(HERE/'HistoryBuffer.lean').read_text(),True)
            require(main_policy['accepted'] and set(main_policy['footprints'])==NAMES and len(main_policy['named_declarations'])==3,
                    'Main theorem compilation/footprint acceptance failed: '+json.dumps(main_policy))
            records=[]
            for name,kind,text,intended in controls():
                run,policy=compile_one(name,text)
                if kind=='positive':require(run.returncode==0 and policy['accepted'],'Positive control rejected: '+name)
                elif kind=='false_math':
                    require(run.returncode!=0 and not policy['accepted'] and
                            re.search(r"decide.*(?:false|failed)|proposition.*false",run.stdout,re.I|re.S),
                            'False theorem did not fail for explicit mathematical witness: '+name)
                else:
                    require(run.returncode==0 and not policy['accepted'] and intended in policy['reasons'],
                            'Compiling integrity payload not rejected for intended policy: '+name)
                records.append({'control':name,'kind':kind,'expected_mechanism':intended,
                                'expected_outcome_observed':True,'policy':policy,'setup_errors_credited':0})
        require(len(records)==8,'Formal control inventory incomplete')
        value={'compiler_version':version,'imports':['Std'],'Mathlib_used':False,'main':main_policy,
               'named_declarations_compiled':3,'formal_controls':8,'positive_controls_accepted':2,
               'false_math_witnesses_rejected_by_compiler':3,'compiling_integrity_payloads_rejected_by_policy':3,
               'controls':records,'setup_errors_credited':0,'all_preregistered_formal_conditions_met':True,
               'scope':'Universal value-history trace only; no Python/float FFI or coupled dynamics proof; closed-file policy not an arbitrary-source sandbox'}
        save(args.output/'result.json',value);print(json.dumps(value,indent=2));return 0
    except Exception as error:
        save(args.output/'failure.json',{'type':type(error).__name__,'message':str(error),'semantic_negative_detection_credited':False});raise


if __name__=='__main__':raise SystemExit(main())
