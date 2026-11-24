# AIEFS_WindowMax — window non-expansion, general N and delay

**Status:** prepared locally for owner deposit; not deposited, independently reviewed, pushed, or promoted. Main base `7865ab19282ceae49df9aa70b396d60ada38d3c2`. DIRECTION-14 reports acceptance of TransientParameter at inbox commit `f81d9fd`; that report is an external review, not a build I ran. Folder date follows the UTC clock (`date -u +%F`).

## Lean results

Let n≥2, d≥0, c=dt·b and let v(k) be the scalar amplitude at history age k. The update is

- `next(v)(0) = (1−(n−1)c)v(0) − c v(d)`;
- `next(v)(k) = v(k−1)` for k>0.

`reference_link` proves that for every n≥1, d, real dt and positive b, every mean-zero spatial vector m, every history age k and node i, this update times m(i) is the directional derivative of main `EngineStepRef.phaseStep` along the direction v(k)m(i). Its synchronized reference orbit has Ω=0, common θ=1 and ω=0. It uses both `phase_step_head` and `history_derivative`; no import of the earlier inbox candidate is needed. It is a fixed-weight, exact-real directional statement, not a full engine refinement.

`coefficient_bound`, `window_step`, and `window_all_steps` prove for n≥2, d≥0, **0≤c≤2/n**, and any nonnegative M bounding every initial slot 0,…,d, that **every retained slot at every subsequent time** remains bounded by M. Thus, choosing M as the initial window maximum gives max-norm non-expansion. This is non-expansion, not strict decay. The proof avoids requiring an actual maximum operator: the pointwise cap implies the max statement on the finite window.

For n=3, d=1, `exact_growth_witness` proves for 2/3<c<1 that initial amplitudes v(0)=v(1)=1 (and all other v(k)=1) have initial window max 1 and first head magnitude exactly `3c−1>1`. With m=(1,−1,0), the spatial vector is mean-zero, so this is a genuine growth witness for the reference-linked mode, not growth from merely copying a slot. c=0 still has gain 1 in this norm.

## Threshold and exact gain: independently checked algebra

For n=3,d=1 the induced max-norm gain is the largest absolute row sum,
`max(|1−2c|+|c|,1)`. For nonnegative c, this is 1 on [0,2/3] and `3c−1` above 2/3. The Lean witness attains the latter. The full operator-norm identity is this hand argument, **not a separately formalized equality**. For general n≥2, d≥1 the head row has sum `|1−(n−1)c|+c`, the shift row has sum 1, and the nonnegative-c non-expansion threshold is exactly 2/n. At d=0 the head and delayed coordinate coincide, so this row-sum sharpness argument does not apply; the Lean non-expansion theorem still applies, but does not claim its threshold is necessary there.

## Read-only engine comparison

Main `aief_experiment_engine_v1.py` SHA-256 `ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede`: L63–68: N=12, dt=0.01, τ=0.5 and heterogeneous natural frequencies; L77: B initialization scale 0.0005; L95: d=50; L322–338: default config; L699–705: random initial phases and random symmetric B with zero diagonal.

For a hypothetical homogeneous frozen b at that scale, c=0.01·0.0005=0.000005, well below 2/12=1/6, including d=50. This is a conditional ideal-real comparison only. Actual engine B is heterogeneous and changes, phases/frequencies are not the synchronized Ω=0 orbit, and the report did not run the engine or prove this scalar mode invariant there. Hence the result is relevant to an idealized engine-scale parameter, not a certified bound for actual engine trajectories or the full Jacobian.

## Build and targeted mutant

Lean 4.33.1: `lake build AIEFGateCore.WindowMax` passed 2,149 jobs, exit 0, no warnings. The five new axiom reports list only `propext`, `Classical.choice`, `Quot.sound`. No `sorry`, new axiom, `admit`, `unsafe`, `native_decide`, or `implemented_by` in final source. An initial failed proof was corrected; it is not the final build.

`make_mutant.py` changes only `next`'s delayed-term sign from minus to plus in a scratch copy. `lake env lean AIEFGateCore/WindowMaxMutant.lean` exited 1: the general reference link, window proof, and exact witness fail to elaborate. The mutant log has `sorryAx` because those mutated declarations failed; the unmutated build has no such dependency. This is a targeted definition mutation, not the project's full mutation suite.

From the package directory, using a main checkout with its mathlib dependencies built:

```sh
cp WindowMax.lean "$REPO/lean/AIEFGateCore/AIEFGateCore/"
python make_mutant.py WindowMax.lean "$REPO/lean/AIEFGateCore/AIEFGateCore/WindowMaxMutant.lean"
cd "$REPO/lean/AIEFGateCore"
lake build AIEFGateCore.WindowMax
lake env lean AIEFGateCore/WindowMaxMutant.lean  # expected exit 1
```

Logs and `SHA256SUMS.txt` accompany this note. No full gate or independent review is claimed.
