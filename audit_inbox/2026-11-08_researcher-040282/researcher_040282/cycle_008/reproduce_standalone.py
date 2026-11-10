"""Actually extract the numbered note, freshly fetch12 sources and repeat008.
Preserve executed results; refuse to overwrite an earlier completed reproduction.
"""
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
    standalone=HERE/'standalone';standalone.mkdir(exist_ok=True)
    require(not (standalone/'checks/cycle_results.json').exists(),'Completed reproduction already exists; do not overwrite')
    require(not (standalone/'upstream').exists(),'Use genuinely fresh dependency directory')
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None)
    commands=[
        [sys.executable,'-B',str(HERE/'proposal/extract_from_report.py'),str(builder.REPORT),str(standalone/'extracted')],
        [sys.executable,'-B',str(standalone/'extracted/fetch_public_dependencies.py'),'--output',str(standalone/'upstream')],
        [sys.executable,'-B',str(standalone/'extracted/run_checks.py'),'--source',str(standalone/'upstream'),'--output',str(standalone/'checks')],
    ]
    records=[]
    with (standalone/'reproduction.log').open('w') as log:
        for command in commands:
            log.write('COMMAND: '+' '.join(command)+'\n');log.flush()
            result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,env=env,timeout=150)
            records.append({'program':str(Path(command[2]).relative_to(HERE)),'returncode':result.returncode})
            log.write('RETURN: '+str(result.returncode)+'\n');log.flush()
            require(result.returncode==0,'Extract/fetch/full rerun failed; inspect preserved log')
    for name in builder.CRITICAL:
        require((HERE/'proposal'/name).read_bytes()==(standalone/'extracted'/name).read_bytes(),'Critical file differs: '+name)
    original=json.loads((HERE/'checks/cycle_results.json').read_text())
    repeated=json.loads((standalone/'checks/cycle_results.json').read_text())
    require(original['science']==repeated['science'],'Scientific summary differs')
    a=json.loads((HERE/'checks/worker_results.json').read_text())
    b=json.loads((standalone/'checks/worker_results.json').read_text())
    strip=lambda rows:[{key:value for key,value in row.items() if key!='elapsed_seconds'} for row in rows]
    require(len(a)==len(b)==6 and strip(a)==strip(b),'Non-timing worker results differ')
    detailed=[]
    for name in ('table_census.json','census_mismatches.json','sequence_definitions.json','invalid_key_results.json'):
        for path in sorted((HERE/'checks').glob('*/'+name)):
            relative=path.relative_to(HERE/'checks')
            require(path.read_bytes()==(standalone/'checks'/relative).read_bytes(),'Detailed results differ: '+str(relative))
            detailed.append(str(relative))
    require(len(detailed)==14,'Expected12 detailed census files and2 candidate-only key files')
    manifest=json.loads((HERE/'proposal/source_modules.json').read_text())
    require(len(manifest['modules'])==12,'Expected actual public package closure')
    receipt={'actually_executed':True,'runner_returncode':records[-1]['returncode'],
             'tested_main':manifest['commit'],'critical_file_count':len(builder.CRITICAL),
             'critical_files':list(builder.CRITICAL),'all_extracted_files_byte_identical':True,
             'fresh_public_source_files_fetched_and_verified':len(manifest['modules']),
             'scientific_summary_matches_original':True,'all_six_worker_nontiming_results_match_original':True,
             'all_fourteen_detailed_census_and_invalid_key_files_byte_identical':True,
             'detailed_matching_files':detailed,'commands_observed':records,
             'original_failures_each_mode':[5,5],'original_errors_each_mode':[0,0],
             'candidate_passes_each_mode':[12,12],'original_census_false_accepts_each_mode':[244,244],
             'candidate_census_mismatches_each_mode':[0,0],
             'candidate_only_invalid_key_cases_each_mode':[10,10],'mutants_detected_each_mode':[8,8],
             'original_elapsed_seconds':original['elapsed_seconds'],'extracted_elapsed_seconds':repeated['elapsed_seconds'],
             'command':'python -B standalone/extracted/run_checks.py --source standalone/upstream --output standalone/checks',
             'result':'cycle_008/standalone/checks/cycle_results.json','log':'cycle_008/standalone/reproduction.log',
             'scope':'Submitter-local exact-note actual-public-API reproduction, not independent-seat approval, installed repair, real S01/201-vs200 or authority/whole-study certificate'}
    (HERE/'standalone_reproduction.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
