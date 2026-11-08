# Cycle 006 preregistration — bounded v4.1 source/synthetic review

Researcher040282. Session preparation stamp2026-09-04, Atlantic/Reykjavik.
Prior owner/seat correspondence carries2026-11-08 handoff labels; those are not
reconstructed execution dates. Do not infer dates from compiler builds or logs.

## Source and nonduplication

Current main acquired read-only: eb3933c196ee19e80e1621ae80d89ca72e6d9485.
Inbox: b466ab6cdd564ce3f7848e7701b378c5f0cc475f. No new targeted005 feedback found
in the selected navigation. Main17 and inbox37 files acquired before this plan;
local import dependencies will be verified before any candidate execution.

Target: AIEF_Experiments/aief_modular_platform_v1_analysis_v4/
AIEF_1_4_Twindow_sensitivity_analysis_v4_1.py. It remains an unaudited synthetic-
only candidate. E17 already corrects saved-grid detection/interval-censoring and
min-positive-saved-spacing tolerance wording. Do NOT rediscover frozen-v4 misses,
re-report corrected strings, or infer actual saved-run impact. Existing candidate
tests were read but are not our independent oracle. No real trajectory files,
--allow-unaudited-candidate, run_analysis or production simulation will be used.

Prior own A-F2/A-F3 already state boundary bootstrap and shorter onset follow-up
limitations. Here verify/explain their precise persistence in the CURRENT
candidate; do not rename them new defects. No code patch or altered estimand is
promised if candidate behavior matches its declared operational contract.

## Operational reference, before tests

Saved grid: intended t_i=1/100+i/2, i=0..639; actual supplied timestamps separately
checked against the acquired candidate's declared array. On a Boolean condition,
find maximal contiguous true runs by a forward scan, independent of candidate
_run_end and searchsorted. A run start s qualifies if its endpoint span is at
least D minus tau, with tau=1e-6 times the minimum positive saved-grid spacing.
Compute reference spans/thresholds with Fraction, not candidate float additions.

Run-onset outputs:
H = earliest qualifying run start, or None;
R =0 iff the initial true run qualifies;
V = earliest qualifying true run start after the first False sample (including
False at index0), or None;
class = retention if R, else recovery if V, else none.

For a sorted grid, later starts in one true run cannot have more remaining span
than its start. Hence H exists iff R exists OR V exists. R and V can both exist:
classification is exclusive by retention precedence, but event flags are not a
partition. Explain/probe rather than silently redefine V or its denominator.

Floating policy versus exact duration must remain separate. The declared tau
intentionally accepts some spans shorter than D by at most approximately tau;
this is not a new bug by itself. For nominal-grid/binary rounding comparisons use
a preregistered1e-10 boundary band: if exact reference outputs at D−1e-10 and
D+1e-10 agree, candidate indices/labels must match EXACTLY (no relaxed index
allowance). If they differ, label the case gray/undetermined and do NOT count it
as conformance. All ordinary/exact-duration cases lie far inside tau's margin.
Record a separate near-tau-boundary sweep; do not demand arbitrary universal
translation invariance within floating gray zones or quietly change the rule.

## Fixed finite checks

1. Exhaust all512 Boolean patterns of length9, durations0.5,1.0,1.25, at origins
   0.01 and100.01 on half-unit grids. Compare H/R/V/class, any/sustained helpers,
   source input preservation, and logical union/precedence identities.
2. On the actual640-point saved grid, test EVERY valid translated start at
   D=17.5 and35.0: exact-minimum-length true blocks and one-step-short blocks.
   Also test representative nominal holds17.502917152858814*rho at
   rho=(.5,.75,1,1.5,2), using starts0,1,32,100,middle,last (deduplicate as needed),
   minimum qualifying blocks and one-step-short blocks. Include all-false,
   all-true, final-sample-only, initial retention, later recovery and tail-only
   fixtures with insufficient confirmation support.
3. Separate policy stress sweep: durations17.5+f*tau for f=(-2,-.5,0,.5,1,2),
   all605 candidate starts of a17.5 block. Record robust versus gray outcomes,
   not a universal floating-point guarantee. Include a tiny positive duration
   below tau as a documented policy-extension stress case, not a normal caller.
4. Exercise actual compute_recovery on a fully synthetic40-seed ×5-rho ×4-branch
   scaffold, generated in a temporary directory. Continue reference stays at.5;
   target=.45; reset_ema uses four archetypes:10 always true,6 initially false
   then held,14 initially held then later dropped/recovered,10 never held.
   Held runs last comfortably beyond all specified holds. Source should produce
   19200 event rows/1600 AUC rows; verify selected rows versus independent masks,
   source interactions11520 rows, full-cohort/complete-case fields and summaries.
   To avoid a vacuous all-zero DID check, shift reset_B masks by10 saved samples
   at nonbaseline rho, leaving reset_ema's planned cohort unchanged. Require a
   nonzero full-cohort and a nonzero complete-case raw DID positive control.
   This calls compute helpers on synthetic Run objects, NOT full validate_run,
   artifact/provenance checks, production feasibility or all run_analysis stages.
5. For that fixed cohort, expected rates R=.6,V=.5,H=.75,overlap=.35;
   classification-recovery=.15. V among ever-dropped seeds is20/30, NOT the
   full-cohort.5. Source rec_time is branch-relative retrospective onset, NOT
   time since first drop; confirmation time is later by the hold/grid rule.
   Capture onset, first drop, confirmation and branch-relative/after-loss times.
6. Actual pointwise_summary with512 joint seed draws, seed2026090406: all-zero,
   all-one, one-finite and all-missing groups. Record degenerate intervals,
   effective n and independently calculated empty/valid bootstrap counts.
   These are fixed-cohort resampling diagnostics, not population-valid boundary
   CIs; no coverage claim or real S01 group count is being established here.

## Numeric comparison allowances (also before execution)

Index/label/Boolean agreement is exact. Timestamp fields use the declared saved
array exactly. Normalized ratios/means/DID allow absolute5e-13,relative0;
independent loop-trapezoid AUC allows absolute5e-12,relative0 for640 terms.
These are not tolerances for event indices or a way to promote gray cases.
Keep mismatches/logs rather than enlarge these allowances after seeing results.

## Strongest wrong-model controls

The harness must detect at least one witness for each admitted wrong model:
zero tolerance/addition miss; double-sized hold requirement; retention-only
substituted for any held; recovery incorrectly includes initial retention;
recovery incorrectly discards later recovery after an initially held run;
retention defined as initial True alone; classification gives recovery precedence;
onset mislabeled as confirmation; recovery flags treated as an exclusive class.
Use small predetermined witnesses and actual-source in-process substitutions,
restored after each. Do not accept a dependency/import failure as a detected
mathematical/semantic mutant. Snapshots/oracle inputs precede candidate calls;
never let a mutable call move the expected answer with the observed input.

No assertion-based acceptance decisions that disappear under python -O. Run the
owned suite normally and optimized. Confirm acquired source files unchanged.
No Lean installation/compilation is planned for this software/estimand audit.
No claim that all640-bit paths, all floating schedules, or every analysis stage
have been proved correct. A limited qualified synthetic review is an acceptable
outcome; do not force a new defect or silently freeze/promote the candidate.

## Handoff acceptance

Produce a numbered standalone report with full critical source/oracle code and
essential results inline; extract/run it with verified public dependencies.
Provide a proposed machine-readable ESTIMAND_CONTRACT as review aid, not a
registered new scientific estimand or changed production output. Keep original
labels/review scope separate:94 prior Lean compilation/footprint confirmations
are not review of these new controls. Main/frozen v4/candidate sources untouched.

Update root state/queue/ledger from observed outcomes only; current main named
exactly. Metadata minimal from acquisition, including no author/contact/signed
payloads. Unpack/index all cited logs in the outgoing bundle. No remote push,
PR, direct inbox/salvage merge, registry edit, bot contact or automatic upload.
