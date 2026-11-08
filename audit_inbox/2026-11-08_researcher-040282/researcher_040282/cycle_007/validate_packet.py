"""Owned007 packet closeout, not scientific reexecution/independent review.
Requires the original saved historical archives for closeout comparisons. They
are not nested into this packet; scientific reproduction uses the eight-file
standalone note instead. Not arbitrary-code security or full secret detection.
"""
from pathlib import Path
import csv
import hashlib
import json
import re
import zipfile

import build_packet as builder

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
EMAIL = re.compile(rb"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
BLOCK = re.compile(r'<!-- BEGIN_CRITICAL_FILE: ([^>\n]+) -->\n```[^\n]*\n(.*?)\n```\n'
                   r'<!-- END_CRITICAL_FILE: \1 -->', re.S)
FIXTURE = 'cycle_006/source_state/main/tools/redteam/test_rt_claims_hygiene.py'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def read_ledger(path):
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream))


def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def inspect_contact_patterns(items):
    matches = []
    for name, data in items:
        count = len(EMAIL.findall(data))
        if count:
            require(name == FIXTURE and count == 2,
                    'Unclassified outgoing contact pattern (path/count only): ' + name + '/' + str(count))
            require(b'GIT_AUTHOR_NAME": "fixture"' in data and b'GIT_COMMITTER_NAME": "fixture"' in data,
                    'Allowlisted path no longer has synthetic fixture context')
            metadata = json.loads((ROOT / 'cycle_006/source_state/main_selected.json').read_text())
            record = next(row for row in metadata['files'] if row['path'] == 'tools/redteam/test_rt_claims_hygiene.py')
            require(git_blob(data) == record['blob'] and len(data) == record['bytes'],
                    'Public fixture differs from acquired, reviewed source')
            matches.append({'path': name, 'occurrences': count,
                            'classification': 'INTENTIONALLY_SYNTHETIC_PUBLIC_GIT_ENV_FIXTURE;NOT_PERSONAL_COMMIT_METADATA',
                            'source_unmodified_and_acquisition_verified': True,
                            'executed_by_this_cycle': False})
    require(len(matches) == 1, 'Expected one synthetic public fixture path')
    return matches



def preflight():
    state = json.loads((ROOT / 'STATE.json').read_text())
    require(state['current_cycle'] ==7 and state['current_status'] == 'COMPLETED_LOCAL_COMPARATOR_PROPOSAL_UNREVIEWED',
            'Current local-completion state mismatch')
    require(state['in_progress'] is None and state['next_cycle'] ==8 and state['research_processes_running'] ==[],
            'Current resumption/process state mismatch')
    require(state['last_updated_date'] =='2026-09-04' and
            not state['date_provenance']['historical004_execution_date_reconstructed'], 'Date-provenance mismatch')
    require(not state['current_cycle_independent_review_received'] and not state['latest_packet_owner_upload_confirmed'],
            'New review/upload must not be inferred')
    require(not state['remote_changes_by_this_agent'] and not state['contacted_other_bots'] and
            not state['automatic_work_between_turns'], 'Remote/automation boundary mismatch')
    boundary = state['authority_boundary']
    require(boundary['frozen_engine_artifact'] =='ART-0702' and not boundary['frozen_source_edited'] and
            not boundary['lock_or_registry_changed'] and not boundary['new_helper_installed'] and
            not boundary['authority_validation_run'] and not boundary['full_equivalence_pipeline_run'],
            'Proposal must not be promoted to a production/authority repair')
    current = read_ledger(ROOT / 'CLAIM_LEDGER.csv')
    prior = read_ledger(HERE / 'previous006_snapshot/CLAIM_LEDGER.csv')
    prior005 = read_ledger(ROOT / 'cycle_006/previous005_snapshot/CLAIM_LEDGER.csv')
    prior004 = read_ledger(ROOT / 'cycle_005/completed_004_snapshot/CLAIM_LEDGER_COMPLETED_004.csv')
    require(len(current) ==len({row['claim_id'] for row in current}) ==112 and len(prior) ==111 and
            current[:111] ==prior, 'Prior111 rows or current uniqueness changed')
    require(len(prior005) ==109 and prior[:109] ==prior005 and len(prior004) ==108 and
            [row for row in prior005 if row['cycle'] !='5'] ==prior004, 'Historical completion scopes changed')
    require(sum(row['evidence_label'] =='LEAN_COMPILED' for row in current) ==94 and
            current[-1]['evidence_label'] =='EXECUTABLE_REGRESSION_CHECK', 'Evidence-label promotion')
    original = json.loads((HERE / 'checks/cycle_results.json').read_text())
    repeat = json.loads((HERE / 'standalone/checks/cycle_results.json').read_text())
    require(original['science'] ==repeat['science'] and original['science']['all_preregistered_acceptance_conditions_met'],
            'Scientific reproduction incomplete')
    science = original['science']
    require(science['baseline_tests']['failures'] ==4 and science['baseline_tests']['errors'] ==0 and
            science['baseline_false_accepts'] ==220 and science['baseline_false_rejects'] ==0 and
            science['reduced_alphabet_ordered_pairs_each_target'] ==2592 and
            science['candidate_engine_leaf_modular_mismatches'] ==[0,0,0] and
            science['mutants_detected_normal'] ==science['mutants_detected_optimized'] ==8,
            'Preregistered red/green/mutant science missing')
    groups = []
    for base in ('checks', 'standalone/checks'):
        runs = json.loads((HERE / base / 'target_runs.json').read_text())
        require(len(runs) ==10, 'Expected ten actual child configurations')
        require({(row['mode'], row['optimized_python']) for row in runs} ==
                {(mode, flag) for mode in ('baseline','candidate-engine','candidate-leaf','modular-extracted','mutants')
                 for flag in (False,True)}, 'Missing/duplicate target configuration')
        for row in runs:
            require(row['verified_source_files_unchanged'] ==2, 'Source preservation missing')
            if row['mode'] =='mutants':
                require(row['observed_returncode'] ==0 and row['mutants_detected'] ==8 and
                        row['setup_errors_credited_as_detections'] ==0, 'Mutants not semantically detected')
            else:
                require(row['tests_run'] ==11 and row['errors'] ==0 and row['skipped'] ==0 and
                        sum(row['fixture_group_counts'].values()) ==2687, 'Common fixture/suite mismatch')
                if row['mode'] =='baseline':
                    require(row['observed_returncode'] ==1 and row['failures'] ==4 and set(row['failure_methods']) ==
                            {'test_missing_real','test_missing_imag','test_nan_positions','test_reduced_alphabet'},
                            'Wrong original failure signature')
                else:
                    require(row['observed_returncode'] ==0 and row['failures'] ==0, 'Unexpected green failure')
                if row['mode'] =='candidate-engine':
                    require(row['source_boundary']['only_one_function_ast_replaced'] and
                            row['source_boundary']['noncomparison_top_level_nodes_preserved'] ==98 and
                            not row['source_boundary']['authority_certified'], 'Candidate authority boundary missing')
        groups.append([{k:v for k,v in row.items() if k !='elapsed_seconds'} for row in runs])
    require(groups[0] ==groups[1], 'Per-target nontiming reproduction mismatch')
    files = list((HERE / 'checks').glob('*/reduced_alphabet_mismatches.json'))
    require(len(files) ==8, 'Expected eight target census files')
    for path in files:
        require(path.read_bytes() ==(HERE / 'standalone/checks' / path.relative_to(HERE / 'checks')).read_bytes(),
                'Census reproduction differs')
    receipt = json.loads((HERE / 'standalone_reproduction.json').read_text())
    require(receipt['actually_executed'] and receipt['runner_returncode'] ==0 and
            receipt['critical_file_count'] ==8 and receipt['fresh_public_source_files_fetched_and_verified'] ==2 and
            receipt['all_ten_child_nontiming_results_match_original'], 'Standalone receipt incomplete')
    report = builder.REPORT.read_text()
    require('PROVISIONAL: extracted-code rerun not executed yet' not in report and
            'not a frozen-run certificate' in report and 'not a full modular-package import' in report,
            'Report is provisional or overstates scope')
    pairs = BLOCK.findall(report)
    require(len(pairs) ==8 and {name for name,_ in pairs} ==set(builder.CRITICAL), 'Critical block set mismatch')
    for name, content in pairs:
        data = (content+'\n').encode()
        require(data ==(HERE / 'proposal' / name).read_bytes() ==(HERE / 'standalone/extracted' / name).read_bytes(),
                'Inline/actual executed source mismatch: '+name)
    acquired = {}
    for branch, expected in (('main',10),('inbox',6)):
        metadata = json.loads((HERE / 'source_state' / (branch+'_selected.json')).read_text())
        require(len(metadata['files']) ==metadata['fetched_and_verified'] ==expected, 'Acquisition count mismatch')
        for record in metadata['files']:
            data = (HERE / 'source_state' / branch / record['path']).read_bytes()
            require(len(data) ==record['bytes'] and git_blob(data) ==record['blob'], 'Acquired source changed')
        acquired[branch] = expected
    public = json.loads((HERE / 'proposal/source_modules.json').read_text())
    require(len(public['modules']) ==2, 'Two public source dependencies required')
    for record in public['modules']:
        data = (HERE / 'standalone/upstream' / record['path']).read_bytes()
        require(git_blob(data) ==record['blob'] and len(data) ==record['bytes'], 'Fresh public source changed')
    with (HERE / 'source_state/main/registry/artifacts.csv').open(newline='') as stream:
        frozen = [row for row in csv.DictReader(stream) if row['artifact_id'] =='ART-0702']
    require(len(frozen) ==1 and frozen[0]['artifact_status'] =='Frozen' and
            frozen[0]['path'] =='aief_experiment_engine_v1.py' and 'authority.lock.json' in frozen[0]['lock_status'],
            'Frozen-authority policy not acknowledged')
    branch_records = [path for path in ROOT.rglob('*_branch*.json') if 'source_state' in path.parts]
    require(len(branch_records) ==12, 'Expected twelve acquisition branch records')
    for path in branch_records:
        value = json.loads(path.read_text())
        require(set(value) =={'branch','commit','metadata_policy'} and all(isinstance(x,str) for x in value.values()),
                'Nonminimal branch metadata: '+str(path.relative_to(ROOT)))
    matches = inspect_contact_patterns((str(path.relative_to(ROOT)),path.read_bytes()) for path in builder.selected_files())
    privacy = {'all_twelve_branch_records_structurally_minimal':True,'new007_metadata_minimal_at_creation':True,
               'personal_commit_contacts_or_signed_payloads_in_branch_metadata':0,
               'unclassified_outgoing_email_pattern_matches':0,
               'allowlisted_historical_synthetic_source_fixture_matches':matches,
               'printed_contact_values':False,
               'scope':'Owned-packet structural minimization and scoped email-pattern scan; not exhaustive secret detection or arbitrary-code security'}
    (HERE / 'privacy_results.json').write_text(json.dumps(privacy,indent=2)+'\n')
    # Everything in the delivered006 packet except explicitly live root navigation/state
    # must remain unchanged; completed006 root state/ledger also have exact snapshots.
    live = {'STATE.json','CLAIM_LEDGER.csv','README.md','WORKFLOW.md','RESEARCH_QUEUE.md',
            'EVIDENCE_INDEX.json','HISTORICAL_ARCHIVE_LOG_MAP.csv'}
    preserved = 0
    with zipfile.ZipFile(ROOT / 'researcher040282-cycle006-v41-contract-review.zip') as archive:
        for member in archive.namelist():
            relative = member.removeprefix('researcher_040282/')
            if relative not in live:
                require((ROOT / relative).is_file() and (ROOT / relative).read_bytes() ==archive.read(member),
                        'Previously delivered evidence changed: '+relative)
                preserved +=1
        for name in ('STATE.json','CLAIM_LEDGER.csv'):
            require((HERE / 'previous006_snapshot' / name).read_bytes() ==archive.read('researcher_040282/'+name),
                    'Completed006 snapshot mismatch')
    restoration = json.loads((HERE / 'historical_restoration.json').read_text())
    require(restoration['restored_content_matches_delivered_member'] and
            restoration['previously_existing_prior_nonlive_members_changed'] ==0 and
            not restoration['scientific007_inputs_code_results_changed'] and
            not restoration['existing_source_or_log_overwritten'], 'Restoration record overstates scope')
    protected004 = ['2026-09-04_researcher040282_004_complex-ema.md']
    protected004 += ['cycle_004/'+name for name in ('GateFoundations.lean','FreezeCore.lean','GateProposalBridge.lean',
                     'CoherenceEMA.lean','CoherenceDriveBridge.lean','check_cycle.py','compare_source.py')]
    with zipfile.ZipFile(ROOT / 'researcher040282-cycle004-complex-ema.zip') as archive:
        for name in protected004:
            require((ROOT/name).read_bytes() ==archive.read('researcher_040282/'+name), 'Protected004 content changed')
    for name in ('README.md','WORKFLOW.md','RESEARCH_QUEUE.md'):
        require('007' in (ROOT/name).read_text() and '008' in (ROOT/name).read_text(), 'Root navigation stale')
    index = json.loads((ROOT / 'EVIDENCE_INDEX.json').read_text())
    require(index['ledger_rows'] ==112 and index['archive_only_ledger_references'] ==0,
            'Index not synchronized')
    for item in index['ledger_evidence']:
        require(item['availability'] =='UNPACKED' and item['packet_members'], 'Unavailable/unpacked citation')
        for member in item['packet_members']:
            require((ROOT.parent/member).is_file(), 'Unpacked evidence missing: '+member)
    return {'current_ledger_rows':112,'completed004_rows':108,'completed005_rows':109,'completed006_rows':111,
            'prior111_rows_preserved':True,'formal_labels_unchanged':94,
            'actual_original_and_extracted_full_runner_success':True,
            'actual_original_expected_failures_each_mode':4,'original_errors_each_mode':0,
            'conforming_target_passes_each_mode':[11,11,11],
            'reduced_alphabet_pairs_each_target':2592,'original_false_accepts':220,'candidate_mismatches':0,
            'mutants_detected_each_mode':8,'ten_child_nontiming_results_match_reproduction':True,
            'critical_inline_files_equal_executed_extracted_sources':8,
            'verified_acquisition_files_unchanged':acquired,'fresh_public_files_verified_unchanged':2,
            'authority_locked_engine_unmodified_not_installed_or_certified':True,
            'test_candidate_only_one_function_ast_changed_other98_preserved':True,
            'prior_packet_nonlive_evidence_files_preserved':preserved,
            'completed006_state_ledger_snapshots_match_delivery':True,
            'one_missing_historical_workflow_restored_exactly_without_science_rerun':True,
            'protected004_critical_files':len(protected004),
            'all_twelve_branch_records_minimal':True,'unclassified_email_pattern_matches':0,
            'historical_intentionally_synthetic_fixture_addresses_distinguished':2,
            'all_ledger_evidence_unpacked':True,'ledger_reference_count':index['unique_ledger_references'],
            'unpacked_log_count':index['unpacked_log_count'],
            'scope':'Owned-packet consistency/privacy closure, not science rerun, independent approval, arbitrary-code security, actual data census or authority certification'}

def verify_archive():
    expected = {'researcher_040282/' + str(path.relative_to(ROOT)): path for path in builder.selected_files()}
    with zipfile.ZipFile(builder.ARCHIVE) as archive:
        names = archive.namelist()
        require(archive.testzip() is None and len(names) == len(set(names)), 'CRC/duplicate archive member failure')
        require(set(names) == set(expected), 'Archive/workspace file selection mismatch')
        contents = []
        for name, path in expected.items():
            data = archive.read(name)
            require(data == path.read_bytes(), 'Archive member differs from workspace: ' + name)
            contents.append((name.removeprefix('researcher_040282/'), data))
        inspect_contact_patterns(contents)
    return len(expected)



def main():
    builder.build_report()
    builder.build_indices()
    result = preflight()
    builder.package()
    verify_archive()
    result.update({'zip_crc_verified':True,'all_members_match_selected_workspace_files':True,
                   'receipt_included_and_final_archive_reverified':True})
    (HERE / 'packet_validation.json').write_text(json.dumps(result, indent=2) + '\n')
    builder.package()
    verify_archive()
    state_path = ROOT / 'STATE.json'
    state = json.loads(state_path.read_text())
    state['handoff_status'] = 'LOCAL_PACKET_CLOSURE_VERIFIED;NOT_UPLOADED'
    state_path.write_text(json.dumps(state, indent=2) + '\n')
    builder.package()
    try:
        members = verify_archive()
        preflight()
        # Preflight writes an identical deterministic privacy receipt; verify that too.
        verify_archive()
    except Exception:
        state['handoff_status'] = 'PACKET_CLOSURE_RECHECK_FAILED;DO_NOT_DELIVER'
        state_path.write_text(json.dumps(state, indent=2) + '\n')
        raise
    print(json.dumps({'validation':result, 'final_archive_members':members,
                      'final_archive_bytes':builder.ARCHIVE.stat().st_size,
                      'standalone_report_bytes':builder.REPORT.stat().st_size}, indent=2))


if __name__ == '__main__':
    main()
