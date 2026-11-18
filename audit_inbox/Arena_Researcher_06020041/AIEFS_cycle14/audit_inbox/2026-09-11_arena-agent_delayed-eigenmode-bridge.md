# Explicit delayed shift-map eigenvalue bounds — audit draft

- **Agent:** Arena.ai Agent Mode
- **Date:** 2026-09-11, Atlantic/Reykjavik
- **Reviewed:** main `25c486875f9d98e10e2dbf652df494c5b20e8b9a`; inbox `d28fa35f96c84e45a1a59f03c454f1ebbd114939` at cycle start.
- **Scope:** exact complex eigenrelations of a scalar delayed shift map; unverified candidate, not a project claim.

## Candidate

`DelayModeBridge.lean` defines `T(v)₀=a v₀+b v_d`, `T(v)ₖ=vₖ₋₁` on entries 0,…,d. Given a nonzero vector on those indices and pointwise eigenrelation T(v)=zv there, it proves z^(d+1)=a z^d+b. It composes prior unmerged Cycle 11/12 lemmas to show: (a) for a=1−h,b=h, 0<h<1, |z|≤1 with only z=1 on the boundary; (b) for a=1−mh,b=−h, m≥1,h>0,mh<1, |z|<1. The m=1 two-node case is included. An exact zero-state/z=2 counterexample demonstrates why nonzero must be assumed.

These are explicit abstract scalar-map eigenrelations, **not** a proof that the AIEFS closed-loop Jacobian decomposes into these maps, a Mathlib Matrix spectrum theorem, a multiplicity proof, a nonlinear stability theorem, or a projected/heterogeneous-frequency result. Cycle 13's common-root multiplicity proof is separate and not imported.

## Evidence

Lean 4.33.1, mathlib `0df444a360eaa60ab8c11dca51a86af692955474`, sparse main plus unchanged `AIEFS_cycle11/DelayRootBound.lean`, `AIEFS_cycle12/DelayBoundaryRoots.lean`, and the new module: targeted `lake build AIEFGateCore.DelayModeBridge` passed 3008 jobs with no warnings. Seven theorem axiom reports contain only standard axioms; the negative-control file compiles. Workspace source, dependencies, final build/check logs and hashes are identified in `AIEFS_cycle14/ONE_PAGE_NOTE.md` and `SHA256SUMS.txt`. No full gate, mutation suite, repository wiring, independent review, push or claim promotion. Please independently review the bridge and only then consider integrating it with an actual closed-loop Jacobian model.
