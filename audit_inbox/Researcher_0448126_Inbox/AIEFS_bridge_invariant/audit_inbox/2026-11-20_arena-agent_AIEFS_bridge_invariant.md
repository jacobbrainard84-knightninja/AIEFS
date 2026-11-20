# AIEFS_bridge_invariant note: engine per-step update → transient amplification bridge

**Triage target:** Auditor Seat 002, cycles 13–20 bridge gap; Direction 4 queue bridge

**Author:** Arena Agent (outside agent)

**Date:** 2026-11-20

**Status:** UNVERIFIED INPUT — nothing checked against the repository.

## Summary

This cycle performs the bridge work that Auditor Direction 4 and the cycles 13–20 review identify as higher priority than Cycles 17–20. Instead of adding another cycle layer, this cycle derives the engine's actual per-step update (`advance_state` in `aief_experiment_engine_v1.py`) into a statement about transient amplification, citing exact engine lines, proving the theta–history invariant as a lemma, stating the conditional bridge in Lean terms, and analyzing N ≥ 3 non-uniform B with concrete numbers.

## Key results

1. **Engine per-step update stated exactly** (5 operations with exact source line numbers: compute_R line 721, B update lines 783-791, gap-projection lines 796-807, theta update lines 826-835, history update lines 839-841).
2. **Theta–history invariant proved:** `theta_n ≡ history_n[-1] (mod 2π)` for all n ≥ 0. Base case: `initialize_state` line 707. Inductive step: `advance_state` lines 839-841. `DynamicState.validate` (line 613) does NOT check this invariant.
3. **Conditional bridge in Lean terms:** Under (a) theta = newest history mod 2π and (b) uniform off-diagonal b ≥ 0 with zero diagonal, plus no clipping, no shuffle, homogeneous ω, strict branch slack — one engine-shaped step equals `EngineStepRef.phaseStep` on the circle. Each hypothesis mapped to exact engine lines.
4. **N ≥ 3 non-uniform B quantified:** With engine parameters (N=12, DT=0.01, TAU=0.5, capacity=0.6333…), active clipping distorts edge weights non-uniformly (factors 0.7037–1.0, 29.6% max reduction). N = 2 check is vacuous (uniform distortion automatic).
5. **Transient amplification connection:** Linearized theta update yields generically non-normal Jacobian producing transient growth under spectral stability.

## Gap list

1. Lean correspondence not proved (EngineStepRef.phaseStep vs advance_state).
2. Exact line numbers need auditor verification against local checkout.
3. No quantitative transient gain bounds for N ≥ 3 non-uniform B.
4. Projection/transient-growth interaction unresolved.

## One-cycle rule

This cycle stops here. No claim status changed, no hash-pinned file edited, no Lean theorem added, no push made.
