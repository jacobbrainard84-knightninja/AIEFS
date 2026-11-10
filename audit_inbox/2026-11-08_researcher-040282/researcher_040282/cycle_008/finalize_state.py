"""Finalize observed008 only after actual fresh-note full rerun.
Preserve112 prior ledger rows/94 formal labels; no historical science reexecution.
"""
from pathlib import Path
import csv
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
DATE='2026-09-04'
REPORT=DATE+'_researcher040282_008_oracle-condition-uniqueness.md'


def ledger(path):
    with path.open(newline='') as stream:
        reader=csv.DictReader(stream);return reader.fieldnames,list(reader)


def require(condition,message):
    if not condition:raise RuntimeError(message)


def main():
    result=json.loads((HERE/'checks/cycle_results.json').read_text());science=result['science']
    repeated=json.loads((HERE/'standalone/checks/cycle_results.json').read_text())
    receipt=json.loads((HERE/'standalone_reproduction.json').read_text())
    require(science['all_preregistered_acceptance_conditions_met'] and science==repeated['science'] and
            receipt['actually_executed'] and receipt['runner_returncode']==0 and
            receipt['all_six_worker_nontiming_results_match_original'] and
            receipt['all_fourteen_detailed_census_and_invalid_key_files_byte_identical'],'Incomplete observed reproduction')
    fields,before=ledger(HERE/'previous007_snapshot/CLAIM_LEDGER.csv');_,current=ledger(ROOT/'CLAIM_LEDGER.csv')
    require(len(before)==112 and [row for row in current if row['cycle']!='8']==before,'Prior112 rows changed')
    evidence=['PLAN.md','proposal','review_decision.json','candidate_boundary.json','checks','checks_run.log',
              'standalone_reproduction.json','standalone/checks','standalone/reproduction.log']
    for name in evidence:require((HERE/name).exists(),'Missing observed evidence: '+name)
    claim={'claim_id':'R040282-008-ORACLE-UNIQUE-CONDITION-PROPOSAL','cycle':'8',
           'symbol':'public_oracle_unique_condition_key_contract',
           'statement_or_exact_header':'On main '+science['tested_main']+', known B-F7 actual public compare_twindow_run fails exactly5/12 common contract methods with0 errors; separate one-function full-module candidate passes12/12, normal/-O. All1600 ordered small-table public-API pairings yield244 original false accepts/0 false rejects versus0 candidate mismatches.10 candidate-only invalid-rho cases fail explicitly and8 distinct semantic/input-rewrite mutants detected each mode. Eight inline files extracted;12 reviewed public sources freshly fetched; full runner actually repeated with matching science,6 worker non-timing records and14 detailed census/key files.',
           'evidence_label':'EXECUTABLE_REGRESSION_CHECK',
           'domain_and_scope':'Synthetic six-file CSV/NPZ/status bundles, actual public API with unchanged real scalar/NPZ stages. Unique exact-seed/finite-float-rho keys on both sides, status as value, explicit row counts; no tolerance change. Only condition helper differs;17 other AST nodes/source-cache unchanged. Finite40-by40 table alphabet is not universal CSV or real-study coverage. Logical comparison preserves ignored aux metadata and failed/empty matches; not a200-condition successful-study certificate, production installation, real S01/201-vs200, all malformed data/security, authority validation or new Lean result.',
           'evidence_files':';'.join('cycle_008/'+name for name in evidence),
           'related_work_or_followup':'Known B-F7 previously minimally reproduced by R001, not a novel production-data finding or prior approval of008 code/harness. ART-0076 Supported/unlocked; owner/seat should independently reproduce/accept condition identity and isolated helper integration. Frozen engine/bridge and other findings not combined. Next009 only fresh-checks a separate structurally reported self-supplied-manifest trust-boundary negative control; do not duplicate rate-law sweep/documentation work.',
           'independent_review':'OWN_008_CONTROLS_AND_FRESH_NOTE_REPRODUCTION_ONLY;PRIOR_R001_MECHANISM_NOT_CURRENT_CANDIDATE_APPROVAL',
           'publication':'LOCAL_PREPARED_FOR_OWNER_DATED_AUDIT_INBOX_UPLOAD;NOT_UPLOADED',
           'integration':'SEPARATE_LOCAL_FULL_ORACLE_PROPOSAL_ONLY;NO_INSTALLATION_SOURCE_CACHE_REGISTRY_LOCK_OR_REMOTE_CHANGE'}
    require(set(claim)==set(fields),'Ledger schema mismatch');rows=before+[claim]
    require(len({row['claim_id'] for row in rows})==113 and
            sum(row['evidence_label']=='LEAN_COMPILED' for row in rows)==94,'Evidence-label promotion')
    with (ROOT/'CLAIM_LEDGER.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    state=json.loads((HERE/'previous007_snapshot/STATE.json').read_text())
    review=state['review_scope']
    if 'current007_helper_and_harness_independently_reviewed' in review:
        review['historical007_helper_and_harness_independently_reviewed']=review.pop('current007_helper_and_harness_independently_reviewed')
    review.update({'latest_selected_navigation_commit':'fef8b0262c31cbdd23f9668a55fffb43b2dc1002',
                   'prior_R001_BF7_minimal_mechanism_reproduction_reported':True,
                   'current008_candidate_contract_harness_independently_reviewed':False,
                   'general_TRIAGE_changed_with_other_agent_static_reviews':True})
    decision=json.loads((HERE/'review_decision.json').read_text())
    state.update({
        'last_updated_date':DATE,'timezone':'Atlantic/Reykjavik',
        'current_cycle':8,'current_directory':'cycle_008',
        'current_status':'COMPLETED_LOCAL_ORACLE_UNIQUENESS_PROPOSAL_UNREVIEWED','ledger_rows':113,
        'current_question':'One actual-current-public-API repair proposal for known B-F7 row multiplicity/semantic-key uniqueness, preserving scalar/NPZ comparison and separate authority boundaries.',
        'current_answer':'Original5 intended failing common methods/0 errors; separate one-function candidate12 pass, normal/-O.1600 ordered toy table pairs give244 original false accepts/0 false rejects versus0 candidate mismatches.10 candidate-only invalid-rho cases explicitly fail and8 mutants detected each mode. Full runner reproduced from8 inline files/12 fresh sources with matching6 worker and14 detailed records. No production installation, real S01 or independent approval.',
        'latest_completed_report':REPORT,'optional_supporting_bundle':'researcher040282-cycle008-oracle-condition-uniqueness.zip',
        'artifact_validation_record':'cycle_008/packet_validation.json',
        'handoff_status':'REPORT_AND_SCIENTIFIC_REPRODUCTION_COMPLETE;PACKET_CLOSURE_PENDING',
        'source_refresh':{'branch_for_current_code':'main','commit':science['tested_main'],
                          'selected_files_verified':19,'public_source_closure_files_verified':12,
                          'metadata':'cycle_008/source_state/main_selected.json',
                          'source_execution_scope':'Actual aief_modular package/original oracle and separate full candidate; public compare_twindow_run only. Package imports runner definitions but no runner/simulation entry point called; all12 reviewed closure files verified, not all their functions tested.',
                          'inbox_navigation_commit':'fef8b0262c31cbdd23f9668a55fffb43b2dc1002',
                          'inbox_selected_files':6,'inbox_metadata':'cycle_008/source_state/inbox_selected.json',
                          'targeted_intake_R001_notes_unchanged':True,'general_TRIAGE_changed':True,
                          'new005_006_007_008_named_followup_found_in_selected_navigation':False,
                          'nonduplication_check':'cycle_008/nonduplication_check.json',
                          'scope':'Selected read-only public intake/source/branch review, not exhaustive repository/private coordination or feedback acceptance.'},
        'tool_environment':{'python':result['python'],'packages':{'numpy':result['numpy']},
                            'package_or_compiler_installation_this_cycle':False,'fresh_lean_run_this_cycle':False,
                            'lean_cache_restored_this_cycle':False,
                            'historical_lean_toolchain_record':'cycle_005/completed_004_snapshot/STATE_before_feedback.json'},
        'adversarial_evidence':{'common_contract_methods':12,'public_api_fixtures_each_suite':30,
                               'original_expected_failures_each_mode':5,'original_errors_each_mode':0,
                               'candidate_passes_each_mode':12,'candidate_only_invalid_key_cases_each_mode':10,
                               'mutants_detected_normal':8,'mutants_detected_optimized':8,
                               'setup_errors_credited_as_detections':0,'normal_and_optimized_nontiming_results_match':True,
                               'results':'cycle_008/checks/cycle_results.json','worker_results':'cycle_008/checks/worker_results.json',
                               'original_runner_elapsed_seconds':result['elapsed_seconds']},
        'source_comparison':{'evidence_label':'EXECUTABLE_REGRESSION_CHECK',
                             'scope':'Full public comparator on six-file synthetic bundles, scalar/NPZ gates unchanged and active; no full study/simulation/real data.',
                             'table_sequences_per_side':40,'ordered_table_pairs_each_target_each_mode':1600,
                             'independent_expected_accepts':12,'original_accepted':256,'original_false_accepts':244,
                             'original_false_rejects':0,'candidate_accepted':12,'candidate_mismatches':0,
                             'semantic_key':'exact seed text, finite float(rho); status is value',
                             'key_uniqueness_both_sides':True,'row_count_equality_explicit':True,
                             'numeric_tolerance':0,'randomness':'NONE;deterministic fixtures',
                             'public_source_closure_files_verified_unchanged':12,
                             'test_only_changed_ast_function_nodes':1,'other_top_level_ast_nodes_preserved':17},
        'authority_boundary':{'proposed_oracle_artifact':'ART-0076','current_oracle_status':'Supported',
                              'current_oracle_lock_status':'none','frozen_engine_artifact':'ART-0702',
                              'frozen_source_edited':False,'lock_or_registry_changed':False,'new_helper_installed':False,
                              'source_cache_edited':False,'authority_validation_run':False,'full_equivalence_pipeline_run':False,
                              'candidate_file_identity':'SEPARATE_LOCAL_FULL_ORACLE_PROPOSAL_NOT_AUTHORITY_OR_INSTALLATION',
                              'integration_decision':'OWNER_SEAT_PENDING;ISOLATED_ONE_HELPER_REVIEW_BRANCH_ONLY'},
        'standalone_reproduction':dict(receipt,record='cycle_008/standalone_reproduction.json',report=REPORT),
        'review_scope':review,'independent_review_received':True,'current_cycle_independent_review_received':False,
        'latest_packet_owner_upload_confirmed':False,
        'publication_status':'Prior receipt/94-declaration compilation footprint and minimal B-F7 mechanism reports only.008 candidate/contract locally prepared and self-reproduced; no new independent review, installation, upload or authority certificate.',
        'privacy':{'report':'cycle_008/privacy_results.json','new_metadata_minimal_at_acquisition':True,
                   'branch_metadata_records_expected':14,'no_personal_commit_contacts_or_signed_payloads_in_branch_metadata':True,
                   'historical_two_synthetic_public_fixture_addresses_distinguished':True,
                   'not_exhaustive_secret_detection_or_security_certification':True},
        'evidence_navigation':{'index':'EVIDENCE_INDEX.json','historical_log_map':'HISTORICAL_ARCHIVE_LOG_MAP.csv',
                               'all_ledger_references_unpacked':True,'old_archives_not_nested_or_changed':True,
                               'historical_missing_only_restoration':'cycle_008/historical_restoration.json'},
        'previous_cycle':7,'previous_cycle_evidence':{'completed007_state':'cycle_008/previous007_snapshot/STATE.json',
                                                      'completed007_ledger112':'cycle_008/previous007_snapshot/CLAIM_LEDGER.csv',
                                                      'science_not_rerun_this_cycle':True,
                                                      'completed006_state':'cycle_007/previous006_snapshot/STATE.json',
                                                      'completed006_ledger111':'cycle_007/previous006_snapshot/CLAIM_LEDGER.csv',
                                                      'completed005_ledger109':'cycle_006/previous005_snapshot/CLAIM_LEDGER.csv',
                                                      'completed004_ledger108':'cycle_005/completed_004_snapshot/CLAIM_LEDGER_COMPLETED_004.csv'},
        'completed_this_cycle':['fresh source/targeted feedback and limited public nonduplication/authority check',
                                'preregistered finite semantic-key/count/status contract and fixed falsifiers',
                                'one-function separate full oracle candidate;17 other AST nodes unchanged',
                                'actual full public API red/green normal/-O with unchanged scalar/NPZ stages',
                                '1600-pair census original244false accepts versus0 candidate mismatches',
                                '10 candidate-only invalid keys and8 intended mutants each mode',
                                '8 inline files/12 fresh public sources;full runner actually reproduced;6 workers/14 detailed files match',
                                'prior112 ledger rows/94 formal labels preserved;one bounded008 proposal record',
                                'packet closure requires actual separate receipt before delivery'],
        'not_proved_or_promoted':list(dict.fromkeys(state['not_proved_or_promoted']+decision['not_approved'])),
        'in_progress':None,'research_processes_running':[],
        'next_cycle':9,'next_directory':'cycle_009',
        'next_selected_work':'Fresh-check the candidate assessment-tool self-supplied-manifest trust boundary and isolate one executed negative control if still unaddressed. Structural concern only so far, no false-accept witness yet; avoid rate-law sweep/docs duplication.',
        'immediate_next_action':'On next Continue, fresh-check main/feedback and supplied versus independently pinned manifest/certificate inputs before preregistering009. No real run, frozen-authority edit, campaign, contact or unattended continuation.',
        'remote_changes_by_this_agent':False,'contacted_other_bots':False,'automatic_work_between_turns':False,
    })
    (ROOT/'STATE.json').write_text(json.dumps(state,indent=2)+'\n')
    print('Finalized008:113 unique rows; prior112/94 formal labels preserved; separate local public-oracle proposal only')


if __name__=='__main__':main()
