# Delayed polynomial boundary roots — audit draft

- **Agent:** Arena.ai Agent Mode
- **Date:** 2026-09-11, Atlantic/Reykjavik
- **Reviewed:** main `ade1179f049bca0a7de3a1152880a2c6e0a19db4`; direction from `audit-inbox@0be5a2a6241802ea4e56eab4182f51af6bc0b672`, including `audit_inbox/2026-11-15_auditor-seat-002_arena06020041-cycles6-10-review/REVIEW.md`.
- **Scope:** pure exact-complex root bounds for the Cycle 9/10 common and N=2 transverse polynomials. Unverified input, not a project claim.

## Candidate

`DelayBoundaryRoots.lean` proves, for any natural d and 0<h<1:

- If `z^(d+1)=(1−h)z^d−h`, then `‖z‖<1` (N=2 transverse case).
- If `z^(d+1)=(1−h)z^d+h`, then `‖z‖≤1`, with `‖z‖=1` only when z=1 (common mode, where h=(N−1)dt b cos(Ωτ)).

The module also proves a closed-disk helper and a complex triangle-equality helper. It does **not** prove that root 1 is simple, identify these expressions with a closed-loop Jacobian, or establish oscillator stability. The Cycle 11 module separately covers N≥3 transverse roots. No heterogeneous-frequency, projected-branch, production, or novelty conclusion is claimed.

## Evidence

Lean 4.33.1 with mathlib `0df444a360eaa60ab8c11dca51a86af692955474`: `lake build AIEFGateCore.DelayBoundaryRoots` passed, 3006 jobs and no warnings, on sparse main plus the new module. All four declarations use only standard axioms according to `#print axioms`. `CheckDelayBoundaryRoots.lean` also checks explicit h=0 and h=1 boundary witnesses. Workspace evidence: `AIEFS_cycle12/DelayBoundaryRoots.lean`, `CheckDelayBoundaryRoots.lean`, `build_final.log`, `check.log`, `SHA256SUMS.txt`. Full gate, mutation suite, repository wiring and independent review were not performed; owner review required before integration.

Main PR #39 has landed c016/P6, so the old Cycle 2 c016 patch is obsolete. No push or claim promotion was made.
