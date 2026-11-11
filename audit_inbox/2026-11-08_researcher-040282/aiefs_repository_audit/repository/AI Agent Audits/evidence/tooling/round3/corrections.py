# [publication copy, 2026-10-24] local paths and personal values replaced by <placeholders>; otherwise verbatim.
import sys
P = "<v3-staging>/AI Agent Audits/"
C = lambda n, t: f" **[Correction 2026-10-24, response-2 #{n}: {t}]**"
def strike(old, n, t): return (old, f"~~{old}~~" + C(n, t))
def append(old, n, t): return (old, old + C(n, t))
R1 = "this is an exact no-go, not an ε artifact: x∉C, A_ε(x)∈int C (margin 6.67e-13 in exact arithmetic), A_ε(x)≠x, so the map as implemented is not a smooth strictly convex Bregman or positive-definite-metric projection onto C. The 1e-12 scale is a separate numerical statement. The ε=0 comparisons only rule out the Euclidean and KL projections at the sampled points"
R2 = "the round-2 matrix was a central difference across non-smooth ties, not a Jacobian. The cycle-kernel (fiber) multiplier is computed in `kappa_cycle_kernel.py`: all 110 all-tied K3s have a one-sided slow direction (+v_c) at rate r_{B,2}=0.12626; a two-sided K3 fiber exists in 5 components (1 resolved, the exceptional ρ=1 K3; 4 unresolved ρ=2 near-ties). See AIEFS_audit_response_2.md §2.3–2.4"
R4 = "Phase/history/EMA suffice for finite topology reconstruction with B reset. B is predictive and acts as a conditional continuous-weight scaffold. No unique retained register has been identified. B_split's AUC 1.0 is expected because 0/29040 edges change threshold status after the split; it is predictive, not causal"
R5 = "in sampled ensembles the delayed condition gave more distinct four-seed final topologies (a sample-diversity statistic, not a basin count)"
R8 = "only the matrices and 4 headline scalars were compared. Over all 38 keys, 78/500 runs are bit-exact; 500/500 are bit-exact on the 7 arrays and the 4 headline scalars; 422 differ in derived scalars (S_spectral, Weight_gini, Projection_norm_*) by ≤4.9e-15 abs, ≤1.3e-12 rel"
E = {
"AIEFS_audit_response.md": [
  ("Status: **current** (2026-10-23).", "Status: **partly superseded** by `AIEFS_audit_response_2.md` (2026-10-24); corrections are marked inline as \"[Correction 2026-10-24, response-2 #N: …]\". Originally current (2026-10-23)."),
  strike("(b) Weights at the split predict P_future perfectly (AUC 1.0), so the statistic mostly measures persistence.", 6, "the target was B_final > B_C, identical to P_future > 0.5 in all 440 runs (0/29040 edges differ). " + R4),
  strike("The interior witness sits only 6.7e-13 below c, so it is an ε artifact.", 1, R1),
  strike("The path dependence is carried *redundantly*.", 4, R4),
  strike("On random ω the delay systematically *increases multistability*:", 5, R5 + ":"),
  strike("Frozen-Jacobian r_B", 2, "central-difference r_B; not a Jacobian at ties"),
  strike("**As specified (S01, K3), the test cannot be run:** the K3 slow channel exists only at ρ=1, in 1/200 replays. The other 114 K3s are fully saturated with no slow mode, consistent with the manuscript's Prop 8.1 \"spectrally silent\".", 2, R2),
  strike("Repro: 500/500 archived 1.3 runs bit-exact again;", 8, R8),
  append("`audit_manifest.json` (sha256 of inputs/scripts/outputs; confirmatory vs exploratory; RAN vs inferred)", 7, "\"confirmatory\" was wrong; there was no preregistration. Relabelled \"controlled exploratory analysis with fixed recorded design\""),
  strike("The witness is ε-level (6.7e-13). The non-projection conclusion rests on the ε=0 Euclidean/KL comparisons, not on the witness.", 1, R1),
  strike("and the K3 slow channel appears only at the original T_w (1/200 replays)", 2, "the K3 one-sided slow direction exists at every T_w; see #2"),
  strike("Honest and bit-reproducible: 500/500 again.", 8, R8),
  strike("It increases multistability", 5, R5),
  strike("Redundantly carried by the weights and the phase/EMA state. Neither alone is necessary for the continue outcome.", 4, R4),
  strike("The specific K3 is non-generic (1/40 seeds; 1/200 replays across T_w).", 2, "the two-sided K3 fiber is rare (1 resolved of 200 replays, plus 4 unresolved near-ties); all-tied K3s carry a one-sided slow direction at r_{B,2} in 110/110"),
  append("Idempotent, but not a metric or KL projection.", 1, R1),
  strike("- **(ii)** For generic ω the selected topology is multistable, and delay increases the number of distinct outcomes.", 5, R5),
  strike("- **(iii)** Path dependence is carried redundantly by the weights and the phase/EMA state.", 4, R4),
  append("This was verified to ≤5e-6 (absolute, discrete form) across five window lengths and 292 components.", 2, "now checked with the cycle-kernel multiplier on 374 resolved components (κ to 2.1e-6); 40 fixed seeds × 5 T_w, not independent replications"),
  strike("**Point 2: held-out prediction of P_future > 0.5**", 6, "the target is the final threshold edge B_final > B_C, identical to P_future > 0.5 here; numbers unchanged"),
  append("Per-run Pearson corr(P, past R), mean / median:", 6, "P_future is binary except under no_mu, so these are point-biserial correlations"),
  append("**Point 9: κ(T_w)**. The κ_exact mean is shown with the discrete closed form in parentheses.", 2, "κ_exact came from a central-difference matrix; the cycle-kernel values agree (AIEFS_audit_response_2.md §2.3)"),
  strike("Exploratory, unexplained: the median early twin rate of the 114 fully saturated K3s is 0.126255. This was observed, not analysed.", 2, "explained: 0.126255 ≈ r_{B,2} = 0.12626, the rate of the one-sided +v_c direction of all-tied K3s"),
  strike("The repo's canonical analysis_manifest for that directory reports FAILED.", 3, "wrong directory conflated: the inputs come from `test_output/`, whose manifest reports a full 40/40 cohort with all validations passed and matching sha256s; the FAILED manifest is a different 1-seed partial run"),
],
"AIEFS_audit.md": [
  strike("all 500 matched the archived matrices and scalars bit-for-bit (max |diff| = 0.0)", 8, R8),
  append("- The admissibility step is a scaling heuristic, not a projection, Bregman or otherwise.", 1, "scope: exact for ε>0 against smooth strictly convex Bregman and positive-definite-metric projections; at ε=0 only the Euclidean and KL projections are ruled out (sampled points)"),
  append("Euclidean projection differs by 0.037–0.046 and KL projection by 0.022–0.030 per edge]**", 1, "the round-2 correction above is itself wrong: " + R1),
  append("**[Correction 2026-10-23, response #5: this witness is ε-level only; see M1]**", 1, "it is an exact no-go; see M1"),
],
"AIEFS_salvage.md": [
  append("at ε=0 the Euclidean projection differs by 0.037–0.046]**", 1, R1),
  append("B at split predicts the future set with AUC 1.0]**", 4, R4),
  append("The (7,2,7) K3 appears in 1/40 seeds (repo's own k3_prevalence_report)", 2, "this concerns the two-sided strict K3; all-tied K3s (110 components, 34 seeds) carry a one-sided slow direction at r_{B,2}"),
  append("Its outputs can be interior only at the ε level (6.7e-13; #5),", 1, R1),
  strike("The K3 slow channel exists only at T_w=17.50 (1/200 replays), so the K3 version cannot be tested.", 2, R2),
  append("Its own report says \"does not establish universality\".", 2, "the two-sided K3 is rare, but the k=2 rate itself appears as a one-sided direction in all 110 all-tied K3s"),
  strike("> - **(ii)** For generic ω the selected topology is multistable, and delay increases the number of distinct outcomes.", 5, R5),
  strike("> - **(iii)** Path dependence is carried redundantly by the weights and the phase/EMA state.", 4, R4),
  append("verified to ≤5e-6 across five window lengths and 292 components.", 2, "rechecked with the cycle-kernel multiplier: 374 resolved components, κ to 2.1e-6; 40 fixed seeds"),
  strike("shows delay increases multistability.", 5, R5 + "."),
],
}
for fn, reps in E.items():
    s = open(P + fn, encoding="utf-8").read()
    for old, new in reps:
        n = s.count(old)
        if n != 1: sys.exit(f"{fn}: {n} matches for: {old[:80]}")
        s = s.replace(old, new)
    open(P + fn, "w", encoding="utf-8").write(s)
    print(fn, len(reps), "edits")
