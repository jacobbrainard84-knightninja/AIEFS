# Phase reference orbit and direct probes — audit draft

- **Agent:** Arena.ai Agent Mode
- **Date:** 2026-09-11, Atlantic/Reykjavik
- **Base:** main `d2a62b7f9e6456ade8591d5f12c9ccdeed185d19`; inbox `d2f62c9f4f3dc039cb5f88af1ea6f59c5bda3837`.
- **Status:** locally kernel-checked revision, unreviewed and not an adaptive-engine theorem.

The revised `EngineStepRef.lean` adds an orbit-invariance theorem under the stated frequency equation, direct N=2 self-delay and unequal-adjacent-history probes, and an explicit clipped-vs-unclipped comparison. Engine source comments include the filename, pinned main SHA and exact line ranges. The old fixed-weight directional derivative remains.

**Sign clarification:** for the defined history `theta−k·dt·Ω`, advancing the orbit is `orbitPath(k)+dt·Ω`. At k=1 the shifted value is the old current angle theta. The minus sign in the relayed suggested statement would be incorrect in general; the checked theorem uses plus.

The final targeted build passed 2,138 jobs without warnings on Lean 4.33.1 and mathlib `0df444a360eaa60ab8c11dca51a86af692955474`; ten axiom reports contain only standard axioms. `ONE_PAGE_NOTE.md`, `MUTATION_PROPOSALS.md`, `build_final.log` and `LOG_HASHES.txt` accompany the source. Mutations are proposed, not run. The reference still freezes weight and omits the adaptive EMA/weight step, projection branch and modulo; Python-state correspondence and nonlinear stability are not proved. No full gate, independent network-off audit, repository integration, push or promotion.
