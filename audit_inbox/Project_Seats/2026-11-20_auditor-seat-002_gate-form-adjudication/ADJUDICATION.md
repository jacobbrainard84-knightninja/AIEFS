# Gate form and AUD-RATELAW: seat adjudication (OQ16, TRIAGE R026-S9)

- **Seat:** Auditor Seat 002. I wrote neither side of this dispute.
- **Date:** 2026-11-20, about 5:20 PM MST.
- **main reviewed:** `d7b9fac600686477babf229ede70a19f1c2dfa13`. Gate: `aief_experiment_engine_v1.py` L803–812, `scale = min(1, capacity/(row_sum_pre + eps))` and `B_unprojected * minimum.outer(scale, scale)`.
- **Inputs read, nothing run:**
  - Arena `audits/experiments/gate_form/REPORT.md` and `run_gate_form.py` on `arena/d4a487cc-aiefs` @ `2af3859`.
  - GPT-6 `2026-11-15_gpt-6_rate-law-gate-adjudication.md`.
  - `registry/claims.csv` L47 (AUD-GATE) and L50 (AUD-RATELAW).
  - `AI Agent Audits/AIEFS_salvage.md` L78 and L137.
  - The Miller & MacKay 1994 abstract and introduction (Neural Computation 6:100, author PDF at Columbia CTN).
- **What I ran:** only my own `gate_exact.py` in this folder (Python 3.13.5, stdlib `fractions`, exact arithmetic, eps = 0). It does not import the engine or any deposited script. Output: `gate_exact.json`.
  - sha256 `gate_exact.py`: `c0d37acdf39c2619c807beb510d298c8471832feb0098d8b12ace0002799933c`
  - sha256 `gate_exact.json`: `203eff3e4129511fbf994df158d0cdd1a83eefbb1e051cf36fbf82bd1aefa508`
  - cap = 19/30 = (a − δ)/q = 0.95/1.5, as on main.

## Verdict

**Option (i): terminology and citation correction only. AUD-RATELAW keeps its scope and status.** One new, small, genuine property of the gate is recorded below as UNEXPLAINED-impact, not as a result.

## Findings

**F1. Arena compared against the wrong rule.** Miller & MacKay's constraint conserves or limits "the total synaptic strength over a cell". The decay rate is "set for the cell as a whole" (abstract and §1). That is a **per-cell** factor, one per node, and not the single global factor Arena's script uses (`enforce_global_multiplicative`). The paper also says the results apply to constraints "over output cells and over input cells". Arena's conclusion survives anyway, because the AIEF gate is not per-cell multiplicative either (F2). Arena's Part A table, which shows 1 factor against 11, does not measure the right comparison.

**F2. The AIEF gate is a third rule: per-edge min-endpoint scaling.** It is exact (W1, W2).
- **W1 (spillover).** Only node 0 is over the cap. Nodes 1 and 2 are under the cap, but their edges to node 0 are still scaled by s_0 = 38/45. Their rows drop from 3/5 to 47/90 and from 7/20 to 14/45. Each of those rows is multiplied by two different factors, {38/45, 1}, so the row's direction changes. Per-cell multiplicative would leave rows 1 and 2 untouched.
- **W2 (overshoot).** Nodes 1 and 2 are over the cap (7/10 > 19/30). After the gate their rows land at 209/420 ≈ 0.498, far **below** the cap of 0.633, because their edges to the heavier node 0 take node 0's smaller factor. Per-cell multiplicative would put them exactly at the cap.
- The output still touches the boundary. The node with the smallest scale always lands exactly at the cap when eps = 0. This agrees with salvage §3.4 ("interior only at the ε level" refers to the whole output, not to individual rows).
- **Why the min is there.** Per-cell scaling breaks symmetry (`percell_symmetric: false` in W1 and W2). The min form is a symmetry-preserving choice. That is a reasonable design, but it is not the Miller–MacKay rule, and their principal-eigenvector theorem cannot be cited for it.

**F3. When the loads are equal, the three rules coincide (W3).** On a saturated clique with equal row sums, the gate, the per-cell rule and a single global factor give identical results (s = 19/36). Salvage L137's "effective weight-proportional decay" reading is therefore correct **inside that scope**, which is the saturated, equal-scale regime where the kη/c rates are derived. It is wrong as a general name for the gate.

**F4. AUD-RATELAW's one-step identity checks out exactly (W4, W5).**
- **W4 (equal scales).** Saturated K4, all controllers tied, s_J = 38/45. Take h in ker A_J: +1 on edges (0,1) and (2,3), −1 on (0,2) and (1,3). The scales are unchanged, and the gated difference equals exactly s_J·ε·h, as conditions (d) and (e) of `claims.csv` L50 predict. With the γ-decay included, the (1 − γdt) factor passes through linearly; see GPT-6 §3, which I re-derived and agree with.
- **W5 (unequal scales).** Node 0 has scale 19/27 and the others 19/24. With the same h, the scales are still unchanged, but the gated difference is **not** proportional to h, and two of its row sums become ±19/216000, so it leaves ker A_J. Condition (e) is essential, as the claim already states.
- Arena's Part A tests generic matrices, while the claim concerns perturbations in ker A_J under (d) and (e). These are different statements, so round 10 does not touch the claim.

## Recommended changes. These are owner items; ledger changes go only through the reconciliation script.

1. **AUD-GATE wording** (`claims.csv` L47). Replace "is node-strength multiplicative normalisation" with: "is symmetric per-edge min-endpoint capacity scaling, B_ij ← B_ij·min(s_i, s_j). It coincides with per-node multiplicative (Miller–MacKay-type) normalisation only when the endpoint scales on a row are equal." The rest of the statement is unchanged.
2. **Salvage L137 and L78.** Add a dated correction note that says the same thing; keep the kη/c citation, scoped to equal-scale saturated components. The salvage file is listed in `AI Agent Audits/evidence/audit_manifest.json` and `registry/artifacts_current.csv`, so treat it as pinned: record the correction as a new ERRATA entry, not as an edit to the file.
3. **AUD-RATELAW** stays Supported / Conditional theorem. Optional: tighten the A_J definition as GPT-6 suggested.

## UNEXPLAINED, not a result

F2's spillover and overshoot mean a heavily loaded node prunes its neighbours' other links harder than the cap requires. Arena's replica, which is indicative only, reports the gate binding on about 89% of steps. **How often binding rows end strictly below the cap in real engine runs, and whether that affects topology selection, is unmeasured.** Proposed next step: a read-only counter on main's engine run, done by a seat, with no engine edit (mutants and instrumentation go only in temp copies).
