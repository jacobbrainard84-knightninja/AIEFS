"""Extract13 owned files from011 note, freshly fetch4 public dependencies,
then repeat ALL science with SAME verified compiler/targeted Mathlib setup.
No second clean setup claim. Refuse overwriting completed reproduction/upstream.
"""
import argparse
from pathlib import Path
import json
import os
import subprocess
import sys
import build_packet as builder

HERE=Path(__file__).resolve().parent

def require(condition,message):
    if not condition:raise RuntimeError(message)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--lean',type=Path,required=True);p.add_argument('--mathlib',type=Path,required=True);args=p.parse_args()
    setup=json.loads((HERE/'compiler_setup.json').read_text());ml=json.loads((HERE/'mathlib_setup.json').read_text())
    require(args.lean.resolve()==Path(setup['compiler_binary']).resolve() and args.lean.is_file() and setup['public_asset_verified'],'Same verified compiler required')
    require(args.mathlib.resolve()==Path(ml['mathlib_directory']).resolve() and args.mathlib.is_dir() and ml['cache_helper_returncode']==0,'Same verified targeted Mathlib required')
    standalone=HERE/'standalone';standalone.mkdir(exist_ok=True)
    require(not (standalone/'checks/cycle_results.json').exists(),'Completed reproduction exists: do not overwrite')
    require(not (standalone/'upstream').exists(),'Fresh public dependency directory required')
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None)
    commands=[
        [sys.executable,'-B',str(HERE/'proposal/extract_from_report.py'),str(builder.REPORT),str(standalone/'extracted')],
        [sys.executable,'-B',str(standalone/'extracted/fetch_public_dependencies.py'),'--output',str(standalone/'upstream')],
        [sys.executable,'-B',str(standalone/'extracted/run_checks.py'),'--source',str(standalone/'upstream'),'--output',str(standalone/'checks'),
         '--lean',str(args.lean.resolve()),'--mathlib',str(args.mathlib.resolve())],
    ];executed=[]
    with (standalone/'reproduction.log').open('w') as log:
        for command in commands:
            log.write('COMMAND: '+' '.join(command)+'\n');log.flush()
            run=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,env=env,timeout=900)
            log.write(run.stdout);log.write('RETURN: '+str(run.returncode)+'\n');log.flush()
            program=str(Path(command[2]).relative_to(HERE));executed.append({'program':program,'returncode':run.returncode})
            require(run.returncode==0,'Extraction/fetch/full rerun blocked; preserve log, never a successful negative')
            if program.endswith('fetch_public_dependencies.py'):
                fetched=json.loads(run.stdout)
                require(fetched['public_dependencies_fetched_and_verified']==4 and all(r['freshly_fetched'] and r['verified'] for r in fetched['files']),'Not all4 fresh dependencies')
                (standalone/'fetch_receipt.json').write_text(json.dumps(fetched,indent=2)+'\n')
    for name in builder.CRITICAL:require((HERE/'proposal'/name).read_bytes()==(standalone/'extracted'/name).read_bytes(),'Extracted bytes differ: '+name)
    original=json.loads((HERE/'checks/cycle_results.json').read_text());repeated=json.loads((standalone/'checks/cycle_results.json').read_text())
    require(original['science']==repeated['science'],'Scientific summary differs')
    a=json.loads((HERE/'checks/worker_results.json').read_text());b=json.loads((standalone/'checks/worker_results.json').read_text())
    strip=lambda rows:[{k:v for k,v in row.items() if k!='elapsed_seconds'} for row in rows]
    require(len(a)==len(b)==4 and strip(a)==strip(b),'Four-worker non-timing data differ')
    files=[]
    for pattern in ('common_*/preexecution_design.json','common_*/advance_observations.json','common_*/input_ratio_observations.json',
                    'wrong_models_*/preexecution_design.json','wrong_models_*/wrong_models.json','proof/result.json',
                    'proof/compiled_sources/*.lean','proof/compiler_logs/*.log'):files.extend((HERE/'checks').glob(pattern))
    matched=[]
    for path in sorted(files):
        relative=path.relative_to(HERE/'checks');require(path.read_bytes()==(standalone/'checks'/relative).read_bytes(),'Detailed record differs: '+str(relative));matched.append(str(relative))
    require(len(matched)==31,'Expected10 source/design/model files +1formal record +20compiled-source/compiler-log files')
    receipt={'actually_executed':True,'runner_returncode':executed[-1]['returncode'],'tested_main':original['science']['tested_main'],
             'critical_file_count':13,'critical_files':list(builder.CRITICAL),'all_extracted_files_byte_identical':True,
             'fresh_public_dependencies_fetched_and_verified':4,'fresh_public_python_sources':1,'fresh_scope_compiler_metadata_files':3,
             'same_original_verified_compiler_and_Mathlib_reused':True,'fresh_clean_compiler_or_Mathlib_installation_claimed':False,
             'scientific_summary_matches_original':True,'all_four_worker_nontiming_results_match_original':True,
             'all_thirtyone_detailed_records_byte_identical':True,'detailed_matching_files':matched,'commands_observed':executed,
             'source_passes_each_mode':[9,9],'source_failures_errors_skips_each_mode':[0,0,0],'actual_advances_each_common_mode':[56,56],
             'source_initializations_each_common_mode':[0,0],'input_complex_coordinates_each_mode':[496,496],'adjacent_complex_coordinates_each_mode':[434,434],
             'wrong_models_detected_each_mode':[10,10],'new_named_Lean_declarations_compiled':3,'reused_history_labels_not_added':3,'formal_controls_repeated':8,
             'original_elapsed_seconds':original['elapsed_seconds'],'extracted_elapsed_seconds':repeated['elapsed_seconds'],
             'command':'python -B standalone/extracted/run_checks.py --source standalone/upstream --output standalone/checks --lean <same verified compiler> --mathlib <same targeted Mathlib>',
             'result':'cycle_011/standalone/checks/cycle_results.json','log':'cycle_011/standalone/reproduction.log',
             'scope':'Submitter-local exact-note full repetition, not independent review, Python/float/full-coupled proof, real study, authority certificate, source repair/integration or upload'}
    (HERE/'standalone_reproduction.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
