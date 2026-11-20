"""Promote observed011 results ONLY after full extracted repetition + own cleanup.
Preserve118 prior rows/97formal labels; add3compiled +1finite contract. No upload,
integration, frozen/authority change or independent-review inference.
"""
from pathlib import Path
import csv
import json
import re

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
DATE='2026-09-04'
REPORT=DATE+'_researcher040282_011_modulo-phase-increment.md'

def require(condition,message):
    if not condition:raise RuntimeError(message)

def read(path):return json.loads(path.read_text())
def ledger(path):
    with path.open(newline='') as stream:
        reader=csv.DictReader(stream);return reader.fieldnames,list(reader)

def main():
    original=read(HERE/'checks/cycle_results.json');science=original['science'];repeat=read(HERE/'standalone/checks/cycle_results.json')
    receipt=read(HERE/'standalone_reproduction.json');cleanup=read(HERE/'compiler_cleanup.json');proof=read(HERE/'checks/proof/result.json')
    require(science['all_preregistered_acceptance_conditions_met'] and science==repeat['science'] and receipt['actually_executed'] and
            receipt['runner_returncode']==0 and receipt['critical_file_count']==13 and receipt['fresh_public_dependencies_fetched_and_verified']==4 and
            receipt['all_four_worker_nontiming_results_match_original'] and receipt['all_thirtyone_detailed_records_byte_identical'] and
            cleanup['cache_absent_after_removal'] and not Path(cleanup['own_cache']).exists() and proof['main']['accepted'] and
            proof['new_named_declarations_compiled']==3,'Reproduction/cleanup/formal acceptance incomplete')
    fields,before=ledger(HERE/'previous010_snapshot/CLAIM_LEDGER.csv');_,current=ledger(ROOT/'CLAIM_LEDGER.csv')
    require(len(before)==118 and sum(r['evidence_label']=='LEAN_COMPILED' for r in before)==97 and [r for r in current if r['cycle']!='11']==before,'Prior118 rows changed')
    lean=(HERE/'proposal/PhaseIncrement.lean').read_text()
    common={'cycle':'11','related_work_or_followup':'One dynamics-library prerequisite after010 constant-history indexing and004 exact-real EMA. Standard modulo/phasor mathematics, no novelty/engine-defect claim. Limited public current-library/head/PR navigation found no duplicate; not exhaustive/private assurance. Next candidate time-varying-input EMA tracking only after another Continue/fresh check; not selected/executed012.',
            'independent_review':'OWN_COMPILATION_FINITE_SOURCE_CONTROLS_AND_EXTRACTED_REPRODUCTION_ONLY;NO_INDEPENDENT_011_SEAT_REVIEW',
            'publication':'LOCAL_PREPARED_FOR_OWNER_DATED_AUDIT_INBOX_UPLOAD;NOT_UPLOADED',
            'integration':'NEW_UNREGISTERED_LIBRARY_CANDIDATE_AND_FINITE_SPEC_ONLY;UPSTREAM_FROZEN_SOURCE_REGISTRY_LOCKS_UNCHANGED;NOT_INSTALLED'}
    formal=['PLAN.md','proposal/PhaseIncrement.lean','proposal/HistoryBuffer.lean','SOURCE_CORRESPONDENCE.md','checks/proof','checks_run.log',
            'standalone_reproduction.json','standalone/checks/proof','standalone/reproduction.log','review_decision.json','compiler_setup.json','mathlib_setup.json','compiler_cleanup.json']
    rows=[]
    for short in ('phasor_wrap','delayed_input_step','delayed_input_chord_bound'):
        symbol='Researcher040282.Phase.'+short;header=re.search(r'(theorem '+re.escape(short)+r'\b[\s\S]*?) := by',lean)
        require(header is not None and set(proof['main']['footprints'][symbol])=={'propext','Classical.choice','Quot.sound'},'Missing theorem/header/standard footprint')
        claim=dict(common,claim_id='R040282-011-'+short,symbol=symbol,statement_or_exact_header=header.group(1),evidence_label='LEAN_COMPILED',
            domain_and_scope='Arbitrary real initial vector, arbitrary unwrapped increment function and index type; defined floor-wrapped recurrence,010 constant-prehistory D+1 value history. E(W(t))=E(t); exact source-shaped input factor with delayed increment0 for n<D, otherwise u(n-D,j); circular chord <=signed-increment absolute value. Three new named claims, standard complete footprints/no final main warnings/errors/forbidden markers,8formal controls and full extracted repeat. Recompiled010 history3not new labels. Generic D0 mathematical only, source D>=1. Not NumPy/Python floating remainder/trig/FFI, complete coupled C/R/B evolution, integrated004 EMA/capacity theorem, locking/convergence/freeze-time or production certificate.',
            evidence_files=';'.join('cycle_011/'+x for x in formal))
        require(set(claim)==set(fields),'Formal ledger schema mismatch');rows.append(claim)
    finite=['PLAN.md','proposal','SOURCE_CORRESPONDENCE.md','preexecution_case_design.json','checks','checks_run.log','standalone_reproduction.json',
            'standalone/checks','standalone/reproduction.log','source_state/main_selected.json','source_state/inbox_selected.json','nonduplication_check.json','review_intake.json','review_decision.json']
    claim=dict(common,claim_id='R040282-011-MODULO-PHASE-INPUT-CONTRACT',symbol='unchanged_engine_modulo_phase_input_contract',
        statement_or_exact_header='Actual unchanged Frozen engine:9common methods pass normal/-O,7constant-prehistory synthetic traces/56advances/0initializers eachmode;496complex inputs z0..z7 and434adjacent coordinates n0..6=157startup+277live (62first-live). Independent immutable math/cmath traces before acquired import. NEW gated B forcing, C pre-phase read, absolute pair-mean offset, positive/negative/multiwrap and legitimate representative/constant-offset phasor invariances. Max source component4.440892098500626e-16, ratio7.348288644237755e-15 against fixed abs5e-13/rel0.10intended wrong models/mode;8formal controls.13inline files extracted/4fresh public deps; full runner repeated with same verified compiler/targeted Mathlib; science/4workers/31detailed records match.',
        evidence_label='EXECUTABLE_REGRESSION_CHECK',
        domain_and_scope='Finite deterministic manually initialized N1/N3/N4,D1..4 non-shuffled trajectories, constant initial history/C0zero. Eight actual C updates produce z0..z7, not z1..z8; decoded observations never expected values. Full C/B/theta/history/R fields plus explicit finite complex components/shape, bools, structure/range/ownership and unchanged RNG. Paper row-capacity specialization finitely checked, not a new formal coupled gate theorem. Ordinary representative increment equality intentionally false at winding; its phasor equality and constant-offset ratio cancellation correctly positive. No source-repair/failing-before claim, arbitrary-float/full coupled Lean equivalence, real study/S01/baseline/shuffle/intervention/CLI/certificate, source edit or installation; independent review absent.',
        evidence_files=';'.join('cycle_011/'+x for x in finite))
    require(set(claim)==set(fields),'Finite ledger schema mismatch');rows.append(claim);combined=before+rows
    require(len(combined)==len({r['claim_id'] for r in combined})==122 and sum(r['evidence_label']=='LEAN_COMPILED' for r in combined)==100,'Final label counts differ')
    for row in rows:
        for x in row['evidence_files'].split(';'):require((ROOT/x).exists(),'Unpacked evidence absent: '+x)
    with (ROOT/'CLAIM_LEDGER.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(combined)
    state=read(HERE/'previous010_snapshot/STATE.json');review=state['review_scope']
    if 'current010_history_oracle_controls_independently_reviewed' in review:
        review['historical010_history_oracle_controls_independently_reviewed']=review.pop('current010_history_oracle_controls_independently_reviewed')
    review.update(latest_selected_navigation_commit='4fbd00b6e5f975b49bd74885e8c381af9abaf9f7',current011_phase_increment_controls_independently_reviewed=False,
                  general_TRIAGE_changed_since010=False,new_Part5_trust_anchor_design_evidence_read_only=True,new_contributed_reproducer_fetched_or_executed=False)
    decision=read(HERE/'review_decision.json')
    state.update({
        'last_updated_date':DATE,'timezone':'Atlantic/Reykjavik','current_cycle':11,'current_directory':'cycle_011',
        'current_status':'COMPLETED_LOCAL_MODULO_PHASE_INCREMENT_AND_CHORD_BOUND_UNREVIEWED','ledger_rows':122,
        'current_question':'Close modulo-safe delayed input increment/chord boundary with constant startup and actual NEW gated B forcing, without assuming locking or claiming complete floating/coupled equivalence.',
        'current_answer':'Three exact-real floor-wrap/input-step/chord claims compile with complete standard footprints; L_nj=0 for n<D else u_(n-D,j). Unchanged engine9pass normal/-O with56advances/mode,496inputs/434ratios,10wrongmodels/mode,8formalcontrols; fixed abs5e-13/rel0.13inline files/4fresh deps full rerun match4workers/31details. Own compiler/Mathlib/Git/decoder/archive cache removed. Not float/full-coupled/locking proof, real study, installed library or independent approval.',
        'latest_completed_report':REPORT,'optional_supporting_bundle':'researcher040282-cycle011-modulo-phase-increment.zip',
        'artifact_validation_record':'cycle_011/packet_validation.json','handoff_status':'SCIENCE_AND_EXTRACTED_REPRODUCTION_COMPLETE;PACKET_CLOSURE_PENDING',
        'source_refresh':{'branch_for_current_code':'main','commit':science['tested_main'],'selected_files_verified':32,'public_python_source_closure_verified':1,
            'scope_compiler_metadata_dependencies_verified':3,'metadata':'cycle_011/source_state/main_selected.json',
            'source_execution_scope':'Intact engine import, ModelConfig/DynamicState validation,56synthetic advance_state calls/mode. No initialize_state/run_seed/simulate_*/production/baseline/CLI/certificate.',
            'inbox_navigation_commit':'4fbd00b6e5f975b49bd74885e8c381af9abaf9f7','inbox_selected_files':8,'inbox_metadata':'cycle_011/source_state/inbox_selected.json',
            'targeted_intake_R001_notes_unchanged':True,'general_TRIAGE_changed':False,'new_Part5_trust_anchor_design_evidence_read_only':True,
            'new_inbox_reproducer_fetched_or_executed':False,'nonduplication_check':'cycle_011/nonduplication_check.json',
            'API403_fallback':'Read-only Git shallow blobless ref/tree +raw selected verified files; separately read public PR HTML',
            'scope':'Limited selected public read-only navigation, not exhaustive/private coordination or independent approval'},
        'tool_environment':{'python':original['environment']['python'],'packages_used':{'numpy':original['environment']['numpy']},'fresh_lean_run_this_cycle':True,
            'new_compiled_named_declarations':3,'reused_history_declarations_not_new_labels':3,'formal_controls':8,
            'complete_runtime_decoder_and_targeted_Mathlib_temporarily_installed_into_own_target':True,'Mathlib_installed_temporarily':True,
            'global_toolchain_changed':False,'earlier_lean_cache_restored':False,'setup_receipt':'cycle_011/compiler_setup.json','mathlib_setup_receipt':'cycle_011/mathlib_setup.json',
            'own_disposable_setup_removed_after_reproduction':True,'cleanup_receipt':'cycle_011/compiler_cleanup.json','compiler':original['environment']['compiler'],
            'mathlib_revision':original['environment']['mathlib_revision']},
        'adversarial_evidence':{'common_contract_methods':9,'source_passes_each_mode':9,'source_failures_errors_skips_each_mode':[0,0,0],
            'wrong_models_detected_normal':10,'wrong_models_detected_optimized':10,'formal_controls':8,'formal_positive':2,'formal_false_math':3,
            'formal_compiling_integrity':3,'setup_errors_credited_as_detections':0,'normal_and_optimized_nontiming_results_match':True,
            'results':'cycle_011/checks/cycle_results.json','worker_results':'cycle_011/checks/worker_results.json','original_runner_elapsed_seconds':original['elapsed_seconds'],
            'retained_failed_control_attempt_not_credited':'cycle_011/development/first_full_runner_control_blocker','all_development_errors_not_controls':True},
        'source_comparison':{'evidence_label':'EXECUTABLE_REGRESSION_CHECK','scope':'Finite coupled phase-input/scalar-reference primitive correspondence, not formal float/Python equivalence',
            'actual_advances_each_mode':56,'initializer_calls_each_mode':0,'input_complex_coordinates_each_mode':496,'adjacent_complex_coordinates_each_mode':434,
            'startup_adjacent_coordinates_each_mode':157,'first_live_coordinates_each_mode':62,'absolute_tolerance':5e-13,'relative_tolerance':0.0,
            'maximum_observed_component_error':science['maximum_observed_component_error'],'maximum_ratio_component_error':science['maximum_ratio_component_error'],
            'reference':'All immutable pure math/cmath expected traces before engine import; C innovation extraction observed only; no pre-call compute_R',
            'source_functions_copied_replaced_or_edited':False,'source_files_verified_unchanged':1,'metadata_files_verified_unchanged':3,
            'source_repair_or_failing_before_claim':False,'production_study_or_full_baseline_equivalence':False},
        'formal_result':{'evidence_label':'LEAN_COMPILED','new_named_declarations':3,'reused_history_declarations_not_new_labels':3,'total_formal_ledger_labels':100,
            'Mathlib_used':True,'axiom_footprints':science['axiom_footprints'],'theorem':'E(W(t))=E(t); z_(n+1)=z_n*E(u_n-L_n), L_n=0 startup else u_(n-D); chord<=|u_n-L_n|',
            'scope':'Exact-real arbitrary-increment wrapped phase +constant history; not floating FFI, integrated004 EMA/capacity or full coupled locking',
            'source_valid_D_minimum':1,'abstract_D0_not_source_valid':True,'record':'cycle_011/checks/proof/result.json'},
        'authority_boundary':{'new_unregistered_library_candidate_and_finite_specification_only':True,'actual_frozen_engine_read_only_import_and_synthetic_primitives':True,
            'frozen_source_edited':False,'lock_or_registry_changed':False,'source_cache_edited':False,'new_helper_or_module_installed':False,'authority_validation_run':False,
            'full_equivalence_pipeline_run':False,'run_seed_simulate_production_CLI_or_writer_called':False,'integration_decision':'OWNER_SEAT_PENDING;NO_AUTHORITY_PROMOTION_OR_PRODUCTION_REPAIR'},
        'standalone_reproduction':dict(receipt,record='cycle_011/standalone_reproduction.json',report=REPORT),'review_scope':review,
        'current_cycle_independent_review_received':False,'latest_packet_owner_upload_confirmed':False,
        'publication_status':'Prior118rows/97formal labels preserved;3new exact-real claims actually compiled +1finite source contract. Own controls/extracted repetition, no independent011 review/library integration/authority promotion/upload.',
        'privacy':{'report':'cycle_011/privacy_results.json','new_metadata_minimal_at_acquisition':True,'branch_metadata_records_expected':20,
            'no_personal_commit_contacts_or_signed_payloads_in_branch_metadata':True,'new_contributed_reproducer_not_acquired_or_executed':True,
            'raw_Git_objects_removed_with_own_cache_after_reproduction':True,'historical_two_synthetic_public_fixture_addresses_distinguished':True,
            'not_exhaustive_secret_detection_or_security_certification':True},
        'evidence_navigation':{'index':'EVIDENCE_INDEX.json','historical_log_map':'HISTORICAL_ARCHIVE_LOG_MAP.csv','all_ledger_references_unpacked':True,'old_archives_not_nested_or_changed':True},
        'previous_cycle':10,'previous_cycle_evidence':dict(state['previous_cycle_evidence'],completed010_state='cycle_011/previous010_snapshot/STATE.json',
            completed010_ledger118='cycle_011/previous010_snapshot/CLAIM_LEDGER.csv',historical_full_suites_not_rerun=True,
            reused010_history_module_and_scalar_reference_explicitly_declared=True),
        'completed_this_cycle':['fresh32main/8inbox texts; API403/read-only Git/raw fallback/public PR HTML; limited nonduplication before selection',
            'preregistered exact-real modulo/startup-aware input/chord and seven fixed finite trajectories before owned proof/source execution',
            'three new clean standard-footprint declarations and unchanged010 history dependency; development errors preserved/not promoted',
            '9source methods normal/-O,56advances/496inputs/434adjacent coordinates per mode,10intended wrongmodels/mode',
            '8actual formal controls:2nonzero positives,3explicitFalse math witnesses,3compiling integrity payload refusals',
            '13inline files extracted/4fresh deps/full runner repeated;4workers/31detailed records match',
            'own complete runtime/targeted Mathlib/archive/decoder/Git cache removed only after actual repeat',
            'prior118/97formal labels preserved;3scoped compiled rows +1finite contract added; packet closure required before delivery'],
        'not_proved_or_promoted':decision['not_approved']+['Exact integrated source-coupled capacity or004 time-varying-input EMA tracking theorem; independent approval of prior005-010 companions'],
        'in_progress':None,'research_processes_running':[],'next_cycle':12,'next_directory':'cycle_012','next_selected_work':decision['next_cycle_candidate_not_executed'],
        'immediate_next_action':'Only another Continue: fresh feedback/source/library/nonduplication check before selecting/preregistering smallest time-varying-input EMA tracking lemma. No locking premise, full campaign, frozen edit or unattended012.',
        'remote_changes_by_this_agent':False,'contacted_other_bots':False,'automatic_work_between_turns':False})
    (ROOT/'STATE.json').write_text(json.dumps(state,indent=2)+'\n')
    print('Finalized011:122unique rows/100formal labels; prior118/97 preserved;3new compiled+1finite contract; no independent review/integration/upload')

if __name__=='__main__':main()
