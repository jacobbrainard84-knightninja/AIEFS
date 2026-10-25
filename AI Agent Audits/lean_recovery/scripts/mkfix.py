import sys
src, dst, variant = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(src).read()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old)
    s = s.replace(old, new)
# F1 PPar_apply_comm (v303 only)
if variant == "v303":
    rep("""lemma PPar_apply_comm (i j : Fin 3) : PPar i j = PPar j i := by
  simp [mul_comm]
""", """lemma PPar_apply_comm (i j : Fin 3) : PPar i j = PPar j i := by
  simp only [PPar_apply]
  ring
""")
# F2 PPar_mulVec_vCtrl: simp already closes the goal
rep("""lemma PPar_mulVec_vCtrl : PPar *ᵥ vCtrl = vCtrl := by
  rw [PPar_mulVec, vCtrl_dot_vCtrl]
  funext i
  simp
  ring
""", """lemma PPar_mulVec_vCtrl : PPar *ᵥ vCtrl = vCtrl := by
  rw [PPar_mulVec, vCtrl_dot_vCtrl]
  funext i
  simp
""")
# F3 PPerp_symmetric (v303 only)
if variant == "v303":
    rep("""theorem PPerp_symmetric (i j : Fin 3) : PPerp i j = PPerp j i := by
  simp [PPerp, PPar_apply_comm i j, eq_comm]
""", """theorem PPerp_symmetric (i j : Fin 3) : PPerp i j = PPerp j i := by
  simp only [PPerp, PPar_apply_comm i j, eq_comm]
""")
# F4 PPar_sq_mulVec: normalise `(c • v) j` to `c * v j` before using hS
rep("""  funext i
  simp [Pi.smul_apply, hS]
  ring
""", """  funext i
  simp only [Pi.smul_apply, smul_eq_mul, hS]
""")
# F5 PPar_mulVec_PPerp
rep("""  rw [PPerp_mulVec, PPar_mulVec, PPar_mulVec x]
  have hdiff :""", """  rw [PPerp_mulVec, PPar_mulVec]
  have hdiff :""")
rep("""    rw [hPx, sum_fin3]
    simp [Pi.smul_apply]
    ring
  funext i
  simp [Pi.smul_apply, hdiff]
""", """    rw [hPx, sum_fin3]
    simp only [Pi.smul_apply, smul_eq_mul, sum_fin3, vCtrl_zero, vCtrl_one, vCtrl_two]
    ring
  funext i
  simp only [Pi.smul_apply, smul_eq_mul, hdiff]
  simp
""")
# F6 range_PPar_iff_ker_CCtrl
rep("""    rw [ha, PPar_mulVec, vCtrl_dot_smul]
    funext i
    simp [Pi.smul_apply]
    ring
""", """    rw [ha, PPar_mulVec]
    funext i
    simp only [Pi.smul_apply, smul_eq_mul, vCtrl_dot_smul]
    ring
""")
# F7 id_eq_PPar_add_PPerp: simp already closes the goal
rep("""  funext i
  simp [PPerp_mulVec]
  ring
""", """  funext i
  simp [PPerp_mulVec]
""")
if variant == "v191":
    # F8 PPerp_sq_mulVec used PPar_mulVec_PPerp-style reasoning before it existed:
    # move it (statement unchanged) after PPar_mulVec_PPerp, with the v303 proof.
    old = """/-- Idempotence: `P⊥² = P⊥` as an action on vectors. -/
theorem PPerp_sq_mulVec (x : Fin 3 → ℚ) :
    PPerp *ᵥ (PPerp *ᵥ x) = PPerp *ᵥ x := by
  funext i
  simp [PPerp_mulVec, PPar_sq_mulVec]

"""
    rep(old, "")
    anchor = "/-- Complementary orthogonality: `P⊥ P∥ = 0`. -/"
    rep(anchor, """/-- Idempotence: `P⊥² = P⊥` as an action on vectors. -/
theorem PPerp_sq_mulVec (x : Fin 3 → ℚ) :
    PPerp *ᵥ (PPerp *ᵥ x) = PPerp *ᵥ x := by
  rw [PPerp_mulVec (PPerp *ᵥ x), PPar_mulVec_PPerp]
  funext i
  simp

""" + anchor)
    # F9 CCtrl_mulVec_PPar: drop unused simp args (warnings only)
    rep("""    simp [Matrix.mulVec, dotProduct, sum_fin3, Pi.smul_apply,
      CCtrl_mulVec_apply_zero, CCtrl_mulVec_apply_one]
    ring
""", """    simp [Matrix.mulVec, dotProduct, sum_fin3, Pi.smul_apply]
    ring
""")
if variant == "v303":
    # F10 PPar_dot_PPerp: `simpa [hx]` loops (hx rewrites PPar*x to PPar*(PPar*x));
    # `simp [PPar_sq_mulVec]` loses to Matrix.mulVec_mulVec.
    rep("""    have hx : PPar *ᵥ x = PPar *ᵥ (PPar *ᵥ x) := (PPar_sq_mulVec x).symm
    calc
      ∑ i, (PPar *ᵥ x) i * (PPar *ᵥ y) i
          = ∑ i, (PPar *ᵥ (PPar *ᵥ x)) i * y i := by
            simpa [hx] using (PPar_selfAdjoint (PPar *ᵥ x) y).symm
      _ = ∑ i, (PPar *ᵥ x) i * y i := by
            simp [PPar_sq_mulVec]
""", """    calc
      ∑ i, (PPar *ᵥ x) i * (PPar *ᵥ y) i
          = ∑ i, (PPar *ᵥ (PPar *ᵥ x)) i * y i :=
            (PPar_selfAdjoint (PPar *ᵥ x) y).symm
      _ = ∑ i, (PPar *ᵥ x) i * y i := by
            rw [PPar_sq_mulVec]
""")
    # F11 CCtrl_mulVec_PPar: drop unused simp args and unreachable `ring` (warnings only)
    rep("""    fin_cases i <;>
      simp [Matrix.mulVec, dotProduct, sum_fin3, Pi.smul_apply,
        CCtrl_mulVec_apply_zero, CCtrl_mulVec_apply_one] <;>
      ring
""", """    fin_cases i <;>
      simp [Matrix.mulVec, dotProduct, sum_fin3, Pi.smul_apply]
""")
open(dst, "w").write(s)
