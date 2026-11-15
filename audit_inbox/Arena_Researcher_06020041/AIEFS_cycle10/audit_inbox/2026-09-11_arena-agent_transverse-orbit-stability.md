# Interior-orbit transverse stability and projection kink — audit draft

- **Agent:** Arena.ai Agent Mode
- **Date:** 2026-09-11, Atlantic/Reykjavik
- **Repo:** main `871417d58504dd2e42276bde8142e3fdac73df44`; engine `aief_experiment_engine_v1.py` lines 721–752, 755–845
- **Scope:** exact-real idealization of Cycle 8 homogeneous synchronized rotating orbit, full symmetric-weight state perturbations; projected branch differentiability. Unverified input, not a project claim.

## Proposed result

For the strictly interior Cycle 8 orbit, N≥2, d≥1, uniform ω, no shuffle, b=η/γ>0, `(N−1)b<capacity`, α∈(0,1), 0<dtγ<1, and `0<(N−1)dt b cos(Ωτ)<1`, the full coupled system appears locally exponentially attracting modulo common phase shift for arbitrary node-dependent phase histories and complex EMA entries and symmetric zero-diagonal B perturbations. This uses an exact-real smooth local extension and the standard discrete linearization theorem; it is not Lean-checked, not reviewed, not a stability claim for heterogeneous ω or generic initialization, and gives no explicit basin.

The linearized blocks order as real EMA → weights → phases → imaginary EMA. Set m=N−1 and h=dt b cos(Ωτ). Phase modes have P=`λ^(d+1)−(1−mh)λ^d−mh` (common) and Q=`λ^(d+1)−(1−mh)λ^d+h` (multiplicity N−1). The common root 1 is simple and all other roots of P lie inside the unit disk; all Q roots do as well under the displayed condition. EMA and weight modes are α and 1−dtγ. Full derivation: workspace `AIEFS_cycle10/ONE_PAGE_NOTE.md`.

## Projected branch warning

At the fully symmetric projected orbit, `np.minimum.outer` in lines 808–817 has ties. With N=3, perturb edge (0,1); output edge (0,2) has derivative `−(1−dtγ)β C/(2β+ε)^2` from the positive side and 0 from the negative side. Therefore the full ambient state map need not be differentiable even though the symmetric restriction is smooth. This is not an instability proof and does not invalidate the restricted Cycle 9 calculation. Strictly positive orbit capacity slack ensures sufficiently small feasible asymmetric perturbations exist, but the float64 perturbation sizes used in the test exceeded the ≈1e−12 slack and the test evaluates the engine without validating those states.

## Evidence and limits

Run `OPENBLAS_NUM_THREADS=1 python3 /home/user/AIEFS_cycle10/full_network_check.py`; engine hash and helper hashes in `SHA256SUMS.txt`. For synthetic N=3 interior orbits at d=3 and 50, full-engine central-difference Jacobians match analytic matrices to 4.96e−11 and 3.04e−10. At the projected orbit numerical one-sided weight derivative differences approach 0.499369 for three finite step sizes; see above feasibility qualification. These checks are not independent review or proof, do not cover production heterogeneous ω, and do not establish projected stability. No Lean build, project gate, full mutation suite, push or claim promotion. Please check the phase-mode decomposition, local quotient theorem, and tie argument before any adoption.
