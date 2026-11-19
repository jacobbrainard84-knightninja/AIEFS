# Lean node-history to aggregate invariant bridge — audit draft

- **Agent:** Arena.ai Agent Mode
- **Date:** 2026-09-11, Atlantic/Reykjavik
- **Base:** main `d2a62b7f9e6456ade8591d5f12c9ccdeed185d19`; inbox `2e63035c1c973ff07e8124e3ca9b8e198b4e5171`.
- **Status:** unreviewed, locally checked Lean candidate; not an engine theorem.

Using the unmerged Cycle 19 module, `QueueNeutral.lean` proves that a consistently shifted scalar delay history induces its aggregate recurrence. `NodeQueueNeutral.lean` defines a node-indexed complete-graph phase-history step with stipulated adaptive node quantities and proves that summing nodes commutes with the scalar queue map. It composes this with Cycle 19 to prove its denominator-cleared neutral functional is conserved through every finite iterate, without assuming an eigenmode or node-symmetric state. The invariant uses node sums, not means. The exact equations, definitions, caveats and commands appear in `AIEFS_cycle20/ONE_PAGE_NOTE.md`.

Evidence: final targeted build passed 963 jobs without warnings on Lean 4.33.1 and mathlib `0df444a360eaa60ab8c11dca51a86af692955474`; six axiom reports use only the standard three axioms; two exact history-sum examples compile. Early exploratory proof contained a temporary `sorry`, removed from the completed sources before final build. No full gate or mutation suite. In particular, neither the stipulated linear phase/weight/EMA equations nor queue semantics have been identified in Lean with the actual engine; convergence and nonlinear stability remain unproved. No independent review, push or promotion. Review requested: scrutinize the neighbour and queue sums, then derive the node model from an explicit smooth interior engine model, including symmetrization.
