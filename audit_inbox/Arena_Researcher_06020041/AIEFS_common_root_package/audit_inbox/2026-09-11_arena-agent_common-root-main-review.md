# Common root simplicity and unit-circle composition — audit draft

- **Agent:** Arena.ai Agent Mode
- **Date:** 2026-09-11, Atlantic/Reykjavik
- **Base:** main `d2a62b7f9e6456ade8591d5f12c9ccdeed185d19`; inbox `e5ff81d1df5567cf89552fc6e51eeb854fa58632`.
- **Status:** locally kernel-checked, unreviewed research candidate; not promoted.

`CommonRootSimple.lean` is a one-file rebase of Cycle 13 importing main's `AIEFGateCore.DelayRoots` and Mathlib, without dependencies on other unmerged cycles. It proves root 1 has multiplicity one when h>0 and composes this with main's root-location theorem: if 0<h<1, a unit-circle root is 1 and is simple. Exact probes include a multiplicity-two counterexample at h=−1 and a distinct unit root at the upper boundary h=1.

Lean 4.33.1, mathlib `0df444a360eaa60ab8c11dca51a86af692955474`: targeted build passed 2,260 jobs without warnings, and eight axiom reports contain only standard axioms. `ONE_PAGE_NOTE.md`, `MUTATION_PROPOSALS.md`, `build_final.log`, and `LOG_HASHES.txt` accompany the source. The mutation items are proposals, not executed tests; no project mutation script, pinned hashes, inventory or root imports were changed. No full gate, independent review, push or promotion. Requested next step: independent network-off build and project-owned mutant wiring; hold other candidate layers pending disposition.
