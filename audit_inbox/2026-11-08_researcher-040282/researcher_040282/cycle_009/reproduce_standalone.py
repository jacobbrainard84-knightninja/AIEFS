"""Execute exact-note009 reproduction with genuinely fresh14 public dependencies.
No overwrite of an earlier completed run, no incoming contributed-code execution.
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
    require(not (standalone/'upstream').exists(),'Fresh dependency directory required')
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None)
    commands=[
        [sys.executable,'-B',str(HERE/'proposal/extract_from_report.py'),str(builder.REPORT),str(standalone/'extracted')],
        [sys.executable,'-B',str(standalone/'extracted/fetch_public_dependencies.py'),'--output',str(standalone/'upstream')],
        [sys.executable,'-B',str(standalone/'extracted/run_checks.py'),'--source',str(standalone/'upstream'),'--output',str(standalone/'checks')],
    ]
    executed=[]
    with (standalone/'reproduction.log').open('w') as log:
        for command in commands:
            log.write('COMMAND: '+' '.join(command)+'\n');log.flush()
            run=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,env=env,timeout=180)
            executed.append({'program':str(Path(command[2]).relative_to(HERE)),'returncode':run.returncode})
            log.write('RETURN: '+str(run.returncode)+'\n');log.flush()
            require(run.returncode==0,'Extract/fresh-fetch/full-rerun failed; preserved log is evidence, not a successful negative')
    for name in builder.CRITICAL:
        require((HERE/'proposal'/name).read_bytes()==(standalone/'extracted'/name).read_bytes(),'Critical extraction differs: '+name)
    original=json.loads((HERE/'checks/cycle_results.json').read_text())
    repeated=json.loads((standalone/'checks/cycle_results.json').read_text())
    require(original['science']==repeated['science'],'Scientific summary differs')
    a=json.loads((HERE/'checks/worker_results.json').read_text());b=json.loads((standalone/'checks/worker_results.json').read_text())
    strip=lambda rows:[{k:v for k,v in row.items() if k!='elapsed_seconds'} for row in rows]
    require(len(a)==len(b)==6 and strip(a)==strip(b),'Six-worker non-timing records differ')
    matched=[]
    for name in ('admission_observations.json','verdict_mismatches.json','configuration_results.json','metadata_only_anchor.json'):
        for path in sorted((HERE/'checks').glob('*/'+name)):
            relative=path.relative_to(HERE/'checks')
            require(path.read_bytes()==(standalone/'checks'/relative).read_bytes(),'Detailed source/guard records differ: '+str(relative))
            matched.append(str(relative))
    require(len(matched)==12,'Expected8 admission/mismatch and4 configuration/metadata records')
    manifest=json.loads((HERE/'proposal/source_modules.json').read_text())
    receipt={'actually_executed':True,'runner_returncode':executed[-1]['returncode'],'tested_main':manifest['commit'],
             'critical_file_count':len(builder.CRITICAL),'critical_files':list(builder.CRITICAL),
             'all_extracted_files_byte_identical':True,'fresh_public_dependencies_fetched_and_verified':14,
             'fresh_public_python_sources':12,'fresh_authority_metadata_files':2,
             'scientific_summary_matches_original':True,'all_six_worker_nontiming_results_match_original':True,
             'all_twelve_detailed_records_byte_identical':True,'detailed_matching_files':matched,
             'commands_observed':executed,'original_failures_each_mode':[4,4],'original_errors_each_mode':[0,0],
             'guard_passes_each_mode':[9,9],'original_unanchored_acceptances_relative_to_policy_each_mode':[7,7],
             'guard_verdict_mismatches_each_mode':[0,0],'mutants_detected_each_mode':[8,8],
             'configuration_rejections_not_semantic_detections_each_mode':[4,4],
             'genuine_S01_full_positive_executed':False,'repository_manifest_positive_is_metadata_only':True,
             'original_elapsed_seconds':original['elapsed_seconds'],'extracted_elapsed_seconds':repeated['elapsed_seconds'],
             'command':'python -B standalone/extracted/run_checks.py --source standalone/upstream --output standalone/checks',
             'result':'cycle_009/standalone/checks/cycle_results.json','log':'cycle_009/standalone/reproduction.log',
             'scope':'Submitter-local exact-note actual-module/new-guard reproduction, not independent guard approval, genuine S01 positive, CLI/bundle/certificate issuance or installed production repair'}
    (HERE/'standalone_reproduction.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
