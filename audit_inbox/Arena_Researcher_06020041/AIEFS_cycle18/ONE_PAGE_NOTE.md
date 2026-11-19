# Cycle 18 — explicit neutral-phase projection with adaptive coupling

**Status:** analytical candidate plus engine finite-difference checks; not Lean-formalized or independently reviewed. This extends Cycles 10 and 17 from the proposed phase-only block to the **linearized full interior model**, conditional on Cycle 10's Jacobian identification. It gives the neutral shift, not a generic convergence or production claim.

## Result

Consider the prepared homogeneous-frequency interior orbit of Cycle 8, N≥2, d≥1, no shuffle, strict branch slack and positive b=η/γ. Use its co-rotating linearization from Cycle 10. Let `h=dt b cos(Ωτ)`, `q=(N−1)h`, `D=1+dq`, `ρ=1−dt γ`, `κ=dt(η+μ)`, `s=sin(Ωτ)`. Assume `0<q<1`, `0<α<1`, `0<ρ<1` and the other smooth interior assumptions in Cycle 10.

For phase-history perturbations `x_k(i)` (k=0 current, k=d delayed), normalized complex-EMA perturbations `u_ij+i v_ij` relative to the orbit's complex accumulator, and symmetric zero-diagonal weight perturbations `w_ij`, define

- `X_k = (1/N) ∑ᵢ x_k(i)`;
- `U = (1/N) ∑ᵢ≠ⱼ u_ij`, and `W = (1/N) ∑ᵢ≠ⱼ w_ij` (off-diagonal **row-sum averages**, not edge averages).

Then the proposed full-Jacobian left neutral functional is

`L = [X₀ + q∑_{k=1}^d X_k − dt s {ρ W/(1−ρ) + κ α U/[(1−ρ)(1−α)]}]/D`.

It is normalized to 1 on a uniform unit phase shift, zero on imaginary EMA perturbations, and satisfies `L J = L` for the interior Jacobian. In the linearized system, any initial perturbation therefore has limiting neutral phase `L` at every node and history slot, while real/imaginary EMA and weight perturbations vanish. This uses Cycle 17's phase-block spectrum and the triangular structure of Cycle 10, with α and ρ strictly inside the disk; it is not a statement that the nonlinear final phase equals this linear formula.

## Derivation

The Cycle 10 equations give `U⁺=αU`, `W⁺=ρW+κ α U` and `X⁺₀=(1−q)X₀+qX_d−dt s W⁺`, with the usual history shifts. Thus `A=X₀+q∑_{k=1}^d X_k` obeys `A⁺−A=−dt s W⁺`. With `H=ρW/(1−ρ)+κ α U/[(1−ρ)(1−α)]`, direct substitution yields `H−H⁺=W⁺`; hence `A−dt s H` is invariant. The coefficient D normalizes the common-phase vector. Other phase and adaptive perturbations may affect transients but not this functional. The phase-only formula is recovered when U=W=0.

## Evidence, scope and reproduction

`OPENBLAS_NUM_THREADS=1 python3 /home/user/AIEFS_cycle18/check_phase_projection.py` uses the Cycle 10 actual-engine helper plus Cycle 8 helper and NumPy. For N=3, d=3 and 50, maximum residuals for `LJ−L` are 1.11e−16 and 2.71e−20 on the previously derived analytic Jacobian; independent central finite differences of the actual engine give 1.65e−11 and 7.81e−10. Mixed-state directional checks and deliberate omission of adaptive coupling pass as controls (`check.log`). Finite differences evaluate the smooth mathematical extension and can include physically inadmissible EMA or capacity perturbations; they are not a proof of behavior for feasible nonlinear trajectories. There was no full-suite or Lean run.

Local engine SHA-256 `ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede` was byte-matched to main `d2a62b7f9e6456ade8591d5f12c9ccdeed185d19`; inbox head `2e63035c1c973ff07e8124e3ca9b8e198b4e5171`. The exact-real linearization-to-engine bridge remains analytical, not formal. No projected gate, heterogeneous frequencies, shuffle, basin, nonlinear asymptotic-phase formula, independent review, push or promotion is claimed.
