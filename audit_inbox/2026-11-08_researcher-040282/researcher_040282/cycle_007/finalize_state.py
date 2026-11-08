"""Finalize observed007 proposal evidence; preserve prior111 rows and snapshots.
No scientific reexecution, frozen file edit, contact or remote submission.
"""
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATE = '2026-09-04'
REPORT = DATE + '_researcher040282_007_complex-nan-comparator.md'


def ledger(path):
    with path.open(newline='') as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def main():
    result = json.loads((HERE / 'checks/cycle_results.json').read_text())
    science = result['science']
    repeated = json.loads((HERE / 'standalone/checks/cycle_results.json').read_text())
    receipt = json.loads((HERE / 'standalone_reproduction.json').read_text())
    if not (science['all_preregistered_acceptance_conditions_met'] and science == repeated['science'] and
            receipt['actually_executed'] and receipt['runner_returncode'] ==0 and
            receipt['all_ten_child_nontiming_results_match_original']):
        raise RuntimeError('Incomplete observed reproduction')
    fields, before = ledger(HERE / 'previous006_snapshot/CLAIM_LEDGER.csv')
    _, current = ledger(ROOT / 'CLAIM_LEDGER.csv')
    if len(before) !=111 or [row for row in current if row['cycle'] !='7'] !=before:
        raise RuntimeError('Prior111 rows changed')
    evidence = ['PLAN.md', 'proposal', 'review_decision.json', 'checks', 'checks_run.log',
                'standalone_reproduction.json', 'standalone/checks', 'standalone/reproduction.log']
    for name in evidence:
        if not (HERE / name).exists():
            raise FileNotFoundError(name)
    claim = {'claim_id':'R040282-007-COMPLEX-NAN-PROPOSAL', 'cycle':'7',
             'symbol':'authority_safe_componentwise_exact_comparison',
             'statement_or_exact_header':'On main ' + science['tested_main'] + ', known B-F6 original engine helper fails exactly4/11 common contracts with0 errors in normal/-O mode; reduced complex64/128 alphabet2592 ordered pairs yields220 false accepts and0 false rejects. Standalone componentwise leaf, one-function full-engine memory candidate and AST-extracted existing modular helper each pass11/11 and have0 census mismatches in both modes.8 semantic/input-mutation mutants detected in each mode. Eight inline files extracted,2 public sources freshly fetched, full runner repeated with matching scientific/non-timing results.',
             'evidence_label':'EXECUTABLE_REGRESSION_CHECK',
             'domain_and_scope':'Deterministic finite numeric/string array and scalar predicate contracts, exact shape/dtype/value and per-component NaN semantics, no tolerance. New-file proposal only; ART-0702 frozen engine untouched. Full original engine imported but only predicate called; candidate replaces one AST function; modular helper only extracted. Not production installation, authority/lock certification, full equivalence pipeline, saved-array census, affected production records, universal NumPy/type theorem or Lean result.',
             'evidence_files':';'.join('cycle_007/' + name for name in evidence),
             'related_work_or_followup':'B-F6 known and R001 previously reproduced mechanism; modular helper already contains component split. Owner/seat must independently review and choose authorized new companion/successor/erratum route. Existing max-difference diagnostics not certified. Oracle uniqueness belongs to a separate future finding/branch.',
             'independent_review':'OWN_007_CONTROLS_ONLY;R001_CONFIRMED_PRIOR_MECHANISM_NOT_THIS_PROPOSAL;NO_NEW_HELPER_APPROVAL',
             'publication':'LOCAL_PREPARED_FOR_OWNER_DATED_AUDIT_INBOX_UPLOAD;NOT_UPLOADED',
             'integration':'NEW_FILE_PROPOSAL_ONLY;FROZEN_ART0702_UNCHANGED;NO_LOCK_REGISTRY_REMOTE_CHANGE_OR_INSTALLATION'}
    if set(claim) !=set(fields):
        raise RuntimeError('Ledger schema mismatch')
    rows = before + [claim]
    if len({row['claim_id'] for row in rows}) !=112 or sum(row['evidence_label']=='LEAN_COMPILED' for row in rows) !=94:
        raise RuntimeError('Unexpected claim/formal-label promotion')
    with (ROOT / 'CLAIM_LEDGER.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    state = json.loads((HERE / 'previous006_snapshot/STATE.json').read_text())
    review_scope = state['review_scope']
    review_scope['historical_intake_receipt'] = review_scope.pop('owner_receipt')
    review_scope.update({'historical_intake_inventory_not_a_new_inbox_census':True,
                         'latest_selected_navigation_commit':'e72bdd2b2c29d815740c321df0ad8703de378e37',
                         'prior_R001_BF6_mechanism_reproduction_reported':True,
                         'current007_helper_and_harness_independently_reviewed':False})
    limits = state['not_proved_or_promoted']
    decision = json.loads((HERE / 'review_decision.json').read_text())
    state.update({
        'last_updated_date':DATE, 'timezone':'Atlantic/Reykjavik',
        'date_provenance':{'session_supplied_preparation_date':DATE,
                           'prior_owner_correspondence_handoff_label':'2026-11-08',
                           'historical004_execution_date_reconstructed':False,
                           'historical006_notice':'cycle_006/ADMINISTRATIVE_PROVENANCE.md',
                           'note':'Session preparation labels and prior owner/repository labels are separate; no chronology inferred from runtime clocks/compiler builds. Earlier scientific protocols/seeds/reports preserved.'},
        'current_cycle':7, 'current_directory':'cycle_007',
        'current_status':'COMPLETED_LOCAL_COMPARATOR_PROPOSAL_UNREVIEWED',
        'ledger_rows':112,
        'current_question':'One authority-safe current-main repair proposal for known B-F6 complex-NaN false equality, preserving frozen engine and existing exact shape/dtype policy.',
        'current_answer':'Original engine4 intended contract failures/0 errors; candidate-engine/leaf/modular-extracted11 pass each, normal/-O. Reduced2592 ordered pairs give original220 false accepts versus0 for three conforming targets.8 mutants detected each mode. Full runner reproduced from8 inline files/2 fresh public sources. Proposal not installed or authority-approved; no simulation/full equivalence run or real-array census.',
        'latest_completed_report':REPORT,
        'optional_supporting_bundle':'researcher040282-cycle007-complex-nan-comparator.zip',
        'artifact_validation_record':'cycle_007/packet_validation.json',
        'handoff_status':'REPORT_AND_SCIENTIFIC_REPRODUCTION_COMPLETE;PACKET_CLOSURE_PENDING',
        'source_refresh':{'branch_for_current_code':'main','commit':science['tested_main'],
                          'selected_files_verified':10,'public_source_files_verified_and_exercised':2,
                          'metadata':'cycle_007/source_state/main_selected.json',
                          'source_execution_scope':'Full original engine import; comparison-only one-function memory candidate; modular equality helper AST-extracted, not full package imported.',
                          'inbox_navigation_commit':'e72bdd2b2c29d815740c321df0ad8703de378e37',
                          'inbox_selected_files':6,'inbox_metadata':'cycle_007/source_state/inbox_selected.json',
                          'selected_notes_unchanged_since_previous_cycle':True,
                          'new005_006_007_named_followup_found_in_selected_navigation':False,
                          'scope':'Selected read-only public source/intake review, not exhaustive private-feedback, repository, artifact or provenance acceptance.'},
        'tool_environment':{'python':result['python'],'packages':{'numpy':result['numpy']},
                            'package_or_compiler_installation_this_cycle':False,
                            'fresh_lean_run_this_cycle':False,'lean_cache_restored_this_cycle':False,
                            'historical_lean_toolchain_record':'cycle_005/completed_004_snapshot/STATE_before_feedback.json'},
        'adversarial_evidence':{'common_contract_methods':11,'fixtures_each_suite':2687,
                                'baseline_expected_failures':4,'baseline_errors':0,
                                'candidate_engine_leaf_modular_pass_counts':[11,11,11],
                                'mutants_detected_normal':8,'mutants_detected_optimized':8,
                                'setup_errors_credited_as_detections':0,
                                'normal_and_optimized_nontiming_results_match':True,
                                'results':'cycle_007/checks/cycle_results.json',
                                'target_results':'cycle_007/checks/target_runs.json',
                                'original_runner_elapsed_seconds':result['elapsed_seconds']},
        'source_comparison':{'evidence_label':'EXECUTABLE_REGRESSION_CHECK',
                             'scope':'Predicate tests only. Two reviewed public files unchanged; original/candidate full-engine modules imported, existing modular predicate only AST-extracted.',
                             'reduced_alphabet_pairs_each_target':2592,'baseline_false_accepts':220,
                             'baseline_false_rejects':0,'three_conforming_target_mismatches':[0,0,0],
                             'numeric_tolerance':0,'randomness':'NONE;deterministic fixtures',
                             'public_source_files_verified_unchanged':2,
                             'test_only_changed_ast_function_nodes':1,'other_top_level_ast_nodes_preserved':98},
        'authority_boundary':{'frozen_engine_artifact':'ART-0702',
                              'registry_policy_read':'cycle_007/source_state/main/registry/artifacts.csv:703',
                              'frozen_source_edited':False,'lock_or_registry_changed':False,
                              'new_helper_installed':False,'authority_validation_run':False,
                              'full_equivalence_pipeline_run':False,
                              'candidate_file_identity':'SYNTHETIC_COMPARISON_ONLY_MEMORY_CANDIDATE_NOT_AUTHORITY',
                              'integration_decision':'OWNER_SEAT_PENDING;NEW_COMPANION_OR_AUTHORIZED_SUCCESSOR_ONLY'},
        'standalone_reproduction':dict(receipt,record='cycle_007/standalone_reproduction.json',report=REPORT),
        'review_scope':review_scope,'independent_review_received':True,
        'current_cycle_independent_review_received':False,'latest_packet_owner_upload_confirmed':False,
        'publication_status':'Prior receipt/94-declaration compilation footprint report and B-F6 mechanism confirmation only.007 proposal locally prepared; no007 independent review, installation, upload, main integration or new authority certificate.',
        'privacy':{'report':'cycle_007/privacy_results.json',
                   'new_metadata_minimal_at_acquisition':True,'branch_metadata_records_expected':12,
                   'no_personal_commit_contacts_or_signed_payloads_in_branch_metadata':True,
                   'historical_two_synthetic_public_fixture_addresses_distinguished':True,
                   'not_exhaustive_secret_detection_or_security_certification':True},
        'evidence_navigation':{'index':'EVIDENCE_INDEX.json','historical_log_map':'HISTORICAL_ARCHIVE_LOG_MAP.csv',
                               'all_ledger_references_unpacked':True,'old_archives_not_nested_or_changed':True},
        'previous_cycle':6,
        'previous_cycle_evidence':{'completed006_state':'cycle_007/previous006_snapshot/STATE.json',
                                    'completed006_ledger111':'cycle_007/previous006_snapshot/CLAIM_LEDGER.csv',
                                    'science_not_rerun_this_cycle':True,
                                    'completed005_ledger109':'cycle_006/previous005_snapshot/CLAIM_LEDGER.csv',
                                    'completed004_ledger108':'cycle_005/completed_004_snapshot/CLAIM_LEDGER_COMPLETED_004.csv'},
        'completed_this_cycle':['fresh-main/feedback read-only check; known issue still present; frozen artifact policy acknowledged',
                                 'preregistered exact per-component/shape/dtype/input-preservation contract and fixed falsifiers',
                                 'new standalone leaf and controlled one-function non-authority memory candidate',
                                 'actual red/green/optimized tests with220 reduced-alphabet original false accepts versus0 after',
                                 'eight intended semantic/input-mutation detections in both modes',
                                 'eight inline files extracted;two fresh public sources;complete runner actually reproduced',
                                 'prior111 ledger rows/94 formal labels preserved;one bounded007 proposal record',
                                 'packet closure requires separate actual receipt before delivery'],
        'not_proved_or_promoted':list(dict.fromkeys(limits+decision['not_approved'])),
        'in_progress':None,'research_processes_running':[],
        'next_cycle':8,'next_directory':'cycle_008',
        'next_selected_work':'Fresh-check one public-oracle duplicate/semantic-key uniqueness repair on then-current main; failing-before/passing-after synthetic tests on a separate proposal. If resolved, avoid duplicate work and choose a load-bearing scientific prerequisite.',
        'immediate_next_action':'On next Continue, check latest main/feedback before preregistering008. No real S01, merged uploader rework, frozen edit or unattended continuation.',
        'remote_changes_by_this_agent':False,'contacted_other_bots':False,'automatic_work_between_turns':False,
    })
    if (HERE / 'historical_restoration.json').exists():
        state['evidence_navigation']['historical_missing_only_restoration'] = 'cycle_007/historical_restoration.json'
    (ROOT / 'STATE.json').write_text(json.dumps(state,indent=2)+'\n')
    print('Finalized007:112 unique rows; prior111 and94 formal labels preserved; new-file proposal only')


if __name__ == '__main__':
    main()
