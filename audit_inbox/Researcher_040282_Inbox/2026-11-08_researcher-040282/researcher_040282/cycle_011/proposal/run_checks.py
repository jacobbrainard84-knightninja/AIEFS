"""011 bounded phase-input contract: full engine normal/-O + actual Lean proof.
Prerequisite separate disposable compiler/targeted Mathlib setup. No production
study, full baseline, shuffle/intervention, CLI/certificate or frozen-file edit.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
from load_reviewed import verify

HERE=Path(__file__).resolve().parent

def require(condition,message):
    if not condition:raise RuntimeError(message)

def save(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--lean',type=Path,required=True);p.add_argument('--mathlib',type=Path,required=True);args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=True);start=time.perf_counter()
    try:
        manifest=verify(args.source)
        require((args.source/'lean/AIEFProofs/lean-toolchain').read_text().strip()==manifest['lean_toolchain']['toolchain'],'Source compiler prescription mismatch')
        lake=json.loads((args.source/'lean/AIEFProofs/lake-manifest.json').read_text());mathlib=next(row for row in lake['packages'] if row['name']=='mathlib')
        require(mathlib['rev']==manifest['mathlib']['revision'],'Source Mathlib prescription mismatch')
        require(args.lean.is_file() and args.mathlib.is_dir(),'Compiler/dependency setup blocker')
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None);workers=[]
        for kind in ('common','wrong_models'):
            for optimized in (False,True):
                name=kind+('_optimized' if optimized else '_normal');directory=args.output/name;begin=time.perf_counter()
                command=[sys.executable]+(['-O'] if optimized else [])+['-B',str(HERE/'check_engine.py'),'--kind',kind,
                          '--source',str(args.source.resolve()),'--output',str(directory.resolve())]
                run=subprocess.run(command,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env,timeout=90)
                (args.output/(name+'.log')).write_text(run.stdout)
                require((directory/'result.json').is_file(),'Worker failed before result, not a falsifier: '+name)
                value=json.loads((directory/'result.json').read_text())
                require(run.returncode==0 and value['optimized_python'] is optimized and value['source_files_unchanged']==1 and value['metadata_files_unchanged']==3,
                        'Source/control worker failed or dependency changed: '+name)
                if kind=='common':
                    require(value['tests_run']==9 and value['failures']==value['errors']==value['skipped']==0 and value['actual_engine_advances']==56 and
                            value['source_initializations']==0 and value['source_cases']==7 and value['input_complex_coordinates']==496 and
                            value['adjacent_complex_coordinates']==434 and value['age_and_chord_stats']['startup_coordinates']==157 and
                            value['age_and_chord_stats']['first_live_coordinates']==62 and value['age_and_chord_stats']['later_live_coordinates']==215 and
                            value['maximum_component_error']<=5e-13 and value['maximum_ratio_component_error']<=5e-13 and
                            value['absolute_tolerance']==5e-13 and value['relative_tolerance']==0,'Common inventory/acceptance mismatch: '+name)
                else:require(value['detected']==10 and value['setup_errors_credited']==0 and value['actual_engine_advances']==0 and
                             not value['actual_engine_imported'],'Wrong-model inventory/mechanism mismatch: '+name)
                value['observed_returncode']=run.returncode;value['elapsed_seconds']=time.perf_counter()-begin;workers.append(value)
                print(name,'return0 / preregistered outcomes verified',flush=True)
        for kind in ('common','wrong_models'):
            values=[{k:v for k,v in row.items() if k not in ('elapsed_seconds','optimized_python')} for row in workers if row['kind']==kind]
            require(values[0]==values[1],'Normal/-O non-timing records differ: '+kind)
        save(args.output/'worker_results.json',workers);proof_start=time.perf_counter()
        run=subprocess.run([sys.executable,'-B',str(HERE/'check_lean.py'),'--lean',str(args.lean.resolve()),'--mathlib',str(args.mathlib.resolve()),
                            '--output',str((args.output/'proof').resolve())],env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=600)
        (args.output/'proof.log').write_text(run.stdout)
        require(run.returncode==0 and (args.output/'proof/result.json').is_file(),'Formal proof/control run blocked, never detection')
        proof=json.loads((args.output/'proof/result.json').read_text())
        require(proof['all_preregistered_formal_conditions_met'] and proof['new_named_declarations_compiled']==3 and
                proof['reused_named_history_declarations_recompiled_not_new_labels']==3 and proof['formal_controls']==8 and proof['setup_errors_credited']==0,
                'Incomplete formal acceptance')
        common=next(row for row in workers if row['kind']=='common')
        science={'tested_main':manifest['commit'],'source_contract_methods_each_mode':9,'source_passes_each_mode':9,'source_failures_errors_skips_each_mode':[0,0,0],
                 'actual_advances_each_common_mode':56,'initializer_calls_each_common_mode':0,'synthetic_traces_each_mode':7,
                 'complex_input_coordinates_each_mode':496,'adjacent_complex_coordinates_each_mode':434,'startup_coordinates_each_mode':157,
                 'live_coordinates_each_mode':277,'first_live_coordinates_each_mode':62,'later_live_coordinates_each_mode':215,
                 'maximum_observed_component_error':common['maximum_component_error'],'maximum_ratio_component_error':common['maximum_ratio_component_error'],
                 'age_and_chord_stats':common['age_and_chord_stats'],'winding_stats':common['winding_stats'],
                 'absolute_tolerance':5e-13,'relative_tolerance':0.0,'wrong_models_detected_each_mode':10,'setup_errors_credited_as_detections':0,
                 'normal_optimized_nontiming_results_match':True,'new_named_Lean_declarations_actually_compiled':3,
                 'reused_history_declarations_recompiled_not_new_labels':3,'formal_controls':8,'formal_positive_controls':2,'formal_false_math_controls':3,
                 'formal_compiling_integrity_controls':3,'axiom_footprints':proof['main']['footprints'],'targeted_Mathlib_used':True,
                 'reviewed_public_engine_unchanged':1,'reviewed_metadata_unchanged':3,'actual_engine_import_no_copied_replaced_or_edited_source_functions':True,
                 'no_source_repair_or_failing_before_claim':True,'all_preregistered_acceptance_conditions_met':True}
        record={'science':science,'environment':{'python':sys.version,'numpy':np.__version__,'compiler':proof['compiler_version'],'mathlib_revision':proof['mathlib_revision']},
                'elapsed_seconds':time.perf_counter()-start,'formal_elapsed_seconds':time.perf_counter()-proof_start,
                'scope':'Exact-real modulo-safe startup-aware delayed input/chord theorem plus finite intact-engine correspondence. Not a Lean proof of Python/float FFI, full coupled map/locking, production baseline, certificate, integration or independent approval.'}
        verify(args.source);save(args.output/'cycle_results.json',record);print(json.dumps(record,indent=2));return 0
    except Exception as problem:
        save(args.output/'failure.json',{'type':type(problem).__name__,'message':str(problem),'semantic_negative_detection_credited':False});raise

if __name__=='__main__':raise SystemExit(main())
