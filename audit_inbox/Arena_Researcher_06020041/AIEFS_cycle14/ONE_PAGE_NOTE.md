# Cycle 14 — connect delayed root bounds to an explicit shift map

**Status:** locally kernel-checked candidate; no independent review or integration. This cycle bridges the Cycle 11/12 root bounds to a concrete finite-delay linear map. It does **not** yet establish that this map is the Jacobian of the AIEFS oscillator.

## The map and results

For indices 0,…,d define `T(v)₀ = a v₀ + b v_d` and `T(v)ₖ = vₖ₋₁` for k>0. Lean represents v as a function on ℕ, but the eigenrelation and nonzero condition are explicitly restricted to 0,…,d; entries above d do not matter. The following statements are proved:

1. `characteristic_of_nonzero_mode`: if `T(v)ₖ = z vₖ` on 0,…,d and v is nonzero at one of those indices, then **z^(d+1)=a z^d+b**. The proof derives the shift-chain identity and proves the final entry is nonzero before cancellation.
2. `common_step_eigenvalue_bound`: for `a=1−h`, `b=h` and 0<h<1, every such eigenvalue has |z|≤1, and a unit-modulus eigenvalue must equal 1.
3. `transverse_step_eigenvalue_inside`: for `a=1−mh`, `b=−h`, m≥1, h>0 and mh<1, every such eigenvalue has |z|<1. It formally combines Cycle 11's m≥2 bound with Cycle 12's m=1 boundary case.

These are pointwise finite-shift eigenrelations, not yet Mathlib `Matrix`/`LinearMap` spectral API statements. They apply to the **abstract scalar delay map**. The identification of its common/transverse coefficients with the full engine's Jacobian, block decomposition, root multiplicity as matrix eigenvalue, nonlinear quotient stability, projected-gate tie, and heterogeneous frequencies are not proved. Cycle 13's simple polynomial root is a separate module and is **not** imported or formally composed here.

The check file proves a negative control: the zero state satisfies the transverse shift equation for z=2, which is outside the unit disk. Therefore the nonzero-state hypothesis is essential; this is an exact witness, not a mutation-suite run.

## Verification and reproducibility

Sparse checkout of main `25c486875f9d98e10e2dbf652df494c5b20e8b9a`; Lean 4.33.1; mathlib `0df444a360eaa60ab8c11dca51a86af692955474`. Place the unchanged Cycle 11 `DelayRootBound.lean`, Cycle 12 `DelayBoundaryRoots.lean`, and this cycle's `DelayModeBridge.lean` in `lean/AIEFGateCore/AIEFGateCore/`, and copy `CheckDelayModeBridge.lean` to `lean/AIEFGateCore/`:

```sh
cd lean/AIEFGateCore
lake build AIEFGateCore.DelayModeBridge
lake env lean CheckDelayModeBridge.lean
```

Final targeted build: PASS, 3008 jobs, no warnings (`build_final.log`); all seven new theorem declarations show only `propext`, `Classical.choice`, `Quot.sound` (`check_final.log`), and the negative control compiles. Dependencies built separately; exact source/log hashes are in `SHA256SUMS.txt`. No full gate, full mutation suite, `Matrix` proof, independent review, repository wiring, push or claim promotion. Current main SHA was rechecked after the build; audit-inbox was unchanged at `d28fa35f96c84e45a1a59f03c454f1ebbd114939` at cycle start.
