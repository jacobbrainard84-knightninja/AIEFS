# Cycle 002 preregistration

Question: formalize the exact post-positivity guarded capacity map's basic
properties without substituting its unconditional scaling kernel.

Target: the same mathematical definition as the first note. Use nonnegative
finite matrices, nonnegative node capacities and epsilon > 0. The engine
specialization has uniform capacity. Exact-real proof is not a float64 theorem.

Planned claims:
- nonnegative row sums and scales;
- unconditional kernel structure and row-capacity bound;
- guarded feasibility, identity on feasible inputs, and idempotence;
- unchanged-full-row-sum difference identity if achievable in this bounded cycle;
- exact rational counterexamples separating unconditional and guarded maps.

Evidence route: compiled standalone Lean source under the repository's recorded
Lean/mathlib toolchain, plus explicit #print axioms output. No sorry, admit,
native_decide or extra axioms. If dependency setup fails, retain a precise proof
candidate and label it uncompiled; do not report setup failure as a red-team win.

Adversarial plan (before compiling the candidate):
1. A false unconditional-idempotence statement must fail Lean compilation for
   mathematical reasons after its dependencies and definitions load.
2. A known-false capacity instance with epsilon < 0 must fail.
3. Replacing endpoint min with max must have a nonnegative counterexample.
4. Removing nonnegativity must have a signed counterexample, ideally with all
   row sums still nonnegative so denominator positivity is not the only issue.
5. A file with a sorry proof must not be counted as verified even if Lean exits 0.
6. A file using a new axiom must not be counted as verified even if Lean exits 0.
7. At least one nonzero active-gate witness must satisfy the retained hypotheses.

Fresh source refresh: current main metadata and selected files were fetched
read-only. The earlier audit-inbox report remains scoped to its original target.
No registry/inbox/main source is modified by this cycle.

No numerical acceptance tolerance will be introduced for the formal claims.
The exact-rational counterexamples have no floating tolerance. Previously
reported float checks retain their original scope and tolerance.
