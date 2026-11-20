"""010 complete bounded history/one-step contract plus actual core Lean checks.
No production study, full baseline-equivalence, CLI, intervention or certificate.
Run after separately bootstrapping prescribed disposable compiler, or supply one.
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
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--lean',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True);start=time.perf_counter()
    try:
        manifest=verify(args.source)
        require((args.source/'lean/AIEFProofs/lean-toolchain').read_text().strip()==manifest['lean_toolchain']['toolchain'],
                'Source compiler prescription changed')
        require(args.lean.is_file(),'Compiler missing: setup blocker, never scientific control detection')
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None);workers=[]
        for kind in ('common','wrong_models'):
            for optimized in (False,True):
                name=kind+('_optimized' if optimized else '_normal');directory=args.output/name
                command=[sys.executable]+(['-O'] if optimized else [])+['-B',str(HERE/'check_engine.py'),
                          '--kind',kind,'--source',str(args.source.resolve()),'--output',str(directory.resolve())]
                worker_start=time.perf_counter()
                run=subprocess.run(command,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env,timeout=60)
                (args.output/(name+'.log')).write_text(run.stdout)
                require((directory/'result.json').is_file(),'Worker failed before result (not a falsifier): '+name)
                value=json.loads((directory/'result.json').read_text())
                require(run.returncode==0 and value['optimized_python'] is optimized and value['source_files_unchanged']==1 and value['metadata_files_unchanged']==2,
                        'Actual engine/control worker failed or source changed: '+name)
                if kind=='common':
                    require(value['tests_run']==9 and value['failures']==value['errors']==value['skipped']==0 and
                            value['actual_engine_advances']==value['reference_compared_transitions']==78 and value['source_initializations']==1 and
                            value['dyadic_exact_states']==65 and value['dyadic_exact_stored_coordinates']==260 and
                            value['invalid_exact_delay_configs_rejected_not_semantic_detections']==2 and
                            value['maximum_component_error']<=5e-13 and value['absolute_tolerance']==5e-13 and value['relative_tolerance']==0,
                            'Common suite not equal to preregistered inventory: '+name)
                else:require(value['detected']==11 and value['setup_errors_credited']==0 and value['actual_engine_advances']==0,
                             'Wrong-model inventory incomplete: '+name)
                value['observed_returncode']=run.returncode;value['elapsed_seconds']=time.perf_counter()-worker_start
                workers.append(value);print(name,'return',run.returncode,'preregistered outcomes verified',flush=True)
        for kind in ('common','wrong_models'):
            values=[{k:v for k,v in row.items() if k not in ('elapsed_seconds','optimized_python')} for row in workers if row['kind']==kind]
            require(values[0]==values[1],'Normal/-O non-timing records differ: '+kind)
        save(args.output/'worker_results.json',workers)
        proof_start=time.perf_counter()
        run=subprocess.run([sys.executable,'-B',str(HERE/'check_lean.py'),'--lean',str(args.lean.resolve()),
                            '--output',str((args.output/'proof').resolve())],env=env,text=True,stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,timeout=180)
        (args.output/'proof.log').write_text(run.stdout)
        require(run.returncode==0 and (args.output/'proof/result.json').is_file(),'Formal run blocked/failed; not a falsifier')
        proof=json.loads((args.output/'proof/result.json').read_text())
        require(proof['all_preregistered_formal_conditions_met'] and proof['named_declarations_compiled']==3 and
                proof['formal_controls']==8 and proof['setup_errors_credited']==0,'Formal acceptance incomplete')
        common=next(row for row in workers if row['kind']=='common')
        science={'tested_main':manifest['commit'],'source_contract_methods_each_mode':9,'source_passes_each_mode':9,
                 'source_failures_errors_skips_each_mode':[0,0,0],'actual_advances_each_common_mode':78,
                 'initializer_calls_each_common_mode':1,'nine_one_step_cases_each_mode':9,
                 'dyadic_transitions_each_mode':60,'dyadic_exact_states_each_mode':65,'dyadic_exact_stored_coordinates_each_mode':260,
                 'maximum_observed_component_error':common['maximum_component_error'],
                 'absolute_tolerance':5e-13,'relative_tolerance':0.0,'wrong_models_detected_each_mode':11,
                 'invalid_exact_delay_configs_rejected_each_mode_not_semantic_detections':2,
                 'setup_errors_credited_as_detections':0,'normal_optimized_nontiming_results_match':True,
                 'new_named_Lean_declarations_actually_compiled':3,'formal_controls':8,'formal_positive_controls':2,
                 'formal_false_math_controls':3,'formal_compiling_integrity_controls':3,
                 'axiom_footprints':proof['main']['footprints'],'core_Std_only_no_Mathlib':True,
                 'reviewed_public_engine_unchanged':1,'reviewed_metadata_unchanged':2,
                 'actual_engine_import_no_copied_replaced_or_edited_source_functions':True,
                 'no_source_repair_or_failing_before_claim':True,'all_preregistered_acceptance_conditions_met':True}
        record={'science':science,'environment':{'python':sys.version,'numpy':np.__version__,'compiler':proof['compiler_version']},
                'elapsed_seconds':time.perf_counter()-start,'formal_elapsed_seconds':time.perf_counter()-proof_start,
                'scope':'Generic reachable value-buffer theorem + finite non-shuffled scalar-reference primitive agreement. NOT a Lean proof of Python, floating trigonometry, whole coupled map, full baseline-equivalence, production study, stability/locking, certificate, installation or independent approval.'}
        verify(args.source);save(args.output/'cycle_results.json',record);print(json.dumps(record,indent=2));return 0
    except Exception as error:
        save(args.output/'failure.json',{'type':type(error).__name__,'message':str(error),'semantic_negative_detection_credited':False});raise


if __name__=='__main__':raise SystemExit(main())
