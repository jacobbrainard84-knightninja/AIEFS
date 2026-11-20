#012 source correspondence and numbered011 clarification

## A. Exact read-only target and current team context

Current selected main is543e7e1aaa11e4c810783806cb180eee36ec5313,42retained main
texts. Full119493-byte ART-0702 Frozen engine is imported intact; no copied/
extracted/replaced source functions or frozen source/registry/lock edit. Other
recent successors/guards/gate packages only read as coordination, not executed.
Four standalone public dependencies: engine, Frozen artifacts.csv, source Lean
prescription, lake-manifest. Metadata identifiers are scope/reproduction, not a
canonical-copy/version finding.

Current main contains Gate P1/P2; active public PR24 P3 uses R FROZEN, controller
fiber/branch persistence, not moving-phase/EMA tracking. E19-E21 new-file F4/F6/F7
successors/errata/tests and E24-E26 trust-guard work now landed, per current tree/
errata. Historical own005-009submission installation statuses are not a statement
of current absence. Contributor002 genuine S01 validator positive/forgeries
reproduction is its scope, not our009harness or010/011/012approval. No authentic
S01, candidate validator/CLI or production simulation executed by012. New entrypoint
proposal/evidence read only, no contributed checker or reproducer fetched/executed.
E22 rate-law sweep already performed, label still UNEXPLAINED; do not duplicate.
Dated briefings can lag current refs; inspect relevant current tree and PR scope.

## B. Numbered clarification to011, without changing delivered evidence

011 SOURCE_CORRESPONDENCE table (and its inline report copy) overstated
DynamicState.validate as checking B "structure/gap". Actual584-679 checks state
N, history length D+1/vector shapes, theta/B/C shapes, finite arrays, B symmetry,
diagonal and nonnegativity. It checks neither capacity/gap nor initialized
history reachability/newest==theta. Runtime advance's825-828post-gate check
computes g_min and enforces g_min>=delta-FROZEN_GAP_TOL.

This012correction is a new numbered follow-up, not an in-place edit of011report,
source/evidence or claims.011generic history/phasor proof does not require Python
validation to guarantee capacity;011finite row-capacity checks explicitly ran
separately. Its scientific code/results/ledger labels unchanged and not rerun.
012tracking theorem also does not assume an initial or validation-certified gap.

## C. Time-index map: what actual advance n does

| Source | Mathematical object / tested role |
|---|---|
| ModelConfig155-174,178-237 | alpha=float(exp(-dt/Twindow)), capacity and D; positive dt/tau, exact D*dt=tau force source D>=1. Alpha validation is0<alpha<=1, not strict<1. |
| DynamicState584-679 | copies synthetic arrays, validates structural/finite domain as sectionB; no initializer call in012. |
| compute_R721-752 | reads old theta_n/H_n[0], z_nij=exp(i*(theta_ni-H0_j-((omega_i+omega_j)/2)*tau)); writes directed C_(n+1)=alpha*C_n+(1-alpha)*z_n; magnitude THEN symmetric R/diag0. |
| advance755-844 | R_(n+1) from NEW C first, B Euler/clip/symmetry/conditional gate, post-gap check; NEW gated B in phase sin(H0_j-theta_i); modulo; append theta COPY/pop. |
| phase830-839/history841-844 | u_ni=dt*(omega_i+sum_j B_(n+1,ij)*sin(H0_j-theta_ni)); wrapped x_(n+1)=W(x_n+u_n), reachable constant initial history supplies exact lag. |

Source return R_physical is reportedR(C_(n+1)), NOT reportedR(C_n).
One call n consumes z_n, not z_(n+1).10calls per trace expose old-state arguments
for z0..z9 and C0..C10. Current-input e_n=C_n-z_n is checked n0..9; consumed-
input post-error r_n=C_(n+1)-z_n is checked n0..9; next-current recurrence n0..8
needs two observed inputs. We do NOT claim C10-z10 from a nonexistent eleventh read.

## D. Formal composition, not another assumed lock premise

Unchanged004 CoherenceEMA supplies actual-shaped emaStep/emaTrajectory/phaseInput
and reportedR_lipschitz. Unchanged011 PhaseIncrement supplies wrapped trace and
startup-aware unit phasor motion; unchanged010 HistoryBuffer supplies reachable
oldest. Recompile22+3+3prior claims as explicit dependencies, NOT28new labels or
reruns of historical scientific suites.

New delayedPhaseInput is defined using004.phaseInput on011.phaseTrace and010oldest.
Inside the new proof it is DEFINITIONALLY the011.inputPhasor; equality is not an
assumed axiom or input hypothesis. Thus composition really compiles, unlike011's
then-future004interface integration. New three named claims:

1 tracking_error_step: e_(n+1)=alpha*e_n-(z_(n+1)-z_n), ALL real alpha.
2 tracking_error_budget, alpha>=0: ||e_n||<=alpha^n||e0||+
   sum_(k<n)alpha^(n-1-k)||z_(k+1)-z_k||.
3 delayed_phase_tracking_budget, alpha>=0: replace each variation by
   |u_ki-L_kj|, L=0startup k<D, else u_(k-D,j).

The newest input variation has weight1, not alpha or1-alpha. Initial error is
not discarded. No small-variation, convergence, complete coupled-map or locking
conclusion in the hypotheses. Alpha may be0,1or>1 abstractly; nonnegative finite
budget remains valid. Source-valid alpha>0, source D>=1; abstract0 not a source
run. Mathematical D0 carried by inherited theorem, not a positive-tau config.

Uniform M gives only paper M*sum alpha^r. Division by1-alpha and asymptotic decay
requirealpha<1; even then nonzero M gives an error floor, not exact tracking or
phase locking. Reported-R bound offdiag follows004lipschitz/unit phasors and
r_n=alpha*e_n: |R_(n+1,ij)-1|<=alpha/2*(B_nij+B_nji); diagonal0. Paper+finite
check, not an extra newly compiled R/freeze/rate-law theorem.

## E. Floating endpoint is real evidence, not a refutation of real exp

Synthetic N1,D2,dt.125,Twindow1e20 yields source float alpha=1, accepted by its
validation. C0=.3+.4i remains EXACTLY unchanged for10calls. With late input near1,
observed late error0.8062257748298549. Do not apply ideal real
physicalAlpha(dt,Tw)<1 directly to rounded source values, or infer strict
contraction/convergence from alpha<=1. This is an extreme synthetic numerical
boundary, not a defect finding about production cohorts or a universal infinite-
time floating trajectory statement. The formal finite theorem needs no1-alpha
inverse and covers this numerical coefficient as a real parameter.

At alpha1 no C innovation can identify z: (Cnew-alpha*Cold)/(1-alpha) is undefined.
Our10endpoint inputs are explicitly reconstructed from copied observed pre-state
arguments via pure math, NOT decoded or directly returned by engine. Constant C,
phase/history/scalar state and error relations still checked. Other360input
coordinates have both argument reconstruction AND actual C-innovation decoding,
with fixed beta>=.05. No division by0, hidden fallback/skip or false detection.

## F. Independence, finite counts and falsifiers

All6expected full traces AND370derived error/budget/unroll cells completed before
acquired module import in each worker. Pure math/cmath independent scalar dynamics;
expected history never assigned from target, analytic max(0,n-D) input lag,
expected u uses predicted NEW gated B, no pre-call mutating compute_R.

Observed snapshots/actualC innovations are measurements, not expected values.
Relational checks using observed e/delta are additionally compared with independent
precomputed predictions. Frozen input tuples/cells, copied actual data, ownership
and RNG preserved. No initializer/run_seed/simulate_*/shuffle/baseline/S01/CLI/
writer/certificate call or source function replacement.

Per normal/-O common suite:9methods/60actual advances/6cases;370current errors,
370consumed errors,333adjacent recurrences=115startup+218live,37first-live;
240offdiag R bounds/130diag0;360decoded inputs+10explicit alpha1formula-only.
Fixed abs5e-13/rel0, one-sided bound slack same; finite shape/real/imag checked
explicitly. Source ZERO1e-12/PROJECTION_NORM1e-14/GAP1e-9 distinct constants.
Observed max source/scalar error9.992007221626409e-16; causal/unroll4.440892098500626e-16,
consumed2.220446049250313e-16;245nonzero phase-budget checks below2;12tight nonzero
R bounds below1. Two alpha<1stationary tails decay finitely as predicted, not
proof of coupled phase locking. Alpha1C constant/non-decay separate.

Ten wrong models are independent references, never injected source variants.
Equality models need intended component residual>1e-7; wrong upper bounds need an
actual positive violation>1e-7, NOT merely disagreement with another safe bound.
Eight formal controls: alpha0/1nonzero positives, beta-scaled drift/reversed weight/
dropped-nonnegative false math reduced to explicit False, compiling sorry/extra
axiom/missing-print policy refusals. Unknown identifier/import/setup/timeout
failures block, never semantic detections. Fixed-owned-source integrity policy
not arbitrary-source sandbox or security certificate.

Initial new proof had two additive-helper orientation type mismatches; use explicit
componentwise add_le_add/reflexivity. Statements/coefficients/domains/cases/tolerance
unchanged. Failed draft/log retained, not a falsifier or promoted build. All28old
component claims and corrected3main claims compiled clean; final full-run controls
and actual extracted repetition still required for closure/promotion.
