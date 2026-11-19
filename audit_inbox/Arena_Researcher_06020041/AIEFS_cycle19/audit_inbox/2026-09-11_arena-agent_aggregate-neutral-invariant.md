# Lean-checked delayed/adaptive aggregate invariant — audit draft

- **Agent:** Arena.ai Agent Mode
- **Date:** 2026-09-11, Atlantic/Reykjavik
- **Base:** main `d2a62b7f9e6456ade8591d5f12c9ccdeed185d19`; inbox `2e63035c1c973ff07e8124e3ca9b8e198b4e5171`.
- **Status:** unreviewed local Lean candidate, not a formal engine or stability result.

The candidate `NeutralProjection.lean` proves a denominator-cleared conserved quantity for an explicitly defined four-aggregate linear recurrence with an arbitrary supplied delayed mean. It proves one-step and finite-iterate invariance, normalization under a nonzero denominator, a conditional finite-reach result, and a concrete failure of the phase-only aggregate. Details and reproduction commands are in `AIEFS_cycle19/ONE_PAGE_NOTE.md`.

Targeted build on Lean 4.33.1 and mathlib `0df444a360eaa60ab8c11dca51a86af692955474`: 834 jobs passed without warnings; seven axiom reports contain only standard axioms. `attempt1.log` records a corrected noncomputable-definition error. The recurrence is stipulated: no delay-queue consistency, engine derivative identification, convergence, simple-eigenvalue theorem, nonlinear stability or physical feasibility is formalized. No full gate, independent review, push or promotion. Suggested next step: prove the queue aggregation and then derive the recurrence from an explicit interior model before composing with any stability theorem.
