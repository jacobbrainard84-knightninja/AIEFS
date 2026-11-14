# Cycle 4 — sharp delay boundary and conditional reported-coherence rate

**Status:** analytic derivation and exact-arithmetic executable checks; not independently reviewed or formalized in Lean. Applies to the proposed P5/Cycle 3 exact-real model, not an established equivalence to the Python engine.

## The delay boundary really is needed

For any integers **N ≥ 1 and d ≥ 1**, take two nodes i ≠ j, all initial phases 0, all frequencies 0, and τ = 0. Set the only nonzero increment to u(N−1,j) = π; all other increments are zero. Thus every increment is zero from N on. Let n = N+d−1. At n, the delayed source reads phase j at N−1, which is 0; at n+1 it reads phase j at N, which is π. The current phase of i is always 0. Therefore

**zₙ(i,j) = 1 and zₙ₊₁(i,j) = −1.**

Here n ≥ N, so this explicitly refutes the Cycle 3 statement with `N+d` weakened to `N`; indeed it refutes any universal threshold smaller than N+d for N,d ≥ 1. The claim is about unchanged **input**, not coherence EMA or closed-loop realizability. It uses P5's oldest-history read at max(0,n−d), and π is an actual phase increment, not merely a representation change. For N=0 the example cannot be constructed: no pre-lock increment exists, and the N+d threshold is sufficient but not generally sharp.

## Compose the existing results mathematically

Put n₀ = N+d and zᵢⱼ = input(n₀,i,j). Cycle 3 theorem 1 says input at consecutive times is equal for every n ≥ n₀. Induction makes it equal to zᵢⱼ for all such n. Substitution into theorem 2 gives

**C(n₀+k,i,j) − zᵢⱼ = αᵏ [C(n₀,i,j) − zᵢⱼ].**

If 0 ≤ α < 1 and both directed EMA entries C(n₀,i,j), C(n₀,j,i) have norm ≤ 1, then for i ≠ j the P5 reported symmetrised value obeys

**0 ≤ 1 − reported(C(n₀+k),i,j) ≤ 2αᵏ.**

Reason: both inputs have unit norm, each error norm is at most 2αᵏ, and the reverse triangle inequality bounds each directed magnitude's distance from 1. The EMA unit disk is invariant for α in [0,1], so reported is at most 1; averaging both directed bounds yields the displayed result. This includes k=0 with α⁰=1. If all initial entries have norm ≤1, the existing P5 unit-disk theorem supplies the n₀ hypothesis. Diagonal reported values are forced to zero and are excluded. This is a rate *after assumed complete phase freezing*; it neither proves freezing nor gives a rate for the actual closed-loop system. It is not a monotonicity claim. Formal composition and this rate are not Lean-checked.

## Reproduce

```sh
python3 /home/user/AIEFS_cycle4/test_delay_lock.py
```

Three unittest methods passed: 64 sharp-boundary instances, a zero-lock-start sanity check, and 16 EMA identity families. Tests use exact integer quarter-turn phasors and rational Gaussian arithmetic, with a small independent transcription of P5's indexing. They are examples and regression aids, not a formal proof of the general result or of Python/Lean equivalence. No Lean compilation or project gate was run this cycle. `test_log.txt` records output; `SHA256SUMS.txt` pins checked script and Cycle 3 source.

Live GitHub main was rechecked at `a559e0d30458bb01989ac47225675d6baec518b8`; P5 was `ab18b068e1560b7d6d8005f42ed4d22c7097c8c2`. The stacked work remains unmerged in our workspace; remote branches other than these two were not exhaustively audited. No GitHub changes or claim promotion.
