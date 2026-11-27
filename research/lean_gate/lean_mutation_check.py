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

  DelayRoots.lean (Arena_Researcher_06020041 cycles 9/10 root lemmas; numbered M95 ff., after the phaselock port):
  M95 symRoot_eq_one_or_lt, ha1 (a < 1) := True                  -> a = 2, d = 1: root -2 (false_symRoot_no_upper)
  M96 symRoot_eq_one_or_lt, conclusion drops `z = 1 ∨`           -> the neutral root 1 (false_one_inside)
  M97 transRoot_lt_one, hm (1 ≤ m) := True                       -> m = 0, h = 3, d = 0: root -2
  M98 transRoot_lt_one, hmh (m h < 1) := True                    -> m = h = 1, d = 0: root -1
  M99 projectedSlope_lt_quarter, `C < x` -> `C ≤ x`              -> C = ε = x = 1: slope exactly 1/4
  M100 symRoot_eq_one_or_lt, ha0 (0 < a) := True                   -> a = -2, d = 1: root 2 (P = (l-1)(l-2))
  M101 transRoot_lt_one, h0 (0 < h) := True                        -> m = 1, h = 0, d = 0: root 1
  M102 symRoot_eq_one_or_lt, `a < 1` -> `a ≤ 1`                    -> a = 1, d = 1: root -1
  M103 transRoot_lt_one, `m h < 1` -> `m h ≤ 1`                   -> m = h = 1, d = 1: root i
  M104 projectedSlope_lt_quarter, `0 < C` and `0 < ε` := True     -> C = ε = -1, x = -1/2: slope 4/9
  (0 < ε alone is redundant given 0 < C: projectedSlope_lt_quarter_of_C; M100-M104 from Researcher 001's audit of ae2c25a)
  M105 projectedSlope_lt_quarter_of_C, hC (0 < C) := True       -> C = ε = -1, x = -1/2: slope 4/9
  M106 projectedSlope_lt_quarter_of_C, `C < x` -> `C ≤ x`       -> C = ε = x = 1: slope exactly 1/4
  (M105-M106 from Researcher 001's audit of cce534d)

  Arena intake (CommonRootSimple.lean cycle 13, EngineStepRef.lean cycle 21; SPEC §16; numbered after M107-M109):
  M110-M113 CommonRootSimple statements (0 < h, h < 1 dropped; P'(1) without the delay factor), M114-M118
  EngineStepRef statements (orbit backward / no frequency equation, 0 < b dropped, history unshifted, neighbour
  read from the current slot), each refuted by a `false_*` theorem. Definition mutants M119-M129 (commonPoly,
  clippedWeight, phaseHead, phaseStep, orbitPath) killed by `probe_*` value probes; E18-E20 must not be killed
  (they break proofs but no probe, so they survive only through the probe rule: disclosed brittleness).
  M130 (#44 N1): phaseHead uses the raw b instead of clippedWeight b -> probe_phaseHead_negative_weight (b = -1).

  Arena bundle intake (MERGE_MANIFEST 2026-11-25, 12 modules, SPEC §17; numbered after M130): statement mutants
  M131-M156 (a load-bearing hypothesis weakened to True, a budget term or delay power dropped, a bound factor
  tightened), each refuted by a `false_*` theorem appended to its file; definition mutants M157-M190 (queue shift,
  view reversal, oldest/newest slot, wrap-free heads, refInput, arcBound, budget, two-slot steps, stepSize, energy,
  mode, WindowMax.next, HeteroStepRef.linearStep/row/phaseHeadW) killed by `probe_*` value probes; E21-E23 must not
  be killed. The bundle reuses short names (State, Consistent, step, iterate, window_step, ...) in distinct
  namespaces, so each refutation opens only the mutated file's own namespace (FILE_OPENS). One exception:
  EMAFiniteSum opens two, CausalEMATracking (for `budget`) and EMAFiniteSum, which share no names (audit note N2).

  H9(b) + H16 (GronwallEnvelope.lean, GateContraction.lean; SPEC §18; author Auditor Seat 002). Numbered in a
  separate block from M300 on (another branch may add mutants right after M190); no rule change, no FILE_OPENS
  entry (the statements name their own namespaces, e.g. `MatrixForm.GateOnM`, `GateContraction.scalarMap`):
  statement mutants M300-M312 (a load-bearing hypothesis weakened to True: `0 ≤ ρ`, `0 ≤ B 0`, `lam ≤ 1`, `0 ≤ κ`,
  `γ dt ≤ 1` (engine-legal `γ dt = 2` witness at `WeightUpdate.pH`), the gate-off hypotheses, symmetry, `ρ ≠ 1`;
  and the wrong-variant control M306, gate applied before the drive), each refuted by a `false_*` theorem of its
  file; definition mutants M313-M316 (`scalarMap` gate order / clamp, `l1` without `|.|`, the witness state
  raised on one side only) killed by the `probe_*` value probes in `VP_H16`. All seventeen predeclared KILLED.
  Follow-up to the Researcher 001 audit of 952f87d (F3 and the coverage note), predeclared in the commit that adds
  them, before any run of them: statement mutants M317 (`stepM_edge_envelope_lower`, `γ dt ≤ 1` -> True; refuted by
  `false_lower_envelope_gamma_dt_gt_one` at `WeightUpdate.pH`) and M318 (`binding_witness_l1`, `6/5` -> `5/4`;
  refuted by `false_binding_l1_five_fourths`), predeclared KILLED; definition-style pins M319 (`6/5` -> `1` in
  `binding_witness_l1`; pin probe `probe_binding_ratio_six_fifths`) and M320 (`8/3` -> `3` in
  `stepM_edge_envelope_pE`; pin probe `probe_envelope_pE_orbit`), predeclared KILLED. These two "probes" are
  statement pins (they consume the theorem with its headline constant written out), not closed-number value
  equalities; KILLED there means "the pinned constant changed". M321 (`6/5` -> `123/100`, a TRUE strengthening,
  since the exact ratio is about 1.2391) is predeclared SURVIVE and listed in `KNOWN_SURVIVORS`: no Lean check can
  reject a statement that is still true and still proved; only the text pin in test_lean_gate_h9h16.py catches it.
  Disclosure: Researcher 001's audit scratch already ran the analogues of M317 (K5), M318 (K4), M319 (K1) and
  M321 (K2), so these predictions are informed by those results, not independent of them. `GateContraction.lean`
  gets a `FILE_OPENS` entry because M318's statement uses the file's short names (`l1`, `B3`, `B3'`).

  C014 (TrajectoryInvariants.lean, port of cycle 014 of Researcher 040282; numbered M71 ff.; the c016 port was
  renumbered after these, its definition mutants M71-M76 becoming M79-M84, plus M85-M86 added for audit N3 (the phase-lock port then takes M87-M94) and its controls E11-E14 becoming E12-E15):
  M71 TrajectorySafety.post_capacity, `(p n).cap` -> `(p (n + 1)).cap`   -> TrajectorySafety.capacity_clock_refuted
  M72 TrajectorySafety.all_times_structural, hInit := True            -> TrajectorySafety.initial_time_refuted
  M73 TrajectorySafety.post_capacity, hp (EngineGate) := True         -> TrajectorySafety.broken_link_refuted (`pB`)
  Definition mutants (rule below): M74 `weightUpdate := symM` (gate bypassed), M75 `feedbackStep` hands `U` the old
  B twice, M76 the new B twice, M77 the raw drive instead of the new B, M78 the time `n + 1`; probes
  `probe_gate_scales_row`, `probe_aux_reads_old_and_new`, `probe_aux_time_and_new_entry`; equivalence control
  E11 (the `let` inlined) must not be killed. M75 is the survivor of Researcher 001's audit of 9b9b3d9.

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

  P6 (CoherenceMotion.lean, port of cycle 016 of Researcher 040282; the statement mutants and M70 are numbered after
  M58, the other definition mutants after C014's M78; no rule change): STATEMENT
  mutants M59-M69 (same three conditions as M1-M58; refuted by the negations `factor_one_refuted`,
  `nonunit_initial_refuted`, `two_step_one_allowance_refuted`, `increase_only_abs_refuted`,
  `negative_alpha_upper_refuted`, `alpha_gt_one_upper_refuted`, `half_increase_upper_refuted`, `diagonal_one_refuted`
  of that file) and DEFINITION mutants M70 and M79-M86 (the observable `rTrace` and the engine alpha `alphaE`; value probes in
  `VP_MOT`, same kill rule), equivalence controls E12-E15 and the typo control T4. The probes of that file prove their
  values from the definitions unfolded in the probe itself (a private helper stated about `rTrace` would let a mutated
  `rTrace` fail only in the helper, which earns no credit).

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
CM_VARS = "{V : Type}"
CM_INST = ("@H (Fin 2) (1/2) (CoherenceMotion.valueC 1) 1 CoherenceMotion.valueX CoherenceMotion.valueU"
           " CoherenceMotion.valueOmega Real.pi")
CM_UNIT = "(fun i j => by simp [CoherenceMotion.valueC])"
CM_PRE = " CoherenceMotion.valueX CoherenceMotion.valueU CoherenceMotion.valueOmega Real.pi"
TS_VARS = "{V S : Type} [Fintype V] [LinearOrder V]"   # section variables of TrajectoryInvariants.lean
FL_VARS = "{V : Type}"                                 # section variables of FrequencyLock.lean
FL_PROBE = " PhaseCoherence.probeX PhaseCoherence.probeU PhaseCoherence.probeOmega Real.pi"
WU_FAC = ("(by norm_num [EngineWitness.pE]) (by norm_num [EngineWitness.pE]) (by norm_num [EngineWitness.pE])"
          " (fun n => rfl) (fun n i j => Capacity.Xo_symm _ i j) ")


def via(inst, binders, pos):
    """Term `fun <binders without pos> => inst <binders with `trivial` at pos>` (feeds `True` to H)."""
    bs = binders.split()
    lam = " ".join(b for i, b in enumerate(bs) if i != pos)
    app = " ".join("trivial" if i == pos else b for i, b in enumerate(bs))
    return f"(fun {lam} => {inst} {app})"


MAIN_BINDERS = "drive B h t ctrl hclip hon hker hc0 hc1"   # binder order of stepB_add_smul_of_branch
ENV_UP = "B lam d ρ hρ0 hB0 hlam1 hrec n"          # binder order of GronwallEnvelope.scalar_envelope_upper
ENV_LO = "B lam κ d ρ hρ0 hκ0 hκ hrec n"         # binder order of GronwallEnvelope.scalar_envelope_lower

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
    # ---- P6: CoherenceMotion.lean (port of cycle 016 of Researcher 040282), numbered after M58 ----
    ("M59_motion_abs_le_factor_two_dropped", "CoherenceMotion.lean", "trace_step_abs_le",
     [("2*(1-alpha)", "(1-alpha)", 1)], CM_VARS,
     f"CoherenceMotion.factor_one_refuted ({CM_INST} (by norm_num) (by norm_num) {CM_UNIT} 0 0 1)", None),
    ("M60_motion_abs_le_bound_halved_not_doubled", "CoherenceMotion.lean", "trace_step_abs_le",
     [("2*(1-alpha)", "(1-alpha)/2", 1)], CM_VARS,
     f"CoherenceMotion.factor_one_refuted (le_trans ({CM_INST} (by norm_num) (by norm_num) {CM_UNIT} 0 0 1)"
     " (by norm_num))", None),
    ("M61_motion_abs_le_unit_disk_dropped", "CoherenceMotion.lean", "trace_step_abs_le",
     [("(hC0 : ∀ i j, ‖C0 i j‖ ≤ 1)", "(hC0 : True)", 1)], CM_VARS,
     "CoherenceMotion.nonunit_initial_refuted (@H (Fin 2) (1/2) (CoherenceMotion.valueC 3) 1" + CM_PRE +
     " (by norm_num) (by norm_num) trivial 0 0 1)", None),
    ("M62_motion_abs_le_two_steps_one_allowance", "CoherenceMotion.lean", "trace_step_abs_le",
     [("(n+1) i j", "(n+2) i j", 1)], CM_VARS,
     "CoherenceMotion.two_step_one_allowance_refuted (@H (Fin 2) (3/4) (CoherenceMotion.valueC 1) 1" + CM_PRE +
     f" (by norm_num) (by norm_num) {CM_UNIT} 0 0 1)", None),
    ("M63_motion_abs_le_min_factor_two_dropped", "CoherenceMotion.lean", "trace_step_abs_le_min",
     [("min 1 (2*(1-alpha))", "min 1 (1-alpha)", 1)], CM_VARS,
     f"CoherenceMotion.factor_one_refuted (le_trans ({CM_INST} (by norm_num) (by norm_num) {CM_UNIT} 0 0 1)"
     " (min_le_right _ _))", None),
    ("M64_motion_abs_le_min_unit_disk_dropped", "CoherenceMotion.lean", "trace_step_abs_le_min",
     [("(hC0 : ∀ i j, ‖C0 i j‖ ≤ 1)", "(hC0 : True)", 1)], CM_VARS,
     "CoherenceMotion.nonunit_initial_refuted (le_trans (@H (Fin 2) (1/2) (CoherenceMotion.valueC 3) 1" + CM_PRE +
     " (by norm_num) (by norm_num) trivial 0 0 1) (min_le_right _ _))", None),
    ("M65_motion_state_bound_increase_only", "CoherenceMotion.lean", "trace_step_abs_state_bound",
     [("(1-alpha)*(1 + rTrace", "(1-alpha)*(1 - rTrace", 1)], CM_VARS,
     f"CoherenceMotion.increase_only_abs_refuted ({CM_INST} (by norm_num) (by norm_num) 0 0 1)", None),
    ("M66_motion_step_bounds_nonneg_alpha_dropped", "CoherenceMotion.lean", "trace_step_bounds",
     [("(ha0 : 0 ≤ alpha)", "(ha0 : True)", 1)], CM_VARS,
     "CoherenceMotion.negative_alpha_upper_refuted (@H (Fin 2) (-1) (CoherenceMotion.valueC 1) 1" + CM_PRE +
     " trivial (by norm_num) 0 0 1).2", None),
    ("M67_motion_step_bounds_alpha_le_one_dropped", "CoherenceMotion.lean", "trace_step_bounds",
     [("(ha1 : alpha ≤ 1)", "(ha1 : True)", 1)], CM_VARS,
     "CoherenceMotion.alpha_gt_one_upper_refuted (@H (Fin 2) 2 (CoherenceMotion.valueC 0) 1" + CM_PRE +
     " (by norm_num) trivial 0 0 1).2", None),
    ("M68_motion_step_bounds_upper_envelope_halved", "CoherenceMotion.lean", "trace_step_bounds",
     [("tau n i j + (1-alpha)", "tau n i j + (1-alpha)/2", 1)], CM_VARS,
     "CoherenceMotion.half_increase_upper_refuted (@H (Fin 2) (1/2) (CoherenceMotion.valueC 0) 1" + CM_PRE +
     " (by norm_num) (by norm_num) 0 0 1).2", None),
    ("M69_motion_diagonal_claimed_one", "CoherenceMotion.lean", "trace_diagonal",
     [("n i i = 0", "n i i = 1", 1)], CM_VARS,
     "CoherenceMotion.diagonal_one_refuted (@H (Fin 2) (1/2) (CoherenceMotion.valueC 1) 1" + CM_PRE + " 1 1)", None),
    # ---- C014 (TrajectoryInvariants.lean, port of cycle 014 of Researcher 040282); numbered from M71 ----
    ("M71_trajectory_post_capacity_next_cap", "TrajectoryInvariants.lean", "post_capacity",
     [("i ≤ (p n).cap", "i ≤ (p (n + 1)).cap", 1)], TS_VARS,
     "TrajectorySafety.capacity_clock_refuted (@H (Fin 2) Unit _ _ TrajectorySafety.capSchedule"
     " TrajectorySafety.oneDrive TrajectorySafety.keepAux ((), TrajectorySafety.zeroB) 0"
     " (by simpa [TrajectorySafety.capSchedule] using TrajectorySafety.pWide_engine) 0)", None),
    ("M72_trajectory_all_times_no_initial_structure", "TrajectoryInvariants.lean", "all_times_structural",
     [("(hInit : Structural initial.2)", "(hInit : True)", 1)], TS_VARS,
     "TrajectorySafety.initial_time_refuted (@H (Fin 2) Unit _ _ (fun _ => TrajectorySafety.pWide)"
     " TrajectorySafety.oneDrive TrajectorySafety.keepAux ((), TrajectorySafety.dirtyB)"
     " (fun _ => by norm_num [TrajectorySafety.pWide]) (fun _ => by norm_num [TrajectorySafety.pWide]) trivial 0)",
     None),
    ("M73_trajectory_post_capacity_no_engine_gate", "TrajectoryInvariants.lean", "post_capacity",
     [("(hp : EngineGate (p n))", "(hp : True)", 1)], TS_VARS,
     "TrajectorySafety.broken_link_refuted (@H (Fin 2) Unit _ _ (fun _ => Capacity.pB)"
     " (fun _ _ _ => TrajectorySafety.X 75) TrajectorySafety.keepAux ((), TrajectorySafety.zeroB) 0 trivial 0)",
     None),
    # ---- Phase lock (FrequencyLock.lean, Auditor Seat 002's rework of Arena cycles 3/5); numbered from M87 (after P6's M85, M86)
    # (P6 holds M79-M86; definition mutants added after #41 are M107-M109, numbered after DelayRoots' M95-M106) ----
    ("M87_lock_reported_factor_two_dropped", "FrequencyLock.lean", "reported_of_pairLock",
     [("1 - 2 * alpha ^ k ≤ reported", "1 - alpha ^ k ≤ reported", 1)], FL_VARS,
     "FrequencyLock.pairLock_factor_two_refuted (@H (Fin 2) (1/2) PhaseCoherence.probeC0 0" + FL_PROBE +
     " (Real.pi / 2) 0 0 1 (by decide) (fun _ _ => ⟨rfl, rfl⟩) (by norm_num) (by norm_num)"
     " (fun _ _ => by simp [PhaseCoherence.probeC0]) 1)", None),
    ("M88_lock_norm_factor_two_dropped", "FrequencyLock.lean", "coherenceTrace_norm_of_pairLock",
     [("1 - 2 * alpha ^ k ≤ ‖", "1 - alpha ^ k ≤ ‖", 1)], FL_VARS,
     "FrequencyLock.pairLock_norm_factor_two_refuted (@H (Fin 2) (1/2) PhaseCoherence.probeC0 0" + FL_PROBE +
     " (Real.pi / 2) 0 0 1 (fun _ _ => ⟨rfl, rfl⟩) (by norm_num) (by norm_num)"
     " (fun _ _ => by simp [PhaseCoherence.probeC0]) 1)", None),
    ("M89_lock_constant_from_N_not_N_plus_d", "FrequencyLock.lean", "coherenceInput_constant_of_pairLock",
     [("(hn : N + d ≤ n)", "(hn : N ≤ n)", 1)], FL_VARS,
     "FrequencyLock.delay_start_refuted (@H (Fin 2) 2" + FL_PROBE +
     " (Real.pi / 2) 0 0 1 (fun _ _ => ⟨rfl, rfl⟩) 0 (le_refl 0))", None),
    ("M90_lock_only_node_i_locked", "FrequencyLock.lean", "coherenceInput_constant_of_pairLock",
     [("(hlock : ∀ n, N ≤ n → u n i = c ∧ u n j = c)", "(hlock : ∀ n, N ≤ n → u n i = c)", 1)], FL_VARS,
     "FrequencyLock.half_lock_refuted (@H (Fin 2) 0 (fun _ => 0) FrequencyLock.splitU (fun _ => 0) 0 Real.pi 0 0 1"
     " (fun _ _ => by simp [FrequencyLock.splitU]) 1 (by norm_num))", None),
    ("M91_lock_period_condition_dropped", "FrequencyLock.lean", "coherenceInput_constant_of_periodicPairRate",
     [("(hper : ∀ n, N + d ≤ n → c n = c (n - d))", "(hper : True)", 1)], FL_VARS,
     "FrequencyLock.nonperiodic_rate_refuted (@H (Fin 2) 1 (fun _ => 0) FrequencyLock.altU (fun _ => 0) 0"
     " (fun m => if m % 2 = 0 then Real.pi else 0) 0 0 1 (fun _ _ => ⟨rfl, rfl⟩) trivial 2 (by norm_num))", None),
    # N6 (Researcher 001, e50102c): the start index of the periodic theorem itself (M89 covers only the corollary)
    ("M94_lock_periodic_constant_from_N_not_N_plus_d", "FrequencyLock.lean",
     "coherenceInput_constant_of_periodicPairRate",
     [("(hn : N + d ≤ n)", "(hn : N ≤ n)", 1)],
     FL_VARS,
     "FrequencyLock.delay_start_refuted (@H (Fin 2) 2" + FL_PROBE +
     " (fun _ => Real.pi / 2) 0 0 1 (fun _ _ => ⟨rfl, rfl⟩) (fun _ _ => rfl) 0 (le_refl 0))", None),
    # ---- DelayRoots.lean (Arena cycles 9/10 root lemmas); numbered M95 ff. after P6's M59-M70, M79-M86 and phaselock's M87-M94 ----
    ("M95_delayroots_sym_upper_bound_dropped", "DelayRoots.lean", "symRoot_eq_one_or_lt",
     [("(ha1 : a < 1)", "(ha1 : True)", 1)], "",
     "DelayRoots.false_symRoot_no_upper (H 2 (by norm_num) trivial 1 (-2) DelayRoots.symRoot_root_a_two)", None),
    ("M96_delayroots_sym_neutral_root_dropped", "DelayRoots.lean", "symRoot_eq_one_or_lt",
     [("    z = 1 ∨ ‖z‖ < 1", "    ‖z‖ < 1", 1)], "",
     "DelayRoots.false_one_inside (H (1 / 2) (by norm_num) (by norm_num) 0 1 (DelayRoots.symRoot_one (1 / 2) 0).1)",
     None),
    ("M97_delayroots_trans_m_ge_one_dropped", "DelayRoots.lean", "transRoot_lt_one",
     [("(hm : 1 ≤ m)", "(hm : True)", 1)], "",
     "DelayRoots.false_minus_two_inside (H 0 trivial 3 (by norm_num) (by norm_num) 0 (-2)"
     " DelayRoots.transRoot_root_m_zero)", None),
    ("M98_delayroots_trans_mh_lt_one_dropped", "DelayRoots.lean", "transRoot_lt_one",
     [("(hmh : (m : ℝ) * h < 1)", "(hmh : True)", 1)], "",
     "DelayRoots.false_minus_one_inside (H 1 le_rfl 1 (by norm_num) trivial 0 (-1) DelayRoots.transRoot_root_mh_one)",
     None),
    ("M99_delayroots_slope_strict_to_weak", "DelayRoots.lean", "projectedSlope_lt_quarter",
     [("(hx : C < x)", "(hx : C ≤ x)", 1)], "",
     "DelayRoots.false_slope_at_boundary (H 1 1 1 (by norm_num) (by norm_num) le_rfl)", None),
    # Researcher 001's audit of ae2c25a (B1, N1): 0 < a and 0 < h are load-bearing; boundary weakenings of a < 1, m h < 1;
    # 0 < C and 0 < eps together (each alone is redundant given the other, see projectedSlope_lt_quarter_of_C)
    ("M100_delayroots_sym_a_pos_dropped", "DelayRoots.lean", "symRoot_eq_one_or_lt",
     [("(ha0 : 0 < a)", "(ha0 : True)", 1)], "",
     "DelayRoots.false_symRoot_two (H (-2) trivial (by norm_num) 1 2 DelayRoots.symRoot_root_a_neg_two)", None),
    ("M101_delayroots_trans_h_pos_dropped", "DelayRoots.lean", "transRoot_lt_one",
     [("(h0 : 0 < h)", "(h0 : True)", 1)], "",
     "DelayRoots.false_one_inside (H 1 le_rfl 0 trivial (by norm_num) 0 1 DelayRoots.transRoot_root_h_zero)", None),
    ("M102_delayroots_sym_a_lt_one_to_le", "DelayRoots.lean", "symRoot_eq_one_or_lt",
     [("(ha1 : a < 1)", "(ha1 : a ≤ 1)", 1)], "",
     "DelayRoots.false_symRoot_minus_one (H 1 (by norm_num) le_rfl 1 (-1) DelayRoots.symRoot_root_a_one)", None),
    ("M103_delayroots_trans_mh_lt_one_to_le", "DelayRoots.lean", "transRoot_lt_one",
     [("(hmh : (m : ℝ) * h < 1)", "(hmh : (m : ℝ) * h ≤ 1)", 1)], "",
     "DelayRoots.false_I_inside (H 1 le_rfl 1 (by norm_num) (by norm_num) 1 Complex.I DelayRoots.transRoot_root_I)",
     None),
    ("M104_delayroots_slope_C_and_eps_pos_dropped", "DelayRoots.lean", "projectedSlope_lt_quarter",
     [("(hC : 0 < C) (hε : 0 < ε)", "(hC : True) (hε : True)", 1)], "",
     "DelayRoots.false_slope_both_negative (H (-1) (-1) (-1 / 2) trivial trivial (by norm_num))", None),
    # Researcher 001's audit of cce534d (N2): the C-only variant has its own two load-bearing hypotheses
    ("M105_delayroots_slopeC_C_pos_dropped", "DelayRoots.lean", "projectedSlope_lt_quarter_of_C",
     [("(hC : 0 < C)", "(hC : True)", 1)], "",
     "DelayRoots.false_slope_both_negative (H (-1) (-1) (-1 / 2) trivial (by norm_num))", None),
    ("M106_delayroots_slopeC_lt_to_le", "DelayRoots.lean", "projectedSlope_lt_quarter_of_C",
     [("(hx : C < x)", "(hx : C ≤ x)", 1)], "",
     "DelayRoots.false_slope_at_boundary (H 1 1 1 (by norm_num) le_rfl)", None),
    # ---- CommonRootSimple.lean (Arena_Researcher_06020041 cycle 13); numbered M110 ff. after the lock's M107-M109.
    # Each refutation is a proved negation of the whole weakened statement, stated in that file ----
    ("M110_commonroot_multiplicity_pos_dropped", "CommonRootSimple.lean", "root_multiplicity_one",
     [("(hh : 0 < h)", "(hh : True)", 1)], "", "CommonRootSimple.false_multiplicity_no_pos H", None),
    ("M111_commonroot_unit_upper_bound_dropped", "CommonRootSimple.lean", "unit_circle_root_unique_and_simple",
     [("(hh1 : h < 1)", "(hh1 : True)", 1)], "", "CommonRootSimple.false_unit_root_no_upper H", None),
    ("M112_commonroot_unit_pos_dropped", "CommonRootSimple.lean", "unit_circle_root_unique_and_simple",
     [("(hh : 0 < h)", "(hh : True)", 1)], "", "CommonRootSimple.false_unit_root_no_pos H", None),
    ("M113_commonroot_derivative_delay_factor_dropped", "CommonRootSimple.lean", "derivative_at_one",
     [("(((1 + (d : ℝ) * h : ℝ) : ℂ))", "(((1 + h : ℝ) : ℂ))", 1)], "",
     "CommonRootSimple.false_derivative_no_delay H", None),
    # ---- EngineStepRef.lean (Arena_Researcher_06020041 cycle 21 revision, audit-inbox 8fc0d24) ----
    ("M114_stepref_orbit_moves_backward", "EngineStepRef.lean", "orbit_invariant",
     [("v 0 k i + dt * Omega", "v 0 k i - dt * Omega", 1)], "", "EngineStepRef.false_orbit_backward H", None),
    ("M115_stepref_orbit_frequency_equation_dropped", "EngineStepRef.lean", "orbit_invariant",
     [("(horbit : Omega = omega + ((n : ℝ) - 1) * clippedWeight b *\n      Real.sin (-((d : ℝ) * dt * Omega)))",
       "(horbit : True)", 1)], "", "EngineStepRef.false_orbit_no_frequency H", None),
    ("M116_stepref_block_positive_weight_dropped", "EngineStepRef.lean", "head_derivative_block",
     [("(hb : 0 < b)", "(hb : True)", 1)], "", "EngineStepRef.false_block_no_pos H", None),
    ("M117_stepref_history_shift_dropped", "EngineStepRef.lean", "history_derivative",
     [("(v (k - 1) i) 0", "(v k i) 0", 1)], "", "EngineStepRef.false_history_no_shift H", None),
    ("M118_stepref_neighbor_reads_current_slot", "EngineStepRef.lean", "neighbor_derivative",
     [("(v d j - v 0 i)) 0", "(v 0 j - v 0 i)) 0", 1)], "", "EngineStepRef.false_neighbor_current_slot H", None),
    # ---- Arena bundle intake (MERGE_MANIFEST 2026-11-25, SPEC §17): statement mutants M131-M156 ----
    ("M131_queue_reachable_consistency_dropped", "ReachableQueue.lean", "reachable_consistent",
     [("(h : Consistent n d s)", "(h : True)", 1)], "", "ReachableQueue.false_reachable_no_consistent H", None),
    ("M132_queue_view_shift_lag_positive_dropped", "ReachableQueue.lean", "view_shift",
     [("(hk : k.val > 0)", "(hk : True)", 1)], "", "ReachableQueue.false_view_shift_no_pos H", None),
    ("M133_queuecomp_transfer_consistency_dropped", "QueueComposition.lean", "consistent_transfer",
     [("(h : ReachableQueue.Consistent n d s)", "(h : True)", 1)], "", "QueueComposition.false_transfer_no_consistent H", None),
    ("M134_matrixbridge_circle_consistency_dropped", "MatrixPhaseBridge.lean", "matrix_circle_bridge",
     [("(hc : Consistent n s)", "(hc : True)", 1)], "", "MatrixPhaseBridge.false_bridge_no_consistent H", None),
    ("M135_matrixbridge_scalar_uniform_dropped", "MatrixPhaseBridge.lean", "matrix_to_scalar",
     [("(hW : Uniform n W b)", "(hW : True)", 1)], "", "MatrixPhaseBridge.false_scalar_no_uniform H", None),
    ("M136_emanear_budget_startup_dropped", "EmaNearUnit.lean", "near_unit",
     [("(budget : alpha ^ N + delta ≤ epsilon)", "(budget : delta ≤ epsilon)", 1)], "", "EmaNearUnit.false_near_unit_no_startup H", None),
    ("M137_emanear_delta_nonneg_dropped", "EmaNearUnit.lean", "near_unit",
     [("(hd : 0 ≤ delta)", "(hd : True)", 1)], "", "EmaNearUnit.false_near_unit_no_delta_nonneg H", None),
    ("M138_emawrap_budget_startup_dropped", "EmaWrapInvariant.lean", "near_unit_circular_spread",
     [("(budget : alpha ^ N + (1 - Real.cos beta) ≤ epsilon)", "(budget : (1 - Real.cos beta) ≤ epsilon)", 1)], "", "EmaWrapInvariant.false_circular_no_startup H", None),
    ("M139_causal_step_alpha_nonneg_dropped", "CausalEMATracking.lean", "tracking_step_bound",
     [("(ha : 0 ≤ alpha)", "(ha : True)", 1)], "", "CausalEMATracking.false_step_bound_no_nonneg H", None),
    ("M140_causal_delayed_alpha_nonneg_dropped", "CausalEMATracking.lean", "delayed_tracking_bound",
     [("(ha : 0 ≤ alpha)", "(ha : True)", 1)], "", "CausalEMATracking.false_delayed_bound_no_nonneg H", None),
    ("M141_emasum_powers_reversed", "EMAFiniteSum.lean", "budget_eq_finite_sum",
     [("alpha ^ (n - 1 - k) * drift k", "alpha ^ k * drift k", 1)], "", "EMAFiniteSum.false_finite_sum_reversed H", None),
    ("M142_emasum_start_decay_dropped", "EMAFiniteSum.lean", "budget_eq_finite_sum",
     [("alpha ^ n * E +", "E +", 1)], "", "EMAFiniteSum.false_finite_sum_no_start_decay H", None),
    ("M143_transbridge_one_step_factor_one", "TransientBridge.lean", "one_step_bound",
     [("(81 / 64 : ℝ)", "(1 : ℝ)", 1)], "", "TransientBridge.false_one_step_factor_one H", None),
    ("M144_transbridge_two_step_quarter", "TransientBridge.lean", "two_step_bound",
     [("(1 / 2 : ℝ)", "(1 / 4 : ℝ)", 1)], "", "TransientBridge.false_two_step_quarter H", None),
    ("M145_transbridge_all_steps_factor_one", "TransientBridge.lean", "all_steps_bound",
     [("(81 / 64 : ℝ)", "(1 : ℝ)", 1)], "", "TransientBridge.false_all_steps_factor_one H", None),
    ("M146_transparam_roots_upper_dropped", "TransientParameter.lean", "stable_roots",
     [("(hc1 : c < 1)", "(hc1 : True)", 1)], "", "TransientParameter.false_stable_no_upper H", None),
    ("M147_transparam_roots_pos_dropped", "TransientParameter.lean", "stable_roots",
     [("(hc0 : 0 < c)", "(hc0 : True)", 1)], "", "TransientParameter.false_stable_no_pos H", None),
    ("M148_transparam_one_step_upper_dropped", "TransientParameter.lean", "one_step_bound",
     [("(hc1 : c ≤ 1)", "(hc1 : True)", 1)], "", "TransientParameter.false_one_step_no_upper H", None),
    ("M149_windowmax_step_threshold_dropped", "WindowMax.lean", "window_step",
     [("(ht : (n : ℝ) * c ≤ 2)", "(ht : True)", 1)], "", "WindowMax.false_window_step_no_threshold H", None),
    ("M150_windowmax_all_threshold_dropped", "WindowMax.lean", "window_all_steps",
     [("(ht : (n : ℝ) * c ≤ 2)", "(ht : True)", 1)], "", "WindowMax.false_window_all_no_threshold H", None),
    ("M151_windowmax_coefficient_size_dropped", "WindowMax.lean", "coefficient_bound",
     [("(hn : 2 ≤ n)", "(hn : True)", 1)], "", "WindowMax.false_coefficient_no_size H", None),
    ("M152_hetero_step_row_dropped", "HeteroStepRef.lean", "window_step",
     [("(hrow : ∀ i, dt * row n B i ≤ 1)", "(hrow : True)", 1)], "", "HeteroStepRef.false_window_step_no_row H", None),
    ("M153_hetero_step_nonneg_dropped", "HeteroStepRef.lean", "window_step",
     [("(hB : ∀ i j, 0 ≤ B i j)", "(hB : True)", 1)], "", "HeteroStepRef.false_window_step_no_nonneg H", None),
    ("M154_hetero_step_dt_nonneg_dropped", "HeteroStepRef.lean", "window_step",
     [("(hdt : 0 ≤ dt)", "(hdt : True)", 1)], "", "HeteroStepRef.false_window_step_no_dt H", None),
    ("M155_heteroguard_cap_dropped", "HeteroGuard.lean", "guarded_window_all_steps",
     [("(hcap : dt * ((a - delta + tol) / q) ≤ 1)", "(hcap : True)", 1)], "", "HeteroStepRef.false_guarded_no_cap H", None),
    ("M156_heteroguard_q_pos_dropped", "HeteroGuard.lean", "guarded_window_all_steps",
     [("(hq : 0 < q)", "(hq : True)", 1)], "", "HeteroStepRef.false_guarded_no_q H", None),
    # ---- Arena bundle audit follow-up (Researcher 001 note N5, SPEC §17.7): statement mutants M191-M201 for the
    # deposited theorems that had none (QueueComposition.initialized_trajectory_bridge cannot be mutated: its
    # statement has a `let`, and theorem_span/statement_prop stop at the first top-level `:=`). PREDECLARED in the commit that adds them, before any run: every one of
    # M191-M201 is expected REJECTED (kept proof fails for a real reason, refuted by its `false_*` with standard
    # axioms, control on the unmutated statement fails). None is expected to survive; a survivor would be reported
    # as UNEXPLAINED, not moved to KNOWN_SURVIVORS.
    ("M191_emanear_projection_startup_dropped", "EmaNearUnit.lean", "trace_projection_bound",
     [("(1 - alpha ^ N) * L ≤", "L ≤", 1)], "", "EmaNearUnit.false_projection_no_startup H", None),
    ("M192_emanear_norm_startup_dropped", "EmaNearUnit.lean", "trace_norm_bound",
     [("(1 - alpha ^ N) * L ≤", "L ≤", 1)], "", "EmaNearUnit.false_norm_no_startup H", None),
    ("M193_emanear_spread_budget_startup_dropped", "EmaNearUnit.lean", "near_unit_of_phase_spread",
     [("(budget : alpha ^ N + (1 - Real.cos beta) ≤ epsilon)", "(budget : (1 - Real.cos beta) ≤ epsilon)", 1)], "",
     "EmaNearUnit.false_spread_no_startup H", None),
    ("M194_emasum_delayed_alpha_nonneg_dropped", "EMAFiniteSum.lean", "delayed_tracking_sum",
     [("(ha : 0 ≤ alpha)", "(ha : True)", 1)], "", "EMAFiniteSum.false_delayed_sum_no_nonneg H", None),
    ("M195_queue_step_reachable_consistency_dropped", "ReachableQueue.lean", "step_reachable_consistent",
     [("(h : Consistent n d s)", "(h : True)", 1)], "", "ReachableQueue.false_step_reachable_no_consistent H", None),
    ("M196_queuecomp_finite_step_reads_head_slot", "QueueComposition.lean", "finite_abstract_step",
     [("history k i", "history 0 i", 1)], "", "QueueComposition.false_finite_step_head_slot H", None),
    ("M197_matrixbridge_direction_cos_dropped", "MatrixPhaseBridge.lean", "matrix_head_direction",
     [("W i j * (Real.cos ((d : ℝ) * dt * Omega) * (v d j - v 0 i))", "W i j * (v d j - v 0 i)", 1)], "",
     "MatrixPhaseBridge.false_head_direction_no_cos H", None),
    ("M198_transbridge_after_first_quarter", "TransientBridge.lean", "after_first_bound",
     [("(81 / 128 : ℝ)", "(1 / 4 : ℝ)", 1)], "", "TransientBridge.false_after_first_quarter H", None),
    ("M199_transbridge_eigenmode_nonzero_dropped", "TransientBridge.lean", "eigenmode_stable",
     [("(hne : v ≠ 0 ∨ w ≠ 0)", "(hne : True)", 1)], "", "TransientBridge.false_eigenmode_no_nonzero H", None),
    ("M200_transparam_eigenmode_nonzero_dropped", "TransientParameter.lean", "eigenmode_stable",
     [("(hne : v ≠ 0 ∨ w ≠ 0)", "(hne : True)", 1)], "", "TransientParameter.false_param_eigenmode_no_nonzero H",
     None),
    ("M201_hetero_all_steps_row_dropped", "HeteroStepRef.lean", "window_all_steps",
     [("(hrow : ∀ i, dt * row n B i ≤ 1)", "(hrow : True)", 1)], "", "HeteroStepRef.false_window_all_no_row H", None),
    # ---- H9(b) + H16 (GronwallEnvelope.lean, GateContraction.lean; SPEC §18). Distinct block from M300 on, so it
    # cannot collide with mutants added after M190 elsewhere. Every outcome predeclared KILLED in the first commit
    # that adds it (build rejected for a real proof failure, refuted by the named false_* theorem, term-specific).
    ("M300_envelope_upper_rho_nonneg_dropped", "GronwallEnvelope.lean", "scalar_envelope_upper",
     [("(hρ0 : 0 ≤ ρ)", "(hρ0 : True)", 1)], "",
     f"GronwallEnvelope.false_upper_no_rho_nonneg {via('H', ENV_UP, 4)}", None),
    ("M301_envelope_upper_start_nonneg_dropped", "GronwallEnvelope.lean", "scalar_envelope_upper",
     [("(hB0 : 0 ≤ B 0)", "(hB0 : True)", 1)], "",
     f"GronwallEnvelope.false_upper_no_start_nonneg {via('H', ENV_UP, 5)}", None),
    ("M302_envelope_upper_lam_le_one_dropped", "GronwallEnvelope.lean", "scalar_envelope_upper",
     [("(hlam1 : ∀ n, lam n ≤ 1)", "(hlam1 : True)", 1)], "",
     f"GronwallEnvelope.false_upper_no_lam_le_one {via('H', ENV_UP, 6)}", None),
    ("M303_envelope_lower_kappa_nonneg_dropped", "GronwallEnvelope.lean", "scalar_envelope_lower",
     [("(hκ0 : ∀ n, 0 ≤ κ n)", "(hκ0 : True)", 1)], "",
     f"GronwallEnvelope.false_lower_no_kappa_nonneg {via('H', ENV_LO, 6)}", None),
    ("M304_envelope_lower_rho_nonneg_dropped", "GronwallEnvelope.lean", "scalar_envelope_lower",
     [("(hρ0 : 0 ≤ ρ)", "(hρ0 : True)", 1)], "",
     f"GronwallEnvelope.false_lower_no_rho_nonneg {via('H', ENV_LO, 5)}", None),
    ("M305_edge_envelope_gamma_dt_le_one_dropped", "GronwallEnvelope.lean", "stepM_edge_envelope_upper",
     [("(hh1 : p.γ * p.dt ≤ 1)", "(hh1 : True)", 1)], WU_VARS,
     "GronwallEnvelope.false_envelope_gamma_dt_gt_one (fun B D hrec hDs hB0s {i j} hij hB0 n => "
     "@H (Fin 2) _ _ WeightUpdate.pH B D trivial hrec hDs hB0s i j hij hB0 n)", None),
    ("M306_edge_recurrence_gate_before_drive", "GronwallEnvelope.lean", "edge_recurrence",
     [("appliedFactor p (symM p D Bm) i j * max 0 ((1 - p.γ * p.dt) * Bm i j + p.dt * D i j)",
       "max 0 (appliedFactor p (symM p D Bm) i j * ((1 - p.γ * p.dt) * Bm i j) + p.dt * D i j)", 1)], CAP_VARS,
     "GronwallEnvelope.false_variant_gate_after_drive (fun D Bm hD hB {i j} hij => "
     "@H (Fin 2) _ _ pE D Bm hD hB i j hij)", None),
    ("M307_upper_geom_gronwall_rho_nonneg_dropped", "GronwallEnvelope.lean", "upper_geom_via_gronwall",
     [("(hρ0 : 0 ≤ ρ)", "(hρ0 : True)", 1)], "",
     f"GronwallEnvelope.false_upper_geom_rho_neg {via('H', 'x ρ β hρ0 hρ1 hstep', 3)}", None),
    ("M308_upper_geom_ne_one_dropped", "GronwallEnvelope.lean", "upper_geom_of_ne_one",
     [("(hρ1 : ρ ≠ 1)", "(hρ1 : True)", 1)], "",
     f"GronwallEnvelope.false_upper_geom_rho_one {via('H', 'x ρ β hρ0 hρ1 hstep', 4)}", None),
    ("M309_lipschitz_gate_off_hypotheses_dropped", "GateContraction.lean", "stepM_entry_lipschitz_gate_off",
     [("(hoff : ¬ MatrixForm.GateOnM p D B) (hoff' : ¬ MatrixForm.GateOnM p D B')", "(hoff : True) (hoff' : True)", 1)],
     CAP_VARS, "GateContraction.false_entry_lipschitz_no_gate_off (fun D B B' i j => "
     "@H (Fin 3) _ _ pE (by norm_num [pE]) D B B' trivial trivial i j)", None),
    ("M310_lipschitz_gamma_dt_le_one_dropped", "GateContraction.lean", "stepM_entry_lipschitz_gate_off",
     [("(hh1 : p.γ * p.dt ≤ 1)", "(hh1 : True)", 1)], CAP_VARS,
     "GateContraction.false_entry_lipschitz_gamma_dt_gt_one (fun D B B' hoff hoff' i j => "
     "@H (Fin 2) _ _ WeightUpdate.pH trivial D B B' hoff hoff' i j)", None),
    ("M311_lipschitz_symm_symmetry_dropped", "GateContraction.lean", "stepM_entry_lipschitz_gate_off_symm",
     [("(hB : ∀ i j, B i j = B j i) (hB' : ∀ i j, B' i j = B' j i)", "(hB : True) (hB' : True)", 1)], CAP_VARS,
     "GateContraction.false_lipschitz_symm_no_symm (fun D B B' hoff hoff' i j => "
     "@H (Fin 2) _ _ pE (by norm_num [pE]) D B B' trivial trivial hoff hoff' i j)", None),
    ("M312_contracting_lam_le_one_dropped", "GateContraction.lean", "scalar_map_contracting",
     [("(hl1 : lam ≤ 1)", "(hl1 : True)", 1)], "",
     f"GateContraction.false_contracting_lam_gt_one {via('H', 'lam ρ d hl0 hl1 hρ0 hρ1', 4)}", None),
    # Audit follow-up (Researcher 001 on 952f87d: coverage note and F3). Predeclared KILLED before any run of them.
    ("M317_edge_envelope_lower_gamma_dt_le_one_dropped", "GronwallEnvelope.lean", "stepM_edge_envelope_lower",
     [("(hh1 : p.γ * p.dt ≤ 1)", "(hh1 : True)", 1)], WU_VARS,
     "GronwallEnvelope.false_lower_envelope_gamma_dt_gt_one (fun B D κ hrec hDs hB0s {i j} hij hκ0 hκ n => "
     "@H (Fin 2) _ _ WeightUpdate.pH B D trivial κ hrec hDs hB0s i j hij hκ0 hκ n)", None),
    ("M318_binding_witness_l1_six_fifths_to_five_fourths", "GateContraction.lean", "binding_witness_l1",
     [("6 / 5 * l1 B3 B3'", "5 / 4 * l1 B3 B3'", 1)], "",
     "GateContraction.false_binding_l1_five_fourths H", None),
]

UR_OLD = "def unitRate (_ : ℕ) (_ : Fin 2) : ℝ := 1\n"
ALT_OLD = "def altU (n : ℕ) (_ : Fin 2) : ℝ := if n % 2 = 0 then Real.pi else 0\n"

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
# P6 (CoherenceMotion.lean): closed-number probes at (1/2, 3/4, the engine alpha); the engine-alpha pins are
# `engine_speed_limit_value` (pins alphaE) and `engine_factor_two_attained` (pins rTrace at alphaE)
VP_MOT = ["probe_half_drop", "probe_half_increase", "probe_two_step", "probe_diagonal_zero", "probe_asym_state",
          "engine_speed_limit_value", "engine_factor_two_attained",
          "alphaE_exact", "engine_pow_1213_gt_half", "engine_pow_1214_lt_half"]
# the equality `alphaE = exp(-(857/1500000))` and the two closed numbers `alpha^1213 > 1/2 > alpha^1214` pin the engine
# alpha exactly (mean-omega numerators 856 and 858 fail one of them; audit of d551540, note N3)
PIN_ALPHA_E = ["engine_speed_limit_value", "alphaE_exact", "engine_pow_1213_gt_half", "engine_pow_1214_lt_half"]
VP_TS = ["probe_gate_scales_row", "probe_aux_reads_old_and_new", "probe_aux_time_and_new_entry"]
# Phase lock (FrequencyLock.lean): the witnesses that pin the rate definitions `unitRate` and `altU`
VP_FL = ["probe_unitRate_nonzero", "probe_altU_not_constant",
         # N2 (Researcher 001, e50102c): value probes for the shape the witness theorems rely on
         # (period 2, node-independent, time-independent); value probes must be `probe_*` equalities
         "probe_altU_period_two", "probe_unitRate_constant",
         # #41 note 1 (Researcher 001, 9fd50ba): pin the values of altU, so pi/2 in place of pi is killed
         "probe_altU_values"]
# CommonRootSimple.lean / EngineStepRef.lean (Arena cycles 13 and 21): closed-number evaluations of the definitions,
# proved by unfolding them in the probe itself
VP_CR = ["probe_commonPoly_eval_d1", "probe_commonPoly_eval_d2"]
VP_SR = ["probe_clippedWeight_values", "probe_phaseHead_value", "probe_phaseHead_negative_weight", "probe_phaseStep_values", "probe_orbitPath_value"]
# Arena bundle intake (SPEC §17): closed-number evaluations appended to each file
VP_ARENA = {"ReachableQueue.lean": ["probe_shift_values", "probe_view_values", "probe_head_value"],
            "QueueComposition.lean": ["probe_abstractState_values", "probe_initState_values"],
            "MatrixPhaseBridge.lean": ["probe_matrixHead_value", "probe_engineStep_shift", "probe_engineStep_head",
                                       "probe_refInput_values"],
            "EmaWrapInvariant.lean": ["probe_arcBound_values"],
            "CausalEMATracking.lean": ["probe_budget_values"],
            "TransientBridge.lean": ["probe_step_values", "probe_energy_value"],
            "TransientParameter.lean": ["probe_step_values", "probe_energy_value", "probe_mode_values"],
            "WindowMax.lean": ["probe_next_values"],
            "HeteroStepRef.lean": ["probe_linearStep_values", "probe_phaseHeadW_value"]}
# H16 (GateContraction.lean, SPEC §18): closed-number probes, each proved from the definitions in the probe itself
VP_H16 = ["probe_scalarMap_value", "probe_scalarMap_clamp", "probe_l1_B3", "probe_binding_ratio_six_fifths"]
# H9 (GronwallEnvelope.lean, audit follow-up F3): statement-pin probe of the `pE` envelope constants
VP_H9 = ["probe_envelope_pE_orbit"]
VALUE_PROBES = {"PhaseIncrement.lean": VP_INC, "PhaseCoherence.lean": VP_COH, "TrajectoryInvariants.lean": VP_TS,
                "CoherenceMotion.lean": VP_MOT,
                "FrequencyLock.lean": VP_FL,
                "CommonRootSimple.lean": VP_CR, "EngineStepRef.lean": VP_SR,
                "GateContraction.lean": VP_H16, "GronwallEnvelope.lean": VP_H9,
                **VP_ARENA}
CP_OLD = "  X ^ (d + 1) - C (((1 - h : ℝ) : ℂ)) * X ^ d - C (h : ℂ)\n"
CW_OLD = "def clippedWeight (b : ℝ) : ℝ := max 0 b\n"
HEAD_OLD = ("  x 0 i + dt * (omega + ∑ j ∈ Finset.univ.erase i,\n"
            "    clippedWeight b * Real.sin (x d j - x 0 i))\n")
STEP_OLD = "  if k = 0 then phaseHead n d dt omega b x i else x (k - 1) i\n"
ORBIT_OLD = "  theta - (k : ℝ) * dt * Omega + t * v k i\n"
WU_DEF_OLD = "def weightUpdate (p : Params) (D B : Weights V) : Weights V := stepM p D B\n"
FB_OLD = "  (U n state.1 state.2 Bnew, Bnew)\n"
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
RT_BODY = "PhaseCoherence.reported (PhaseCoherence.coherenceTrace alpha C0 d x0 u omega tau n) i j"
RT_OLD = "ℝ :=\n  " + RT_BODY + "\n"
AE_OLD = "def alphaE : ℝ := Real.exp (-((1/100) / (25 / (857/600))))\n"


def rt(new):
    """edit of the body of `rTrace` (CoherenceMotion.lean)"""
    return [(RT_OLD, "ℝ :=\n  " + new + "\n", 1)]


def ae(new):
    """edit of the engine alpha `alphaE` (CoherenceMotion.lean)"""
    return [(AE_OLD, "def alphaE : ℝ := " + new + "\n", 1)]

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
    # ---- P6 (CoherenceMotion.lean), numbered after M58: mutants of the observable `rTrace` and of the engine alpha ----
    ("M70_motion_rtrace_reads_next_trace", "CoherenceMotion.lean",
     rt("PhaseCoherence.reported (PhaseCoherence.coherenceTrace alpha C0 d x0 u omega tau (n + 1)) i j"),
     ["probe_half_drop", "probe_half_increase", "probe_two_step", "engine_factor_two_attained"]),
    # ---- C014 (TrajectoryInvariants.lean); M74-M78 follow the C014 statement mutants M71-M73 ----
    ("M74_trajectory_weight_update_bypasses_gate", "TrajectoryInvariants.lean",
     [(WU_DEF_OLD, "def weightUpdate (p : Params) (D B : Weights V) : Weights V := symM p D B\n", 1)],
     ["probe_gate_scales_row"]),
    ("M75_trajectory_aux_update_gets_old_B_only", "TrajectoryInvariants.lean",
     [(FB_OLD, "  (U n state.1 state.2 state.2, Bnew)\n", 1)], ["probe_aux_reads_old_and_new"]),
    ("M76_trajectory_aux_update_gets_new_B_only", "TrajectoryInvariants.lean",
     [(FB_OLD, "  (U n state.1 Bnew Bnew, Bnew)\n", 1)], ["probe_aux_reads_old_and_new"]),
    # Researcher 001's two survivors on 3a4c75b (audit note 3), killed by the second probe:
    ("M77_trajectory_aux_update_gets_drive_not_new_B", "TrajectoryInvariants.lean",
     [(FB_OLD, "  (U n state.1 state.2 (F n state.1 state.2), Bnew)\n", 1)], ["probe_aux_time_and_new_entry"]),
    ("M78_trajectory_aux_update_gets_next_time", "TrajectoryInvariants.lean",
     [(FB_OLD, "  (U (n + 1) state.1 state.2 Bnew, Bnew)\n", 1)], ["probe_aux_time_and_new_entry"]),
    # ---- P6 (CoherenceMotion.lean), continued: M79-M86 (M79-M84 renumbered from M71-M76 after C014 took M71-M78) ----
    ("M79_motion_rtrace_one_sided_not_symmetrised", "CoherenceMotion.lean",
     rt("‖PhaseCoherence.coherenceTrace alpha C0 d x0 u omega tau n i j‖"), ["probe_asym_state"]),
    ("M80_motion_rtrace_diagonal_one", "CoherenceMotion.lean",
     rt("@ite ℝ (i = j) (Classical.propDecidable _) 1 (" + RT_BODY + ")"), ["probe_diagonal_zero"]),
    ("M81_motion_rtrace_single_step_from_c0", "CoherenceMotion.lean",
     rt("PhaseCoherence.reported (PhaseCoherence.coherenceStep alpha C0 d x0 u omega tau n) i j"),
     ["probe_half_drop", "probe_two_step", "engine_factor_two_attained"]),
    ("M82_motion_alphaE_dt_ten_times_too_large", "CoherenceMotion.lean",
     ae("Real.exp (-((1/10) / (25 / (857/600))))"), PIN_ALPHA_E),
    ("M83_motion_alphaE_mean_omega_one", "CoherenceMotion.lean",
     ae("Real.exp (-((1/100) / (25 / 1)))"), PIN_ALPHA_E),
    ("M84_motion_alphaE_sign_flipped", "CoherenceMotion.lean",
     ae("Real.exp ((1/100) / (25 / (857/600)))"), PIN_ALPHA_E),
    # audit N3 (d551540): near-miss numerators of the mean omega 857/600, the one-unit edits the old range pin admitted
    ("M85_motion_alphaE_mean_omega_numerator_856", "CoherenceMotion.lean",
     ae("Real.exp (-((1/100) / (25 / (856/600))))"), PIN_ALPHA_E),
    ("M86_motion_alphaE_mean_omega_numerator_858", "CoherenceMotion.lean",
     ae("Real.exp (-((1/100) / (25 / (858/600))))"), PIN_ALPHA_E),
    # ---- Phase lock (FrequencyLock.lean): the rate definitions of the witnesses ----
    ("M92_lock_unit_rate_frozen", "FrequencyLock.lean", [(UR_OLD, "def unitRate (_ : ℕ) (_ : Fin 2) : ℝ := 0\n", 1)],
     ["probe_unitRate_nonzero"]),
    ("M93_lock_alt_rate_constant", "FrequencyLock.lean", [(ALT_OLD, "def altU (_ : ℕ) (_ : Fin 2) : ℝ := Real.pi\n", 1)],
     ["probe_altU_not_constant"]),
    # #41 note 1 (Researcher 001, 9fd50ba), numbered after DelayRoots' M95-M106: the wrong angle, the wrong period,
    # and a time-varying unit rate
    ("M107_lock_alt_rate_half_pi", "FrequencyLock.lean",
     [(ALT_OLD, "def altU (n : ℕ) (_ : Fin 2) : ℝ := if n % 2 = 0 then Real.pi / 2 else 0\n", 1)],
     ["probe_altU_values"]),
    ("M108_lock_alt_rate_period_three", "FrequencyLock.lean",
     [(ALT_OLD, "def altU (n : ℕ) (_ : Fin 2) : ℝ := if n % 3 = 0 then Real.pi else 0\n", 1)],
     ["probe_altU_period_two"]),
    ("M109_lock_unit_rate_time_varying", "FrequencyLock.lean",
     [(UR_OLD, "def unitRate (n : ℕ) (_ : Fin 2) : ℝ := (n : ℝ) + 1\n", 1)],
     ["probe_unitRate_constant"]),
    # ---- CommonRootSimple.lean: the polynomial (numbered after the statement mutants M110-M118) ----
    ("M119_commonroot_constant_sign_flipped", "CommonRootSimple.lean",
     [(CP_OLD, "  X ^ (d + 1) - C (((1 - h : ℝ) : ℂ)) * X ^ d + C (h : ℂ)\n", 1)], VP_CR),
    ("M120_commonroot_middle_power_shifted", "CommonRootSimple.lean",
     [(CP_OLD, "  X ^ (d + 1) - C (((1 - h : ℝ) : ℂ)) * X ^ (d + 1) - C (h : ℂ)\n", 1)], VP_CR),
    ("M121_commonroot_middle_coefficient_one_plus_h", "CommonRootSimple.lean",
     [(CP_OLD, "  X ^ (d + 1) - C (((1 + h : ℝ) : ℂ)) * X ^ d - C (h : ℂ)\n", 1)], VP_CR),
    # ---- EngineStepRef.lean: clip, head, step, orbit ----
    ("M122_stepref_clip_dropped", "EngineStepRef.lean", [(CW_OLD, "def clippedWeight (b : ℝ) : ℝ := b\n", 1)],
     ["probe_clippedWeight_values"]),
    ("M123_stepref_clip_min_for_max", "EngineStepRef.lean",
     [(CW_OLD, "def clippedWeight (b : ℝ) : ℝ := min 0 b\n", 1)], ["probe_clippedWeight_values"]),
    ("M124_stepref_head_self_coupling", "EngineStepRef.lean",
     [(HEAD_OLD, "  x 0 i + dt * (omega + ∑ j : Fin n,\n    clippedWeight b * Real.sin (x d j - x 0 i))\n", 1)],
     ["probe_phaseHead_value"]),
    ("M125_stepref_head_reads_current_slot", "EngineStepRef.lean",
     [(HEAD_OLD, "  x 0 i + dt * (omega + ∑ j ∈ Finset.univ.erase i,\n"
                 "    clippedWeight b * Real.sin (x 0 j - x 0 i))\n", 1)], ["probe_phaseHead_value"]),
    ("M126_stepref_head_sine_reversed", "EngineStepRef.lean",
     [(HEAD_OLD, "  x 0 i + dt * (omega + ∑ j ∈ Finset.univ.erase i,\n"
                 "    clippedWeight b * Real.sin (x 0 i - x d j))\n", 1)], ["probe_phaseHead_value"]),
    ("M127_stepref_head_dt_on_omega_only", "EngineStepRef.lean",
     [(HEAD_OLD, "  x 0 i + dt * omega + (∑ j ∈ Finset.univ.erase i,\n"
                 "    clippedWeight b * Real.sin (x d j - x 0 i))\n", 1)], ["probe_phaseHead_value"]),
    ("M128_stepref_history_not_shifted", "EngineStepRef.lean",
     [(STEP_OLD, "  if k = 0 then phaseHead n d dt omega b x i else x k i\n", 1)], ["probe_phaseStep_values"]),
    ("M129_stepref_orbit_sign_flipped", "EngineStepRef.lean",
     [(ORBIT_OLD, "  theta + (k : ℝ) * dt * Omega + t * v k i\n", 1)], ["probe_orbitPath_value"]),
    # #44 note N1 (Researcher 001, d3dc332): the head uses the raw weight b, bypassing the clip (engine np.maximum)
    ("M130_stepref_head_raw_weight", "EngineStepRef.lean",
     [(HEAD_OLD, "  x 0 i + dt * (omega + ∑ j ∈ Finset.univ.erase i,\n"
                 "    b * Real.sin (x d j - x 0 i))\n", 1)], ["probe_phaseHead_negative_weight"]),
    # ---- Arena bundle intake (SPEC §17): definition mutants M157-M190 ----
    ("M157_queue_shift_not_shifted", "ReachableQueue.lean",
     [("    s.history ⟨j.val + 1, by have := j.isLt; omega⟩ i⟩\n", "    s.history j i⟩\n", 1)], ["probe_shift_values"]),
    ("M158_queue_shift_not_appended", "ReachableQueue.lean",
     [("  ⟨out, fun j i => if h : j.val = d then out i else\n", "  ⟨out, fun j i => if h : j.val = d then s.history j i else\n", 1)], ["probe_shift_values"]),
    ("M159_queue_view_not_reversed", "ReachableQueue.lean",
     [("  ⟨d - k.val, by have := k.isLt; omega⟩\n", "  ⟨k.val, by have := k.isLt; omega⟩\n", 1)], ["probe_view_values"]),
    ("M160_queue_head_reads_newest", "ReachableQueue.lean",
     [("    W i j * Real.sin (s.history 0 j - s.theta i))\n", "    W i j * Real.sin (s.history (newestIndex d) j - s.theta i))\n", 1)], ["probe_head_value"]),
    ("M161_queuecomp_view_not_reversed", "QueueComposition.lean",
     [("then ReachableQueue.view n d s ⟨k, by omega⟩ i else 0⟩\n", "then s.history ⟨k, by omega⟩ i else 0⟩\n", 1)], ["probe_abstractState_values"]),
    ("M162_queuecomp_init_zero", "QueueComposition.lean",
     [("  ⟨theta, fun _ i => theta i⟩\n", "  ⟨theta, fun _ _ => 0⟩\n", 1)], ["probe_initState_values"]),
    ("M163_matrixbridge_head_current_slot", "MatrixPhaseBridge.lean",
     [("W i j * Real.sin (x d j - x 0 i))\n", "W i j * Real.sin (x 0 j - x 0 i))\n", 1)], ["probe_matrixHead_value"]),
    ("M164_matrixbridge_head_sine_reversed", "MatrixPhaseBridge.lean",
     [("W i j * Real.sin (x d j - x 0 i))\n", "W i j * Real.sin (x 0 i - x d j))\n", 1)], ["probe_matrixHead_value"]),
    ("M165_matrixbridge_step_not_shifted", "MatrixPhaseBridge.lean",
     [("if k = 0 then out i else s.history (k - 1) i⟩\n", "if k = 0 then out i else s.history k i⟩\n", 1)], ["probe_engineStep_shift"]),
    ("M166_matrixbridge_step_reads_slot_zero", "MatrixPhaseBridge.lean",
     [("    W i j * Real.sin (s.history d j - s.theta i))\n", "    W i j * Real.sin (s.history 0 j - s.theta i))\n", 1)], ["probe_engineStep_head"]),
    ("M167_matrixbridge_refinput_history_at_zero", "MatrixPhaseBridge.lean",
     [("  if k = 0 then s.theta i else s.history k i\n", "  if k = 0 then s.history 0 i else s.history k i\n", 1)], ["probe_refInput_values"]),
    ("M168_emawrap_arcbound_reversed", "EmaWrapInvariant.lean",
     [("Prop := Real.cos beta ≤ Real.cos phi\n", "Prop := Real.cos phi ≤ Real.cos beta\n", 1)], ["probe_arcBound_values"]),
    ("M169_causal_budget_drift_scaled", "CausalEMATracking.lean",
     [("  | n + 1 => alpha * budget alpha E drift n + drift n\n", "  | n + 1 => alpha * budget alpha E drift n + (1 - alpha) * drift n\n", 1)], ["probe_budget_values"]),
    ("M170_causal_budget_no_decay", "CausalEMATracking.lean",
     [("  | n + 1 => alpha * budget alpha E drift n + drift n\n", "  | n + 1 => budget alpha E drift n + drift n\n", 1)], ["probe_budget_values"]),
    ("M171_causal_budget_zero_start", "CausalEMATracking.lean",
     [("  | 0 => E\n", "  | 0 => 0\n", 1)], ["probe_budget_values"]),
    ("M172_transbridge_stepsize_third", "TransientBridge.lean",
     [("def stepSize : ℝ := 1 / 4\n", "def stepSize : ℝ := 1 / 3\n", 1)], ["probe_step_values"]),
    ("M173_transbridge_step_coefficient_one_c", "TransientBridge.lean",
     [("  ((1 - 2 * stepSize) * p.1 - stepSize * p.2, p.1)\n", "  ((1 - stepSize) * p.1 - stepSize * p.2, p.1)\n", 1)], ["probe_step_values"]),
    ("M174_transbridge_step_delayed_sign", "TransientBridge.lean",
     [("  ((1 - 2 * stepSize) * p.1 - stepSize * p.2, p.1)\n", "  ((1 - 2 * stepSize) * p.1 + stepSize * p.2, p.1)\n", 1)], ["probe_step_values"]),
    ("M175_transbridge_step_not_shifted", "TransientBridge.lean",
     [("  ((1 - 2 * stepSize) * p.1 - stepSize * p.2, p.1)\n", "  ((1 - 2 * stepSize) * p.1 - stepSize * p.2, p.2)\n", 1)], ["probe_step_values"]),
    ("M176_transbridge_energy_one_slot", "TransientBridge.lean",
     [("def energy (p : ℝ × ℝ) : ℝ := p.1 ^ 2 + p.2 ^ 2\n", "def energy (p : ℝ × ℝ) : ℝ := p.1 ^ 2\n", 1)], ["probe_energy_value"]),
    ("M177_transparam_step_coefficient_one_c", "TransientParameter.lean",
     [(":= ((1 - 2 * c) * p.1 - c * p.2, p.1)\n", ":= ((1 - c) * p.1 - c * p.2, p.1)\n", 1)], ["probe_step_values"]),
    ("M178_transparam_step_delayed_sign", "TransientParameter.lean",
     [(":= ((1 - 2 * c) * p.1 - c * p.2, p.1)\n", ":= ((1 - 2 * c) * p.1 + c * p.2, p.1)\n", 1)], ["probe_step_values"]),
    ("M179_transparam_step_not_shifted", "TransientParameter.lean",
     [(":= ((1 - 2 * c) * p.1 - c * p.2, p.1)\n", ":= ((1 - 2 * c) * p.1 - c * p.2, p.2)\n", 1)], ["probe_step_values"]),
    ("M180_transparam_energy_one_slot", "TransientParameter.lean",
     [("def energy (p : ℝ × ℝ) : ℝ := p.1 ^ 2 + p.2 ^ 2\n", "def energy (p : ℝ × ℝ) : ℝ := p.1 ^ 2\n", 1)], ["probe_energy_value"]),
    ("M181_transparam_mode_not_mean_zero", "TransientParameter.lean",
     [("if i = 1 then -1 else 0\n", "if i = 1 then 1 else 0\n", 1)], ["probe_mode_values"]),
    ("M182_windowmax_head_coefficient_n", "WindowMax.lean",
     [("  if k = 0 then (1 - ((n : ℝ) - 1) * c) * v 0 - c * v d else v (k - 1)\n", "  if k = 0 then (1 - (n : ℝ) * c) * v 0 - c * v d else v (k - 1)\n", 1)], ["probe_next_values"]),
    ("M183_windowmax_delayed_sign", "WindowMax.lean",
     [("  if k = 0 then (1 - ((n : ℝ) - 1) * c) * v 0 - c * v d else v (k - 1)\n", "  if k = 0 then (1 - ((n : ℝ) - 1) * c) * v 0 + c * v d else v (k - 1)\n", 1)], ["probe_next_values"]),
    ("M184_windowmax_reads_slot_zero", "WindowMax.lean",
     [("  if k = 0 then (1 - ((n : ℝ) - 1) * c) * v 0 - c * v d else v (k - 1)\n", "  if k = 0 then (1 - ((n : ℝ) - 1) * c) * v 0 - c * v 0 else v (k - 1)\n", 1)], ["probe_next_values"]),
    ("M185_windowmax_not_shifted", "WindowMax.lean",
     [("  if k = 0 then (1 - ((n : ℝ) - 1) * c) * v 0 - c * v d else v (k - 1)\n", "  if k = 0 then (1 - ((n : ℝ) - 1) * c) * v 0 - c * v d else v k\n", 1)], ["probe_next_values"]),
    ("M186_hetero_linear_coefficient_plus", "HeteroStepRef.lean",
     [("  if k = 0 then (1 - dt * row n B i) * v 0 i + dt * ∑ j, B i j * v d j\n", "  if k = 0 then (1 + dt * row n B i) * v 0 i + dt * ∑ j, B i j * v d j\n", 1)], ["probe_linearStep_values"]),
    ("M187_hetero_linear_reads_slot_zero", "HeteroStepRef.lean",
     [("  if k = 0 then (1 - dt * row n B i) * v 0 i + dt * ∑ j, B i j * v d j\n", "  if k = 0 then (1 - dt * row n B i) * v 0 i + dt * ∑ j, B i j * v 0 j\n", 1)], ["probe_linearStep_values"]),
    ("M188_hetero_linear_not_shifted", "HeteroStepRef.lean",
     [("  else v (k - 1) i\n", "  else v k i\n", 1)], ["probe_linearStep_values"]),
    ("M189_hetero_row_without_diagonal", "HeteroStepRef.lean",
     [("  ∑ j : Fin n, B i j\n", "  ∑ j ∈ Finset.univ.erase i, B i j\n", 1)], ["probe_linearStep_values"]),
    ("M190_hetero_head_current_slot", "HeteroStepRef.lean",
     [("    B i j * Real.sin (x d j - x 0 i))\n", "    B i j * Real.sin (x 0 j - x 0 i))\n", 1)], ["probe_phaseHeadW_value"]),
    # ---- H16 (GateContraction.lean; SPEC §18): definition mutants, predeclared KILLED by the named value probes
    ("M313_scalarMap_gate_before_drive", "GateContraction.lean",
     [("def scalarMap (lam ρ d : ℝ) (x : ℝ) : ℝ := lam * max 0 (ρ * x + d)\n", "def scalarMap (lam ρ d : ℝ) (x : ℝ) : ℝ := max 0 (lam * (ρ * x) + d)\n", 1)],
     ["probe_scalarMap_value"]),
    ("M314_scalarMap_clamp_dropped", "GateContraction.lean",
     [("def scalarMap (lam ρ d : ℝ) (x : ℝ) : ℝ := lam * max 0 (ρ * x + d)\n", "def scalarMap (lam ρ d : ℝ) (x : ℝ) : ℝ := lam * (ρ * x + d)\n", 1)], ["probe_scalarMap_clamp"]),
    ("M315_l1_abs_dropped", "GateContraction.lean",
     [("def l1 (X Y : Fin 3 → Fin 3 → ℝ) : ℝ := ∑ i, ∑ j, |X i j - Y i j|\n",
       "def l1 (X Y : Fin 3 → Fin 3 → ℝ) : ℝ := ∑ i, ∑ j, (X i j - Y i j)\n", 1)], ["probe_l1_B3"]),
    ("M316_B3prime_raised_one_side_only", "GateContraction.lean",
     [("![13 / 30, 0, 1 / 3]", "![1 / 3, 0, 1 / 3]", 1)], ["probe_l1_B3"]),
    # Audit follow-up (F3): the headline constants, pinned by statement-pin probes. Predeclared KILLED.
    ("M319_binding_witness_l1_six_fifths_to_one", "GateContraction.lean",
     [("    6 / 5 * l1 B3 B3' < l1 (stepM", "    1 * l1 B3 B3' < l1 (stepM", 1)], ["probe_binding_ratio_six_fifths"]),
    ("M320_envelope_pE_eight_thirds_to_three", "GronwallEnvelope.lean",
     [("    B n i j ≤ (19997 / 20000 : ℝ) ^ n * B 0 i j + (1 - (19997 / 20000 : ℝ) ^ n) * (8 / 3) := by\n",
       "    B n i j ≤ (19997 / 20000 : ℝ) ^ n * B 0 i j + (1 - (19997 / 20000 : ℝ) ^ n) * 3 := by\n", 1)],
     ["probe_envelope_pE_orbit"]),
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
    ("E11_trajectory_feedback_let_inlined", "TrajectoryInvariants.lean",
     [(FB_OLD, "  (U n state.1 state.2 (weightUpdate (p n) (F n state.1 state.2) state.2),\n"
               "    weightUpdate (p n) (F n state.1 state.2) state.2)\n", 1)]),
    # P6: `reported` is symmetric, so reading it at (j, i) is the same observable; the symmetrisation written out; the
    # engine alpha written as the reduced fraction / with T_window = 15000/857 (the same real)
    ("E12_motion_rtrace_reads_j_i", "CoherenceMotion.lean",
     rt("PhaseCoherence.reported (PhaseCoherence.coherenceTrace alpha C0 d x0 u omega tau n) j i")),
    ("E13_motion_alphaE_reduced_fraction", "CoherenceMotion.lean", ae("Real.exp (-(857 / 1500000))")),
    ("E14_motion_rtrace_symmetrisation_written_out", "CoherenceMotion.lean",
     rt("@ite ℝ (i = j) (Classical.propDecidable _) 0 ((‖PhaseCoherence.coherenceTrace alpha C0 d x0 u omega tau n i j‖"
        " + ‖PhaseCoherence.coherenceTrace alpha C0 d x0 u omega tau n j i‖) / 2)")),
    ("E15_motion_alphaE_t_window_reduced", "CoherenceMotion.lean", ae("Real.exp (-((1/100) / (15000 / 857)))")),
    # Phase lock: any nonzero constant rate is the same witness (numbered after c016's renumbered E12-E15)
    ("E16_lock_unit_rate_five", "FrequencyLock.lean", [(UR_OLD, "def unitRate (_ : ℕ) (_ : Fin 2) : ℝ := 5\n", 1)]),
    # #41 note 1: the same altU with the branches swapped must not be killed by probe_altU_values
    ("E17_lock_alt_rate_branches_swapped", "FrequencyLock.lean",
     [(ALT_OLD, "def altU (n : ℕ) (_ : Fin 2) : ℝ := if n % 2 = 1 then 0 else Real.pi\n", 1)]),
    # Arena cycles 13 and 21 (the researcher's P-E1 for each file, plus a commuted max)
    ("E18_commonroot_top_power_split", "CommonRootSimple.lean",
     [(CP_OLD, "  X ^ d * X - C (((1 - h : ℝ) : ℂ)) * X ^ d - C (h : ℂ)\n", 1)]),
    ("E19_stepref_sine_written_negated", "EngineStepRef.lean",
     [(HEAD_OLD, "  x 0 i + dt * (omega + ∑ j ∈ Finset.univ.erase i,\n"
                 "    clippedWeight b * -Real.sin (x 0 i - x d j))\n", 1)]),
    ("E20_stepref_clip_max_commuted", "EngineStepRef.lean",
     [(CW_OLD, "def clippedWeight (b : ℝ) : ℝ := max b 0\n", 1)]),
    # Arena bundle intake (SPEC §17): equivalent rewrites that must not be killed
    ("E21_windowmax_delayed_term_commuted", "WindowMax.lean",
     [("  if k = 0 then (1 - ((n : ℝ) - 1) * c) * v 0 - c * v d else v (k - 1)\n",
       "  if k = 0 then (1 - ((n : ℝ) - 1) * c) * v 0 - v d * c else v (k - 1)\n", 1)]),
    ("E22_transparam_coefficient_split", "TransientParameter.lean",
     [(":= ((1 - 2 * c) * p.1 - c * p.2, p.1)\n", ":= ((1 - c - c) * p.1 - c * p.2, p.1)\n", 1)]),
    ("E23_causal_budget_sum_commuted", "CausalEMATracking.lean",
     [("  | n + 1 => alpha * budget alpha E drift n + drift n\n",
       "  | n + 1 => drift n + alpha * budget alpha E drift n\n", 1)]),
]

# Typo / invalid-mutant controls: must be classified INVALID (a name-reference or parse error line) and not killed.
TYPO_CONTROLS = [
    ("T1_misspelled_identifier_inputPhasorXX", "PhaseCoherence.lean", ci("inputPhasorXX d x0 u omega tau n i j")),
    ("T2_syntax_garbage_unbalanced_paren", "PhaseCoherence.lean", ci("inputPhasor d x0 u omega tau n i j )")),
    ("T3_misspelled_identifier_delayedIncrementXX", "PhaseIncrement.lean",
     [(DELAY_OLD, "  if d ≤ n then u (n - d) j else delayedIncrementXX", 1)]),
    ("T4_misspelled_identifier_reportedXX", "CoherenceMotion.lean",
     rt("PhaseCoherence.reportedXX (PhaseCoherence.coherenceTrace alpha C0 d x0 u omega tau n) i j")),
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
# H16 audit follow-up (predeclared SURVIVE in the commit that adds it): M321 strengthens the constant of
# `binding_witness_l1` from 6/5 to 123/100. The statement is still TRUE (exact ratio about 1.2391) and the kept proof
# closes it, and `probe_binding_ratio_six_fifths` still follows from it, so the Lean build passes: no Lean check can
# kill a true strengthening. Only the text pin in test_lean_gate_h9h16.py catches it.
KNOWN_SURVIVORS = [
    ("M321_binding_witness_l1_six_fifths_to_123_100", "GateContraction.lean",
     [("    6 / 5 * l1 B3 B3' < l1 (stepM", "    123 / 100 * l1 B3 B3' < l1 (stepM", 1)]),
]

# Classifier negative control (P3 rule change, see (a) above): the P2 deletion form of M1 fails to build with
# name-reference errors only; it must be classified as such and must NOT count as a build rejection.
LEGACY_NAME_ONLY = ("M1_legacy_delete_kernel_hypothesis", "GateMap.lean", "stepB_add_smul_of_branch",
                    [("    (hker : InCtrlKer G ctrl h)\n", "", 1)])

OPENS = ("open Finset\nopen AIEFGate.MatrixForm (CE KG toEdge stepM symM rowM)\n"
         "open AIEFGate.EngineWitness (pE driveE BE sE driveW BW)\nopen AIEFGate.RedTeam (hw ctrlX)\n"
         "open AIEFGate.Bridge (toR CtrlJ01)\nopen AIEFGate.ControllerFiber (vCtrl)\n"
         "open AIEFGate.Capacity (rowS kernelM gateM appliedFactor)\nopen AIEFGate.MatrixForm (preM)\n"
         "open AIEFGate.WeightUpdate (pdriveRow edgeFloor Good onGap Sstar)\n"
         "open AIEFGate.CoherenceMotion (rTrace)\n"
         "open AIEFGate.TrajectorySafety (Weights weightsTrace Structural)\n"
         "open AIEFGate.PhaseCoherence (coherenceInput coherenceTrace reported)\n"
         "open Polynomial (derivative)\nopen AIEFGate.CommonRootSimple (commonPoly)\n"
         "open AIEFGate.EngineStepRef (clippedWeight phaseHead phaseStep orbitPath)\n")
# Per-file opens for the refutation files of the Arena bundle (SPEC §17). The bundle reuses short names
# (State, Consistent, step, iterate, mode, energy, window_step, window_all_steps, ...) in distinct namespaces,
# so a refutation opens only the namespace of the mutated file. The one exception is EMAFiniteSum, which opens two
# (CausalEMATracking for `budget`, and EMAFiniteSum); those two share no names, and the arena test pins this.
FILE_OPENS = {"ReachableQueue.lean": "open AIEFGate.ReachableQueue\n",
              "QueueComposition.lean": "open AIEFGate.QueueComposition\n",
              "MatrixPhaseBridge.lean": "open AIEFGate.MatrixPhaseBridge\n",
              "EmaNearUnit.lean": "open AIEFGate.EmaNearUnit\n",
              "EmaWrapInvariant.lean": "open AIEFGate.EmaWrapInvariant\n",
              "CausalEMATracking.lean": "open AIEFGate.CausalEMATracking\n",
              "EMAFiniteSum.lean": "open AIEFGate.CausalEMATracking AIEFGate.EMAFiniteSum\n",
              "TransientBridge.lean": "open AIEFGate.TransientBridge\n",
              "TransientParameter.lean": "open AIEFGate.TransientParameter\n",
              "WindowMax.lean": "open AIEFGate.WindowMax\n",
              "HeteroStepRef.lean": "open AIEFGate.HeteroStepRef\n",
              "HeteroGuard.lean": "open AIEFGate.HeteroStepRef\n",
              # H16 audit follow-up: M318's statement uses this file's short names (`l1`, `B3`, `B3'`)
              "GateContraction.lean": "open AIEFGate.GateContraction\n"}
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


def refute(msrc, src, thm, closure, term, preamble=""):
    """(refuted, why, control_ok): step (b) on the mutated statement and step (c) on the unmutated one."""
    rrc, rerrs, rout = lean(refutation_file(statement_prop(msrc, thm, closure), term, preamble))
    refuted, why = refutation_valid(rrc, rerrs, rout)
    crc, cerrs, _ = lean(refutation_file(statement_prop(src, thm, closure), term, preamble))
    return refuted, why, crc != 0 and bool(cerrs), (rerrs or rout.splitlines())


def partial_run_reason(only, n_stmt_ran, n_def_ran, n_stmt=None, n_def=None):
    """None for a full run; otherwise why the run cannot PASS. A filtered or short run (AIEF_MUT_ONLY, or fewer mutants
    executed than listed) is a debugging aid only: it may report, but it must FAIL, so an injected filter (for example
    `AIEF_MUT_ONLY: '^$'`, which selects nothing) cannot turn the CI step green while running 0 mutants."""
    n_stmt = len(MUTANTS) if n_stmt is None else n_stmt
    n_def = len(DEF_MUTANTS) if n_def is None else n_def
    if only:
        return f"AIEF_MUT_ONLY is set ({only!r}): filtered debugging run, not a PASS"
    if n_stmt_ran != n_stmt or n_def_ran != n_def:
        return f"ran {n_stmt_ran}/{n_stmt} statement and {n_def_ran}/{n_def} definition mutants: incomplete run, not a PASS"
    if n_stmt == 0 or n_def == 0:
        return "empty mutant list: not a PASS"
    return None


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
    only = os.environ.get("AIEF_MUT_ONLY")   # debugging aid: regex on mutant names; a filtered run always FAILS (partial_run_reason)
    n_stmt_ran = 0
    n_def_ran = 0
    for name, f, thm, edits, closure, term, eterm in MUTANTS:
        if only and not re.search(only, name):
            continue
        n_stmt_ran += 1
        src = srcs[f]
        msrc = mutate(src, thm, edits)
        assert msrc != src
        rc, errs, out = lean(msrc)
        kind = classify(errs, out)
        build_rej = build_rejected(rc, errs, kind)
        refuted, why, control_ok, rmsg = refute(msrc, src, thm, closure, term, FILE_OPENS.get(f, ""))
        rejected = build_rej and refuted and control_ok
        line = (f"{name}: build {'REJECTED' if build_rej else 'NOT REJECTED (BAD)'} [{kind}]; "
                f"refuted by proof: {'YES' if refuted else 'NO (BAD)'} [{why}]; "
                f"same term on unmutated statement fails (term-specificity only): {'YES' if control_ok else 'NO (BAD)'}")
        emsg = []
        if eterm is not None:
            erefuted, ewhy, econtrol, emsg = refute(msrc, src, thm, closure, eterm, FILE_OPENS.get(f, ""))
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
        refuted, why, control_ok, _ = refute(msrc, src, thm, closure, term, FILE_OPENS.get(f, ""))
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
        n_def_ran += 1
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
    why = partial_run_reason(only, n_stmt_ran, n_def_ran)
    if why:
        print("PARTIAL RUN: " + why)
        ok = False
    print("RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
