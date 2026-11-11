"""Owned012 packet/preservation/privacy closure, no source/proof science rerun.
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
NAMES={'Researcher040282.Tracking.tracking_error_step','Researcher040282.Tracking.tracking_error_budget','Researcher040282.Tracking.delayed_phase_tracking_budget'}
DEPENDENCY_COUNTS={'HistoryBuffer':3,'PhaseIncrement':3,'CoherenceEMA':22}
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
    p=read(directory/'proof/result.json');main=p['main']
    require(p['Mathlib_used'] and p['new_named_declarations_compiled']==3 and p['reused_named_declarations_recompiled_not_new_labels']==28 and
        p['formal_controls']==8 and p['positive_controls_accepted']==2 and p['false_math_witnesses_rejected_by_compiler']==3 and p['compiling_integrity_payloads_rejected_by_policy']==3 and
        p['setup_errors_credited']==0 and p['all_preregistered_formal_conditions_met'],'Formal inventory incomplete')
    require(main['accepted'] and main['reasons']==[] and main['raw_compiler_returncode']==0 and len(main['named_declarations'])==3 and
        set(main['footprints'])==set(main['requested_axiom_prints'])==NAMES and all(set(v)=={'propext','Classical.choice','Quot.sound'} for v in main['footprints'].values()),'Main footprint/name coverage differs')
    require({x['module']:x['reused_named_claims_not_new_labels'] for x in p['dependencies']}==DEPENDENCY_COUNTS,'Dependency counts/labels differ')
    policies=[('EMATracking',main,3)]+[(x['module'],x['policy'],x['reused_named_claims_not_new_labels']) for x in p['dependencies']]
    for module,policy,count in policies:
        source=(HERE/'proposal'/(module+'.lean')).read_text();names=set(re.findall(r'^#print axioms ([\w.]+)',source,re.M))
        require(policy['accepted'] and policy['reasons']==[] and policy['raw_compiler_returncode']==0 and len(policy['named_declarations'])==count and
            len(names)==count and set(policy['footprints'])==set(policy['requested_axiom_prints'])==names and policy['unapproved_axioms']=={} and
            all(set(x)<={'propext','Classical.choice','Quot.sound'} for x in policy['footprints'].values()),'Dependency/main footprint policy differs')
        require((directory/'proof/compiled_sources'/(module+'.lean')).read_bytes()==(HERE/'proposal'/(module+'.lean')).read_bytes(),'Compiled source differs')
        log=(directory/'proof/compiler_logs'/(module+'.log')).read_text()
        require(not re.search(r'\b(?:warning|error)\s*:',log,re.I) and 'sorryAx' not in log and log.count('depends on axioms:')==count,'Main/dependency compiler log not clean/complete')
    rows=p['controls'];require(len(rows)==len({x['control'] for x in rows})==8,'Formal controls missing/duplicate');counts={'positive':0,'false_math':0,'integrity':0}
    for row in rows:
        counts[row['kind']]+=1;policy=row['policy'];log=(directory/'proof/compiler_logs'/(row['control']+'.log')).read_text()
        require(row['expected_outcome_observed'] and row['setup_errors_credited']==0 and not re.search(r'unknown module|unknown identifier|unknown constant|unknown tactic|object file .* does not exist|failed to import|cannot open shared object|failed to synthesize|maximum.*(?:recursion|heartbeats)|deterministic timeout|unexpected token',log,re.I),'Setup/identifier failure credited')
        if row['kind']=='positive':require(policy['accepted'] and policy['raw_compiler_returncode']==0,'Endpoint positive failed')
        elif row['kind']=='false_math':require(not policy['accepted'] and policy['raw_compiler_returncode']!=0 and re.search('unsolved goals',log,re.I) and re.search(r'⊢\s*False',log),'False math did not explicitly reduce to False')
        else:require(not policy['accepted'] and policy['raw_compiler_returncode']==0 and row['expected_mechanism'] in policy['reasons'],'Compiling integrity payload wrong refusal')
    require(counts=={'positive':2,'false_math':3,'integrity':3},'Formal kinds differ');return p


def decoded(value):return complex(value[0],value[1])
def component(a,b):return max(abs(a.real-b.real),abs(a.imag-b.imag))


def check_workers(directory):
    workers=read(directory/'worker_results.json');require(len(workers)==4 and {(x['kind'],x['optimized_python']) for x in workers}=={(k,o) for k in ('common','wrong_models') for o in (False,True)},'Four-worker inventory differs')
    for row in workers:
        name=row['kind']+('_optimized' if row['optimized_python'] else '_normal');sub=directory/name
        require({k:v for k,v in row.items() if k not in ('elapsed_seconds','observed_returncode')}==read(sub/'result.json') and row['observed_returncode']==0 and row['source_files_unchanged']==1 and row['metadata_files_unchanged']==3,'Worker/child/dependency mismatch')
        design=read(sub/'preexecution_design.json');require(design==read(HERE/'preexecution_case_design.json') and len(design['cases'])==6 and
            all(x['intended_witness']>1e-7 for x in design['ten_wrong_models']),'Design changed/vacuous')
        if row['kind']=='wrong_models':
            controls=read(sub/'wrong_models.json');require(controls==row['records'] and row['detected']==len(controls)==len({x['model'] for x in controls})==10 and
                row['actual_engine_advances']==0 and not row['actual_engine_imported'] and row['setup_errors_credited']==0,'Wrong-model count/boundary differs')
            require(all(x['detected'] and x['intended_field']==x['detected_field'] and x['numeric_witness']>1e-7 and x['setup_errors_credited']==0 for x in controls),'Wrong mechanism/tolerance witness')
            require(sum(x['kind']=='upper_bound' for x in controls)==4,'Expected4actual false-upper-bound witnesses');continue
        stats=row['tracking_stats']
        require(row['tests_run']==9 and row['failures']==row['errors']==row['skipped']==0 and row['actual_engine_advances']==60 and row['source_initializations']==0 and
            row['source_cases']==6 and row['precomputed_tracking_cells']==370 and row['absolute_tolerance']==5e-13 and row['relative_tolerance']==0 and
            row['all_expected_traces_and_derived_budgets_before_import'] and row['explicit_compute_R_calls_by_harness']==0 and row['actual_full_engine_import_no_function_copy_replacement_or_edit'] and
            not row['production_simulation_baseline_CLI_or_certificate_called'] and row['immutable_inputs_expected_tables_rng_and_history_ownership_verified'] and
            row['alpha1_not_decoded_or_assumed_strictly_less_than_one'],'Common scope/inventory differs')
        log=(directory/(name+'.log')).read_text();require('Ran 9 tests in ' in log and '\nOK\n' in log,'Actual unittest success missing')
        observations=read(sub/'advance_observations.json');lookup={(x['case'],x['n']):x for x in observations}
        require(len(observations)==len(lookup)==60 and len({x['case'] for x in observations})==6,'Source call records missing/duplicate');decoded_count=endpoint_count=diag=off=0
        for obs in observations:
            n=obs['N'];a=obs['alpha'];require(n in (1,3,4) and obs['D'] in (1,2,3,4) and 0<=obs['n']<10 and math.isfinite(a) and 0<a<=1 and
                all(math.isfinite(x) and 0<=x<=5e-13 for x in obs['component_errors'].values()) and obs['all_expectations_before_import'] and obs['rng_unchanged'] and obs['independent_history_storage'] and
                len(obs['theta_before'])==len(obs['theta_after'])==len(obs['row_sums'])==n and all(math.isfinite(x) and 0<=x<math.tau for x in obs['theta_after']) and
                all(math.isfinite(x) and 0<=x<=.6+5e-13 for x in obs['row_sums']),'Source finite/structure/post-row record inconsistent')
            for key in ('C_before','C_after','input_from_observed_arguments'):
                matrix=obs[key];require(len(matrix)==n and all(len(r)==n for r in matrix) and all(math.isfinite(x) and math.isfinite(y) for r in matrix for x,y in r),'Complex shape/finite record invalid')
            z=obs['input_from_observed_arguments'];require(all(abs(abs(decoded(v))-1)<=5e-13 for r in z for v in r),'Input not unit within fixed tolerance')
            if a==1:
                require(obs['decoded_C_innovation'] is None and obs['input_channel']=='formula_only_beta0_unidentifiable_in_C' and obs['C_before']==obs['C_after'],'Alpha1 falsely decoded/changed C');endpoint_count+=n*n
            else:
                require(1-a>=.05 and obs['input_channel']=='formula_and_actual_C_innovation' and obs['decoded_C_innovation'] is not None,'Bad decoder conditioning/channel');decoded_count+=n*n
                for i in range(n):
                    for j in range(n):require(component(decoded(obs['decoded_C_innovation'][i][j]),decoded(z[i][j]))<=5e-13,'Decoded innovation mismatch')
            for i in range(n):
                for j in range(n):
                    physical=obs['R_physical'][i][j]
                    if i==j:require(physical==0,'Physical diagonal not0');diag+=1
                    else:
                        expected=(abs(decoded(obs['C_after'][i][j]))+abs(decoded(obs['C_after'][j][i])))/2
                        require(math.isfinite(physical) and abs(physical-expected)<=5e-13,'Physical R not after C');off+=1
        require((decoded_count,endpoint_count,off,diag)==(360,10,240,130) and row['maximum_component_error']==max(v for x in observations for v in x['component_errors'].values())==9.992007221626409e-16,'Input/R/max counts differ')
        records=read(sub/'tracking_observations.json');cells={(x['case'],x['n'],x['i'],x['j']):x for x in records};require(len(records)==len(cells)==370,'Tracking cells missing/duplicate');causal=0
        for cell in records:
            case=cell['case'];n=cell['n'];i=cell['i'];j=cell['j'];obs=lookup[(case,n)];a=obs['alpha'];z=decoded(obs['input_from_observed_arguments'][i][j]);got=decoded(obs['C_before'][i][j])-z
            initial=lookup[(case,0)];e0=decoded(initial['C_before'][i][j])-decoded(initial['input_from_observed_arguments'][i][j])
            differences=[decoded(lookup[(case,k+1)]['input_from_observed_arguments'][i][j])-decoded(lookup[(case,k)]['input_from_observed_arguments'][i][j]) for k in range(n)]
            unroll=a**n*e0-sum(a**(n-1-k)*differences[k] for k in range(n));bound=a**n*abs(e0)+sum(a**(n-1-k)*abs(differences[k]) for k in range(n))
            require(decoded(cell['observed_current_error'])==got and component(decoded(cell['expected_current_error']),got)<=5e-13 and component(decoded(cell['expected_complex_unroll']),got)<=5e-13 and
                component(unroll,got)<=5e-13 and cell['observed_error_norm']==abs(got)<=cell['input_variation_budget']+5e-13 and abs(bound-cell['input_variation_budget'])<=5e-13 and
                math.isfinite(cell['phase_increment_budget']) and cell['input_variation_budget']<=cell['phase_increment_budget']+5e-13 and 0<=cell['unroll_component_error']<=5e-13,'Tracking budget/unroll arithmetic invalid')
            consumed=decoded(obs['C_after'][i][j])-z;require(decoded(cell['consumed_input_error'])==consumed and component(a*got,consumed)<=5e-13 and component(decoded(cell['expected_consumed_error']),consumed)<=5e-13,'Consumed-input error invalid')
            bji=cells[(case,n,j,i)]['phase_increment_budget'];require(cell['reported_R_bound']==a*(cell['phase_increment_budget']+bji)/2,'Reported R envelope coefficient invalid')
            if i!=j:require(abs(obs['R_physical'][i][j]-1)<=cell['reported_R_bound']+5e-13,'Reported R envelope violated')
            if n:
                old=lookup[(case,n-1)];oldz=decoded(old['input_from_observed_arguments'][i][j]);olde=decoded(old['C_before'][i][j])-oldz
                require(component(a*olde-(z-oldz),got)<=5e-13 and cell['causal_residual_from_previous'] is not None and 0<=cell['causal_residual_from_previous']<=5e-13,'Causal relation inconsistent');causal+=1
            else:require(cell['causal_residual_from_previous'] is None,'Invented previous recurrence')
        require(causal==333 and stats['adjacent_causal_coordinates']==333 and stats['tracking_coordinates']==stats['consumed_input_coordinates']==370 and
            stats['startup_adjacent_coordinates']==115 and stats['live_adjacent_coordinates']==218 and stats['first_live_coordinates']==37 and stats['nonzero_tracking_bounds_below_two']==245 and
            stats['tight_nonzero_reported_R_bounds_below_one']==12 and stats['alpha1_C_exactly_constant'] and stats['alpha1_not_strict_contraction'] and stats['beta0_divisions']==0 and
            stats['source_alpha0_configs']==0 and stats['rounded_alpha1_tail_error']==.8062257748298549,'Causal/channel/tail summary differs')
    for kind in ('common','wrong_models'):
        pair=[{k:v for k,v in x.items() if k not in ('elapsed_seconds','optimized_python')} for x in workers if x['kind']==kind];require(pair[0]==pair[1],'Normal/-O non-timing mismatch')
    return [{k:v for k,v in x.items() if k!='elapsed_seconds'} for x in workers]


def preflight():
    state=read(ROOT/'STATE.json')
    require(state['current_cycle']==12 and state['current_status']=='COMPLETED_LOCAL_CAUSAL_EMA_TRACKING_AND_PHASE_COMPOSITION_UNREVIEWED' and
        state['in_progress'] is None and state['next_cycle']==13 and state['research_processes_running']==[] and not (ROOT/'cycle_013').exists(),'Completed/next-cycle boundary differs')
    require(state['last_updated_date']=='2026-09-04' and not any(state[k] for k in ('current_cycle_independent_review_received','latest_packet_owner_upload_confirmed','remote_changes_by_this_agent','contacted_other_bots','automatic_work_between_turns')),'Date/review/remote overclaim')
    boundary=state['authority_boundary'];require(boundary['new_unregistered_library_candidate_and_finite_specification_only'] and boundary['actual_frozen_engine_read_only_import_and_synthetic_primitives'] and
        not any(boundary[k] for k in ('frozen_source_edited','lock_or_registry_changed','source_cache_edited','new_helper_or_module_installed','authority_validation_run','full_equivalence_pipeline_run','run_seed_simulate_production_CLI_or_writer_called')),'Authority boundary changed')
    require(not Path('/home/user/audit').exists() and Path('/home/user/aief_audit').is_dir() and Path('/home/user/aiefs_repository_audit').is_dir(),'Deleted Lua/retained AIEFS boundary differs')
    current=ledger(ROOT/'CLAIM_LEDGER.csv');prior=ledger(HERE/'previous011_snapshot/CLAIM_LEDGER.csv')
    require(len(current)==len({x['claim_id'] for x in current})==126 and len(prior)==122 and current[:122]==prior and sum(x['evidence_label']=='LEAN_COMPILED' for x in prior)==100 and
        sum(x['evidence_label']=='LEAN_COMPILED' for x in current)==103 and [x['evidence_label'] for x in current[122:]]==['LEAN_COMPILED']*3+['EXECUTABLE_REGRESSION_CHECK'] and all(x['cycle']=='12' for x in current[122:]),'Prior122/100 preservation/new row scope differs')
    for count,path in ((118,'cycle_011/previous010_snapshot/CLAIM_LEDGER.csv'),(114,'cycle_010/previous009_snapshot/CLAIM_LEDGER.csv'),(113,'cycle_009/previous008_snapshot/CLAIM_LEDGER.csv'),(112,'cycle_008/previous007_snapshot/CLAIM_LEDGER.csv'),(111,'cycle_007/previous006_snapshot/CLAIM_LEDGER.csv'),(109,'cycle_006/previous005_snapshot/CLAIM_LEDGER.csv')):
        old=ledger(ROOT/path);require(len(old)==count and prior[:count]==old,'Older ledger scope changed')
    old004=ledger(ROOT/'cycle_005/completed_004_snapshot/CLAIM_LEDGER_COMPLETED_004.csv');old005=ledger(ROOT/'cycle_006/previous005_snapshot/CLAIM_LEDGER.csv')
    require(len(old004)==108 and [x for x in old005 if x['cycle']!='5']==old004,'Completed004 scope changed')
    original=read(HERE/'checks/cycle_results.json');repeated=read(HERE/'standalone/checks/cycle_results.json');science=original['science']
    require(science==repeated['science'] and science['all_preregistered_acceptance_conditions_met'] and science['source_contract_methods_each_mode']==science['source_passes_each_mode']==9 and
        science['actual_advances_each_common_mode']==60 and science['initializer_calls_each_common_mode']==0 and science['wrong_models_detected_each_mode']==10 and
        science['new_named_Lean_declarations_actually_compiled']==3 and science['reused_named_declarations_recompiled_not_new_labels']==28 and science['formal_controls']==8 and
        science['setup_errors_credited_as_detections']==0 and science['alpha1_no_division_or_strict_contraction_assumption'],'Science incomplete/overclaimed')
    require(check_workers(HERE/'checks')==check_workers(HERE/'standalone/checks'),'Original/extracted workers differ')
    require(check_formal(HERE/'checks')==check_formal(HERE/'standalone/checks'),'Original/extracted formal records differ')
    receipt=read(HERE/'standalone_reproduction.json');require(receipt['actually_executed'] and receipt['runner_returncode']==0 and receipt['critical_file_count']==16 and
        receipt['fresh_public_dependencies_fetched_and_verified']==4 and receipt['same_original_verified_compiler_and_Mathlib_reused'] and not receipt['fresh_clean_compiler_or_Mathlib_installation_claimed'] and
        receipt['all_four_worker_nontiming_results_match_original'] and receipt['all_thirtyfive_detailed_records_byte_identical'] and len(receipt['detailed_matching_files'])==35,'Repeat receipt incomplete')
    for name in receipt['detailed_matching_files']:require((HERE/'checks'/name).read_bytes()==(HERE/'standalone/checks'/name).read_bytes(),'Detailed byte match changed')
    fetched=read(HERE/'standalone/fetch_receipt.json');require(fetched['public_dependencies_fetched_and_verified']==4 and fetched['metadata_files']==3 and all(x['freshly_fetched'] and x['verified'] for x in fetched['files']),'Four fresh public deps unobserved')
    report=builder.REPORT.read_text();pairs=BLOCK.findall(report);require(len(pairs)==16 and {x for x,_ in pairs}==set(builder.CRITICAL) and
        'PROVISIONAL: extracted-code rerun not executed yet' not in report and not re.search(r'\{\{[A-Z_]+\}\}',report) and '126 unique rows / 103 LEAN_COMPILED labels' in report and
        'no post-target tolerance' in report and 'Numbered011clarification' in report and 'NOT called decoded' in report and 'No013work started' in report,
        'Report provisional/inline/caveat mismatch')
    for name,body in pairs:
        require((body+'\n').encode()==(HERE/'proposal'/name).read_bytes()==(HERE/'standalone/extracted'/name).read_bytes(),'Final inline !=executed extracted code: '+name)
        if name.endswith('.py'):require(not any(isinstance(x,ast.Assert) for x in ast.walk(ast.parse(body))),'Critical code has -O-removable assert')
    for name,old in (('HistoryBuffer.lean','cycle_011/proposal/HistoryBuffer.lean'),('PhaseIncrement.lean','cycle_011/proposal/PhaseIncrement.lean'),('CoherenceEMA.lean','cycle_004/CoherenceEMA.lean'),('step_contract.py','cycle_011/proposal/step_contract.py'),('phase_contract.py','cycle_011/proposal/phase_contract.py')):
        require((HERE/'proposal'/name).read_bytes()==(ROOT/old).read_bytes(),'Reused dependency edited: '+name)
    acquired={}
    for branch,count in (('main',42),('inbox',12)):
        record=read(HERE/'source_state'/(branch+'_selected.json'));require(len(record['files'])==record['fetched_and_verified']==count,'Retained acquisition count differs')
        for x in record['files']:
            data=(HERE/'source_state'/branch/x['path']).read_bytes();require(len(data)==x['bytes'] and blob(data)==x['blob'],'Acquired retained text changed')
        acquired[branch]=count
    manifest=read(HERE/'proposal/source_modules.json');require(len(manifest['modules'])==1 and len(manifest['metadata'])==3,'Four-file reviewed source closure differs')
    for x in manifest['modules']+manifest['metadata']:
        for directory in (HERE/'source_state/main',HERE/'standalone/upstream'):
            data=(directory/x['path']).read_bytes();require(len(data)==x['bytes'] and blob(data)==x['blob'],'Original/fresh public dependency changed')
    selected=read(HERE/'source_state/inbox_selected.json')['files'];require(not any(x['path'].endswith(('.py','CHANGES_2026-10-28_pii_email.md')) for x in selected),'Contributed script/irrelevant PII text included')
    refine=read(HERE/'selection_refinement.json');require(refine['irrelevant_salvage_PII_note_not_used_as_evidence'] and refine['email_pattern_count_only']==1 and not refine['personal_values_printed'] and not refine['source_executed'],'Selection/privacy refinement differs')
    setup=read(HERE/'compiler_setup.json');ml=read(HERE/'mathlib_setup.json');cleanup=read(HERE/'compiler_cleanup.json')
    require(setup['public_asset_verified'] and setup['download_bytes']==manifest['lean_toolchain']['bytes']==570405234 and setup['complete_runtime_extracted_members']==18130 and
        setup['complete_runtime_extracted_bytes']==3037354159 and not setup['global_toolchain_changed'] and ml['mathlib_revision']==manifest['mathlib']['revision'] and ml['cache_helper_returncode']==0 and
        ml['owned_regular_file_logical_bytes']<=12*1024**3 and setup['elapsed_seconds']+ml['elapsed_seconds']<900 and cleanup['actually_removed_after_successful_full_reproduction'] and
        cleanup['cache_absent_after_removal'] and not Path(cleanup['own_cache']).exists() and cleanup['only_cycle012_owned_runtime_archive_decoder_Git_Mathlib_quarantined_input_target_removed'] and
        cleanup['quarantined_irrelevant_PII_text_removed'] and cleanup['regular_file_logical_bytes_removed']>setup['download_bytes'] and isinstance(cleanup['symlinks_removed'],int) and cleanup['measured_before_removal'],'Setup/cleanup overclaim')
    require('sorryAx' in (HERE/'development/initial_proof/EMATracking.log').read_text() and not re.search(r'\b(?:warning|error)\s*:',(HERE/'development/explicit_additions/EMATracking.log').read_text(),re.I) and
        read(HERE/'development/first_full_runner_control_blocker/checks/failure.json')['semantic_negative_detection_credited'] is False and
        all(x['observed_returncode']==0 for x in read(HERE/'development/first_full_runner_control_blocker/checks/worker_results.json')) and
        'rewrite' in (HERE/'development/first_full_runner_control_blocker/checks/proof/compiler_logs/false_reverse_weights.log').read_text() and
        '⊢ False' in (HERE/'development/explicit_norm_control/false_reverse_weights.log').read_text(),'Retained draft/control blockers not preserved')
    branches=[x for x in ROOT.rglob('*_branch*.json') if 'source_state' in x.parts];require(len(branches)==22,'Expected22minimal branch records')
    for x in branches:
        v=read(x);require(set(v)=={'branch','commit','metadata_policy'} and all(isinstance(i,str) for i in v.values()),'Branch metadata not minimal')
    contacts=inspect_contacts((str(x.relative_to(ROOT)),x.read_bytes()) for x in builder.selected_files())
    privacy={'all_twenty_two_branch_records_structurally_minimal':True,'new012_metadata_minimal_at_creation':True,'personal_commit_contacts_or_signed_payloads_in_branch_metadata':0,
        'raw_Git_and_one_irrelevant_contact_bearing_input_confined_to_own_excluded_cache_then_removed':True,'irrelevant_contact_values_not_printed':True,
        'unclassified_outgoing_email_pattern_matches':0,'contributed_scripts_not_acquired_or_executed':True,'historical_synthetic_fixture_matches':contacts,
        'known009_static_encoded_source_inspection_preserved':'cycle_009/incoming_static_privacy.json','printed_contact_values':False,
        'scope':'Owned structural minimization/scoped pattern scan, not exhaustive secret/security certification'}
    (HERE/'privacy_results.json').write_text(json.dumps(privacy,indent=2)+'\n');preserved=0
    with zipfile.ZipFile(ROOT/'researcher040282-cycle011-modulo-phase-increment.zip') as z:
        for member in z.namelist():
            name=member.removeprefix('researcher_040282/')
            if name not in LIVE:require((ROOT/name).is_file() and (ROOT/name).read_bytes()==z.read(member),'Prior011nonlive evidence changed: '+name);preserved+=1
        for name in ('STATE.json','CLAIM_LEDGER.csv'):require((HERE/'previous011_snapshot'/name).read_bytes()==z.read('researcher_040282/'+name),'Completed011snapshot differs')
    restoration=read(HERE/'historical_restoration.json');require(restoration['nonlive_members_checked']==1504 and restoration['missing_only_restored']==1 and
        restoration['missing_before_administrative_recovery']==[{'path':'cycle_006/source_state/main/.github/workflows/repo-checks.yml','bytes':9175}] and restoration['all_recovered_bytes_equal_delivered_members'] and
        not restoration['existing_files_overwritten'] and not restoration['historical_science_rerun'] and not restoration['scientific012_inputs_code_results_changed'] and
        not restoration['legacy_deleted_Lua_restored'] and restoration['user_deleted_legacy_Lua_absent'],'Missing-only old evidence recovery differs')
    protected=['2026-09-04_researcher040282_004_complex-ema.md']+['cycle_004/'+x for x in ('GateFoundations.lean','FreezeCore.lean','GateProposalBridge.lean','CoherenceEMA.lean','CoherenceDriveBridge.lean','check_cycle.py','compare_source.py')]
    with zipfile.ZipFile(ROOT/'researcher040282-cycle004-complex-ema.zip') as z:
        for name in protected:require((ROOT/name).read_bytes()==z.read('researcher_040282/'+name),'Protected004 source/report changed')
    for name in ('README.md','WORKFLOW.md','RESEARCH_QUEUE.md'):
        text=(ROOT/name).read_text();require('012' in text and '013' in text,'Root navigation stale')
    index=read(ROOT/'EVIDENCE_INDEX.json');require(index['ledger_rows']==126 and index['archive_only_ledger_references']==0,'Evidence index stale')
    for row in index['ledger_evidence']:
        require(row['availability']=='UNPACKED' and row['packet_members'],'Ledger citation archive-only')
        for member in row['packet_members']:require((ROOT.parent/member).is_file(),'Cited unpacked member absent')
    return {'current_ledger_rows':126,'prior122_rows_preserved':True,'formal_labels_prior100_plus3':103,'original_and_extracted_full_runner_success':True,
        'source_passes_each_mode':9,'actual_advances_each_mode':60,'source_initializers_each_mode':0,'current_tracking_coordinates_each_mode':370,'consumed_input_coordinates_each_mode':370,
        'adjacent_causal_coordinates_each_mode':333,'startup_coordinates_each_mode':115,'first_live_coordinates_each_mode':37,'decoded_C_innovations_each_mode':360,'alpha1_formula_only_inputs_each_mode':10,
        'reported_R_offdiag_bounds_each_mode':240,'reported_R_exact_diag_coordinates_each_mode':130,'maximum_component_error':9.992007221626409e-16,
        'wrong_models_detected_each_mode':10,'new_named_Lean_claims':3,'reused_named_dependencies_not_new_labels':28,'formal_controls':8,'setup_errors_credited':0,
        'four_workers_and_thirtyfive_details_match_reproduction':True,'critical_inline_files_equal_executed_extracted_sources':16,'verified_retained_acquisition_unchanged':acquired,
        'public_engine_unchanged':1,'scope_compiler_metadata_unchanged':3,'source_functions_not_copied_replaced_or_edited':True,'exact_real_not_full_Python_float_coupled_map_theorem':True,
        'new_module_not_installed_or_independently_reviewed':True,'no_production_study_authority_certificate_or_remote_write':True,'own_setup_and_quarantined_irrelevant_input_removed_after_full_reproduction':True,
        'retained_draft_control_blockers_not_detections':True,'prior011nonlive_evidence_files_preserved':preserved,'completed011_state_ledger_snapshots_match_delivery':True,'protected004_critical_files':len(protected),
        'numbered011validation_clarification_without_old_report_or_science_edit':True,'one_missing_old_CI_source_restored_exactly_no_science_rerun':True,'deleted_legacy_Lua_audit_remains_absent':True,
        'all_twenty_two_branch_records_minimal':True,'unclassified_email_pattern_matches':0,'historical_intentionally_synthetic_fixture_addresses_distinguished':2,
        'all_ledger_evidence_unpacked':True,'ledger_reference_count':index['unique_ledger_references'],'unpacked_log_count':index['unpacked_log_count'],
        'scope':'Owned arithmetic/packet/privacy/preservation consistency, no source/compiler scientific rerun, independent review/authority/integration/security certification'}

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
