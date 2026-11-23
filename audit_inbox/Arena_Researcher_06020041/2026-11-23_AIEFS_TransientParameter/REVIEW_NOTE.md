# AIEFS_TransientParameter — stable range and one-step gain

**Status:** prepared for owner deposit; not deposited, independently reviewed, or promoted. Base main `7865ab19282ceae49df9aa70b396d60ada38d3c2`; inbox checked at `b3cca7b5d46a380966f0e3daedf5e9f508576f83`. Folder label from `date -u +%F`; the container reported `2026-11-23 22:38:21 GMT`. Imports only main `EngineStepRef` and `DelayRoots`; no inbox candidate, project file, CI, root import or prior deposit was edited.

## Ran: Lean results

For N=3, d=1, Ω=ω=0, synchronized phase 1, a common positive off-diagonal b, and arbitrary dt, `reference_mode_link` proves both derivatives of main's `phaseStep` on the mean-zero spatial mode `(1,−1,0)` are represented by

`A(c) = [[1−2c, −c], [1, 0]]`, where `c = dt·b`.

This is a directional-derivative link to main's exact-real fixed-weight reference, not Python refinement or a full adaptive Jacobian. `eigenmode_stable` proves that for `0<c<1` every eigenvalue of this complexified two-slot map has modulus strictly less than 1; `stable_roots` directly handles the full interval, including `c ≥ 1/2` which is outside the sufficient range of main's existing `DelayRoots.transRoot_lt_one` for m=2. A separate direct probe shows c=0 has root 1.

`one_step_bound` proves for all real x,y and `0 ≤ c ≤ 1`:

`‖A(c)(x,y)‖² ≤ (21/8) ‖(x,y)‖²`.

Thus the **one-step** gain is at most `G=√(21/8) ≈ 1.620185`. This is near-tight but is not an all-k bound. `quarter_probe` directly checks the prior 5/4 squared-energy witness at c=1/4.

## Exact range and peak — independent hand argument, not Lean-checked

The strictly stable range of `A(c)` over all real c is exactly `0<c<1`. Lean proves the sufficient half. For necessity: if c≤0, the real polynomial `p(t)=t²−(1−2c)t+c` satisfies `p(1)=3c≤0` and tends to +∞, so it has a real root at least 1. If c≥1, the product of its two complex roots is c, so they cannot both have modulus <1. These necessity arguments and root existence are **not formalized in this file**.

Let `T(c)=2−4c+5c²`. Direct eigenvalue calculation for `A(c)ᵀA(c)` gives the exact one-step squared gain

`[T(c)+√(T(c)²−4c²)]/2`.

The supremum over the open stable interval is the golden ratio `φ=(1+√5)/2 ≈ 1.618034`, approached as c→1 from below, not attained inside it. Reason: `A(c)=(1−c)A(0)+cA(1)`; the operator norm is convex, `‖A(0)‖=√2<φ`, and `‖A(1)‖=φ`. Continuity gives the endpoint limit. This exact formula, convexity argument and supremum are mathematical reasoning, **not Lean theorems** in this deposit.

## Falsifiable all-time claim — tested, not proved

Claim: for every `0<c<1` and every integer `k≥0`, `‖A(c)^k‖₂ ≤ G=√(21/8)`. The Lean bound above proves only k=1; it does **not** prove this all-time claim. `grid_probe.py` ran 999 values c=0.001,…,0.999 and powers k=1,…,100. The largest observed norm was `1.6161400134670594` at c=0.999, k=1; the finite grid passed the threshold. This is not proof for untested c or k, and no engine trajectory was run. The printed result is preserved in `grid.log.txt`.

## Read: engine defaults and scope

At the cited main engine, L64–68 set N=12, dt=0.01, τ=0.5 and heterogeneous frequencies; L70–77 give the physical constants and initial B scale 0.0005; L322–338 construct the default config; L702–705 initialize a random symmetric B. Default delay is d=50 (L95). Therefore the actual defaults do **not** specify a single common b or this N=3,d=1 synchronized model, and it would be misleading to assign them one c or to say the engine lies in this model's stable range. As a conditional arithmetic comparison only, if a uniform b were in `(0,0.0005]` with dt=0.01, then `0<c≤0.000005<1`; this does not establish such an engine state or orbit.

## Ran: mutant and verification

A scratch copy changed the update's history coordinate from `p.1` to `−p.1`. `lake env lean AIEFGateCore/TransientParameterMutant.lean` exited 1: `reference_mode_link` no longer matches main's history derivative. This is a targeted definition mutant, not an engine or project mutation-suite run. `sorryAx` in the failed-elaboration mutant log is not a final-source axiom.

Lean 4.33.1: `lake build AIEFGateCore.TransientParameter` passed **2,213 jobs without warnings**. Six candidate axiom reports contain only `propext`, `Classical.choice`, `Quot.sound`; final source has no `sorry`, `admit`, new axiom, `native_decide`, `implemented_by` or `unsafe`. Earlier failed builds were corrected before the final build. `.log.txt` files and `SHA256SUMS.txt` are included.

```sh
cp TransientParameter.lean "$REPO/lean/AIEFGateCore/AIEFGateCore/"
cd "$REPO/lean/AIEFGateCore"
lake build AIEFGateCore.TransientParameter
# Scratch copy with history-coordinate sign replaced as described:
lake env lean AIEFGateCore/TransientParameterMutant.lean  # expected exit 1
python grid_probe.py  # from this package directory
```

No all-k continuum proof, full gate, Python-engine run, independent review, push or promotion. The previously proved all-step bound at c=1/4 does not automatically extend to other c.
