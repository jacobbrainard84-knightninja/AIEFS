# Audit inbox draft — common-increment phase lock and delayed EMA

**Unverified input for independent review; no push or claim promotion.**

`RotatingLock.lean` extends the workspace Cycle 3 phase-freeze theorem to a common constant increment w, including nonzero w. If u n i = w for all nodes and n ≥ N, then from N+d each directed P5 input is constant and its EMA error relative to that input obeys the exact α^k identity. This is conditional on an assumed lock and applies for all real α; only |α|<1 gives decay. It does not prove closed-loop locking, Python equivalence, or reported-R monotonicity.

Evidence: Lean 4.33.1 targeted `lake build AIEFGateCore.RotatingLock` passed, 2220 jobs, no warnings after style fixes; three declarations show only standard axioms. See `AIEFS_cycle6/build_final.log`, `axioms.log`, `SHA256SUMS.txt`. Tested on P5 b8404198… with the unmerged Cycle 3 `PhaseLockCoherence.lean` added; full gate, mutation testing, and independent review remain outstanding. `ONE_PAGE_NOTE.md` has precise setup and compile commands.

An exact-arithmetic P5 trace also refutes universal monotonicity after freezing: d=1, α=1/2, zero initial phases/coherence, equal increments π at n=0,1 and zero thereafter. At n=3 both directed C are −5/8; at n=4 both are 3/16, so off-diagonal reported R decreases from 5/8 to 3/16. This externally specified sequence is not shown realizable by the coupled engine; this example is not a Lean theorem. `test_rotating_lock.py` and `examples.log` record the check.

Rechecked main `7129d31322b31389f5fee3a64bb216b19574600f`: P5 merged in #31 and production-delay probes in #33; prior workspace refresh patches should not be applied wholesale. Tested P5 and current-main versions of the three core phase/history files have matching hashes; no complete main-tree build was performed. Owner should independently triage, rebase and run required project gates before integration.
