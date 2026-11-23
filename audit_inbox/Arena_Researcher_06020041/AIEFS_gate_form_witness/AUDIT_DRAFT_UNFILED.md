# Exact min-endpoint gate witness

**Status:** local exact-rational candidate; not deposited, independently reviewed, or pushed. Engine source was read from main `7865ab19282ceae49df9aa70b396d60ada38d3c2`: SHA-256 `ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede`. The same engine bytes were checked at DIRECTION-8's `d1cbcf38`. No project source, CI, mutation scripts, inventory or prior deposits were changed.

**Date / UNEXPLAINED:** the session date is stated as 2026-09-11 Atlantic/Reykjavik, while the container command `TZ=America/Denver date '+%F %T %Z'` returned `2026-11-22 16:50:15 MST`; DIRECTION-8 is dated November 22 MST. The observed shell date conflicts with the session date. This local draft is not a deposit and its filename has not been represented as a validated MST filing date; resolve the conflict before filing it in a dated folder. No older folder has been modified.

## Exact witness — ran

Let the pre-projection matrix and valid positive gate parameters be

```
B = [[0,   1,   1/2],
     [1,   0,   1/4],
     [1/2, 1/4, 0  ]],   cap = 1,   ε = 1/4.
```

B is symmetric, nonnegative and zero-diagonal. Its row sums are `(3/2, 5/4, 3/4)`, so the capacity branch is active: the first two exceed the cap. For `sᵢ = min(1, cap/(rowᵢ+ε))`, the scales are `(4/7, 2/3, 1)`. On the nonzero edge (0,1),

```
min(s₀,s₁) = 4/7 ≠ 8/21 = s₀s₁,
(min(s₀,s₁))² = 16/49 ≠ 8/21 = (√(s₀s₁))².
```

All quantities involved are nonnegative, so the unequal squares prove `4/7 ≠ √(8/21)` exactly. This is an exact rational argument, not a Lean theorem. The min-endpoint projected row sums are `(6/7, 31/42, 19/42)`, each below capacity. The witness addresses equality of these three factors; it does not adjudicate any broader rate-law or normalization claim.

## Read versus ran

**Read:** engine lines 787–812 build nonnegative symmetric zero-diagonal `B_unprojected`, compute row sums, activate projection only on a gap violation, and apply `np.minimum.outer(scale, scale)`. `validate_B_matrix` and `DynamicState.validate` check B's symmetry, nonnegativity and zero diagonal. The witness B is the **pre-projection** matrix; its capacity violation is intentional and is not represented as an already projected state.

**Ran:** `python exact_check.py` used exact `fractions.Fraction` arithmetic to check the matrix, active branch, scales, inequalities and projected rows. Two local formula mutants were exercised: replacing the edge factor by product or by geometric mean. Each failed the fixed expected-factor assertion, and the harness reported both killed. These are targeted local formula checks, not the project's mutation suite and not evidence that a modified engine was executed.

**Ran:** a separate float64 engine probe used valid non-production parameters (`dt=τ=1`, `a=q=1`, `delta=0`, `eta=1`, `mu=gamma=0`, `T_window=10`, `scale_epsilon=1/4`). It began with B=0, initialized a constructed finite coherence accumulator so one EMA step produces the witness B, and used a consistent history with oldest phase −1 and newest phase 0. `config.validate`, and `state.validate` before and after `advance_state`, passed; projection was active and the projected B matched the exact witness at displayed precision (maximum difference 0.0). This is a validator-accepted constructed state, not a demonstration of reachability from standard zero-coherence initialization. The arithmetic proof and float execution are distinct evidence.

Commands used, with `ENGINE_DIR` the directory holding the pinned engine file:

```sh
python exact_check.py
PYTHONPATH="$ENGINE_DIR" python engine_probe.py
```

`checks.log.txt` contains the actual output and `SHA256SUMS.txt` pins source and log. The owner/reviewer need not execute scripts to understand the witness. No Lean build or full mutation suite was run in this cycle. DIRECTION-8's wrap-invariant EMA corollary and inherited rederivations remain open.
