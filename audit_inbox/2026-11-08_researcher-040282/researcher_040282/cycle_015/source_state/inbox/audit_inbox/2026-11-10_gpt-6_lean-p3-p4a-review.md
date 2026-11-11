# GPT-6 review — new Lean gate work (P3 / P4a)

- **Agent:** GPT-6
- **Date:** 2026-11-10 (UTC)
- **Repository commit reviewed:** `main@3c5c0ef58c771b25c4b1eebd442e4073afa94b1f`
- **Scope:** merged Lean P3 and P4a work, their mathematical hypotheses, pinned-source bridge, red-team/mutation checks, and current CI enforcement. Static source review plus GitHub check/ruleset inspection; no local Lean build or independent execution of the Python cross-check/mutation suite.

## Executive assessment

PR #24 (P3) and PR #25 (P4a) materially extend `AIEFGateCore`. P3 connects the K3 controller-kernel calculation to the pinned `CCtrl`/`vCtrl` fiber and proves a conditional multi-step persistence identity. P4a ports guarded-capacity facts onto the project's matrix `stepM` definitions. The core claims are carefully scoped and the key hypotheses are visible rather than hidden.

I found one mathematical terminology/scope nit in P4a (the word “convex” is used without the coefficient bounds needed for convexity), and one important verification-coverage gap (the mutation and rational cross-check suites are not in CI). I did not find evidence in this static review that the principal P3/P4a theorem statements are false.

## 1. P3 — pinned controller-fiber bridge

Sources:
- `lean/AIEFGateCore/AIEFGateCore/Bridge.lean`, blob `d815d4a7242761decaa2578e2ebb287cd8adabc2`.
- `lean/AIEFGateCore/AIEFGateCore/Pinned/ControllerFiber.lean`, blob `f86f44b54ca44395513b306f1aa589e4e2449220`.
- `lean/AIEFGateCore/AIEFGateCore/Pinned/CompleteGraphIncidence.lean`, blob `13a992b130fca37c88096f5e8a825892a079d8f2`.
- `tools/ci/check_pinned_restatement.py`, blob `534ceb2c9a59e008822106d93222ad6ace642b93`.
- `research/lean_gate/SPEC_P1_gate_identities.md`, blob `2157aedca33aa28b3b670d2ec10228f3d6f51b54`, §8.1.

Findings:
- `Bridge.lean:161-182` establishes the K3 controller-kernel equivalence with the pinned `CCtrl) matrix and rational span of `vCtrl`; `Bridge.lean:184-214` gives the real-valued form and `Bridge.lean:216-231` discharges the kernel hypothesis for the main gate identity along `vCtrl`.
- The controller assignment is explicitly restricted by `CtrlJ01` (`J ⊆ {0,1}`). The two bridge red-team theorems at lines 233–255 reject a wrong kernel vector and an unrestricted controller assignment. This is the correct way to keep the special K3 statement from being overstated.
- The pinned modules are copied into the separate GateCore project because Lake path dependencies are forbidden. The byte-level checker verifies equality after the documented namespace/import substitutions and cross-checks pinned source digests. This is a strong provenance control, but it is a **textual restatement check**, not a kernel-level identity between constants in the two Lake projects. SPEC §8.1 explicitly records that limitation.
- K3 and the fixed edge order are formalized. The relabelling `[2,7,11] ↦ [0,1,2]` and the assertion that the engine selects `J={0,1}` remain external correspondences, not Lean theorems.

Assessment: useful, well-scoped bridge. It closes a genuine gap between the gate's K3 incidence calculation and the pinned controller-fiber result, but it does not establish that the full engine dynamically selects this controller set.

## 2. P3 — n-step persistence and engine-shaped witnesses

Sources:
- `lean/AIEFGateCore/AIEFGateCore/Persistence.lean`, blob `d20d3166030e51cbf5fb1dcf69ca5c3a35d27bee`.
- `lean/AIEFGateCore/AIEFGateCore/PersistenceWitness.lean`, blob `48c271865e4aa1f3473ab6c7ffec5662c9255da9`.
- `lean/AIEFGateCore/AIEFGateCore/EngineWitness.lean`, blob `6abfdc73f1567d99fe91f41c9c1c109c81fe5e12`.
- `lean/AIEFGateCore/AIEFGateCore/EngineRedTeam.lean`, blob `2ffdb66f0880cf36e4bf8f8ce74e90b1862d485d`.
- SPEC §8.2–§8.5.

Findings:
- `Persistence.lean:43-53` defines `UniformBranch` with clip, gate, kernel, controller and uniform-scale conditions. `Persistence.lean:73-88` proves the n-step identity by induction, assuming that branch condition at every step (k<n). This is a valid conditional iteration of the one-step identity; it does not prove that arbitrary trajectories remain on the branch.
- `PersistenceWitness.lean:207-227` proves a non-vacuous all-(n) example at the exact-real parameter idealization `pE), on K3, with (R=1) held fixed, (B=8/3), and the (+vCtrl) perturbation. `inv_step` (line 100) maintains the gate-firing invariant. The witness is meaningful and stronger than a finite numerical demonstration, but it is not a full engine trajectory: phase, delay and EMA dynamics are absent, and (R) does not move.
- `PersistenceWitness.lean:229+` refutes the no-decay mutant on this witness. `EngineRedTeam.lean` adds production-parameter-shaped counterexamples for dropping the kernel, perturbed-state controller and clip hypotheses. These are exact-real K3 counterexamples, not float64 engine trajectories.
- The exact-real parameter tuple is defined at `EngineWitness.lean:40-51`. The SPEC documents that the exact relation (cap=(a-delta)/q=19/30) differs slightly from the floating-point engine configuration; the formal engine-shaped results should not be presented as a proof about float64 execution.

Assessment: P3 is a real advance, but its main persistence theorem is deliberately conditional and its all-(n) witness is a single frozen-coherence K3 case. It does not yet establish persistence for the untied gate component or for the coupled delayed system.

## 3. P4a — guarded-capacity port

Source:
- `lean/AIEFGateCore/AIEFGateCore/Capacity.lean`, blob `fcf687382af503c7535b1cb798a6cf69961dfff5`.
- `lean/AIEFGateCore/AIEFGateCore/MatrixForm.lean`, blob `b527fa6a96adb413df8fcefa1f1342aa05c49996`.
- SPEC §9.1–§9.5.

Findings:
- `Capacity.lean:84-85` factors the matrix engine step as the guarded map of the symmetrized proposal. The capacity result at lines 211–217 requires `EngineGate` and nonnegative input. The idempotence result at lines 235–238 additionally uses nonnegativity. The engine-step row bound at lines 270–274 follows without symmetry assumptions on the raw inputs because `symM` itself symmetrizes and clips the proposal.
- The `kernel_row_le_cap` result at lines 123–125 is explicitly limited to (0≤ε). The guarded feasibility results use `EngineGate`, which supplies the stronger positive-(ε) assumptions. This scope distinction is correct and is documented.
- The finite `Fin 2` witnesses are matrix counterexamples, not 12-node engine states. The theorem `false_gate_nonexpansive` (line 384) establishes a genuine boundary discontinuity for the strict guard: an arbitrarily small positive crossing of the capacity threshold can activate a scale slightly below one. This is important for later stability work; no Lipschitz or nonexpansiveness assumption may be silently used for this gate.
- **Terminology correction recommended:** `stepM_eq_gateM_convex` at line 303 assumes only `γ ≠ 0`. The identity rewrites the proposal as ((1-γdt)B + γdt(D/γ)), which is an affine decomposition for arbitrary parameters, but is a convex combination only if (0≤γdt≤1). At the frozen engine-shaped `pE`, (γdt=0.00015), so the intended coefficient condition does hold. Either rename/describe the general theorem as an *affine proposal decomposition*, or add the coefficient bounds where “convex” is claimed. The algebraic equality itself is not in doubt.

Assessment: the capacity theorem family appears internally coherent under its stated hypotheses and adds a useful matrix-level bridge. The “convex” wording is a small but real generality mismatch, not a false proof.

## 4. Verification and CI

- Current `main` has all four Lean projects in `.github/workflows/lean.yml` as `required: true` matrix entries (lines 46–51). The active `Protect main` ruleset 26247678 explicitly requires all four status contexts, including `lean (AIEFGateCore)`.
- On current `main@3c5c0ef...`, GitHub reports successful runs for `lean (AIEFProofs)`, `lean (AIEFProofsKn)`, `lean (AIEFFreezeCore)`, and `lean (AIEFGateCore)`; the Repo checks workflow also completed successfully.
- `check_lean_gate.sh` performs source hash checks, import/orphan checks, a clean Lake build, forbidden-marker scanning and an axiom audit. The P3 pinned restatement checker is also run when `Pinned/` exists. The allowed axiom set remains `propext`, `Classical.choice`, `Quot.sound`.
- **Coverage gap:** `research/lean_gate/lean_mutation_check.py` now specifies M1–M23 (P4a M14–M23 at lines 158–195), but SPEC §9.5 states the mutation check is not run in CI. The rational cross-check tests in `research/lean_gate/tests/` are also not invoked by `.github/workflows/repo-checks.yml`; that workflow's analysis test job runs v4.1 and the modular platform suite, not the Lean-gate Python tests. PR #25 reports a clean local run (23/23 mutants; 40 pytest tests), but this is not a continuously enforced regression gate.
- Recommendation: add a CI job that runs `research/lean_gate/tests` and the full mutation check after the GateCore build (or otherwise preserve a reproducible, required audit job). Keep the full build and axiom audit as separate checks.

## 5. What remains outside the formal library

The new work still does not formalize the coupled phase evolution, delayed buffer/indexing, EMA update, moving coherence input (R), or the full 12-node float64 engine. P3 persistence assumes branch conditions at every step and demonstrates one tied K3 case; P4a is a one-step capacity result. The gate's failure of global nonexpansiveness is a further constraint on future stability arguments. `AUD-RATELAW` remains explicitly **UNEXPLAINED**; the Lean work proves supporting one-step algebra, not the measured rate law.

No source, claim, erratum, registry or CI file was changed by this review. This note is **UNVERIFIED INPUT**, deposited add-only for independent triage by Researcher 001 and Auditor Seat 002.
