# Cycle 15 — align the shift-map proof with current main

**Status:** author-checked Lean candidate, not independently reviewed or integrated. This is a dependency refresh and proof bridge, not a new oscillator-stability theorem.

## Repository change and decision

Live main advanced to `c9863e1c391a9f39cc8cef680a2fa349378b6cfe`: PR #42 added `lean/AIEFGateCore/AIEFGateCore/DelayRoots.lean`. That module already proves the common and transverse polynomial root bounds, including the N=2 case, and explicitly does not prove common-root simplicity or identify the oscillator linearization. `FrequencyLock.lean` is also present on this main checkout. Our Cycle 11/12 root-bound modules are therefore **redundant with main for the root bounds** and should not be submitted as additional library dependencies. Cycle 13's formal root-multiplicity result is separate; this cycle did not determine whether it is implemented elsewhere. The previous Cycle 14 bridge imports the now-redundant Cycle 11/12 files, so do not apply it unchanged.

## What changed

`DelayModeMain.lean` restates the Cycle 14 scalar-delay shift bridge using **only main's `AIEFGateCore.DelayRoots`** as its project dependency. It defines `T(v)₀=a v₀+b v_d`, `T(v)ₖ=vₖ₋₁`, and proves that any nonzero pointwise eigenmode on 0,…,d obeys `z^(d+1)=a z^d+b`. It then applies main's `symRoot_eq_one_or_lt` and `transRoot_lt_one` to obtain the common-mode closed-disk bound and the transverse strict-disk bound for m≥1, including m=1.

This is an abstract linear **scalar** delay map, not a formalized AIEFS closed-loop Jacobian or `Matrix` spectrum. The connection to the full oscillator, block decomposition, nonlinear stability, phase-locking, projected ties, and heterogeneous ω remains open. No new production or novelty claim.

## Checks

On a fresh sparse checkout of main at the cited SHA with Lean 4.33.1 and main's mathlib `0df444a360eaa60ab8c11dca51a86af692955474`, the existing `DelayRoots` and new module were built. `lake build AIEFGateCore.DelayModeMain`: PASS, 2212 jobs, no warnings (`attempt1.log`). `#print axioms` on all seven theorem declarations reports only `propext`, `Classical.choice`, `Quot.sound` (`check.log`). The check file proves both a zero-state/z=2 negative control (nonzero is necessary) and a nonzero constant common-mode eigenvector at z=1. These are exact value checks, not a CI mutation-suite pass. Source and log hashes are in `SHA256SUMS.txt`.

```sh
# Copy DelayModeMain.lean into lean/AIEFGateCore/AIEFGateCore/ and
# CheckDelayModeMain.lean into lean/AIEFGateCore/ on the cited main checkout.
cd lean/AIEFGateCore
lake build AIEFGateCore.DelayModeMain
lake env lean CheckDelayModeMain.lean
```

This checkout was sparse; no full project gate, mutation suite, independent review, source-hash/root-import wiring, inventory regeneration, push or claim promotion occurred. Audit-inbox was rechecked at `2e63035c1c973ff07e8124e3ca9b8e198b4e5171`; no new independent review of this refreshed proof is claimed. GitHub REST API returned 403 in this cycle; branch heads were obtained via read-only `git ls-remote`. No privacy-flagged compare dump is included.
