import AIEFProofs
import AIEFProofs.Basic
import AIEFProofs.ControllerFiber
import AIEFProofs.NegTest
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
