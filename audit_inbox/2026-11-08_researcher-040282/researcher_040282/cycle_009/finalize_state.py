"""Finalize observed009 after actual nine-file/fresh14-dependency reproduction.
Add one bounded claim; preserve prior113 rows/94 formal labels/history.
"""
from pathlib import Path
import csv
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
DATE='2026-09-04'
REPORT=DATE+'_researcher040282_009_anchored-cohort-admission.md'


def require(condition,message):
    if not condition:raise RuntimeError(message)


def ledger(path):
    with path.open(newline='') as stream:
        reader=csv.DictReader(stream);return reader.fieldnames,list(reader)


def main():
    result=json.loads((HERE/'checks/cycle_results.json').read_text());science=result['science']
    repeated=json.loads((HERE/'standalone/checks/cycle_results.json').read_text())
    receipt=json.loads((HERE/'standalone_reproduction.json').read_text())
    require(science['all_preregistered_acceptance_conditions_met'] and science==repeated['science'] and
            receipt['actually_executed'] and receipt['runner_returncode']==0 and
            receipt['critical_file_count']==9 and receipt['fresh_public_dependencies_fetched_and_verified']==14 and
            receipt['all_six_worker_nontiming_results_match_original'] and receipt['all_twelve_detailed_records_byte_identical'],
            'Incomplete observed reproduction')
    fields,before=ledger(HERE/'previous008_snapshot/CLAIM_LEDGER.csv');_,current=ledger(ROOT/'CLAIM_LEDGER.csv')
    require(len(before)==113 and [r for r in current if r['cycle']!='9']==before,'Prior113 rows changed')
    evidence=['PLAN.md','proposal','review_decision.json','nonduplication_check.json','checks','checks_run.log',
              'standalone_reproduction.json','standalone/checks','standalone/reproduction.log','source_state/main_selected.json']
    for name in evidence:require((HERE/name).exists(),'Missing observed evidence: '+name)
    claim={'claim_id':'R040282-009-CALLER-ANCHORED-ADMISSION-PROPOSAL','cycle':'9',
           'symbol':'caller_anchored_cohort_admission',
           'statement_or_exact_header':'On main '+science['tested_main']+', actual imported discover_inputs/validate_run accepts7 unanchored variants relative to explicitly proposed external-root/S01 admission policy among18 declared cases. Baseline4/9intended failing methods/0errors; new-file explicit caller-anchor guard delegates unchanged validator and passes9/9, normal/-O, rejecting7roots before delegation while preserving3test-owned synthetic positives/8source hash-schema rejections.8wrong models detected,4malformed-policy configuration rejections separately. Nine inline files extracted/14fresh public dependencies; full runner repeated with matching science/6workers/12detailed records.',
           'evidence_label':'EXECUTABLE_REGRESSION_CHECK',
           'domain_and_scope':'Synthetic40seed x5rho x4branch five-file input,800scalar/200status rows,2600readable NPZ keys independently inspected. Actual source functions not copied/replaced/edited. Proposed root is explicit caller assumption, not an existing validate_run argument; byte lineage under trusted-root/unchanged-input/digest-binding assumptions only. ART-2217 committed-manifest positive is METADATA ONLY, no genuine five-file S01 positive, real trajectories, run_analysis/main/writer/CLI/bundle/certificate issuance. No physics/crypto/universal Python theorem, full schema/NPZ-by-validator/lineage/TOCTOU security or Lean result. Guard not installed/wired into pipeline.',
           'evidence_files':';'.join('cycle_009/'+name for name in evidence),
           'related_work_or_followup':'Known GPT6-P1; new colleague full-schema report already claims copied-function acceptance/downstream results, not rerun or approved here. This cycle independently exercises actual full module and tests caller-anchor companion, not novelty. Owner/seat must accept trust-source/policy, independently review and authorize integration/real positive. Preserve unaudited refusal/frozen sources. Next010 fresh-checks actual history/delay/phase semantics and a load-bearing buffer lemma, no duplicate rate-law/docs work.',
           'independent_review':'PRIOR_LEAD_ACTUAL_MODULE_WITNESS_OBSERVED_BY_THIS_AGENT;OWN_009_GUARD_CONTRACT_CONTROLS_ONLY;NO_INDEPENDENT_SEAT_APPROVAL',
           'publication':'LOCAL_PREPARED_FOR_OWNER_DATED_AUDIT_INBOX_UPLOAD;NOT_UPLOADED',
           'integration':'NEW_FILE_COMPANION_ONLY;ALL_UPSTREAM_UNCHANGED;CURRENT_CLI_PIPELINE_NOT_WIRED;NO_FROZEN_REGISTRY_LOCK_REMOTE_OR_INSTALLATION_CHANGE'}
    require(set(claim)==set(fields),'Ledger schema mismatch');rows=before+[claim]
    require(len({r['claim_id'] for r in rows})==114 and sum(r['evidence_label']=='LEAN_COMPILED' for r in rows)==94,
            'Claim/formal-label promotion')
    with (ROOT/'CLAIM_LEDGER.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    state=json.loads((HERE/'previous008_snapshot/STATE.json').read_text())
    review=state['review_scope']
    if 'current008_candidate_contract_harness_independently_reviewed' in review:
        review['historical008_candidate_contract_harness_independently_reviewed']=review.pop('current008_candidate_contract_harness_independently_reviewed')
    if 'general_TRIAGE_changed_with_other_agent_static_reviews' in review:
        review['historical008_general_TRIAGE_changed_with_other_agent_static_reviews']=review.pop('general_TRIAGE_changed_with_other_agent_static_reviews')
    review.update({'latest_selected_navigation_commit':'908639412c5560cc2c308b089ade0679c846b15c',
                   'general_TRIAGE_changed_since008':False,'new_colleague_copied_function_runtime_report_found':True,
                   'colleague_downstream_runtime_independently_rerun_here':False,
                   'known_lead_observed_on_actual_module_with_own_fixture':True,
                   'current009_policy_guard_contract_harness_independently_reviewed':False})
    decision=json.loads((HERE/'review_decision.json').read_text())
    state.update({
        'last_updated_date':DATE,'timezone':'Atlantic/Reykjavik','current_cycle':9,'current_directory':'cycle_009',
        'current_status':'COMPLETED_LOCAL_ANCHORED_ADMISSION_PROPOSAL_UNREVIEWED','ledger_rows':114,
        'current_question':'Advance known self-supplied-manifest lead beyond new copied-function report: actual full-module witness plus independently caller-anchored new-file admission companion, not duplicate downstream analysis.',
        'current_answer':'Actual imported validator accepts7unanchored variants relative to proposed external-root policy; baseline4/9method failures/0errors. New guard9pass normal/-O,7root rejects before delegate,3synthetic positives/8existing hash-schema rejects preserved.8mutants/4configuration rejections separately. Nine-file extraction/14fresh dependencies full rerun matches6workers/12details. Metadata-only official-root positive, no genuine five-file S01/CLI/bundle/install/independent guard approval.',
        'latest_completed_report':REPORT,'optional_supporting_bundle':'researcher040282-cycle009-anchored-cohort-admission.zip',
        'artifact_validation_record':'cycle_009/packet_validation.json',
        'handoff_status':'REPORT_AND_SCIENTIFIC_REPRODUCTION_COMPLETE;PACKET_CLOSURE_PENDING',
        'source_refresh':{'branch_for_current_code':'main','commit':science['tested_main'],'selected_files_verified':20,
                          'public_python_source_closure_verified':12,'authority_metadata_dependencies_verified':2,
                          'metadata':'cycle_009/source_state/main_selected.json',
                          'source_execution_scope':'Full unchanged candidate/package import; actual discover_inputs/validate_run only. Runner definitions imported through package, no runner/engine/CLI/analysis/writer entry point; all12 sources verified, not all functions tested.',
                          'inbox_navigation_commit':'908639412c5560cc2c308b089ade0679c846b15c','inbox_selected_files':10,
                          'inbox_metadata':'cycle_009/source_state/inbox_selected.json','targeted_intake_R001_notes_unchanged':True,
                          'general_TRIAGE_changed':False,'new_colleague_full_schema_report_and_two_reproducers_found':True,
                          'inbox_reproducer_code_executed':False,'incoming_static_scan':'cycle_009/incoming_static_privacy.json',
                          'nonduplication_check':'cycle_009/nonduplication_check.json',
                          'scope':'Selected read-only public source/intake/branch navigation, not exhaustive repository/private coordination or approval of contributed report.'},
        'tool_environment':{'python':result['python'],'packages':{'numpy':result['numpy'],'pandas':result['pandas']},
                            'package_or_compiler_installation_this_cycle':False,'fresh_lean_run_this_cycle':False,
                            'lean_cache_restored_this_cycle':False,
                            'historical_lean_toolchain_record':'cycle_005/completed_004_snapshot/STATE_before_feedback.json'},
        'adversarial_evidence':{'common_contract_methods':9,'admission_fixtures_each_suite':18,
                               'original_expected_failures_each_mode':4,'original_errors_each_mode':0,
                               'guard_passes_each_mode':9,'mutants_detected_normal':8,'mutants_detected_optimized':8,
                               'invalid_configuration_rejections_each_guard_mode':4,'configuration_errors_credited_as_semantic_detections':0,
                               'setup_errors_credited_as_detections':0,'normal_and_optimized_nontiming_results_match':True,
                               'results':'cycle_009/checks/cycle_results.json','worker_results':'cycle_009/checks/worker_results.json',
                               'original_runner_elapsed_seconds':result['elapsed_seconds']},
        'source_comparison':{'evidence_label':'EXECUTABLE_REGRESSION_CHECK','scope':'Actual full-module discovery/validation, complete synthetic minimum-consumed-schema input; no copied source, downstream analysis or real S01.',
                             'policy':'EXPLICIT_PROPOSED_EXTERNAL_ANCHOR_NOT_AN_EXISTING_ORIGINAL_ARGUMENT',
                             'admission_cases_each_suite':18,'original_false_accepts_relative_to_proposed_policy':7,
                             'original_false_rejects':0,'guard_verdict_mismatches':0,'test_owned_synthetic_positive_cases':3,
                             'early_root_rejections':7,'source_hash_schema_rejections_preserved':8,
                             'baseline_actual_validate_run_calls_each_mode':18,'guard_actual_validate_run_calls_each_mode':11,
                             'synthetic_npz_keys_inspected':2600,'numeric_tolerance':'NONE_ADDED;byte_admission_not_metric_comparison',
                             'randomness':'NONE;deterministic arithmetic fixture and ZIP metadata',
                             'public_source_closure_files_verified_unchanged':12,'authority_metadata_files_verified_unchanged':2,
                             'source_functions_copied_replaced_or_edited':False},
        'authority_boundary':{'guard_identity':'NEW_UNREGISTERED_LOCAL_COMPANION_NOT_PIPELINE_INSTALLATION',
                              'independent_repository_manifest_artifact':'ART-2217','committed_manifest_matches_inventory':True,
                              'repository_anchor_positive_scope':'METADATA_ONLY_NOT_GENUINE_COHORT',
                              'full_genuine_S01_positive_executed':False,'test_positive_anchors':'EXPLICIT_TEST_OWNED_SYNTHETIC_NOT_AUTHORITY_ISSUANCE',
                              'trust_source':'CALLER_ASSUMPTION_REQUIRES_OWNER_SEAT_ACCEPTANCE_NOT_SELF_SUPPLIED',
                              'frozen_source_edited':False,'lock_or_registry_changed':False,'new_helper_installed':False,
                              'source_cache_edited':False,'authority_validation_run':False,'full_equivalence_pipeline_run':False,
                              'run_analysis_main_or_writer_called':False,'integration_decision':'OWNER_SEAT_PENDING;NEW_FILE_GUARD_AND_TRUST_POLICY_REVIEW_ONLY'},
        'standalone_reproduction':dict(receipt,record='cycle_009/standalone_reproduction.json',report=REPORT),
        'review_scope':review,'independent_review_received':True,'current_cycle_independent_review_received':False,
        'latest_packet_owner_upload_confirmed':False,
        'publication_status':'Prior94-declaration compilation/intake/mechanism reports preserved. New copied-function lead credited; this agent observed actual-module acceptance with own fixture.009 guard/policy locally tested/reproduced only; no independent guard approval, integration or upload.',
        'privacy':{'report':'cycle_009/privacy_results.json','incoming_expanded_text_scan':'cycle_009/incoming_static_privacy.json',
                   'new_metadata_minimal_at_acquisition':True,'branch_metadata_records_expected':16,
                   'no_personal_commit_contacts_or_signed_payloads_in_branch_metadata':True,
                   'historical_two_synthetic_public_fixture_addresses_distinguished':True,
                   'not_exhaustive_secret_detection_or_security_certification':True},
        'evidence_navigation':{'index':'EVIDENCE_INDEX.json','historical_log_map':'HISTORICAL_ARCHIVE_LOG_MAP.csv',
                               'all_ledger_references_unpacked':True,'old_archives_not_nested_or_changed':True,
                               'historical_missing_only_restoration':'cycle_009/historical_restoration.json'},
        'previous_cycle':8,'previous_cycle_evidence':{'completed008_state':'cycle_009/previous008_snapshot/STATE.json',
                                                      'completed008_ledger113':'cycle_009/previous008_snapshot/CLAIM_LEDGER.csv',
                                                      'science_not_rerun_this_cycle':True,
                                                      'completed007_state':'cycle_008/previous007_snapshot/STATE.json',
                                                      'completed007_ledger112':'cycle_008/previous007_snapshot/CLAIM_LEDGER.csv',
                                                      'completed006_ledger111':'cycle_007/previous006_snapshot/CLAIM_LEDGER.csv',
                                                      'completed005_ledger109':'cycle_006/previous005_snapshot/CLAIM_LEDGER.csv',
                                                      'completed004_ledger108':'cycle_005/completed_004_snapshot/CLAIM_LEDGER_COMPLETED_004.csv'},
        'completed_this_cycle':['fresh main/feedback/public coordination; new colleague runtime report credited before preregistration',
                                'fixed caller-root admission protocol, immutable18scenarios, complete deterministic2600key toy generator',
                                'new stdlib-only external-anchor guard with actual unchanged full-module discovery/validation',
                                'original4intended method failures/0errors;guard9pass normal/-O;7unanchored variants blocked before delegate',
                                '3synthetic positives/8old hash-schema rejects preserved;8mutants/4configuration errors separately',
                                'metadata-only committed ART-2217 root check;no genuine S01 positive/CLI/analysis output',
                                '9inline files extracted/14fresh dependencies;full runner repeated;6workers/12details match',
                                'prior113 ledger rows/94formal labels preserved;one scoped009 proposal record',
                                'actual packet closure receipt required before delivery'],
        'not_proved_or_promoted':list(dict.fromkeys(state['not_proved_or_promoted']+decision['not_approved'])),
        'in_progress':None,'research_processes_running':[],'next_cycle':10,'next_directory':'cycle_010',
        'next_selected_work':'Return to a dynamics-library prerequisite: fresh-check actual history/delay/phase-step semantics, independent indexed-buffer model and wrong-index/update-order controls; then choose one smallest useful formal lemma. No duplicate rate-law sweep/docs or broad inventory.',
        'immediate_next_action':'On next Continue, fresh-check current engine/Lean reference status and feedback, choose one load-bearing history/phase contract before preregistering010. Frozen engine remains unchanged; check existing toolchain/cache before any install. No real study/campaign or unattended work.',
        'remote_changes_by_this_agent':False,'contacted_other_bots':False,'automatic_work_between_turns':False,
    })
    (ROOT/'STATE.json').write_text(json.dumps(state,indent=2)+'\n')
    print('Finalized009:114unique rows;prior113/94formal labels preserved;new local admission companion only')


if __name__=='__main__':main()
