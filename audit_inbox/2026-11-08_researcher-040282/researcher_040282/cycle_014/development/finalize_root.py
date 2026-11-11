"""Update current root records after observed direct checks; no packet machinery."""
from pathlib import Path
import json,csv,datetime,re,zipfile
here=Path(__file__).resolve().parents[1];root=here.parent;now=datetime.datetime.now(datetime.timezone.utc).isoformat();note='2026-11-10_researcher040282_014_feedback-trajectory-invariants.md';lean='cycle_014/TrajectoryInvariants.lean'
log=(here/'development/baseline_compile/compiler.log').read_text();obs=json.loads((here/'development/mutations/observations.json').read_text());cleanup=json.loads((here/'development/cleanup.json').read_text())
if re.search(r'\b(?:warning|error)\s*:',log,re.I) or 'sorryAx' in log or len(obs['rows'])!=8 or not cleanup['absent_after_removal']:raise RuntimeError('Direct evidence incomplete')
if (here/'TrajectoryInvariants.lean').read_bytes()!=(here/'development/baseline_compile/TrajectoryInvariants.lean').read_bytes():raise RuntimeError('Lean changed after baseline compile')
p=root/'CLAIM_LEDGER.csv'
with p.open(newline='') as f:r=csv.DictReader(f);fields=r.fieldnames;rows=list(r)
if any(x['cycle']=='14' for x in rows):raise RuntimeError('Do not duplicate014rows')
# New current-main integration metadata; prior scientific statements remain untouched.
for x in rows:
 if x['cycle']=='2':
  x['integration']='TEAM_CAPACITY_PORT_MERGED_ON_MAIN_PR25;NO_BLANKET_OWN_HARNESS_APPROVAL'
  x['independent_review']='TEAM_RELAY_ADOPT_MATH;PORT_MERGED_MAIN_PR25;NOT_OWN_HARNESS_APPROVAL'
base={'cycle':'14','related_work_or_followup':'Team priority3: current main PR25Capacity now merged; lift genuine main matrix facts to arbitrary causal feedback trajectories, not frozen-R P3branch response. Add independently derived sine-coupling/phase-increment envelope; prove exact feedback two-cycle to delimit safety versus freezing.013review still pending; no008/009/003port/rate-law work.',
 'independent_review':'NEW_014_CANDIDATE_AWAITING_TEAM_REVIEW;OWN_DIRECT_COMPILE_AND_FIXED_COUNTEREXAMPLES_ONLY','publication':'LOCAL_ONE_LEAN_AND_SHORT_NOTE_READY;NOT_UPLOADED',
 'integration':'NEW_FILE_ONLY_ON_MAIN_CAPACITY_API;NO_MAIN_PINNED_EDIT;NOT_MERGED'}
formal=dict(base,claim_id='R040282-014-FEEDBACK-TRAJECTORY-SAFETY',symbol='AIEFGate.TrajectorySafety (scoped module result)',
 statement_or_exact_header='Causal Aux×B recursion uses actual main stepM with D_n=F(n,aux_n,B_n),then U(n,aux_n,B_n,B_(n+1)). All positive-time B structural under current cap>=0/epsilon>=0, time0needs initial structure. Under EngineGate(p_n), post row/edge<=cap_n, not cap_(n+1), no initial feasibility. New-B delayed-current sine coupling<=cap_n and increment<=|dt_n|*(|omega_i|+cap_n). Valid bounded state-feedback has exact all-n0/1two-cycle and arbitrarily late threshold switches, so safety alone is not freezing in this drive class.',
 evidence_label='LEAN_COMPILED',domain_and_scope='Exact reals, finite linearly ordered nodes, unrestricted state-dependent/asymmetric/negative/time-varying driver and auxiliary update. Only current transition parameters needed for positive-time safety. No gamma/dt stability, source Rband/locking or initial Bcondition for n>=1. Structural cap/eps>=0 includes abstract real epsilon0, source epsilonpositive only; guarded capacity uses actual EngineGate cap>0/eps>0/gapQ>0/exact link. Norm/forcing bounds uniform in phase, NOT source-convention pin. Main defines Bmap but no complete phase/EMA state instantiation: not Python/float FFI, full-source counterexample, production trajectory or independent adoption. One grouped formal row, not per-helper score.',
 evidence_files=';'.join([lean,note,'cycle_014/PLAN.md','cycle_014/source_state/main_selected.json','cycle_014/development/baseline_compile/compiler.log','cycle_014/development/baseline_compile/invocation.json','cycle_014/development/main_compile','cycle_014/development/source_hook_review.json']))
mut=dict(base,claim_id='R040282-014-TRAJECTORY-SEMANTIC-CONTROLS',symbol='TrajectoryInvariants fixed semantic mutations',
 statement_or_exact_header='Eight fixed temporary changes rejected by compiler with names/imports present: stale B, no clip, no symmetrisation, retained diagonal, gate bypass, wrong next capacity clock, omitted initial invariant, unlinked capacity assertion. Baseline separately proves exact bad component values, dirty-start/time0 and capacity-clock refutations, and reuses main broken-link counterexample.',
 evidence_label='EXECUTABLE_REGRESSION_CHECK',domain_and_scope='Direct observations on fixed new candidate only; imports/main/pinned files unchanged. Failed proof-term type matching alone not the evidence: compiled baseline demonstrates actual false variants. No unknown-name/setup/parser/timeouts credited; no arbitrary-Lean security verifier, packet/extracted replay or Python engine experiment.',
 evidence_files=';'.join([lean,note,'cycle_014/development/mutations','cycle_014/development/mutation_run.log','cycle_014/development/source_hook_review.json']))
for x in (formal,mut):
 if set(x)!=set(fields):raise RuntimeError('Ledger schema mismatch')
rows.extend([formal,mut])
with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
old='cycle_006/source_state/main/.github/workflows/repo-checks.yml';target=root/old
if not target.exists():
 with zipfile.ZipFile(root/'researcher040282-cycle012-causal-ema-tracking.zip') as z:data=z.read('researcher_040282/'+old)
 target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 (here/'development/historical_path_restore.json').write_text(json.dumps({'missing_only':old,'bytes':len(data),'source':'delivered012ZIP','existing_overwrite':False,'science_rerun':False,'Lua_restored':False},indent=2)+'\n')
refs=sorted({v.strip() for row in rows for v in row['evidence_files'].split(';') if v.strip()});entries=[]
for ref in refs:
 path=root/ref
 if path.is_file():files=[ref]
 elif path.is_dir():files=sorted(str(x.relative_to(root)) for x in path.rglob('*') if x.is_file() and not x.is_symlink() and not any(t in x.parts for t in ('.git','__pycache__','.cache')))
 else:raise FileNotFoundError('Unpacked citation missing: '+ref)
 if not files:raise FileNotFoundError('Empty citation: '+ref)
 entries.append({'referenced_as':ref,'availability':'UNPACKED','files':files})
labels=sum(x['evidence_label']=='LEAN_COMPILED' for x in rows)
(root/'EVIDENCE_INDEX.json').write_text(json.dumps({'current_cycle':14,'observed_runtime_utc':now,'ledger_rows':len(rows),'formal_ledger_row_labels':labels,
 'label_granularity_note':'013/014use grouped module rows, labels are not declaration-count progress','unique_ledger_references':len(refs),'all_ledger_references_unpacked':True,'archive_only_ledger_references':0,
 'ledger_evidence':entries,'logs':sorted(str(x.relative_to(root)) for x in root.rglob('*.log') if x.is_file()),'mode':'Navigational workspace index only, no new packet/self-certification'},indent=2)+'\n')
oldstate=json.loads((here/'previous013_snapshot/STATE.json').read_text());team=oldstate.get('team_feedback',{});team.update({'002':'teamCapacity port PR25MERGED on current main','013':'phase/eta candidate still pending review','014':'newfeedbacktrajectorysafety candidate pendingreview'})
state={'role':'Researcher040282','current_cycle':14,'current_directory':'cycle_014','current_status':'COMPLETED_LOCAL_FEEDBACK_TRAJECTORY_SAFETY_AND_FORCING_BOUND_PENDING_REVIEW',
 'last_updated_date':now[:10],'last_updated_runtime_utc':now,'date_basis':'Observed execution-environment UTC clock, not historical reconstruction','date_provenance':oldstate.get('date_provenance',{}),
 'current_question':'Prove all-step structural/capacity safety under causal state feedback on actual main stepM, derive forcing envelope, delimit safety versus freezing',
 'latest_completed_report':note,'latest_completed_lean_file':lean,'handoff_status':'LEAN_AND_SHORT_NOTE_READY;NOT_UPLOADED','new_packet_created':False,'ledger_rows':len(rows),'formal_ledger_row_labels':labels,
 'source_basis':{'main':'3c5c0ef58c771b25c4b1eebd442e4073afa94b1f','source_record':'cycle_014/source_refresh.json','ERRATA_and_merged_PRs_read':True,'PR25':'MERGED;Capacity on main','open_PRs_observed':0,'inbox':'1b5ae52bfe5ae60092f1bacb4a61175f09fde211','inbox_feedback_changed_since013':False,'existing_Persistence_scope':'frozen R/branch response, not arbitrary feedback safety','no_public_duplicate_trajectory_result_found':'limited current library/branches/PRscope only, no private-work assurance'},
 'proof_observation':{'new_file':lean,'direct_compiler_returncode':0,'public_footprint_prints':29,'allowed_axioms':['propext','Classical.choice','Quot.sound'],'no_baseline_warnings_errors_holes':True,'raw_log':'cycle_014/development/baseline_compile/compiler.log','main_dependencies_compiled_unmodified':['GateMap','K3','RedTeam','EngineWitness','MatrixForm','Capacity'],'not_whole_main_CI_or_independent_adoption':True},
 'mutation_observation':{'fixed_cases':8,'compiler_rejections':8,'setup_or_name_failures_credited':0,'baseline_semantic_counterexamples_compiled':True,'record':'cycle_014/development/mutations/observations.json','not_general_Lean_verifier':True},
 'meaningful_results':['All positive-time Bstructure and all-times safety with initial structure, for state-dependent changing D and arbitrary auxiliary evolution','Capacity parameter clock p_n bounds B_(n+1), no initial feasibility','New-B sine coupling<=cap_n, source-shaped increment<=|dt_n|*(|omega_i|+cap_n), no locking premise','Exact safe/capacity-valid feedback two-cycle and arbitrary late threshold switches refute freezing from safety alone in general drive class'],
 'scope_limits':['Exact-real main Boperator feedback schema, not complete phase/EMA oscillator instantiation or Python/float FFI','Two-cycle is not a counterexample to full AIEFS because its arbitrary driver is not proved to arise from physical EMA/phases','Structural cap/eps>=0 only; guarded capacity actual EngineGate cap/eps/gapQ>0 and exactlink','No gamma/dt stability, desired Rband or branch persistence assumption; no fullN12sharp ON/freezing claim','Uniform sine bound does not identify phase convention,013is separate','Fixed-source hook review, not arbitrary-source security'],
 'team_feedback':team,'review_status':'PENDING_TEAM_REVIEW','current_cycle_independent_review_received':False,'latest_packet_owner_upload_confirmed':False,
 'authority_boundary':{'new_file_only':True,'main_or_pinned_artifacts_edited':False,'remote_changes':False,'module_integrated':False,'Python_engine_experiments_run':False},
 'cleanup':'cycle_014/development/cleanup.json','own_cache_removed':True,'source_hook_review':'cycle_014/development/source_hook_review.json','historical_science_preserved':True,'legacy_deleted_Lua_remains_absent':not Path('/home/user/audit').exists(),
 'previous_cycle':13,'previous_cycle_state':'cycle_014/previous013_snapshot/STATE.json','previous_ledger':'cycle_014/previous013_snapshot/CLAIM_LEDGER.csv',
 'in_progress':None,'research_processes_running':[],'next_cycle':15,'next_directory':'cycle_015','next_selected_work':'NOT_SELECTED;freshmain/ERRATA/mergedPR/teamfeedback first, then coordinate full phase/EMA instantiation or derived local bands; no015work',
 'remote_changes_by_this_agent':False,'contacted_other_bots':False,'automatic_work_between_turns':False}
(root/'STATE.json').write_text(json.dumps(state,indent=2)+'\n')
(root/'README.md').write_text('''# Researcher040282 — current handoff

##014completed locally; independent team review pending

- [TrajectoryInvariants.lean](cycle_014/TrajectoryInvariants.lean)
- [Short014note](2026-11-10_researcher040282_014_feedback-trajectory-invariants.md)

Main PR25capacity port is now merged.014builds on its actual stepM/Capacity API,
not a copy: all-step Bsymmetry/nonnegativity/diag0with arbitrary causal feedback,
post-step row/edge capacity with correct parameter clock, and an all-step sine-
coupling/increment envelope. No frozen R or desired band assumed. Initial structure
needed only when including time0; no initial feasibility for positive-time capacity.

An exact valid feedback two-cycle proves safety alone does not give freezing in
the general drive class; NOT a counterexample to the uninstantiated full phase/
EMA oscillator. No full coupled/float FFI, locking or sharp future-band claim.
Baseline compiles clean;8fixed semantic mutations rejected with separately proved
countervalues, not unknown-name/setup credit. OneLean+shortnote, no new packet,
ZIP, extracted replay or008/009work. Only own temporary setup removed.

## Current records

[STATE.json](STATE.json), [CLAIM_LEDGER.csv](CLAIM_LEDGER.csv),
[EVIDENCE_INDEX.json](EVIDENCE_INDEX.json) reflect014.013/014use grouped module
rows, not declaration-count scores. Cited evidence remains unpacked; historical
science/reports/archives preserved. [DATE_PROVENANCE.csv](DATE_PROVENANCE.csv)
withdraws old September filenames AS EXECUTION DATES; unrecorded historical
execution dates stay unknown, no guesses. New timestamps are observed UTC clock
records. Deleted Lua remains absent; other AIEFS audit roots untouched.

## Coordination and stop

002Capacity port PR25merged;003candidate next team port, no competing port here.
013phase/eta candidate still separately pending review. Main has no full phase/
EMA state model: future instantiation/binding and genuinely derived local bands
remain open.008E21and009E24–E26already main; no local replacement/guard work.
No rate-law/uploader/chronicler/entrypoint duplicate or remote action/upload.

Only another Continue: fresh current main/ERRATA/mergedPR/feedback, then choose
one highest-value missing result with team coordination. No015directory/proof/
setup/test or unattended process started. Owner controls publication/integration.
''')
p=root/'RESEARCH_QUEUE.md';text=p.read_text();pos=text.find('## Adopted/pending/closed scopes');tail=text[pos:] if pos>=0 else ''
tail=tail.replace('PR25pending owner merge at start','PR25MERGED on current main').replace('##014 NOT SELECTED/STARTED','##015 NOT SELECTED/STARTED')
head='''# Team-prioritized research queue — Researcher040282

One bounded cycle per Continue; current main, ERRATA AND merged PRs first.
One new Lean file+short note, no packet/self-certification, pinned edit or outreach.

##014completed locally, pending team review

Actual main stepM causal feedback trajectories: all-step structural safety and
post-capacity clock, edge/coupling/increment bounds; exact general-feedback two-
cycle with arbitrarily late threshold switches delimits safety versus freezing.
No frozen-R/input-band premise or initial capacity needed. EngineGate scope exact.
No full oscillator/float FFI or sharp local ONband.013review separately pending.

##015 NOT SELECTED/STARTED — only another Continue after fresh checks

1 Read new owner/seat feedback and current main/ERRATA/merged/open PRs; don't
  duplicate003port, adopted capacity, pending phase/trajectory work or team tasks.
2 Prefer a faithful full real phase/EMA/weight-state instantiation or a genuinely
  useful derived local drive/phase envelope, according to current team needs.
  Safety alone does not close locking/freezing: the exact two-cycle makes this
  limitation explicit. Do not insert desired future bands as assumptions.
3 Preserve exact epsilon/gamma/dt/source domain distinctions; no redundant hf0.
4 Direct compiler +meaningful semantic falsifiers, no name/setup credit or general
  Lean-security claim. New-file/erratum only, owner upload/integration decisions.
5 No015proof/directory/preregistration/setup/study, real S01/production/baseline/
  CLI/certificate, remote contact/push/PR/upload/merge or unattended continuation.

'''
p.write_text(head+tail)
p=root/'WORKFLOW.md';text=p.read_text().replace('PR25open at013start','PR25merged at014start').replace('013source-sensitive candidate compiles with eight rejected implementation mutations; team review pending, no014work.','013source-sensitive candidate and014feedback-trajectory candidate compiled with semantic mutations; both await team review, no015work.');p.write_text(text)
print(json.dumps({'cycle':14,'ledger_rows':len(rows),'formal_label_groups':labels,'unpacked_references':len(refs),'format':'OneLean+shortnote;notuploaded','015started':False},indent=2))
