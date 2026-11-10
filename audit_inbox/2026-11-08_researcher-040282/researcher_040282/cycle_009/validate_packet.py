"""Owned009 packet consistency/privacy closeout, not scientific reexecution.
Requires earlier delivered ZIPs for preservation checks; not independent review,
authority validation, full secret detection, or arbitrary-code security.
"""
from pathlib import Path
import ast
import csv
import hashlib
import json
import re
import zipfile
import build_packet as builder

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
EMAIL=re.compile(rb"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
BLOCK=re.compile(r'<!-- BEGIN_CRITICAL_FILE: ([^>\n]+) -->\n```[^\n]*\n(.*?)\n```\n'
                 r'<!-- END_CRITICAL_FILE: \1 -->',re.S)
FIXTURE='cycle_006/source_state/main/tools/redteam/test_rt_claims_hygiene.py'
RED={'test_scalar_repin','test_certificate_repin','test_manifest_repin','test_official_pin'}


def require(condition,message):
    if not condition:raise RuntimeError(message)


def read_json(path):return json.loads(path.read_text())


def read_ledger(path):
    with path.open(newline='') as stream:return list(csv.DictReader(stream))


def git_blob(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def inspect_contact_patterns(items):
    matches=[]
    for name,data in items:
        count=len(EMAIL.findall(data))
        if not count:continue
        require(name==FIXTURE and count==2,'Unclassified contact pattern (path/count only): '+name+'/'+str(count))
        require(b'GIT_AUTHOR_NAME": "fixture"' in data and b'GIT_COMMITTER_NAME": "fixture"' in data,
                'Allowlisted path lacks intentionally synthetic context')
        metadata=read_json(ROOT/'cycle_006/source_state/main_selected.json')
        record=next(row for row in metadata['files'] if row['path']=='tools/redteam/test_rt_claims_hygiene.py')
        require(git_blob(data)==record['blob'] and len(data)==record['bytes'],'Historical public fixture changed')
        matches.append({'path':name,'occurrences':count,
                        'classification':'INTENTIONALLY_SYNTHETIC_PUBLIC_GIT_ENV_FIXTURE_NOT_PERSONAL_COMMIT_METADATA',
                        'source_unmodified_and_acquisition_verified':True,'executed_by_this_cycle':False})
    require(len(matches)==1,'Expected one historical synthetic fixture path');return matches


def preflight():
    state=read_json(ROOT/'STATE.json')
    require(state['current_cycle']==9 and state['current_status']=='COMPLETED_LOCAL_ANCHORED_ADMISSION_PROPOSAL_UNREVIEWED',
            'Current completion state mismatch')
    require(state['in_progress'] is None and state['next_cycle']==10 and state['research_processes_running']==[],
            'Resumption/process state mismatch')
    require(state['last_updated_date']=='2026-09-04' and
            not state['date_provenance']['historical004_execution_date_reconstructed'],'Preparation/history date mismatch')
    require(not any(state[key] for key in ('current_cycle_independent_review_received','latest_packet_owner_upload_confirmed',
                                         'remote_changes_by_this_agent','contacted_other_bots','automatic_work_between_turns')),
            'Review/upload/remote boundary mismatch')
    boundary=state['authority_boundary']
    require(boundary['independent_repository_manifest_artifact']=='ART-2217' and
            boundary['committed_manifest_matches_inventory'] and boundary['repository_anchor_positive_scope']=='METADATA_ONLY_NOT_GENUINE_COHORT' and
            not any(boundary[key] for key in ('full_genuine_S01_positive_executed','frozen_source_edited','lock_or_registry_changed',
                                             'new_helper_installed','source_cache_edited','authority_validation_run',
                                             'full_equivalence_pipeline_run','run_analysis_main_or_writer_called')),
            'Caller-anchor proposal promoted to a production/authority repair')
    require(not Path('/home/user/audit').exists(),'Deleted legacy Lua audit must remain absent')
    current=read_ledger(ROOT/'CLAIM_LEDGER.csv');prior=read_ledger(HERE/'previous008_snapshot/CLAIM_LEDGER.csv')
    prior007=read_ledger(ROOT/'cycle_008/previous007_snapshot/CLAIM_LEDGER.csv')
    prior006=read_ledger(ROOT/'cycle_007/previous006_snapshot/CLAIM_LEDGER.csv')
    prior005=read_ledger(ROOT/'cycle_006/previous005_snapshot/CLAIM_LEDGER.csv')
    prior004=read_ledger(ROOT/'cycle_005/completed_004_snapshot/CLAIM_LEDGER_COMPLETED_004.csv')
    require(len(current)==len({r['claim_id'] for r in current})==114 and len(prior)==113 and current[:113]==prior,
            'Current uniqueness/prior113 rows changed')
    require(len(prior007)==112 and prior[:112]==prior007 and len(prior006)==111 and prior[:111]==prior006 and
            len(prior005)==109 and prior[:109]==prior005 and len(prior004)==108 and
            [r for r in prior005 if r['cycle']!='5']==prior004,'Historical completed scopes changed')
    require(sum(r['evidence_label']=='LEAN_COMPILED' for r in current)==94 and
            current[-1]['evidence_label']=='EXECUTABLE_REGRESSION_CHECK' and current[-1]['cycle']=='9','Evidence-label promotion')
    original=read_json(HERE/'checks/cycle_results.json');repeat=read_json(HERE/'standalone/checks/cycle_results.json')
    science=original['science']
    require(science==repeat['science'] and science['all_preregistered_acceptance_conditions_met'] and
            science['common_contract_methods']==9 and science['admission_fixtures_each_suite']==18 and
            science['original_expected_failures_each_mode']==4 and science['original_errors_each_mode']==0 and
            science['candidate_passes_each_mode']==9 and science['original_false_accepts_relative_to_proposed_anchor_policy']==7 and
            science['original_false_rejects']==0 and science['candidate_verdict_mismatches']==0 and
            science['expected_positive_test_owned_synthetic_cases']==3 and science['untrusted_root_rejections_before_delegation']==7 and
            science['preserved_child_hash_and_schema_rejections']==8 and science['mutants_detected_each_mode']==8 and
            science['invalid_anchor_configuration_rejections_each_candidate_mode']==4 and
            science['configuration_errors_credited_as_semantic_detections']==0 and science['genuine_S01_five_file_positive_not_executed'],
            'Science differs from fixed contract or overclaims genuine positive')
    worker_sets=[]
    for base in ('checks','standalone/checks'):
        directory=HERE/base;runs=read_json(directory/'worker_results.json')
        require(len(runs)==6 and {(r['mode'],r['optimized_python']) for r in runs}==
                {(mode,opt) for mode in ('baseline','candidate','mutants') for opt in (False,True)},'Worker set incomplete')
        for row in runs:
            name=row['mode']+('_optimized' if row['optimized_python'] else '_normal');sub=directory/name
            require({k:v for k,v in row.items() if k!='observed_returncode'}==read_json(sub/'result.json'),'Worker/child record mismatch')
            require(row['public_source_files_unchanged']==12 and row['authority_metadata_files_unchanged']==2,'Source custody missing')
            inspected=row['fixture_inspection']
            require(inspected['npz_total_keys']==2600 and inspected['trajectory_arrays']==2400 and inspected['continue_matrices']==200 and
                    inspected['samples_per_trajectory']==640 and inspected['scalar_rows']==800 and
                    inspected['successful_condition_rows']==200 and inspected['unique_seed_count']==40 and
                    inspected['all_keys_shapes_finiteness_and_ranges_checked'] and inspected['synthetic_not_engine_trajectories'],
                    'Independent fixture nonvacuity/inspection incomplete')
            if row['mode']=='mutants':
                require(row['observed_returncode']==0 and row['detected']==8 and row['setup_errors_credited']==0 and
                        all(r['detected'] for r in row['records']) and len({r['mutant'] for r in row['records']})==8 and
                        [r['mechanism'] for r in row['records']]==['verdict']*6+['admission_order','input_preservation'],
                        'Mutant failures not exact intended mechanisms')
                continue
            require(row['tests_run']==9 and row['errors']==row['skipped']==0 and
                    len(row['fixture_group_counts'])==9 and sum(row['fixture_group_counts'].values())==18,'Common suite incomplete')
            source_scope=row['source_boundary']
            require(source_scope['actual_full_module_imported'] and source_scope['actual_discover_inputs_and_validate_run_called'] and
                    not any(source_scope[key] for key in ('source_functions_copied_replaced_or_edited','new_guard_installed',
                                                         'run_analysis_main_or_writer_called','genuine_S01_five_file_validation_executed')),
                    'Actual-module/new-file/genuine-positive boundary misstated')
            observations=read_json(sub/'admission_observations.json');bad=read_json(sub/'verdict_mismatches.json')
            require(len(observations)==len({r['case'] for r in observations})==18 and
                    sum(r['expected_accept'] for r in observations)==3 and
                    all(r['all_five_input_files_and_inventory_unchanged'] and len(r['precall_input_digests'])==5 for r in observations),
                    'Observation pre-call/snapshot inventory incomplete')
            require(bad==[r for r in observations if r['expected_accept']!=r['observed_accept']], 'Mismatch record inconsistent')
            calculated={'admission_calls':18,'expected_accepts':3,'observed_accepts':sum(r['observed_accept'] for r in observations),
                        'false_accepts':sum(not r['expected_accept'] and r['observed_accept'] for r in observations),
                        'false_rejects':sum(r['expected_accept'] and not r['observed_accept'] for r in observations),
                        'delegate_calls':sum(r['observed_delegate_calls'] for r in observations),'mismatched_verdicts':len(bad)}
            require(calculated==row['observations'],'Recorded observed counts inconsistent')
            if row['mode']=='baseline':
                require(row['observed_returncode']==1 and row['failures']==4 and set(row['failure_methods'])==RED and
                        row['configuration_rejections_not_semantic_detections']==0 and calculated==
                        {'admission_calls':18,'expected_accepts':3,'observed_accepts':10,'false_accepts':7,'false_rejects':0,
                         'delegate_calls':18,'mismatched_verdicts':7},'Wrong original red signature')
                require((directory/(name+'.log')).read_text().count('expected=False, observed=True')==7,
                        'Original failed for unplanned reasons')
            else:
                require(row['observed_returncode']==0 and row['failures']==0 and calculated==
                        {'admission_calls':18,'expected_accepts':3,'observed_accepts':3,'false_accepts':0,'false_rejects':0,
                         'delegate_calls':11,'mismatched_verdicts':0},'Guard acceptance incomplete')
                roots=[r for r in observations if r['expected_stage']=='root'];old=[r for r in observations if r['expected_stage'] in ('schema','child_hash')]
                require(len(roots)==7 and all(not r['observed_accept'] and r['observed_stage']=='root' and
                        r['observed_reason']=='manifest_not_anchored' and r['observed_delegate_calls']==0 for r in roots),
                        'Wrong roots reached old validator')
                require(len(old)==8 and all(not r['observed_accept'] and r['observed_delegate_calls']==1 and
                        r['observed_stage']==r['expected_stage'] for r in old),'Existing validators not preserved')
                positives=[r for r in observations if r['expected_accept']]
                require(len(positives)==3 and all(r['returned_scalar_rows']==800 and r['returned_seed_count']==40 and
                        r['reported_input_hashes_match_precall'] and r['exact_delegated_object_returned'] for r in positives),
                        'Synthetic positive/results contract missing')
                cfg=read_json(sub/'configuration_results.json');metadata=read_json(sub/'metadata_only_anchor.json')
                require(row['configuration_rejections_not_semantic_detections']==4 and len(cfg)==4 and
                        all(r['TrustConfigurationError'] and r['delegate_calls']==0 and not r['semantic_negative_detection_credited'] for r in cfg),
                        'Configuration errors conflated with semantic negatives')
                require(metadata['committed_manifest_metadata_anchor_passed'] and not metadata['full_genuine_S01_positive_executed'],
                        'Metadata-only positive promoted')
        worker_sets.append([{k:v for k,v in r.items() if k!='elapsed_seconds'} for r in runs])
        for mode in ('baseline','candidate','mutants'):
            pair=[{k:v for k,v in r.items() if k not in ('elapsed_seconds','optimized_python')} for r in runs if r['mode']==mode]
            require(pair[0]==pair[1],'Normal/optimized non-timing mismatch')
    require(worker_sets[0]==worker_sets[1],'Original/extracted worker non-timing mismatch')
    receipt=read_json(HERE/'standalone_reproduction.json')
    require(receipt['actually_executed'] and receipt['runner_returncode']==0 and receipt['critical_file_count']==9 and
            receipt['fresh_public_dependencies_fetched_and_verified']==14 and receipt['fresh_public_python_sources']==12 and
            receipt['fresh_authority_metadata_files']==2 and receipt['all_six_worker_nontiming_results_match_original'] and
            receipt['all_twelve_detailed_records_byte_identical'] and len(receipt['detailed_matching_files'])==12 and
            not receipt['genuine_S01_full_positive_executed'] and receipt['repository_manifest_positive_is_metadata_only'],
            'Standalone receipt incomplete/overstated')
    for name in receipt['detailed_matching_files']:
        require((HERE/'checks'/name).read_bytes()==(HERE/'standalone/checks'/name).read_bytes(),'Detailed reproduction changed')
    report=builder.REPORT.read_text()
    require('PROVISIONAL: extracted-code rerun not executed yet' not in report and not re.search(r'\{\{[A-Z_]+\}\}',report) and
            'false accepts **relative to' in report and 'Genuine-S01 positive limitation' in report and
            'not atomic I/O' in report and 'No source function copied' in report,'Report provisional or scope caveat missing')
    pairs=BLOCK.findall(report)
    require(len(pairs)==9 and {name for name,_ in pairs}==set(builder.CRITICAL),'Critical inline set mismatch')
    for name,content in pairs:
        require((content+'\n').encode()==(HERE/'proposal'/name).read_bytes()==(HERE/'standalone/extracted'/name).read_bytes(),
                'Inline/actually executed extraction differs: '+name)
        if name.endswith('.py'):require(not any(isinstance(n,ast.Assert) for n in ast.walk(ast.parse(content))),
                                        'Owned critical gate uses optimization-removable assert')
    acquired={}
    for branch,count in (('main',20),('inbox',10)):
        metadata=read_json(HERE/'source_state'/(branch+'_selected.json'))
        require(len(metadata['files'])==metadata['fetched_and_verified']==count,'Acquisition count mismatch')
        for record in metadata['files']:
            data=(HERE/'source_state'/branch/record['path']).read_bytes()
            require(len(data)==record['bytes'] and git_blob(data)==record['blob'],'Acquired source changed')
        acquired[branch]=count
    public=read_json(HERE/'proposal/source_modules.json')
    require(len(public['modules'])==12 and len(public['authority_metadata'])==2,'Dependency closure/metadata incomplete')
    for record in public['modules']+public['authority_metadata']:
        for directory in (HERE/'source_state/main',HERE/'standalone/upstream'):
            data=(directory/record['path']).read_bytes()
            require(len(data)==record['bytes'] and git_blob(data)==record['blob'],'Reviewed/fresh dependency changed')
    policy=public['authority']
    with (HERE/'source_state/main'/policy['inventory']).open(newline='') as stream:
        anchors=[r for r in csv.DictReader(stream) if r['snapshot_artifact_id']=='ART-2217' and r['path']==policy['manifest']]
    require(len(anchors)==1,'Independent metadata anchor missing/ambiguous')
    pin=anchors[0]['sha256'];data=(HERE/'source_state/main'/policy['manifest']).read_bytes()
    require(hashlib.sha256(data).hexdigest()==pin,'Committed manifest metadata check failed')
    observations=read_json(HERE/'checks/baseline_normal/admission_observations.json')
    witness=next(r for r in observations if r['action']=='official_pin')
    require(witness['expected_external_anchor']==pin and witness['precall_input_digests']['manifest']!=pin and
            not witness['manifest_matches_external_anchor_before_call'] and witness['observed_accept'] and
            witness['observed_delegate_calls']==1,'Actual-module unanchored witness absent')
    incoming=read_json(HERE/'incoming_static_privacy.json')
    require(len(incoming['records'])==2 and all(r['static_decode_only'] and not r['source_executed'] and
            r['expanded_email_pattern_matches']==0 and r['expanded_source_syntax_parsed'] for r in incoming['records']),
            'Incoming opaque source not statically scoped/pattern-inspected')
    branches=[p for p in ROOT.rglob('*_branch*.json') if 'source_state' in p.parts]
    require(len(branches)==16,'Expected sixteen minimal branch records')
    for path in branches:
        value=read_json(path);require(set(value)=={'branch','commit','metadata_policy'} and
                                     all(isinstance(v,str) for v in value.values()),'Nonminimal branch metadata')
    contacts=inspect_contact_patterns((str(p.relative_to(ROOT)),p.read_bytes()) for p in builder.selected_files())
    privacy={'all_sixteen_branch_records_structurally_minimal':True,'new009_metadata_minimal_at_creation':True,
             'personal_commit_contacts_or_signed_payloads_in_branch_metadata':0,'unclassified_outgoing_email_pattern_matches':0,
             'incoming_two_encoded_public_launchers_static_decoded_pattern_checked_not_executed':True,
             'allowlisted_historical_synthetic_source_fixture_matches':contacts,'printed_contact_values':False,
             'scope':'Owned packet structural minimization/scoped pattern scan, including known encoded sources; not exhaustive secret detection or security certification'}
    (HERE/'privacy_results.json').write_text(json.dumps(privacy,indent=2)+'\n')
    live={'STATE.json','CLAIM_LEDGER.csv','README.md','WORKFLOW.md','RESEARCH_QUEUE.md','EVIDENCE_INDEX.json','HISTORICAL_ARCHIVE_LOG_MAP.csv'}
    preserved=0
    with zipfile.ZipFile(ROOT/'researcher040282-cycle008-oracle-condition-uniqueness.zip') as archive:
        for member in archive.namelist():
            name=member.removeprefix('researcher_040282/')
            if name not in live:
                require((ROOT/name).is_file() and (ROOT/name).read_bytes()==archive.read(member),'Prior008 nonlive evidence changed: '+name)
                preserved+=1
        for name in ('STATE.json','CLAIM_LEDGER.csv'):
            require((HERE/'previous008_snapshot'/name).read_bytes()==archive.read('researcher_040282/'+name),
                    'Completed008 state/ledger snapshot differs from delivery')
    restoration=read_json(HERE/'historical_restoration.json')
    require(restoration['restored_bytes']==9175 and restoration['restored_content_matches_delivered_member'] and
            not restoration['existing_source_or_log_overwritten'] and not restoration['scientific009_inputs_code_results_changed'] and
            not restoration['historical_science_rerun'] and restoration['user_deleted_legacy_lua_audit_remains_absent'],
            'Administrative restoration overstates scope')
    protected=['2026-09-04_researcher040282_004_complex-ema.md']+['cycle_004/'+name for name in (
        'GateFoundations.lean','FreezeCore.lean','GateProposalBridge.lean','CoherenceEMA.lean','CoherenceDriveBridge.lean',
        'check_cycle.py','compare_source.py')]
    with zipfile.ZipFile(ROOT/'researcher040282-cycle004-complex-ema.zip') as archive:
        for name in protected:require((ROOT/name).read_bytes()==archive.read('researcher_040282/'+name),'Protected004 evidence changed')
    for name in ('README.md','WORKFLOW.md','RESEARCH_QUEUE.md'):
        require('009' in (ROOT/name).read_text() and '010' in (ROOT/name).read_text(),'Root navigation stale')
    index=read_json(ROOT/'EVIDENCE_INDEX.json');require(index['ledger_rows']==114 and index['archive_only_ledger_references']==0,'Index stale')
    for item in index['ledger_evidence']:
        require(item['availability']=='UNPACKED' and item['packet_members'],'Evidence not unpacked')
        for member in item['packet_members']:require((ROOT.parent/member).is_file(),'Unpacked evidence missing')
    return {'current_ledger_rows':114,'prior113_rows_preserved':True,'formal_labels_unchanged':94,
            'original_and_extracted_full_runner_success':True,'original_expected_method_failures_each_mode':4,
            'original_errors_each_mode':0,'guard_common_passes_each_mode':9,'admission_cases_each_suite':18,
            'original_unanchored_accepts_relative_to_proposed_policy':7,'guard_verdict_mismatches':0,
            'early_root_rejections_before_delegation':7,'synthetic_positive_cases':3,'source_hash_schema_rejections_preserved':8,
            'mutants_detected_each_mode':8,'configuration_rejections_separate_each_mode':4,
            'six_worker_nontiming_records_match_reproduction':True,'twelve_detailed_files_match_reproduction':True,
            'critical_inline_files_equal_executed_extracted_sources':9,'verified_acquisition_files_unchanged':acquired,
            'public_python_sources_unchanged':12,'authority_metadata_dependencies_unchanged':2,
            'actual_imported_discovery_validator_no_copied_replaced_functions':True,
            'committed_manifest_positive_is_metadata_only_no_genuine_S01_positive':True,
            'guard_not_installed_or_pipeline_wired_no_authority_issuance':True,
            'source_frozen_pinned_registry_lock_files_unmodified':True,
            'prior008_nonlive_evidence_files_preserved':preserved,'completed008_state_ledger_snapshots_match_delivery':True,
            'protected004_critical_files':len(protected),'one_missing_old_workflow_restored_exactly_no_science_rerun':True,
            'deleted_legacy_lua_audit_remains_absent':True,'all_sixteen_branch_records_minimal':True,
            'two_encoded_incoming_sources_static_only_pattern_checked':True,'unclassified_email_pattern_matches':0,
            'historical_intentionally_synthetic_fixture_addresses_distinguished':2,
            'all_ledger_evidence_unpacked':True,'ledger_reference_count':index['unique_ledger_references'],
            'unpacked_log_count':index['unpacked_log_count'],
            'scope':'Owned packet consistency/privacy, not science reexecution, independent guard review, genuine-S01 positive, full schema/security, actual bundle/certificate or production installation'}


def verify_archive():
    expected={'researcher_040282/'+str(p.relative_to(ROOT)):p for p in builder.selected_files()}
    with zipfile.ZipFile(builder.ARCHIVE) as archive:
        names=archive.namelist();require(archive.testzip() is None and len(names)==len(set(names)),'CRC/duplicate member failure')
        require(set(names)==set(expected),'Archive/workspace selection mismatch')
        contents=[]
        for name,path in expected.items():
            data=archive.read(name);require(data==path.read_bytes(),'Archive differs from workspace: '+name)
            contents.append((name.removeprefix('researcher_040282/'),data))
        inspect_contact_patterns(contents)
    return len(expected)


def main():
    builder.build_report();builder.build_indices();result=preflight();builder.package();verify_archive()
    result.update({'zip_crc_verified':True,'all_members_match_selected_workspace_files':True,
                   'receipt_included_and_final_archive_reverified':True})
    (HERE/'packet_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    builder.package();verify_archive()
    state=read_json(ROOT/'STATE.json');state['handoff_status']='LOCAL_PACKET_CLOSURE_VERIFIED;NOT_UPLOADED'
    (ROOT/'STATE.json').write_text(json.dumps(state,indent=2)+'\n');builder.package()
    try:
        members=verify_archive();preflight();verify_archive()
    except Exception:
        state['handoff_status']='PACKET_CLOSURE_RECHECK_FAILED;DO_NOT_DELIVER'
        (ROOT/'STATE.json').write_text(json.dumps(state,indent=2)+'\n');raise
    print(json.dumps({'validation':result,'final_archive_members':members,
                      'final_archive_bytes':builder.ARCHIVE.stat().st_size,
                      'standalone_report_bytes':builder.REPORT.stat().st_size},indent=2))


if __name__=='__main__':main()
