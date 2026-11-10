"""Owned008 packet consistency/privacy closeout, not scientific reexecution.
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
RED={'test_alias_duplicate','test_candidate_duplicate','test_oracle_duplicate','test_shared_duplicate','test_status_in_key'}


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
    require(state['current_cycle']==8 and state['current_status']=='COMPLETED_LOCAL_ORACLE_UNIQUENESS_PROPOSAL_UNREVIEWED',
            'Current local completion state mismatch')
    require(state['in_progress'] is None and state['next_cycle']==9 and state['research_processes_running']==[],
            'Resumption/process state mismatch')
    require(state['last_updated_date']=='2026-09-04' and
            not state['date_provenance']['historical004_execution_date_reconstructed'],'Preparation/history date mismatch')
    require(not state['current_cycle_independent_review_received'] and not state['latest_packet_owner_upload_confirmed'] and
            not state['remote_changes_by_this_agent'] and not state['contacted_other_bots'] and
            not state['automatic_work_between_turns'],'Review/upload/remote authorization mismatch')
    boundary=state['authority_boundary']
    require(boundary['proposed_oracle_artifact']=='ART-0076' and boundary['current_oracle_status']=='Supported' and
            boundary['current_oracle_lock_status']=='none' and boundary['frozen_engine_artifact']=='ART-0702' and
            not any(boundary[key] for key in ('frozen_source_edited','lock_or_registry_changed','new_helper_installed',
                                             'source_cache_edited','authority_validation_run','full_equivalence_pipeline_run')),
            'Local candidate promoted or source/authority boundary changed')
    require(not Path('/home/user/audit').exists(),'User-deleted legacy Lua audit must remain absent')
    current=read_ledger(ROOT/'CLAIM_LEDGER.csv');prior=read_ledger(HERE/'previous007_snapshot/CLAIM_LEDGER.csv')
    prior006=read_ledger(ROOT/'cycle_007/previous006_snapshot/CLAIM_LEDGER.csv')
    prior005=read_ledger(ROOT/'cycle_006/previous005_snapshot/CLAIM_LEDGER.csv')
    prior004=read_ledger(ROOT/'cycle_005/completed_004_snapshot/CLAIM_LEDGER_COMPLETED_004.csv')
    require(len(current)==len({row['claim_id'] for row in current})==113 and len(prior)==112 and current[:112]==prior,
            'Prior112 rows or current uniqueness changed')
    require(len(prior006)==111 and prior[:111]==prior006 and len(prior005)==109 and prior[:109]==prior005 and
            len(prior004)==108 and [row for row in prior005 if row['cycle']!='5']==prior004,'Historical completion scopes changed')
    require(sum(row['evidence_label']=='LEAN_COMPILED' for row in current)==94 and
            current[-1]['evidence_label']=='EXECUTABLE_REGRESSION_CHECK' and current[-1]['cycle']=='8','Label promotion')
    original=read_json(HERE/'checks/cycle_results.json');repeated=read_json(HERE/'standalone/checks/cycle_results.json')
    science=original['science']
    require(science==repeated['science'] and science['all_preregistered_acceptance_conditions_met'] and
            science['common_contract_methods']==12 and science['original_expected_failures_each_mode']==5 and
            science['original_errors_each_mode']==0 and science['candidate_passes_each_mode']==12 and
            science['public_api_table_pairs_each_target']==1600 and science['independent_expected_accepts']==12 and
            science['original_accepted']==256 and science['original_false_accepts']==244 and
            science['original_false_rejects']==0 and science['candidate_accepted']==12 and science['candidate_mismatches']==0 and
            science['candidate_only_invalid_key_cases_each_mode']==10 and science['mutants_detected_each_mode']==8,
            'Scientific outcome differs from fixed protocol')
    workers=[]
    for base in ('checks','standalone/checks'):
        directory=HERE/base;runs=read_json(directory/'worker_results.json')
        require(len(runs)==6 and {(r['mode'],r['optimized_python']) for r in runs}==
                {(mode,opt) for mode in ('baseline','candidate','mutants') for opt in (False,True)},'Missing/duplicate workers')
        for row in runs:
            name=row['mode']+('_optimized' if row['optimized_python'] else '_normal');sub=directory/name
            raw=read_json(sub/'result.json')
            require({k:v for k,v in row.items() if k!='observed_returncode'}==raw,'Child and recorded worker disagree')
            require(row['public_sources_unchanged']==12,'Public package closure preservation missing')
            if row['mode']=='mutants':
                require(row['observed_returncode']==0 and row['detected']==8 and row['setup_errors_credited']==0 and
                        all(r['detected'] for r in row['records']) and len({r['mutant'] for r in row['records']})==8 and
                        [r['reason'] for r in row['records']]==['verdict']*7+['input_preservation'],
                        'Wrong/missing mutant mechanism')
                continue
            require(row['tests_run']==12 and row['errors']==row['skipped']==0 and
                    len(row['fixture_group_counts'])==12 and sum(row['fixture_group_counts'].values())==30 and
                    row['boundary']['actual_public_api'] and not row['boundary']['simulation_or_runner_entrypoints_called'],
                    'Common suite/API scope mismatch')
            if row['mode']=='baseline':
                require(row['observed_returncode']==1 and row['failures']==5 and set(row['failure_methods'])==RED and
                        row['candidate_only_invalid_key_cases']==0,'Wrong original red signature')
                require((directory/(name+'.log')).read_text().count('expected=False, observed=True')==7,
                        'Original fails for unexpected reasons')
                want=(256,244,0)
            else:
                require(row['observed_returncode']==0 and row['failures']==0 and row['candidate_only_invalid_key_cases']==10 and
                        row['boundary']['only_changed_function']=='_compare_condition_coverage' and
                        row['boundary']['other_top_level_nodes_preserved']==17 and not row['boundary']['proposal_installed'],
                        'Candidate contract/source boundary failure')
                invalid=read_json(sub/'invalid_key_results.json')
                require(len(invalid)==10 and all(r['status']=='failed' and
                        any('invalid finite rho' in msg for msg in r['errors']) for r in invalid),'Invalid keys not explicitly rejected')
                want=(12,0,0)
            records=read_json(sub/'table_census.json');bad=read_json(sub/'census_mismatches.json')
            seq=read_json(sub/'sequence_definitions.json')
            require(len(seq)==40 and [len(r) for r in seq]==[0]+[1]*3+[2]*9+[3]*27 and len(records)==1600,
                    'Census domain/call inventory mismatch')
            require([(r['candidate_sequence'],r['oracle_sequence']) for r in records]==
                    [(i,j) for i in range(40) for j in range(40)] and
                    all(isinstance(r['expected'],bool) and isinstance(r['observed'],bool) for r in records),
                    'Census pairs incomplete/duplicated or verdicts invalid')
            require(sum(r['expected'] for r in records)==12 and bad==[r for r in records if r['expected']!=r['observed']],
                    'Recorded expected accepts/mismatches inconsistent')
            accepted=sum(r['observed'] for r in records)
            fa=sum(not r['expected'] and r['observed'] for r in records)
            fr=sum(r['expected'] and not r['observed'] for r in records)
            require((accepted,fa,fr)==want and row['census']==
                    {'ordered_table_pairs':1600,'expected_passes':12,'observed_passes':accepted,
                     'mismatches':fa+fr,'false_accepts':fa,'false_rejects':fr},'Observed census summary inconsistent')
        stripped=[{k:v for k,v in row.items() if k!='elapsed_seconds'} for row in runs];workers.append(stripped)
        for mode in ('baseline','candidate','mutants'):
            pair=[{k:v for k,v in row.items() if k not in ('elapsed_seconds','optimized_python')} for row in runs if row['mode']==mode]
            require(pair[0]==pair[1],'Normal/optimized results differ')
    require(workers[0]==workers[1],'Original/fresh extracted non-timing worker results differ')
    receipt=read_json(HERE/'standalone_reproduction.json')
    require(receipt['actually_executed'] and receipt['runner_returncode']==0 and receipt['critical_file_count']==8 and
            receipt['fresh_public_source_files_fetched_and_verified']==12 and receipt['scientific_summary_matches_original'] and
            receipt['all_six_worker_nontiming_results_match_original'] and
            receipt['all_fourteen_detailed_census_and_invalid_key_files_byte_identical'] and
            len(receipt['detailed_matching_files'])==14,'Standalone receipt incomplete')
    for name in receipt['detailed_matching_files']:
        require((HERE/'checks'/name).read_bytes()==(HERE/'standalone/checks'/name).read_bytes(),'Detailed reproduction differs')
    report=builder.REPORT.read_text()
    require('PROVISIONAL: extracted-code rerun not executed yet' not in report and
            not re.search(r'\{\{[A-Z_]+\}\}',report) and
            'Logical equality is not a successful200-condition' in report and
            'No runner/simulation entry point' in report,'Report provisional or scope caveats missing')
    pairs=BLOCK.findall(report)
    require(len(pairs)==8 and {name for name,_ in pairs}==set(builder.CRITICAL),'Critical block set mismatch')
    for name,content in pairs:
        require((content+'\n').encode()==(HERE/'proposal'/name).read_bytes()==(HERE/'standalone/extracted'/name).read_bytes(),
                'Inline/actually executed extraction source mismatch: '+name)
        if name.endswith('.py'):require(not any(isinstance(n,ast.Assert) for n in ast.walk(ast.parse(content))),
                                        'Owned critical acceptance contains optimization-removable assert')
    acquired={}
    for branch,count in (('main',19),('inbox',6)):
        metadata=read_json(HERE/'source_state'/(branch+'_selected.json'))
        require(len(metadata['files'])==metadata['fetched_and_verified']==count,'Acquisition count mismatch')
        for record in metadata['files']:
            data=(HERE/'source_state'/branch/record['path']).read_bytes()
            require(git_blob(data)==record['blob'] and len(data)==record['bytes'],'Acquired source changed')
        acquired[branch]=count
    public=read_json(HERE/'proposal/source_modules.json');require(len(public['modules'])==12,'Package closure incomplete')
    for record in public['modules']:
        for directory in (HERE/'source_state/main',HERE/'standalone/upstream'):
            data=(directory/record['path']).read_bytes()
            require(git_blob(data)==record['blob'] and len(data)==record['bytes'],'Reviewed or fresh public module changed')
    trees=[ast.parse((HERE/'source_state/main'/public['oracle']).read_text()),ast.parse((HERE/'proposal/oracle_candidate.py').read_text())]
    def other_nodes(tree):return [ast.dump(n,include_attributes=False) for n in tree.body
                                  if not (isinstance(n,ast.FunctionDef) and n.name=='_compare_condition_coverage')]
    require(other_nodes(trees[0])==other_nodes(trees[1]) and len(other_nodes(trees[0]))==17 and
            all(sum(isinstance(n,ast.FunctionDef) and n.name=='_compare_condition_coverage' for n in t.body)==1 for t in trees),
            'One-function candidate AST boundary changed')
    with (HERE/'source_state/main/registry/artifacts.csv').open(newline='') as stream:
        artifacts=list(csv.DictReader(stream))
    oracle=next(r for r in artifacts if r['artifact_id']=='ART-0076')
    engine=next(r for r in artifacts if r['artifact_id']=='ART-0702')
    require(oracle['artifact_status']=='Supported' and oracle['lock_status']=='none' and
            engine['artifact_status']=='Frozen' and 'authority.lock.json' in engine['lock_status'],'Registry policy not acknowledged')
    branches=[p for p in ROOT.rglob('*_branch*.json') if 'source_state' in p.parts]
    require(len(branches)==14,'Expected fourteen minimal branch records')
    for path in branches:
        value=read_json(path);require(set(value)=={'branch','commit','metadata_policy'} and
                                     all(isinstance(v,str) for v in value.values()),'Nonminimal branch metadata')
    contacts=inspect_contact_patterns((str(p.relative_to(ROOT)),p.read_bytes()) for p in builder.selected_files())
    privacy={'all_fourteen_branch_records_structurally_minimal':True,'new008_metadata_minimal_at_creation':True,
             'personal_commit_contacts_or_signed_payloads_in_branch_metadata':0,'unclassified_outgoing_email_pattern_matches':0,
             'allowlisted_historical_synthetic_source_fixture_matches':contacts,'printed_contact_values':False,
             'scope':'Owned-packet structural minimization and scoped pattern scan; not exhaustive secret detection or arbitrary-code security'}
    (HERE/'privacy_results.json').write_text(json.dumps(privacy,indent=2)+'\n')
    live={'STATE.json','CLAIM_LEDGER.csv','README.md','WORKFLOW.md','RESEARCH_QUEUE.md','EVIDENCE_INDEX.json','HISTORICAL_ARCHIVE_LOG_MAP.csv'}
    preserved=0
    with zipfile.ZipFile(ROOT/'researcher040282-cycle007-complex-nan-comparator.zip') as archive:
        for member in archive.namelist():
            name=member.removeprefix('researcher_040282/')
            if name not in live:
                require((ROOT/name).is_file() and (ROOT/name).read_bytes()==archive.read(member),'Prior delivered nonlive evidence changed: '+name)
                preserved+=1
        for name in ('STATE.json','CLAIM_LEDGER.csv'):
            require((HERE/'previous007_snapshot'/name).read_bytes()==archive.read('researcher_040282/'+name),
                    'Completed007 state/ledger snapshot differs from delivery')
    restoration=read_json(HERE/'historical_restoration.json')
    require(restoration['restored_bytes']==9175 and restoration['restored_content_matches_delivered_member'] and
            not restoration['existing_source_or_log_overwritten'] and not restoration['scientific008_inputs_code_results_changed'] and
            not restoration['historical_science_rerun'] and restoration['user_deleted_legacy_lua_audit_remains_absent'],
            'Administrative restoration overstates scope')
    protected004=['2026-09-04_researcher040282_004_complex-ema.md']+[
        'cycle_004/'+name for name in ('GateFoundations.lean','FreezeCore.lean','GateProposalBridge.lean','CoherenceEMA.lean',
                                      'CoherenceDriveBridge.lean','check_cycle.py','compare_source.py')]
    with zipfile.ZipFile(ROOT/'researcher040282-cycle004-complex-ema.zip') as archive:
        for name in protected004:require((ROOT/name).read_bytes()==archive.read('researcher_040282/'+name),'Protected004 changed')
    for name in ('README.md','WORKFLOW.md','RESEARCH_QUEUE.md'):
        require('008' in (ROOT/name).read_text() and '009' in (ROOT/name).read_text(),'Root navigation stale')
    index=read_json(ROOT/'EVIDENCE_INDEX.json')
    require(index['ledger_rows']==113 and index['archive_only_ledger_references']==0,'Index stale')
    for item in index['ledger_evidence']:
        require(item['availability']=='UNPACKED' and item['packet_members'],'Evidence not available unpacked')
        for member in item['packet_members']:require((ROOT.parent/member).is_file(),'Unpacked citation missing')
    return {'current_ledger_rows':113,'prior112_rows_preserved':True,'formal_labels_unchanged':94,
            'actual_original_and_extracted_full_runner_success':True,'original_expected_failures_each_mode':5,
            'original_errors_each_mode':0,'candidate_passes_each_mode':12,'public_api_census_pairs_each_target':1600,
            'original_false_accepts':244,'original_false_rejects':0,'candidate_mismatches':0,
            'candidate_only_invalid_key_cases_each_mode':10,'mutants_detected_each_mode':8,
            'six_worker_nontiming_results_match_reproduction':True,'fourteen_detailed_files_match_reproduction':True,
            'critical_inline_files_equal_executed_extracted_sources':8,'verified_acquisition_files_unchanged':acquired,
            'fresh_public_package_source_files_verified_unchanged':12,'only_one_function_ast_changed_other17_preserved':True,
            'supported_unlocked_oracle_candidate_not_installed_or_authority_certified':True,
            'frozen_engine_and_pinned_bridge_unmodified':True,'prior_packet_nonlive_evidence_files_preserved':preserved,
            'completed007_state_ledger_snapshots_match_delivery':True,'protected004_critical_files':len(protected004),
            'one_missing_old_workflow_restored_exactly_no_science_rerun':True,'deleted_legacy_lua_audit_remains_absent':True,
            'all_fourteen_branch_records_minimal':True,'unclassified_email_pattern_matches':0,
            'historical_intentionally_synthetic_fixture_addresses_distinguished':2,
            'all_ledger_evidence_unpacked':True,'ledger_reference_count':index['unique_ledger_references'],
            'unpacked_log_count':index['unpacked_log_count'],
            'scope':'Owned packet consistency/privacy, not science rerun, independent review, full schema/security, real data impact or authority certification'}


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
