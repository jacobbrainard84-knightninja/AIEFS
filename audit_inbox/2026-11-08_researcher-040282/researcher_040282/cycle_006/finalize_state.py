"""Finalize observed006 evidence/state, preserving all prior109 ledger rows.
Does not execute scientific code, contact anyone, or alter frozen snapshots.
"""
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATE = '2026-09-04'
MAIN = 'eb3933c196ee19e80e1621ae80d89ca72e6d9485'
REPORT = DATE + '_researcher040282_006_v41-contract-review.md'


def read_ledger(path):
    with path.open(newline='') as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def main():
    normal = json.loads((HERE / 'checks/cycle_results.json').read_text())
    optimized = json.loads((HERE / 'optimized_checks/cycle_results.json').read_text())
    standalone = json.loads((HERE / 'standalone_reproduction.json').read_text())
    decision = json.loads((HERE / 'review_decision.json').read_text())
    if not (normal['all_preregistered_robust_checks_passed'] and
            optimized['all_preregistered_robust_checks_passed'] and
            standalone['actually_executed'] and standalone['returncodes'] == [0, 0] and
            standalone['all_six_scientific_result_groups_match_all_four_runs']):
        raise RuntimeError('Do not finalize an incomplete audit')
    fields, prior = read_ledger(HERE / 'previous005_snapshot/CLAIM_LEDGER.csv')
    _, current = read_ledger(ROOT / 'CLAIM_LEDGER.csv')
    if len(prior) != 109 or [row for row in current if row['cycle'] != '6'] != prior:
        raise RuntimeError('Prior109 rows changed')
    common = {'cycle': '6', 'independent_review': 'SUBMITTER_LOCAL_ORACLE_AND_CONTROLS_ONLY;NO_INDEPENDENT_SEAT_REVIEW_OF_006',
              'publication': 'LOCAL_PREPARED_FOR_OWNER_DATED_AUDIT_INBOX_UPLOAD;NOT_UPLOADED',
              'integration': 'NO_SOURCE_PATCH;NO_REMOTE_CHANGE;NO_PROJECT_FREEZE_OR_REGISTRY_PROMOTION'}
    executable_files = ['PLAN.md', 'PLAN_PREREGISTERED_BEFORE_ADMIN_NOTICE.md',
                        'programs/audit_v41.py', 'programs/reference_contract.py', 'programs/load_upstream.py',
                        'programs/source_modules.json', 'checks/cycle_results.json',
                        'optimized_checks/cycle_results.json', 'checks/mutation_results.json',
                        'checks/policy_boundary_cases.csv', 'checks/synthetic_events.csv',
                        'checks/synthetic_auc.csv', 'checks/synthetic_event_interactions.csv',
                        'audit_run.log', 'optimized_audit_run.log', 'standalone_reproduction.json',
                        'standalone/checks/cycle_results.json', 'standalone/optimized_checks/cycle_results.json',
                        'standalone/reproduction.log']
    note_files = ['programs/ESTIMAND_CONTRACT.json', 'review_decision.json',
                  'checks/semantic_witnesses.json', 'checks/synthetic_cohort_summary.csv',
                  'checks/bootstrap_pointwise_summary.csv', 'checks/bootstrap_diagnostics.json',
                  'programs/reference_contract.py', 'checks/cycle_results.json',
                  'prior_context/pasted_source_AUDIT-REPORT.md']
    rows = [dict(common, claim_id='R040282-006-CONTRACT-CHECK', symbol='candidate_saved_grid_held_contract',
                 statement_or_exact_header='On main ' + MAIN + ', independent forward-run/Fraction reference agrees with candidate helpers on3072 exhaustive small cases,2350 translated640-grid cases,60 nominal paired cases and12 other robust cases.605 preregistered gray boundary cases are excluded. All8 semantic mutants detected. Selected fields of19200 synthetic event,1600 AUC and11520 DID rows agree at fixed allowances. Ordinary/-O results match; all six science groups reproduce from seven inline files with12 fresh public modules.',
                 evidence_label='EXECUTABLE_REGRESSION_CHECK',
                 domain_and_scope='Finite saved-grid helper and fully synthetic Run-scaffold conformance, not all floating schedules, target-channel swaps, every metadata column, validate_run/run_analysis, real trajectories, engine feasibility, universal correctness, population inference, Lean theorem or freeze approval.',
                 evidence_files=';'.join('cycle_006/' + name for name in executable_files),
                 related_work_or_followup='E17 wording and frozen-v4 duration failure already known; no novelty re-report. Candidate source unchanged. Owner/seat to review oracle/controls and additional acceptance surfaces.'),
            dict(common, claim_id='R040282-006-ESTIMAND-NOTE', symbol='held_flags_onset_riskset_and_interval_contract',
                 statement_or_exact_header='For sorted finite grids and the stated qualifying maximal-run rule, any-held iff initial retention OR post-first-False recovery; these flags can overlap, with retention precedence only for exclusive classification. Held event_time is retrospective qualifying onset, not confirmation or after-False latency. Full-cohort capped recovery is not an overall retention ranking or physical-onset censoring at its cap. Empirical all0/all1 percentile bounds do not provide general boundary-population coverage; iid Bernoulli p=.01,n40 gives allzero probability .99^40.',
                 evidence_label='PAPER_ARGUMENT',
                 domain_and_scope='Explicit operational set identity, simple probability counterexample and actual finite source/synthetic witnesses. No new Lean compilation, physical crossing reconstruction, causal risk-set repair, chosen replacement CI, real S01 impact or new registered metric. Contract is a review aid.',
                 evidence_files=';'.join('cycle_006/' + name for name in note_files),
                 related_work_or_followup='Prior A-F2/A-F3 already state bootstrap/onset-support limitations. Current candidate interpretation made precise, not new novelty. Decide estimand and interval scope before population claims/freeze.')]
    ledger = prior + rows
    if len({row['claim_id'] for row in ledger}) !=111:
        raise RuntimeError('Ledger IDs not unique')
    if sum(row['evidence_label'] == 'LEAN_COMPILED' for row in ledger) !=94:
        raise RuntimeError('Unexpected formal-label promotion')
    for row in rows:
        if set(row) != set(fields):
            raise RuntimeError('Ledger field mismatch')
        for name in row['evidence_files'].split(';'):
            if not (ROOT / name).is_file():
                raise FileNotFoundError(name)
    with (ROOT / 'CLAIM_LEDGER.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(ledger)
    state = json.loads((HERE / 'previous005_snapshot/STATE.json').read_text())
    review_scope = state['review_scope']
    review_scope['prior005_main_tested'] = review_scope.pop('current_main_tested')
    review_scope.update({'this_is_prior_002_003_004_compilation_review_only': True,
                         'current006_harness_or_inference_independently_reviewed': False,
                         'current006_review_basis': MAIN})
    old_limits = state['not_proved_or_promoted']
    state.update({
        'last_updated_date': DATE, 'timezone': 'Atlantic/Reykjavik',
        'date_provenance': {'session_supplied_preparation_date': DATE,
                            'prior_owner_correspondence_handoff_label': '2026-11-08',
                            'historical004_execution_date_reconstructed': False,
                            'administrative_notice_written_after_original006_executions': True,
                            'scientific_protocol_or_seed_changed_by_notice': False,
                            'note': 'Preparation label and historical owner/seat handoff labels are separate; no chronology inferred from compiler builds, runtime clocks or durations. Original delivered reports/snapshots unchanged.',
                            'notice': 'cycle_006/ADMINISTRATIVE_PROVENANCE.md'},
        'current_cycle': 6, 'current_directory': 'cycle_006',
        'current_status': 'COMPLETED_LOCAL_QUALIFIED_CONTRACT_REVIEW', 'ledger_rows': 111,
        'current_question': 'Review current v4.1 candidate held-event semantics, estimands and interval limitations without rediscovering frozen-v4 or already-corrected wording.',
        'current_answer': 'All preregistered robust finite checks pass normally/-O and extracted-note reruns;8/8 semantic mutants detected,12 public modules unchanged. Actual synthetic19200event/1600AUC/11520DID selected fields conform.605 gray boundary cases excluded. Flags may overlap, times are retrospective onset, full-cohort capped scores have finite-support/risk-set meaning, and bootstrap bounds are not population-certified. Qualified conformance, not freeze or real-data approval.',
        'latest_completed_report': REPORT,
        'optional_supporting_bundle': 'researcher040282-cycle006-v41-contract-review.zip',
        'artifact_validation_record': 'cycle_006/packet_validation.json',
        'handoff_status': 'REPORT_AND_SCIENTIFIC_REPRODUCTION_COMPLETE;PACKET_CLOSURE_PENDING',
        'source_refresh': {'branch_for_current_code': 'main', 'commit': MAIN,
                           'selected_files_verified': 28, 'verified_import_modules_exercised': 12,
                           'metadata': 'cycle_006/source_state/main_selected.json',
                           'inbox_navigation_commit': 'b466ab6cdd564ce3f7848e7701b378c5f0cc475f',
                           'inbox_selected_files': 37, 'inbox_metadata': 'cycle_006/source_state/inbox_selected.json',
                           'new_targeted005_feedback_found_in_selected_navigation': False,
                           'prior_compilation_review_received': True,
                           'scope': 'Selected public read-only source/intake review and static12-module import closure; not exhaustive repository/provenance acceptance.'},
        'tool_environment': {'python': normal['python'], 'packages': normal['packages'],
                             'package_or_compiler_installation_this_cycle': False,
                             'fresh_lean_run_this_cycle': False, 'lean_cache_restored_this_cycle': False,
                             'historical_lean_toolchain_record': 'cycle_005/completed_004_snapshot/STATE_before_feedback.json'},
        'adversarial_evidence': {'all_preregistered_robust_checks_passed': True,
                                 'semantic_mutants_detected': 8, 'gray_cases_not_counted_as_conformance': 605,
                                 'normal_and_optimized_six_scientific_groups_match': True,
                                 'normal_elapsed_seconds': normal['elapsed_seconds'],
                                 'optimized_elapsed_seconds': optimized['elapsed_seconds'],
                                 'normal_result': 'cycle_006/checks/cycle_results.json',
                                 'optimized_result': 'cycle_006/optimized_checks/cycle_results.json'},
        'source_comparison': {'evidence_label': 'EXECUTABLE_REGRESSION_CHECK',
                              'scope': 'Actual compute helpers on synthetic scaffolds only; shared density/similarity masks/targets and selected-field checks, not full schema/channel independence or actual engine trajectories.',
                              'event_rows': 19200, 'auc_rows': 1600, 'did_rows': 11520,
                              'modules_verified_unchanged': 12, 'numeric_absolute_allowance': 5e-13,
                              'auc_absolute_allowance': 5e-12, 'relative_allowance': 0,
                              'bootstrap_seed': 2026090406, 'bootstrap_draws': 512,
                              'index_label_timestamp_agreement': 'EXACT'},
        'standalone_reproduction': dict(standalone, record='cycle_006/standalone_reproduction.json', report=REPORT),
        'review_scope': review_scope, 'independent_review_received': True,
        'current_cycle_independent_review_received': False,
        'latest_packet_owner_upload_confirmed': False,
        'publication_status': 'Prior receipt/94-declaration compilation footprint report only.006 prepared locally for owner upload; no independent006 review, registry promotion, freeze or main integration.',
        'privacy': {'report': 'cycle_006/privacy_results.json',
                    'new_acquisition_metadata_minimal_at_creation': True,
                    'branch_metadata_records_expected': 10,
                    'two_intentionally_synthetic_public_git_fixture_addresses_expected': True,
                    'no_personal_commit_contacts_or_signed_payloads_in_branch_metadata': True,
                    'not_a_general_secret_or_arbitrary_code_security_certification': True},
        'evidence_navigation': {'index': 'EVIDENCE_INDEX.json',
                                'historical_log_map': 'HISTORICAL_ARCHIVE_LOG_MAP.csv',
                                'all_ledger_references_unpacked': True,
                                'old_archives_not_nested_or_changed': True},
        'previous_cycle': 5,
        'previous_cycle_evidence': {'completed005_state': 'cycle_006/previous005_snapshot/STATE.json',
                                    'completed005_ledger109': 'cycle_006/previous005_snapshot/CLAIM_LEDGER.csv',
                                    'completed004_ledger108': 'cycle_005/completed_004_snapshot/CLAIM_LEDGER_COMPLETED_004.csv',
                                    'final005_candidate_methods_normal_and_optimized': 22,
                                    'not_rerun_this_cycle': True},
        'completed_this_cycle': ['fresh-main/intake read-only review; E17/prior A-F2/F3 acknowledged',
                                 'preregistered independent forward-run/Fraction oracle and bounded tests',
                                 'actual normal/optimized runs and8 intended semantic mutant detections',
                                 'actual19200event/1600AUC/11520DID synthetic selected-field comparisons',
                                 'explicit flags/onset/risk-set/cap/bootstrap contract and counterexamples',
                                 'seven inline files extracted,12 public modules freshly fetched, normal/-O reruns matched',
                                 'prior109 ledger rows preserved; two scoped006 records; no formal promotion',
                                 'new metadata minimized at acquisition; packet closure is separate and requires its actual receipt before delivery'],
        'not_proved_or_promoted': list(dict.fromkeys(old_limits + decision['not_approved'])),
        'in_progress': None, 'research_processes_running': [],
        'next_cycle': 7, 'next_directory': 'cycle_007',
        'next_selected_work': 'Fresh-check one open engine complex-NaN comparison repair; failing-before/passing-after on current main. If already fixed, use the separate oracle uniqueness repair, not a combined branch.',
        'immediate_next_action': 'On next Continue: inspect current source and feedback before committing a small007 repair. No new uploader work or default full S01 rerun.',
        'remote_changes_by_this_agent': False, 'contacted_other_bots': False,
        'automatic_work_between_turns': False,
    })
    (ROOT / 'STATE.json').write_text(json.dumps(state, indent=2) + '\n')
    print('Finalized006:111 unique rows; prior109 and94 formal labels preserved; local qualified review only')


if __name__ == '__main__':
    main()
