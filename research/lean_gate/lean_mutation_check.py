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
]

# Classifier negative control (P3 rule change, see (a) above): the P2 deletion form of M1 fails to build with
# name-reference errors only; it must be classified as such and must NOT count as a build rejection.
LEGACY_NAME_ONLY = ("M1_legacy_delete_kernel_hypothesis", "GateMap.lean", "stepB_add_smul_of_branch",
                    [("    (hker : InCtrlKer G ctrl h)\n", "", 1)])

OPENS = ("open Finset\nopen AIEFGate.MatrixForm (CE KG toEdge stepM)\n"
         "open AIEFGate.EngineWitness (pE driveE BE sE driveW BW)\nopen AIEFGate.RedTeam (hw ctrlX)\n"
         "open AIEFGate.Bridge (toR CtrlJ01)\nopen AIEFGate.ControllerFiber (vCtrl)\n"
         "open AIEFGate.Capacity (rowS kernelM gateM appliedFactor)\n")
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


def refute(msrc, src, thm, closure, term):
    """(refuted, why, control_ok): step (b) on the mutated statement and step (c) on the unmutated one."""
    rrc, rerrs, rout = lean(refutation_file(statement_prop(msrc, thm, closure), term))
    refuted, why = refutation_valid(rrc, rerrs, rout)
    crc, cerrs, _ = lean(refutation_file(statement_prop(src, thm, closure), term))
    return refuted, why, crc != 0 and bool(cerrs), (rerrs or rout.splitlines())


def main():
    ok = True
    srcs = {}
    for f in sorted({m[1] for m in MUTANTS}):
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
    for name, f, thm, edits, closure, term, eterm in MUTANTS:
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
        print(f"{line} -> {'REJECTED (good)' if rejected else 'NOT REJECTED (BAD)'}")
        for l in errs[:1]:
            print("    build: " + l.split("Mutant.lean:")[-1][:150])
        if not refuted:
            for l in rmsg[:3]:
                print("    refutation: " + l.split("Mutant.lean:")[-1][:200])
        for l in emsg[:3]:
            print("    engine refutation: " + l.split("Mutant.lean:")[-1][:200])
        ok &= rejected
    print(f"mutants rejected: {n_rej}/{len(MUTANTS)}")
    print("RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
