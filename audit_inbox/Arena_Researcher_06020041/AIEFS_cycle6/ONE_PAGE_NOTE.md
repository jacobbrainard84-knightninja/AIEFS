# Cycle 6 — common-frequency phase locking (Lean candidate)

**Status:** locally kernel-checked research input; not independently reviewed or integrated. This extends the earlier zero-increment result to uniformly rotating locks.

Suppose that, from step N, every node has the same **constant** real phase increment w, which may be nonzero. Write n₀=N+d, where d is the P5 discrete delay. The new Lean file proves:

- `input_step_of_common_increment`: each directed coherence input is unchanged from one step to the next for n ≥ n₀. The current and delayed increments are both w, so they cancel in P5's phase/delay input identity.
- `input_eq_of_common_increment`: each input equals its n₀ value throughout that tail.
- `geometric_of_common_increment`: if z is that n₀ input, then `C(n₀+k)−z = α^k (C(n₀)−z)` on each directed edge. α is arbitrary real; decay needs `|α|<1` separately.

Arbitrary initial phases and frequencies are allowed, but the shared fixed increment is **assumed**, not derived from the closed-loop dynamics or natural frequencies. No formal theorem here establishes locking, reported-R convergence/monotonicity, floating-point behavior, or Python/Lean equivalence. The unmerged Cycle 3 module supplies the EMA identity. Novelty outside this project has not been established.

## A warning about monotonicity

An exact-arithmetic example starts with zero coherence, two identical nodes, d=1, α=1/2, u₀=u₁=π and uₙ=0 thereafter. At N+d=3, both directed entries are −5/8; after one constant-input update they are 3/16. Thus symmetrised off-diagonal reported R **decreases from 5/8 to 3/16**, despite frozen phases and constant input on that tail. This is a mathematical P5 trace with externally specified increments, not evidence that the closed-loop Python engine realizes it. It is checked by exact rational/quarter-turn arithmetic, not formalized in Lean.

## Verification and branch changes

Fresh sparse checkout of P5 branch at `b8404198bff62d77373ac2c19e988b0f90660aff`, plus the final unmerged Cycle 3 module and this file. Lean 4.33.1 and mathlib `0df444a360eaa60ab8c11dca51a86af692955474`. Final `lake build AIEFGateCore.RotatingLock`: PASS, 2220 jobs, no warnings; three `#print axioms` checks: only `propext`, `Classical.choice`, `Quot.sound`. The first build had two style warnings, fixed and rebuilt. See `build_final.log`, `axioms.log`, `SHA256SUMS.txt`. No full gate, mutation suite or independent review.

**Repository state changed since Cycle 5:** main is now `7129d31322b31389f5fee3a64bb216b19574600f`; P5 was merged via #31, and production-delay engine probes via #33. Rate-law/status and mutation-guard changes also landed. We did not determine that those changes originated from our proposals. The three core P5 phase/history source files have identical SHA-256 hashes on the tested P5 branch and this main commit; the complete main tree was not built. `PhaseLockCoherence`, `CoherenceMotion`, `LockedCoherence`, and `RotatingLock` are absent from main at that commit. Previous patches based on old main should **not** be applied wholesale without rebasing/review.

## Reproduce

With a checkout of P5 `b8404198…` and its pinned toolchain/cache, copy `AIEFS_cycle3/files/lean/AIEFGateCore/AIEFGateCore/PhaseLockCoherence.lean` and `AIEFS_cycle6/RotatingLock.lean` into `lean/AIEFGateCore/AIEFGateCore/`, then:

```sh
cd lean/AIEFGateCore
lake build AIEFGateCore.RotatingLock
# Copy AIEFS_cycle6/CheckRotatingLock.lean here first:
lake env lean CheckRotatingLock.lean
python3 /home/user/AIEFS_cycle6/test_rotating_lock.py
```

The Python check also requires `/home/user/AIEFS_cycle4/test_delay_lock.py`. Its two methods passed, covering 16 common-rotation (N,d) cases for both directed edges and the R counterexample. The test transcribes a restricted P5 indexing model; it does not exercise the engine. No push or claim promotion was made.
