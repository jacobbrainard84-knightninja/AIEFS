# Cycle 5 — formal composition of delayed locking and EMA identity

**Result:** two new Lean declarations, kernel-checked locally, join the phase/delay result to the EMA result without assuming constant input separately. This is author verification, not independent review or a merged project contribution.

Let `n₀ = N+d`. If all phase increments `u n i` vanish for all nodes and all `n ≥ N`, then:

1. `input_eq_at_lock_delay`: the P5 delayed coherence input on any directed pair at any `n ≥ n₀` equals its value at `n₀`.
2. `geometric_after_phase_lock`: for any real `α`, complex initial matrix, and `k ≥ 0`,
   `C(n₀+k) − z = α^k (C(n₀) − z)`, where `z` is the phase-derived input at `n₀`.

The first uses induction plus Cycle 3's adjacent-time equality; the second applies its constant-input EMA identity using the first. The equality is valid for arbitrary real `α`: decay requires an extra assumption such as `|α| < 1`, which is **not** part of the Lean theorem. Freezing is assumed, not proved. No reported-R bound, counterexample, Python equivalence, float result, or closed-loop phase-locking result is formalized here. The Cycle 4 reported-R estimate and sharpness argument remain separate, unformalized analytic work.

## Checked dependencies and evidence

A fresh sparse checkout of P5 `ab18b068e1560b7d6d8005f42ed4d22c7097c8c2` was supplemented with the **final** Cycle 3 `PhaseLockCoherence.lean` and this cycle's `LockedCoherence.lean`. Unlike the proposed full Cycle 3 patch, these two modules themselves do not import Cycle 2's c016 module; this targeted test does **not** establish the full patch stack is compatible or integrated. Lean `4.33.1`; mathlib rev `0df444a360eaa60ab8c11dca51a86af692955474` from P5's manifest. Targeted `lake build AIEFGateCore.LockedCoherence` passed, 2220 jobs, no warnings in its log; `#print axioms` for both new declarations reports only `propext`, `Classical.choice`, `Quot.sound`. See `build.log`, `axioms.log`, `SHA256SUMS.txt`. No full project gate, mutation suite, inventory regeneration, integration test or independent review was performed this cycle.

## Reproduce

From a checkout at the exact P5 commit, install its pinned Lean/toolchain and mathlib cache, then copy both source files into `lean/AIEFGateCore/AIEFGateCore/`. The dependency is `AIEFS_cycle3/files/lean/AIEFGateCore/AIEFGateCore/PhaseLockCoherence.lean`; the new file is `AIEFS_cycle5/LockedCoherence.lean`. Then:

```sh
cd lean/AIEFGateCore
lake exe cache get
lake build AIEFGateCore.LockedCoherence
# Copy AIEFS_cycle5/CheckCycle5.lean into this directory, then:
lake env lean CheckCycle5.lean
```

This is a targeted command, not a substitute for `check_lean_gate.sh`. The scratch checkout and cached build are not part of the persisted deliverable. Main was rechecked at `a559e0d30458bb01989ac47225675d6baec518b8`, P5 at the commit above. No repo push, merge, changes to frozen evidence, or claim promotion.
