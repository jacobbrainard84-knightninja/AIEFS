"""Promote only observed010 scoped results AFTER exact-note full reproduction.
Preserve prior114 rows/94 formal labels; add3 compiled +1 finite contract row.
No upstream registry, authority, installation, independent review or upload.
"""
from pathlib import Path
import csv
import json
import re

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
DATE='2026-09-04'
REPORT=DATE+'_researcher040282_010_history-phase-contract.md'


def require(condition,message):
    if not condition:raise RuntimeError(message)


def ledger(path):
    with path.open(newline='') as stream:
        reader=csv.DictReader(stream);return reader.fieldnames,list(reader)


def main():
    original=json.loads((HERE/'checks/cycle_results.json').read_text());science=original['science']
    repeated=json.loads((HERE/'standalone/checks/cycle_results.json').read_text())
    receipt=json.loads((HERE/'standalone_reproduction.json').read_text())
    cleanup=json.loads((HERE/'compiler_cleanup.json').read_text());proof=json.loads((HERE/'checks/proof/result.json').read_text())
    require(science['all_preregistered_acceptance_conditions_met'] and science==repeated['science'] and
            receipt['actually_executed'] and receipt['runner_returncode']==0 and receipt['critical_file_count']==10 and
            receipt['fresh_public_dependencies_fetched_and_verified']==3 and receipt['all_four_worker_nontiming_results_match_original'] and
            receipt['all_twentyfive_detailed_records_byte_identical'] and cleanup['cache_absent_after_removal'] and
            not Path(cleanup['own_cache']).exists() and proof['main']['accepted'] and proof['named_declarations_compiled']==3,
            'Required scientific reproduction/cleanup incomplete')
    fields,before=ledger(HERE/'previous009_snapshot/CLAIM_LEDGER.csv');_,current=ledger(ROOT/'CLAIM_LEDGER.csv')
    require(len(before)==114 and sum(r['evidence_label']=='LEAN_COMPILED' for r in before)==94 and
            [r for r in current if r['cycle']!='10']==before,'Prior114 rows changed')
    lean=(HERE/'proposal/HistoryBuffer.lean').read_text()
    common={'cycle':'10','related_work_or_followup':'Dynamics-library prerequisite after004 fixed-input EMA and009 admission work. Generic buffer fact not a novelty claim; selected current Lean scopes exclude phase/history. Next candidate fresh-checks modulo-safe phase-increment/delayed-input bridge with startup separate; not executed.',
            'independent_review':'OWN_COMPILATION_REFERENCE_TESTS_CONTROLS_AND_EXTRACTED_REPRODUCTION_ONLY;NO_INDEPENDENT_010_SEAT_REVIEW',
            'publication':'LOCAL_PREPARED_FOR_OWNER_DATED_AUDIT_INBOX_UPLOAD;NOT_UPLOADED',
            'integration':'NEW_UNREGISTERED_LIBRARY_CANDIDATE_AND_EXECUTABLE_SPEC_ONLY;ALL_UPSTREAM_FROZEN_REGISTRY_LOCKS_UNCHANGED;NOT_INSTALLED'}
    formal_evidence=['PLAN.md','proposal/HistoryBuffer.lean','SOURCE_CORRESPONDENCE.md','checks/proof','checks_run.log',
                     'standalone_reproduction.json','standalone/checks/proof','standalone/reproduction.log','review_decision.json',
                     'compiler_setup.json','compiler_cleanup.json']
    rows=[]
    for short in ('historyTrace_index','historyTrace_oldest','historyTrace_newest'):
        symbol='Researcher040282.Delay.'+short
        header=re.search(r'(theorem '+re.escape(short)+r'\b[\s\S]*?) := by',lean)
        require(header is not None and symbol in proof['main']['footprints'],'Named proof/header absent')
        require(set(proof['main']['footprints'][symbol])=={'propext','Quot.sound'},'Unexpected final proof footprint')
        claim=dict(common,claim_id='R040282-010-'+short,symbol=symbol,
                   statement_or_exact_header=header.group(1),evidence_label='LEAN_COMPILED',
                   domain_and_scope='For arbitrary universe/value type A, natural D, trace x:Nat->A, constant H0=x0 and defined D+1 shift/append recurrence. Nat subtraction truncated at0. Coordinate theorem plus oldest/newest corollaries; all actually compiled Std-only, complete footprint coverage, no main warnings/errors/forbidden markers, eight formal controls, full extracted recompile. Source valid D>=1, abstract D0 mathematical only. Reachable value-history theorem, NOT every state accepted by Python validation, a copy-allocation/float/trigonometry FFI theorem, full coupled step, stability/locking or production certificate.',
                   evidence_files=';'.join('cycle_010/'+name for name in formal_evidence))
        require(set(claim)==set(fields),'Formal ledger schema mismatch');rows.append(claim)
    executable_evidence=['PLAN.md','proposal','SOURCE_CORRESPONDENCE.md','preexecution_case_design.json','checks','checks_run.log',
                         'standalone_reproduction.json','standalone/checks','standalone/reproduction.log',
                         'source_state/main_selected.json','source_state/inbox_selected.json','nonduplication_check.json','review_decision.json']
    claim=dict(common,claim_id='R040282-010-HISTORY-PHASE-PRIMITIVE-CONTRACT',symbol='unchanged_engine_history_phase_primitive_contract',
               statement_or_exact_header='Actual unchanged full frozen engine: nine common primitive-contract methods pass normal/-O,78 advances and1 initializer each mode, independent immutable math/cmath reference computed before advance. C updated -> magnitude then R symmetry -> clipped/conditional gated B -> phase with NEW gated B -> append COPY. Max component error2.220446049250313e-16 against fixed abs5e-13/rel0. Five D1..5 dyadic traces:60 transitions/65states/260 exact stored coordinates.11 independent wrong models detected by intended field each mode;2 invalid exact-delay configurations separately.10 inline files extracted/3 fresh public dependencies, complete runner repeated with same core compiler; science/4workers/25 detailed records match.',
               evidence_label='EXECUTABLE_REGRESSION_CHECK',
               domain_and_scope='Finite deterministic synthetic non-shuffled validated states; nine scalar-step cases N1..4/D1..4 plus reachable dyadic histories D1..5. Explicit finite real/imag, matrix, flag, history, RNG, structure/range/ownership checks; no reference from target outputs or copied/replaced source functions. One initializer probe per mode, not a production study. Other synthetic one-step histories not certified physical trajectories. No full baseline equivalence, real S01, shuffle/intervention/CLI/certificate, universal float/Python or full coupled Lean theorem; no source-repair/failing-before claim, frozen edit or installation.',
               evidence_files=';'.join('cycle_010/'+name for name in executable_evidence))
    require(set(claim)==set(fields),'Executable ledger schema mismatch');rows.append(claim);combined=before+rows
    require(len(combined)==len({r['claim_id'] for r in combined})==118 and sum(r['evidence_label']=='LEAN_COMPILED' for r in combined)==97,
            'Claim count/label mismatch')
    for row in rows:
        for path in row['evidence_files'].split(';'):require((ROOT/path).exists(),'Evidence absent: '+path)
    with (ROOT/'CLAIM_LEDGER.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(combined)
    state=json.loads((HERE/'previous009_snapshot/STATE.json').read_text());review=state['review_scope']
    if 'current009_policy_guard_contract_harness_independently_reviewed' in review:
        review['historical009_policy_guard_contract_harness_independently_reviewed']=review.pop('current009_policy_guard_contract_harness_independently_reviewed')
    review.update({'latest_selected_navigation_commit':'00a29ce538a40b553a723dd73dbd676129bfcd9a',
                   'general_TRIAGE_changed_since009':False,'new_provenance_mutation_report_evidence_read_only':True,
                   'new_contributed_reproducer_fetched_or_executed':False,'current010_history_oracle_controls_independently_reviewed':False})
    decision=json.loads((HERE/'review_decision.json').read_text())
    state.update({
        'last_updated_date':DATE,'timezone':'Atlantic/Reykjavik','current_cycle':10,'current_directory':'cycle_010',
        'current_status':'COMPLETED_LOCAL_HISTORY_FOUNDATION_AND_PHASE_CONTRACT_UNREVIEWED','ledger_rows':118,
        'current_question':'Close a load-bearing dynamics-library boundary: reachable constant-prehistory D+1 buffer indexing and actual non-shuffled coupled one-step update order, without assuming lag or full coupled stability.',
        'current_answer':'Three Std-only history declarations compile with propext/Quot.sound; oldest=x(max(0,n-D)), newest=x(n). Actual unchanged engine passes9 methods normal/-O,78advances+1initializer each, max component error2.220446049250313e-16 at abs5e-13/rel0;65dyadic states/260 exact stored coordinates.11wrong models eachmode;8formal controls;2exact-delay domain errors separately. Ten inline files/3fresh deps full rerun matches4workers/25details; own disposable compiler removed. Not formal Python/coupled-map equivalence, real study, installation or independent review.',
        'latest_completed_report':REPORT,'optional_supporting_bundle':'researcher040282-cycle010-history-phase-contract.zip',
        'artifact_validation_record':'cycle_010/packet_validation.json','handoff_status':'SCIENCE_AND_EXTRACTED_REPRODUCTION_COMPLETE;PACKET_CLOSURE_PENDING',
        'source_refresh':{'branch_for_current_code':'main','commit':science['tested_main'],'selected_files_verified':32,
                          'public_python_source_closure_verified':1,'scope_compiler_metadata_dependencies_verified':2,
                          'metadata':'cycle_010/source_state/main_selected.json',
                          'source_execution_scope':'Actual full frozen engine import; ModelConfig/DynamicState validation, one synthetic initialize_state and78advance_state calls per mode. No run_seed/simulate_prefix/future/baseline-equivalence/production/CLI/certificate.',
                          'inbox_navigation_commit':'00a29ce538a40b553a723dd73dbd676129bfcd9a','inbox_selected_files':8,
                          'inbox_metadata':'cycle_010/source_state/inbox_selected.json','targeted_intake_R001_notes_unchanged':True,
                          'general_TRIAGE_changed':False,'new_provenance_mutation_review_evidence_read_only':True,
                          'new_inbox_reproducer_fetched_or_executed':False,'nonduplication_check':'cycle_010/nonduplication_check.json',
                          'scope':'Selected read-only public inspection, not exhaustive/private-work coordination or independent approval.'},
        'tool_environment':{'python':original['environment']['python'],'packages_used':{'numpy':original['environment']['numpy']},
                            'fresh_lean_run_this_cycle':True,'new_compiled_named_declarations':3,'formal_controls':8,
                            'core_compiler_and_decoder_temporarily_installed_into_own_target_this_cycle':True,
                            'Mathlib_installed':False,'global_toolchain_changed':False,'earlier_lean_cache_restored':False,
                            'setup_receipt':'cycle_010/compiler_setup.json','own_disposable_setup_removed_after_reproduction':True,
                            'cleanup_receipt':'cycle_010/compiler_cleanup.json','compiler':original['environment']['compiler']},
        'adversarial_evidence':{'common_contract_methods':9,'source_passes_each_mode':9,'source_failures_errors_skips_each_mode':[0,0,0],
                               'wrong_models_detected_normal':11,'wrong_models_detected_optimized':11,'formal_controls':8,
                               'formal_positive':2,'formal_false_math':3,'formal_compiling_integrity':3,
                               'invalid_exact_delay_configs_each_mode_not_semantic_detections':2,'setup_errors_credited_as_detections':0,
                               'normal_and_optimized_nontiming_results_match':True,'results':'cycle_010/checks/cycle_results.json',
                               'worker_results':'cycle_010/checks/worker_results.json','original_runner_elapsed_seconds':original['elapsed_seconds'],
                               'initial_owned_proof_error_preserved_not_a_control':'cycle_010/development/initial_proof/compiler.log'},
        'source_comparison':{'evidence_label':'EXECUTABLE_REGRESSION_CHECK','scope':'Finite actual-engine non-shuffled primitive with independent scalar oracle, not formal Python equivalence.',
                             'actual_advances_each_mode':78,'initializer_calls_each_mode':1,'dyadic_exact_states_each_mode':65,
                             'dyadic_exact_stored_coordinates_each_mode':260,'absolute_tolerance':5e-13,'relative_tolerance':0.0,
                             'maximum_observed_component_error':science['maximum_observed_component_error'],
                             'reference':'Immutable math/cmath scalar cases; expected values before target advance, no pre-call compute_R',
                             'source_functions_copied_replaced_or_edited':False,'source_files_verified_unchanged':1,'metadata_files_verified_unchanged':2,
                             'source_repair_or_failing_before_claim':False,'production_study_or_full_baseline_equivalence':False},
        'formal_result':{'evidence_label':'LEAN_COMPILED','new_named_declarations':3,'total_formal_ledger_labels':97,
                         'imports':['Std'],'axiom_footprints':science['axiom_footprints'],
                         'theorem':'H(n)[i]=x(n+i-D), Nat truncated subtraction, constant prehistory/shift-append recurrence',
                         'scope':'Generic reachable value history; not arbitrary validated Python histories, allocations, floating phases or whole coupled map',
                         'source_valid_D_minimum':1,'abstract_D0_not_source_valid':True,'record':'cycle_010/checks/proof/result.json'},
        'authority_boundary':{'new_unregistered_library_candidate_and_finite_specification_only':True,
                              'actual_frozen_engine_read_only_import_and_synthetic_primitives':True,
                              'frozen_source_edited':False,'lock_or_registry_changed':False,'source_cache_edited':False,
                              'new_helper_or_module_installed':False,'authority_validation_run':False,'full_equivalence_pipeline_run':False,
                              'run_seed_simulate_production_CLI_or_writer_called':False,
                              'integration_decision':'OWNER_SEAT_PENDING;NO_AUTHORITY_PROMOTION_OR_PRODUCTION_REPAIR'},
        'standalone_reproduction':dict(receipt,record='cycle_010/standalone_reproduction.json',report=REPORT),
        'review_scope':review,'independent_review_received':True,'current_cycle_independent_review_received':False,
        'latest_packet_owner_upload_confirmed':False,
        'publication_status':'Prior114 rows/94 formal labels preserved. New3 generic history declarations actually compiled; finite source contract and controls/full extracted rerun pass. No independent010 review, library integration, authority promotion or upload.',
        'privacy':{'report':'cycle_010/privacy_results.json','new_metadata_minimal_at_acquisition':True,
                   'branch_metadata_records_expected':18,'no_personal_commit_contacts_or_signed_payloads_in_branch_metadata':True,
                   'new_contributed_reproducer_not_acquired_or_executed':True,
                   'historical_two_synthetic_public_fixture_addresses_distinguished':True,
                   'not_exhaustive_secret_detection_or_security_certification':True},
        'evidence_navigation':{'index':'EVIDENCE_INDEX.json','historical_log_map':'HISTORICAL_ARCHIVE_LOG_MAP.csv',
                               'all_ledger_references_unpacked':True,'old_archives_not_nested_or_changed':True},
        'previous_cycle':9,'previous_cycle_evidence':{'completed009_state':'cycle_010/previous009_snapshot/STATE.json',
                                                      'completed009_ledger114':'cycle_010/previous009_snapshot/CLAIM_LEDGER.csv',
                                                      'prior_science_not_rerun_this_cycle':True,
                                                      'completed008_state':'cycle_009/previous008_snapshot/STATE.json',
                                                      'completed008_ledger113':'cycle_009/previous008_snapshot/CLAIM_LEDGER.csv',
                                                      'completed007_ledger112':'cycle_008/previous007_snapshot/CLAIM_LEDGER.csv',
                                                      'completed006_ledger111':'cycle_007/previous006_snapshot/CLAIM_LEDGER.csv',
                                                      'completed005_ledger109':'cycle_006/previous005_snapshot/CLAIM_LEDGER.csv',
                                                      'completed004_ledger108':'cycle_005/completed_004_snapshot/CLAIM_LEDGER_COMPLETED_004.csv'},
        'completed_this_cycle':['fresh32main/8inbox selection and limited public nonduplication check; provenance report/evidence read-only',
                                'preregistered reachable history/scalar primitive contract and fixed tolerances before engine execution/proof compilation',
                                'three corrected Std-only history declarations compile; initial draft error preserved, not credited as a control',
                                'actual unchanged engine9pass normal/-O with78advances and1initializer each;65states/260exact stored coordinates',
                                '11intended wrong models eachmode;8formal controls;2invalid-delay domain cases separately',
                                'teninline files extracted/threefresh deps;complete runner repeats;4workers/25detailed records match',
                                'own temporary compiler/archive/decoder removed after actual rerun; no Mathlib/global toolchain change',
                                'prior114 ledger rows/94formal labels preserved;three scoped compiled rows plusone finite contract row',
                                'packet closure receipt required before delivery'],
        'not_proved_or_promoted':decision['not_approved']+[
            'Modulo-safe phase-input increment/delayed-drive theorem, sharper derived future ON/OFF bands or common finite freeze time',
            'Independent approval/integration of prior005-009 companions; exact historical boundaries in previous009 snapshot/reports'],
        'in_progress':None,'research_processes_running':[],'next_cycle':11,'next_directory':'cycle_011',
        'next_selected_work':decision['next_cycle_candidate_not_executed'],
        'immediate_next_action':'Only on another Continue: read latest owner/seat feedback and current source/library state, then preregister one smallest useful modulo-safe phase-increment/delayed-input lemma with constant startup distinct from live delayed trace. No coupled-locking assumption, production campaign, frozen edit or unattended work.',
        'remote_changes_by_this_agent':False,'contacted_other_bots':False,'automatic_work_between_turns':False,
    })
    (ROOT/'STATE.json').write_text(json.dumps(state,indent=2)+'\n')
    print('Finalized010:118unique rows; prior114/94formal preserved;3new compiled +1finite contract; no independent review/integration/upload')


if __name__=='__main__':main()
