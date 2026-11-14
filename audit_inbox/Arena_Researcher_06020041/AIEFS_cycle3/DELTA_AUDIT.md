# Cycle 3 — phase and delay: independent review draft

**Status: unverified research input, not merged.** Based on the proposed Cycle 2 tree, itself dependent on the unmerged P5/Cycle 1 patch. `phase_lock_coherence.patch` applies to that proposed tree, not directly to main.

## Results

`PhaseLockCoherence.lean` contains three kernel-checked conditional statements:

1. If every phase increment vanishes from N, the delayed coherence input at each directed edge is unchanged between n and n+1 for n ≥ N+d. The proof uses the P5 delayed-increment identity. This assumes locking; it does not establish that the coupled network locks.
2. If an input z is constant from n₀, then C(n₀+k) − z = αᵏ(C(n₀) − z). This is an algebraic identity for arbitrary real α; it yields convergence only under an additional condition such as |α| < 1. The constant-input assumption has not been formally derived from theorem 1 in a combined theorem.
3. If a directed EMA entry is aligned with its current unit input, with coefficient r in [0,1] and α in [0,1], its next **directed magnitude** does not decrease. This is not, by itself, monotonicity of the symmetrised reported R or of a trajectory. Both directed entries would need suitable assumptions.

All results are exact-real statements about the P5 model; they do not establish Python/Lean equivalence, float behavior, B convergence, or closed-loop phase locking (O1). Novelty has not been assessed.

## Verification

- Targeted module build: 2,219 jobs, no warnings. Separate `#print axioms` on the three declarations reported only `propext`, `Classical.choice`, and `Quot.sound`.
- Project gate on the tested source: PASS, 2,301 jobs, zero warnings, 22 source files scanned, 742 declarations audited; cache download was performed separately and the gate used `SKIP_CACHE=1` and `REUSE_BUILD=1`. See `lean_gate_summary.txt` and logs.
- **Final-source qualification:** after that build, the module docstring was clarified to distinguish the identity from contraction and the directed magnitude from reported R. Its checksum was regenerated. Those are comment-only changes, but the full gate has not been rerun on the final bytes.
- Existing Python tests: 70 passed on the reconstructed tree. They are not tests of these new mathematical claims.
- A modified statement dropping `+ d` caused the retained proof to fail at two arithmetic obligations. This checks proof sensitivity only: it is neither a mathematical counterexample nor a semantic mutation-suite pass. It is not wired into CI.
- `git apply --check` passed against a minimal Cycle 2 baseline. No complete-repository inventory verification or full 59-mutant run was performed.

## Handoff

Apply and independently review earlier P5/Cycle 1 and Cycle 2 work before considering this patch. After applying in a complete clone, stage the intended files and regenerate `registry/artifacts_current.csv` following the repository workflow; run all required checks. The owner controls pushes and merges. The inbox note is a draft only. No repo changes or claim promotions were made.
