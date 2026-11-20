# 010 preregistration — reachable history indices and coupled one-step source contract

Researcher040282. Prepared2026-09-04 Atlantic/Reykjavik. Session preparation label
is separate from owner/repository November labels and compiler/runtime clocks.
This plan precedes acquired-engine execution, theorem compilation and comparisons.
Source/Lean/feedback inspection and independent formula design only so far.

## Fresh source, scope and nonduplication

Main eb3933c196ee19e80e1621ae80d89ca72e6d9485;32 selected source/library/status
files. Inbox00a29ce538a40b553a723dd73dbd676129bfcd9a;8 selected notes/evidence.
Targeted R040282 intake/R001 notes/general TRIAGE unchanged. Three new public
provenance-mutation files exist; read only review/evidence, not the reproducer.
Those report copied-function mutations consistent with009; not independent review
of our companion, not a reason to duplicate provenance work in010. No new named
005–009 review/receipt in selected targeted notes. Current main Lean modules
explicitly exclude phases/delay in their scopes; keyword/header check finds no
history-buffer implementation among selected main lean/*.lean. Not an exhaustive
private theorem/coordination search. Public first100 navigation:1 open PR,
16branches, no history/delay/phase/buffer match. Open PR16 is chronicler corrigenda,
not a dynamics-buffer implementation; avoid that work and rate-law sweep/docs.

Actual aief_experiment_engine_v1.py is ART-0702 Frozen/authority-locked. Never edit
source, registry, locks or install a replacement. Full engine import allowed for
isolated synthetic primitive probes; NO run_seed/simulate_prefix/simulate_future/
run_baseline_equivalence, real study, production trajectory or certificate. Short
one/few-step SYNTHETIC microtrajectories are the test, not a campaign. Shuffle
branch/interventions/diagnostic pipeline remain outside scope. No remote writes,
PR, contact/upload or unattended011. Prior009 is complete; do not rerun it.

## One load-bearing boundary and exact mathematical statement

Source ModelConfig.delay_steps is D=round(tau/dt); validate requires tau>0,
dt>0 and EXACT D*dt==tau (rtol0,atol0), hence validated cases have D>=1.
History length must be D+1; initialize_state constructs D+1 independent copies
of theta0. compute_R and phase update read history[0] BEFORE append/pop.
advance_state uses theta_old/history0 to update directed complex C, reads R from
UPDATED C by magnitude THEN symmetrization/zero diagonal, updates/clips/symmetrizes
B, conditionally gates it, advances phase with NEW GATED B, then appends a COPY of
new theta and pops oldest if length>D+1. No separately pre-calling compute_R,
which would update C twice. RNG must remain unchanged for shuffle_driver=False.

For any value type A, delay D in Nat and arbitrary trace x:Nat->A, define H0 as
constant D+1-vector x(0). Let H(n+1)=shift-tail-and-append(H(n),x(n+1)). Prove:

    H(n)[i] = x(n+i-D), for every i:Fin(D+1),

where Nat subtraction is truncated at0. Endpoint corollaries:
H(n)[0]=x(n-D), H(n)[D]=x(n). This settles the D versus D+1 storage/read confusion
and startup constant prehistory, without assuming the lag identity in a premise.
At read time step n the delayed phase is x(max(0,n-D)), not x(n-D+1).
This is a reachable/initialization-history theorem, NOT an assertion for every
arbitrary history merely accepted by state.validate (it does not enforce last=
theta or reconstruction from a trajectory). Shift equality assumes value semantics;
Python copy-ownership is separately probed, not Lean-verified memory semantics.

Three named declarations intended: universal coordinate theorem plus oldest/
newest corollaries. Generic core Lean module, import Std only; no Mathlib or
coupled stability assumption. A=phase vectors is an intended instantiation, not a
formal Python/float FFI theorem. No phase-locking/global gate/ON/OFF claim.

## Independent scalar reference and fixed numeric domain

Immutable tuple cases; compute ALL expected outputs BEFORE source call. Pure
Python math/cmath scalar loops for phase input/complex EMA, magnitudes, row sums,
nonnegative B clipping, strict conditional capacity gate, coupling and modulo.
Do not call engine compute_R/advance_state or get expected values from their
outputs. Actual engine imported intact, constructor copies provided arrays;
advance_state mutates only a disposable working state, not immutable case data.
Use actual config/state validation before each intended transition.

Check R_physical/R_driver, C_new, B_new, theta_new, every history vector, selected
pre_violation/projection_active/g_min_pre/g_min values. No certification of other
norm/relative projection diagnostics, shuffle/intervention or production loops.
Absolute tolerance5e-13,relative0 for finite numeric fields, fixed before results;
exact shapes/flags/counts/alias checks, finite outputs and phase range[0,2*pi).
Do not adjust tolerance to turn a failure green. Compare complex components via
real/imag numeric differences, not the known whole-element-NaN helper.

Nine one-step cases: nontrivial inactive D1; active D2; active D3; zero-C/new-drive
D2; phase-wrap D1; exact-capacity N2 boundary (a1,q1,delta.5,Bedge.5,eta=mu=gamma0,
epsilon.01); negative proposal clipped to0; directed-C N4/D4; N1 dyadic drift.
Default nontrivial N3 theta(.31,1.27,4.13), omega(.5,1,1.5), oldest(5.91,.81,2.24),
Bold edges(.08,.23,.32), directed C with nonparallel/asymmetric entries. dt1/8,
tau=D/8, Tw.5; a1,q1.5,delta.1; active eta3,mu.05,gamma.2,epsilon1e-12. Values
chosen from the scalar formulas BEFORE comparing source. Require active case's
correct phase to differ from old-B and unprojected-B models by>1e-7; asymmetric
R models/age/frequency/sign controls must have a>1e-7 field witness (not tolerance
fuzz). Inactive/zero/clipped/boundary cases avoid only vacuous zero coupling.

## Same nine common source methods, normal and -O

1 nine scalar-reference one-step cases, all fields above;
2 change oldest only (pair): expected instantaneous C/phase dependence, not newest;
3 change an interior non-oldest history only (pair,D2): same immediate C/R/B/theta,
   different shifted history; shows interior is latent rather than discarded;
4 five exact dyadic N1 histories (D1..5),12 advances each, theta0=.25,omega1,
   dt.125, no wrapping: exact H(n)[i]=.25+(max(0,n+i-D))*.125.65 states,
   260 stored-coordinate checks,60 actual transitions; source values bit-exact,
   expected from arithmetic trace not previously observed source phase outputs;
5 explicit new-gated-B nonvacuity versus old/unprojected models;
6 updated-C then magnitude/symmetrization nonvacuity;
7 wrap/clipping cases and output ranges;
8 independent history storage: no vector aliases another or theta;
9 validate nine configs and exact-delay domain; tau.2/.1875 withdt.125 fail for
   exact consistency, not setup errors. Domain checks counted separately, not
   wrong-model detections. Abstract Lean D0 is valid mathematics only, not a
   source config permitted by positive tau/exact consistency.

Expect nine source methods PASS/0errors/0skips, both interpreters. Planned78
actual advance_state calls per common suite (including60 dyadic transitions).
No source repair/failing-before claim:010 establishes a faithful component.

## Eleven independent wrong models, both interpreters

Newest instead of oldest; second-oldest off-by-one; individual omega_i instead
of mean(omega_i,omega_j) in C input; old C for R; symmetrize C before magnitude;
old B for phase; unprojected B for phase; reverse sine coupling sign; append OLD
theta; alias appended history to current theta; apply gate unconditionally even
at exact capacity. All numerical controls must fail intended field comparison;
alias control must fail storage_ownership. Use fixed witnesses, require distinct
wrong-model names; source remains untouched. Setup/import/timeouts are blockers,
not successful falsifiers. Normal/-O records match without timings.

## Lean/compiler and eight proof-check controls

Existing lean/lake executable and old disposable cache absent;20GB free observed.
Use prescribed leanprover/lean4:v4.33.1, core Std only. Public570405234B release
asset; verify published digest/length before selective compiler/runtime extraction
into own excluded .cache/researcher040282-cycle010. Small zstandard decoder may
be installed into that disposable target only. No global toolchain setting,
Mathlib download, old cache restoration or third-party code in packet. Remove
OWN disposable compiler/archive/decoder after actual standalone reproduction;
preserve minimal setup receipt/logs only. Do not restore deleted Lua audit.

Compiler must return0 without warnings, named theorem/axiom print coverage exact,
footprints subset{propext,Classical.choice,Quot.sound}; no sorry/admit/native_decide/
extra axioms/unsafe accepted. Preserve any development compilation errors as such,
not intended negative controls; final claim only actually accepted theorem source.

Eight formal controls: nonzero-delay positive, abstract-D0 positive; false youngest-
read, false one-extra-delay read, false append-old/current endpoint (three explicit
Nat witnesses) must fail math with no dependency/setup error; compiling sorry and
compiling added-axiom payloads must be rejected by policy; compiling omitted-axiom-
print source must be rejected by coverage. Do not count compiler/setup failures
as rejection of false math or integrity detection.

## Closeout / what must not be promoted

Full runner original/optimized engine/mutant checks plus actual theorem/control
compilation; then full inline standalone note, extract owned critical code,
fresh-fetch engine+registry/toolchain metadata (3 public dependencies) and repeat
complete runner with same disposable compiler. Compare science/non-timing child/
proof records, not timing logs. No independent approval inferred. Only after
observed success append three scoped LEAN_COMPILED rows and one executable source
contract row (expected118total,97formal labels), retaining prior114/94 unchanged.
If Lean is blocked, no compiled promotion; if source mismatch, preserve and narrow
or report blocker rather than weaken tests. All old science/state snapshots,
reports and archives unchanged, cited logs unpacked/indexed, metadata minimal.
One bounded foundation result; no011 work this turn. Owner uploads dated note.
