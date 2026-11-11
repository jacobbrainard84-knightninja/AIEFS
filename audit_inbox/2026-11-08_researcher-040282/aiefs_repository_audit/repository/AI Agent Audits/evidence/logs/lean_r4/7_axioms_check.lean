import AIEFProofs
import AIEFProofs.Basic
import AIEFProofs.CompleteGraphIncidence
import AIEFProofs.ControllerFiber
import AIEFProofs.ControllerFiberProjector
import AIEFProofs.ControllerFiberQuotient
import AIEFProofs.Smoke
open Lean Elab Command in
/-- For every constant defined in a project module, collect its axioms and
fail if any is outside the allowed set. Prints one line per declaration. -/
elab "#aief_axiom_audit" : command => do
  let env ← getEnv
  let allowed : List Name := [``propext, ``Classical.choice, ``Quot.sound]
  let mut bad : Array (Name × Array Name) := #[]
  let mut count : Nat := 0
  for (c, _) in env.constants.toList do
    let some idx := env.getModuleIdxFor? c | continue
    let modName := env.header.moduleNames[idx.toNat]!
    unless (`AIEFProofs).isPrefixOf modName do continue
    if c.isInternal then continue
    count := count + 1
    let axs ← liftCoreM (Lean.collectAxioms c)
    let extra := axs.filter (fun a => !allowed.contains a)
    logInfo m!"AXIOMS {c} [{modName}]: {axs.toList}"
    unless extra.isEmpty do bad := bad.push (c, extra)
  logInfo m!"AUDITED {count} project declarations"
  unless bad.isEmpty do
    throwError m!"DISALLOWED AXIOMS: {bad.toList}"

#aief_axiom_audit
#print axioms AIEFProofs.CompleteGraphIncidence.finrank_ker_of_right_inverse
#print axioms AIEFProofs.CompleteGraphIncidence.complete3
#print axioms AIEFProofs.CompleteGraphIncidence.complete4
#print axioms AIEFProofs.CompleteGraphIncidence.complete5
#print axioms AIEFProofs.CompleteGraphIncidence.complete6
#print axioms AIEFProofs.CompleteGraphIncidence.rinv3
#print axioms AIEFProofs.CompleteGraphIncidence.rinv4
#print axioms AIEFProofs.CompleteGraphIncidence.rinv5
#print axioms AIEFProofs.CompleteGraphIncidence.rinv6
#print axioms AIEFProofs.CompleteGraphIncidence.finrank_ker_K3
#print axioms AIEFProofs.CompleteGraphIncidence.finrank_ker_K4
#print axioms AIEFProofs.CompleteGraphIncidence.finrank_ker_K5
#print axioms AIEFProofs.CompleteGraphIncidence.finrank_ker_K6
#print axioms AIEFProofs.CompleteGraphIncidence.ker_K3_eq_bot
#print axioms AIEFProofs.CompleteGraphIncidence.inc_vRay_self
#print axioms AIEFProofs.CompleteGraphIncidence.inc_vRay_other
#print axioms AIEFProofs.CompleteGraphIncidence.inc_neg_vRay_self
#print axioms AIEFProofs.CompleteGraphIncidence.vRay_not_mem_ker
#print axioms AIEFProofs.CompleteGraphIncidence.inc3_rows_eq_CCtrl
#print axioms AIEFProofs.CompleteGraphIncidence.vRay_two_eq_vCtrl
#print axioms AIEFProofs.ControllerFiber.CCtrl_00
#print axioms AIEFProofs.ControllerFiber.CCtrl_01
#print axioms AIEFProofs.ControllerFiber.CCtrl_02
#print axioms AIEFProofs.ControllerFiber.CCtrl_10
#print axioms AIEFProofs.ControllerFiber.CCtrl_11
#print axioms AIEFProofs.ControllerFiber.CCtrl_12
#print axioms AIEFProofs.ControllerFiber.vCtrl_zero
#print axioms AIEFProofs.ControllerFiber.vCtrl_one
#print axioms AIEFProofs.ControllerFiber.vCtrl_two
#print axioms AIEFProofs.ControllerFiber.univ_fin3
#print axioms AIEFProofs.ControllerFiber.sum_fin3
#print axioms AIEFProofs.ControllerFiber.CCtrl_mulVec_apply_zero
#print axioms AIEFProofs.ControllerFiber.CCtrl_mulVec_apply_one
#print axioms AIEFProofs.ControllerFiber.CCtrl_mulVec_vCtrl
#print axioms AIEFProofs.ControllerFiber.CCtrl_mulVec_eq_zero_iff
#print axioms AIEFProofs.ControllerFiber.CCtrl_coords_iff
#print axioms AIEFProofs.ControllerFiber.CCtrl_eq_zero_iff_locked_ratio
#print axioms AIEFProofs.ControllerFiber.CCtrl_mulVec_eq_zero_iff_exists_smul
#print axioms AIEFProofs.ControllerFiber.vCtrl_ne_zero
#print axioms AIEFProofs.ControllerFiber.PPar_apply
#print axioms AIEFProofs.ControllerFiber.PPar_apply_comm
#print axioms AIEFProofs.ControllerFiber.vCtrl_dot_vCtrl
#print axioms AIEFProofs.ControllerFiber.vCtrl_dot_smul
#print axioms AIEFProofs.ControllerFiber.PPar_mulVec
#print axioms AIEFProofs.ControllerFiber.PPar_mulVec_vCtrl
#print axioms AIEFProofs.ControllerFiber.PPerp_mulVec
#print axioms AIEFProofs.ControllerFiber.PPar_symmetric
#print axioms AIEFProofs.ControllerFiber.PPerp_symmetric
#print axioms AIEFProofs.ControllerFiber.PPar_selfAdjoint
#print axioms AIEFProofs.ControllerFiber.PPar_sq_mulVec
#print axioms AIEFProofs.ControllerFiber.PPar_mulVec_PPerp
#print axioms AIEFProofs.ControllerFiber.PPerp_mulVec_PPar
#print axioms AIEFProofs.ControllerFiber.PPerp_sq_mulVec
#print axioms AIEFProofs.ControllerFiber.PPar_dot_PPerp
#print axioms AIEFProofs.ControllerFiber.CCtrl_mulVec_PPar
#print axioms AIEFProofs.ControllerFiber.CCtrl_mulVec_sub
#print axioms AIEFProofs.ControllerFiber.CCtrl_mulVec_PPerp
#print axioms AIEFProofs.ControllerFiber.range_PPar_iff_ker_CCtrl
#print axioms AIEFProofs.ControllerFiber.id_eq_PPar_add_PPerp
#print axioms AIEFProofs.ControllerFiber.im_PPar_inter_im_PPerp
#print axioms AIEFProofs.ControllerFiber.CCtrl_mulVec_SPerp
#print axioms AIEFProofs.ControllerFiber.PPerp_eq_SPerp_CCtrl
#print axioms AIEFProofs.ControllerFiber.PPerp_mulVec_sub
#print axioms AIEFProofs.ControllerFiber.CCtrl_eq_iff_exists_smul
#print axioms AIEFProofs.ControllerFiber.CCtrl_eq_iff_PPerp_eq
#print axioms AIEFProofs.ControllerFiber.PPerp_eq_iff_PPar_sub
#print axioms AIEFProofs.ControllerFiber.controller_fiber_tfae
