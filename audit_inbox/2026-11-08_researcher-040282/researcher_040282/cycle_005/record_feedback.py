"""Record narrowly scoped received feedback; do not promote evidence labels.
Idempotent ledger update. Does not contact seats or alter remote files.
"""
from pathlib import Path
import ast
import csv
import json
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REVIEW = 'audit_inbox/2026-11-08_auditor-seat-002_workspace-notes/TRIAGE_r040282.md'
INTAKE = 'audit_inbox/2026-11-08_auditor-seat-002_researcher-040282-intake.md'
BASE = 'f3e3a57632c613e860a9941f007732cb4c2c91c6'
INBOX = 'b466ab6cdd564ce3f7848e7701b378c5f0cc475f'


def dump(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def main():
    results = json.loads((HERE / 'checks/cycle_results.json').read_text())
    if not results['all_preregistered_acceptance_conditions_met']:
        raise RuntimeError('Cannot record incomplete checks as completed')
    feedback = {
        'current_main_tested': BASE, 'review_acquired_from_inbox': INBOX,
        'intake_note': INTAKE, 'researcher001_triage': REVIEW,
        'evidence_kind': 'Publicly acquired colleague reports of their own execution; not our reexecution of their witnesses',
        'reviewer_main_basis': '942f8526daee5ac547f2e422101fa95c61eeef41',
        'independent_compilation_reported': {'002': 22, '003': 44, '004_EMA': 22, '004_drive': 6},
        'compiled_total': 94, 'reported_warnings': 0, 'reported_errors': 0,
        'reported_footprint': ['propext', 'Classical.choice', 'Quot.sound'],
        'scope_exclusions': ['library-grade statement-fidelity approval', 'integration decision',
                             'our check_cycle.py controls', 'our ZIP checkers', 'full S01 reanalysis',
                             'our4800 saved held-event comparisons', 'real-array finiteness census',
                             'new005 repair-candidate review'],
        'additional_review_confirmation': 'Coarse baseline ON bound fails to reach threshold; not evidence of OFF',
        'uploader_disposition': 'Owner reports PR10 uploader and PR11 checksum checker merged; supplied main head matches acquired head. No new uploader work; no behavioral certification of those merges here.',
        'current_python_CI': '.github/workflows/repo-checks.yml exists on the tested source; withdraw the stale no-Python-CI generalization as a current-main claim',
        'owner_receipt': 'Actual audit-inbox intake and triage found; uploaded root ledger independently counted78 rows, versus108 at completed004',
        'contact_or_remote_write_by_this_agent': False,
        'reviewer_private_log_paths': 'Mentioned by reviewer; not fetched or represented as included local evidence',
    }
    dump(HERE / 'feedback_scope.json', feedback)
    source = HERE / 'source_state/main/AIEF_1_4_proposal_equalization_bridge_analysis.py'
    syntax = ast.parse(source.read_text())
    calls = [node.lineno for node in ast.walk(syntax)
             if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
             and node.func.id == 'synthetic_self_test']
    saved = json.loads((HERE / 'source_state/main/aief_1_4_proposal_equalization_bridge/analysis_manifest.json').read_text())
    historical = Path('/home/user/aiefs_repository_audit/replay_one_condition.py')
    destination = HERE / 'historical_provenance'
    destination.mkdir(exist_ok=True)
    shutil.copyfile(historical, destination / historical.name)
    historical_syntax = ast.parse(historical.read_text())
    imports = []
    for node in ast.walk(historical_syntax):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    if '--self-test' in saved['command'] or calls != [361]:
        raise RuntimeError('Saved-command/dispatch inspection changed; review manually')
    provenance = {
        'tested_main': BASE, 'inspection_only_no_production_replay_rerun': True,
        'saved_manifest': 'source_state/main/aief_1_4_proposal_equalization_bridge/analysis_manifest.json',
        'recorded_command': saved['command'], 'recorded_command_contains_self_test': False,
        'only_direct_synthetic_self_test_call_lines_in_bridge': calls,
        'dispatch': 'lines358–362: if args.self_test, run synthetic_self_test and return; normal replay begins after that branch',
        'saved_manifest_branch_checks': saved['branch_checks'],
        'prior_own_S01_replay_script_copy': 'historical_provenance/replay_one_condition.py',
        'prior_own_S01_replay_imports': sorted(set(imports)),
        'prior_own_S01_script_imports_bridge': any('proposal_equalization' in item for item in imports),
        'prior_own_audit_probes': 'test_deep_audit.py/additional_probes.py invoked old synthetic_self_test to expose its false PASS, not to endorse the fixture',
        'bounded_conclusion': 'Inspected saved normal-replay command/path does not invoke the synthetic self-test. This defect alone does not invalidate the conditional algebra or recorded real-data replay. Not a fresh replay, exhaustive dependency/provenance audit, or certification of every historical wrapper.',
        'near_tie_limit': 'Saved minimum margin4.440892098500626e-14 is much smaller than new positive synthetic margins; no robustness claim for saved near-tie cases.',
    }
    dump(HERE / 'saved_evidence_provenance.json', provenance)
    ledger = ROOT / 'CLAIM_LEDGER.csv'
    with ledger.open(newline='') as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)
    original = [row for row in rows if row['cycle'] != '5']
    if len(original) != 108 or len({row['claim_id'] for row in original}) != 108:
        raise RuntimeError('Expected completed004108-row claim set')
    for row in original:
        if row['evidence_label'] == 'LEAN_COMPILED':
            row['independent_review'] = 'R001_TRIAGE:REPORTED_INDEPENDENT_COMPILATION_AND_STANDARD_FOOTPRINT_ONLY;STATEMENT_FIDELITY_PENDING;SUBMITTER_CONTROLS_NOT_RUN'
        else:
            row['independent_review'] = 'EXTERNAL_TRIAGE_RECEIVED;THIS_SUBMITTER_FINITE_CHECK_NOT_INDEPENDENTLY_RERUN;NO_BLANKET_APPROVAL'
        row['publication'] = 'AUDIT_INBOX_RECEIPT_CONFIRMED;NO_LIBRARY_APPROVAL_CLAIM'
    def write_ledger(path, content):
        with path.open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(content)
    write_ledger(HERE / 'completed_004_snapshot/CLAIM_LEDGER_COMPLETED_004.csv', original)
    new = dict.fromkeys(fields, '')
    new.update({
        'claim_id': 'R040282-005-BRIDGE-SELFTEST', 'cycle': '5',
        'symbol': 'proposed branch-faithful K3 self-test companion',
        'statement_or_exact_header': 'On main f3e3a57632c613e860a9941f007732cb4c2c91c6, the same3 wiring/fail-closed contracts fail on legacy self-test and pass on companion; all21 candidate unittest methods pass normally and under -O. Actual-operator/Fraction checks pass for default plus64 seeded positive cases at absolute1e-14,relative0; wrong branch/tie/inactive and output/metadata/constant/input-mutation/guard/epsilon mutations are rejected.',
        'evidence_label': 'EXECUTABLE_REGRESSION_CHECK',
        'domain_and_scope': 'Finite synthetic isolated12-node/66-edge tests of the current-main pure edge-coordinate audit operator, not production-engine advance_state, a saved replay, universal float64 equivalence, a Lean theorem, or library approval. Candidate is a new-file/erratum proposal; pinned ART-0050 unchanged.',
        'evidence_files': 'cycle_005/PLAN.md;cycle_005/proposal/AIEF_1_4_proposal_equalization_branch_selftest_r040282.py;cycle_005/proposal/test_proposal_equalization_branch_selftest_r040282.py;cycle_005/proposal/run_checks.py;cycle_005/proposal/source_modules.json;cycle_005/checks/cycle_results.json;cycle_005/checks/red_legacy.log;cycle_005/checks/green_candidate.log;cycle_005/checks/green_candidate_optimized.log',
        'related_work_or_followup': 'Known B-F4 mechanism confirmed by R001, not a novelty claim. Erratum/candidate require independent review. Engine complex-NaN and oracle uniqueness repairs remain separate. Review v4.1 before rediscovering frozen-v4 failures.',
        'independent_review': 'OWN_CONTROLS_ONLY;CANDIDATE_UNREVIEWED;R001_REVIEW_PREDATES_THIS_REPAIR',
        'publication': 'LOCAL_PREPARED_FOR_OWNER_UPLOAD;NO_AUTOMATIC_SUBMISSION',
        'integration': 'NO_REMOTE_CHANGE;PINNED_ARTIFACT_UNCHANGED',
    })
    write_ledger(ledger, original + [new])
    snapshot = {
        'cycle': 4, 'status': 'COMPLETED', 'ledger_rows': 108,
        'ledger': 'CLAIM_LEDGER_COMPLETED_004.csv',
        'report': '2026-09-04_researcher040282_004_complex-ema.md',
        'original_control_runner_exit': 0, 'extracted_control_runner_exit': 0,
        'controls_each_run': 18, 'valid_compute_R_cases_each_run': 34,
        'compute_R_calls_each_run': 253, 'configuration_rejection_count_separate': 1,
        'state_drift_correction': 'Uploaded older root stopped003/78; intended004 closure is004/108. New005 workflow root separately has109 rows.',
        'date_provenance': 'Old September4 chronological production stamp withdrawn. Owner review/handoff label2026-11-08, not asserted execution date. No run timestamp reconstructed; sources/seeds preserved.',
        'independent_review': 'Compilation/standard-footprint report received for94 declarations across002–004; not controls or statement-fidelity approval',
    }
    dump(HERE / 'completed_004_snapshot/COMPLETED_004_STATE.json', snapshot)
    print('Recorded narrowly scoped feedback; completed004 snapshot108 rows; current ledger109 rows; evidence labels unchanged for original108.')


if __name__ == '__main__':
    main()
