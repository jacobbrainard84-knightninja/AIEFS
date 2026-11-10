"""Owned011 packet/preservation/privacy closure, no source/proof science rerun.
Not independent review, integration, authority validation or security certification.
"""
from pathlib import Path
import ast
import cmath
import csv
import hashlib
import json
import math
import re
import zipfile
import build_packet as builder

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
EMAIL=re.compile(rb"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
BLOCK=re.compile(r'<!-- BEGIN_CRITICAL_FILE: ([^>\n]+) -->\n```[^\n]*\n(.*?)\n```\n'
                 r'<!-- END_CRITICAL_FILE: \1 -->',re.S)
FIXTURE='cycle_006/source_state/main/tools/redteam/test_rt_claims_hygiene.py'
NAMES={'Researcher040282.Phase.phasor_wrap','Researcher040282.Phase.delayed_input_step','Researcher040282.Phase.delayed_input_chord_bound'}
DEPENDENCIES={'Researcher040282.Delay.historyTrace_index','Researcher040282.Delay.historyTrace_oldest','Researcher040282.Delay.historyTrace_newest'}
LIVE={'STATE.json','CLAIM_LEDGER.csv','README.md','WORKFLOW.md','RESEARCH_QUEUE.md','EVIDENCE_INDEX.json','HISTORICAL_ARCHIVE_LOG_MAP.csv'}

def require(condition,message):
    if not condition:raise RuntimeError(message)


def read(path):return json.loads(path.read_text())


def ledger(path):
    with path.open(newline='') as stream:return list(csv.DictReader(stream))


def blob(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def inspect_contacts(items):
    matches=[]
    for name,data in items:
        count=len(EMAIL.findall(data))
        if not count:continue
        require(name==FIXTURE and count==2,'Unclassified contact pattern (path/count only): '+name+'/'+str(count))
        require(b'GIT_AUTHOR_NAME": "fixture"' in data and b'GIT_COMMITTER_NAME": "fixture"' in data,'Historical fixture context absent')
        record=next(r for r in read(ROOT/'cycle_006/source_state/main_selected.json')['files'] if r['path']=='tools/redteam/test_rt_claims_hygiene.py')
        require(len(data)==record['bytes'] and blob(data)==record['blob'],'Historical synthetic fixture changed')
        matches.append({'path':name,'occurrences':count,'classification':'INTENTIONALLY_SYNTHETIC_PUBLIC_GIT_ENV_FIXTURE_NOT_PERSONAL_COMMIT_METADATA',
                        'source_unmodified_and_acquisition_verified':True,'executed_by_this_cycle':False})
    require(len(matches)==1,'Expected one known synthetic fixture path');return matches



def check_formal(directory):
    p=read(directory/'proof/result.json');main=p['main'];dependency=p['dependency']
    require(p['Mathlib_used'] and p['new_named_declarations_compiled']==3 and p['reused_named_history_declarations_recompiled_not_new_labels']==3 and
            p['formal_controls']==8 and p['positive_controls_accepted']==2 and p['false_math_witnesses_rejected_by_compiler']==3 and
            p['compiling_integrity_payloads_rejected_by_policy']==3 and p['setup_errors_credited']==0 and p['all_preregistered_formal_conditions_met'],'Formal inventory differs')
    for module,policy,names,allowed in (('HistoryBuffer',dependency,DEPENDENCIES,{'propext','Quot.sound'}),
                                        ('PhaseIncrement',main,NAMES,{'propext','Quot.sound','Classical.choice'})):
        require(policy['accepted'] and policy['reasons']==[] and policy['raw_compiler_returncode']==0 and len(policy['named_declarations'])==3 and
                set(policy['footprints'])==set(policy['requested_axiom_prints'])==names and
                all(set(values)==allowed for values in policy['footprints'].values()) and policy['unapproved_axioms']=={},'Main/dependency named proof policy differs')
        require((directory/'proof/compiled_sources'/(module+'.lean')).read_bytes()==(HERE/'proposal'/(module+'.lean')).read_bytes(),'Compiled main/dependency differs')
        log=(directory/'proof/compiler_logs'/(module+'.log')).read_text()
        require(not re.search(r'\b(?:warning|error)\s*:',log,re.I) and 'sorryAx' not in log and log.count('depends on axioms:')==3,'Final main/dependency log not clean')
    records=p['controls'];require(len(records)==len({x['control'] for x in records})==8,'Formal controls duplicate/missing');counts={'positive':0,'false_math':0,'integrity':0}
    for row in records:
        counts[row['kind']]+=1;policy=row['policy'];log=(directory/'proof/compiler_logs'/(row['control']+'.log')).read_text()
        require(row['expected_outcome_observed'] and row['setup_errors_credited']==0 and not re.search(
            r'unknown module|unknown identifier|unknown tactic|object file .* does not exist|failed to import|cannot open shared object|failed to synthesize|maximum.*(?:recursion|heartbeats)|deterministic timeout|unexpected token',log,re.I),'Formal blocker credited')
        if row['kind']=='positive':require(policy['accepted'] and policy['raw_compiler_returncode']==0,'Nonzero positive failed')
        elif row['kind']=='false_math':require(not policy['accepted'] and policy['raw_compiler_returncode']!=0 and re.search('unsolved goals',log,re.I) and re.search(r'⊢\s*False',log),'False witness not explicit mathematical False')
        else:require(not policy['accepted'] and policy['raw_compiler_returncode']==0 and row['expected_mechanism'] in policy['reasons'],'Integrity payload not actually compiled/intended refusal')
    require(counts=={'positive':2,'false_math':3,'integrity':3},'Formal kind counts differ');return p


def decoded(value):return complex(value[0],value[1])
def component(a,b):return max(abs(a.real-b.real),abs(a.imag-b.imag))


def check_workers(directory):
    runs=read(directory/'worker_results.json')
    require(len(runs)==4 and {(x['kind'],x['optimized_python']) for x in runs}=={(k,o) for k in ('common','wrong_models') for o in (False,True)},'Four workers missing/duplicated')
    for row in runs:
        name=row['kind']+('_optimized' if row['optimized_python'] else '_normal');sub=directory/name
        require({k:v for k,v in row.items() if k not in ('elapsed_seconds','observed_returncode')}==read(sub/'result.json') and row['observed_returncode']==0 and
                row['source_files_unchanged']==1 and row['metadata_files_unchanged']==3,'Worker/source/result mismatch')
        design=read(sub/'preexecution_design.json')
        require(design==read(HERE/'preexecution_case_design.json') and design['actual_advances_planned']==56 and design['input_complex_coordinates_planned']==496 and
                design['adjacent_complex_coordinates_planned']==434 and design['startup_adjacent_coordinates_planned']==157 and
                all(x['component_difference']>1e-7 for x in design['ten_fixed_control_witnesses']),'Preimport design changed/vacuous')
        if row['kind']=='wrong_models':
            controls=read(sub/'wrong_models.json')
            require(controls==row['records'] and row['detected']==len(controls)==len({x['model'] for x in controls})==10 and row['actual_engine_advances']==0 and
                    not row['actual_engine_imported'] and row['setup_errors_credited']==0,'Wrong model inventory/source boundary differs')
            require(all(x['detected'] and x['intended_field']==x['detected_field'] and x['component_difference']>1e-7 and x['setup_errors_credited']==0 for x in controls),'Wrong detection mechanism/tiny witness');continue
        require(row['tests_run']==9 and row['failures']==row['errors']==row['skipped']==0 and row['actual_engine_advances']==56 and row['source_initializations']==0 and
                row['source_cases']==7 and row['input_complex_coordinates']==496 and row['adjacent_complex_coordinates']==434 and row['absolute_tolerance']==5e-13 and
                row['relative_tolerance']==0 and row['independent_expected_trace_built_before_import'] and row['explicit_compute_R_calls_by_harness']==0 and
                row['actual_full_engine_import_no_function_copy_replacement_or_edit'] and not row['production_simulation_baseline_CLI_or_certificate_called'] and
                row['immutable_cases_rng_and_history_ownership_verified'],'Common source inventory/scope differs')
        log=(directory/(name+'.log')).read_text();require('Ran 9 tests in ' in log and '\nOK\n' in log,'Actual unittest success absent')
        observations=read(sub/'advance_observations.json');lookup={(x['case'],x['n']):x for x in observations}
        require(len(observations)==len(lookup)==56 and len({x['case'] for x in observations})==7,'Source call observations missing/duplicate')
        input_count=0
        for obs in observations:
            n=obs['N'];require(n in (1,3,4) and obs['D'] in (1,2,3,4) and 0<=obs['n']<8 and
                set(obs['component_errors'])=={'C','B','theta','history','R_physical','R_driver','g_min_pre','g_min','input_innovation'} and
                all(math.isfinite(x) and 0<=x<=5e-13 for x in obs['component_errors'].values()) and obs['independent_expected_trace_before_import'] and
                obs['rng_unchanged'] and obs['independent_history_storage'] and len(obs['theta_before'])==len(obs['theta_after'])==len(obs['row_sums'])==n and
                all(math.isfinite(x) and 0<=x<math.tau for x in obs['theta_after']) and all(math.isfinite(x) and 0<=x<=.6+5e-13 for x in obs['row_sums']),
                'Finite component/range/capacity/storage observation inconsistent')
            matrix=obs['decoded_input_innovation'];require(len(matrix)==n and all(len(r)==n for r in matrix),'Input shape differs')
            require(all(math.isfinite(a) and math.isfinite(b) and abs(abs(complex(a,b))-1)<=5e-13 for r in matrix for a,b in r),'Input not finite/unit within fixed slack');input_count+=n*n
        require(input_count==496 and row['maximum_component_error']==max(x for obs in observations for x in obs['component_errors'].values())==4.440892098500626e-16,'Maximum/input count differs')
        ratios=read(sub/'input_ratio_observations.json');require(len(ratios)==len({(x['case'],x['n'],x['i'],x['j']) for x in ratios})==434,'Adjacent observations missing/duplicate')
        for pair in ratios:
            old=lookup[(pair['case'],pair['n'])];new=lookup[(pair['case'],pair['n']+1)];i=pair['i'];j=pair['j'];v=pair['signed_increment']
            require(0<=pair['n']<7 and 0<=i<old['N'] and 0<=j<old['N'] and pair['startup']==(pair['n']<old['D']),'Ratio age/shape differs')
            z=decoded(old['decoded_input_innovation'][i][j]);zn=decoded(new['decoded_input_innovation'][i][j]);factor=zn/z;want=cmath.exp(1j*v)
            require(decoded(pair['observed_factor'])==factor and decoded(pair['expected_factor'])==want and pair['component_error']==component(want,factor)<=5e-13 and
                    pair['observed_chord']==abs(zn-z)<=abs(v)+5e-13 and pair['signed_increment_bound']==abs(v)<=pair['paper_capacity_bound']+5e-13,'Ratio/chord record arithmetic inconsistent')
        require(sum(x['startup'] for x in ratios)==157 and sum(not x['startup'] for x in ratios)==277 and
                sum(x['n']==lookup[(x['case'],x['n'])]['D'] for x in ratios)==62 and
                row['maximum_ratio_component_error']==max(x['component_error'] for x in ratios)==7.348288644237755e-15 and
                row['age_and_chord_stats']['nonzero_chords_with_bound_below_two']==382 and
                row['winding_stats']['positive_windings']==14 and row['winding_stats']['negative_windings']==9 and row['winding_stats']['multiple_turn_windings']==16 and
                row['winding_stats']['representative_difference_phasor_is_valid_not_a_wrong_model'] and
                row['age_and_chord_stats']['constant_offset_ratio_invariance_is_valid_not_a_wrong_model'],'Age/winding/positive invariance summary differs')
    for kind in ('common','wrong_models'):
        pair=[{k:v for k,v in row.items() if k not in ('elapsed_seconds','optimized_python')} for row in runs if row['kind']==kind]
        require(pair[0]==pair[1],'Normal/-O non-timing difference')
    return [{k:v for k,v in row.items() if k!='elapsed_seconds'} for row in runs]


def preflight():
    state=read(ROOT/'STATE.json')
    require(state['current_cycle']==11 and state['current_status']=='COMPLETED_LOCAL_MODULO_PHASE_INCREMENT_AND_CHORD_BOUND_UNREVIEWED' and
            state['in_progress'] is None and state['next_cycle']==12 and state['research_processes_running']==[] and not (ROOT/'cycle_012').exists(),
            'Completion/resumption boundary differs')
    require(state['last_updated_date']=='2026-09-04' and not any(state[k] for k in ('current_cycle_independent_review_received',
            'latest_packet_owner_upload_confirmed','remote_changes_by_this_agent','contacted_other_bots','automatic_work_between_turns')),'Date/review/remote/upload overclaim')
    boundary=state['authority_boundary'];require(boundary['new_unregistered_library_candidate_and_finite_specification_only'] and
        boundary['actual_frozen_engine_read_only_import_and_synthetic_primitives'] and not any(boundary[k] for k in (
        'frozen_source_edited','lock_or_registry_changed','source_cache_edited','new_helper_or_module_installed','authority_validation_run',
        'full_equivalence_pipeline_run','run_seed_simulate_production_CLI_or_writer_called')),'Authority/source boundary differs')
    require(not Path('/home/user/audit').exists() and Path('/home/user/aief_audit').is_dir() and Path('/home/user/aiefs_repository_audit').is_dir(),'Lua deletion/AIEFS preservation boundary differs')
    current=ledger(ROOT/'CLAIM_LEDGER.csv');prior=ledger(HERE/'previous010_snapshot/CLAIM_LEDGER.csv')
    require(len(current)==len({x['claim_id'] for x in current})==122 and len(prior)==118 and current[:118]==prior and
            sum(x['evidence_label']=='LEAN_COMPILED' for x in prior)==97 and sum(x['evidence_label']=='LEAN_COMPILED' for x in current)==100 and
            [x['evidence_label'] for x in current[118:]]==['LEAN_COMPILED']*3+['EXECUTABLE_REGRESSION_CHECK'] and
            all(x['cycle']=='11' for x in current[118:]),'Prior118 preservation/new label scope differs')
    for count,path in ((114,'cycle_010/previous009_snapshot/CLAIM_LEDGER.csv'),(113,'cycle_009/previous008_snapshot/CLAIM_LEDGER.csv'),
                       (112,'cycle_008/previous007_snapshot/CLAIM_LEDGER.csv'),(111,'cycle_007/previous006_snapshot/CLAIM_LEDGER.csv'),(109,'cycle_006/previous005_snapshot/CLAIM_LEDGER.csv')):
        old=ledger(ROOT/path);require(len(old)==count and prior[:count]==old,'Older ledger changed')
    old004=ledger(ROOT/'cycle_005/completed_004_snapshot/CLAIM_LEDGER_COMPLETED_004.csv');old005=ledger(ROOT/'cycle_006/previous005_snapshot/CLAIM_LEDGER.csv')
    require(len(old004)==108 and [x for x in old005 if x['cycle']!='5']==old004,'Completed004 scope changed')
    original=read(HERE/'checks/cycle_results.json');repeated=read(HERE/'standalone/checks/cycle_results.json');science=original['science']
    require(science==repeated['science'] and science['all_preregistered_acceptance_conditions_met'] and science['source_contract_methods_each_mode']==science['source_passes_each_mode']==9 and
            science['actual_advances_each_common_mode']==56 and science['initializer_calls_each_common_mode']==0 and science['wrong_models_detected_each_mode']==10 and
            science['new_named_Lean_declarations_actually_compiled']==3 and science['formal_controls']==8 and science['setup_errors_credited_as_detections']==0,'Scientific summary incomplete')
    require(check_workers(HERE/'checks')==check_workers(HERE/'standalone/checks'),'Original/extracted workers differ')
    require(check_formal(HERE/'checks')==check_formal(HERE/'standalone/checks'),'Original/extracted formal records differ')
    receipt=read(HERE/'standalone_reproduction.json')
    require(receipt['actually_executed'] and receipt['runner_returncode']==0 and receipt['critical_file_count']==13 and receipt['fresh_public_dependencies_fetched_and_verified']==4 and
            receipt['same_original_verified_compiler_and_Mathlib_reused'] and not receipt['fresh_clean_compiler_or_Mathlib_installation_claimed'] and
            receipt['all_four_worker_nontiming_results_match_original'] and receipt['all_thirtyone_detailed_records_byte_identical'] and len(receipt['detailed_matching_files'])==31,'Reproduction receipt overstates')
    for name in receipt['detailed_matching_files']:require((HERE/'checks'/name).read_bytes()==(HERE/'standalone/checks'/name).read_bytes(),'Detailed repeat changed')
    fetched=read(HERE/'standalone/fetch_receipt.json');require(fetched['public_dependencies_fetched_and_verified']==4 and fetched['metadata_files']==3 and
            all(x['freshly_fetched'] and x['verified'] for x in fetched['files']),'Four fresh dependency fetches unobserved')
    report=builder.REPORT.read_text();pairs=BLOCK.findall(report)
    require(len(pairs)==13 and {name for name,_ in pairs}==set(builder.CRITICAL) and 'PROVISIONAL: extracted-code rerun not executed yet' not in report and
            not re.search(r'\{\{[A-Z_]+\}\}',report) and '122 unique rows / 100 LEAN_COMPILED labels' in report and 'not a universal guarantee' in report and
            'no post-result tolerance tuning' in report and 'Two legitimate invariances' in report and 'constant' in report,'Final report stale/provisional/caveat absent')
    for name,body in pairs:
        require((body+'\n').encode()==(HERE/'proposal'/name).read_bytes()==(HERE/'standalone/extracted'/name).read_bytes(),'Inline !=executed extracted code: '+name)
        if name.endswith('.py'):require(not any(isinstance(n,ast.Assert) for n in ast.walk(ast.parse(body))),'Critical code uses -O-removable assert')
    require((HERE/'proposal/HistoryBuffer.lean').read_bytes()==(ROOT/'cycle_010/proposal/HistoryBuffer.lean').read_bytes() and
            (HERE/'proposal/step_contract.py').read_bytes()==(ROOT/'cycle_010/proposal/step_contract.py').read_bytes(),'Reused010 dependency silently edited')
    acquired={}
    for branch,count in (('main',32),('inbox',8)):
        m=read(HERE/'source_state'/(branch+'_selected.json'));require(len(m['files'])==m['fetched_and_verified']==count,'Acquisition count differs')
        for row in m['files']:
            data=(HERE/'source_state'/branch/row['path']).read_bytes();require(len(data)==row['bytes'] and blob(data)==row['blob'],'Acquired text changed')
        acquired[branch]=count
    manifest=read(HERE/'proposal/source_modules.json');require(len(manifest['modules'])==1 and len(manifest['metadata'])==3,'Reviewed4-file closure differs')
    for row in manifest['modules']+manifest['metadata']:
        for directory in (HERE/'source_state/main',HERE/'standalone/upstream'):
            data=(directory/row['path']).read_bytes();require(len(data)==row['bytes'] and blob(data)==row['blob'],'Original/fresh dependency changed')
    require(not list((HERE/'source_state/inbox').rglob('*trust-anchor-regression.py')),'New contributed reproducer acquired unexpectedly')
    setup=read(HERE/'compiler_setup.json');ml=read(HERE/'mathlib_setup.json');cleanup=read(HERE/'compiler_cleanup.json')
    require(setup['public_asset_verified'] and setup['download_bytes']==manifest['lean_toolchain']['bytes']==570405234 and
            setup['complete_runtime_extracted_members']==18130 and setup['complete_runtime_extracted_bytes']==3037354159 and
            not setup['global_toolchain_changed'] and ml['mathlib_revision']==manifest['mathlib']['revision'] and ml['cache_helper_returncode']==0 and
            ml['owned_regular_file_logical_bytes']<=12*1024**3 and setup['elapsed_seconds']+ml['elapsed_seconds']<900 and
            cleanup['actually_removed_after_successful_full_reproduction'] and cleanup['cache_absent_after_removal'] and not Path(cleanup['own_cache']).exists() and
            cleanup['only_cycle011_owned_runtime_archive_decoder_Git_Mathlib_target_removed'] and cleanup['regular_file_logical_bytes_removed']>setup['download_bytes'] and
            isinstance(cleanup['symlinks_removed'],int) and cleanup['measured_before_removal'],'Resource/cleanup receipt differs')
    require('HTTP Error 403' in (HERE/'development/source_refresh_api403.log').read_text() and
            'sorryAx' in (HERE/'development/phase_pilot_01/PhaseIncrement.log').read_text() and
            'warning:' in (HERE/'development/phase_pilot_03/PhaseIncrement.log').read_text() and
            read(HERE/'development/first_full_runner_control_blocker/checks/failure.json')['semantic_negative_detection_credited'] is False and
            all(x['observed_returncode']==0 for x in read(HERE/'development/first_full_runner_control_blocker/checks/worker_results.json')),
            'Retained transport/proof/control blockers missing or miscredited')
    branches=[p for p in ROOT.rglob('*_branch*.json') if 'source_state' in p.parts];require(len(branches)==20,'Expected20minimal branch records')
    for p in branches:
        v=read(p);require(set(v)=={'branch','commit','metadata_policy'} and all(isinstance(x,str) for x in v.values()),'Nonminimal branch metadata')
    contacts=inspect_contacts((str(p.relative_to(ROOT)),p.read_bytes()) for p in builder.selected_files())
    privacy={'all_twenty_branch_records_structurally_minimal':True,'new011_metadata_minimal_at_creation':True,
             'personal_commit_contacts_or_signed_payloads_in_branch_metadata':0,'raw_Git_objects_not_copied_and_own_cache_removed':True,
             'unclassified_outgoing_email_pattern_matches':0,'new_contributed_reproducer_not_acquired_or_executed':True,
             'historical_synthetic_fixture_matches':contacts,'known009_static_encoded_source_inspection_preserved':'cycle_009/incoming_static_privacy.json',
             'printed_contact_values':False,'scope':'Owned packet structural minimization/scoped pattern scan, not exhaustive secrets/security certification'}
    (HERE/'privacy_results.json').write_text(json.dumps(privacy,indent=2)+'\n');preserved=0
    with zipfile.ZipFile(ROOT/'researcher040282-cycle010-history-phase-contract.zip') as z:
        for member in z.namelist():
            name=member.removeprefix('researcher_040282/')
            if name not in LIVE:require((ROOT/name).is_file() and (ROOT/name).read_bytes()==z.read(member),'Prior010 nonlive evidence changed: '+name);preserved+=1
        for name in ('STATE.json','CLAIM_LEDGER.csv'):require((HERE/'previous010_snapshot'/name).read_bytes()==z.read('researcher_040282/'+name),'Completed010 snapshot differs')
    restoration=read(HERE/'historical_restoration.json');require(restoration['nonlive_members_checked']==1243 and restoration['missing_only_restored']==1 and
        restoration['missing_before_administrative_recovery']==[{'path':'cycle_006/source_state/main/.github/workflows/repo-checks.yml','bytes':9175}] and
        restoration['all_recovered_bytes_equal_delivered_members'] and not restoration['existing_files_overwritten'] and not restoration['historical_science_rerun'] and
        not restoration['scientific011_inputs_code_results_changed'] and not restoration['legacy_deleted_Lua_restored'] and restoration['user_deleted_legacy_Lua_absent'],'Missing-only historical recovery differs')
    protected=['2026-09-04_researcher040282_004_complex-ema.md']+['cycle_004/'+x for x in ('GateFoundations.lean','FreezeCore.lean','GateProposalBridge.lean','CoherenceEMA.lean','CoherenceDriveBridge.lean','check_cycle.py','compare_source.py')]
    with zipfile.ZipFile(ROOT/'researcher040282-cycle004-complex-ema.zip') as z:
        for name in protected:require((ROOT/name).read_bytes()==z.read('researcher_040282/'+name),'Protected004 file changed')
    for name in ('README.md','WORKFLOW.md','RESEARCH_QUEUE.md'):
        text=(ROOT/name).read_text();require('011' in text and '012' in text,'Root navigation stale')
    index=read(ROOT/'EVIDENCE_INDEX.json');require(index['ledger_rows']==122 and index['archive_only_ledger_references']==0,'Evidence index stale')
    for row in index['ledger_evidence']:
        require(row['availability']=='UNPACKED' and row['packet_members'],'Ledger evidence archive-only')
        for member in row['packet_members']:require((ROOT.parent/member).is_file(),'Unpacked cited member missing')
    return {'current_ledger_rows':122,'prior118_rows_preserved':True,'formal_labels_prior97_plus3':100,'original_and_extracted_full_runner_success':True,
            'source_passes_each_mode':9,'actual_advances_each_mode':56,'source_initializers_each_mode':0,'input_complex_coordinates_each_mode':496,
            'adjacent_complex_coordinates_each_mode':434,'startup_coordinates_each_mode':157,'first_live_coordinates_each_mode':62,
            'maximum_component_error':4.440892098500626e-16,'maximum_ratio_component_error':7.348288644237755e-15,'wrong_models_detected_each_mode':10,
            'new_named_Lean_claims':3,'reused_history_not_new_labels':3,'formal_controls':8,'setup_errors_credited':0,
            'four_workers_and_thirtyone_details_match_reproduction':True,'critical_inline_files_equal_executed_extracted_sources':13,
            'verified_acquisition_files_unchanged':acquired,'public_engine_unchanged':1,'scope_compiler_metadata_unchanged':3,
            'source_functions_not_copied_replaced_or_edited':True,'exact_real_not_full_Python_float_coupled_map_theorem':True,
            'new_module_spec_not_installed_or_independently_reviewed':True,'no_production_study_authority_certificate_or_remote_write':True,
            'own_runtime_Git_Mathlib_decoder_archive_removed_after_full_reproduction':True,'retained_draft_transport_control_blockers_not_detections':True,
            'prior010_nonlive_evidence_files_preserved':preserved,'completed010_state_ledger_snapshots_match_delivery':True,'protected004_critical_files':len(protected),
            'one_missing_old_CI_source_restored_exactly_no_science_rerun':True,'deleted_legacy_Lua_audit_remains_absent':True,
            'all_twenty_branch_records_minimal':True,'unclassified_email_pattern_matches':0,'historical_intentionally_synthetic_fixture_addresses_distinguished':2,
            'all_ledger_evidence_unpacked':True,'ledger_reference_count':index['unique_ledger_references'],'unpacked_log_count':index['unpacked_log_count'],
            'scope':'Owned consistency/privacy/preservation arithmetic recheck, no source/compiler science rerun, independent review/authority/integration/security certification'}

def verify_archive():
    expected={'researcher_040282/'+str(path.relative_to(ROOT)):path for path in builder.selected_files()}
    with zipfile.ZipFile(builder.ARCHIVE) as archive:
        names=archive.namelist();require(archive.testzip() is None and len(names)==len(set(names)),'ZIP CRC/duplicate member failure')
        require(set(names)==set(expected),'ZIP/workspace selected membership differs');contents=[]
        for name,path in expected.items():
            data=archive.read(name);require(data==path.read_bytes(),'ZIP selected content differs: '+name)
            contents.append((name.removeprefix('researcher_040282/'),data))
        inspect_contacts(contents)
    return len(expected)


def main():
    builder.build_report();builder.build_indices();result=preflight();builder.package();verify_archive()
    result.update({'zip_crc_verified':True,'all_members_match_selected_workspace_files':True,
                   'receipt_included_and_final_archive_reverified':True})
    (HERE/'packet_validation.json').write_text(json.dumps(result,indent=2)+'\n');builder.package();verify_archive()
    state=read(ROOT/'STATE.json');state['handoff_status']='LOCAL_PACKET_CLOSURE_VERIFIED;NOT_UPLOADED'
    (ROOT/'STATE.json').write_text(json.dumps(state,indent=2)+'\n');builder.package()
    try:members=verify_archive();preflight();verify_archive()
    except Exception:
        state['handoff_status']='PACKET_CLOSURE_RECHECK_FAILED;DO_NOT_DELIVER';(ROOT/'STATE.json').write_text(json.dumps(state,indent=2)+'\n');raise
    print(json.dumps({'validation':result,'final_archive_members':members,'final_archive_bytes':builder.ARCHIVE.stat().st_size,
                      'standalone_report_bytes':builder.REPORT.stat().st_size},indent=2))


if __name__=='__main__':main()
