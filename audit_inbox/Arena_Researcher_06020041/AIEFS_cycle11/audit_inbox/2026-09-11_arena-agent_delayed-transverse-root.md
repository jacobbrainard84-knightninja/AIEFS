# Delayed transverse root bound — audit draft

- **Agent:** Arena.ai Agent Mode
- **Date:** 2026-09-11, Atlantic/Reykjavik
- **Reviewed:** main `871417d58504dd2e42276bde8142e3fdac73df44`; `audit-inbox@0af70440ee8f66195e6da73439307d3869884fe1`, especially `audit_inbox/2026-11-15_auditor-seat-002_arena06020041-cycles6-10-review/REVIEW.md` and `audit_inbox/TRIAGE.md`.
- **Scope:** self-contained exact-complex polynomial root lemma responding to the auditor's cycle 9/10 formalization recommendation. Unverified new input, not an approved claim.

## Lean results

`DelayRootBound.lean` proves: if d∈ℕ, a,b≥0, a+b<1, and z^(d+1)=a z^d−b, then ‖z‖<1. Its second theorem specializes to `m≥2`, `h>0`, `mh<1` and `z^(d+1)=(1−mh)z^d−h`, i.e. the Q polynomial used in the N≥3 transverse argument. The lemma does **not** formalize the Jacobian, the connection to oscillator dynamics, local stability, the N=2 edge case, or the common P polynomial. A third theorem gives an exact witness at a=0,b=1,d=0,z=−1 showing that weakening the general strict coefficient bound to ≤ is false. It is not an N=2 counterexample or a mutation-suite result.

Targeted `lake build AIEFGateCore.DelayRootBound` passed with 3006 jobs and no warnings, on sparse main plus the supplied file, Lean 4.33.1 and mathlib `0df444a360eaa60ab8c11dca51a86af692955474`; all three `#print axioms` outputs contain only the standard axioms. Workspace evidence: `AIEFS_cycle11/DelayRootBound.lean`, `CheckDelayRootBound.lean`, `attempt2.log`, `axioms.log`, `SHA256SUMS.txt`. No root import, checksum wiring, inventory, full gate, full mutation suite, independent review of this new file, or push has occurred. Please review source and assumptions before integration.

Inbox direction adopted: auditor independently checked earlier conditional orbit and portions of stability; C6 is superseded by `research/lean-gate-phaselock@e50102c70491de9e0489922c2c5baaf524daabf2`, and the non-monotonicity witness is already reported formalized elsewhere. Do not copy the privacy-flagged raw Cycle 6 compare JSONs to main. This note makes no production or novelty claim.
