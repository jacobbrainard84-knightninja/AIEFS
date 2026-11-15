# Closed-loop synchronized rotating orbit — audit draft

- **Agent:** Arena.ai Agent Mode
- **Date:** 2026-09-11, Atlantic/Reykjavik
- **Repo:** main `871417d58504dd2e42276bde8142e3fdac73df44`; tested `aief_experiment_engine_v1.py` SHA-256 `ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede`
- **Scope:** exact-real idealization of `aief_experiment_engine_v1.py` `compute_R` (lines 721–752) and `advance_state` (lines 755–845); finite Python checks. Unverified input, not a project claim.

## Proposed construction

With identical frequencies ω, symmetric complete-graph weights b, synchronized queue entries and no shuffle, set the full delay history to the uniformly rotating phases θₙ=(θ₀+n·dt·Ω) mod 2π and all EMA entries to z=exp(i(Ωτ−ωτ)), assuming τ=d·dt. Put m=N−1 and K=mb. The coupled dynamics preserves this trajectory if Ω solves Ω=ω−K sin(Ωτ), and b is a fixed point of the engine weight update at reported off-diagonal R=1. If Kτ<1, the frequency root exists and is unique. Interior branch: b=η/γ with mb<capacity. Projected branch, for t=1−dtγ>0 and h=dtη>0: b is the unique positive root of `m t b² + (m h + ε − capacity t)b − capacity h = 0` and must separately satisfy `m(tb+h)>capacity`. Here ε is `scale_epsilon`; the projection uses `minimum.outer` and hence a single scale factor. See workspace `AIEFS_cycle8/ONE_PAGE_NOTE.md` for conditions and derivation.

This is an exactly prepared special orbit, not a proof that normal random initialization/zero EMA approaches it; neither stability nor attraction nor applicability to heterogeneous production frequencies is claimed. The analytic construction has not been checked in Lean or independently reviewed.

## Reproduction

`python3 /home/user/AIEFS_cycle8/test_rotating_solution.py` requires the workspace engine, NumPy, and Cycle 7 helper. For N=12, d=50 and homogeneous ω≈1.42833, tests ran 1,000 steps each on interior η=.0005 and projected η=.04; projection triggered 0 and 1000 times respectively. Maximum circular phase errors were 6.39e−14 and 8.97e−14. Guessing Ω=ω failed by about 0.00415 in one-step phase increment. Full output, source hashes, and remaining state errors are in `AIEFS_cycle8/test.log` and `SHA256SUMS.txt`. These finite float64 checks do not prove the analytic statement or equivalence to Lean. No full project gate or mutation suite was run. Main's PR #38 C014 follow-up was not reviewed in this cycle.

Please independently verify the reduction, branch conditions and one-step orbit invariance before any formalization or claim promotion. No repository changes or push were made.
