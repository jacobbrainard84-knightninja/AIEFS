# Cycle 004 preregistration — complex EMA, reported coherence, and drive

Agent: Researcher 040282. Date: 2026-09-04 (Atlantic/Reykjavik).
Status at writing: proposed statements; no candidate proof or numerical test run.

## Source refresh and rationale

Read-only refresh: 27 selected main files at ad58a46ae8da79c19b5484762363eb2e9f2f7923
and eight intake/navigation files at 5c1ffed0377c4769154e9342464ce7265cf1c599.
Searched all 14 active-project Lean files plus five historical Lean fixtures;
none supplies the EMA/coherence component. No 040282 feedback found in this
selected refresh. This is not a complete audit of branches or assignments.

The prior bridge supplies a weight-component model and conditional per-edge
OFF/ON results. This cycle supplies another missing actual-source component,
not a proof that the coupled phases satisfy infinite-tail bands. Do not claim
that range bounds alone provide sharp ON certificates, phase locking, or rates
for two distinct coupled trajectories. Registry S11 already cautions against
unconditional homogeneous decay of directed complex differences.

Source: aief_experiment_engine_v1.py:162–164, 707–708, 721–752.
compute_R reads theta and history[0], computes directed complex inputs, mutates
coherence_acc in place by EMA, then reports the mean of forward/reverse
magnitudes, with diagonal reset. It does not symmetrize/zero the accumulator.
The returned R is based on the UPDATED accumulator, not its previous value.

## Exact-real proposed model

For arbitrary index type I (finite only for row bounds), real alpha, complex
matrix C, real theta/delayed/omega vectors and real tau:

- phi_ij = theta_i - delayed_j - ((omega_i+omega_j)/2)*tau.
- z_ij = exp(i*phi_ij), so |z_ij|=1.
- Cnext_ij = alpha*C_ij + (1-alpha)*z_ij.
- R(C)_ii=0; R(C)_ij=(|C_ij|+|C_ji|)/2 for i!=j.
- Returned R at the nth call from initial C0 is R(C_{n+1}). A sequence indexed
  by C_n before a call instead reports R(C_n); keep that distinction explicit.
- alpha=exp(-dt/Tw) has 0<alpha<1 in real arithmetic for dt,Tw>0.

Proposed load-bearing proofs:

1. Unit-disk preservation for alpha in [0,1], |C0|<=1 and |z_n|<=1, including
   both endpoints. Derive this for the actual phase-input expression without
   requiring complex C symmetry or a zero complex diagonal.
2. Reported R is nonnegative, symmetric and zero-diagonal for any C, and <=1
   under the unit-disk invariant. A reverse-triangle Lipschitz bound controls
   changes in R by the two directed accumulator changes.
3. Exact FORCED difference law with term (1-alpha)*(z-w). Only for identical
   entire supplied input sequences may differences decay homogeneously as
   alpha^n*(C0-D0). Prove a corresponding reported-observable bound if practical.
4. Fixed-input closed form C_n=z+alpha^n*(C0-z). From C0=0 and |z|=1,
   |C_n|=1-alpha^n for alpha in [0,1]. Conditional convergence for alpha<1;
   alpha=1 is not a forgetting/convergence-to-input regime. Constant phase
   offsets of any angle give unit limiting magnitude, not cosine similarity.
5. For gamma>0, eta,mu>=0, u=((eta+mu)R-mu)/gamma lies in
   [-mu/gamma,eta/gamma]. Its off-diagonal positive-drive row (using the prior
   bridge's actual definition) is <= (card I - 1)*(eta/gamma). Prove symmetry
   and u_ii=-mu/gamma, not a zero drive diagonal. Reuse the previous sources
   unchanged if needed to avoid silently introducing a different row model.

These are component/model proofs, not formal semantics of NumPy, float64
rounding, the history-buffer invariant, phase integration, or closed-loop
locking. Counts of helper declarations are not a scientific acceptance target.
Compiler/axiom checks will use the recorded public project toolchain. No sorry,
admit, native_decide, or extra axioms in accepted sources. Allowed footprints:
propext, Classical.choice, Quot.sound only. Independently recompile any reused
local/upstream module needed by the new bridge; give existing proofs credit.

## Strong falsifiers and nonvacuity

Before compiling, target these wrong variants:

- Drop alpha<=1: alpha=2, C=1, z=-1 gives |Cnext|=3.
- Drop alpha>=0: alpha=-1 with the same C,z gives |Cnext|=3.
- Drop the input norm condition: alpha=1/2, C=0, z=4 gives norm 2.
- Drop equal-input hypothesis in difference decay: alpha=1/2, C=D=0,
  z=1, w=-1 gives nonzero next difference despite zero previous difference.
- Apply magnitude AFTER averaging complex directions: C01=1,C10=-1 gives
  actual reported R01=1, not |(C01+C10)/2|=0.
- Confuse reported zero diagonal with complex zero diagonal: C0=0, z=1,
  alpha=1/2 makes the complex diagonal 1/2 while reported diagonal is zero.
- Demand strict forgetting at alpha=1: every C_n remains C0.
- Treat coherence magnitude as cos(phi): constant unit input -1 has limiting
  magnitude 1, not -1. Anti-phase is coherent in this observable.

Use false-math Lean cases that fail for mathematical reasons, not missing
imports/instances/APIs. Test a proof hole and new axiom that raw-compile but are
policy-rejected, and missing requested axiom coverage. Reject Python -O/-OO.

Independent exact finite checks will use Gaussian rationals (pairs of Fraction)
and norm-squared inequalities, avoiding floating square roots for disk tests.
Planned seed: 20260904. 64 shared-input and 64 fixed-input scalar trajectories,
16 steps each, alpha covering 0,1 and interior/near-endpoint values; 120 finite
matrix/drive cases across N in {1,2,3,6,12}. Include zero/nonzero initial states,
unit-circle Pythagorean inputs, eta/mu zero endpoints and positive gamma.
Check each listed falsifier with a stated expected direction. These finite
checks are not the universal proof. Preserve failures and narrow claims if a
valid counterexample is found; do not relax a tolerance to obtain a pass.

## Separate source-comparison protocol

See SOURCE_COMPARISON_PLAN.md, also written before its first execution. It will
exercise ACTUAL compute_R without replacement and compare both updated complex C
and returned R to an independent loop/cmath oracle. No coupled trajectory claim,
production horizon regeneration, upload, registry change, or outreach is planned.

## Handoff

Create a numbered standalone Markdown with complete critical Lean/checker/source
comparison code and essential actual evidence inline. Execute code extracted
from that Markdown in a fresh directory, with public dependencies. Record that
as local self-reproduction, not independent-seat review. Preserve previous
packets, update local ledger/STATE/queue, and present the audit for owner upload.
