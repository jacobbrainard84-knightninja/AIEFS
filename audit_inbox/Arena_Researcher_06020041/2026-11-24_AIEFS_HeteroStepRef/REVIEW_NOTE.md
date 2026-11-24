# AIEFS_HeteroStepRef — heterogeneous fixed-B window bound

**Status:** prepared locally for owner deposit; not deposited, independently reviewed, pushed, or promoted. Main base verified this cycle: `7865ab19282ceae49df9aa70b396d60ada38d3c2`; `EngineStepRef.lean` SHA-256 `573adfd6d98181d5734c2293f8867236e78c55c3fe0a5bdaa8f120d4844c2666`. UTC folder label from `date -u +%F`. DIRECTION-16 and its confirmation of the blocker were supplied by the lead; I did not independently rerun the lead's review. New files are add-only; no main file, root import, or frozen evidence changed.

## Lean-checked results

`HeteroStepRef.lean` imports main's `EngineStepRef`. `phaseHeadW` and `phaseStepW` define an exact-real, unwrapped fixed-B model with each edge's weight `B i j` in the sum over `j≠i`, followed by the history shift. The definition does **not** clip weights and omits the gate, shuffle, adaptation and modulo. It mirrors the *shape* of the engine's coupling at L830–839, not a proved Python correspondence.

1. **Anti-drift.** `agrees_main` proves pointwise equality with main `phaseStep` at every node and history slot whenever every off-diagonal `B i j = clippedWeight b`. The diagonal may be arbitrary because both definitions exclude self-coupling. This is stronger than just checking a sample.
2. **Directional derivative.** `weighted_head_derivative` uses main `neighbor_derivative`; with zero diagonal it proves the requested row formula, including the general cosine `cos(d·dt·Ω)`. `weighted_step_derivative` specializes to Ω=0 and uses main `history_derivative` for retained slots. For arbitrary perturbations, the head then equals `(1−dt·rᵢ)v₀ᵢ + dt·Σⱼ Bᵢⱼv_dⱼ`, where `rᵢ=ΣⱼBᵢⱼ`.
3. **Window non-expansion.** `window_step` and `window_all_steps` prove that, for arbitrary N and d, fixed `B i j≥0`, `dt≥0` and `dt·rᵢ≤1` for each i, every node and retained slot of every iterate of the *linear model* stays within any nonnegative initial window cap M. No mean-zero assumption is used. Symmetry is not required: the theorem is stronger on that point. The derivative interpretation uses zero diagonal and the synchronized Ω=0 reference; repeating this same linear map describes the stationary synchronized fixed-B case, not an adaptive system.
4. **Guard.** `guard_row_bound` proves `δ−tol≤a−q r` and `q>0` imply `r≤(a−δ+tol)/q`. In the second file, `guarded_window_all_steps` composes this with the window theorem when `dt·(a−δ+tol)/q≤1`. `engine_constants_safe` proves the comparison using exact rational decimal values.
5. **Sharp growth witness.** `growth_witness` proves for `d≥1` and any row with `dt·rᵢ>1` that a history whose current entries are 1 and all positive-age entries are −1 has initial max 1 and head magnitude exactly `2·dt·rᵢ−1>1`. For interpretation as the weighted reference derivative, use zero diagonal. The theorem does not assert a witness for d=0, where current and delayed slots coincide.

## Read-only engine comparison and its limits

At main `aief_experiment_engine_v1.py`: defaults N=12, dt=0.01, τ=0.5 and heterogeneous frequencies at L63–68; a=1, q=1.5, δ=0.05 at L70–72; `FROZEN_GAP_TOL=1e-9` at L80; default config at L322–338; delay d=50 at L95. Proposal is clipped/symmetrized and diagonal-zeroed at L790–797; projection is conditional at L803–813; the post-gate assignment occurs at L823 and the runtime gap guard at L824–828; phase coupling reads that `state.B` at L830–839.

Under an **exact-real interpretation of the guard** and q>0, a non-raising step satisfies each `rᵢ≤(1−0.05+1e−9)/1.5 = 0.633333334`, so `dt·rᵢ≤0.00633333334<1`. This covers either gate branch and is based on the guard, not the initialization scale. These numbers are compared as exact rationals in Lean. Actual NumPy summation, multiplication and comparisons are floating-point: turning a Python non-raise into this exact-real hypothesis requires a finite-value and rounding/error argument, which is **OPEN** (in particular, a NaN comparison cannot be treated as an ordinary real inequality). No engine simulation or proof of end-to-end correspondence was run. The engine has heterogeneous phases/frequencies and changing B; the stationary Ω=0 fixed-B linear model cannot be applied to the real adaptive trajectory merely from the guard.

## Mutations — all reported

The generator creates scratch mutations of the final `HeteroStepRef.lean`, one at a time, leaving main untouched. Each completed `lake env lean` exited 1; all three are proof-elaboration failures, not independent semantic proofs of the mutants' negations:

- **Sign:** flip `linearStep`'s delayed contribution `+` to `−`. `weighted_step_derivative` no longer matches the independently derived weighted head, and the window/witness proofs also fail. Exit 1.
- **Threshold:** weaken `window_step`'s `dt·rᵢ≤1` to `≤2`. Its `sub_nonneg` step fails; downstream use also has a changed premise type. Exit 1. A hand counterexample is symmetric two-node B with off-diagonal 3/2, dt=1 and d=1: current values 1 and delayed values −1 give head −2 although initial max is 1.
- **Nonnegativity:** replace `0≤Bᵢⱼ` in `window_step` by the tautological disjunction `0≤Bᵢⱼ ∨ Bᵢⱼ<0`, i.e. remove the nonnegativity restriction while preserving a named hypothesis. The proof cannot extract nonnegativity and downstream use also has a changed premise type. Exit 1. A hand counterexample is symmetric two-node B with off-diagonal −1, dt=1 and d=1: the row condition holds, but current 1/delayed −1 gives head 3.

No mutant survived. The threshold and nonnegativity failures contain downstream type mismatches as well as failure at the targeted proof step; the counterexamples explain why the proposed broadenings are actually false. The `sorryAx` lines in mutant logs reflect failed elaboration, not axioms in final source. Initial parallel runs were stopped under memory pressure and restarted sequentially; the included logs are the completed sequential runs.

## Reproduction and evidence

Lean 4.33.1. `lake build AIEFGateCore.HeteroStepRef` passed 2,149 jobs, and `lake build AIEFGateCore.HeteroGuard` passed 2,150 jobs. The nine new axiom reports list only `propext`, `Classical.choice`, `Quot.sound`; no warnings in the successful builds. Final sources contain no `sorry`, `admit`, new axiom, `native_decide`, `unsafe`, or `implemented_by`. Earlier failed builds were corrected. `.log.txt` files and SHA256SUMS accompany the package.

```sh
cp HeteroStepRef.lean HeteroGuard.lean "$REPO/lean/AIEFGateCore/AIEFGateCore/"
python make_mutants.py HeteroStepRef.lean "$REPO/lean/AIEFGateCore/AIEFGateCore/"
cd "$REPO/lean/AIEFGateCore"
lake build AIEFGateCore.HeteroStepRef
lake build AIEFGateCore.HeteroGuard
for m in Sign Threshold Nonnegative; do
  lake env lean "AIEFGateCore/HeteroMutant${m}.lean"  # each expected exit 1
done
```

Python correspondence, floating-point guard transfer, off-synchronous dynamics, adaptive B and the full Jacobian remain **OPEN**. No full gate or independent review is claimed.
