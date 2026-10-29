# AIEFFreezeCore (Lean 4 + Mathlib)

Scalar comparison core of the **conditional** finite-time support-freezing theorem in
[`research/freezing/REPORT.md`](../../research/freezing/REPORT.md) (§3, §6). A separate Lake project so
that the hash-pinned `lean/AIEFProofs` project (root module, lakefile, check script, pin files) is not
touched. Same toolchain (`leanprover/lean4:v4.33.1`) and Mathlib pin (`0df444a3…`) as `lean/AIEFProofs`;
depends on Mathlib only.

| declaration (namespace `AIEFFreeze`) | statement |
|---|---|
| `upper_geom` | x_{n+1} ≤ ρ x_n + β, ρ ∈ [0,1) ⇒ x_n − β/(1−ρ) ≤ ρ^n (x_0 − β/(1−ρ)) |
| `eventually_off` / `eventually_on` | strict margin to the comparison fixed point ⇒ ∃N, ∀n ≥ N, x_n < B_c (resp. > B_c) |
| `edge_eventually_off` | B_{n+1} = λ_n · max 0 ((1−h)B_n + h u_n), λ_n ∈ [0,1], u_n ≤ U < B_c ⇒ eventually B_n < B_c (gate-independent) |
| `edge_eventually_on` | same recurrence with κ ≤ λ_n (κ ∈ (0,1]), L ≤ u_n, L ≥ 0, κhL/(1−κ(1−h)) > B_c ⇒ eventually B_n > B_c |

**Scope.** The conclusions are existential (∃N); the explicit N of the paper is not formalised and is
paper-level, real-arithmetic only. Not formalised: Lemma 1 (gate row-sum sandwich), Theorem 3
(gated-OFF), Corollary 4, and anything about phases, delay or the EMA. The hypotheses on the drive `u`
are the R-band hypotheses of the paper; whether the closed loop satisfies them (phase-locking with
margin) is open. This project is not wired into CI.

**Check** (from this directory): `./check_lean_freeze.sh` (or `SKIP_CACHE=1 ./check_lean_freeze.sh`
offline). Seven steps as in `lean/AIEFProofs/check_lean.sh`: toolchain, pins
(`AIEF_LEAN_FREEZE_SOURCE_SHA256SUMS.txt` covers toolchain, lakefile, manifest, all `.lean` files and the
script), imports/orphans (strict), cache, clean build with **0 warnings** required, forbidden markers
(`sorry`, `axiom`, `native_decide`, …), and an axiom audit (only propext, Classical.choice, Quot.sound).
Local result 2026-10-29: PASS, 1669 jobs, 0 warnings, 5 declarations audited.

`.lake/` is ignored by the root `.gitignore`. To reuse an existing Mathlib build instead of downloading the
cache, hard-link another project's packages: `cp -al ../AIEFProofs/.lake/packages .lake/packages`.
