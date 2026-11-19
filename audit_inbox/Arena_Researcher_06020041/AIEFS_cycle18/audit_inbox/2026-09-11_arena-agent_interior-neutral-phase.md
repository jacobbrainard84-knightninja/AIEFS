# Interior full-Jacobian neutral phase functional — audit draft

- **Agent:** Arena.ai Agent Mode
- **Date:** 2026-09-11, Atlantic/Reykjavik
- **Reference:** main `d2a62b7f9e6456ade8591d5f12c9ccdeed185d19`; inbox `2e63035c1c973ff07e8124e3ca9b8e198b4e5171`. Tested engine is byte-identical to main; its SHA-256 is `ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede`.
- **Status:** unreviewed analytical candidate with finite-difference checks, not a Lean theorem or promoted project result.

For the prepared homogeneous-frequency interior orbit and Cycle 10 full linearization, the candidate `A−dt sin(Ωτ) H` is invariant, where `A=X₀+q∑₁ᵈX_k`, `q=(N−1)dt b cos(Ωτ)`, `H=ρW/(1−ρ)+κ α U/[(1−ρ)(1−α)]`, `ρ=1−dt γ`, `κ=dt(η+μ)` and U,W are mean off-diagonal row sums of normalized real EMA and weight perturbations. Dividing by `1+dq` yields a normalized left neutral functional. Derivation, assumptions and definitions are in `AIEFS_cycle18/ONE_PAGE_NOTE.md`. Combining with the proposed Cycle 17 spectrum and Cycle 10 triangular Jacobian gives the linearized asymptotic phase shift, not a nonlinear formula.

Evidence: `check_phase_projection.py` checks both the analytical Jacobian and actual-engine central finite differences for N=3,d=3 and 50, includes mixed perturbations and a negative control omitting adaptive coupling; output in `check.log`. Finite differences can leave the physically admissible set and are not a feasible-trajectory experiment. The engine derivative identification, invariant and spectral decomposition have not been independently reviewed or composed in Lean. No projected-branch, random initialization, heterogeneous-frequency or production stability claim; no full gate, push or promotion. Suggested review: independently derive the adaptive row-sum equations and functional, then formalize the linear map and its neutral projection.
