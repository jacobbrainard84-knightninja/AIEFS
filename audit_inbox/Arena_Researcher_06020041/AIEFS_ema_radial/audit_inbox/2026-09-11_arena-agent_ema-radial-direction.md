# Normalized EMA magnitude directional derivative — audit draft

- **Agent:** Arena.ai Agent Mode
- **Date:** 2026-09-11, Atlantic/Reykjavik
- **Base:** main `63e06d76bafa6d8e3627d31fbbbf5cb4499ae49d`; inbox `520924b89c94af0a57f8e56b858a185ca52422d1`.
- **Status:** locally kernel-checked candidate, not independently reviewed or integrated.

`EmaRadialRef.lean` defines an exact-real normalized directed EMA path at unit coherence and proves its real, imaginary and complex-norm directional derivatives; it also proves the derivative of the average of two directed magnitudes. The magnitude derivative is `αu`, and the averaged derivative is `α(u₁+u₂)/2`, independent of angular and imaginary directions. Three exact probes and `#print axioms` declarations are included. The file imports only Mathlib and no unmerged cycle.

Final targeted build on Lean 4.33.1 and mathlib `0df444a360eaa60ab8c11dca51a86af692955474`: 2,139 jobs, no warnings; ten theorem axiom reports show only standard axioms. `ONE_PAGE_NOTE.md`, `MUTATION_PROPOSALS.md`, `build_final.log` and `LOG_HASHES.txt` accompany the source. Mutants are proposals, not executed.

Critical limitation: the normalized path is stipulated and is not yet shown in Lean equivalent to main's `PhaseCoherence.coherenceStep` or the Python engine; no history-to-phase perturbation bridge, diagonal masking, weight update, gate, modulo, full Fréchet derivative or stability is proved. No full gate, independent review, repository wiring, push or promotion. Requested review: verify normalization and source correspondence, then connect to existing main definitions before composing larger results.
