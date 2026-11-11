# AIEFGateCore (Lean 4 + Mathlib)

Lean work packages P1, P2 (SPEC §7), P3 (SPEC §8), P4a (SPEC §9, `Capacity.lean`) and P4b (SPEC §10, `Freeze.lean`, `WeightUpdate.lean`): branch-conditional identities of the engine-v1 capacity gate along controller-kernel
directions, which the rate-law audit (`AUD-RATELAW`; ERRATA E5, and E22 on
`main` (landed via PR #18)) relies on. **AUD-RATELAW stays UNEXPLAINED**: this package
proves one-step real-arithmetic algebra used by the audit's estimator; it does not explain the rate law. Spec, code mapping and scope:
[`research/lean_gate/SPEC_P1_gate_identities.md`](../../research/lean_gate/SPEC_P1_gate_identities.md).
A separate Lake project so that the hash-pinned `lean/AIEFProofs` is not touched. Same toolchain
(`leanprover/lean4:v4.33.1`) and Mathlib pin (`0df444a3…`) as the other projects; depends on Mathlib only.
`AIEFGateCore/Pinned/` (P3) holds verbatim restatements of four pinned `lean/AIEFProofs` modules (only the
`namespace`/`end` lines and internal imports renamed), byte-checked by `tools/ci/check_pinned_restatement.py`
(SPEC §8.1); do not edit them.

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
| `EngineWitness.engine_rel_strictly_weaker` | (P2) same parameters (`ε = 10⁻¹²`), an edge with `x_e = h_e = 0`: every per-edge (`_on`) hypothesis holds while the P1 all-edge kernel hypothesis fails for every controller (`engine_nonvacuous` alone has `x_e ≠ 0` everywhere, so it does not exercise the weakening) |
| `MatrixForm.stepM_eq_stepB`, `stepM_symm`, `stepM_diag` | (P2) the engine's matrix step equals the edge-vector step on the complete graph for symmetric `B` and drive; `false_matrix_no_symm` |
| `RedTeam.*` | non-vacuity instance (`ε = 0`, not an engine config); proved negations of four known-false variants; `false_drop_{clip,hon,ker,hc0,hc1}`: main theorem with exactly one hypothesis dropped is false (`hon` only for a non-engine gate) |
| `Bridge.inCtrlKer_iff_exists_smul_vCtrl`, `inCtrlKer_iff_smul_vCtrl`, `inCtrlKer_iff_CCtrl`, `incCoeff_eq_inc`, `vRay_two_eq_vCtrl`, `sc_ctrl_eq_of_PPerp_eq`, `stepB_add_smul_vCtrl` | (P3) the gate's kernel hypothesis on K3 for every controller assignment with `J ⊆ {0,1}` (`CtrlJ01`) is exactly the pinned `ker CCtrl = span vCtrl`; the gate incidence is the pinned `inc`; main theorem along `vCtrl` with `hker` discharged; `false_bridge_wrong_vector`, `false_bridge_any_ctrl` |
| `iterate_stepB_add_smul_of_branch`, `stepB_add_smul_of_uniformBranch`, `amp_mem_Icc` | (P3) if the uniform branch holds at every step `k < n`, then `stepB^[n](B + t h) = stepB^[n] B + amp n · h`, `amp n = t ∏ (1−γdt) s_k` |
| `PersistenceWitness.engine_gated_persistence` | (P3) for every `n`, at `ε = 10⁻¹²`, K3, `R` frozen, `h = vCtrl`: gate firing and binding scale at every step, branch hypothesis holds for all `k < n`; `false_iterate_no_decay` |
| `EngineRedTeam.engine_false_{drop_ker,drop_hc1,drop_clip,main_no_gamma,multiplier_no_gamma}` | (P3) the same negations at engine-shaped parameters (`ε = 10⁻¹² > 0`, `EngineGate`) |
| `Capacity.gateM_feasible`, `gateM_fixes_feasible`, `gateM_idempotent`, `stepM_row_le_cap`, `kernel_row_le_cap`, `gateM_sub_of_rowSum_eq`, `stepM_eq_gateM_convex`, `false_*`, `witness_*` | (P4a) guarded-capacity content of the matrix gate on `Params`/`GateOnM`/`stepM`, ported from the cycle-002 statements of Researcher 040282 (handle only; source path and commit in the module docstring and SPEC §9): row sums `≤ cap` for `EngineGate` (`0 < ε`), `0 ≤ ε` only for the kernel row bound, idempotence, fixed points, negations (unguarded kernel, nonexpansiveness, `ε < 0`, broken link) and `Fin 2` witnesses |
| `WeightUpdate.rowM_le_upper`, `stepM_factor_lower`, `stepM_scalar_recurrence`, `trajectory_symmetric`, `trajectory_good_of_start`, `edge_eventually_off/on(_from)`, `onGap_iff`, `onGap_N12_fails`, `false_*`, `witness_*` | (P4b) weight-update bridge of the cycle-003 deposit on `Params`/`stepM`: Lemma 1 row sandwich, gate-factor floor, scalar recurrence, trajectory invariants (B stays symmetric, nonnegative, zero-diagonal, feasible), per-edge ∃N OFF/ON freezing (`Freeze.lean` restates the scalar core), and the exact ON-certificate threshold `S < 18999999991/90000000000` at `pE`, `B_c = 3/25` (fails at the N = 12 coarse envelope) |

**Scope.** Reals, not float64; edge-vector form, not the symmetric matrix; one step with `R` fixed (ERRATA E5);
exact controller order (no `TIE_TOL`). Persistence (P3) is conditional on staying in the branch, with `R` frozen;
its witness is the tied K3 `+vCtrl` side only. P1's `IsCtrl`/`InCtrlKer` quantify over all edges; P2's `_on` theorems
need them only on edges with `x_e ≠ 0` or `h_e ≠ 0` (SPEC §7.1). Matrix vs edge-vector form: proved for symmetric
`B` and drive (P2, SPEC §7.4).
Not formalised: the closed-form clique multiplier `λ_k`, finite-time
departure from the locked state, persistence with moving `R` or non-uniform scales, phases, delay, EMA, K12 (`lean/AIEFProofsKn`).

**Check** (from this directory): `./check_lean_gate.sh` (or `SKIP_CACHE=1 ./check_lean_gate.sh` offline). Seven
steps as in `lean/AIEFFreezeCore/check_lean_freeze.sh`: toolchain, pins (`AIEF_LEAN_GATE_SOURCE_SHA256SUMS.txt`),
step 2b (P3: `Pinned/` must pass `tools/ci/check_pinned_restatement.py`), imports/orphans (strict), cache, clean
build with 0 warnings, forbidden markers, axiom audit (only propext, Classical.choice, Quot.sound). Local result
2026-11-09 (P3, `SKIP_CACHE=1`): PASS, 2149 jobs, 0 warnings, 14 source files, 439 declarations audited, 239
theorems printed with `#print axioms`, 0 disallowed.
Cross-check against the pinned engine: `research/lean_gate/lean_gate_crosscheck_v1.py`; mutation check:
`research/lean_gate/lean_mutation_check.py`. Mutation check (SPEC §7.3, §8.4, §9.3): 23 mutants, each must (a) fail to build with the kept
proof by a real proof failure (since P3 a failure made only of `Unknown identifier`/`unknown constant` errors does
not count; a classifier negative control checks this), (b) be refuted by a proved negation theorem (no `sorry`,
standard axioms only, checked with `#print axioms`; a `sorry` and an `axiom` refutation are rejected as negative
controls; M1–M5 also at engine parameters `ε = 10⁻¹²`) and (c) the same refutation term must fail on the unmutated
statement (term-specificity only). M1–M3 and M8 weaken the hypothesis to `(name : True)`, the same proposition as
dropping it, so their build rejection is a type mismatch, not a name reference. M11–M13: wrong bridge vector,
weakened controller set, persistence without decay. M14–M23 (P4a): statements of `Capacity.lean` weakened or altered, refuted by its `false_*` theorems. M24–M36 (P4b): the same for `WeightUpdate.lean`.

`.lake/` is ignored by the root `.gitignore`. To reuse an existing Mathlib build instead of downloading the
cache, hard-link another project's packages: `cp -al ../AIEFFreezeCore/.lake/packages .lake/packages`.
