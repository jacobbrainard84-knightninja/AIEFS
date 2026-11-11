"""Promote observed012scoped results after exact-note full repeat/own cleanup.
Preserve122prior rows/100formal labels;3new compiled+1finite contract, no remote
upload/integration/authority change or independent-seat inference.
"""
from pathlib import Path
import csv
import json
import re

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
DATE='2026-09-04'
REPORT=DATE+'_researcher040282_012_causal-ema-tracking.md'

def require(condition,message):
    if not condition:raise RuntimeError(message)

def read(path):return json.loads(path.read_text())
def ledger(path):
    with path.open(newline='') as stream:
        r=csv.DictReader(stream);return r.fieldnames,list(r)

def main():
    original=read(HERE/'checks/cycle_results.json');science=original['science'];repeated=read(HERE/'standalone/checks/cycle_results.json')
    receipt=read(HERE/'standalone_reproduction.json');cleanup=read(HERE/'compiler_cleanup.json');proof=read(HERE/'checks/proof/result.json')
    require(science==repeated['science'] and science['all_preregistered_acceptance_conditions_met'] and receipt['actually_executed'] and receipt['runner_returncode']==0 and
            receipt['critical_file_count']==16 and receipt['fresh_public_dependencies_fetched_and_verified']==4 and receipt['all_four_worker_nontiming_results_match_original'] and
            receipt['all_thirtyfive_detailed_records_byte_identical'] and proof['main']['accepted'] and proof['new_named_declarations_compiled']==3 and
            proof['reused_named_declarations_recompiled_not_new_labels']==28 and cleanup['cache_absent_after_removal'] and not Path(cleanup['own_cache']).exists(),'Required repeat/proof/cleanup incomplete')
    fields,before=ledger(HERE/'previous011_snapshot/CLAIM_LEDGER.csv');_,current=ledger(ROOT/'CLAIM_LEDGER.csv')
    require(len(before)==122 and sum(x['evidence_label']=='LEAN_COMPILED' for x in before)==100 and [x for x in current if x['cycle']!='12']==before,'Prior122/100 scope changed')
    source=(HERE/'proposal/EMATracking.lean').read_text();common={'cycle':'12',
        'related_work_or_followup':'Standard causal linear-filter tracking/convolution formalized at actual moving delayed-phase input boundary; composes004EMA and011/010phase/history.22current public heads/1open R-frozen gate-P3PR and current42main texts inspected; no EMA tracking duplicate found, not exhaustive/private assurance. No rate-law/guard/entrypoint/uploader/chronicler duplicate. Next reported-R composition only after another Continue/fresh check, not selected013.',
        'independent_review':'OWN_COMPILATION_FINITE_SOURCE_CONTROLS_AND_EXTRACTED_REPRODUCTION_ONLY;NO_INDEPENDENT_012_SEAT_REVIEW',
        'publication':'LOCAL_PREPARED_FOR_OWNER_DATED_AUDIT_INBOX_UPLOAD;NOT_UPLOADED',
        'integration':'NEW_UNREGISTERED_LIBRARY_CANDIDATE_AND_FINITE_SPEC_ONLY;FROZEN_SOURCE_REGISTRY_LOCKS_UNCHANGED;NOT_INSTALLED'}
    formal=['PLAN.md','proposal/EMATracking.lean','proposal/CoherenceEMA.lean','proposal/PhaseIncrement.lean','proposal/HistoryBuffer.lean','SOURCE_CORRESPONDENCE.md',
            'checks/proof','checks_run.log','standalone_reproduction.json','standalone/checks/proof','standalone/reproduction.log','review_decision.json','compiler_setup.json','mathlib_setup.json','compiler_cleanup.json']
    rows=[]
    for short in ('tracking_error_step','tracking_error_budget','delayed_phase_tracking_budget'):
        symbol='Researcher040282.Tracking.'+short;header=re.search(r'(theorem '+re.escape(short)+r'\b[\s\S]*?) := by',source)
        require(header is not None and set(proof['main']['footprints'][symbol])=={'propext','Classical.choice','Quot.sound'},'Header/standard footprint absent')
        row=dict(common,claim_id='R040282-012-'+short,symbol=symbol,statement_or_exact_header=header.group(1),evidence_label='LEAN_COMPILED',
            domain_and_scope='Exact-real C_(n+1)=alpha*C_n+(1-alpha)*z_n, arbitrary complex C0/sequence z: e_(n+1)=alpha e_n-Delta z_n; alpha>=0 gives chronological alpha^n initial error +sum_(k<n)alpha^(n-1-k)||Delta z_k|| bound. Definition-level004phaseInput/EMA composition with011wrapped trace/010constant history replaces variation by |u_ki-L_kj|,L0startup else aged increment. No alpha<1/small-drift/locking premise; alpha0/1abstract covered, source alpha0invalid/float1valid, source D>=1/generic D0only mathematical.3new clean complete standard-footprint claims,28old dependency declarations recompiled NOT new labels;8formal controls/full extracted repeat. Not floating FFI/full coupled map, strict contraction for alpha1, integrated main project, sharp Rbands/freezing/locking or production certificate.',
            evidence_files=';'.join('cycle_012/'+x for x in formal))
        require(set(row)==set(fields),'Formal ledger schema mismatch');rows.append(row)
    evidence=['PLAN.md','proposal','SOURCE_CORRESPONDENCE.md','preexecution_case_design.json','checks','checks_run.log','standalone_reproduction.json','standalone/checks','standalone/reproduction.log',
              'source_state/main_selected.json','source_state/inbox_selected.json','nonduplication_check.json','review_intake.json','selection_refinement.json','review_decision.json']
    row=dict(common,claim_id='R040282-012-CAUSAL-EMA-TRACKING-CONTRACT',symbol='unchanged_engine_causal_EMA_tracking_contract',
        statement_or_exact_header='Intact Frozen engine9common methods pass normal/-O;6synthetic traces/60advances/0initializers per mode.370current and370consumed-input error coordinates,333causal recurrences (115startup/218live/37first-live),240offdiag Rbounds/130diag0.360actual Cinnovations decoded,10roundedalpha1inputs only reconstructed from observed arguments; beta0never divided, alpha1Cexactly unchanged, tail error0.8062257748298549. Independent full trajectories AND370derived cells before acquired import. Max component9.992007221626409e-16, causal/unroll4.440892098500626e-16, consumed2.220446049250313e-16 at fixed abs5e-13/rel0.10wrong models/mode require actual false-bound violation or intended equality mismatch>1e-7;8formal controls.16inline files/4fresh deps full runner repeat, science/4workers/35details match.',
        evidence_label='EXECUTABLE_REGRESSION_CHECK',
        domain_and_scope='Finite manually initialized N1/N3/N4,D1..4,dt.125,Twindow.0625/.125/.5/2/1e20 non-shuffled source states, not random production outputs. Nonzero C0, moving input/startup, multiple windings and NEW gated B; no pre-call compute_R/source replacement. R after C, temporal unroll, explicit finite components/shape, bools/range/ownership and RNG/input/table preservation checked. Formula-only beta0channel not called decoded or skipped. Paper uniform-variation/Rbounds finitely checked, not extra compiled claims. Source alpha1edge not production-cohort defect/infinite-time claim; exact-real physicalAlpha strict<1 not float FFI.012corrects011validation table gap overstatement in numbered followup, prior science untouched. No production/S01/baseline/shuffle/intervention/CLI/certificate, repair/install/independent review.',
        evidence_files=';'.join('cycle_012/'+x for x in evidence))
    require(set(row)==set(fields),'Finite ledger schema mismatch');rows.append(row);combined=before+rows
    require(len(combined)==len({x['claim_id'] for x in combined})==126 and sum(x['evidence_label']=='LEAN_COMPILED' for x in combined)==103,'Claim totals differ')
    for row in rows:
        for x in row['evidence_files'].split(';'):require((ROOT/x).exists(),'Unpacked evidence absent: '+x)
    with (ROOT/'CLAIM_LEDGER.csv').open('w',newline='') as stream:
        w=csv.DictWriter(stream,fieldnames=fields);w.writeheader();w.writerows(combined)
    state=read(HERE/'previous011_snapshot/STATE.json');review=state['review_scope']
    if 'current011_phase_increment_controls_independently_reviewed' in review:review['historical011_phase_increment_controls_independently_reviewed']=review.pop('current011_phase_increment_controls_independently_reviewed')
    review.update(latest_selected_navigation_commit='b61f4340a4dfc9ae5b2732e51efeb49d0c10bd3d',current012_EMA_tracking_controls_independently_reviewed=False,
        current_main_new_file_F4_F6_F7_and_guard_context_acknowledged=True,contributor_genuineS01_validation_positive_not_our009harness_approval=True,
        targeted_intake_R001_notes_unchanged=True,new_entrypoint_and_guard_reproducers_acquired_or_executed=False)
    decision=read(HERE/'review_decision.json')
    state.update({'last_updated_date':DATE,'timezone':'Atlantic/Reykjavik','current_cycle':12,'current_directory':'cycle_012',
        'current_status':'COMPLETED_LOCAL_CAUSAL_EMA_TRACKING_AND_PHASE_COMPOSITION_UNREVIEWED','ledger_rows':126,
        'current_question':'What causal finite EMA tracking error follows from moving wrapped delayed phasor inputs without assuming locking or float alpha<1?',
        'current_answer':'Three clean standard-footprint causal-error/finite-convolution/delayed-phase composition claims;28old dependencies not new labels. Intact engine9pass normal/-O,60advances/mode,370current/370consumed/333causal coords;360decoded inputs/10explicit beta0formula-only; source alpha1Cunchanged.10wrong models/mode,8formal controls.16inline/4fresh deps/full repeat match4workers/35details; own setup/quarantined input removed. No full coupled/float/locking or independent approval.',
        'latest_completed_report':REPORT,'optional_supporting_bundle':'researcher040282-cycle012-causal-ema-tracking.zip','artifact_validation_record':'cycle_012/packet_validation.json',
        'handoff_status':'SCIENCE_AND_EXTRACTED_REPRODUCTION_COMPLETE;PACKET_CLOSURE_PENDING',
        'source_refresh':{'branch_for_current_code':'main','commit':science['tested_main'],'selected_files_verified':42,'public_python_source_closure_verified':1,
            'scope_compiler_metadata_dependencies_verified':3,'metadata':'cycle_012/source_state/main_selected.json','source_execution_scope':'Full Frozen engine import/validation,60synthetic advance_state calls per mode; no initializer, production, baseline, S01, shuffle, CLI or certificate',
            'inbox_navigation_commit':'b61f4340a4dfc9ae5b2732e51efeb49d0c10bd3d','inbox_selected_files':12,'inbox_metadata':'cycle_012/source_state/inbox_selected.json',
            'targeted_intake_R001_notes_unchanged':True,'contributor_scripts_acquired_or_executed':False,'nonduplication_check':'cycle_012/nonduplication_check.json',
            'transport':'Read-only Git shallow blobless ref/tree plus selected raw files, public PR HTML; no current012API403attempt',
            'selection_refinement':'Token EMA excludes incidental email/schema; irrelevant raw PII-path text quarantined outside outgoing evidence then removed with own cache',
            'new_main_context':'Gate P1/P2landed/P3PR24R-frozen; E19-E21new-file successors/errata/tests and E24-E26guards now landed per current read; E22sweep alreadydone, not duplicated',
            'scope':'Limited public/source/feedback read, not exhaustive/private coordination or independent approval'},
        'tool_environment':{'python':original['environment']['python'],'packages_used':{'numpy':original['environment']['numpy']},'fresh_lean_run_this_cycle':True,
            'new_compiled_named_declarations':3,'reused_named_declarations_not_new_labels':28,'formal_controls':8,'complete_runtime_decoder_and_targeted_Mathlib_temporarily_installed_into_own_target':True,
            'global_toolchain_changed':False,'earlier_lean_cache_restored':False,'setup_receipt':'cycle_012/compiler_setup.json','mathlib_setup_receipt':'cycle_012/mathlib_setup.json',
            'own_disposable_setup_removed_after_reproduction':True,'cleanup_receipt':'cycle_012/compiler_cleanup.json','compiler':original['environment']['compiler'],'mathlib_revision':original['environment']['mathlib_revision']},
        'adversarial_evidence':{'common_contract_methods':9,'source_passes_each_mode':9,'source_failures_errors_skips_each_mode':[0,0,0],
            'wrong_models_detected_normal':10,'wrong_models_detected_optimized':10,'formal_controls':8,'formal_positive':2,'formal_false_math':3,'formal_compiling_integrity':3,
            'setup_errors_credited_as_detections':0,'normal_and_optimized_nontiming_results_match':True,'results':'cycle_012/checks/cycle_results.json','worker_results':'cycle_012/checks/worker_results.json',
            'original_runner_elapsed_seconds':original['elapsed_seconds'],'retained_blockers_not_detections':'cycle_012/development','source_passed_before_control_syntax_fix':True},
        'source_comparison':{'evidence_label':'EXECUTABLE_REGRESSION_CHECK','scope':'Finite causal moving-input EMA/component correspondence, not formal Python/float equivalence',
            'actual_advances_each_mode':60,'initializer_calls_each_mode':0,'current_tracking_coordinates_each_mode':370,'consumed_input_coordinates_each_mode':370,'adjacent_causal_coordinates_each_mode':333,
            'decoded_innovation_coordinates_each_mode':360,'alpha1_formula_only_input_coordinates_each_mode':10,'absolute_tolerance':5e-13,'relative_tolerance':0.0,
            'maximum_observed_component_error':science['maximum_observed_component_error'],'tracking_stats':science['tracking_stats'],
            'reference':'All immutable math/cmath traces and370derived cells before acquired import; observed data and independent predictions distinct; no pre-call compute_R',
            'source_functions_copied_replaced_or_edited':False,'source_files_verified_unchanged':1,'metadata_files_verified_unchanged':3,'source_repair_or_failing_before_claim':False,'production_study_or_full_baseline_equivalence':False},
        'formal_result':{'evidence_label':'LEAN_COMPILED','new_named_declarations':3,'reused_named_declarations_not_new_labels':28,'total_formal_ledger_labels':103,'Mathlib_used':True,'axiom_footprints':science['axiom_footprints'],
            'theorem':'e_next=alpha*e-Delta z; finite chronological weighted-norm budget; definition-level004EMA/011phase/010history composition via signed increment bound',
            'alpha_domain':'Identity all real alpha; finite bounds alpha>=0, no alpha<1or division by1-alpha; abstract alpha0not source valid, float1can be',
            'scope':'Exact-real components composed, not full coupled map/float FFI, sharp future bands or locking','record':'cycle_012/checks/proof/result.json'},
        'authority_boundary':{'new_unregistered_library_candidate_and_finite_specification_only':True,'actual_frozen_engine_read_only_import_and_synthetic_primitives':True,
            'frozen_source_edited':False,'lock_or_registry_changed':False,'source_cache_edited':False,'new_helper_or_module_installed':False,'authority_validation_run':False,'full_equivalence_pipeline_run':False,
            'run_seed_simulate_production_CLI_or_writer_called':False,'integration_decision':'OWNER_SEAT_PENDING;NO_AUTHORITY_PROMOTION_OR_PRODUCTION_REPAIR'},
        'standalone_reproduction':dict(receipt,record='cycle_012/standalone_reproduction.json',report=REPORT),'review_scope':review,'current_cycle_independent_review_received':False,
        'latest_packet_owner_upload_confirmed':False,'publication_status':'Prior122/100 preserved;3new component claims actually compiled+1finite contract, no independent012review/project integration/authority promotion/upload',
        'privacy':{'report':'cycle_012/privacy_results.json','new_metadata_minimal_at_acquisition':True,'branch_metadata_records_expected':22,'no_personal_commit_contacts_or_signed_payloads_in_branch_metadata':True,
            'contributed_reproducers_not_acquired_or_executed':True,'raw_Git_and_irrelevant_PII_input_confined_to_own_excluded_cache_then_removed':True,
            'contact_values_not_printed':True,'historical_two_synthetic_public_fixture_addresses_distinguished':True,'not_exhaustive_secret_detection_or_security_certification':True},
        'evidence_navigation':{'index':'EVIDENCE_INDEX.json','historical_log_map':'HISTORICAL_ARCHIVE_LOG_MAP.csv','all_ledger_references_unpacked':True,'old_archives_not_nested_or_changed':True},
        'previous_cycle':11,'previous_cycle_evidence':dict(state['previous_cycle_evidence'],completed011_state='cycle_012/previous011_snapshot/STATE.json',completed011_ledger122='cycle_012/previous011_snapshot/CLAIM_LEDGER.csv',historical_full_suites_not_rerun=True,reused004_010_011_components_explicitly_declared=True),
        'numbered_followup_correction':{'target':'011SOURCE_CORRESPONDENCE/inline source table','clarification':'DynamicState.validate is structural/finite/history length/Bsymmetry/diag/nonnegative, NOT gap/capacity/reachability; advance checks post-gap','old_report_code_results_ledger_rows_unchanged':True,'record':'cycle_012/SOURCE_CORRESPONDENCE.md'},
        'completed_this_cycle':['fresh42main/12retained inbox texts and22heads/1PR limited coordination; new landed-team state acknowledged, no duplicate work',
            'preregistered3causal tracking claims,6fixed cases/tolerance/tenwrongmodels/eightformalcontrols before owned proof/source calls',
            'corrected new3main compile clean;28reused component declarations recompiled without new labels, failed own drafts/control syntax retained/not credited',
            '9source methods normal/-O,60advances/370current/370consumed/333causal/360decoded+10explicit alpha1formula-only per mode',
            '10wrongmodels/mode,8formalcontrols,16inline/4fresh deps/full actual repeat match4workers/35details',
            'own runtime/archive/decoder/Git/Mathlib/quarantined irrelevant input cache removed after actual repeat',
            'new numbered011validation wording correction, prior122/100 and all completed evidence preserved, packet closure before delivery'],
        'not_proved_or_promoted':decision['not_approved'],'in_progress':None,'research_processes_running':[],'next_cycle':13,'next_directory':'cycle_013',
        'next_selected_work':decision['next_cycle_candidate_not_executed'],'immediate_next_action':'Only another Continue: fresh feedback/source/library/nonduplication then consider smallest exact reported-R envelope composition; no sharp-band/locking premise, real study/frozen edit or unattended013',
        'remote_changes_by_this_agent':False,'contacted_other_bots':False,'automatic_work_between_turns':False})
    (ROOT/'STATE.json').write_text(json.dumps(state,indent=2)+'\n')
    print('Finalized012:126unique rows/103formal labels, prior122/100 preserved;3new compiled+1finite contract; no independent review/integration/upload')

if __name__=='__main__':main()
