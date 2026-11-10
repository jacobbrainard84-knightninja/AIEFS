# GPT-6 review — P4b weight-update and freezing bridge

- **Agent / model:** GPT-6
- **Date:** 2026-11-10 (America/Los_Angeles)
- **Main commit reviewed:** `1c30ca56e56f11517d1e04f90d521a5aa6990c52`
- **Relevant merges:** PR #26 `4988600d49a86d1c852acca4170e70b79baad0a7`; PR #27 `1c30ca56e56f11517d1e04f90d521a5aa6990c52`
- **Scope:** current-main P4b Lean additions (`Freeze.lean`, `WeightUpdate.lean`), P4b exact-rational/mutation tests, follow-up CI wiring, and the remaining documentation/test guardrails. Static source review and GitHub Actions result inspection; no local Lean build or local test execution.

## 1. Current state and concise verdict

Main has advanced beyond the prior P4a review. PR #26 merged P4b (scalar freezing restatement plus the matrix weight-update bridge); PR #27 then merged the P4a affine/convexity clarification and added the Lean mutation check and P4b/P4a Python test suite to CI.

The mathematical core of P4b is coherent as a **conditional exact-real theorem package**. It now connects the matrix step `stepM` to a scalar edge recurrence, derives a lower bound on the edge gate factor from positive-drive row bounds, and applies scalar comparison arguments to prove eventual OFF/ON under uniform infinite-tail drive hypotheses. The new trajectory invariants also remove the need to assume that symmetry is preserved.

This is meaningful progress beyond the earlier one-step gate identities. It is not a proof of the full AIEFS dynamics: the drive sequence is still an input to the theorems, not derived from phase dynamics or the EMA; the ON/OFF bands are assumed for all future steps; and the results are exact-real, not float64 implementation theorems.

## 2. P4b mathematical review

### 2.1 Matrix-to-edge recurrence and row envelope

Current source:
- `lean/AIEFGateCore/AIEFGateCore/WeightUpdate.lean`, blob `ebdd160cdd50fc2603b7eeae61e8817e8ccdb318`.
- `lean/AIEFGateCore/AIEFGateCore/MatrixForm.lean`, blob `b527fa6a96adb413df8fcefa1f1342aa05c49996`.

The proof chain is well-factored:

- `preM_eq_affine` rewrites the proposal as `(1 - γ·dt) B + dt·D`.
- `symM_eq_clip` uses symmetry of both B and D to reduce the symmetrized proposal to the clipped scalar edge proposal.
- `rowM_le_upper` bounds each proposal row by `(1 - γ·dt) rowS(B) + dt·pdriveRow(D)`, under B ≥ 0, B/D symmetric, dt ≥ 0 and γ·dt ≤ 1.
- `rowM_le_envelope` combines this with row feasibility and a positive-drive row bound.
- `stepM_scalar_recurrence` exposes the edge update as the clipped affine proposal multiplied by the actual `appliedFactor`.
- `stepM_factor_lower` turns the drive-row bounds into the uniform lower gate-factor `edgeFloor`.

The hypotheses are mathematically material, not decorative: the coefficient of B must be nonnegative for the row upper bound; symmetry is needed for the scalar recurrence; and the gate-factor floor needs the positive-drive row bounds. The P4b mutation set M24–M27 targets these dependencies.

### 2.2 Invariants and conditional freezing

`Good` packages nonnegativity, symmetry, zero diagonal and row sums ≤ cap. `good_step` proves every `stepM) output is Good under `EngineGate p`, without assumptions on the incoming matrix or drive. Consequently, from step one onward the trajectory is Good; the more general `trajectory_good_of_start` states the exact start condition.

The two edge theorems then apply the scalar comparison results in `Freeze.lean`:

- OFF: if the edge drive is uniformly bounded above by U ≥ 0 with U < γ Bc, the edge is eventually strictly below Bc.
- ON: if the edge drive is uniformly bounded below by L ≥ 0, both endpoint positive-drive row sums have uniform upper bounds, and the resulting strict gate-factor fixed-point gap exceeds Bc, the edge is eventually strictly above Bc.

The scalar lemmas in `Freeze.lean` restate five declarations from `AIEFFreezeCore/FreezeCore.lean`; the P4b Python test compares their statements textually. This is a statement-level consistency check, not a kernel-level identity between constants across Lake projects. Both projects independently compile their proofs.

### 2.3 The N=12 ON calculation is correctly limited

At the frozen exact-real parameters `pE`, with maximal edge drive D = 1/25 (R = 1) and Bc = 3/25, `onGap_iff` proves that the ON sufficient hypothesis holds exactly when the positive-drive row bound S is below

`18999999991/90000000000 ≈ 0.211111111011`.

The coarse N=12 envelope S = 11/25 = 0.44 fails that sufficient condition; the resulting comparison value is between 0.0575 and 0.0576, below Bc. Five maximally driven neighbours pass the criterion; six fail it.

This is **not** evidence that ON actually fails at N=12. It says only that this coarse uniform row-envelope certificate cannot establish ON there. The module and PR description make that distinction explicitly, which is the right scientific wording.

The `witness_on_instance` and `witness_off_instance` are useful non-vacuity controls, but they are constant-drive Fin 2 examples, not an N=12 trajectory generated from phases and EMA.

### 2.4 Remaining model boundary

The theorem statements are explicit that the edge theorems require 0 < dt, 0 < γ and γ·dt < 1. The engine's parameter validation permits γ = 0 and γ·dt ≥ 1, so those legal configurations are outside these freezing theorems. The row-sandwich theorem separately uses dt ≥ 0 and γ·dt ≤ 1.

The drive D remains an arbitrary symmetric sequence subject to the stated bounds. No theorem here derives those bounds from the phase update, delayed history buffer, coherence EMA, or a coupled trajectory. No float64 rounding, TIE_TOL, delay τ, or phase dynamics are formalized. Thus the correct status is **conditional weight-subsystem formalization**, not full-system freezing or convergence.

## 3. PR #27 follow-up: good closure, two small guardrail notes

PR #27 fixes the P4a wording issue I raised: `stepM_eq_gateM_convex` is accurately described as an affine rewriting when only γ ≠ 0 is assumed; `convex_weights_iff` and `preM_between` add the missing 0 ≤ γ·dt ≤ 1 condition for a true convex pair. The source docstring now states this distinction. The counterexample `false_preM_between_no_bound` correctly demonstrates why the upper bound is needed.

The new CI wiring is present in:
- `.github/workflows/lean.yml`, blob `b36b3e2ca396e89ac62d4ad7e8ff13deab148bc7`, lines 90–102: mutation check on the AIEFGateCore matrix row.
- `.github/workflows/repo-checks.yml`, blob `790a1e429d01b1f17f97cada9b7db43325cec79d`, lines 189–195: pytest for `research/lean_gate/tests`.

GitHub Actions on main commit `1c30ca56...` reports all 13 check runs completed successfully, including `lean (AIEFGateCore)`, the other three Lean projects, CI tool self-tests, and the analysis tests. This verifies that the new CI steps ran on the current main commit; it is not an independent scientific audit of the hypotheses.

Two low-cost hardening items remain:

1. The workflow's mutation step exits successfully with an echo on non-AIEFGateCore rows. The existing `tools/ci/tests/test_lean_presence.py` blob `06e06b92869fabff12473704c164b5bc05e6f7fc`, lines 264–266, does assert the exact four matrix project names, so the specific row-rename scenario is already caught by the tool self-tests. However, `workflow_problems` does not assert that the mutation-check step itself exists or invokes `research/lean_gate/lean_mutation_check.py`. Add a focused test that fails if that step is removed, its project predicate changes, or its command becomes a no-op.

2. The P4b test `research/lean_gate/tests/test_lean_gate_p4b.py`, blob `ca827df6cdd9352a46105590be278f9c9709dda3`, line 54, contains:
   `assert SSTAR == Fr(19, 90) - Fr(1, 10**10) and float(SSTAR) == float(Fr(19, 90)) - 1e-10 or True`.
   Python's operator precedence makes the entire assertion always true. Other exact-rational assertions do test `on_gap(SSTAR) == BC` and the strict sides of the threshold, so this does not invalidate the theorem or all threshold coverage; it does mean the explicit cross-check against the simplified closed form is dead. Replace it with a direct exact assertion (and, if desired, a separate approximate-float assertion without `or True`).

A documentation tidy-up is also warranted: search the current README and SPEC for residual prose describing the P4a proposal as a convex combination without the new bounds, and align it with the corrected theorem docstring.

## 4. Verification limits and source record

- **Read:** current-main P4b/P4a Lean sources, P4b test, Lean and repo-check workflows, and the relevant workflow guard test.
- **Observed remotely:** all 13 GitHub check runs for current main commit `1c30ca56...` succeeded.
- **Not run by this reviewer:** local Lake build, local pytest, mutation suite, or a numerical N=12 trajectory. The P4b PR description reports its independent audit results (599 declarations, 36/36 mutants killed, 229 pytest passes); those figures remain PR-reported, not independently rerun here.
- **Not established:** phase locking, EMA consistency, delayed recurrence, float64 correspondence, or any actual N=12 ON/OFF classification from the coupled engine.

## 5. Triage status

This is an add-only review note. It does not change source, registry, errata, CI, or briefing files. The findings above are **UNVERIFIED INPUT** until Researcher 001 and Auditor Seat 002 independently triage them. No approval or promotion is requested.
