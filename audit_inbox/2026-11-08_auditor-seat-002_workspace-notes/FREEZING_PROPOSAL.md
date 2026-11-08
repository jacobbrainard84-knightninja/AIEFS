# Freezing: status and assessment of the Corollary 4 fix

Fri Oct 30, 2026 (7:20–7:38 PM EDT). **Status: PENDING.** This is Researcher 001's work.

- `85ba0a6` is not in `integration/round5`, and the final claims will not be built from `85ba0a6`.
- The 4-row claim split is adopted. Merge it once Researcher 001 posts the new sha with the split and the Corollary 4 fix. The recipe is in `MERGE_PLAN.md` §3: E12, builder order LEAN-KN-01 then freezing rows, `AIEFFreezeCore` required, exec bits, inventory regeneration.
- I have not rewritten any freezing proof or claim row.

## The gap (in `85ba0a6` `research/freezing/REPORT.md`, Corollary 4)

The limit form says the Thm 2/3 inequalities are "strict and continuous in (U⁺, u^min, S⁺, ℓ)", so they hold on some finite tail [T,∞).

But Thm 3's lower bound ℓ_f = max(0, x*_f − ρ_f^{N1}(x*_f − x_{T,f})⁺) depends on the **state** x_{T,f} at the chosen T, not only on the limsup/liminf data. Moving T moves ℓ_f, so the limit-form hypothesis is not a statement about limits alone.

## The proposed fix: B_f(n) ≥ (1 − ρ_f^{N1}) x*_f for n ≥ T + N1

**Assessment: correct, and it closes the gap.**

1. The proof of Thm 2 (ON) gives x_{T+k} ≥ x* − ρ^k(x* − x_T) = (1 − ρ^k)x* + ρ^k x_T for every k ≥ 0.
2. x_T = B_f(T) ≥ 0, because the update clips at 0. So x_{T+k} ≥ (1 − ρ^k)x*.
3. For an edge with u^min_f > 0, we have g_f ≥ 1 and 0 < h < 1, so ρ_f = (1−h)/g_f ∈ (0,1). Also x*_f = h u^min_f/(g_f − 1 + h) > 0. So (1 − ρ^k)x* is non-decreasing in k, and for every k ≥ N1 it is ≥ (1 − ρ^{N1})x*.
4. Hence B_f(n) ≥ (1 − ρ_f^{N1})x*_f for all n ≥ T + N1, whatever the state at T. The sign conditions this needs (x_T ≥ 0, x* ≥ 0, 0 ≤ ρ < 1) already hold under Thm 2's hypotheses.
5. For edges with u^min_f ≤ 0, keep ℓ_f := 0.

The new bound depends only on (h, u^min_f, S⁺ via g_f, N1). These are tail quantities, so the "strict and continuous, take T large" argument now goes through: fix N1 first, then choose T.

## Things to state in the write-up

- **(a) Two different ℓ.** The new ℓ is weaker than the state-based ℓ_f, because it drops the ρ^{N1}x_T term. A weaker ℓ means a smaller σ_i and a larger κ, so the corollary's gated-OFF condition is harder to meet. Say that the corollary uses the state-free ℓ.
  - The finite-T code certificate (`freeze_check.py::certificate`) may keep the state-based ℓ_f, which remains valid for that specific T.
  - Do not claim that the code's certificates and the corollary's hypothesis are the same condition.
- **(b) Order of quantifiers.** The required order is: N1 exists; the strict limit inequalities hold with ℓ = (1 − ρ^{N1})x*; therefore T exists. The ON/OFF parts (Thm 2) were already state-independent in their thresholds; only their N depends on x_T, and that is fine for an "eventually" statement.
- **(c) Status label.** It stays "PROVEN (paper proof; not in Lean)". If FreezeCore formalizes the comparison lemma, the k ≥ N1 monotonicity step is a small Lean lemma. I have not added it, because that is Researcher 001's code.
- **(d) Unchanged caveats.** The float64 margin guard (§3.6) and the open items O1–O4 are unchanged by this fix. In particular, freezing of the closed loop is still conditional on R on [T,∞).

I have not seen Researcher 001's new commit. When it lands, check the corollary text against points 1–5 and (a)–(b), and confirm the 4 claim rows match the split.
