#!/usr/bin/env python3
"""Lean P1/P2/P3 red team, part 2: mutation check of lean/AIEFGateCore.

Each mutant changes a theorem STATEMENT (weakens a hypothesis to `True`, shrinks an edge set, drops a constant,
replaces the bridge vector, ...) in a copy of its source file and keeps the original proof. A mutant counts as
REJECTED only if ALL of the following hold:

  (a) build rejection: the mutated file, written to a temporary directory outside the project and elaborated with
      `lake env lean`, fails (the kept proof no longer goes through) AND the failure is a real proof failure (type
      mismatch, unsolved goals, failed rewrite, ...). P3 rule change: a failure consisting only of name-reference
      errors ("Unknown identifier" / "unknown constant") no longer counts as a build rejection, because it says
      nothing about the mutated statement (it only shows the proof mentions a deleted binder name). For that reason
      M1-M3 now weaken the hypothesis to `(name : True)` instead of deleting it: `True -> P` is equivalent to `P`,
      so the mutated statement is the same proposition as "hypothesis dropped", the binder name stays in scope, and
      the kept proof must fail on the type (M8 likewise: its P2 deletion form failed with name errors plus one
      cascading `rfl` failure, so it was only formally a "real" failure). Classifier negative control: the P2 deletion form of M1 is still run
      and must be classified NAME-REFERENCE ONLY and NOT counted as a build rejection;
  (b) semantic rejection (P2): the mutated statement itself is REFUTED by a proved negation theorem. The script
      extracts the mutated statement from the mutated file, closes it over its section variables, and elaborates
          theorem aief_refutation : ¬ (∀ <section variables> <binders>, <conclusion>) :=
            fun H => <negation theorem> (H <instance>)
          #print axioms aief_refutation
      against the built project (`import AIEFGateCore`). The refutation counts only if Lean exits 0, reports no
      error, the output contains neither "declaration uses" nor "sorry", and `#print axioms aief_refutation` lists
      only propext / Classical.choice / Quot.sound (so a `sorry`- or `axiom`-based "refutation" is not accepted;
      see the negative controls below). This is a real Lean proof that the mutant is false, not a name reference.
      P3: for M1-M5 a SECOND refutation at the frozen engine parameters `EngineWitness.pE` (`ε = 10⁻¹² > 0`,
      `EngineRedTeam.engine_false_*`) must also pass the same validator, so these mutants are refuted at an
      engine-shaped instance and not only at the toy `RedTeam.p0` (`ε = 0`);
  (c) term-specificity control: the same refutation term applied to the UNMUTATED statement must FAIL to elaborate.
      This only shows that the refutation term depends on the mutation (any type mismatch satisfies it); it is NOT
      a semantic control and adds no evidence beyond (b). (That the unmutated statement is true is shown separately
      by the positive control below: the unmutated file, with its proof, elaborates.) Checked for every
      refutation term (toy and engine).

Negative controls of the step-(b) validator (must be REJECTED, else the run fails): a refutation whose term is
`sorry`, and a refutation that uses a freshly declared `axiom aief_cheat : False`.

The unmutated files must elaborate cleanly (positive control). Exit 0 iff every control passes and every mutant is
rejected in senses (a), (b) and (c). Requires a built project (`lake build` in lean/AIEFGateCore) for step (b).

Mutants (statement -> negation theorem used in step (b); "+ engine" = second refutation at pE):
  M1 stepB_add_smul_of_branch, hker := True           -> RedTeam.false_drop_ker + engine_false_drop_ker
  M2 stepB_add_smul_of_branch, hc1 := True            -> RedTeam.false_drop_hc1 + engine_false_drop_hc1
  M3 stepB_add_smul_of_branch, hclip := True          -> RedTeam.false_drop_clip + engine_false_drop_clip
  M4 stepB_add_smul_of_branch without (1 - γ dt)      -> RedTeam.false_main_no_gamma + engine_false_main_no_gamma
  M5 multiplier_eq_branch_formula without (1 - γ dt)  -> RedTeam.false_multiplier_no_gamma
                                                         + engine_false_multiplier_no_gamma
  M6 stepB_add_smul_of_branch_on, edge set x_e ≠ 0    -> RedTeam.false_rel_x_only
  M7 stepB_add_smul_of_branch_on, edge set h_e ≠ 0    -> RedTeam.false_rel_h_only
  M8 MatrixForm.stepM_eq_stepB, hD hB := True         -> MatrixForm.false_matrix_no_symm
  M9 EngineWitness.engine_nonvacuous without (1-γdt)  -> EngineWitness.engine_false_no_gamma
  M10 EngineWitness.engine_rel_strictly_weaker with "¬ InCtrlKer" -> "InCtrlKer" (the all-edge kernel condition
      claimed to hold) -> refuted by the unmutated theorem's own clause at ctrl = ctrlX
  M11 Bridge.inCtrlKer_iff_smul_vCtrl with the pinned vCtrl replaced by the pinned vRay 0 (wrong kernel vector)
      -> Bridge.false_bridge_wrong_vector
  M12 Bridge.inCtrlKer_iff_smul_vCtrl with CtrlJ01 weakened to "ctrl e is an endpoint of e" (J not restricted)
      -> Bridge.false_bridge_any_ctrl
  M13 iterate_stepB_add_smul_of_branch with the amplitude amp n replaced by t (no decay)
      -> PersistenceWitness.false_iterate_no_decay

  P4a (Capacity.lean, port of the guarded-capacity statements of Researcher 040282; all refuted at the frozen
  `pE` (`ε = 10⁻¹²`) except M14 (`ε < 0`, `pN`) and M22/M23 (`EngineGate` link broken, `pB`)):
  M14 Capacity.kernel_row_le_cap, hε (0 ≤ ε) := True       -> Capacity.false_kernel_row_no_eps (ε = -1/2)
  M15 Capacity.gateM_idempotent, gate -> unguarded kernel    -> Capacity.false_kernel_idempotent
  M16 Capacity.gateM_fixes_feasible, hf (feasible) := True   -> Capacity.false_fixes_without_feasible
  M17 Capacity.gateM_feasible, `≤ cap` -> `< cap`            -> Capacity.false_row_lt_cap
  M18 Capacity.gateM_le_input, inequality reversed           -> Capacity.false_le_reversed
  M19 Capacity.gateM_sub_of_rowSum_eq, hrow := True          -> Capacity.false_diff_without_equal_rows
  M20 Capacity.kernel_row_lower, hℓ := True                  -> Capacity.false_kernel_lower_no_hyp
  M21 Capacity.gateM_symm, hs (symmetry) := True             -> Capacity.false_gateM_symm_no_hs
  M22 Capacity.gateM_feasible, hp (EngineGate) := True       -> Capacity.false_gateM_feasible_no_link
  M23 Capacity.stepM_row_le_cap, hp (EngineGate) := True     -> Capacity.false_stepM_row_no_link

  P4b (WeightUpdate.lean, port of the cycle-003 weight-update bridge of Researcher 040282; statement -> negation
  theorem, all at the frozen `pE` except M24 (`γ dt = 2`, `pH`)):
  M24 WeightUpdate.rowM_le_upper, hh1 (γ dt ≤ 1) := True        -> WeightUpdate.false_rowM_upper_no_hh1
  M25 WeightUpdate.stepM_scalar_recurrence, hB (B symmetric) := True -> WeightUpdate.false_recurrence_no_symm
  M26 WeightUpdate.appliedFactor_lower, hi (row bound) := True   -> WeightUpdate.false_factor_lower_no_rowbound
  M27 WeightUpdate.stepM_factor_lower, hSi, hSj := True          -> WeightUpdate.false_factor_lower_no_drivebounds
  M28 WeightUpdate.trajectory_symmetric, hB0 := True             -> WeightUpdate.false_trajectory_symmetric_no_start
  M29 WeightUpdate.trajectory_zero_diag, hB0 := True             -> WeightUpdate.false_trajectory_diag_no_start
  M30 WeightUpdate.trajectory_nonneg, hB0 := True                -> WeightUpdate.false_trajectory_nonneg_no_start
  M31 WeightUpdate.trajectory_good_of_start, hstart := True      -> WeightUpdate.false_good_no_start
  M32 WeightUpdate.edge_eventually_off_from, hUc := True         -> WeightUpdate.false_off_no_gap_from (ON instance)
  M33 WeightUpdate.edge_eventually_on_from, hgap := True         -> WeightUpdate.false_on_no_gap_from (OFF instance)
  M34 WeightUpdate.edge_eventually_off, hUc := True              -> WeightUpdate.false_off_no_gap
  M35 WeightUpdate.edge_eventually_on, hgap := True              -> WeightUpdate.false_on_no_gap
  M36 WeightUpdate.onGap_iff, `S < Sstar` -> `S ≤ Sstar`          -> WeightUpdate.false_gap_at_threshold

  #27 (Capacity.lean follow-ups; numbered M57-M58 because M37-M56 are the P5 definition mutants):
  M57 Capacity.preM_between, h1 (γ dt ≤ 1) := True                -> Capacity.false_preM_between_no_bound (γ = 1, dt = 2)
  M58 Capacity.convex_weights_iff, `γ dt ≤ 1` dropped              -> (γ = 1, dt = 2: the left side fails, the mutant's right holds)

  c016 (CoherenceMotion.lean, port of cycle 016):
  M59 trace_step_abs_le, `2*(1-alpha)` -> `(1-alpha)/2`      -> CoherenceMotion.false_trace_step_abs_le_half

  P5 (PhaseCoherence.lean / PhaseIncrement.lean, port of cycles 010, 011, 013 of Researcher 040282): DEFINITION
  mutants, a second kind (see `DEF_MUTANTS` below, numbered M37 ff. because M24-M36 are the P4b statement mutants).
  A mutated definition has no statement to refute by a negation theorem, so the (b)/(c) steps do not apply. RULE
  (revised after the audit of 64f39eb, which showed that the first version scored semantically EQUIVALENT rewrites
  such as `* 1`, `+ 0`, `id (...)` and even a misspelled identifier as killed, i.e. it measured proof brittleness):
  a definition mutant is KILLED iff
    (1) the mutated file fails to build;
    (2) NO error line anywhere is a name-reference error (Unknown identifier / constant / namespace) or a parse error
        (unexpected token, expected ...): such a mutant is INVALID and fails the run (it says nothing about semantics);
    (3) at least one of the VALUE PROBES declared for that mutant (closed-form value equalities, `VALUE_PROBES`)
        fails. A rewrite lemma such as `input_engine_convention` or `delayed_input_step` failing does NOT count: it
        fails under equivalent rewrites too.
  Negative controls, all of which must come out as expected or the run FAILS: EQUIV_CONTROLS (semantically equal
  definitions: `* 1`, `+ 0`, `id`, a reordered EMA sum, a commuted `reported`, `not (n < d)` for `d <= n`, a
  different proof term for the oldest slot, a commuted `(eta + mu)`) must NOT be killed; TYPO_CONTROLS (a misspelled
  identifier, syntax garbage) must be classified INVALID and not killed. The statement mutants M1-M23 are protected
  by step (b) (a typo or an equivalent statement cannot be refuted by a proved negation); STATEMENT_CONTROLS checks
  one of each, and every statement mutant whose build output contains a name-reference/parse error line is flagged
  (information only, the verdict is unchanged). `KNOWN_SURVIVORS` lists mutants that are expected to survive; they
  are run and reported but do not enter the count (the list is empty since N2).
  (N1) KILLED means "a pre-declared closed-number VALUE probe FAILS TO BUILD", not "the mutant computes a different
  value": the harness never evaluates the mutated definition, it only sees which probe declarations no longer
  elaborate. (N2) M53-M56 mutate the static offset (ω_i + ω_j)/2 · τ (wrong index, dropped, node-uniform ω); they are
  killed only by the asymmetric-ω probes (ω = (1, 0)), because every earlier probe has node-uniform ω.

Usage: python research/lean_gate/lean_mutation_check.py   (needs elan/lake and a built project)
"""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PROJ = REPO / "lean" / "AIEFGateCore"
SRCDIR = PROJ / "AIEFGateCore"

# Closures over the section variables of each file, and how to instantiate them for the negation theorem.
GATE_VARS = "{V E : Type} [DecidableEq V] [Fintype E] (p : Params) (G : Graph V E)"
GATE_INST = "@H (Fin 3) (Fin 3) _ _ RedTeam.p0 G3"
pL = "    (hclip : ∀ e, h e ≠ 0 → 0 ≤ pre p drive B e ∧ 0 ≤ pre p drive (B + t • h) e)\n"
REL = "(Rel (prop p drive B) h)"

ENGINE_INST = "@H (Fin 3) (Fin 3) _ _ EngineWitness.pE G3"
CAP_VARS = "{V : Type} [Fintype V] [LinearOrder V] (p : Params)"
XO_NN = "(Capacity.Xo_nonneg (by norm_num [EngineWitness.pE]))"
GP = "EngineWitness.engineGate_pE"
WU_VARS = CAP_VARS + " (B D : ℕ → V → V → ℝ)"
WU_FAC = ("(by norm_num [EngineWitness.pE]) (by norm_num [EngineWitness.pE]) (by norm_num [EngineWitness.pE])"
          " (fun n => rfl) (fun n i j => Capacity.Xo_symm _ i j) ")


def via(inst, binders, pos):
    """Term `fun <binders without pos> => inst <binders with `trivial` at pos>` (feeds `True` to H)."""
    bs = binders.split()
    lam = " ".join(b for i, b in enumerate(bs) if i != pos)
    app = " ".join("trivial" if i == pos else b for i, b in enumerate(bs))
    return f"(fun {lam} => {inst} {app})"


MAIN_BINDERS = "drive B h t ctrl hclip hon hker hc0 hc1"   # binder order of stepB_add_smul_of_branch

MUTANTS = [
    # name, file, theorem, [(old, new, count)], closure vars, refutation term, engine refutation term (or None)
    ("M1_kernel_hypothesis_weakened_to_True", "GateMap.lean", "stepB_add_smul_of_branch",
     [("    (hker : InCtrlKer G ctrl h)\n", "    (hker : True)\n", 1)], GATE_VARS,
     f"RedTeam.false_drop_ker {via(GATE_INST, MAIN_BINDERS, 7)}",
     f"EngineRedTeam.engine_false_drop_ker {via(ENGINE_INST, MAIN_BINDERS, 7)}"),
    ("M2_perturbed_controller_hypothesis_weakened_to_True", "GateMap.lean", "stepB_add_smul_of_branch",
     [("    (hc1 : IsCtrl p G (prop p drive (B + t • h)) ctrl) :\n", "    (hc1 : True) :\n", 1)], GATE_VARS,
     f"RedTeam.false_drop_hc1 {via(GATE_INST, MAIN_BINDERS, 9)}",
     f"EngineRedTeam.engine_false_drop_hc1 {via(ENGINE_INST, MAIN_BINDERS, 9)}"),
    ("M3_clip_hypothesis_weakened_to_True", "GateMap.lean", "stepB_add_smul_of_branch",
     [(pL, "    (hclip : True)\n", 1)], GATE_VARS,
     f"RedTeam.false_drop_clip {via(GATE_INST, MAIN_BINDERS, 5)}",
     f"EngineRedTeam.engine_false_drop_clip {via(ENGINE_INST, MAIN_BINDERS, 5)}"),
    ("M4_wrong_constant_no_gamma_dt", "GateMap.lean", "stepB_add_smul_of_branch",
     [("t * (1 - p.γ * p.dt) * branchScale p G drive B ctrl e * h e", "t * branchScale p G drive B ctrl e * h e", 1)],
     GATE_VARS, f"RedTeam.false_main_no_gamma ({GATE_INST})",
     f"EngineRedTeam.engine_false_main_no_gamma ({ENGINE_INST})"),
    ("M5_multiplier_wrong_constant", "GateMap.lean", "multiplier_eq_branch_formula",
     [("      (1 - p.γ * p.dt) * (∑ e, branchScale p G drive B ctrl e * h e ^ 2) / ∑ e, h e ^ 2",
       "      (∑ e, branchScale p G drive B ctrl e * h e ^ 2) / ∑ e, h e ^ 2", 1)],
     GATE_VARS, f"RedTeam.false_multiplier_no_gamma ({GATE_INST})",
     f"EngineRedTeam.engine_false_multiplier_no_gamma ({ENGINE_INST})"),
    ("M6_edge_set_x_only", "GateMap.lean", "stepB_add_smul_of_branch_on",
     [(REL, "(fun e => prop p drive B e ≠ 0)", 3)], GATE_VARS, f"RedTeam.false_rel_x_only ({GATE_INST})", None),
    ("M7_edge_set_h_only", "GateMap.lean", "stepB_add_smul_of_branch_on",
     [(REL, "(fun e => h e ≠ 0)", 3)], GATE_VARS, f"RedTeam.false_rel_h_only ({GATE_INST})", None),
    ("M8_matrix_symmetry_weakened_to_True", "MatrixForm.lean", "stepM_eq_stepB",
     [("(hD : ∀ i j, D i j = D j i)\n    (hB : ∀ i j, Bm i j = Bm j i) ", "(hD : True)\n    (hB : True) ", 1)],
     "{V : Type} [Fintype V] [LinearOrder V] (p : Params)",
     "MatrixForm.false_matrix_no_symm (fun D Bm e => @H (Fin 2) _ _ MatrixForm.pT D Bm trivial trivial e)", None),
    ("M9_engine_witness_no_gamma_dt", "EngineWitness.lean", "engine_nonvacuous",
     [("((1 / 10) * (1 - 15 / 1000 * (1 / 100)) * sE) • vRay 2", "((1 / 10) * sE) • vRay 2", 1)],
     "", "EngineWitness.engine_false_no_gamma H.2.2.2.2.2.2.2.2.2", None),
    ("M10_engine_weakening_claims_all_edge_kernel", "EngineWitness.lean", "engine_rel_strictly_weaker",
     [("      ¬ InCtrlKer G3 ctrl hw) ∧", "      InCtrlKer G3 ctrl hw) ∧", 1)], "",
     "(EngineWitness.engine_rel_strictly_weaker.2.2.2.2.1 RedTeam.ctrlX EngineWitness.ctrlX_mem)"
     " (H.2.2.2.2.1 RedTeam.ctrlX EngineWitness.ctrlX_mem)", None),
    ("M11_bridge_wrong_kernel_vector", "Bridge.lean", "inCtrlKer_iff_smul_vCtrl",
     [("∃ a : ℝ, h = a • toR vCtrl", "∃ a : ℝ, h = a • toR (CompleteGraphIncidence.vRay 0)", 1)], "",
     "Bridge.false_bridge_wrong_vector (fun _ hc h => H hc h)", None),
    ("M12_bridge_controller_set_unrestricted", "Bridge.lean", "inCtrlKer_iff_smul_vCtrl",
     [("(hc : CtrlJ01 ctrl)", "(hc : ∀ e, ctrl e = G3.src e ∨ ctrl e = G3.dst e)", 1)], "",
     "Bridge.false_bridge_any_ctrl (fun _ hc h => H hc h)", None),
    ("M13_persistence_no_decay", "Persistence.lean", "iterate_stepB_add_smul_of_branch",
     [("(stepB p G drive)^[n] B + amp p t s n • h", "(stepB p G drive)^[n] B + t • h", 1)], GATE_VARS,
     f"PersistenceWitness.false_iterate_no_decay ({ENGINE_INST})", None),
    # ---- P4a: Capacity.lean (statement -> negation theorem, all at engine-shaped parameters but M14/M22/M23) ----
    ("M14_capacity_eps_nonneg_dropped", "Capacity.lean", "kernel_row_le_cap",
     [("(hε : 0 ≤ p.ε)", "(hε : True)", 1)], CAP_VARS,
     f"Capacity.false_kernel_row_no_eps (@H (Fin 2) _ _ Capacity.pN (Capacity.Xo (3 / 2)) {XO_NN}"
     " (by norm_num [Capacity.pN]) trivial 0)", None),
    ("M15_capacity_idempotence_unguarded", "Capacity.lean", "gateM_idempotent",
     [("gateM p (gateM p X) = gateM p X", "kernelM p (kernelM p X) = kernelM p X", 1)], CAP_VARS,
     f"Capacity.false_kernel_idempotent (@H (Fin 2) _ _ pE {GP} (Capacity.Xo pE.cap) {XO_NN})", None),
    ("M16_capacity_fixes_without_feasibility", "Capacity.lean", "gateM_fixes_feasible",
     [("(hf : ∀ i, rowS X i ≤ p.cap)", "(hf : True)", 1)], CAP_VARS,
     f"Capacity.false_fixes_without_feasible (@H (Fin 2) _ _ pE {GP} (Capacity.Xo 1) trivial)", None),
    ("M17_capacity_strict_bound", "Capacity.lean", "gateM_feasible",
     [("rowS (gateM p X) i ≤ p.cap", "rowS (gateM p X) i < p.cap", 1)], CAP_VARS,
     f"Capacity.false_row_lt_cap (@H (Fin 2) _ _ pE {GP} (Capacity.Xo pE.cap) {XO_NN} 0)", None),
    ("M18_capacity_gate_ge_input", "Capacity.lean", "gateM_le_input",
     [("gateM p X i j ≤ X i j", "X i j ≤ gateM p X i j", 1)], CAP_VARS,
     f"Capacity.false_le_reversed (@H (Fin 2) _ _ pE (Capacity.Xo 1) {XO_NN} 0 1)", None),
    ("M19_capacity_difference_without_equal_rows", "Capacity.lean", "gateM_sub_of_rowSum_eq",
     [("(hrow : ∀ i, rowS X i = rowS Y i)", "(hrow : True)", 1)], CAP_VARS,
     "Capacity.false_diff_without_equal_rows (@H (Fin 2) _ _ pE (Capacity.Xo 0) (Capacity.Xo 1)"
     " (Capacity.Xo_diag 0) (Capacity.Xo_diag 1) trivial 0 1)", None),
    ("M20_capacity_lower_bound_without_scale_hypothesis", "Capacity.lean", "kernel_row_lower",
     [("(hℓ : ∀ k, ℓ ≤ scale p (rowS X k))", "(hℓ : True)", 1)], CAP_VARS,
     f"Capacity.false_kernel_lower_no_hyp (@H (Fin 2) _ _ pE (Capacity.Xo 1) {XO_NN}"
     " (Capacity.Xo_diag 1) 1 trivial 0)", None),
    ("M21_capacity_symmetry_dropped", "Capacity.lean", "gateM_symm",
     [("(hs : ∀ i j, X i j = X j i)", "(hs : True)", 1)], CAP_VARS,
     "Capacity.false_gateM_symm_no_hs (@H (Fin 2) _ _ pE Capacity.Xn trivial 0 1)", None),
    ("M22_capacity_engine_gate_dropped", "Capacity.lean", "gateM_feasible",
     [("(hp : EngineGate p)", "(hp : True)", 1)], CAP_VARS,
     f"Capacity.false_gateM_feasible_no_link (@H (Fin 2) _ _ Capacity.pB trivial (Capacity.Xo (3 / 4)) {XO_NN} 0)",
     None),
    ("M23_capacity_stepM_engine_gate_dropped", "Capacity.lean", "stepM_row_le_cap",
     [("(hp : EngineGate p)", "(hp : True)", 1)], CAP_VARS,
     "Capacity.false_stepM_row_no_link (@H (Fin 2) _ _ Capacity.pB trivial (Capacity.Xo 75)"
     " (fun _ _ => (0 : ℝ)) 0)", None),
    # ---- P4b: WeightUpdate.lean (statement -> negation theorem) ----
    ("M24_weight_update_row_upper_gamma_dt_dropped", "WeightUpdate.lean", "rowM_le_upper",
     [("(hh1 : p.γ * p.dt ≤ 1)", "(hh1 : True)", 1)], CAP_VARS,
     "WeightUpdate.false_rowM_upper_no_hh1 (@H (Fin 2) _ _ WeightUpdate.pH (Capacity.Xo 0) (Capacity.Xo 1)"
     " (Capacity.Xo_symm 0) (Capacity.Xo_symm 1) (by norm_num [WeightUpdate.pH]) trivial"
     " (Capacity.Xo_nonneg (by norm_num)) 0)", None),
    ("M25_weight_update_recurrence_symmetry_dropped", "WeightUpdate.lean", "stepM_scalar_recurrence",
     [("(hB : ∀ i j, Bm i j = Bm j i)", "(hB : True)", 1)], CAP_VARS,
     "WeightUpdate.false_recurrence_no_symm (@H (Fin 2) _ _ EngineWitness.pE (Capacity.Xo 0) Capacity.Xn"
     " (Capacity.Xo_symm 0) trivial 0 1 (by decide))", None),
    ("M26_weight_update_factor_floor_row_bound_dropped", "WeightUpdate.lean", "appliedFactor_lower",
     [("(hi : rowS X i ≤ Mi)", "(hi : True)", 1)], CAP_VARS,
     "WeightUpdate.false_factor_lower_no_rowbound (@H (Fin 2) _ _ EngineWitness.pE EngineWitness.engineGate_pE"
     " WeightUpdate.Xr WeightUpdate.Xr_nonneg 0 1 0 0 trivial (by simp [Capacity.rowS, WeightUpdate.Xr, Fin.sum_univ_two]))", None),
    ("M27_weight_update_drive_bounds_dropped", "WeightUpdate.lean", "stepM_factor_lower",
     [("(hSi : pdriveRow D i ≤ Si)", "(hSi : True)", 1), ("(hSj : pdriveRow D j ≤ Sj)", "(hSj : True)", 1)],
     CAP_VARS,
     "WeightUpdate.false_factor_lower_no_drivebounds (@H (Fin 2) _ _ EngineWitness.pE EngineWitness.engineGate_pE"
     " (by norm_num [EngineWitness.pE]) (by norm_num [EngineWitness.pE]) (Capacity.Xo 100) (fun _ _ => (0 : ℝ))"
     " (Capacity.Xo_symm 100) (fun _ _ => rfl) (fun _ _ => le_rfl)"
     " (fun i => by simp [Capacity.rowS]; norm_num [EngineWitness.pE]) 0 1 0 0 trivial trivial)", None),
    ("M28_weight_update_symmetric_start_dropped", "WeightUpdate.lean", "trajectory_symmetric",
     [("(hB0 : ∀ i j, B 0 i j = B 0 j i)", "(hB0 : True)", 1)], WU_VARS,
     "WeightUpdate.false_trajectory_symmetric_no_start (@H (Fin 2) _ _ EngineWitness.pE"
     " (WeightUpdate.orbit (fun _ => Capacity.Xo 0) Capacity.Xn) (fun _ => Capacity.Xo 0) (fun n => rfl) trivial 0 0 1)",
     None),
    ("M29_weight_update_zero_diag_start_dropped", "WeightUpdate.lean", "trajectory_zero_diag",
     [("(hB0 : ∀ i, B 0 i i = 0)", "(hB0 : True)", 1)], WU_VARS,
     "WeightUpdate.false_trajectory_diag_no_start (@H (Fin 2) _ _ EngineWitness.pE"
     " (WeightUpdate.orbit (fun _ => Capacity.Xo 0) (fun _ _ => 1)) (fun _ => Capacity.Xo 0) (fun n => rfl) trivial 0 0)",
     None),
    ("M30_weight_update_nonneg_start_dropped", "WeightUpdate.lean", "trajectory_nonneg",
     [("(hB0 : ∀ i j, 0 ≤ B 0 i j)", "(hB0 : True)", 1)], WU_VARS,
     "WeightUpdate.false_trajectory_nonneg_no_start (@H (Fin 2) _ _ EngineWitness.pE"
     " (WeightUpdate.orbit (fun _ => Capacity.Xo 0) (fun _ _ => -1)) (fun _ => Capacity.Xo 0)"
     " EngineWitness.engineGate_pE (fun n => rfl) trivial 0 0 0)", None),
    ("M31_weight_update_good_start_dropped", "WeightUpdate.lean", "trajectory_good_of_start",
     [("(hstart : Good p (B 0) ∨ 1 ≤ T)", "(hstart : True)", 1)], WU_VARS,
     "WeightUpdate.false_good_no_start (@H (Fin 2) _ _ EngineWitness.pE"
     " (WeightUpdate.orbit (fun _ => Capacity.Xo 0) (Capacity.Xo 1)) (fun _ => Capacity.Xo 0)"
     " EngineWitness.engineGate_pE (fun n => rfl) 0 trivial 0 le_rfl)", None),
    ("M32_weight_update_edge_off_from_gap_dropped", "WeightUpdate.lean", "edge_eventually_off_from",
     [("(hUc : U < p.γ * Bc)", "(hUc : True)", 1)], WU_VARS,
     "WeightUpdate.false_off_no_gap_from (@H (Fin 2) _ _ EngineWitness.pE WeightUpdate.Bon"
     " (fun _ => Capacity.Xo (1 / 25)) EngineWitness.engineGate_pE " + WU_FAC +
     "1 (Or.inr le_rfl) 0 1 (by decide) (1 / 25) (3 / 25) (fun n => by simp [Capacity.Xo]) (by norm_num) trivial)", None),
    ("M33_weight_update_edge_on_from_gap_dropped", "WeightUpdate.lean", "edge_eventually_on_from",
     [("(hgap : Bc < edgeFloor p Si Sj * (p.dt * L) / (1 - edgeFloor p Si Sj * (1 - p.γ * p.dt)))",
       "(hgap : True)", 1)], WU_VARS,
     "WeightUpdate.false_on_no_gap_from (@H (Fin 2) _ _ EngineWitness.pE WeightUpdate.Boff"
     " (fun _ => Capacity.Xo (1 / 1000)) EngineWitness.engineGate_pE " + WU_FAC +
     "1 (Or.inr le_rfl) 0 1 (by decide) (1 / 1000) (1 / 1000) (1 / 1000) (3 / 25)"
     " (fun n => (WeightUpdate.pdriveRow_Xo (by norm_num) 0).le)"
     " (fun n => (WeightUpdate.pdriveRow_Xo (by norm_num) 1).le) (fun n => by simp [Capacity.Xo])"
     " (by norm_num) trivial)", None),
    ("M34_weight_update_edge_off_gap_dropped", "WeightUpdate.lean", "edge_eventually_off",
     [("(hUc : U < p.γ * Bc)", "(hUc : True)", 1)], WU_VARS,
     "WeightUpdate.false_off_no_gap (@H (Fin 2) _ _ EngineWitness.pE WeightUpdate.Bon"
     " (fun _ => Capacity.Xo (1 / 25)) EngineWitness.engineGate_pE " + WU_FAC +
     "0 1 (by decide) (1 / 25) (3 / 25) (fun n => by simp [Capacity.Xo]) (by norm_num) trivial)", None),
    ("M35_weight_update_edge_on_gap_dropped", "WeightUpdate.lean", "edge_eventually_on",
     [("(hgap : Bc < edgeFloor p Si Sj * (p.dt * L) / (1 - edgeFloor p Si Sj * (1 - p.γ * p.dt)))",
       "(hgap : True)", 1)], WU_VARS,
     "WeightUpdate.false_on_no_gap (@H (Fin 2) _ _ EngineWitness.pE WeightUpdate.Boff"
     " (fun _ => Capacity.Xo (1 / 1000)) EngineWitness.engineGate_pE " + WU_FAC +
     "0 1 (by decide) (1 / 1000) (1 / 1000) (1 / 1000) (3 / 25)"
     " (fun n => (WeightUpdate.pdriveRow_Xo (by norm_num) 0).le)"
     " (fun n => (WeightUpdate.pdriveRow_Xo (by norm_num) 1).le) (fun n => by simp [Capacity.Xo])"
     " (by norm_num) trivial)", None),
    ("M36_weight_update_threshold_strictness", "WeightUpdate.lean", "onGap_iff",
     [("3 / 25 < onGap S ↔ S < Sstar", "3 / 25 < onGap S ↔ S ≤ Sstar", 1)], "",
     "WeightUpdate.false_gap_at_threshold ((H WeightUpdate.Sstar (by norm_num [WeightUpdate.Sstar])).2 le_rfl)",
     None),
    # ---- #27 (Capacity.lean, auditor follow-ups); numbered after the P5 definition mutants M37-M56 ----
    ("M57_capacity_preM_between_gamma_dt_bound_dropped", "Capacity.lean", "preM_between",
     [("(h1 : p.γ * p.dt ≤ 1)", "(h1 : True)", 1)], CAP_VARS,
     "Capacity.false_preM_between_no_bound (fun p D Bm i j hγ h0 => (@H Unit _ _ p hγ h0 trivial D Bm i j).1)",
     None),
    ("M58_capacity_convex_weights_upper_bound_dropped", "Capacity.lean", "convex_weights_iff",
     [("(0 ≤ p.γ * p.dt ∧ p.γ * p.dt ≤ 1)", "(0 ≤ p.γ * p.dt)", 1)], CAP_VARS,
     "(by have h := ((@H Unit _ _ ⟨2, 1, 1, 0, 0, 0, 0⟩).2 (by norm_num)).1; norm_num at h)", None),
    # ---- c016 (CoherenceMotion.lean, port of cycle 016): one statement mutant ----
    ("M59_coherence_motion_half_bound", "CoherenceMotion.lean", "trace_step_abs_le",
     [("≤ 2*(1-alpha)", "≤ (1-alpha)/2", 1)], "{V : Type}",
     "CoherenceMotion.false_trace_step_abs_le_half H", None),
]

# ---- P5: definition mutants (numbered after P4b's M24-M36, which live on research/lean-gate-p4b) ----
# name, file, [(old, new, count)] applied to the whole file text, VALUE PROBES declared in advance (>= 1 must fail).
# Rule (see the module docstring): build fails, no name-reference/parse error line, and a declared VALUE PROBE fails.
CI_OLD = "    (tau : ℝ) (n : ℕ) (i j : V) : ℂ :=\n  inputPhasor d x0 u omega tau n i j\n"


def ci(new):
    return [(CI_OLD, "    (tau : ℝ) (n : ℕ) (i j : V) : ℂ :=\n  " + new + "\n", 1)]


# closed-form value equalities (statements of the form `f (concrete data) = concrete value`), proved from the
# definitions; rewrite lemmas (input_engine_convention, delayed_input_step, innovation_*, ...) are NOT in these lists
VP_INC = ["probe_delayed_increment_values", "probe_input_delay_values", "probe_input_asym_omega_value"]
VP_COH = ["probe_coherence_values", "probe_asym_coherence_values", "probe_alpha_quarter", "probe_input_offset_value",
          "probe_reported_second", "probe_drive_second", "probe_asym_drive", "probe_main_preM",
          "probe_asym_reported", "probe_asym_reported_swapped", "probe_asym_reported_diag",
          "probe_coherence_input_asym_omega"]
VALUE_PROBES = {"PhaseIncrement.lean": VP_INC, "PhaseCoherence.lean": VP_COH}
PIN_INPUT = ["probe_coherence_values", "probe_asym_coherence_values"]
PIN_DRIVE = ["probe_drive_second", "probe_asym_drive"]
DRIVE_OLD = "  (eta + mu) * reported C i j - mu\n"
REP_OLD = "  if i = j then 0 else (‖C i j‖ + ‖C j i‖) / 2\n"
EMA_OLD = "  (alpha : ℂ) * C i j + ((1 - alpha : ℝ) : ℂ) * coherenceInput d x0 u omega tau n i j\n"
DELAY_OLD = "  if d ≤ n then u (n - d) j else 0"
OFFSET_OLD = "    ((omega i + omega j) / 2) * tau)\n\nnoncomputable def delayedIncrement"


def offset(new):
    """edit of the static offset `(ω_i + ω_j)/2 · τ` at the end of `inputPhasor` (PhaseIncrement.lean, line 58)"""
    return [(OFFSET_OLD, "    " + new + ")\n\nnoncomputable def delayedIncrement", 1)]


PIN_OMEGA = ["probe_input_asym_omega_value"]
SLOT_OLD = "AIEFGate.History.historyTrace d (phaseTrace x0 u) n ⟨0, Nat.zero_lt_succ d⟩ j -"
DEF_MUTANTS = [
    # 011 (PhaseIncrement.lean): value probes of `delayedIncrement` (M37, M38) and of the input read (M39)
    ("M37_phase_delayed_increment_starts_late", "PhaseIncrement.lean",
     [(DELAY_OLD, "  if d < n then u (n - d) j else 0", 1)], ["probe_delayed_increment_values"]),
    ("M38_phase_delayed_increment_off_by_one", "PhaseIncrement.lean",
     [(DELAY_OLD, "  if d ≤ n then u (n - d + 1) j else 0", 1)], ["probe_delayed_increment_values"]),
    ("M39_phase_input_reads_newest_slot", "PhaseIncrement.lean",
     [(SLOT_OLD, "AIEFGate.History.historyTrace d (phaseTrace x0 u) n ⟨d, Nat.lt_succ_self d⟩ j -", 1)],
     ["probe_input_delay_values"]),
    # cycle-004 survivors, now on the phase-specific coherence input (PhaseCoherence.lean)
    ("M40_coherence_input_wrong_delay_plus_one", "PhaseCoherence.lean",
     ci("inputPhasor (d + 1) x0 u omega tau n i j"), PIN_INPUT),
    ("M41_coherence_input_wrong_delay_minus_one", "PhaseCoherence.lean",
     ci("inputPhasor (d - 1) x0 u omega tau n i j"), PIN_INPUT),
    ("M42_coherence_input_current_theta_not_delayed", "PhaseCoherence.lean",
     ci("phasor (phaseTrace x0 u n i - phaseTrace x0 u n j - ((omega i + omega j) / 2) * tau)"), PIN_INPUT),
    ("M43_coherence_input_dropped_omega_tau", "PhaseCoherence.lean",
     ci("inputPhasor d x0 u (fun _ => 0) tau n i j"), ["probe_input_offset_value", "probe_coherence_values"]),
    ("M44_coherence_input_phase_is_zero", "PhaseCoherence.lean", ci("1"), PIN_INPUT),
    ("M45_drive_missing_eta", "PhaseCoherence.lean",
     [(DRIVE_OLD, "  mu * reported C i j - mu\n", 1)], PIN_DRIVE),
    # the auditor's cycle-013 mutants (five killed in the audit, two survivors of the original file)
    ("M46_coherence_input_swap_i_j", "PhaseCoherence.lean",
     ci("inputPhasor d x0 u omega tau n j i"), PIN_INPUT),
    ("M47_coherence_input_conjugated", "PhaseCoherence.lean",
     ci("(starRingEnd ℂ) (inputPhasor d x0 u omega tau n i j)"), PIN_INPUT),
    ("M48_coherence_ema_alpha_swapped", "PhaseCoherence.lean",
     [(EMA_OLD, "  ((1 - alpha : ℝ) : ℂ) * C i j + (alpha : ℂ) * coherenceInput d x0 u omega tau n i j\n", 1)],
     ["probe_alpha_quarter"]),
    ("M49_drive_mu_sign", "PhaseCoherence.lean",
     [(DRIVE_OLD, "  (eta + mu) * reported C i j + mu\n", 1)], PIN_DRIVE),
    ("M50_trace_step_uses_next_input", "PhaseCoherence.lean",
     [("  | n + 1 => coherenceStep alpha (coherenceTrace alpha C0 d x0 u omega tau n) d x0 u omega tau n\n",
       "  | n + 1 =>\n    coherenceStep alpha (coherenceTrace alpha C0 d x0 u omega tau n) d x0 u omega tau (n + 1)\n", 1)],
     PIN_INPUT),
    ("M51_reported_one_sided_not_symmetrised", "PhaseCoherence.lean",
     [(REP_OLD, "  if i = j then 0 else ‖C i j‖\n", 1)], ["probe_asym_reported"]),
    ("M52_reported_diagonal_one", "PhaseCoherence.lean",
     [(REP_OLD, "  if i = j then 1 else (‖C i j‖ + ‖C j i‖) / 2\n", 1)], ["probe_asym_reported_diag"]),
    # (N2) the static offset `(ω_i + ω_j)/2 · τ` of `inputPhasor` (PhaseIncrement.lean line 58): the node-uniform
    # probes (`ω = 1` or `ω = 0`) cannot see a wrong index; the asymmetric probe (`ω = (1, 0)`) pins it.
    ("M53_phase_input_offset_omega_i_only", "PhaseIncrement.lean", offset("omega i * tau"), PIN_OMEGA),
    ("M54_phase_input_offset_omega_j_only", "PhaseIncrement.lean", offset("omega j * tau"), PIN_OMEGA),
    ("M55_phase_input_offset_dropped", "PhaseIncrement.lean", offset("0"), PIN_OMEGA),
    ("M56_coherence_input_node_uniform_omega_i", "PhaseCoherence.lean",
     ci("inputPhasor d x0 u (fun _ => omega i) tau n i j"), ["probe_coherence_input_asym_omega"]),
]

# Equivalence negative controls: semantically EQUAL definitions. Each must NOT be killed (no declared value probe of
# the file fails); a control scored killed FAILS the run (the rule would then measure proof brittleness).
EQUIV_CONTROLS = [
    ("E1_coherence_input_times_one", "PhaseCoherence.lean", ci("inputPhasor d x0 u omega tau n i j * 1")),
    ("E2_coherence_input_plus_zero", "PhaseCoherence.lean", ci("(inputPhasor d x0 u omega tau n i j + 0)")),
    ("E3_coherence_input_id", "PhaseCoherence.lean", ci("id (inputPhasor d x0 u omega tau n i j)")),
    ("E4_delayed_read_not_lt", "PhaseIncrement.lean", [(DELAY_OLD, "  if ¬ n < d then u (n - d) j else 0", 1)]),
    ("E5_delayed_read_plus_zero", "PhaseIncrement.lean", [(DELAY_OLD, "  if d ≤ n then u (n - d + 0) j else 0", 1)]),
    ("E6_oldest_slot_other_proof_term", "PhaseIncrement.lean",
     [(SLOT_OLD, "AIEFGate.History.historyTrace d (phaseTrace x0 u) n ⟨0, Nat.succ_pos d⟩ j -", 1)]),
    ("E7_ema_sum_commuted", "PhaseCoherence.lean",
     [(EMA_OLD, "  ((1 - alpha : ℝ) : ℂ) * coherenceInput d x0 u omega tau n i j + (alpha : ℂ) * C i j\n", 1)]),
    ("E8_reported_sum_commuted", "PhaseCoherence.lean",
     [(REP_OLD, "  if i = j then 0 else (‖C j i‖ + ‖C i j‖) / 2\n", 1)]),
    ("E9_drive_coefficient_commuted", "PhaseCoherence.lean",
     [(DRIVE_OLD, "  (mu + eta) * reported C i j - mu\n", 1)]),
    ("E10_offset_sum_commuted", "PhaseIncrement.lean", offset("((omega j + omega i) / 2) * tau")),
]

# Typo / invalid-mutant controls: must be classified INVALID (a name-reference or parse error line) and not killed.
TYPO_CONTROLS = [
    ("T1_misspelled_identifier_inputPhasorXX", "PhaseCoherence.lean", ci("inputPhasorXX d x0 u omega tau n i j")),
    ("T2_syntax_garbage_unbalanced_paren", "PhaseCoherence.lean", ci("inputPhasor d x0 u omega tau n i j )")),
    ("T3_misspelled_identifier_delayedIncrementXX", "PhaseIncrement.lean",
     [(DELAY_OLD, "  if d ≤ n then u (n - d) j else delayedIncrementXX", 1)]),
]

# Statement-level controls on M4's statement (GateMap.stepB_add_smul_of_branch): an equivalent rewrite and a typo must
# both be NOT rejected (step (b): neither can be refuted by the proved negation `false_main_no_gamma`).
M4_OLD = "t * (1 - p.γ * p.dt) * branchScale p G drive B ctrl e * h e"
STATEMENT_CONTROLS = [
    ("SE1_statement_equivalent_commuted_gamma_dt", "GateMap.lean", "stepB_add_smul_of_branch",
     [(M4_OLD, "t * (1 - p.dt * p.γ) * branchScale p G drive B ctrl e * h e", 1)], GATE_VARS,
     f"RedTeam.false_main_no_gamma ({GATE_INST})"),
    ("ST1_statement_typo_branchScaleXX", "GateMap.lean", "stepB_add_smul_of_branch",
     [(M4_OLD, "t * (1 - p.γ * p.dt) * branchScaleXX p G drive B ctrl e * h e", 1)], GATE_VARS,
     f"RedTeam.false_main_no_gamma ({GATE_INST})"),
]

# Expected survivors: reported and run, never counted. EMPTY since the (N2) asymmetric-ω value probe: the static
# offset (ω_i + ω_j)/2 · τ cancels in the step ratio of `delayed_input_step`, so before N2 dropping it in
# PhaseIncrement.lean alone survived (that file had no value probe involving ω or τ; S1, killed only one level up by
# M43). `probe_input_asym_omega_value` (PhaseIncrement.lean) now kills it (M55, a counted definition mutant). The
# mechanism is kept: a mutant listed here is run, reported, and fails the run if it is detected (stale entry).
KNOWN_SURVIVORS = []

# Classifier negative control (P3 rule change, see (a) above): the P2 deletion form of M1 fails to build with
# name-reference errors only; it must be classified as such and must NOT count as a build rejection.
LEGACY_NAME_ONLY = ("M1_legacy_delete_kernel_hypothesis", "GateMap.lean", "stepB_add_smul_of_branch",
                    [("    (hker : InCtrlKer G ctrl h)\n", "", 1)])

OPENS = ("open Finset\nopen AIEFGate.MatrixForm (CE KG toEdge stepM symM rowM)\n"
         "open AIEFGate.CoherenceMotion (rTrace)\n"
         "open AIEFGate.EngineWitness (pE driveE BE sE driveW BW)\nopen AIEFGate.RedTeam (hw ctrlX)\n"
         "open AIEFGate.Bridge (toR CtrlJ01)\nopen AIEFGate.ControllerFiber (vCtrl)\n"
         "open AIEFGate.Capacity (rowS kernelM gateM appliedFactor)\nopen AIEFGate.MatrixForm (preM)\n"
         "open AIEFGate.WeightUpdate (pdriveRow edgeFloor Good onGap Sstar)\n")
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}


def theorem_span(src, name):
    """(start, end) of the statement of `theorem name` (from `theorem` to the `:=` that ends the statement)."""
    m = re.search(rf"^theorem {re.escape(name)}\b", src, re.M)
    if not m:
        raise RuntimeError(f"theorem {name} not found")
    i, depth = m.end(), 0
    while i < len(src):
        c = src[i]
        if c in "([{⟨":
            depth += 1
        elif c in ")]}⟩":
            depth -= 1
        elif depth == 0 and src.startswith(":=", i):
            return m.start(), i
        i += 1
    raise RuntimeError(f"no := for {name}")


def mutate(src, name, edits):
    s, e = theorem_span(src, name)
    stmt = src[s:e]
    for old, new, count in edits:
        if stmt.count(old) != count:
            raise RuntimeError(f"{name}: expected {count} occurrence(s) of {old!r}, found {stmt.count(old)}")
        stmt = stmt.replace(old, new)
    return src[:s] + stmt + src[e:]


def statement_prop(src, name, closure):
    """The statement of `theorem name` in `src` as a closed proposition `∀ closure binders, conclusion`."""
    s, e = theorem_span(src, name)
    sig = src[s:e]
    sig = sig[len(re.match(rf"theorem {re.escape(name)}", sig).group(0)):]
    depth = 0
    for i, c in enumerate(sig):
        if c in "([{⟨":
            depth += 1
        elif c in ")]}⟩":
            depth -= 1
        elif c == ":" and depth == 0 and not sig.startswith(":=", i):
            binders, concl = sig[:i].strip(), sig[i + 1:].strip()
            break
    else:
        raise RuntimeError(f"cannot split statement of {name}")
    allb = " ".join(x for x in (closure, " ".join(binders.split())) if x)
    concl = " ".join(concl.split())
    return f"(∀ {allb}, {concl})" if allb else f"({concl})"


def lean(text):
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "Mutant.lean"
        f.write_text(text)
        env = dict(os.environ, PATH=str(Path.home() / ".elan" / "bin") + os.pathsep + os.environ.get("PATH", ""))
        r = subprocess.run(["lake", "env", "lean", str(f)], cwd=PROJ, capture_output=True, text=True, env=env)
        out = r.stdout + r.stderr
        errs = [l for l in out.splitlines() if ": error" in l]
        return r.returncode, errs, out


def refutation_file(prop, term, preamble=""):
    return ("import AIEFGateCore\n\nset_option autoImplicit false\n\nnamespace AIEFGate\n" + OPENS + preamble +
            f"\ntheorem aief_refutation : ¬ {prop} := fun H => {term}\n\n#print axioms aief_refutation\n"
            "\nend AIEFGate\n")


def refutation_valid(rc, errs, out):
    """(ok, reason): a refutation counts only if it elaborates with no error, no sorry, and standard axioms only."""
    if rc != 0 or errs:
        return False, "does not elaborate"
    if "declaration uses" in out or "sorry" in out:
        return False, "uses sorry"
    m = re.search(r"'AIEFGate\.aief_refutation' depends on axioms: \[([^\]]*)\]", out, re.S)
    if m:
        axs = {a.strip() for a in m.group(1).replace("\n", " ").split(",") if a.strip()}
    elif "'AIEFGate.aief_refutation' does not depend on any axioms" in out:
        axs = set()
    else:
        return False, "no #print axioms output"
    if not axs <= ALLOWED_AXIOMS:
        return False, f"non-standard axioms {sorted(axs - ALLOWED_AXIOMS)}"
    return True, f"axioms {sorted(axs)}"


def classify(errs, out):
    if not errs:
        return "none"
    name_only = all(("nknown identifier" in l) or ("unknown constant" in l) for l in errs)
    return "NAME-REFERENCE ONLY (weak)" if name_only else "REAL PROOF FAILURE"


def build_rejected(rc, errs, kind):
    """P3 rule: a build rejection counts only if the kept proof fails for a real reason (not name-only)."""
    return rc != 0 and bool(errs) and kind == "REAL PROOF FAILURE"


def mutate_file(src, edits):
    """Definition mutants: exact-count textual edits on the whole file."""
    out = src
    for old, new, count in edits:
        if out.count(old) != count:
            raise RuntimeError(f"expected {count} occurrence(s) of {old!r}, found {out.count(old)}")
        out = out.replace(old, new)
    return out


DECL_RE = re.compile(r"^\s*(?:private\s+|protected\s+)*(?:noncomputable\s+)?(?:theorem|lemma|def|abbrev|instance)\s+(\S+)")


def failing_decls(msrc, errs):
    """Names of the declarations that contain an error line (`Mutant.lean:LINE:COL: error: ...`)."""
    lines = msrc.splitlines()
    names = []
    for e in errs:
        m = re.search(r"Mutant\.lean:(\d+):", e)
        if not m:
            continue
        for k in range(int(m.group(1)) - 1, -1, -1):
            d = DECL_RE.match(lines[k])
            if d:
                if d.group(1) not in names:
                    names.append(d.group(1))
                break
    return names


NAME_REF_RE = re.compile(r"nknown (identifier|constant|namespace)")
PARSE_ERR_RE = re.compile(r"\berror(\([^)]*\))?: (unexpected |expected )")


def invalid_lines(errs):
    """Error lines that are name-reference or parse errors (such a mutant says nothing about semantics)."""
    return [l for l in errs if NAME_REF_RE.search(l) or PARSE_ERR_RE.search(l)]


def def_mutant_status(rc, errs, failing, pins):
    """Definition-mutant rule (P5, revised): 'BUILDS' (no error), 'INVALID' (any name-reference or parse error line),
    'KILLED' (builds fail, no invalid line, and a declared VALUE PROBE fails) or 'SURVIVED' (fails only in other
    declarations, e.g. brittle rewrite lemmas, which gives no credit)."""
    if rc == 0 and not errs:
        return "BUILDS"
    if rc == 0 or not errs:
        return "INVALID"
    if invalid_lines(errs):
        return "INVALID"
    return "KILLED" if any(p in failing for p in pins) else "SURVIVED"


def def_mutant_killed(rc, errs, failing, pins):
    return def_mutant_status(rc, errs, failing, pins) == "KILLED"


def refute(msrc, src, thm, closure, term):
    """(refuted, why, control_ok): step (b) on the mutated statement and step (c) on the unmutated one."""
    rrc, rerrs, rout = lean(refutation_file(statement_prop(msrc, thm, closure), term))
    refuted, why = refutation_valid(rrc, rerrs, rout)
    crc, cerrs, _ = lean(refutation_file(statement_prop(src, thm, closure), term))
    return refuted, why, crc != 0 and bool(cerrs), (rerrs or rout.splitlines())


def main():
    ok = True
    srcs = {}
    for f in sorted({m[1] for m in MUTANTS} | {m[1] for m in DEF_MUTANTS} | {m[1] for m in KNOWN_SURVIVORS} | {m[1] for m in EQUIV_CONTROLS} | {m[1] for m in TYPO_CONTROLS}):
        srcs[f] = (SRCDIR / f).read_text()
        rc, errs, _ = lean(srcs[f])
        good = rc == 0 and not errs
        print(f"CONTROL unmutated {f}: rc={rc} errors={len(errs)} -> {'PASS' if good else 'FAIL'}")
        ok &= good
    # negative controls of the step-(b) validator: a sorry refutation and an axiom refutation must be rejected
    _, f1, t1, e1, c1, _, _ = MUTANTS[0]
    prop1 = statement_prop(mutate(srcs[f1], t1, e1), t1, c1)
    for label, term, pre in (("sorry", "sorry", ""),
                             ("axiom", "aief_cheat.elim", "\naxiom aief_cheat : False\n")):
        valid, why = refutation_valid(*lean(refutation_file(prop1, term, pre)))
        print(f"VALIDATOR NEGATIVE CONTROL ({label}-based refutation of M1): "
              f"{'ACCEPTED (BAD)' if valid else 'REJECTED (good)'} [{why}]")
        ok &= not valid
    # classifier negative control: a name-only build failure must not count as a build rejection
    lname, lf, lthm, ledits = LEGACY_NAME_ONLY
    lrc, lerrs, lout = lean(mutate(srcs[lf], lthm, ledits))
    lkind = classify(lerrs, lout)
    lgood = lrc != 0 and lkind.startswith("NAME-REFERENCE ONLY") and not build_rejected(lrc, lerrs, lkind)
    print(f"CLASSIFIER NEGATIVE CONTROL ({lname}): build fails [{lkind}]; counted as build rejection: "
          f"{'YES (BAD)' if build_rejected(lrc, lerrs, lkind) else 'NO'} -> {'PASS' if lgood else 'FAIL'}")
    ok &= lgood
    n_rej = 0
    n_flag = 0
    only = os.environ.get("AIEF_MUT_ONLY")   # debugging aid: regex on mutant names; the full run is the record
    for name, f, thm, edits, closure, term, eterm in MUTANTS:
        if only and not re.search(only, name):
            continue
        src = srcs[f]
        msrc = mutate(src, thm, edits)
        assert msrc != src
        rc, errs, out = lean(msrc)
        kind = classify(errs, out)
        build_rej = build_rejected(rc, errs, kind)
        refuted, why, control_ok, rmsg = refute(msrc, src, thm, closure, term)
        rejected = build_rej and refuted and control_ok
        line = (f"{name}: build {'REJECTED' if build_rej else 'NOT REJECTED (BAD)'} [{kind}]; "
                f"refuted by proof: {'YES' if refuted else 'NO (BAD)'} [{why}]; "
                f"same term on unmutated statement fails (term-specificity only): {'YES' if control_ok else 'NO (BAD)'}")
        emsg = []
        if eterm is not None:
            erefuted, ewhy, econtrol, emsg = refute(msrc, src, thm, closure, eterm)
            rejected = rejected and erefuted and econtrol
            line += (f"; engine-shaped (pE, ε>0) refutation: {'YES' if erefuted else 'NO (BAD)'} [{ewhy}], "
                     f"term-specific: {'YES' if econtrol else 'NO (BAD)'}")
            if erefuted:
                emsg = []
        n_rej += rejected
        if invalid_lines(errs):
            line += "; NOTE: build output also has a name-reference/parse error line (info only)"
            n_flag += 1
        print(f"{line} -> {'REJECTED (good)' if rejected else 'NOT REJECTED (BAD)'}")
        for l in errs[:1]:
            print("    build: " + l.split("Mutant.lean:")[-1][:150])
        if not refuted:
            for l in rmsg[:3]:
                print("    refutation: " + l.split("Mutant.lean:")[-1][:200])
        for l in emsg[:3]:
            print("    engine refutation: " + l.split("Mutant.lean:")[-1][:200])
        ok &= rejected
    print(f"statement mutants rejected: {n_rej}/{len(MUTANTS)}; flagged with a name-reference/parse error line: {n_flag}")
    # statement-level controls: an equivalent statement and a typo must NOT be rejected
    for name, f, thm, edits, closure, term in STATEMENT_CONTROLS:
        src = srcs[f]
        msrc = mutate(src, thm, edits)
        rc, errs, out = lean(msrc)
        build_rej = build_rejected(rc, errs, classify(errs, out))
        refuted, why, control_ok, _ = refute(msrc, src, thm, closure, term)
        rejected = build_rej and refuted and control_ok
        good = not rejected and not refuted
        print(f"STATEMENT CONTROL {name}: build rejected: {build_rej}; refuted by proof: {refuted} -> "
              f"{'NOT REJECTED (good)' if good else 'REJECTED (BAD)'}")
        ok &= good
    # P5: definition mutants (rule: build fails, no name-reference/parse error line, a declared value probe fails)
    n_def = 0
    for name, f, edits, pins in DEF_MUTANTS:
        if only and not re.search(only, name):
            continue
        src = srcs[f]
        msrc = mutate_file(src, edits)
        assert msrc != src
        rc, errs, out = lean(msrc)
        failing = failing_decls(msrc, errs)
        status = def_mutant_status(rc, errs, failing, pins)
        killed = status == "KILLED"
        n_def += killed
        hit = [p for p in pins if p in failing]
        print(f"{name}: {status}; failing declarations: {', '.join(failing) or '-'}; "
              f"value probes failing: {', '.join(hit) or 'NONE'} -> "
              f"{'KILLED (good)' if killed else status + ' (BAD)'}")
        for l in invalid_lines(errs)[:1]:
            print("    invalid-mutant line: " + l.split("Mutant.lean:")[-1][:150])
        ok &= killed
    print(f"definition mutants killed: {n_def}/{len(DEF_MUTANTS)}")
    print(f"mutants rejected in total: {n_rej + n_def}/{len(MUTANTS) + len(DEF_MUTANTS)}")
    # equivalence controls: must NOT be killed
    n_eq = 0
    for name, f, edits in EQUIV_CONTROLS:
        msrc = mutate_file(srcs[f], edits)
        rc, errs, out = lean(msrc)
        failing = failing_decls(msrc, errs)
        status = def_mutant_status(rc, errs, failing, VALUE_PROBES[f])
        good = status != "KILLED"
        n_eq += good
        print(f"EQUIVALENCE CONTROL {name}: {status}; build {'passes' if rc == 0 and not errs else 'fails'}; "
              f"failing declarations: {', '.join(failing) or '-'} -> "
              f"{'NOT KILLED (good)' if good else 'KILLED (BAD: the rule scores an equivalent rewrite as a kill)'}")
        ok &= good
    print(f"equivalence controls not killed: {n_eq}/{len(EQUIV_CONTROLS)}")
    # typo / invalid-mutant controls: must be classified INVALID
    n_ty = 0
    for name, f, edits in TYPO_CONTROLS:
        msrc = mutate_file(srcs[f], edits)
        rc, errs, out = lean(msrc)
        failing = failing_decls(msrc, errs)
        status = def_mutant_status(rc, errs, failing, VALUE_PROBES[f])
        good = status == "INVALID"
        n_ty += good
        print(f"TYPO CONTROL {name}: {status} -> {'FLAGGED INVALID, not killed (good)' if good else 'NOT FLAGGED (BAD)'}")
        ok &= good
    print(f"typo controls flagged invalid: {n_ty}/{len(TYPO_CONTROLS)}")
    # expected survivors: reported honestly, not counted
    for name, f, edits in KNOWN_SURVIVORS:
        rc, errs, out = lean(mutate_file(srcs[f], edits))
        clean = rc == 0 and not errs
        print(f"{name}: build {'PASSES' if clean else 'FAILS'} -> "
              f"{'SURVIVES, as documented (not counted)' if clean else 'now detected (documented survivor is stale)'}")
        ok &= clean
    print("RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
