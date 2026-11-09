# AIEFGateCore (Lean 4 + Mathlib)

Lean work packages P1 and P2 (SPEC §7): branch-conditional identities of the engine-v1 capacity gate along controller-kernel
directions, which the rate-law audit (`AUD-RATELAW`; ERRATA E5, and E22 on
`research/rate-law-delta-sweep` (pending merge)) relies on. **AUD-RATELAW stays UNEXPLAINED**: this package
proves one-step real-arithmetic algebra used by the audit's estimator; it does not explain the rate law. Spec, code mapping and scope:
[`research/lean_gate/SPEC_P1_gate_identities.md`](../../research/lean_gate/SPEC_P1_gate_identities.md).
A separate Lake project so that the hash-pinned `lean/AIEFProofs` is not touched. Same toolchain
(`leanprover/lean4:v4.33.1`) and Mathlib pin (`0df444a3…`) as the other projects; depends on Mathlib only.

| declaration (namespace `AIEFGate`) | statement (real arithmetic, one step, `R` fixed) |
|---|---|
| `stepB_add_smul_of_branch` | same clip pattern on supp h, same gate decision, `h ∈ ker A_J`, controller assignment valid at both states ⇒ `stepB (B + t h) = stepB B + t(1−γdt)·branchScale·h` |
| `multiplier_eq_branch_formula` | ⇒ audit estimator `⟨ΔB'/t, h⟩/⟨h,h⟩ = (1−γdt) Σ branchScale h² / Σ h²`, independent of `t` |
| `stepB_sub_eq_smul_of_uniform` | equal controller scales on supp h ⇒ `h` is an exact eigenvector, eigenvalue `(1−γdt)s` |
| `eventually_clip_gate` | strict clip and a firing gate test persist for small `t` |
| `K3_gate_component_multiplier`, `K3_gate_branch_sub_state` | gap component `[2,7,11]`, `J={2,7}`: multiplier `(1−γdt)(min s₀ s₁+s₀+s₁)/3`; branch − state `= −(1−γdt)|s₀−s₁|/6` |
| `K3_tied_plus_exact`, `K3_tied_plus_hasDerivWithinAt` | all-tied K3: along `+vRay c`, exact eigen-response for `t ≥ 0`; right derivative `(1−γdt)s·vRay c` |
| `K3_tied_minus_exact`, `K3_tied_minus_hasDerivWithinAt`, `K3_tied_minus_not_eigen` | along `−vRay c`: node `c` controls; rational response; right derivative `(1−γdt)s(1−2x_e/(q_c+ε))`, not eigen |
| `gateOn_iff_of_branch`, `stepB_add_smul_of_branch_engine` | engine-shaped gate (`EngineGate`: `cap·q = a − delta`, `q, cap, ε > 0`): the same-gate-decision hypothesis is implied by the others; main theorem without it |
| `stepB_add_smul_of_branch_on` (+ `_engine_on`, `multiplier_…_on`, `…_uniform_on`) | (P2) same, with kernel/controller conditions only on edges with `x_e ≠ 0 ∨ h_e ≠ 0`; P1 theorems are corollaries; `RedTeam.false_rel_x_only`/`false_rel_h_only`: smaller edge sets are false; `rel_strictly_weaker` |
| `EngineWitness.engine_nonvacuous` | (P2) all hypotheses of the engine-shaped theorem hold at the frozen production parameters (exact reals, `ε = 10⁻¹²`), gate firing, binding scale |
| `MatrixForm.stepM_eq_stepB`, `stepM_symm`, `stepM_diag` | (P2) the engine's matrix step equals the edge-vector step on the complete graph for symmetric `B` and drive; `false_matrix_no_symm` |
| `RedTeam.*` | non-vacuity instance (`ε = 0`, not an engine config); proved negations of four known-false variants; `false_drop_{clip,hon,ker,hc0,hc1}`: main theorem with exactly one hypothesis dropped is false (`hon` only for a non-engine gate) |

**Scope.** Reals, not float64; edge-vector form, not the symmetric matrix; one step with `R` fixed (ERRATA E5);
exact controller order (no `TIE_TOL`). P1's `IsCtrl`/`InCtrlKer` quantify over all edges; P2's `_on` theorems
need them only on edges with `x_e ≠ 0` or `h_e ≠ 0` (SPEC §7.1). Matrix vs edge-vector form: proved for symmetric
`B` and drive (P2, SPEC §7.4).
Not formalised: the closed-form clique multiplier `λ_k`, finite-time
departure from the locked state, branch persistence over time, phases, delay, EMA.

**Check** (from this directory): `./check_lean_gate.sh` (or `SKIP_CACHE=1 ./check_lean_gate.sh` offline). Seven
steps as in `lean/AIEFFreezeCore/check_lean_freeze.sh`: toolchain, pins (`AIEF_LEAN_GATE_SOURCE_SHA256SUMS.txt`),
imports/orphans (strict), cache, clean build with 0 warnings, forbidden markers, axiom audit (only propext,
Classical.choice, Quot.sound). Local result 2026-11-09 (P2): PASS, 2032 jobs, 0 warnings, 237 declarations audited
(`GateMap.lean` imports specific Mathlib modules since P2).
Cross-check against the pinned engine: `research/lean_gate/lean_gate_crosscheck_v1.py`; mutation check:
`research/lean_gate/lean_mutation_check.py`.

`.lake/` is ignored by the root `.gitignore`. To reuse an existing Mathlib build instead of downloading the
cache, hard-link another project's packages: `cp -al ../AIEFFreezeCore/.lake/packages .lake/packages`.
