"""Root navigation maintenance after observed branch-scoped checks; no packet."""
from pathlib import Path
import json,csv,datetime,re,zipfile
here=Path(__file__).resolve().parents[1];root=here.parent;now=datetime.datetime.now(datetime.timezone.utc).isoformat();note='2026-11-11_researcher040282_016_branch-coherence-motion.md';lean='cycle_016/CoherenceMotion.lean'
log=(here/'development/baseline_compile/compiler.log').read_text();obs=json.loads((here/'development/counterprobes/observations.json').read_text());cleanup=json.loads((here/'development/cleanup.json').read_text())
if re.search(r'\b(?:warning|error)\s*:',log,re.I) or 'sorryAx' in log or len(obs['rows'])!=7 or any(not x['explicit_false_goal'] or x['setup_name_or_timeout_failure'] for x in obs['rows']) or obs['equivalence_control']['returncode']!=0 or not cleanup['absent_after_removal']:raise RuntimeError('Observed checks incomplete')
if (here/'CoherenceMotion.lean').read_bytes()!=(here/'development/baseline_compile/CoherenceMotion.lean').read_bytes():raise RuntimeError('Delivered source not clean compiled source')
p=root/'CLAIM_LEDGER.csv'
with p.open(newline='') as f:r=csv.DictReader(f);fields=r.fieldnames;rows=list(r)
if any(x['cycle']=='16' for x in rows):raise RuntimeError('016alreadyrecorded')
for x in rows:
 if x['cycle']=='3':
  x['integration']='TEAM_FREEZE_WEIGHTUPDATE_PORT_MAIN_PR26_MERGED;OWN_PREVIOUS_CONTROLS_SEPARATE'
  x['independent_review']='TEAM_PORT_MERGED_PR26;NO_BLANKET_APPROVAL_OF_OWN_HARNESS'
base={'cycle':'16','related_work_or_followup':'USER_APPROVED_UNMERGED_P5_COMPONENT_SCOPE after main dependency check/clarification. Source main1c30PR26/27merged, noP5/C014/ClosedLoop; team P5branch54037eaoperators used with team module/namespaces, not flat015. Coupled nonreset/nonconsthistory carry/delayprobe deferred untilmainport. No015resend, no newstate, no08/09orotherteamwork.',
 'independent_review':'NEW_016_BRANCH_COMPONENT_CANDIDATE_AWAITING_TEAM_REVIEW;NOT_MAIN_INTEGRATION','publication':'LOCAL_ONE_LEAN_AND_SHORT_NOTE_READY;NO_AGENT_UPLOAD',
 'integration':'ADDITIVE_UNMERGED_TEAM_P5_BRANCH_ONLY;NO_MAIN_PINNED_EDIT;COUPLED_MODEL_INSTANTIATION_DEFERRED'}
formal=dict(base,claim_id='R040282-016-BRANCH-COHERENCE-MOTION',symbol='AIEFGate.CoherenceMotion (unmerged P5 scoped component)',
 statement_or_exact_header='For actual P5coherenceStep unit input and alpha∈[0,1], alpha*r-(1-alpha)<=rnext<=alpha*r+(1-alpha); signed change in[-(1-alpha)(1+r),(1-alpha)(1-r)], abschange<=(1-alpha)(1+r). Transfer to existingP5coherenceTrace. InitialCunitdisk gives abs one-step Rchange<=min(1,2(1-alpha))alln,diag0. Factor2attained foralpha>=1/2withunit initial C/oppositeinput; increasefactorattainedfromzeroC.',
 evidence_label='LEAN_COMPILED',domain_and_scope='Exact-real additive component on UNMERGED teamP5@54037ea1fabbeaed1eab44636971051000ac1673, actual moduleAIEFGateCore.PhaseCoherence; userexplicitlyselectedthisscope. No new state/EMAoperator, only observablewrapper/normlemmas. State-dependent envelope needsalpha rangeonly, not Cunit; uniformtracebound needs plainly stated initialCunit and inheritedP5invariant, NOTassumedfutureONband. Factor2sharpnessfamilydoesnotclaimoptimalminboundforallalphaorproductionattainment. Notmain/currentClosedLoopmodelpropertyyet, no Bcarry/dt/delayedcouplingpin,F1/F2portfix, locking/freezing/floatFFIorindependentadoption.',
 evidence_files=';'.join([lean,note,'cycle_016/PLAN.md','cycle_016/scope_decision.json','cycle_016/dependency_scope.json','cycle_016/source_state/p5_selected.json','cycle_016/development/baseline_compile/compiler.log','cycle_016/development/baseline_compile/invocation.json','cycle_016/development/dependency_compile','cycle_016/development/source_hook_review.json']))
neg=dict(base,claim_id='R040282-016-COHERENCE-MOTION-EXACT-CONTROLS',symbol='CoherenceMotion exact value/domain/clock controls',
 statement_or_exact_header='Seven exact positive baseline valuesreturn0; seven bad claims/observablechangesreturn1with explicitFalse: dropfactor2,increaseenvelopeforabs,negativealpha,alphagt1,nonunitinitial,two-stepdifferenceone-stepallowance,shiftobservableclock. +0observableequivalencewithsame7valueprobesreturn0. Independent fixed-timeP5operatorcalculation, not applyingnewboundtoitself.',
 evidence_label='EXECUTABLE_REGRESSION_CHECK',domain_and_scope='Fixed exact probes on unmergedP5sourcebasis, not a generic security verifier or coupled016nonresetprobe. Missingnames/parse/import/heartbeats/timeoutsnotcredited. Sourceimplemented_by/extern/macro/elab/unsafe/holehooksreviewedabsent, not arbitrary-source security. No state widen/015port/sourcePython/production/CLI/cert/remoteaction.',
 evidence_files=';'.join([lean,note,'cycle_016/development/counterprobes','cycle_016/development/counterprobe_run.log','cycle_016/development/source_hook_review.json']))
for x in (formal,neg):
 if set(x)!=set(fields):raise RuntimeError('Ledger schema')
rows.extend([formal,neg])
with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
old='cycle_006/source_state/main/.github/workflows/repo-checks.yml';target=root/old
if not target.exists():
 with zipfile.ZipFile(root/'researcher040282-cycle012-causal-ema-tracking.zip') as z:data=z.read('researcher_040282/'+old)
 target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 (here/'development/historical_path_restore.json').write_text(json.dumps({'missing_only':old,'bytes':len(data),'source':'delivered012ZIP','existing_overwrite':False,'science_rerun':False,'Lua_restored':False},indent=2)+'\n')
refs=sorted({v.strip() for x in rows for v in x['evidence_files'].split(';') if v.strip()});entries=[]
for ref in refs:
 path=root/ref
 if path.is_file():files=[ref]
 elif path.is_dir():files=sorted(str(x.relative_to(root)) for x in path.rglob('*') if x.is_file() and not x.is_symlink() and not any(t in x.parts for t in ('.git','__pycache__','.cache')))
 else:raise FileNotFoundError('Cited pathmissing:'+ref)
 if not files:raise FileNotFoundError('Emptycitation:'+ref)
 entries.append({'referenced_as':ref,'availability':'UNPACKED','files':files})
labels=sum(x['evidence_label']=='LEAN_COMPILED' for x in rows)
(root/'EVIDENCE_INDEX.json').write_text(json.dumps({'current_cycle':16,'observed_runtime_utc':now,'ledger_rows':len(rows),'formal_ledger_row_labels':labels,'label_granularity_note':'Groupedmodule rows from013, notdeclaration-countprogress','unique_ledger_references':len(refs),'all_ledger_references_unpacked':True,'archive_only_ledger_references':0,'ledger_evidence':entries,'logs':sorted(str(x.relative_to(root)) for x in root.rglob('*.log') if x.is_file()),'mode':'Navigationalindexonly, no packet'},indent=2)+'\n')
prior=json.loads((here/'previous015_snapshot/STATE.json').read_text());team=prior.get('team_feedback',{});team['015']='AUDITOR002_USER_RELAY_ADOPT_WITH_NOTES;35standardprints/steporder;F1required,F2dt/F3carry/F4deadprobe/F5evidencequalifiers;teamportnotonmain';team['016']='UserapprovedbranchscopedRcomponent;couplednonresetprobeDEFERRED'
state={'role':'Researcher040282','current_cycle':16,'current_directory':'cycle_016','current_status':'COMPLETED_UNMERGED_P5_R_MOVEMENT_COMPONENT_PENDING_REVIEW',
 'last_updated_date':now[:10],'last_updated_runtime_utc':now,'date_basis':'Observedexecution-environmentUTCclock, historicaldatesnotreconstructed','date_provenance':prior.get('date_provenance',{}),
 'current_question':'Derivedone-stepreportedRmovementonexistingteamP5coherenceoperator, userapprovedunmergedcomponentscope',
 'latest_completed_report':note,'latest_completed_lean_file':lean,'handoff_status':'BRANCH_SCOPED_LEAN_AND_SHORT_NOTE_READY;NO_AGENT_UPLOAD','new_packet_created':False,'ledger_rows':len(rows),'formal_ledger_row_labels':labels,
 'scope_decision':'cycle_016/scope_decision.json','dependency_record':'cycle_016/dependency_scope.json','source_basis':{'actual_main':'1c30ca56e56f11517d1e04f90d521a5aa6990c52','compiled_basis':'UNMERGEDresearch/lean-gate-p5@54037ea1fabbeaed1eab44636971051000ac1673','actual_team_module':'AIEFGateCore.PhaseCoherence','namespace':'AIEFGate.PhaseCoherence','merged_PRs_observed':[26,27],'open_PRs_observed':0,'main_lacks_P5_C014_and_ClosedLoopports_atinspection':True,'no_branch_merge_or_pretendmainimports':True,'coupled_nonreset_probe_deferred':True},
 'proof_observation':{'file':lean,'direct_compiler_returncode':0,'public_named_footprint_prints':21,'allowed_axioms':['propext','Classical.choice','Quot.sound'],'no_baseline_warnings_errors_or_holes':True,'raw_log':'cycle_016/development/baseline_compile/compiler.log','notmain_wholeCI_or_independentreview':True},
 'result':['DerivedRstepintervalalpha*r-beta<=rnext<=alpha*r+beta','Derivedasymmetricsigned/state-dependentabsenvelopewithoutinitialunitpremise','InitialunitC+P5unitdiskinvariantgivesallnabsone-stepRchange<=min(1,2beta),diag0','Factor2attainedforalpha>=1/2withinunitinitial/oppositeinputcomponentdomain;increaseboundattainedfromzeroC'],
 'counterprobe_observation':{'positive_baselines':7,'exact_false_negatives':7,'name_setup_timeout_failures_credited':0,'legitimate_pluszero_equivalence_returncode':0,'record':'cycle_016/development/counterprobes/observations.json','notgenericLeansecurity':True},
 'scope_limits':['UNMERGEDbranchcomponentonly;not015coupledrecursiononmainyet','No newstate/operator, no015resubmission or teamport/F1/F2fixclaimed','Nonfullreset/nonconsthistory Bcarry/coupling/dtprobe remainsdeferredpendingmainports','No phase-conventionpin fromnormbounds, no desiredfutureband/locking/Bpositivity/freezing/floatFFIorproductionclaim','Counterexampleswithinvalidalpha/nonunitinitialtestdroppedhypotheses, notsourceconfigurationruns'],
 'team_feedback':team,'user015feedback_record':'cycle_016/user_feedback_record.json','review_status':'PENDING_TEAM_REVIEW','current_cycle_independent_review_received':False,'owner_upload_confirmed':False,
 'authority_boundary':{'new_file_only':True,'main_branch_pinned_or_oldscientificsources_edited':False,'remote_changes':False,'integrated':False,'Python_engine_experiments_run':False},
 'cleanup':'cycle_016/development/cleanup.json','own_cache_removed':True,'source_hook_review':'cycle_016/development/source_hook_review.json','historical_science_preserved':True,'legacy_deleted_Lua_remains_absent':not Path('/home/user/audit').exists(),
 'previous_cycle':15,'previous_state':'cycle_016/previous015_snapshot/STATE.json','previous_ledger':'cycle_016/previous015_snapshot/CLAIM_LEDGER.csv',
 'in_progress':None,'research_processes_running':[],'next_cycle':17,'next_directory':'cycle_017','next_selected_work':'NOT_SELECTED;freshmain/ERRATA/mergedPR/feedback,checkportsfirst;couplednonresetprobeusingactualmainnameswhenavailable;no017work',
 'remote_changes_by_this_agent':False,'contacted_other_bots':False,'automatic_work_between_turns':False}
(root/'STATE.json').write_text(json.dumps(state,indent=2)+'\n')
(root/'README.md').write_text('''# Researcher040282 — currenthandoff

##016completed: USER-APPROVED UNMERGED P5 COMPONENT ONLY

- [CoherenceMotion.lean](cycle_016/CoherenceMotion.lean)
- [Shortbranch-scope016note](2026-11-11_researcher040282_016_branch-coherence-motion.md)

Uses team module AIEFGateCore.PhaseCoherence from unmergedP5@54037ea, NOTmain and
notflat015imports. User chose this component-onlyscope afterdependencycheck.
Main1c30hasPR26/27butnottheP5/C014/ClosedLoopports. Couplednonreset/nonconstant-
history Bcarry/delay/dtprobe remainsDEFERREDuntilmainmodelport. No015resend.

Derivedalpha*r-beta<=rnext<=alpha*r+beta, asymmetricchangeenvelope andstate-
dependentabsbound. InitialunitC+existingP5invariant givesabsone-stepRchange<=
min(1,2(1-alpha))foralln,diag0. Factor2attainedforalpha>=1/2; notglobaloptimality
orproductionattainmentclaim. No assumedfutureband/newstate/locking/freezing/FFI.
Cleanbaseline,7exactFalsecasesandlegitimate+0equivalenceaccepted; notaverifier.

## Scoped015adoptionandrecords

015ADOPT_WITH_NOTES recorded:Auditor00235standardprints/steporderreproduced,
13invalidmutationskilled/2legitequivalencesaccepted. F1requiredcouplingdelaypin,
F2dt,F3nonresetcarry,F4deadprobe,F5probe-over-rflqualifiersacknowledged. Teamowns
port/fixes; no blanketapprovalofownscripts or'closedloopproved'.

[STATE.json](STATE.json),[CLAIM_LEDGER.csv](CLAIM_LEDGER.csv),
[EVIDENCE_INDEX.json](EVIDENCE_INDEX.json) currentfor016. Groupedrows, notdeclaration
scores. Prior science preserved, citationsunpacked, unknownhistoricaldatesnot
guessed ([DATE_PROVENANCE.csv](DATE_PROVENANCE.csv)); newrecordsobservedUTCclock.
OneLean+shortnote,nopacket/ZIP/agentupload/remoteaction; owncache removed.

NextContinuefirstchecksactualmain/ERRATA/mergedPRs/feedback/portavailability.
Whenavailable, do thenonfullresetcarry/delayprobeonactualteamcoupledmodeland
instantiateRmovementthere. No017directory/proof/setup/test or unattendedwork.
008/009doneonmain;nooracle/admission/rate-law/CI/entrypoint/chroniclerwork.
DeletedLuaabsent, otherAIEFSevidencepreserved. Owner/team controlreview/intake.
''')
p=root/'RESEARCH_QUEUE.md';text=p.read_text();pos=text.find('## Adopted/pending/closed scopes');tail=text[pos:] if pos>=0 else ''
head='''# Team-prioritized research queue — Researcher040282

OneboundedcycleperContinue,currentmain/ERRATA/mergedandopenPRsbeforeselection.
OneLean+shortnote,no packet/securityverifier/pinnededit/outreach.

##016complete—UNMERGED P5 component, user-approvedscope

DerivedRstep/asymmetricmovementboundsanduniformmin(1,2beta)usingactualteamP5
coherenceoperator. Sharpness/value/domain/clockcontrols,legit+0accepted. No state
widening/015rewrite/mainintegration/coupledprobeclaim. Mainportsstillabsentatbasis.

##017NOTSELECTED/STARTED

1 Refreshcurrentmain/ERRATA/mergedPRs/feedback, checkP5/C014/ClosedLoopports.
2 Onceavailable,useactualteammainmodules/namespaces,notflatcopies. Firstthe
  nonfullresetprobe0<gamma*dt<1,B0nonzero,nonconsthistory,provedcarry/delay/dtvalues.
  TheninstantiateRmovementonactualcoupledmodelorsufficientedgepositivityproperty,
  notanassumedband. Do notresend015orcompete withitsport/F1/F2teamfixes.
3 Ifprerequisitesstillunmerged, honourtheexplicitdependency-scopechoice; do not
  pretendbranchportsaremainorwiden/redeclarethemodeltosidestepmissingimports.
4 NegativecreditonlyexplicitFalse;name/parse/timeoutblocked. Leadwithindependent
  values,notthecandidateagreeingwithitselfbyrfl. Keepimplemented_by/extern/macro/
  elabhookreviewscoped,notarbitrary-Leansecurity. Oldscience/datespreservedhonestly.
5 No017directory/proof/setup/test,production/S01/baseline/CLI/cert,remoteactionor
  unattendedwork. Owner/team decideadoptionandintegration.

'''
p.write_text(head+tail)
p=root/'WORKFLOW.md';text=p.read_text();text+='''\n##016scopeupdate\n
User-approvedunmergedP5Rcomponentonly.015ADOPT_WITH_NOTESscoped;F1/F2teamport,
F3carry/F4/F5evidenceissuesacknowledged. Mainlacksprerequisiteportsatbasis;
nonresetcoupledprobedeferred. Useactualteamnameswhenportsland, no015resend.
Cleancomponent/probeoutcomesnotadoption; no017work ornewpacket.\n''';p.write_text(text)
print(json.dumps({'cycle':16,'branch_scope':'UNMERGEDP5,userapproved','rows':len(rows),'formal_label_groups':labels,'unpacked_references':len(refs),'coupledprobe':'DEFERRED','017started':False},indent=2))
