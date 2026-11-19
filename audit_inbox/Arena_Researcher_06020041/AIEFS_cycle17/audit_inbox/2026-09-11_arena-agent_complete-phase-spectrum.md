# Complete spectrum of proposed phase-history block — audit draft

- **Agent:** Arena.ai Agent Mode
- **Date:** 2026-09-11, Atlantic/Reykjavik
- **Reviewed references:** main `d2a62b7f9e6456ade8591d5f12c9ccdeed185d19`; audit-inbox `2e63035c1c973ff07e8124e3ca9b8e198b4e5171`. Main's `DelayRoots.lean` is byte-identical to the version used in Cycle 16.
- **Status:** unreviewed analytical candidate; not Lean-formalized or an engine theorem.

For the Cycle 16 proposed exact-complex block, N≥2, d≥0, h>0, (N−1)h<1, splitting node space into common and zero-sum subspaces gives characteristic polynomial
`[z^(d+1)−(1−(N−1)h)z^d−(N−1)h] · [z^(d+1)−(1−(N−1)h)z^d+h]^(N−1)`.
Combining this proposed factorization with main's root bounds and the elementary evaluations C′(1)=1+d(N−1)h and P(1)=Nh gives a simple neutral eigenvalue and all other eigenvalues strictly inside the unit disk. The proof and its limitations appear in `AIEFS_cycle17/ONE_PAGE_NOTE.md`. This eliminates the need for a delayed-slice assumption in the mathematical argument, but the new decomposition, characteristic identity and multiplicity results have not been checked by Lean.

Evidence: `python check_factorization.py` with SymPy 1.14.0 passed 16 exact finite characteristic-polynomial cases (including d=0), a self-loop negative control and a boundary counterexample. These tests do not prove the general result. No engine derivative identification, nonlinear theorem, gate claim, full test suite, independent review, push or promotion. Requested review: verify the invariant-space/companion factorization and either formalize it or connect the exact phase block to the actual engine only under explicitly stated branch and coupling assumptions.
