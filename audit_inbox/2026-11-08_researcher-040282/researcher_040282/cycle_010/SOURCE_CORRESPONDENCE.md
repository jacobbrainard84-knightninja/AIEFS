# 010 source correspondence, not a Python/Lean FFI proof

Frozen engine `aief_experiment_engine_v1.py`, read-only acquisition in
`source_state/main/`. Identifiers in the manifest are reproduction metadata,
not a finding about labels/copies. No source repair is proposed.

| Source location | Executable behavior | Abstract / independent-spec role |
|---|---|---|
| ModelConfig.delay_steps 172–174; validation 176–237 | D=round(tau/dt), positive dt/tau and exact D*dt=tau | Tested source D>=1. Abstract theorem also permits D=0; that is not a source-valid configuration. |
| DynamicState 584–600 | Copies theta, B, complex C and every history array | Value-buffer abstraction needs independent storage; separately exercised by ownership/mutation tests. |
| state.validate 624–679 | Exactly D+1 entries, shapes/finite/symmetric nonnegative B | Does not require last==theta, constant startup, or trajectory reconstruction; validation alone does NOT imply the lag theorem. |
| initialize_state 686–718, especially 709–710 | D+1 independent copies of current initial theta | H(0)[i]=x(0); one actual synthetic initializer probe per interpreter. |
| compute_R 721–752, especially 733–734 | Reads history[0] before any append | At reachable step n this is x(max(0,n-D)). |
| compute_R 739–744 | Current-minus-delayed, subtract mean-frequency*tau | Scalar cmath phasor; omega_i alone is a falsified wrong model. |
| compute_R 746–752 | Mutates directed C by EMA, then abs, then symmetry/diagonal | Reference computed before advance; never pre-call this mutating helper. |
| advance_state 773–790 | Updated R_driver, then B update, clip, symmetrize, zero diagonal | Scalar specification includes whole non-shuffled order; R_driver=R_physical. |
| advance_state 795–815 | Gate only when g_min_pre < delta; scale row endpoints using epsilon | Strict equality boundary tested. Not an unconditional gate. projection_active uses norm threshold1e-14. |
| advance_state 823–837 | Store gated B, check gap, use NEW B for delayed-current sine | Old/unprojected B and reversed-sine models numerically separated. |
| advance_state 838–849 | Modulo2pi then append theta.copy(), pop oldest if too long | shiftAppend D H(n) x(n+1); alias/append-old controls separated. |

Line ranges intentionally include adjacent comments; the acquired complete file is
available and unchanged. Neither matrix magnitudes, trigonometry, floating-point
rounding nor Python allocation semantics are implemented/proved in the Lean module.
`HistoryBuffer.lean` proves generic value/history indexing; `step_contract.py`
specifies the finite scalar map; `check_engine.py` probes actual imported source.
These are three distinct evidence layers, not a full equivalence theorem.

## Reachability and startup

Let x(n) be the phase value after n advances, before advance n+1. Constant startup
H(0)=x(0) and shift/append x(n+1) imply H(n)[i]=x(n+i-D), truncated at0. Thus oldest
is x(n-D), newest x(n). For n=0,...,D the oldest remains x(0). D+1 stored snapshots
span D transitions; reading before append is essential. Arbitrary validated states
need not satisfy any particular physical/generated trace. The five N1 dyadic
microtrajectories are genuinely initialized constant and recurrently advanced;
other one-step input histories are intentionally synthetic states, not claimed
reachable trajectories of the full coupled production model.

## Comparison boundaries

Compare C real/imag components, R_physical/R_driver, clipped/gated B, theta, every
history vector, pre_violation/projection_active and g_min_pre/g_min. Fixed absolute
5e-13, relative0, explicit finiteness; exact shape/flags/counts/range/storage checks.
No certification of relative projection diagnostics, shuffle/interventions,
production loops or full baseline equivalence. Normal/-O each78 actual advances,
one initializer call, nine common methods; setup exceptions never count as controls.
