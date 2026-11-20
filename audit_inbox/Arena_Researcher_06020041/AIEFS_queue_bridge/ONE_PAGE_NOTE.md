# Conditional engine/reference bridge: queue and circular phases

**Status:** source-based exact-real argument, supported by three finite float64 checks; not Lean-formalized or independently reviewed. This addresses the queue/modulo correspondence gap without extending the held adaptive-weight or stability work. It does not establish the derivative of the full engine.

## Claim to review

Fix N≥2, d≥1, homogeneous fixed ω, and a successful engine step with a queue of length d+1. Interpret phases on the circle `T=ℝ/(2πℤ)`. Suppose, at the **start** of the step, `theta` and the newest history vector represent the same point of T at every node. Suppose also that the engine's actual **post-weight-update** matrix for this step has every off-diagonal entry equal to a common b≥0 and diagonal zero. Then its phase and retained history output on T agree exactly with the one-step output of the unwrapped fixed-weight reference `phaseStep`, with `clippedWeight b=b`, after projection onto T.

The condition on the post-update weights is a hypothesis about the step's result, not a claim that weights are fixed as the input varies. It does not require us to assume which earlier clipping, shuffle or projection branch produced that matrix. In particular, this conditional pointwise equality **cannot be differentiated as an engine identity** unless its hypotheses are shown to hold along the perturbation family, or the contribution from changing weights is separately controlled. The earlier reference derivative is therefore still not a proof of the full engine derivative.

## Argument from the source

The engine reads `history[0]` as delayed ([lines 729–740](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/d2a62b7f9e6456ade8591d5f12c9ccdeed185d19/aief_experiment_engine_v1.py#L729-L740)); after weight processing it uses the new `state.B` and the same `history[0]` in the sine coupling and takes phase modulo 2π ([lines 822–839](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/d2a62b7f9e6456ade8591d5f12c9ccdeed185d19/aief_experiment_engine_v1.py#L822-L839)). For any real lifts x₀=theta and x_d=history[0], uniform b gives exactly the reference head before the final modulo. Adding integer multiples of 2π independently to any input lift changes the sine by zero and changes the lifted output only by the current node's integer multiple of 2π, so the circle-valued result is well-defined.

For 1≤k≤d, the reference's new history index k contains old x_(k−1). Python appends the new theta and removes the oldest entry ([lines 841–844](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/d2a62b7f9e6456ade8591d5f12c9ccdeed185d19/aief_experiment_engine_v1.py#L841-L844)). At k=1 this shifts the old **newest history**, so it agrees with old theta only by the explicit consistency hypothesis; at k≥2 the entries agree by indexing. The new newest history and theta agree after a successful step. Because the comparison is on T, no discontinuity of the numeric `[0,2π)` representative is claimed to be a discontinuity of the circle map; a proof relating local real charts to Python's modulo still needs to handle cuts and rounding.

## Important boundary of the hypothesis

`DynamicState.validate` checks queue length, shapes and finite values, but does **not** compare theta to the newest history ([lines 613–680](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/d2a62b7f9e6456ade8591d5f12c9ccdeed185d19/aief_experiment_engine_v1.py#L613-L680)). Thus validation alone does not justify the history-shift bridge. Standard initialization does set all history entries to theta ([lines 699–713](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/d2a62b7f9e6456ade8591d5f12c9ccdeed185d19/aief_experiment_engine_v1.py#L699-L713)); successful ordinary steps preserve newest-entry consistency. This is a scope observation and a counterexample for arbitrary constructed states, not a claim that standard runs violate the invariant.

## Evidence

The local engine bytes matched main `d2a62b7f9e6456ade8591d5f12c9ccdeed185d19` (SHA-256 `ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede`). `check_queue_bridge.py` ran with Python/NumPy 2.3.5: (1) a consistent two-node example matched phase and history at float precision, (2) an intentionally inconsistent state passed the engine validator but its shifted-history entry differed from old theta by circular chord distance 0.958851077, and (3) changing real phase representatives by multiples of 2π gave discrepancy 1.73e−15. See `check.log`. These are finite examples only; the argument above is a source reading, not a formal proof or comprehensive test.

```sh
# With the cited engine at ../AIEFS/aief_experiment_engine_v1.py:
OPENBLAS_NUM_THREADS=1 python check_queue_bridge.py
```

No Lean build, full test gate, independent audit, push or promotion. No project files were modified. Main and inbox heads were `d2a62b7…` and `8fc0d242547a28eba9b7d3388798bcaf923ba4a1`. Next: review this conditional quotient/queue identity, then separately prove the hypotheses needed for the actual prepared orbit and its derivative; the user-visible numerical test does not close those gaps.
