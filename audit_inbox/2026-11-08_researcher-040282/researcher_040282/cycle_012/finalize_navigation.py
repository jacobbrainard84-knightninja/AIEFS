"""Update live navigation ONLY after observed012science/repetition/cleanup.
No science/source/Lean execution. Preserve standing workflow and historical scopes.
"""
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent

def require(condition,message):
    if not condition:raise RuntimeError(message)

def main():
    state=json.loads((ROOT/'STATE.json').read_text());repeat=json.loads((HERE/'standalone_reproduction.json').read_text());cleanup=json.loads((HERE/'compiler_cleanup.json').read_text())
    require(state['current_cycle']==12 and state['in_progress'] is None and repeat['actually_executed'] and repeat['runner_returncode']==0 and cleanup['cache_absent_after_removal'],'Only completed actual science updates live navigation')
    previous=(ROOT/'README.md').read_text();old=previous[previous.index('## Preserved earlier contributions'):previous.index('## Next bounded candidate')]
    old=old.replace('full historical suites not rerun in011','full historical suites not rerun in012')
    old+='''\n-011wrapped phase input/chord:3new compiled claims,28not yet composed there;9methods/
  56advances/mode,496inputs/434adjacent coords,10wrong models/8formal controls;
  13inline/4fresh full repeat/31details;122rows/100formal labels.012now composes
  prior004EMA/011phase/010history; small011validation-table correction is numbered
  in012, completed011report/code/results unchanged.\n\n'''
    old=old.replace('3new compiled claims,28not yet composed there','3new compiled claims,004EMA not yet composed there')
    intro='''# Researcher040282 — self-directed AIEFS research

Supporting Researcher001 and AuditorSeat002 with source-faithful exact-real
components, finite checks and adversarial controls. Prepared is not uploaded;
local compilation/repetition is not independent approval or integration. One
bounded cycle per Continue.

## Latest completed local science —012

**Causal moving-input EMA tracking and finite chronological variation budget,
actually composed with prior wrapped delayed phasor input.**

[Standalone012 report](2026-09-04_researcher040282_012_causal-ema-tracking.md).
Optional evidence: `researcher040282-cycle012-causal-ema-tracking.zip`.
Owner handoff: `cycle_012/HANDOFF.md`; closure: `cycle_012/packet_validation.json`.

-3new named theorem claims compiled clean, complete standard footprints:
 e_next=alpha*e-Delta z; finite alpha^n initial error+chronological weighted input
 variation;004EMA/011phase/010history definition-level composition.28old named
 dependencies recompiled, NOT new labels. Bound onlyalpha>=0, no locking premise.
-Actual intact Frozen engine9pass normal/-O,6traces/60advances/0initializers per
 mode.370current+370consumed errors,333causal coords (115startup/218live/37first
 live);240offdiag Rbounds/130diag0. Expected trajectories AND370cells before import.
-360actual Cinnovations decoded,10alpha1inputs explicitly argument-formula only;
 beta0never divided. Source alpha1accepted at synthetic Tw1e20,C exactly unchanged,
 late error0.8062257748298549. No ideal-real exp<1toFloat inference or strict
 contraction for<=1. Abstractalpha0not source valid. No production defect claim.
-Max component9.992007221626409e-16, causal/unroll4.440892098500626e-16 at fixed
 abs5e-13/rel0.245nonzero phase budgets<2,12tight nonzero Rbounds<1.10wrong models/
 mode (actual false-bound violations, not just different safe bounds),8formal controls.
-16inline files extracted,4public deps freshly fetched, full runner repeated with
 SAME verified runtime/Mathlib, science/4workers/35details match. No second clean
 setup or independent-review claim. Both research jobs exited, own setup removed.

**Scope:** exact-real component composition+finite float trajectories, not universal
NumPy/Python EMA/remainder/trig FFI, complete coupled map/stability/locking,
sharp future Rband/freezing/production/baseline/S01/shuffle/CLI/certificate, main
Lake project integration or independent approval. New unregistered local candidate,
source/registry/locks unchanged, not installed.

## State, evidence, follow-up and current team context

-`STATE.json`:012science/reproduction/cleanup complete, closure separately recorded;
 next013NOT STARTED.126local ledger rows/103LEAN_COMPILED labels, prior122/100
 unchanged. These are local labels, NOT main reference-library integration counts.
-`cycle_012/standalone_reproduction.json`: actual16file/fresh4deps/full repetition,
 same original setup; all35detailed files and4worker non-timing records match.
-`cycle_012/previous011_snapshot/`: completed011state/122-row ledger match delivery.
 All prior reports/archives/science preserved.1504old011nonlive members checked;
 one missing9175-byte006CI source restored exactly from delivered011ZIP, no old
 science rerun or existing overwrite. Deleted Lua remains absent; AIEFS roots kept.
-`EVIDENCE_INDEX.json` and `HISTORICAL_ARCHIVE_LOG_MAP.csv`: cited evidence/logs
 UNPACKED, historic archives separate/not nested.22minimal branch records;
 synthetic fixture contacts distinguished. One irrelevant contact-bearing note
 kept outside outgoing evidence and removed with own excluded cache, value not printed.
-012NUMBERED CLARIFICATION:011source table overstated DynamicState.validate as gap
 checking; actual finite/structural/history-length/Bsymmetry/diag/nonnegative only.
 No capacity/gap/reachability guarantee. Advance checks post-gap at825-828.
 Completed011report/code/results/ledger unedited, not rerun; proof/row checks unaffected.

Fresh42main/12retained inbox texts,22heads/1openPR24scope read. Main now contains
Gate P1/P2; active P3R-frozen controller/persistence not duplicated. E19-E21new-file
F4/F6/F7successors/errata/tests and E24-E26trust-guard work landed per current read;
older own submission "not installed" scopes are historical, not current absence.
Contributor genuineS01validator positive/forgeries are ITS scope, not our009harness
or010/011/012approval. E22sweep already performed, labelUNEXPLAINED; new entrypoint
proposal read only. No guard/rate-law/entrypoint/uploader/chronicler duplicate work.
Limited public inspection, not exhaustive/private coordination. No contributed
reproducer/checker acquired/executed. No remote action/upload/contact/merge.

Prepared2026-09-04 Atlantic/Reykjavik session label; owner/repository November and
runtime build dates separate. Unknown004chronology stays unknown; short004addendum
retained. Historical R00194compilation report does not approve our new controls,
source fidelity or005–012proposals. All own candidate review scopes remain explicit.

'''
    end='''## Next bounded candidate —013 NOT STARTED

Only another Continue: fresh owner/seat feedback/current source/library/limited
nonduplication, then consider smallest exact reported-R envelope composition from
this causal budget. No sharp future-band/locking conclusion inserted as a premise,
real campaign/frozen edit/remote push/PR/contact/upload/merge or unattended work.
Owner/seat control review/publication/integration. Own012compiler/Mathlib cache is
removed; check actual tools/resources before any future setup, do not claim reuse.
'''
    (ROOT/'README.md').write_text(intro+old+end)
    p=ROOT/'WORKFLOW.md';previous=p.read_text();head=previous[:previous.index('## Latest completed local science')];tail=previous[previous.index('## Prior formal evidence, preserved'):]
    tail=tail.replace('not fresh004 compilations in011','not fresh004 compilations in012').replace('Completed006/007/008/009/010/011 each added two minimal-at-creation records; current total20.','Completed006/007/008/009/010/011/012 each added two minimal-at-creation records; current total22.')
    current='''## Latest completed local science —012

Three clean standard-footprint causal EMA error/finite budget/phase-composition
claims;28old named dependencies recompiled, not new labels. e_next=alpha e-Delta z,
newestvariationweight1, initialerror explicit. Alpha>=0finite, not alpha<1; no
locking premise. C_(n+1)-z_n=alpha e_n differs from next-current error. Actual
source9pass normal/-O,60advances/6traces per mode;370current/370consumed/333causal
coords,240offdiag Rbounds/130diag0,360decoded+10alpha1formula-only inputs. Source
alpha1accepted, C exactly unchanged at extreme synthetic Tw1e20; no beta0division,
strict-contraction inference or production-cohort/infinite-time claim. Abs5e-13/
rel0fixed. Ten wrong models require actual inequality violation or intended
component mismatch>1e-7;8formal controls,0setup errors credited. Full16inline/
4fresh public deps repetition,4workers/35details match using same verified runtime/
Mathlib, not second clean setup or independent review. Own complete setup removed.

Initial proof helper-orientation and false-control complex-numeral norm rewrite
errors preserved, NOT falsifier success or promoted builds. Strict classifier
blocked rewrite error; correct only own syntax, no source/statement/case/tolerance
change. Final full runner and extracted repetition both0/allconditions observed.

126rows/103formal labels, prior122/100 preserved. Completed011state/ledger protected,
all prior science/archives unchanged.012corrects011validation table in numbered
follow-up: structural/finite state.validate NOT gap/capacity/reachability; advance
checks post-gap. Prior generic proof/finite row checks unaffected, no011rerun.
Missing-only006CI9175bytes recovered from011ZIP, no Lua restoration. All claim
citations/logs unpacked/indexed;22minimal branch records, historical synthetic
contacts distinguished; irrelevant PII-path note never outgoing, own cache removed.

Fresh42main/12retained inbox texts,22heads/PR24R-frozen scope. P1/P2and E19-E21,
E24-E26now landed per current tree/errata read; historical submissions not current
absence claims. ContributorS01positive not our009harness approval. E22sweep already
performed, entrypoint proposal read only. No duplicate gate/guard/rate-law/uploader/
chronicler/entrypoint work or contributed script execution. Limited public/private
coordination assurance only, no authority integration/certificate/remote write.

Next013NOT STARTED. Only another Continue: fresh feedback/source/library/nondup-
lication before selecting/preregistering smallest reported-R envelope composition.
No sharp future-band/locking assumption, real study or unattended continuation.

'''
    p.write_text(head+current+tail)
    p=ROOT/'RESEARCH_QUEUE.md';previous=p.read_text();tail=previous[previous.index('## Separate pending review / acceptance'):]
    tail=tail.replace('## Separate pending review / acceptance','''## Separate pending review / acceptance

-**012causal EMA tracking:**3new claims and28reused dependencies, source mappings,
  9methods/10wrong models/8formal controls require independent review. Definition-
  level composition now compiled, not full coupled/float FFI. Alpha1source rounding
  explicit, beta0not decoded, alpha0formal only. Paper R/uniform bounds not extra
  compiled claims. Numbered011validation clarification preserves delivered evidence.
  Current main independently landed successors/guards are separate from own local
  companions; do not infer our old controls/full scientific results approved.''')
    tail=tail.replace('011 now settles generic real wrapped input/chord semantics with startup; it\n   does NOT settle complete coupled transition, floating FFI or004 EMA composition.','012 now composes004EMA with011/010wrapped input/history in a finite budget,\n   but NOT complete coupled transition/floating FFI or closed-loop locking.')
    tail=tail.replace('009114;010118;011122. Latest6compiled history/phase results are not included in that old review.','009114;010118;011122;012126. Latest9compiled history/phase/tracking claims are not included in that old review.')
    tail=tail.replace('Completed010 state/ledger protected before011 transition (earlier snapshots retained).','Completed011state/ledger protected before012 transition; all earlier snapshots retained.')
    tail=tail.replace('Current20branch records minimal; own raw Git/cache removed after repetition.','Current22branch records minimal; own raw Git/quarantined irrelevant input/cache removed after repetition.')
    tail=tail.replace('unattended012 authorized by this completed cycle.','unattended013 authorized by this completed cycle.')
    prefix='''# Research queue — Researcher040282

One bounded cycle per Continue, fresh current source/library/feedback/nonduplication
before scientific selection. Local revisable plan, not assignments to other seats.

##012completed locally — causal moving-input EMA tracking

Three new compiled claims: exact e_next=alpha e-Delta z, finite chronological
variation budget and004/011/010definition-level composition.28reused names not
new labels. Actual intact engine9pass normal/-O,6traces/60advances/370current/
370consumed/333causal coords per mode;360decoded+10explicit alpha1formula-only.
10wrong models/mode/8formal controls.16inline/4fresh full repetition,4workers/
35details match; own runtime/Mathlib/Git/decoder/archive/quarantined input removed.
126rows/103formal labels, prior122/100 unchanged. No full coupled locking/float
proof, independent review/integration or owner upload. Numbered011gap-validation
wording correction, prior completed science not changed/rerun.

## Next candidate —013 NOT STARTED

1 Only another Continue: refresh owner/seat feedback, current library/source and
  limited public coordination. P1/P2and main successors/guards now landed; P3active
  R-frozen branch not a phase/EMA result. Do not duplicate rate-law/E22, guards,
  contributed entrypoint, uploader/checksum or chronicler work.
2 Consider smallest formal reported-R envelope using causal tracking budget,
  unit phasors and current returned-R read order. Do not assume a sharp future
  band/locking as the premise; stated input variation/capacity conditions must
  be independently justified. Select ONEafter inspection, not already selected.
3 Preregister exact domain, interface, nonzero positives, false variants and any
  fixed tolerance before target tests/compilation. Keep real finite bounds,
  float alpha1/source0exclusion, paper/Rregimes and full coupled dynamics separate.
4 Own012setup removed. Check actual tools/resources; do not claim reuse or install
  by habit. Setup/import/parse/identifier/runtime/timeouts never math detections.
5 No production/S01/full baseline/shuffle/CLI/certificate, frozen/registry/lock edit,
  authority promotion, contact/push/PR/upload/merge or unattended013. No013directory,
  preregistration/proof/setup/test started. Owner/seat decide any review/intake.

'''
    p.write_text(prefix+tail)
    handoff=f'''#012owner handoff — causal EMA tracking

Main: `{REPORT_NAME}`\nOptional: `researcher040282-cycle012-causal-ema-tracking.zip`.
Owner uploads; no agent remote action. Inbox-ready only with packet_validation.json
and root LOCAL_PACKET_CLOSURE_VERIFIED;NOT_UPLOADED. Prepared2026-09-04session
label separate from owner/repository November/runtime build dates.

3new clean standard-footprint claims,28old dependency claims NOT new labels:
causal current-input error, chronological finite budget, actual004/011/010definition
composition. Latest variation weight1; initial error explicit; alpha>=0finite,
no alpha<1/convergence/locking premise. Source Rafter C/old-input consumption.

Actual unchanged engine9pass normal/-O,6traces/60advances/mode,0initializers;
370current+370consumed/333causal coords,115startup/218live/37first-live;
240offdiag Rbounds/130diag0.360decoded inputs+10alpha1argument-formula only,
beta0never divided, source alpha1Cexactly unchanged, late error.8062257748298549.
Abs5e-13/rel0fixed; max component9.992007221626409e-16,10wrong models/mode,
8formal controls. Actual false upper-bound violations, not just different safe bounds.
Counts per accepted run, not total including retained blocked attempt/repetition.

16inline files extracted/4fresh public deps/full runner repetition; same verified
runtime/targeted Mathlib, NOT second clean setup or independent approval. Science/
4worker non-timing/35detailed files match. Original{repeat['original_elapsed_seconds']}s,
extracted{repeat['extracted_elapsed_seconds']}s, both0. Own cache removed afterward:
{cleanup['regular_files_removed']}regular files/{cleanup['regular_file_logical_bytes_removed']}logical
bytes/{cleanup['symlinks_removed']}measured symlinks. Includes raw Git/quarantined
irrelevant PII text never outgoing. No unrelated-cache audit/deletion claim.

Preserved failed own proof helper-orientation and complex-numeral false-control
rewrite blocker. Strict classifier blocked it, not math success. Source passed
before/after own syntax fix; no source/statement/case/tolerance change.

126local ledger rows/103formal labels, prior122/100 untouched. Completed011snapshot
matches delivery;1504nonlive old011members preserved; one missing9175-byte006CI
copy restored exact from011ZIP, no old science rerun or Lua restoration. Other
AIEFS audit roots untouched. All claim citations/logs unpacked, prior archives not
nested,22minimal branch records, known synthetic fixture contacts distinguished.

New012clarification to011table: state.validate is finite/structural/Bsymmetry/
diag/nonnegative/history length, NOT gap/capacity/reachability; advance checks
post-gap. Completed011report/code/results unchanged; proof/rowchecks unaffected.

Current main42texts/12retained inbox,22heads/PR24R-frozen scope. Gate P1/P2and
E19-E21/E24-E26now landed per current read; prior local statuses historical.
Contributor genuineS01validator positive not our009harness/010/011/012approval.
No duplicated rate-law/guard/entrypoint/uploader/chronicler or contributed scripts.

Not full coupled/float FFI/locking, sharp future bands, production/S01/baseline/
CLI/writer/certificate, main project integration/authority promotion. New unregistered
local module only, not installed. Independent012review pending. Only another
Continue: fresh check then consider smallest exact reported-R envelope composition.
No013work/directory/preregistration/setup/test or unattended job started.
'''.replace('{REPORT_NAME}','2026-09-04_researcher040282_012_causal-ema-tracking.md')
    (HERE/'HANDOFF.md').write_text(handoff)
    print('012live navigation/handoff updated from observed completed receipts;013not started')

REPORT_NAME='2026-09-04_researcher040282_012_causal-ema-tracking.md'
if __name__=='__main__':main()
