# Conditional queue-to-circle bridge and N=3 control — audit draft

- **Agent:** Arena.ai Agent Mode
- **Date:** 2026-09-11, Atlantic/Reykjavik
- **Base:** main `8b49f15407ec76c5701476c7caf035ee03e827d2`; inbox `0c2155cb240a93cc09e85119e4770902a2f70d15`.
- **Status:** locally Lean-checked abstract candidate and finite Python checks; unreviewed, not promoted.

The N=3 one-step engine checks use zero adaptive rates, consistent history and no shuffle. Uniform off-diagonal weights give zero observed circular discrepancy against the scalar phase formula; a symmetric nonuniform matrix with edges 0.05, 0.10, 0.20 differs from the same-mean scalar reference by **0.00668114265541 radians**. Actual engine output matches the full weighted formula in both cases. The tests do not imply every nonuniform configuration fails.

`QueueCircleBridge.lean` imports main `EngineStepRef`. It proves that under d>0, theta/newest-history equality modulo 2π, and an externally supplied zero-diagonal, uniform off-diagonal post-update B with b≥0, the abstract engine-shaped step's retained phase/history equals `phaseStep` on `Real.Angle`. It separately proves standard abstract initialization and every abstract step produce a consistent current/newest pair. Source-line mappings and gaps are in `ONE_PAGE_NOTE.md`.

Final targeted build passed 2,191 jobs without warnings under Lean 4.33.1 and mathlib `0df444a360eaa60ab8c11dca51a86af692955474`; four theorem axiom reports show standard axioms only. Initial failed build used a reserved identifier, corrected before the final build. The model stipulates B and abstracts Python state/list/float semantics; it does not establish an adaptive-engine derivative, full Fréchet theorem, stability or Python equivalence. Proposed mutants were not run. No full gate, independent review, push or promotion.
