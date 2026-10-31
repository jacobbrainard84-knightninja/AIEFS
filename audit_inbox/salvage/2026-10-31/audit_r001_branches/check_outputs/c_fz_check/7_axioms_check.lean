import AIEFFreezeCore
import AIEFFreezeCore.FreezeCore
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
    unless (`AIEFFreezeCore).isPrefixOf modName do continue
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
#print axioms AIEFFreeze.upper_geom
#print axioms AIEFFreeze.eventually_off
#print axioms AIEFFreeze.eventually_on
#print axioms AIEFFreeze.edge_eventually_off
#print axioms AIEFFreeze.edge_eventually_on
