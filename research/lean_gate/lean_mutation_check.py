#!/usr/bin/env python3
"""Lean P1/P2 red team, part 2: mutation check of lean/AIEFGateCore.

Each mutant changes a theorem STATEMENT (drops a hypothesis, shrinks an edge set, or drops a constant) in a copy of
its source file and keeps the original proof. A mutant counts as REJECTED only if BOTH hold:

  (a) build rejection: the mutated file, written to a temporary directory outside the project and elaborated with
      `lake env lean`, fails (the kept proof no longer goes through). The script reports whether the errors are
      only name references ("Unknown identifier": weak, syntactic) or a real proof failure (type mismatch,
      unsolved goals, failed rewrite, ...);
  (b) semantic rejection (P2): the mutated statement itself is REFUTED by a proved negation theorem. The script
      extracts the mutated statement from the mutated file, closes it over its section variables, and elaborates
          example : ¬ (∀ <section variables> <binders>, <conclusion>) := fun H => <negation theorem> (H <instance>)
      against the built project (`import AIEFGateCore`). This is a real Lean proof that the mutant is false, not a
      name reference. As a positive control, the same refutation applied to the UNMUTATED statement must FAIL to
      elaborate (a true theorem cannot be refuted, so a refutation that also "refutes" the original would be
      meaningless).

The unmutated files must elaborate cleanly (positive control). Exit 0 iff every control passes and every mutant is
rejected in both senses. Requires a built project (`lake build` in lean/AIEFGateCore) for step (b).

Mutants (statement -> negation theorem used in step (b)):
  M1 stepB_add_smul_of_branch without hker            -> RedTeam.false_drop_ker
  M2 stepB_add_smul_of_branch without hc1             -> RedTeam.false_drop_hc1
  M3 stepB_add_smul_of_branch without hclip           -> RedTeam.false_drop_clip
  M4 stepB_add_smul_of_branch without (1 - γ dt)      -> RedTeam.false_main_no_gamma
  M5 multiplier_eq_branch_formula without (1 - γ dt)  -> RedTeam.false_multiplier_no_gamma
  M6 stepB_add_smul_of_branch_on, edge set x_e ≠ 0    -> RedTeam.false_rel_x_only
  M7 stepB_add_smul_of_branch_on, edge set h_e ≠ 0    -> RedTeam.false_rel_h_only
  M8 MatrixForm.stepM_eq_stepB without symmetry       -> MatrixForm.false_matrix_no_symm
  M9 EngineWitness.engine_nonvacuous without (1-γdt)  -> EngineWitness.engine_false_no_gamma

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

MUTANTS = [
    # name, file, theorem, [(old, new, count)], closure vars, refutation term
    ("M1_drop_kernel_hypothesis", "GateMap.lean", "stepB_add_smul_of_branch",
     [("    (hker : InCtrlKer G ctrl h)\n", "", 1)], GATE_VARS, f"RedTeam.false_drop_ker ({GATE_INST})"),
    ("M2_drop_perturbed_controller_hypothesis", "GateMap.lean", "stepB_add_smul_of_branch",
     [("    (hc1 : IsCtrl p G (prop p drive (B + t • h)) ctrl) :\n", "    :\n", 1)], GATE_VARS,
     f"RedTeam.false_drop_hc1 ({GATE_INST})"),
    ("M3_drop_clip_hypothesis", "GateMap.lean", "stepB_add_smul_of_branch", [(pL, "", 1)], GATE_VARS,
     f"RedTeam.false_drop_clip ({GATE_INST})"),
    ("M4_wrong_constant_no_gamma_dt", "GateMap.lean", "stepB_add_smul_of_branch",
     [("t * (1 - p.γ * p.dt) * branchScale p G drive B ctrl e * h e", "t * branchScale p G drive B ctrl e * h e", 1)],
     GATE_VARS, f"RedTeam.false_main_no_gamma ({GATE_INST})"),
    ("M5_multiplier_wrong_constant", "GateMap.lean", "multiplier_eq_branch_formula",
     [("      (1 - p.γ * p.dt) * (∑ e, branchScale p G drive B ctrl e * h e ^ 2) / ∑ e, h e ^ 2",
       "      (∑ e, branchScale p G drive B ctrl e * h e ^ 2) / ∑ e, h e ^ 2", 1)],
     GATE_VARS, f"RedTeam.false_multiplier_no_gamma ({GATE_INST})"),
    ("M6_edge_set_x_only", "GateMap.lean", "stepB_add_smul_of_branch_on",
     [(REL, "(fun e => prop p drive B e ≠ 0)", 3)], GATE_VARS, f"RedTeam.false_rel_x_only ({GATE_INST})"),
    ("M7_edge_set_h_only", "GateMap.lean", "stepB_add_smul_of_branch_on",
     [(REL, "(fun e => h e ≠ 0)", 3)], GATE_VARS, f"RedTeam.false_rel_h_only ({GATE_INST})"),
    ("M8_matrix_drop_symmetry", "MatrixForm.lean", "stepM_eq_stepB",
     [("(hD : ∀ i j, D i j = D j i)\n    (hB : ∀ i j, Bm i j = Bm j i) ", "", 1)],
     "{V : Type} [Fintype V] [LinearOrder V] (p : Params)",
     "MatrixForm.false_matrix_no_symm (@H (Fin 2) _ _ MatrixForm.pT)"),
    ("M9_engine_witness_no_gamma_dt", "EngineWitness.lean", "engine_nonvacuous",
     [("((1 / 10) * (1 - 15 / 1000 * (1 / 100)) * sE) • vRay 2", "((1 / 10) * sE) • vRay 2", 1)],
     "", "EngineWitness.engine_false_no_gamma H.2.2.2.2.2.2.2.2.2"),
]

OPENS = "open Finset\nopen AIEFGate.MatrixForm (CE KG toEdge stepM)\nopen AIEFGate.EngineWitness (pE driveE BE sE)\n"


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


def refutation_file(prop, term):
    return ("import AIEFGateCore\n\nset_option autoImplicit false\n\nnamespace AIEFGate\n" + OPENS +
            f"\nexample : ¬ {prop} := fun H => {term}\n\nend AIEFGate\n")


def classify(errs, out):
    if not errs:
        return "none"
    name_only = all(("nknown identifier" in l) or ("unknown constant" in l) for l in errs)
    return "NAME-REFERENCE ONLY (weak)" if name_only else "REAL PROOF FAILURE"


def main():
    ok = True
    srcs = {}
    for f in sorted({m[1] for m in MUTANTS}):
        srcs[f] = (SRCDIR / f).read_text()
        rc, errs, _ = lean(srcs[f])
        good = rc == 0 and not errs
        print(f"CONTROL unmutated {f}: rc={rc} errors={len(errs)} -> {'PASS' if good else 'FAIL'}")
        ok &= good
    n_rej = 0
    for name, f, thm, edits, closure, term in MUTANTS:
        src = srcs[f]
        msrc = mutate(src, thm, edits)
        assert msrc != src
        rc, errs, out = lean(msrc)
        build_rej = rc != 0 and bool(errs)
        kind = classify(errs, out)
        # (b) semantic: refute the mutated statement; control: the same refutation of the original must fail
        rrc, rerrs, rout = lean(refutation_file(statement_prop(msrc, thm, closure), term))
        refuted = rrc == 0 and not rerrs
        crc, cerrs, _ = lean(refutation_file(statement_prop(src, thm, closure), term))
        control_ok = crc != 0 and bool(cerrs)
        rejected = build_rej and refuted and control_ok
        n_rej += rejected
        print(f"{name}: build {'REJECTED' if build_rej else 'ACCEPTED (BAD)'} [{kind}]; "
              f"refuted by proof: {'YES' if refuted else 'NO (BAD)'}; "
              f"refutation of unmutated statement fails: {'YES' if control_ok else 'NO (BAD)'} -> "
              f"{'REJECTED (good)' if rejected else 'NOT REJECTED (BAD)'}")
        for l in errs[:1]:
            print("    build: " + l.split("Mutant.lean:")[-1][:150])
        if not refuted:
            for l in (rerrs or rout.splitlines())[:3]:
                print("    refutation: " + l.split("Mutant.lean:")[-1][:200])
        ok &= rejected
    print(f"mutants rejected: {n_rej}/{len(MUTANTS)}")
    print("RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
