#!/usr/bin/env python3
"""Lean P1 red team, part 2: mutation check of lean/AIEFGateCore/AIEFGateCore/GateMap.lean.

Each mutant drops a hypothesis or changes a constant in a main theorem STATEMENT and keeps the original proof. The
mutant is written to a temporary file outside the project and elaborated with `lake env lean`; it must FAIL (the
proof no longer goes through). The unmutated file must elaborate cleanly (positive control). Exit 0 iff the control
passes and every mutant fails.

What rejects each mutant, stated exactly:
  * M1 (drop hker), M2 (drop hc1), M3 (drop hclip): inside THIS script they are rejected only by name reference --
    the kept proof mentions the dropped hypothesis ("Unknown identifier"), a syntactic failure that is weak evidence
    on its own. Each of these mutated statements is, separately, REFUTED by a negation theorem in RedTeam.lean
    (`¬ ∀ ...` of the main theorem on K3 with exactly that hypothesis dropped, every other hypothesis holding):
      M1 -> false_drop_ker,  M2 -> false_drop_hc1,  M3 -> false_drop_clip.
    (Also there, not mutants here: false_drop_hc0 for hc0, and false_drop_hon for hon -- the latter only for a
    non-engine gate test; for engine-shaped Params, hon is implied, see GateMap.stepB_add_smul_of_branch_engine.)
  * M4 (main theorem without the (1 - γ dt) factor): rejected semantically here (unsolved goals / failed rewrite),
    and a K3 specialisation of the mutated claim (response (t s) • vRay 2) is refuted by RedTeam.false_wrong_constant.
  * M5 (multiplier formula without the (1 - γ dt) factor): rejected semantically here (unsolved goals / failed
    rewrite); there is no separate negation theorem for M5 in RedTeam.lean.

Usage: python research/lean_gate/lean_mutation_check.py   (needs elan/lake and a built Mathlib in the project)
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PROJ = REPO / "lean" / "AIEFGateCore"
SRC = PROJ / "AIEFGateCore" / "GateMap.lean"

MAIN = "theorem stepB_add_smul_of_branch"
MUTANTS = {
    "M1_drop_kernel_hypothesis": (MAIN, "    (hker : InCtrlKer G ctrl h)\n", ""),
    "M2_drop_perturbed_controller_hypothesis": (MAIN, "    (hc1 : IsCtrl p G (prop p drive (B + t • h)) ctrl) :\n    stepB p G drive (B + t • h) =",
                                                 "    :\n    stepB p G drive (B + t • h) ="),
    "M3_drop_clip_hypothesis": (MAIN, "    (hclip : ∀ e, h e ≠ 0 → 0 ≤ pre p drive B e ∧ 0 ≤ pre p drive (B + t • h) e)\n", ""),
    "M4_wrong_constant_no_gamma_dt": (MAIN, "t * (1 - p.γ * p.dt) * branchScale p G drive B ctrl e * h e := by",
                                      "t * branchScale p G drive B ctrl e * h e := by"),
    "M5_multiplier_wrong_constant": ("theorem multiplier_eq_branch_formula",
                                     "      (1 - p.γ * p.dt) * (∑ e, branchScale p G drive B ctrl e * h e ^ 2) / ∑ e, h e ^ 2 := by",
                                     "      (∑ e, branchScale p G drive B ctrl e * h e ^ 2) / ∑ e, h e ^ 2 := by"),
}


def mutate(src, anchor, old, new):
    i = src.index(anchor)
    j = src.index(old, i)          # first occurrence after the theorem's name
    nxt = src.find("\ntheorem ", i + 1)
    if 0 <= nxt < j:
        raise RuntimeError(f"mutation text for {anchor!r} is not inside that theorem")
    return src[:j] + new + src[j + len(old):]


def elaborate(text):
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "Mutant.lean"
        f.write_text(text)
        env = dict(os.environ, PATH=str(Path.home() / ".elan" / "bin") + os.pathsep + os.environ.get("PATH", ""))
        r = subprocess.run(["lake", "env", "lean", str(f)], cwd=PROJ, capture_output=True, text=True, env=env)
        errs = [l for l in (r.stdout + r.stderr).splitlines() if ": error" in l]
        return r.returncode, errs


def main():
    src = SRC.read_text()
    ok = True
    rc, errs = elaborate(src)
    print(f"CONTROL unmutated GateMap.lean: rc={rc} errors={len(errs)} -> {'PASS' if rc == 0 else 'FAIL'}")
    ok &= rc == 0
    for name, (anchor, old, new) in MUTANTS.items():
        m = mutate(src, anchor, old, new)
        assert m != src
        rc, errs = elaborate(m)
        rejected = rc != 0 and errs
        print(f"{name}: rc={rc} errors={len(errs)} -> {'REJECTED (good)' if rejected else 'ACCEPTED (BAD)'}")
        for l in errs[:2]:
            print("    " + l.split("Mutant.lean:")[-1][:160])
        ok &= bool(rejected)
    print("RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
