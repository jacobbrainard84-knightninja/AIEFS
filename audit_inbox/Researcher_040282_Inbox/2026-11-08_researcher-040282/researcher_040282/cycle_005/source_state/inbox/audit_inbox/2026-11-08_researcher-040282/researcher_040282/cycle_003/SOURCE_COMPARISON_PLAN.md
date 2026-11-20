# Optional controlled-drive source comparison — preregistered before execution

Cycle 003, Researcher 040282, 2026-11-07 (Atlantic/Reykjavik).

Purpose: finite one-step numerical check of the new adaptive proposal/gate
translation with nonzero eta, mu and gamma. Not a coupled EMA/delay trajectory
or a float64 correctness theorem. This supplements, not replaces, Lean proofs.

Read-only source: source_state/main/aief_experiment_engine_v1.py at the cycle's
recorded main commit. Load it normally, initialize valid 12-node state/config,
then replace only its in-process compute_R function by a fixed symmetric,
zero-diagonal matrix for that call. Restore it afterward. Compare only updated
B; do not claim the replacement evolves a physical coherence accumulator.

Fixed 24 cases, default configuration:
- 4 active cases: k=3,4,6,12 cliques, B_ij=c/(k-1) within the clique and zero
  elsewhere, R_ij=1 inside and 0 outside (off diagonal).
- 4 inactive dense cases: B_ij=c/(4*11), R_ij=0,3/7,1/2,1 respectively.
- 16 inactive dense random cases: seed 2026110703; B_ij=c/(2*11)*m/16,
  R_ij=k/16 for independently drawn m,k in {0,...,16}, symmetric off diagonal.

Separate exact Fraction oracle: embed the actual binary floating inputs and
config values as exact rationals; form the affine update entrywise, clip, mask
diagonal, and apply the guarded min-endpoint capacity rule using explicit loops.
For these symmetric inputs the exact symmetrization is the identity. Check
that exact gap and capacity guards agree and have gap-boundary distance >1e-8;
that safety margin is fixed before testing. Expected branches are 4 active and
20 inactive. Do not discard failing cases or loosen the boundary screen.

Acceptance: entrywise absolute error <=5e-15, zero relative tolerance, matching
the earlier isolated source allowance. This is a deliberately explicit finite
comparison allowance, not a universal rounding budget. All 24 cases must pass;
missing dependencies or an API/branch mismatch must be reported as a blocker,
not a successful test. Preserve structured results, maximum error, case labels,
actual branch counts and actual elapsed time. No production NPZ data required.
