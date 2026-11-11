"""Current root navigation/evidence maintenance, not a packet or proof verifier."""
from pathlib import Path
import json,csv,datetime,re,zipfile
here=Path(__file__).resolve().parents[1];root=here.parent;now=datetime.datetime.now(datetime.timezone.utc).isoformat();note='2026-11-10_researcher040282_015_real-coupled-core.md';lean='cycle_015/ClosedLoopCore.lean'
log=(here/'development/clean_baseline/compiler.log').read_text();obs=json.loads((here/'development/counterprobes/observations.json').read_text());cleanup=json.loads((here/'development/cleanup.json').read_text())
if re.search(r'\b(?:warning|error)\s*:',log,re.I) or 'sorryAx' in log or len(obs['rows'])!=7 or any(not x['explicit_false_goal'] or x['setup_or_name_failure'] for x in obs['rows']) or not cleanup['absent_after_removal']:raise RuntimeError('Actual evidence incomplete')
if (here/'ClosedLoopCore.lean').read_bytes()!=(here/'development/clean_baseline/ClosedLoopCore.lean').read_bytes():raise RuntimeError('Delivered file not clean compiled bytes')
p=root/'CLAIM_LEDGER.csv'
with p.open(newline='') as f:r=csv.DictReader(f);fields=r.fieldnames;rows=list(r)
if any(x['cycle']=='15' for x in rows):raise RuntimeError('Do not duplicate015')
for x in rows:
 if x['cycle']=='3':x['integration']='TEAM_FREEZE_WEIGHTUPDATE_PORT_PR26_OPEN_AT015_INSPECTION;NO_COMPETING_PORT'
base={'cycle':'15','related_work_or_followup':'Concrete non-shuffled real closed-loop instantiation of own013/014candidate components and accepted010/011 on actual main Boperator. Main3c5c0ef,ERRATA/mergedPR25/openPR26read; no003port duplicate,008/009/rate-law/CI work. Inbox newstaticP3/P4areview not an adoption of own candidates.',
 'independent_review':'NEW_015_CANDIDATE_AWAITING_TEAM_REVIEW;013_014DEPENDENCIES_REMAIN_OWN_UNADOPTED_CANDIDATES','publication':'LOCAL_ONE_LEAN_AND_SHORT_NOTE_READY;NO_AGENT_UPLOAD',
 'integration':'NEW_PROPOSED_REAL_STATE_MODEL_ON_CURRENT_MAIN_BAPI;NO_MAIN_PINNED_EDIT;NOT_MERGED'}
formal=dict(base,claim_id='R040282-015-CONCRETE-REAL-COUPLED-CORE',symbol='AIEFGate.ClosedLoop (scoped model/connection result)',
 statement_or_exact_header='Config includes actual main Params and real exp(-dt/Tw) coefficient. Aux has theta,D+1history,directedC; concrete Fcomputes NEWC/magnitude-symmetricR/drive, main stepM NEWB, Uuses NEWgatedBforphase/wrap/appendNEWtheta. Actual theta=011phaseTrace on source-force increments generated from actual NEWB; actual history=010historyTrace; actual rawinput=011inputPhasor; actual Ctrace=013coherenceTrace, alln.014Bstructure/capacity apply to this constrained recurrence; actual Cunit/Rrange conditional on dt>=0,Tw>0,C0unit.',
 evidence_label='LEAN_COMPILED',domain_and_scope='Exact-real proposed full non-shuffle state transition, not existing-main-phase-state equality or Python/float FFI. Current main BAPI actual/unmodified; accepted010/011 plus own013/014candidate imports explicit. No prescribed external drive/u, source-force not ordinary wrapped-angle subtraction. Constant initial history, supplied initialtheta/C/B. Source delay consistency positive dt/tau,Ddt=tau impliesD>0; algebra cancoverD0onlyabstract. Bstructureinitialguard/cap/epsilon scopes inherited exactly, EngineGate strict positivity/link for capacity. Does not prove locking/freezing/sharp N12bands, source runtime validation/diagnostics/shuffle/aliasing/rounding or fullproduction.35public proofs standard footprints, onegrouped row notper-helper score. Optional bounds corollaries timedout and EXCLUDED, not claimed.',
 evidence_files=';'.join([lean,note,'cycle_015/PLAN.md','cycle_015/source_state/main_selected.json','cycle_015/source_state/inbox_selected.json','cycle_015/feedback_navigation.json','cycle_015/development/clean_baseline/compiler.log','cycle_015/development/clean_baseline/invocation.json','cycle_015/development/dependency_compile','cycle_015/development/source_hook_review.json']))
negative=dict(base,claim_id='R040282-015-SOURCE-ORDER-COUNTERPROBES',symbol='ClosedLoopCore exact fixed ordering/convention probes',
 statement_or_exact_header='Real-alpha1/2nonzero firststep: Cdiagonal1/2/offdiag+-I/2,Roffdiag1/2,drive/proposal2,gatedB2/3,used increment2/3versusoldB0/unprojected2,newtheta/newesthistory2/3. Seven positive exact probes plus one normaliser repair positive compiled0; seven fixed implementation changes reduceexplicitFalse: oldCdrive,complexmeanbeforeabs,oldBphase,unprojectedBphase,appendoldtheta,newestread,dropomega*tau. Five completed initial negatives+two repaired/completed; blocked normalisation/setup/timeout attempts not credited.',
 evidence_label='EXECUTABLE_REGRESSION_CHECK',domain_and_scope='Focused exact definition-prefix Lean probes, not a general Lean verifier, packet certification or Python engine run. Expected points fixed before compile, alpha relation proved from inverse-log Tw rather than replaced by constant. Same actual candidate definitions/imports, only designated temporary changes. Non-production realFin2state/component witnesses; manual history/offset argument probes not production trajectories. Source hook list reviewed absent, not arbitrary-source security. No model/tolerance/expected-point tuning; unprojected normaliser rewrite ordering fixed, initial canceled seventhcase later completed.',
 evidence_files=';'.join([lean,note,'cycle_015/development/counterprobes','cycle_015/development/counterprobe_run.log','cycle_015/development/first_counterprobe_blocker','cycle_015/development/repair_setup_error.log','cycle_015/development/source_hook_review.json']))
for x in (formal,negative):
 if set(x)!=set(fields):raise RuntimeError('Ledger schema mismatch')
rows.extend([formal,negative])
with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
old='cycle_006/source_state/main/.github/workflows/repo-checks.yml';target=root/old
if not target.exists():
 with zipfile.ZipFile(root/'researcher040282-cycle012-causal-ema-tracking.zip') as z:data=z.read('researcher_040282/'+old)
 target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 (here/'development/historical_path_restore.json').write_text(json.dumps({'missing_only':old,'bytes':len(data),'source':'delivered012ZIP','existing_overwrite':False,'old_science_rerun':False,'Lua_restored':False},indent=2)+'\n')
refs=sorted({v.strip() for x in rows for v in x['evidence_files'].split(';') if v.strip()});entries=[]
for ref in refs:
 path=root/ref
 if path.is_file():files=[ref]
 elif path.is_dir():files=sorted(str(x.relative_to(root)) for x in path.rglob('*') if x.is_file() and not x.is_symlink() and not any(t in x.parts for t in ('.git','__pycache__','.cache')))
 else:raise FileNotFoundError('Unpacked citation missing:'+ref)
 if not files:raise FileNotFoundError('Empty citation:'+ref)
 entries.append({'referenced_as':ref,'availability':'UNPACKED','files':files})
labels=sum(x['evidence_label']=='LEAN_COMPILED' for x in rows)
(root/'EVIDENCE_INDEX.json').write_text(json.dumps({'current_cycle':15,'observed_runtime_utc':now,'ledger_rows':len(rows),'formal_ledger_row_labels':labels,
 'label_granularity_note':'013onward uses grouped formal module rows, not declaration-count progress','unique_ledger_references':len(refs),'all_ledger_references_unpacked':True,'archive_only_ledger_references':0,
 'ledger_evidence':entries,'logs':sorted(str(x.relative_to(root)) for x in root.rglob('*.log') if x.is_file()),'mode':'Navigational workspace index only, no packet/self-certification'},indent=2)+'\n')
previous=json.loads((here/'previous014_snapshot/STATE.json').read_text());team=previous.get('team_feedback',{});team.update({'003':'teamFreeze/WeightUpdate port PR26OPEN at015inspection, no competing port','013':'candidate dependency,reviewpending','014':'candidate dependency,reviewpending','015':'concrete coupled real model and connection proofs,reviewpending'})
state={'role':'Researcher040282','current_cycle':15,'current_directory':'cycle_015','current_status':'COMPLETED_LOCAL_CONCRETE_REAL_COUPLED_CORE_PENDING_TEAM_REVIEW',
 'last_updated_date':now[:10],'last_updated_runtime_utc':now,'date_basis':'Observed execution-environment UTC clock, not historical reconstruction','date_provenance':previous.get('date_provenance',{}),
 'current_question':'Instantiate phase/history/EMA and main Bstep as one real recursion and prove its actual trajectories match the component interfaces',
 'latest_completed_report':note,'latest_completed_lean_file':lean,'handoff_status':'LEAN_AND_SHORT_NOTE_READY;NO_AGENT_UPLOAD','new_packet_created':False,'ledger_rows':len(rows),'formal_ledger_row_labels':labels,
 'source_basis':{'main':'3c5c0ef58c771b25c4b1eebd442e4073afa94b1f','source_record':'cycle_015/source_refresh.json','ERRATA_merged_and_open_PRs_read':True,'PR25':'MERGED Capacity','PR26':'OPEN Freeze/WeightUpdate003port,notduplicated','inbox':'df5c28f162bfb0b23d5ffb872dc2a8c6258b4193','inbox_new_content':'Static P3/P4areview only, read/notexecuted/notowncandidateadoption','feedback_record':'cycle_015/feedback_navigation.json','scope':'Limited public coordination, no private-work assurance'},
 'proof_observation':{'file':lean,'direct_compiler_returncode':0,'public_footprint_prints':35,'allowed_axioms':['propext','Classical.choice','Quot.sound'],'no_clean_baseline_warnings_errors_or_sorry':True,'raw_log':'cycle_015/development/clean_baseline/compiler.log','imports':'Unmodified current main BAPI,accepted010/011,own013/014candidates; all dependencies recompiled, no oldlabelsrecounted','not_whole_main_CI_or_independent_adoption':True},
 'new_connections':['Concrete source-order F/U instantiate014; drive/u no longer unspecified inputs','Actual coupled theta=011phaseTrace on increments generated by actual NEW model B, not wrapped-angle differences','Actual history=010historyTrace; oldest/newest/startup are derived invariants of coupledrun','Actual rawinput=011inputPhasor and actual Ctrace=013coherenceTrace foralln','Bstructure/capacity and Cunitdisk/Rrange apply along this actual model recursion'],
 'counterprobe_observation':{'positive_baselines':7,'additional_repair_positive':1,'exact_negative_cases':7,'all_explicit_false':True,'name_setup_parser_timeouts_credited':0,'actual_record':'cycle_015/development/counterprobes/observations.json','attempts':'Five completed initial negatives+two repaired/completed; blocked unprojectednormalisation/setup/cancelledcase notcredited','not_general_Lean_security':True},
 'scope_limits':['Proposed exact-real deterministic non-shuffled model, not existing-main-phase identity, main integration or Python/float FFI','No source validation/exception/projectiondiagnostic/shuffle/aliasing/rounding theorem','No closed-loop locking/freezing/sharp future Rband/N12ONcertificate','Real-alpha range conditions not IEEEalpha strict<1 guarantee','Current013/014imports are own candidates, not claimed team-adopted','Two optional extra bounds corollaries timedout,excluded from finalcompiledfile and claims'],
 'team_feedback':team,'review_status':'PENDING_TEAM_REVIEW','current_cycle_independent_review_received':False,'owner_upload_confirmed':False,
 'authority_boundary':{'new_file_only':True,'main_pinned_or_previous_candidate_sources_edited':False,'remote_changes':False,'module_integrated':False,'Python_engine_experiments_run':False},
 'cleanup':'cycle_015/development/cleanup.json','own_cache_removed':True,'source_hook_review':'cycle_015/development/source_hook_review.json','historical_science_preserved':True,'legacy_deleted_Lua_remains_absent':not Path('/home/user/audit').exists(),
 'previous_cycle':14,'previous_state':'cycle_015/previous014_snapshot/STATE.json','previous_ledger':'cycle_015/previous014_snapshot/CLAIM_LEDGER.csv',
 'in_progress':None,'research_processes_running':[],'next_cycle':16,'next_directory':'cycle_016','next_selected_work':'NOT_SELECTED;freshmain/ERRATA/mergedPR/teamfeedback first; formal source-model adoption/connections or derived local bands, no016work',
 'remote_changes_by_this_agent':False,'contacted_other_bots':False,'automatic_work_between_turns':False}
(root/'STATE.json').write_text(json.dumps(state,indent=2)+'\n')
(root/'README.md').write_text('''# Researcher040282 — current handoff

##015completed locally; independent team review pending

- [ClosedLoopCore.lean](cycle_015/ClosedLoopCore.lean)
- [Short015note](2026-11-10_researcher040282_015_real-coupled-core.md)

A concrete REAL non-shuffled phase/history/EMA/B recursion now instantiates the
current-main Boperator and own013/014candidate interfaces. It computes REAL alpha
fromdt/Tw, NEWC/R/drive beforemainBstep, then NEWgatedBphase/wrap/appendNEWtheta.
Drive and unwrapped increments are generated by the state, not external inputs.

Kernel proofs connect ACTUAL coupled history/theta/rawinput/Ctrace to010/011/013;
014Bstructure/capacity and Cunitdisk/Rrange apply along THIS recurrence. Nonzero
first-step probes distinguish oldC,complexmean-before-abs,old/unprojectedBphase,
oldthetaappend,newestread,droppedfrequencyterm. Seven positive baselines plus
one repair positive; seven negativesexplicitFalse. Clean model standardaxioms
only; optional corollaries timedoutand EXCLUDED. No fake timeout/name credit.

Not a full Python/float FFI, validation/diagnostic/shuffle/memory theorem, main
integration, closed-loop locking/freezing or sharp N12ONcertificate.013/014remain
own candidate dependencies pendingreview, not adoptedbyassertion. Newmodel is a
proposed missing real state layer, not equalitytoexistingmainphaseState.

## Current records and coordination

[STATE.json](STATE.json),[CLAIM_LEDGER.csv](CLAIM_LEDGER.csv),
[EVIDENCE_INDEX.json](EVIDENCE_INDEX.json) updatedfor015. Groupedmodule rows,
not declaration scores. Prior science preserved, all citationsunpacked, old
unrecordeddatesnotinvented ([DATE_PROVENANCE.csv](DATE_PROVENANCE.csv)).
OneLean+shortnote, no newZIP/packet/self-certification, no agentupload/remotecontact.
Onlyown temporaryruntime/Git/Mathlib/cache removed; deletedLuaremainsabsent.

MainPR25merged; PR26cycle003Freeze/WeightUpdateportopenatinspection, notduplicated.
NewinboxP3/P4astaticreview readonly, not own013/014/015adoption.008E21and009E24–E26
closedonmain, no replacement/admission/rate-law/CI/entrypoint/chroniclerwork here.

AnotherContinue firstrefreshesmain/ERRATA/mergedandopenPRs/teamfeedback. Focusnext
on actual constrained phase/EMA dynamics or useful derivedlocalbands, not a desired
bandassumedaspremise. No016directory/proof/setup/test or unattendedjob started.
Owner/team control publication, reviewand integration.
''')
p=root/'RESEARCH_QUEUE.md';oldtext=p.read_text();pos=oldtext.find('## Adopted/pending/closed scopes');tail=oldtext[pos:] if pos>=0 else ''
tail=tail.replace('adopt candidate, next team port','adopt candidate, team port PR26OPEN at015inspection').replace('next team port','team port PR26OPEN at015inspection')
p.write_text('''# Team-prioritized research queue — Researcher040282

Oneboundedcycle perContinue, currentmain/ERRATA/mergedandopenPRs first.
OneLean+shortnote, no newpacket/generalverifier/pinnededit/outreach.

##015completed locally, reviewpending

Concrete real state model computes ownphase/history/EMA/current-mainBfeedback.
Actualtheta/history/rawinput/Ctrace connections to010/011/013proved, B/C/R
invariants transferred to actualrun. Exactreal alpha relation/nonzero firststep
orderprobes, seven explicitFalsevariants. No fullsourcefloatFFI, mainadoption,
locking/freezing/sharpbands. Optionalextra boundscorollaries blockedandexcluded.

##016NOT SELECTED/STARTED — anotherContinueafterfreshchecks only

1 Read new teamfeedback/currentmain/ERRATA/merged/openPRs; avoid003portPR26,
  pendingsource-model/phase/trajectorywork and allclosed008/009/activeRatelawtasks.
2 Prefer adoption/interface gaps in the concrete model or rigorously derived
  phase/drive local envelopes along its actualconstrainedevolution. Do not
  assume desiredbandsorlocking.014general-feedbacktwo-cycle is NOT a counterexample
  to the more constrained015driver without additional proof.
3 Keep positivity/epsilon/delay/sourceTime/real-versus-float domains exact;
  no redundant hf0. Named interface lemmas should avoid expensive global definitional
  unfolding if revisiting the optional capacity-to-force corollary.
4 Directcompile/fixedsemanticcounterexamples only, no timeouts/name/setupcredit,
  no arbitrary-source-securityclaim. Preserve completedscientificevidence.
5 No016directory/preregistration/proof/setup/test, production/S01/baseline/CLI/
  certificate, remotecontact/push/PR/upload/merge or unattendedcontinuation.

'''+tail)
p=root/'WORKFLOW.md';t=p.read_text().replace('003adopt candidate,\nnext team port','003adopt candidate,\nteam port PR26openat015inspection').replace('013source-sensitive candidate and014feedback-trajectory candidate compiled with semantic mutations; both await team review, no015work.','013phase/014trajectory/015concrete coupled-model candidates await teamreview; currentroots updated, no016work.');p.write_text(t)
print(json.dumps({'cycle':15,'rows':len(rows),'formal_label_groups':labels,'unpacked_references':len(refs),'format':'oneLean+shortnote;noagentupload','016started':False},indent=2))
