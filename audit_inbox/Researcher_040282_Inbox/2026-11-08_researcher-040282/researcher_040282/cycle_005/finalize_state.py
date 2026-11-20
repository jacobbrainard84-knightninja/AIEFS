"""Finalize only observed cycle005 results; no scientific code execution here."""
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def load(path):
    return json.loads(path.read_text())


def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    original = load(HERE / 'checks/cycle_results.json')
    repeated = load(HERE / 'standalone/checks/cycle_results.json')
    extraction = load(HERE / 'standalone/extraction_result.json')
    fetch = json.loads((HERE / 'standalone/public_fetch.log').read_text())
    for result in (original, repeated):
        if not result['all_preregistered_acceptance_conditions_met']:
            raise RuntimeError('Cannot finalize unobserved success')
        if [item['tests_run'] for item in result['regression_runs']] != [3, 22, 22]:
            raise RuntimeError('Wrong control counts')
    for key in ('legacy_witness', 'candidate_default_positive', 'positive_perturbation_cases',
                'max_abs_left_residual', 'max_abs_right_residual', 'max_oracle_errors'):
        if original[key] != repeated[key]:
            raise RuntimeError('Extracted rerun differs: ' + key)
    if extraction['count'] != 6 or not extraction['all_match_supplied_sources'] or fetch['verified_modules'] != 10:
        raise RuntimeError('Incomplete extraction/public dependency acquisition')
    for name in extraction['critical_files']:
        if (HERE / 'standalone/extracted' / name).read_bytes() != (HERE / 'proposal' / name).read_bytes():
            raise RuntimeError('Extracted source changed after execution')
    reproduction = {
        'actually_executed': True, 'runner_exit': 0,
        'report': '2026-11-08_researcher040282_005_review-response.md',
        'critical_files': extraction['critical_files'], 'critical_file_count': 6,
        'all_extracted_files_match_supplied_sources': True,
        'fresh_public_modules_fetched_and_verified': 10,
        'tested_main': repeated['tested_source_commit'],
        'legacy_expected_failures': 3, 'legacy_errors': 0,
        'candidate_methods_passed': 22, 'candidate_methods_passed_optimized': 22,
        'positive_perturbation_cases': 64, 'default_plus_perturbations': 65,
        'results_match_original_numerically': True,
        'elapsed_runner_seconds': repeated['elapsed_seconds'],
        'result_file': 'cycle_005/standalone/checks/cycle_results.json',
        'log': 'cycle_005/standalone/reproduction.log',
        'fetch_log': 'cycle_005/standalone/public_fetch.log',
        'scope': 'Submitter-local one-note self-reproduction with public dependencies; not independent controls/review, production replay, or proof',
    }
    dump(HERE / 'standalone_reproduction.json', reproduction)
    ledger = list(csv.DictReader((ROOT / 'CLAIM_LEDGER.csv').open()))
    if len(ledger) != 109 or len({row['claim_id'] for row in ledger}) != 109:
        raise RuntimeError('Current ledger must have109 unique rows')
    for row in ledger:
        if row['cycle'] == '5':
            extra = ';cycle_005/standalone_reproduction.json;cycle_005/standalone/checks/cycle_results.json;cycle_005/standalone/reproduction.log'
            if 'cycle_005/standalone_reproduction.json' not in row['evidence_files']:
                row['evidence_files'] += extra
    with (ROOT / 'CLAIM_LEDGER.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(ledger[0]))
        writer.writeheader(); writer.writerows(ledger)
    previous = load(HERE / 'completed_004_snapshot/STATE_before_feedback.json')
    feedback = load(HERE / 'feedback_scope.json')
    state = {
        'agent': 'Researcher 040282',
        'owner_instruction': 'Self-direct bounded, red-teamed AIEFS research; create dated audit-inbox handoffs for owner upload. Continue does not authorize remote submission or unattended work.',
        'workflow': 'WORKFLOW.md', 'queue': 'RESEARCH_QUEUE.md', 'claim_ledger': 'CLAIM_LEDGER.csv',
        'last_updated_date': '2026-09-04', 'timezone': 'Atlantic/Reykjavik',
        'date_provenance': {'session_supplied_preparation_date': '2026-09-04',
                            'owner_correspondence_handoff_label': '2026-11-08',
                            'historical004_execution_date_reconstructed': False,
                            'note': 'September4 chronological production stamp withdrawn for004; use owner label for handoff indexing only. No inference from compiler build dates/durations; sources/seeds unchanged.'},
        'current_cycle': 5, 'current_status': 'COMPLETED_LOCAL_CANDIDATE_UNREVIEWED',
        'current_directory': 'cycle_005', 'ledger_rows': 109,
        'current_question': 'Resolve received004 packaging/privacy/review-scope feedback, then repair known wrong-branch synthetic bridge assurance through one new-file/erratum proposal.',
        'current_answer': 'Three legacy wiring contracts fail with0 errors; proposed companion21 methods pass normally/-O,65 finite operator/oracle checks at fixed tolerance. Six inline files extracted and full runner repeated using10 freshly fetched public modules. Pinned ART-0050, model and old scientific content unchanged. No new Lean/production replay/engine-oracle patch/v4.1 conclusion.',
        'latest_completed_report': '2026-11-08_researcher040282_005_review-response.md',
        'short004_addendum': '2026-11-08_researcher040282_004_addendum.md',
        'optional_supporting_bundle': 'researcher040282-cycle005-review-response.zip',
        'artifact_validation_record': 'cycle_005/packet_validation.json',
        'source_refresh': {'branch_for_current_code': 'main', 'commit': original['tested_source_commit'],
                           'selected_files_verified': 26, 'verified_import_modules_exercised': 10,
                           'metadata': 'cycle_005/source_state/main_selected.json',
                           'inbox_navigation_commit': 'b466ab6cdd564ce3f7848e7701b378c5f0cc475f',
                           'inbox_selected_files': 35, 'inbox_metadata': 'cycle_005/source_state/inbox_selected.json',
                           'review_received': True, 'scope': 'Selected public read-only acquisition; initial12 main selections plus6 bridge and8 import-dependency files. Not an exhaustive assignment/provenance audit.'},
        'tool_environment': {'python': original['python'], 'packages': original['packages'],
                             'lean_cache_available_at_start': False, 'lean_cache_restored_this_cycle': False,
                             'fresh_lean_run_this_cycle': False,
                             'historical_lean_toolchain_record': 'cycle_005/completed_004_snapshot/STATE_before_feedback.json',
                             'note': 'No package/compiler installation in005. Check disposable cache before future restoration; historical logs are not new builds.'},
        'adversarial_evidence': {'runs': original['regression_runs'],
                                 'all_preregistered_acceptance_conditions_met': True,
                                 'limits': original['limits'], 'results': 'cycle_005/checks/cycle_results.json',
                                 'own_candidate_input_mutation_falsifier': {'pre_fix_single_control_failed': True, 'pre_fix_errors': 0, 'fixed_by_pre_call_snapshot_and_oracle': True, 'record': 'cycle_005/input_mutation_red.json', 'not_an_upstream_mutation_claim': True}},
        'source_comparison': {'evidence_label': 'EXECUTABLE_REGRESSION_CHECK',
                              'scope': 'Pure edge-coordinate audit helper, not production-engine advance_state; finite isolated12-node synthetic inputs only',
                              'valid_cases': 65, 'perturbation_cases': 64, 'seed': 2026090405,
                              'absolute_tolerance': 1e-14, 'relative_tolerance': 0.0,
                              'max_abs_left_residual': original['max_abs_left_residual'],
                              'max_abs_right_residual': original['max_abs_right_residual'],
                              'max_oracle_errors': original['max_oracle_errors']},
        'standalone_reproduction': reproduction,
        'review_scope': feedback,
        'independent_review_received': True, 'current_cycle_independent_review_received': False,
        'owner_upload_confirmed': True, 'latest_packet_owner_upload_confirmed': False,
        'publication_status': 'Prior audit-inbox receipt confirmed;94-declaration compilation/footprint review only. New005 packet prepared locally, not uploaded. No library-grade approval or main integration.',
        'privacy': {'report': 'cycle_005/privacy_results.json', 'three_reported_acquisition_jsons_minimized': True, 'three_additional_legacy_inbox_records_minimized': True,
                    'removed_contact_values_printed_or_backed_up': False,
                    'signed_commit_payloads_omitted': True,
                    'new_packet_scan': 'cycle_005/packet_validation.json', 'remote_metadata_changed': False},
        'evidence_navigation': {'index': 'EVIDENCE_INDEX.json', 'historical_log_map': 'HISTORICAL_ARCHIVE_LOG_MAP.csv',
                                'ledger_paths_unpacked': True, 'unlabelled_archive_only_logs': False},
        'previous_cycle': 4,
        'previous_cycle_evidence': {'status': 'COMPLETED', 'ledger_rows': 108,
                                    'snapshot': 'cycle_005/completed_004_snapshot/COMPLETED_004_STATE.json',
                                    'ledger': 'cycle_005/completed_004_snapshot/CLAIM_LEDGER_COMPLETED_004.csv',
                                    'original_full_state_before_feedback': 'cycle_005/completed_004_snapshot/STATE_before_feedback.json',
                                    'report': previous['latest_completed_report'],
                                    'formal_evidence': previous['formal_evidence'],
                                    'adversarial_evidence': previous['adversarial_evidence'],
                                    'source_comparison': previous['source_comparison'],
                                    'standalone_reproduction': previous['standalone_reproduction'],
                                    'note': 'All of these are historical004 outcomes; no new Lean compilation in005. Review metadata now acknowledges received narrow external compilation report.'},
        'completed_this_cycle': ['Acquired relevant current-main and actual inbox review notes read-only',
                                  'Sanitized three reported main records plus three additional legacy inbox records, including signed payload removal, without printing or backing up contacts',
                                  'Corrected004 date/state/108-row and external-review scope via a short addendum',
                                  'Prepared new-file K3 self-test/erratum candidate, preserving pinned artifact and model',
                                  'Observed shared legacy-red3/candidate-green21 contracts and full optimized21-method run',
                                  'Compared65 finite actual-helper outputs/metadata and identities to independent Fraction map',
                                  'Extracted6 inline critical files, freshly fetched10 public modules and repeated all outcomes',
                                  'Synchronized current109-row and completed004108-row ledger/state views',
                                  'Unpacked/indexed cited proof/source logs for owner handoff'],
        'not_proved_or_promoted': ['Universal float64 or machine-checked Python execution equivalence',
                                   'Fresh saved bridge replay, full S01 reanalysis,4800-case check or finiteness census',
                                   'Independent controls or approval of the new005 repair',
                                   'Library-grade statement fidelity/main integration of94 prior Lean declarations',
                                   'Complete delay-buffer/phase-step semantics, sharp derived future drive bands',
                                   'Gated-OFF/finite aggregation, explicit freeze times, selected-controller rate law',
                                   'Coupled locking or unconditional convergence'],
        'in_progress': None, 'research_processes_running': [],
        'next_cycle': 6, 'next_directory': 'cycle_006',
        'next_selected_work': 'Review existing v4.1 held-event semantics/estimands and boundary interval wording after fresh main/feedback refresh. Do not rediscover frozen v4 or rework merged uploader/checksum fixes.',
        'immediate_next_action': 'On Continue: read latest state/report/feedback, refresh relevant current main/inbox read-only, check already-landed work, preregister v4.1 event/estimand oracle and boundary controls. If resolved, pick a separate still-open engine/oracle repair. Do not start unattended work.',
        'remote_changes_by_this_agent': False, 'contacted_other_bots': False,
        'automatic_work_between_turns': False,
    }
    dump(ROOT / 'STATE.json', state)
    print('Finalized observed005 completion and actual standalone reproduction; root109, completed004108, next006.')


if __name__ == '__main__':
    main()
