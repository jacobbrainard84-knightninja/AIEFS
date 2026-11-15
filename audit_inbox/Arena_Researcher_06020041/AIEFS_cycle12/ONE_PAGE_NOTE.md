# Cycle 12 — Lean proofs for the boundary cases of delayed roots

**Status:** author-checked Lean research candidate; independent review and project integration outstanding. In direct response to the inbox recommendation to formalize the Cycle 9/10 root arguments, this cycle covers the cases left open by Cycle 11. These are polynomial-root statements, **not** a formal proof of the oscillator Jacobian or of nonlinear stability.

## Results

For any d∈ℕ and 0<h<1:

1. `two_node_transverse_root_inside`: every complex root of **z^(d+1)=(1−h)z^d−h** has |z|<1. This is the N=2 transverse polynomial, the coefficient-sum-equals-one boundary that the Cycle 11 strict-sum lemma did not cover.
2. `common_root_closed_and_unit_unique`: every complex root of **z^(d+1)=(1−h)z^d+h** has |z|≤1, and a root of norm 1 must equal 1. Hence every other root lies strictly inside the unit disk. For Cycle 10's common mode, this h corresponds to `(N−1)·dt·b·cos(Ωτ)`.
3. Two helper results prove a general closed-disk bound and the equality case of the complex triangle inequality. They are also kernel-checked.

**Still open in Lean:** root 1's *simplicity*; identification of these polynomials with the closed-loop Jacobian; the local nonlinear/quotient stability theorem; and the nonsmooth projected branch. No heterogeneous-frequency or production claim follows. Cycle 11 handles the N≥3 transverse polynomial separately.

## Checks

A fresh sparse checkout of main `ade1179f049bca0a7de3a1152880a2c6e0a19db4`, Lean 4.33.1, mathlib `0df444a360eaa60ab8c11dca51a86af692955474`, plus the new module: targeted `lake build AIEFGateCore.DelayBoundaryRoots` **PASS**, 3006 jobs, no warnings (`build_final.log`). `#print axioms` reports only `propext`, `Classical.choice`, `Quot.sound` for all four declarations. `CheckDelayBoundaryRoots.lean` also kernel-checks two endpoint counterexamples: h=0 defeats strict two-node transverse stability, while h=1 allows common-mode z=−1 on the unit circle for d=1. These are value checks, not a project mutation-suite pass. Earlier failed attempts and their error logs are retained; the final source was rebuilt after correction.

```sh
# On the cited main checkout, copy DelayBoundaryRoots.lean to
# lean/AIEFGateCore/AIEFGateCore/ and CheckDelayBoundaryRoots.lean to lean/AIEFGateCore/.
cd lean/AIEFGateCore
lake build AIEFGateCore.DelayBoundaryRoots
lake env lean CheckDelayBoundaryRoots.lean
```

The module imports Mathlib only; no repository root import, checksum, inventory, or mutation wiring was changed. No full gate, project mutation suite, independent review, push, or claim promotion. Source and log hashes are in `SHA256SUMS.txt`.

## Live repository update

Main advanced from `871417d…` to `ade1179…` via PR #39, which landed P6/c016 `CoherenceMotion.lean` and related fixes. The previously proposed Cycle 2 c016 port should not be applied on top. Audit-inbox advanced to `0be5a2a6241802ea4e56eab4182f51af6bc0b672`; the new entries concern study-registry path integrity and triage. Those new entries were not independently audited in this cycle. No raw GitHub compare dump is included in this handoff.
