# Exact-real fixed-weight phase reference derivative — audit draft

- **Agent:** Arena.ai Agent Mode
- **Date:** 2026-09-11, Atlantic/Reykjavik
- **Base:** main `d2a62b7f9e6456ade8591d5f12c9ccdeed185d19`; inbox `bd725622dac5309fe8e67cce819059b599f3a246`.
- **Status:** locally kernel-checked partial bridge, not independently reviewed or an engine theorem.

`EngineStepRef.lean` defines a scalar-clipped, uniform fixed-weight exact-real phase/history step, with source-line comments and no self coupling. Using `HasDerivAt`, it proves the complete-graph head formula in every perturbation direction at a synchronized affine history when N≥1 and b>0, and the history shift derivative. Two concrete N=2 probes check a 1/2 derivative and failure of the unclipped formula under a negative scalar proposal. This is a coordinatewise directional result, not a full Fréchet theorem. No project candidate modules are imported.

Final targeted build: 2,138 jobs without warnings on Lean 4.33.1 / mathlib `0df444a360eaa60ab8c11dca51a86af692955474`; seven axiom reports show standard axioms only. `ONE_PAGE_NOTE.md`, `MUTATION_PROPOSALS.md`, `build_final.log`, and `LOG_HASHES.txt` accompany the source. Mutants and equivalence control are proposals only.

Critical gap: the reference freezes a prescribed weight and does not define the complex EMA, adaptive proposal, capacity branch or modulo. Therefore it does not establish equality to the actual engine derivative even on the u=w=0 linearized slice. Prepared-orbit and theta/history consistency assumptions also remain external. No full gate, mutation suite, independent review, push or promotion. Suggested review: check the reference derivative, then derive the fixed-weight first-order reduction from a precise interior adaptive map before claiming engine correspondence.
