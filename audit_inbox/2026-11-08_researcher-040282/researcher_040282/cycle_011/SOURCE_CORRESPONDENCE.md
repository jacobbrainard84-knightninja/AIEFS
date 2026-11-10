# Source correspondence and proof boundary —011

## Read-only source and timing

`source_state/main/aief_experiment_engine_v1.py` is the119493-byte entire reviewed
ART-0702 Frozen module, acquired/verified before preregistration, imported intact
by `load_reviewed.py`. Registry/lock acknowledgement is a scope restriction, not
permission to patch a frozen file. No copied/extracted/replaced source functions.
The independent owned math/cmath scalar specification is explicitly separate.

| Actual source location | Exact role in this cycle |
|---|---|
| ModelConfig properties172–174/validation through237 | positive finite dt/tau, D=round(tau/dt), exact D*dt=tau; hence source D>=1. Frequencies finite, not required positive. All7configs satisfy. |
| DynamicState584–679 | validates finite shape/history length D+1 and B structure/gap; does not certify history reachability or newest==theta. Our synthetic initial histories are separately constant and thereafter independently shadowed. |
| initialize_state686–718 | historical justification of constant-prehistory convention; NOT called in011. We construct7synthetic states; random production initializer not claimed to output them. |
| compute_R721–752 | reads OLD theta/history[0], input exp(i*(theta_i-H0_j-((omega_i+omega_j)/2)*tau)), directed C EMA, THEN magnitude, THEN symmetric R/zero diagonal. Mutates C, so never pre-call for expected values. |
| advance_state755–856 | C/R update first; B Euler/clipping/symmetry; strict g_min_pre<delta conditional capacity gate; phase from NEW gated B using sin(H0_j-theta_i), no mean-frequency offset in that sine; modulo; append theta COPY/pop oldest. |
| phase update830–839/history841–844 | real mathematical shape x_(n+1)=W(x_n+u_n), u_ni=dt*(omega_i+sum_j B_(n+1,ij)*sin(H0_j-x_ni)); source B_(n+1) means post-step/gated B. Delayed historical u_(n-D,j) uses that historical step's own post-gate B, not current B. |

No shuffle; same supplied RNG unchanged. No run_seed/simulate_*/full baseline/
intervention/production/CLI/writer/certificate or authority-validation call.

## Universal exact-real theorem, not floating equivalence

Owned `HistoryBuffer.lean` is unchanged010 reusable dependency; its three Std
claims are RECOMPILED, not three new ledger claims. `HistoryTrace` starts with
constant x0 and shifts/appends x(n+1), so H_n[k]=x(max(0,n+k-D)). New
`PhaseIncrement.lean` defines actual floor wrap W(t)=t-floor(t/(2pi))*2pi and
arbitrary unwrapped increment trace u. New claims:

- `Researcher040282.Phase.phasor_wrap`: E(W(t))=E(t).
- `.delayed_input_step`: z_(n+1,ij)=z_(n,ij)*E(u_ni-L_nj), where
  L_nj=0 for n<D, else u_(n-D,j).
- `.delayed_input_chord_bound`: ||z_(n+1,ij)-z_(n,ij)||<=|u_ni-L_nj|.

z_n uses the D+1 queue's oldest value, exact source-shaped mean-frequency offset
and E(t)=exp(i*t). No assumption of synchronization, small increments, convergence,
locking, freeze time, or the asserted phasor identity. The wrapped recurrence is a
definition. Arbitrary u permits feedback-generated increments, but C/R/B and a full
coupled real map have NOT been formalized/instantiated in Lean here. Module does
not import004's EMA module; its same-shaped input can be aligned in future reviewed
integration, not an already compiled end-to-end composition.

Mathlib's integer-period exponential theorem proves floor-wrap invariance; the
stock unit norm and real-imaginary-exponential Lipschitz/chord inequality give the
norm estimate. Complete three-name axiom-print coverage; allowed standard
propext/Classical.choice/Quot.sound only. No new axiom/sorry/native_decide premise.
Mathematical D0 is covered by the generic theorem but not source-valid with positive
tau. No proof of NumPy remainder/trig rounding or float/Python FFI.

For D>=1 the same delayed phasor increment can be read as E(H_n[1]_j-H_n[0]_j),
including startup repetitions; recovering the UNWRAPPED historical increment as an
ordinary stored-angle difference is invalid. That observation is a paper/value-
index corollary, NOT another new compiled declaration in this cycle.

## Constant startup is not a drifting negative-time extension

At transition n=D-1->D the oldest stays x0. It first changes on n=D->D+1,
with increment u0. Thus guard is n>=D, not n>=D-1 or n>=D+1. During startup
one must NOT subtract dt*omega_j or an initial/current delayed-node increment.

Finite N1,D3,omega1,dt.125,tau.375 example: absolute inputs z0..z7 are
E(-.375),E(-.25),E(-.125),1,1,1,1,1 (up to fixed floating tolerance),
even though stored theta wraps. Startup ratios E(.125), first live and later1.
A fictitious linearly drifting prehistory would erase exactly this startup.

Mean-frequency offset is static for a pair: it cancels between consecutive z's,
but its absolute phasor remains part of the C input/initial condition. Ratio-only
checks cannot catch omitting it. Conversely E(stored_new-stored_old)=E(u_n) is
VALID despite winding; do not count it as a mutant. Only an equality of ordinary
real stored differences to unwrapped u is wrong. No global Euclidean angle bound
is inferred from the circular chord estimate.

## Independent finite evidence design and C read order

All seven full immutable expected traces built by pure math/cmath BEFORE actual
engine import in EACH common worker. Scalar C/B/phase/history evolve only from
prior expected tuples, never observed outputs. Expected u uses predicted NEW gated
B, and expected z uses independent analytic age index max(0,n-D), not target
history contents. First/negative/multiple winding witnesses all fixed in PLAN.

Eight actual advances per trace produce C innovations for z0..z7, not z1..z8.
Observe each innovation from copied ACTUAL old C and actual new C, divided by
1-alpha (alpha=exp(-.25), safely bounded away from1). This is observed data, not an
expected value. Seven adjacent ratios n0..6 need two consecutive actual updates;
no ninth call, no pre-call mutating compute_R. Counts per normal/-O suite:
56advances,496complex inputs,434adjacent pair coordinates=157startup+277live;
62first live at n=D,215strictly later. C/B/theta/history and R outputs also checked.

Fixed abs5e-13,rel0; explicit finite real/imag/shape checks, exact bools, structure,
range, ownership and RNG/input preservation. One-sided chord/capacity slack also
5e-13, not source diagnostic thresholds (ZERO1e-12,PROJECTION_NORM1e-14,GAP1e-9).
This finite domain is not a blanket guarantee for arbitrary validated floats.

## Capacity specialization — paper + finite check, not a new formal gate theorem

If post-gate B>=0 and row sum<=c, |kappa_ni|<=c by |sin|<=1. Then for dt>=0:
startup |v_ij|<=dt*(|omega_i|+c); live |v_ij|<=dt*(|omega_i-omega_j|+2c).
No locking assumption; frequency differences, rather than a cancelled constant
phase offset, remain in the live bound. C=.6 for these configs. Numerically check
post-gate rows and both inequalities on the fixed cases. Do not equate Python's
validation tolerance with exact row feasibility for EVERY possible input. The
formal result is the signed-increment chord bound; a coupled-capacity composition
still requires separate exact-real definitions/obligations.

## Controls, setup and independence

Ten independent incorrect-factor/absolute-input/real-increment models exercise
startup, boundary, aged increment, sign, old/unprojected B, missing absolute offset,
C read time and Euclidean-winding confusion. They do not replace frozen functions.
Two nonzero formal positives; three false math witnesses must reduce to explicit
False; three compiling integrity payloads must be policy-rejected for intended
reason. Imports, setup, unknown identifiers, timeouts and proof-draft errors block
and are never mathematical detections. Fixed owned-source checker is not a generic
untrusted-Lean sandbox/security certification.

Development errors retained: initial proof's phasor-zero/cast-matching/import and
unused-tactic issues, concurrent edit overwrite, then concrete positive control's
n0 history simplification. First full attempt already passed both source modes
and10wrong models/mode and clean main proof, but its positive-control blocker did
NOT satisfy overall acceptance. Correct only own control/harness code, not source,
statements or tolerances. Independent seat approval still absent.
