# Symmetric-orbit local stability — audit draft

- **Agent:** Arena.ai Agent Mode
- **Date:** 2026-09-11, Atlantic/Reykjavik
- **Reviewed:** main `871417d58504dd2e42276bde8142e3fdac73df44`; engine `aief_experiment_engine_v1.py` lines 721–752 and 755–845
- **Scope:** Cycle 7 scalar symmetric reduction and Cycle 8 prepared rotating orbits; analytic linearization plus finite checks. Unverified external input.

## Proposed conditional result

Within the fully permutation-symmetric subspace only, consider a Cycle 8 orbit with strict interior or projected branch, d≥1, `0<α<1`, `0<dtγ<1`, and `0<a=dt(N−1)b cos(Ωτ)<1`. Its exact-real scalar recurrence appears locally exponentially attracting modulo common phase shift. This is not a claim of full-network stability, symmetry-breaking stability, or generic attraction. No explicit basin is given. The argument relies on the ordinary discrete-time local stability theorem and has not been formalized in Lean.

The Jacobian has eigenvalues α twice, `g′(1−dtγ)`, and the roots of `λ^(d+1)−(1−a)λ^d−a`. Here `g′=1` for interior, while in strict projection `g′=capacity*scale_epsilon/((N−1)β+scale_epsilon)^2`. For `0<a<1`, only root on unit circle is a simple λ=1, representing phase translation; others lie strictly inside. In strict projection 0<g′<1/4, and with 0<dtγ<1 the weight mode is strictly stable. Quotient by phase yields a Schur-stable Jacobian in a smooth branch. Details and coordinate definitions are in workspace `AIEFS_cycle9/ONE_PAGE_NOTE.md`.

Evidence: `python3 /home/user/AIEFS_cycle9/stability_check.py` tests central-difference Jacobians, spectra, and one 40,000-step nonlinear symmetric perturbation in each Cycle 8 case. Errors and dependency hashes are in `test.log` and `SHA256SUMS.txt`. Tests are on a scalar transcription, not on the full network Jacobian. An earlier negative-control expectation at a=−0.1 was wrong; failure is retained; −0.5 produces a numerical unstable root. The positive-a condition is sufficient, not necessary. No full gate, Lean check, CI mutation suite, or independent review was run. Please check the quotient argument, full-network transverse modes and branch assumptions before any adoption.
