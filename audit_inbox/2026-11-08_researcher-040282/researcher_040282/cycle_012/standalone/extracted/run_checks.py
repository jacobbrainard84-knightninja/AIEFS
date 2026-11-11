"""012 causal moving-input EMA contract, actual full engine normal/-O + Lean.
Deliberate external setup first; no production/full baseline/S01/CLI/certificate.
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
    p.add_argument('--lean',type=Path,required=True);p.add_argument('--mathlib',type=Path,required=True);args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True);start=time.perf_counter()
    try:
        manifest=verify(args.source)
        require((args.source/'lean/AIEFProofs/lean-toolchain').read_text().strip()==manifest['lean_toolchain']['toolchain'],'Compiler prescription mismatch')
        lake=json.loads((args.source/'lean/AIEFProofs/lake-manifest.json').read_text());ml=next(x for x in lake['packages'] if x['name']=='mathlib')
        require(ml['rev']==manifest['mathlib']['revision'] and args.lean.is_file() and args.mathlib.is_dir(),'Dependency/available setup mismatch')
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None);workers=[]
        for kind in ('common','wrong_models'):
            for optimized in (False,True):
                name=kind+('_optimized' if optimized else '_normal');directory=args.output/name;begin=time.perf_counter()
                command=[sys.executable]+(['-O'] if optimized else [])+['-B',str(HERE/'check_engine.py'),'--kind',kind,'--source',str(args.source.resolve()),'--output',str(directory.resolve())]
                run=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,env=env,timeout=90);(args.output/(name+'.log')).write_text(run.stdout)
                require((directory/'result.json').is_file(),'Worker failed before result, never falsifier: '+name);value=json.loads((directory/'result.json').read_text())
                require(run.returncode==0 and value['optimized_python'] is optimized and value['source_files_unchanged']==1 and value['metadata_files_unchanged']==3,'Worker/source failure: '+name)
                if kind=='common':
                    s=value['tracking_stats']
                    require(value['tests_run']==9 and value['failures']==value['errors']==value['skipped']==0 and value['actual_engine_advances']==60 and
                        value['source_initializations']==0 and value['source_cases']==6 and value['precomputed_tracking_cells']==370 and s['tracking_coordinates']==370 and
                        s['adjacent_causal_coordinates']==333 and s['consumed_input_coordinates']==370 and s['startup_adjacent_coordinates']==115 and s['live_adjacent_coordinates']==218 and
                        s['first_live_coordinates']==37 and s['reported_R_offdiag_bound_coordinates']==240 and s['reported_R_exact_diag_coordinates']==130 and
                        s['decoded_C_innovation_coordinates']==360 and s['alpha1_formula_only_input_coordinates']==10 and s['beta0_divisions']==0 and
                        s['alpha1_C_exactly_constant'] and s['alpha1_not_strict_contraction'] and value['maximum_component_error']<=5e-13 and
                        s['maximum_causal_component_residual']<=5e-13 and s['maximum_unroll_component_residual']<=5e-13 and s['maximum_consumed_component_residual']<=5e-13 and
                        value['absolute_tolerance']==5e-13 and value['relative_tolerance']==0,'Common acceptance/count mismatch: '+name)
                else:require(value['detected']==10 and value['setup_errors_credited']==0 and value['actual_engine_advances']==0 and not value['actual_engine_imported'],'Wrong-model acceptance mismatch')
                value['observed_returncode']=run.returncode;value['elapsed_seconds']=time.perf_counter()-begin;workers.append(value);print(name,'return0 / observed preregistered conditions',flush=True)
        for kind in ('common','wrong_models'):
            pair=[{k:v for k,v in row.items() if k not in ('elapsed_seconds','optimized_python')} for row in workers if row['kind']==kind];require(pair[0]==pair[1],'Normal/-O non-timing mismatch: '+kind)
        save(args.output/'worker_results.json',workers);begin=time.perf_counter()
        run=subprocess.run([sys.executable,'-B',str(HERE/'check_lean.py'),'--lean',str(args.lean.resolve()),'--mathlib',str(args.mathlib.resolve()),'--output',str((args.output/'proof').resolve())],
            stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,env=env,timeout=900);(args.output/'proof.log').write_text(run.stdout)
        require(run.returncode==0 and (args.output/'proof/result.json').is_file(),'Formal check/control blocker, never detection');proof=json.loads((args.output/'proof/result.json').read_text())
        require(proof['all_preregistered_formal_conditions_met'] and proof['new_named_declarations_compiled']==3 and proof['reused_named_declarations_recompiled_not_new_labels']==28 and
                proof['formal_controls']==8 and proof['setup_errors_credited']==0,'Formal inventory incomplete')
        common=next(x for x in workers if x['kind']=='common')
        science={'tested_main':manifest['commit'],'source_contract_methods_each_mode':9,'source_passes_each_mode':9,'source_failures_errors_skips_each_mode':[0,0,0],
            'actual_advances_each_common_mode':60,'initializer_calls_each_common_mode':0,'synthetic_traces_each_mode':6,'current_tracking_coordinates_each_mode':370,
            'consumed_input_coordinates_each_mode':370,'adjacent_causal_coordinates_each_mode':333,'startup_adjacent_coordinates_each_mode':115,'live_adjacent_coordinates_each_mode':218,
            'first_live_coordinates_each_mode':37,'decoded_C_innovation_coordinates_each_mode':360,'alpha1_formula_only_input_coordinates_each_mode':10,
            'reported_R_offdiag_bounds_each_mode':240,'reported_R_exact_diagonal_zeros_each_mode':130,'maximum_observed_component_error':common['maximum_component_error'],
            'tracking_stats':common['tracking_stats'],'absolute_tolerance':5e-13,'relative_tolerance':0.0,'wrong_models_detected_each_mode':10,
            'setup_errors_credited_as_detections':0,'normal_optimized_nontiming_results_match':True,'new_named_Lean_declarations_actually_compiled':3,
            'reused_named_declarations_recompiled_not_new_labels':28,'formal_controls':8,'formal_positive_controls':2,'formal_false_math_controls':3,'formal_compiling_integrity_controls':3,
            'axiom_footprints':proof['main']['footprints'],'targeted_Mathlib_used':True,'reviewed_public_engine_unchanged':1,'reviewed_metadata_unchanged':3,
            'actual_engine_import_no_copied_replaced_or_edited_source_functions':True,'no_source_repair_or_failing_before_claim':True,
            'alpha1_no_division_or_strict_contraction_assumption':True,'all_preregistered_acceptance_conditions_met':True}
        result={'science':science,'environment':{'python':sys.version,'numpy':np.__version__,'compiler':proof['compiler_version'],'mathlib_revision':proof['mathlib_revision']},
            'elapsed_seconds':time.perf_counter()-start,'formal_elapsed_seconds':time.perf_counter()-begin,
            'scope':'Exact-real causal error/finite convolution composed with phase input; finite intact-engine trajectories including rounded alpha1. Not floating FFI/full coupled locking, sharp future bands, production/S01/baseline/CLI/certificate, installed library or independent review.'}
        verify(args.source);save(args.output/'cycle_results.json',result);print(json.dumps(result,indent=2));return 0
    except Exception as problem:
        save(args.output/'failure.json',{'type':type(problem).__name__,'message':str(problem),'semantic_negative_detection_credited':False});raise

if __name__=='__main__':raise SystemExit(main())
