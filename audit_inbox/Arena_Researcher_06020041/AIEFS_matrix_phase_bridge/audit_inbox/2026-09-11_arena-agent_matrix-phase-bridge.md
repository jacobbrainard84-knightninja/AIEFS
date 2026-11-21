# Fixed-matrix phase bridge and exact witnesses — audit draft

- **Agent:** Arena.ai Agent Mode
- **Session date:** 2026-09-11, Atlantic/Reykjavik. **Filing date unconfirmed:** the relayed lead note is dated 2026-11-20, Europe/Tirane. Reconcile the project date and this draft's filename before upload.
- **Base main:** `0a6a2f62ea9af147cac60a7be30d85d6b37fe52a`; main later advanced to `d7b9fac600686477babf229ede70a19f1c2dfa13` and inbox to `b84f54d861524ed27d424c7b410f91d1fbe5166a` during the work. The main `EngineStepRef.lean` and engine bytes match across the two cited main SHAs; the later head was not built.
- **Status:** locally kernel-checked candidate, not independently reviewed or integrated.

`MatrixPhaseBridge.lean` imports main's `EngineStepRef`, defines a fixed supplied-matrix phase head and engine-shaped queue step, proves reduction to the scalar reference for uniform zero-diagonal b≥0, proves the circle bridge without uniformity under theta/history consistency, and proves the fixed-W directional head derivative at a synchronized history. Exact Lean inequalities show an N=3 nonuniform matrix differs from its mean-weight scalar reference, and inconsistent input breaks the circle correspondence against main `phaseStep`. Two direct value examples probe queue shifting and delayed sine input. `ONE_PAGE_NOTE.md` explains the important limits: W is post-update and held fixed; the synchronized history need not be an orbit; Python/adaptive derivative correspondence is unproved.

Final targeted Lean 4.33.1 / mathlib `0df444a360eaa60ab8c11dca51a86af692955474` build passed 2,191 jobs without warnings; seven theorem axiom reports contain only standard axioms. `MUTATION_PROPOSALS.md` lists unexecuted mutants and an equivalence control; no full gate, independent review, push or promotion. No project-owned guards, CI, inventory, mutation scripts or root imports were edited.
