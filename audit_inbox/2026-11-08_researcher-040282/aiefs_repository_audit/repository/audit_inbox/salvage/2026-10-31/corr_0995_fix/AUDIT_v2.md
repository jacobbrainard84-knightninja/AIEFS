# Audit of `fix/corr-0995-scope-v2` @ 4f5df7b (on top of b77ce5f)

Date: 2026-10-28 (local, read-only audit; nothing pushed). Worktree `/workspace/AIEFS_corr_scope` (clean). Evidence read at the same blobs as `main` 853498f: `git diff 853498f 4f5df7b -- "AI Agent Audits"` is empty.

- Diff scope: `4f5df7b` changes exactly 2 lines (1 per file) in `AI_AGENT_HANDOFF_PROMPT.md` (l.118) and `AIEF_HISTORIC_UNFOLDING.md` (l.171). The new paragraph is byte-identical in both files.
- `git diff --check b77ce5f 4f5df7b` → no output, exit 0. `git diff --check 853498f 4f5df7b` → exit 0. No CRs.
- Sources: `AI Agent Audits/evidence/results/delay_heldout_analysis.json` (cited below as `J:`), the script `evidence/scripts/analyze_delay_heldout.py`, `results/omega_random.json` and `logs/omega_random.log`, `results/frozen_topology_check.json`, `AI Agent Audits/AIEFS_salvage.md` (`S:`) and `AIEFS_audit_response.md` (`R:`) at 853498f.
- Below, "Rpred" is the Δω-only predictor `Rpred_only (Delta-omega closed form)` and "Rpast" is `Rpast_only (endogenous, = Corr_physical input)`. The target is `final_threshold_edge`. `J:point2_heldout_P_future_gt_half` is numerically identical, and `J:label_equality` shows 0 differing edges in every condition.

## A. Researcher 001's stated basis

| Claim | Verdict | Evidence |
|---|---|---|
| (1) Delay off at repo ω: Δω-only already has AUC 1.0 | **Accurate** | `J:point2_heldout.repo_omega_no_delay.heldout_seed_10fold.Rpred_only.auc = 1.0` (logloss 2.68e-6). Rpast is also 1.0 (logloss 2.30e-6). `mean_pearson_P_Rpred = 0.9955`. |
| (2) Uniform no-delay: Rpast AUC 0.850 vs Rpred 0.883, so Rpast wins only on log loss | **Accurate** | `J:point2_heldout.uniform_no_delay.heldout_omega_LOGO`: Rpast auc 0.84997, logloss 0.2397; Rpred auc 0.88289, logloss 0.3957. The combination is also lower: `Rpred+Rpast.auc = 0.8680 < 0.8829`. |
| Conclusion: "past R adds beyond Δω" holds for repo-ω baseline and as a calibration gain in uniform, not across the board | **Accurate, slightly conservative for uniform baseline** | Repo-ω baseline: Rpast auc 0.999995 vs 0.97216, logloss 0.00286 vs 0.12363, `rpast_beats_rpred_runs = 100/100`. Uniform *baseline*: Rpast also edges Rpred on AUC (0.8444 vs 0.8328), and Rpred+Rpast reaches 0.8571 (no CI is reported), with logloss 0.2608 vs 0.4455. So there it is not purely a calibration gain. R:2 and R conclusion 3 ("adds over Δω-only for uniform") overstate this for uniform no-delay. |

## B. Sentence-by-sentence: 4f5df7b paragraph

**S1.** "The reported mean Corr_physical ~0.995 is a within-graph edgewise association (66 edges per run) between past resonance and future threshold persistence, averaged over 100 independently initialized runs that all use the repository's fixed, deliberately clustered frequency vector with delay on."
→ **Accurate.**
- `J:point2_heldout.repo_omega_baseline.mean_pearson_P_Rpast = 0.99522`, `n = 100`.
- `J:label_equality.repo_omega_baseline.edges_total = 6600` (6600 / 100 = 66 = C(12,2)).
- The ω vector is "hand-picked tight clusters around 1.0, 1.5 and 2.0" (S:42).
- Nit: "deliberately" infers intent. "hand-picked, tightly clustered" matches S:42 exactly. The value is not delay-specific either: delay off gives 0.99854 (`repo_omega_no_delay.mean_pearson_P_Rpast`).

**S2.** "It should not be generalized to other frequency sets." → **Accurate.**

**S3.** "Controlled exploratory N=12 random-frequency studies gave lower and very uneven values: uniform ensembles had a mean near 0.75 but a median near 0.98 (60/60 runs defined), and clustered ensembles had a mean near 0.53-0.55 with only 37-39 of 60 runs defined, because in the rest every edge had the same persistence label."
→ **Numbers accurate. The sourcing is incomplete (overstated as the only figures).**
- Uniform: `J:point2_heldout.uniform_baseline.per_run_correlations.pearson_P_Rpast = [0.74547, 0.97751, 60]` and `uniform_no_delay … = [0.74656, 0.98649, 60]`, with `correlation_valid_runs = 60`.
- Clustered: `clustered_baseline … = [0.55332, 0.44900, 37]` and `clustered_no_delay … = [0.53095, 0.37944, 39]`. `correlation_undefined_runs_constant_P = 23 / 21`, and `_meta.warnings` gives "23/60 … 21/60 runs have constant P_future".
- The "same label" reason holds because P_future is binary: `frozen_topology_check.json → random_omega_delay_experiment.*.nonbinary_P_future_count = 0`.
- Problem: these figures come from the 15+15 ω × 4-seed **replication** only. The first pass (S table §3.1, S row 2, R:3; `logs/omega_random.log`) gave 0.711/0.712 (uniform) and 0.588/0.634 (clustered). The note drops those without saying why, so it now disagrees with S row 2, which it no longer cites.
- "lower" is true of the means. The uniform median (0.98) is barely below 0.995.

**S4a.** "The association is expected from the model, because resonance drives weight growth and the future threshold topology is already frozen, but it is not a frequency-gap tautology:"
→ **Accurate.** `frozen_topology_check.json`: `edges_changing_status = 0` in every archived repo-ω and random-ω condition. That file is not cited in the Evidence line, though.

**S4b.** "…in held-out tests past resonance beat a frequency-gap-only predictor for the repository frequencies with delay,"
→ **Accurate.** `J:point2_heldout.repo_omega_baseline.heldout_seed_10fold`: Rpast auc 0.9999952 / logloss 0.002865 vs Rpred 0.9721572 / 0.123632, with `rpast_beats_rpred_runs = 100`. Precision nit: at repo ω the held-out unit is the **seed** (10-fold); only the random-ω tests hold out ω sets (LOGO).

**S4c.** "…and improved calibration (log loss) for uniform ensembles,"
→ **Accurate.**
- `uniform_baseline`: logloss 0.26076 vs 0.44555.
- `uniform_no_delay`: logloss 0.23972 vs 0.39574.
- Note: log loss mixes calibration and discrimination. Calling it "calibration" is fair for no-delay, where Rpast's AUC is lower. For baseline, Rpast's AUC is also slightly higher (0.8444 vs 0.8328).

**S4d.** "…but not in clustered ensembles,"
→ **Overstated / partly wrong.**
- Discrimination does fail: Rpast auc 0.45706 vs Rpred 0.65232 (`clustered_baseline`) and 0.47296 vs 0.72531 (`clustered_no_delay`), both below chance.
- Read as part of the preceding "improved calibration (log loss)" clause, it is wrong for `clustered_baseline`: Rpast logloss 0.30402 < Rpred 0.31910.
- Adding Rpast to Rpred lowers log loss in both clustered conditions: 0.30168 < 0.31910, and 0.27306 < 0.27878.
- Rpast alone is worse only in `clustered_no_delay` (0.28590 > 0.27878).
- All of these log-loss differences are ≤ 0.017.

**S4e.** "…and with delay off at the repository frequencies the frequency gap alone was already perfect."
→ **Accurate.** `repo_omega_no_delay.Rpred_only.auc = 1.0`, logloss 2.68e-6 (see A1).

**S5.** "Evidence: `AI Agent Audits/evidence/results/delay_heldout_analysis.json` (sections point2_heldout and label_equality)."
→ **Partly wrong (miscited).**
- `label_equality` does not show the "same persistence label" fact. Per `analyze_delay_heldout.py` l.8-10 and 116-130, it checks that the `B_final > B_C` target equals `P_future > 0.5`.
- The constant-label runs are in `_meta.warnings` and `point2_heldout.*.correlation_undefined_runs_constant_P`.
- The frozen-topology fact is in `frozen_topology_check.json`.
- The revision also removes the links to S §3.1 row 2 and R point 2, which hold the first-pass numbers and the held-out table (R §5).

**S6.** "Do not cite 0.995 as a general AIEF result." → **Accurate.**

## C. The original b77ce5f note (0.71 and 0.59–0.63)

- "holds only for the repo's hand-picked frequencies (omega)" → **Accurate.** Repo-ω only: 0.9952 with delay on, 0.9985 with delay off.
- "With random frequencies it drops to about 0.71 (uniform) and 0.59-0.63 (clustered)" → **Accurate as a citation, overstated as a characterization.**
  - The numbers match the first-pass means in `logs/omega_random.log`: uniform Corr_phys 0.711 (no_delay, n=20) and 0.712 (baseline, n=40); clustered 0.588 (no_delay) and 0.634 (baseline). They also match S row 2 and R:3.
  - Recomputed from `results/omega_random.json`: the clustered means cover only the **defined** runs (15/20 no-delay, 30/40 baseline), and the note does not say so.
  - Uniform medians are 0.975/0.975, so "drops to about 0.71" does not describe a typical run.
  - The independent replication gives a uniform mean of 0.745/0.747 and a clustered mean of 0.553/0.531 (`J` above; R:2(c)). The clustered 0.59–0.63 range therefore does **not** replicate: it is 0.53–0.55.
- "It is not tautological, but it mostly measures persistence." → **Supported but contested.** R conclusion 3 ("dominated by persistence") and S §3.2 ("mostly persistence") support it. However, R:2(b)'s "so the statistic mostly measures persistence" is struck through by the 2026-10-24 correction (response-2 #6: B_split AUC 1.0 is "predictive, not causal").

## D. Suggested exact wording (replaces the 4f5df7b paragraph in both files)

> Scope note (audit correction, revised 2026-10-28): The reported mean Corr_physical ~0.995 is a within-graph edgewise association (66 edges per run) between past resonance and future threshold persistence, averaged over 100 independently initialized runs that all use the repository's fixed, hand-picked, tightly clustered frequency vector with delay on (about 0.999 with delay off). It should not be generalized to other frequency sets. In exploratory N=12 random-frequency runs the mean was lower and the per-run values were very uneven. In the first pass (20+20 frequency sets) uniform ensembles averaged about 0.71 and clustered ensembles 0.59-0.63. In a replication (15+15 sets × 4 seeds), uniform ensembles had a mean near 0.75 but a median near 0.98 (60/60 runs defined), and clustered ensembles had a mean near 0.53-0.55 with only 37-39 of 60 runs defined. In the other clustered runs every edge had the same persistence label, so the correlation is undefined. The association is expected from the model, because resonance drives weight growth and the threshold topology does not change after the split. It is not a frequency-gap tautology, though. In held-out tests, past resonance beat a frequency-gap-only predictor at the repository frequencies with delay (held-out seeds: AUC 0.99999 vs 0.972). For uniform ensembles (held-out frequency sets) it mainly lowered log loss (0.26 vs 0.45 with delay; 0.24 vs 0.40 without), with similar or lower AUC (0.84 vs 0.83 with delay; 0.85 vs 0.88 without). In clustered ensembles it discriminated no better than chance (AUC 0.46-0.47 vs 0.65-0.73 for the frequency gap), with log-loss differences of at most 0.02. With delay off at the repository frequencies, the frequency gap alone was already perfect (AUC 1.0). Evidence: `AI Agent Audits/evidence/results/delay_heldout_analysis.json` (point2_heldout; constant-label runs in `_meta.warnings` and `correlation_undefined_runs_constant_P`), `AI Agent Audits/evidence/results/frozen_topology_check.json`, `AI Agent Audits/AIEFS_salvage.md` (section 3.1 and row 2) and `AI Agent Audits/AIEFS_audit_response.md` (points 2-3). Do not cite 0.995 as a general AIEF result.

If a shorter edit is preferred, make the minimum fixes:

1. S4d: replace "but not in clustered ensembles" with "but in clustered ensembles it discriminated no better than chance (AUC 0.46-0.47 vs 0.65-0.73), with log-loss differences of at most 0.02".
2. S5: replace "(sections point2_heldout and label_equality)" with "(point2_heldout; constant-label runs in `_meta.warnings`) and `results/frozen_topology_check.json`".
3. S3: add "(replication; the first pass in AIEFS_salvage.md §3.1 gave about 0.71 uniform and 0.59-0.63 clustered)".

Out of scope, for a later pass on main: R conclusion 3 and R:2 say Rpast "adds over Δω-only for uniform". That holds for uniform *baseline* (AUC and log loss), but for uniform no-delay it holds on log loss only.
