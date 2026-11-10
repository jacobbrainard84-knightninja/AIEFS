"""Owned010 packet/privacy/preservation closure; NO science/compiler rerun.
Requires separate delivered older ZIPs for preservation checks. Not independent
review, security certification, production/authority validation or installation.
"""
from pathlib import Path
import ast
import csv
import hashlib
import json
import math
import re
import zipfile
import build_packet as builder

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
EMAIL=re.compile(rb"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
BLOCK=re.compile(r'<!-- BEGIN_CRITICAL_FILE: ([^>\n]+) -->\n```[^\n]*\n(.*?)\n```\n'
                 r'<!-- END_CRITICAL_FILE: \1 -->',re.S)
FIXTURE='cycle_006/source_state/main/tools/redteam/test_rt_claims_hygiene.py'
NAMES={'Researcher040282.Delay.historyTrace_index','Researcher040282.Delay.historyTrace_oldest',
       'Researcher040282.Delay.historyTrace_newest'}
LIVE={'STATE.json','CLAIM_LEDGER.csv','README.md','WORKFLOW.md','RESEARCH_QUEUE.md','EVIDENCE_INDEX.json','HISTORICAL_ARCHIVE_LOG_MAP.csv'}


def require(condition,message):
    if not condition:raise RuntimeError(message)


def read(path):return json.loads(path.read_text())


def ledger(path):
    with path.open(newline='') as stream:return list(csv.DictReader(stream))


def blob(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def inspect_contacts(items):
    matches=[]
    for name,data in items:
        count=len(EMAIL.findall(data))
        if not count:continue
        require(name==FIXTURE and count==2,'Unclassified contact pattern (path/count only): '+name+'/'+str(count))
        require(b'GIT_AUTHOR_NAME": "fixture"' in data and b'GIT_COMMITTER_NAME": "fixture"' in data,'Historical fixture context absent')
        record=next(r for r in read(ROOT/'cycle_006/source_state/main_selected.json')['files'] if r['path']=='tools/redteam/test_rt_claims_hygiene.py')
        require(len(data)==record['bytes'] and blob(data)==record['blob'],'Historical synthetic fixture changed')
        matches.append({'path':name,'occurrences':count,'classification':'INTENTIONALLY_SYNTHETIC_PUBLIC_GIT_ENV_FIXTURE_NOT_PERSONAL_COMMIT_METADATA',
                        'source_unmodified_and_acquisition_verified':True,'executed_by_this_cycle':False})
    require(len(matches)==1,'Expected one known synthetic fixture path');return matches


def check_formal(directory):
    proof=read(directory/'proof/result.json');main=proof['main']
    require(proof['imports']==['Std'] and not proof['Mathlib_used'] and proof['named_declarations_compiled']==3 and
            proof['formal_controls']==8 and proof['positive_controls_accepted']==2 and
            proof['false_math_witnesses_rejected_by_compiler']==proof['compiling_integrity_payloads_rejected_by_policy']==3 and
            proof['setup_errors_credited']==0 and proof['all_preregistered_formal_conditions_met'],'Formal inventory differs')
    require(main['accepted'] and main['reasons']==[] and main['raw_compiler_returncode']==0 and
            len(main['named_declarations'])==3 and set(main['footprints'])==set(main['requested_axiom_prints'])==NAMES and
            all(set(values)=={'propext','Quot.sound'} for values in main['footprints'].values()) and main['unapproved_axioms']=={},
            'Final named declaration/footprint acceptance differs')
    require((directory/'proof/compiled_sources/HistoryBuffer.lean').read_bytes()==(HERE/'proposal/HistoryBuffer.lean').read_bytes(),
            'Compiled final main source differs')
    main_log=(directory/'proof/compiler_logs/HistoryBuffer.log').read_text()
    require(not re.search(r'\b(?:warning|error)\s*:',main_log,re.I) and 'sorryAx' not in main_log and
            main_log.count('depends on axioms:')==3,'Main raw compiler evidence incomplete')
    records=proof['controls'];require(len(records)==len({r['control'] for r in records})==8,'Formal controls duplicate/missing')
    kinds={'positive':0,'false_math':0,'integrity':0}
    for row in records:
        require(row['expected_outcome_observed'] and row['setup_errors_credited']==0,'Formal unexpected/setup detection')
        kinds[row['kind']]+=1;policy=row['policy'];log=(directory/'proof/compiler_logs'/(row['control']+'.log')).read_text()
        require(not re.search(r'unknown module|object file .* does not exist|failed to import|cannot open shared object|unknown namespace',log,re.I),
                'Formal setup/import failure counted as a falsifier')
        if row['kind']=='positive':require(policy['accepted'] and policy['raw_compiler_returncode']==0,'Positive control rejected')
        elif row['kind']=='false_math':
            require(not policy['accepted'] and policy['raw_compiler_returncode']!=0 and
                    re.search(r'decide.*(?:false|failed)|proposition.*false',log,re.I|re.S),'False math failed for wrong reason')
        else:require(not policy['accepted'] and policy['raw_compiler_returncode']==0 and
                     row['expected_mechanism'] in policy['reasons'],'Compiling integrity payload not actually compiled/rejected')
    require(kinds=={'positive':2,'false_math':3,'integrity':3},'Formal kind inventory differs')
    return proof


def check_workers(directory):
    runs=read(directory/'worker_results.json')
    require(len(runs)==4 and {(r['kind'],r['optimized_python']) for r in runs}==
            {(kind,opt) for kind in ('common','wrong_models') for opt in (False,True)},'Four-worker inventory differs')
    for row in runs:
        name=row['kind']+('_optimized' if row['optimized_python'] else '_normal');sub=directory/name
        require({k:v for k,v in row.items() if k not in ('elapsed_seconds','observed_returncode')}==read(sub/'result.json') and
                row['observed_returncode']==0 and row['source_files_unchanged']==1 and row['metadata_files_unchanged']==2,'Worker/child or source mismatch')
        if row['kind']=='wrong_models':
            controls=read(sub/'wrong_models.json')
            require(controls==row['records'] and row['detected']==len(controls)==11 and len({r['model'] for r in controls})==11 and
                    row['actual_engine_advances']==0 and row['setup_errors_credited']==0,'Wrong-model inventory differs')
            for control in controls:
                require(control['detected'] and control['intended_field']==control['detected_field'] and control['setup_errors_credited']==0,
                        'Wrong model rejected by unintended mechanism')
                if control['model']=='alias_new_theta':require(control['detected_field']=='storage_ownership' and
                        control['maximum_component_difference'] is None,'Alias control not storage-specific')
                else:require(control['maximum_component_difference']>1e-7 and control['minimum_numeric_witness_required']==1e-7,
                             'Numeric wrong-model witness is tolerance fuzz')
            continue
        require(row['tests_run']==9 and row['failures']==row['errors']==row['skipped']==0 and
                row['actual_engine_advances']==row['reference_compared_transitions']==78 and row['source_initializations']==1 and
                row['dyadic_exact_states']==65 and row['dyadic_exact_stored_coordinates']==260 and
                row['absolute_tolerance']==5e-13 and row['relative_tolerance']==0 and
                row['actual_full_engine_import_no_source_function_copy_replacement_or_edit'] and
                not row['production_simulation_baseline_CLI_or_certificate_called'],'Common source inventory/boundary differs')
        log=(directory/(name+'.log')).read_text();require('Ran 9 tests in ' in log and '\nOK\n' in log,'Actual unittest success log absent')
        observations=read(sub/'advance_observations.json');require(len(observations)==len({r['label'] for r in observations})==78,'Actual-call observations incomplete')
        for observed in observations:
            require(set(observed['component_errors'])=={'C','R_physical','R_driver','B','theta','history','g_min_pre','g_min'} and
                    observed['maximum_component_error']==max(observed['component_errors'].values()) and
                    all(math.isfinite(v) and 0<=v<=5e-13 for v in observed['component_errors'].values()) and
                    observed['input_case_unchanged'] and observed['rng_unchanged'] and observed['independent_history_storage'] and
                    all(math.isfinite(v) and 0<=v<math.tau for v in observed['theta']),'Finite comparison/ownership observation inconsistent')
        require(row['maximum_component_error']==max(r['maximum_component_error'] for r in observations)==2.220446049250313e-16,
                'Observed maximum differs from final report')
        require(len([r for r in observations if r['label'].startswith('one_step/')])==9,'Nine scalar cases absent')
        dyadic=[r for r in observations if r['label'].startswith('dyadic/')];require(len(dyadic)==60,'Dyadic60 transitions absent')
        for observed in dyadic:
            match=re.fullmatch(r'dyadic/D([1-5])/step(\d+)',observed['label']);require(match is not None,'Unexpected dyadic label')
            d,n=map(int,match.groups())
            require(1<=n<=12 and observed['D']==d and observed['theta']==[0.25+n*0.125] and
                    observed['component_errors']['history']==observed['component_errors']['theta']==0.0,'Exact reachable trace record differs')
        domain=read(sub/'domain_checks.json')
        require(len(domain)==row['invalid_exact_delay_configs_rejected_not_semantic_detections']==2 and
                {r['tau'] for r in domain}=={0.2,0.1875} and all(r['dt']==0.125 and r['rejected_for_exact_delay'] and
                not r['semantic_negative_detection_credited'] for r in domain),'Domain errors conflated with semantic falsifiers')
    for kind in ('common','wrong_models'):
        pair=[{k:v for k,v in row.items() if k not in ('elapsed_seconds','optimized_python')} for row in runs if row['kind']==kind]
        require(pair[0]==pair[1],'Normal/optimized non-timing mismatch')
    return [{k:v for k,v in row.items() if k!='elapsed_seconds'} for row in runs]


def preflight():
    state=read(ROOT/'STATE.json')
    require(state['current_cycle']==10 and state['current_status']=='COMPLETED_LOCAL_HISTORY_FOUNDATION_AND_PHASE_CONTRACT_UNREVIEWED' and
            state['in_progress'] is None and state['next_cycle']==11 and state['research_processes_running']==[] and
            not (ROOT/'cycle_011').exists(),'Completion/resumption boundary differs')
    require(state['last_updated_date']=='2026-09-04' and not state['date_provenance']['historical004_execution_date_reconstructed'],
            'Preparation versus historical date scope differs')
    require(not any(state[key] for key in ('current_cycle_independent_review_received','latest_packet_owner_upload_confirmed',
                                         'remote_changes_by_this_agent','contacted_other_bots','automatic_work_between_turns')),'Review/remote/upload overclaim')
    boundary=state['authority_boundary']
    require(boundary['new_unregistered_library_candidate_and_finite_specification_only'] and
            boundary['actual_frozen_engine_read_only_import_and_synthetic_primitives'] and not any(boundary[key] for key in (
            'frozen_source_edited','lock_or_registry_changed','source_cache_edited','new_helper_or_module_installed',
            'authority_validation_run','full_equivalence_pipeline_run','run_seed_simulate_production_CLI_or_writer_called')),'Authority/source boundary differs')
    require(not Path('/home/user/audit').exists() and Path('/home/user/aief_audit').is_dir() and Path('/home/user/aiefs_repository_audit').is_dir(),
            'Deleted Lua/retained AIEFS roots boundary differs')
    current=ledger(ROOT/'CLAIM_LEDGER.csv');prior=ledger(HERE/'previous009_snapshot/CLAIM_LEDGER.csv')
    require(len(current)==len({r['claim_id'] for r in current})==118 and len(prior)==114 and current[:114]==prior and
            sum(r['evidence_label']=='LEAN_COMPILED' for r in current)==97 and
            [r['evidence_label'] for r in current[114:]]==['LEAN_COMPILED']*3+['EXECUTABLE_REGRESSION_CHECK'] and
            all(r['cycle']=='10' for r in current[114:]),'Prior114 preservation/new labels differ')
    for count,path in ((113,'cycle_009/previous008_snapshot/CLAIM_LEDGER.csv'),(112,'cycle_008/previous007_snapshot/CLAIM_LEDGER.csv'),
                       (111,'cycle_007/previous006_snapshot/CLAIM_LEDGER.csv'),(109,'cycle_006/previous005_snapshot/CLAIM_LEDGER.csv')):
        old=ledger(ROOT/path);require(len(old)==count and prior[:count]==old,'Historical row scope changed')
    old004=ledger(ROOT/'cycle_005/completed_004_snapshot/CLAIM_LEDGER_COMPLETED_004.csv')
    old005=ledger(ROOT/'cycle_006/previous005_snapshot/CLAIM_LEDGER.csv')
    require(len(old004)==108 and [r for r in old005 if r['cycle']!='5']==old004,'Completed004 scope changed')
    original=read(HERE/'checks/cycle_results.json');repeat=read(HERE/'standalone/checks/cycle_results.json');science=original['science']
    require(science==repeat['science'] and science['all_preregistered_acceptance_conditions_met'] and
            science['source_contract_methods_each_mode']==science['source_passes_each_mode']==9 and
            science['actual_advances_each_common_mode']==78 and science['wrong_models_detected_each_mode']==11 and
            science['new_named_Lean_declarations_actually_compiled']==3 and science['formal_controls']==8 and
            science['setup_errors_credited_as_detections']==0,'Scientific summary differs/incomplete')
    require(check_workers(HERE/'checks')==check_workers(HERE/'standalone/checks'),'Original/extracted workers differ')
    a=check_formal(HERE/'checks');b=check_formal(HERE/'standalone/checks');require(a==b,'Original/extracted proof records differ')
    receipt=read(HERE/'standalone_reproduction.json')
    require(receipt['actually_executed'] and receipt['runner_returncode']==0 and receipt['critical_file_count']==10 and
            receipt['fresh_public_dependencies_fetched_and_verified']==3 and receipt['same_original_verified_compiler_reused'] and
            not receipt['fresh_clean_compiler_installation_claimed'] and receipt['all_four_worker_nontiming_results_match_original'] and
            receipt['all_twentyfive_detailed_records_byte_identical'] and len(receipt['detailed_matching_files'])==25,'Reproduction receipt overstates/incomplete')
    for name in receipt['detailed_matching_files']:
        require((HERE/'checks'/name).read_bytes()==(HERE/'standalone/checks'/name).read_bytes(),'Detailed reproduction content changed')
    fetched=read(HERE/'standalone/fetch_receipt.json')
    require(fetched['public_dependencies_fetched_and_verified']==3 and all(r['freshly_fetched'] and r['verified'] for r in fetched['files']),
            'Three fresh dependency fetches unobserved')
    report=builder.REPORT.read_text();pairs=BLOCK.findall(report)
    require(len(pairs)==10 and {name for name,_ in pairs}==set(builder.CRITICAL) and
            'PROVISIONAL: extracted-code rerun not executed yet' not in report and not re.search(r'\{\{[A-Z_]+\}\}',report) and
            '118 unique rows / 97 LEAN_COMPILED labels' in report and 'not a source-bug/failing-before repair claim' in report and
            'No tolerance was tuned' in report and 'Reachability is explicit' in report,'Report provisional/stale/missing caveat')
    for name,body in pairs:
        require((body+'\n').encode()==(HERE/'proposal'/name).read_bytes()==(HERE/'standalone/extracted'/name).read_bytes(),
                'Final inline !=actually executed extracted critical source: '+name)
        if name.endswith('.py'):require(not any(isinstance(node,ast.Assert) for node in ast.walk(ast.parse(body))),
                                        'Owned critical check uses optimization-removable assert')
    acquired={}
    for branch,count in (('main',32),('inbox',8)):
        metadata=read(HERE/'source_state'/(branch+'_selected.json'))
        require(len(metadata['files'])==metadata['fetched_and_verified']==count,'Acquisition count differs')
        for row in metadata['files']:
            data=(HERE/'source_state'/branch/row['path']).read_bytes()
            require(len(data)==row['bytes'] and blob(data)==row['blob'],'Acquired source changed')
        acquired[branch]=count
    manifest=read(HERE/'proposal/source_modules.json')
    require(len(manifest['modules'])==1 and len(manifest['metadata'])==2,'Reviewed closure count differs')
    for row in manifest['modules']+manifest['metadata']:
        for directory in (HERE/'source_state/main',HERE/'standalone/upstream'):
            data=(directory/row['path']).read_bytes()
            require(len(data)==row['bytes'] and blob(data)==row['blob'],'Original/fresh dependency changed')
    require(not list((HERE/'source_state/inbox').rglob('*provenance-mutation*repro*')),'New contributed reproducer unexpectedly acquired')
    setup=read(HERE/'compiler_setup.json');cleanup=read(HERE/'compiler_cleanup.json')
    require(setup['public_asset_verified'] and setup['download_bytes']==manifest['lean_toolchain']['bytes'] and
            not setup['Mathlib_installed'] and not setup['global_toolchain_changed'] and
            cleanup['actually_removed_after_successful_full_reproduction'] and cleanup['cache_absent_after_removal'] and
            not Path(cleanup['own_cache']).exists() and cleanup['only_cycle010_owned_compiler_archive_decoder_target_removed'] and
            cleanup['regular_file_logical_bytes_removed']>setup['download_bytes'] and cleanup['symlinks_removed'] is None,
            'Compiler resource/cleanup receipt differs')
    broken=(HERE/'development/initial_proof/compiler.log').read_text();fixed=(HERE/'development/projection_explicit/compiler.log').read_text()
    require('error: omega could not prove the goal' in broken and 'sorryAx' in broken and 'sorryAx' not in fixed and
            not re.search(r'\b(?:warning|error)\s*:',fixed,re.I),'Development failure/corrected preflight not retained')
    branches=[p for p in ROOT.rglob('*_branch*.json') if 'source_state' in p.parts];require(len(branches)==18,'Expected eighteen minimal branch records')
    for path in branches:
        value=read(path);require(set(value)=={'branch','commit','metadata_policy'} and all(isinstance(v,str) for v in value.values()),'Nonminimal branch metadata')
    contacts=inspect_contacts((str(path.relative_to(ROOT)),path.read_bytes()) for path in builder.selected_files())
    privacy={'all_eighteen_branch_records_structurally_minimal':True,'new010_metadata_minimal_at_creation':True,
             'personal_commit_contacts_or_signed_payloads_in_branch_metadata':0,'unclassified_outgoing_email_pattern_matches':0,
             'new_contributed_reproducer_not_acquired_or_executed':True,'historical_synthetic_fixture_matches':contacts,
             'known009_encoded_sources_prior_static_inspection_preserved':'cycle_009/incoming_static_privacy.json',
             'printed_contact_values':False,'scope':'Owned packet structural minimization/scoped pattern scan, not exhaustive secrets/security certification'}
    (HERE/'privacy_results.json').write_text(json.dumps(privacy,indent=2)+'\n')
    preserved=0
    with zipfile.ZipFile(ROOT/'researcher040282-cycle009-anchored-cohort-admission.zip') as archive:
        for member in archive.namelist():
            name=member.removeprefix('researcher_040282/')
            if name not in LIVE:
                require((ROOT/name).is_file() and (ROOT/name).read_bytes()==archive.read(member),'Prior009 nonlive evidence changed/missing: '+name);preserved+=1
        for name in ('STATE.json','CLAIM_LEDGER.csv'):
            require((HERE/'previous009_snapshot'/name).read_bytes()==archive.read('researcher_040282/'+name),'Completed009 snapshot differs from delivery')
    restoration=read(HERE/'historical_restoration.json')
    require(restoration['missing_before_this_administrative_step'] and restoration['restored_bytes']==9175 and
            restoration['restored_content_matches_delivered_member'] and not restoration['existing_source_or_log_overwritten'] and
            not restoration['historical_science_rerun'] and not restoration['scientific010_inputs_code_results_changed'] and
            restoration['user_deleted_legacy_lua_audit_remains_absent'],'Missing-only historical restoration differs')
    protected=['2026-09-04_researcher040282_004_complex-ema.md']+['cycle_004/'+name for name in (
        'GateFoundations.lean','FreezeCore.lean','GateProposalBridge.lean','CoherenceEMA.lean','CoherenceDriveBridge.lean','check_cycle.py','compare_source.py')]
    with zipfile.ZipFile(ROOT/'researcher040282-cycle004-complex-ema.zip') as archive:
        for name in protected:require((ROOT/name).read_bytes()==archive.read('researcher_040282/'+name),'Protected004 source/report changed')
    for name in ('README.md','WORKFLOW.md','RESEARCH_QUEUE.md'):
        text=(ROOT/name).read_text();require('010' in text and '011' in text,'Root navigation stale')
    index=read(ROOT/'EVIDENCE_INDEX.json');require(index['ledger_rows']==118 and index['archive_only_ledger_references']==0,'Evidence index stale')
    for row in index['ledger_evidence']:
        require(row['availability']=='UNPACKED' and row['packet_members'],'Cited evidence not unpacked')
        for member in row['packet_members']:require((ROOT.parent/member).is_file(),'Unpacked member missing')
    return {'current_ledger_rows':118,'prior114_rows_preserved':True,'formal_labels_prior94_plus3':97,
            'original_and_extracted_full_runner_success':True,'source_passes_each_mode':9,'actual_advances_each_mode':78,
            'source_initializers_each_mode':1,'dyadic_exact_states_each_mode':65,'dyadic_exact_stored_coordinates_each_mode':260,
            'maximum_component_error':2.220446049250313e-16,'wrong_models_detected_each_mode':11,'formal_controls':8,
            'exact_delay_configuration_rejections_separate_each_mode':2,'setup_errors_credited':0,
            'four_workers_and_twentyfive_details_match_reproduction':True,'critical_inline_files_equal_executed_extracted_sources':10,
            'verified_acquisition_files_unchanged':acquired,'public_engine_unchanged':1,'scope_compiler_metadata_unchanged':2,
            'source_functions_not_copied_replaced_or_edited':True,'generic_history_not_full_Python_float_coupled_map_theorem':True,
            'new_module_spec_not_installed_or_independently_reviewed':True,'no_production_study_authority_certificate_or_remote_write':True,
            'own_disposable_compiler_removed_after_full_reproduction':True,'initial_owned_proof_failure_retained_not_a_control':True,
            'prior009_nonlive_evidence_files_preserved':preserved,'completed009_state_ledger_snapshots_match_delivery':True,
            'protected004_critical_files':len(protected),'one_missing_old_CI_source_restored_exactly_no_science_rerun':True,
            'deleted_legacy_lua_audit_remains_absent':True,'all_eighteen_branch_records_minimal':True,
            'unclassified_email_pattern_matches':0,'historical_intentionally_synthetic_fixture_addresses_distinguished':2,
            'all_ledger_evidence_unpacked':True,'ledger_reference_count':index['unique_ledger_references'],
            'unpacked_log_count':index['unpacked_log_count'],
            'scope':'Owned packet consistency/privacy/preservation, no scientific rerun or independent review/authority/integration/security certification'}


def verify_archive():
    expected={'researcher_040282/'+str(path.relative_to(ROOT)):path for path in builder.selected_files()}
    with zipfile.ZipFile(builder.ARCHIVE) as archive:
        names=archive.namelist();require(archive.testzip() is None and len(names)==len(set(names)),'ZIP CRC/duplicate member failure')
        require(set(names)==set(expected),'ZIP/workspace selected membership differs');contents=[]
        for name,path in expected.items():
            data=archive.read(name);require(data==path.read_bytes(),'ZIP selected content differs: '+name)
            contents.append((name.removeprefix('researcher_040282/'),data))
        inspect_contacts(contents)
    return len(expected)


def main():
    builder.build_report();builder.build_indices();result=preflight();builder.package();verify_archive()
    result.update({'zip_crc_verified':True,'all_members_match_selected_workspace_files':True,
                   'receipt_included_and_final_archive_reverified':True})
    (HERE/'packet_validation.json').write_text(json.dumps(result,indent=2)+'\n');builder.package();verify_archive()
    state=read(ROOT/'STATE.json');state['handoff_status']='LOCAL_PACKET_CLOSURE_VERIFIED;NOT_UPLOADED'
    (ROOT/'STATE.json').write_text(json.dumps(state,indent=2)+'\n');builder.package()
    try:members=verify_archive();preflight();verify_archive()
    except Exception:
        state['handoff_status']='PACKET_CLOSURE_RECHECK_FAILED;DO_NOT_DELIVER';(ROOT/'STATE.json').write_text(json.dumps(state,indent=2)+'\n');raise
    print(json.dumps({'validation':result,'final_archive_members':members,'final_archive_bytes':builder.ARCHIVE.stat().st_size,
                      'standalone_report_bytes':builder.REPORT.stat().st_size},indent=2))


if __name__=='__main__':main()
