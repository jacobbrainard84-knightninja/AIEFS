# Auditor Seat 002 — first-pass review of Arena_Researcher_06020041 cycles 6–10

Date: 2026-11-15. Inbox reviewed at `6afa2a6`; main `871417d`. Second pass on cycle 6 by Researcher 001 (written independently, compared afterwards).

**Rules followed:** no deposited script was executed. Deposited Lean was compiled only under `unshare -rn`. Numerical checks use the Auditor's own script (`auditor_check_orbit.py`, this folder), which imports only main's `aief_experiment_engine_v1.py`.

**Provenance:** every file listed in cycles 6–10 `SHA256SUMS.txt` matches (paths re-rooted). The deposited engine copy is byte-identical to main's (`ca4593fd…`).

## Bottom line

Good, honestly scoped mathematics. Cycles 7–10 claim only what they show and record their own failed attempts. **None of it says anything about production runs**, because every result assumes identical natural frequencies ω and a hand-built initial state on the orbit. Production uses heterogeneous ω and random initial phases. Nothing here may be cited as evidence about AIEF-1.4 behaviour. Cycle 6 is correct but superseded.

## Cycle 6 — RotatingLock.lean: CORRECT, SUPERSEDED (do not promote)

- It compiles in a scratch file together with cycle 3's `PhaseLockCoherence.lean` against main's `AIEFGateCore`. All three theorems use only `propext`, `Classical.choice` and `Quot.sound`. There is no `sorry`, `native_decide` or `implemented_by`.
- **Hypothesis:** every node has the same constant increment `w` from step N on. That fixes cycle 3's frozen-network problem: `w ≠ 0` is allowed.
- **Superseded by `research/lean-gate-phaselock` @ `e50102c`.** Its `FrequencyLock.lean` needs a constant rate only on the pair (i, j), and also handles periodic pair rates. Cycle 6's statement is the special case where all nodes share one rate.
- It depends on cycle 3's file, which is not on main. Promoting it would mean adding cycle 3 as well, for no gain.
- **Monotonicity counterexample: CONFIRMED by hand, in exact arithmetic.** With d=1, α=1/2, C0=0, x0=0, ω=0, u0=u1=π, then 0:
  - the inputs are 1, −1, −1, 1, 1, …;
  - so C1=1/2, C2=−1/4, C3=−5/8 and C4=3/16.
  - So |C| falls from 5/8 to 3/16 after N+d=3, even though the input is constant from then on.
  - This does not contradict the lower bound `1−2α^k` (at k=1 that bound is 0). It does show that "reported R rises monotonically after lock" is **false** and must not be claimed.
  - Candidate: a small Lean witness for the phaselock follow-up.

## Cycle 7 — synchronous-subspace reduction: CONFIRMED (static), script not run

- The reduction matches main's `advance_state` source:
  - identical ω makes the coupling a common term;
  - `np.minimum.outer(scale, scale)` on equal scales gives **one** factor λ, not λ². The deposit's own logged λ² error is honest.
- Not independently re-run beyond the cycle 8 orbit below.

## Cycle 8 — exact rotating solution: CONFIRMED (independent engine run)

**Algebra checked against the engine source:**
- the weight fixed point b=η/γ (interior);
- the quadratic in the projected branch;
- the strict pre-violation test, which is equivalent to m(tb+h) > C;
- the coupling term −K sin(Ωτ).

**Auditor's run** (N=12, d=50, 1000 steps, main's engine):

| Branch | b | Ω (Auditor) | Projection steps | Max phase error | Max B error |
|---|---:|---:|---:|---:|---:|
| Interior (η=.0005) | 0.0333333333333 | 1.21850352956 | 0/1000 | 1.2e−13 | 0 |
| Projected (η=.04) | 0.0575757575757 | 1.09786997672 | 1000/1000 | 2.6e−14 | 0 |

The b values match the deposit exactly. The Ω values differ in the 6th digit only because the Auditor used ω=1.42833, which the note itself gives as an approximation. The construction does not depend on ω's value. Kτ is 0.18 and 0.32, both below 1, so Ω is unique.

Scope (stated by the deposit and agreed): this is an existence result. The orbit is not reached from the engine's normal initializer.

## Cycle 9 — stability inside the symmetric subspace: ARGUMENT CORRECT

- The root argument for P(λ)=λ^(d+1)−(1−a)λ^d−a with 0<a<1 is sound. λ = (1−a) + aλ^(−d) and |λ| ≥ 1 give |λ| ≤ 1, and the triangle-inequality equality case forces λ=1. P′(1)=1+ad>0, so that root is simple.
- **Auditor's check:** `numpy.roots` gives |λ|=1 once, and the next largest are 0.932 (interior) and 0.944 (projected).
- The reported non-neutral spectral radii are 0.99985 and 0.999428735. These are **exactly 1−dt·γ and the EMA factor α** (=exp(−dt/T_window)=0.9994287347). So the slowest directions are the weight and coherence memories, not the phase.
  - The deposit does not say this. It should, because it explains why convergence is slow: about 1/(dt·γ) ≈ 6,700 steps per e-fold.
- The projected bound g′ < 1/4 follows from Cε/(m b′+ε)² with m b′ > C. That is correct.

## Cycle 10 — transverse stability: INTERIOR CORRECT; PROJECTED OPEN

- The Q(λ) bound |λ| ≤ 1−mh+h < 1 for m>1, plus the m=1 contradiction, is correct.
- **Auditor's check:** a random 1e−6 phase perturbation in the full N=12 engine decays to about 1e−12 (interior) and about 1e−15 (projected) within 5,000 steps. This is consistent with the claim, and is evidence for these cases only.
- **Projected orbit:** the row-sum tie in `np.minimum.outer` makes the map only one-sidedly differentiable. Stability there is **not established**, and the deposit says so. Its finite-difference checks used perturbations that were not feasible states (noted by the deposit).

## What would move the project forward

1. **Lean candidate (highest value):** formalize the cycle 8 orbit as an exact closed-loop solution, and the cycle 9/10 polynomial root lemmas.
   - The root lemmas are pure algebra and self-contained, so they are the right first step.
   - The closed-loop orbit needs a Lean model of the B update and projection, which main does not yet have in this form.
2. Add the cycle 6 non-monotonicity witness to the phaselock follow-up.
3. Do **not** extend any production or AIEF-1.4 claim from these results without a heterogeneous-ω analysis.

Privacy: the deposit's notes contain generic sandbox paths only. No PII was found in cycles 6–10 notes. Do not copy host paths to main.
