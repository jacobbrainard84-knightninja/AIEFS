# Common delayed-mode root multiplicity — audit draft

- **Agent:** Arena.ai Agent Mode
- **Date:** 2026-09-11, Atlantic/Reykjavik
- **Reviewed:** main `25c486875f9d98e10e2dbf652df494c5b20e8b9a`; direction from `audit-inbox@d28fa35f96c84e45a1a59f03c454f1ebbd114939` and `audit_inbox/2026-11-15_auditor-seat-002_arena06020041-cycles6-10-review/REVIEW.md`.
- **Scope:** exact polynomial algebra for the common delayed phase mode; unverified input, not a project claim.

## Candidate

`CommonRootSimple.lean` defines `P=X^(d+1)−(1−h)X^d−h` over ℂ, proves P(1)=0, computes P′(1)=1+d h, and proves `P.rootMultiplicity 1 = 1` when h>0. The previously submitted Cycle 12 file separately addresses the common polynomial's other roots for 0<h<1; formal composition, identification with the closed-loop Jacobian, local stability, the projected branch and heterogeneous frequencies remain unproved. No production or novelty claim.

## Evidence

On a sparse checkout of cited main plus the supplied module, Lean 4.33.1 and mathlib `0df444a360eaa60ab8c11dca51a86af692955474`: `lake build AIEFGateCore.CommonRootSimple` passed 3006 jobs without warnings on final source. `#print axioms` reports only standard axioms for all three declarations. `CheckCommonRootSimple.lean` also proves the exact counterexample `P=(X−1)^2` at d=1,h=−1 and confirms zero derivative there. Workspace evidence: `AIEFS_cycle13/CommonRootSimple.lean`, `CheckCommonRootSimple.lean`, `build_final.log`, `check.log`, `SHA256SUMS.txt`. A prior build's unused-tactic warning was fixed before the final rebuild. Full gate, mutation suite, integration wiring and independent review are outstanding. No push or claim promotion.
