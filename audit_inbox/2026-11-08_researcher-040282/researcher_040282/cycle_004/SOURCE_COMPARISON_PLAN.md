# Preregistered source-side EMA experiment — cycle 004

Written 2026-09-04 before implementing/running the experiment.
Question: does the ideal component translate the actual compute_R update,
including directed C, delay/omega input, readout order, symmetry and masking?
This is finite numerical evidence, not a float64 or closed-loop theorem.

## Actual function and independent oracle

Use the reviewed public aief_experiment_engine_v1.py at the cycle source basis,
imported read-only from a local copy; call actual compute_R without replacing it.
Keep theta, B and history fixed between calls, supplying valid controlled states
rather than claiming they were reached by the full coupled dynamics.

Independently loop over i,j in Python: phi=theta[i]-history[0][j]
-0.5*(omega[i]+omega[j])*tau; z=complex(cos(phi),sin(phi));
Cnew=alpha*C+(1-alpha)*z. Take complex absolute values pairwise, average their
magnitudes for off-diagonal returned R, and set only the reported diagonal to 0.
Use the actual binary config.alpha as the oracle's scalar parameter. The Lean
alpha/real-exp proof is not a proof of that binary parameter's strict bounds.
Compare BOTH Cnew and R, since initial-zero R alone can hide incorrect phases.
Verify in-place C array identity, exact R symmetry and zero diagonal, and that
compute_R does not change theta/B/history.

## Cases and fixed allowances

Seed: 2026090404.

1. 30 cases = N in {1,2,3,6,12}, rho in {.5,1,2}, and initial C zero/random
   disk-valued directed complex matrix. Tw=rho*the baseline exact T_window
   (not rounded). Use omega=linspace(1,2,N), independent random theta and oldest
   delayed phase; last history entry is current theta and differs from oldest.
   Run two calls in each case without advancing phases/history.
2. Three fixed-offset cases, N=2, equal omega=1, phase offsets 0,pi/2,pi,
   delayed phases congruent to theta-omega*tau. C0=0, tune Tw=dt/log(2), and
   run 64 calls. Compare R after call m to 1-alpha^m; all offsets have unit
   input norm, irrespective of their cosine. No physical phase-locking claim.
3. Two valid floating-parameter extreme cases, Tw=1e30 and 1e-30 with the other
   config values moderate and positive. Observe whether binary alpha is 1/0.
   This documents the exact-real/float hypothesis boundary, not a source bug.

Total: 35 cases (normal 60 calls, fixed-offset 192 calls, extreme two calls).
Construct ModelConfig from the actual default config via dataclasses.replace,
set N/omega/Tw explicitly, and call validate. All initial complex norms<=1.

Before observing results set absolute tolerance 2e-14, relative zero, for maximum
complex-norm error in C and maximum absolute error in R. The same 2e-14 is a
finite slack for disk/R bounds in this bounded experiment. Real input angles
are moderate; repeated offset tests use alpha near .5, not nearly undamped
long-horizon accumulation. This allowance is roughly 90 binary64 machine eps
and small compared with the expected wrong-model separations. It is not a
proved rounding budget and will not be enlarged after seeing an error.

## Sensitivity controls

On the preregistered N=3,rho=1,random-C case, compare the correct loop output with
six deliberately wrong translations: history[-1] instead of history[0]; omit
omega*tau correction; interchange alpha and 1-alpha coefficients; report R
before updating C; take magnitude after averaging complex directions; zero the
complex accumulator diagonal. For each require at least 1e-8 maximum separation
in C or R, while the correct implementation passes the fixed allowance. Do not
count inability to load/configure the source as successful sensitivity.

## Evidence boundary

No phase or delay evolution is replaced inside compute_R. The test controls the
state vectors and holds them fixed; it does not run advance_state or produce a
coupled trajectory. All comparisons are finite and component-local. In particular,
identical prescribed inputs do not imply two coupled runs have identical inputs.
Keep initial-memory decay separate from source-forced directed differences.

## Recorded protocol correction after initial validation attempt

The initial run reached the tiny-Tw case and `ModelConfig.validate` rejected
binary alpha=0 with its existing `(0,1]` check (engine line 228). The preregistered
claim that both floating extremes were valid configurations was wrong. This is
our protocol-assumption correction, not a source defect or mathematical success.
The failed-run traceback is preserved in source_comparison_initial.log.

Keep the same designed states, source, six sensitivity controls, and unchanged
2e-14 allowance. Treat Tw=1e-30 as one EXPECTED CONFIGURATION REJECTION control;
do not execute compute_R or count a numerical comparison there. Expected actual
comparisons: 34 cases, 253 compute_R calls, plus that separately reported rejected
configuration (35 original case outcomes accounted for). Tw=1e30/alpha=1 remains
a valid endpoint observation. No case was substituted to obtain a comparison
pass; no tolerance or error test was relaxed.
