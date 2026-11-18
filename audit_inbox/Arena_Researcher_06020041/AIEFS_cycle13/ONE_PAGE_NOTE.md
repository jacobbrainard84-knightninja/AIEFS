# Cycle 13 — the delayed common mode has a simple neutral root

**Status:** locally kernel-checked Lean candidate, not independently reviewed or integrated. This closes the root-multiplicity gap identified in Cycle 12, but does not formalize the oscillator Jacobian or nonlinear stability.

Define over ℂ, for any natural d and real h,

`P(X) = X^(d+1) − (1−h) X^d − h`.

`CommonRootSimple.lean` proves:

1. `common_root`: P(1)=0 for every d and h.
2. `derivative_at_one`: P′(1)=1+d·h for every d and h.
3. `root_multiplicity_one`: if h>0, the algebraic root multiplicity of 1 is **exactly one**. It uses the nonzero derivative, not just uniqueness on the unit circle.

The previous Cycle 12 file separately proves that, for 0<h<1, 1 is the only common-polynomial root on the unit circle and no root lies outside. The two results have **not been formally composed into a single theorem**; mathematically, their combination supplies the common-mode root property in the Cycle 9/10 argument. Neither file proves that P is the characteristic polynomial of AIEFS's linearization, that the quotient is stable, or that a prepared orbit attracts generic states. The projected branch and heterogeneous frequencies remain open.

## Verification

Fresh sparse main checkout `25c486875f9d98e10e2dbf652df494c5b20e8b9a`, Lean 4.33.1, pinned mathlib `0df444a360eaa60ab8c11dca51a86af692955474`: `lake build AIEFGateCore.CommonRootSimple` **PASS**, 3006 jobs, no warnings (`build_final.log`). All three declarations use only `propext`, `Classical.choice`, `Quot.sound` (`check.log`). The check file also proves the negative control `P(X)=(X−1)²` for d=1, h=−1, and verifies its derivative at 1 is zero. This shows h cannot be dropped without replacement; it is not a project mutation-suite test. The first successful build had an unused-tactic warning, corrected and rebuilt on final bytes; see `attempt1.log` and `build_final.log`.

```sh
# Copy CommonRootSimple.lean to lean/AIEFGateCore/AIEFGateCore/ and
# CheckCommonRootSimple.lean to lean/AIEFGateCore/ in the cited checkout.
cd lean/AIEFGateCore
lake build AIEFGateCore.CommonRootSimple
lake env lean CheckCommonRootSimple.lean
```

No root import, checksum, inventory or mutation wiring was changed; no full project gate, independent review, push or claim promotion. `SHA256SUMS.txt` pins the two Lean files and final logs.

## Repository and inbox direction

Main advanced since Cycle 12 via PR #40 (study-registry path checker); no claim that this cycle independently audited that change. Inbox now contains the owner-relayed Cycle 11/12 files and two outside-audit notes: a conditional rate-law gate adjudication and modular-oracle false-pass concerns. Those notes are unverified inputs, not project findings, and were not independently reproduced here. The earlier reviewer-recommended polynomial lemmas motivated this cycle. Keep any private metadata in old compare files out of handoffs.
