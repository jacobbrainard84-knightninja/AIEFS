#!/usr/bin/env python3
"""Reconcile registry/claims.csv against the AI-agent audit verdicts (rounds 1-4).

Written 2026-10-28 by Researcher 001 (local merge-prep; not pushed).
Idempotent: re-running on an already-reconciled claims.csv rebuilds the same
columns from the pre-audit values recorded in `prior_status`.

Rules followed:
  * artifact_status / evidence_scope stay inside the arena vocabulary enforced by
    audits/engineering/verify_inventory.py.
  * The audited verdict goes in NEW columns: prior_status, audited_status,
    audit_source, reconciliation_note, legacy_list_refs.
  * Where the audit records do not settle a claim, audited_status is
    "needs owner/auditor decision". No verdict is invented.
Second pass 2026-10-28 (MERGE_CHECK.md required + minor fixes, owner SSRH correction):
  * STATEMENT_OVERRIDE / SCOPE_OVERRIDE reword a few arena statements (original wording is in git at 7edbab2).
  * NEW rows are skipped on input and rebuilt, so re-running stays idempotent.
  * artifact_status / evidence_scope still stay inside the verify_inventory.py vocabulary; where the audited
    label has no vocabulary value (e.g. 'Quarantined', 'controlled exploratory analysis with fixed recorded
    design', 'Speculative / untested origin hypothesis') the label is in audited_status and the row note says so.
Line endings (2026-10-28, work/post-push-1): both outputs are written with LF ("\n"), matching the
branch after the upload converted registry CSVs to LF. Neither output is hash-pinned. The input
LINEAGE_IN is pinned (CRLF bytes, ART-2845) and is only read, never written.
Audit file abbreviations used in audit_source (all under "AI Agent Audits/"):
  audit  = AIEFS_audit.md            salvage = AIEFS_salvage.md
  resp1  = AIEFS_audit_response.md   resp2   = AIEFS_audit_response_2.md
  resp3  = AIEFS_audit_response_3.md
"""
import csv, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
CLAIMS = ROOT / "registry" / "claims.csv"
LINEAGE_IN = ROOT / "audits/github_reconciliation/recovered_from_workspace_019ff402/zip_only_files/AIEF_1_4_analysis_lineage.csv"
LINEAGE_OUT = ROOT / "registry" / "lineage_reconciliation.csv"

BASE_COLS = ["claim_id", "study_id", "statement", "artifact_status", "evidence_scope",
             "supporting_artifacts", "scope_boundary_and_caveat"]
NEW_COLS = ["prior_status", "audited_status", "audit_source", "reconciliation_note", "legacy_list_refs"]
ND = "needs owner/auditor decision"

# ---- verdicts for existing arena rows ---------------------------------------
# claim_id -> (new artifact_status or None to keep, audited_status, audit_source, note)
CFS = "Supported (conditional, single exceptional seed; not independently re-derived by the audit)"
CFOBS = ("Finite numerical observation, single seed (not re-checked by the audit); not Frozen "
         "(artifact_status moved Frozen -> Supported on 2026-10-28, MERGE_CHECK Q2)")
EXISTING = {
 "EMP-AIEF13-01": (None, "Supported (audit-qualified)",
   "salvage §3 table row 3c (line 99) + §3.3; resp1 ledger #8 (line 21); resp2 #7 (line 21), #8 (line 22)",
   "Valid necessity test, but the outcome is forced by construction (shuffled mean R 0.371 < threshold 0.4286, so D_B=0). "
   "Design was fixed and recorded, not preregistered (resp2 #7). Numbers re-run 2026-10-28 by Researcher 001 with "
   "--cohort syntax: D_B +0.305909 [0.298939, 0.313030], dz 8.434 (matches)."),
 "EMP-AIEF13-02": (None, "Supported (audit-qualified)",
   "salvage §3 table row 3a (line 97) + §3.3; resp1 §3 item 4 (line 43); resp2 #5 (line 19)",
   "no_mu is a valid necessity test with a closed-form explanation. Delay: 'not necessary, but not inert' (resp1 §3.4); "
   "the caveat 'adaptive coupling feedback rather than bare delay length drives persistence' is broader than the audit wording. "
   "Re-run 2026-10-28: no_mu +0.271061 dz 4.900; no_delay -0.027424 dz -0.756 (matches)."),
 "EMP-AIEF14-01": (None, "Supported (audit-qualified, reworded)",
   "resp2 #4 (line 18) and §3 wording; resp1 §3 item 5 (line 44); salvage §3 table row 5a (line 101); resp3 #4 (line 25)",
   "Use the audit wording: 'Phase, history and EMA together suffice to reconstruct the finite topology when B is reset "
   "(reset_B: Jaccard 1.000 vs continue). B is predictive and acts as a conditional continuous-weight scaffold. No unique "
   "retained memory register has been identified.' B_split AUC 1.0 is predictive, not causal: 0/29040 edges change threshold "
   "status after the split (resp3 #4). Scope: 40 paired seeds."),
 "EMP-AIEF14-02": ("Exploratory", "Exploratory: controlled exploratory analysis with fixed recorded design (per audit; not Frozen)",
   "resp2 #3 (line 17), #7 (line 21); resp1 §6 Limits (line 101 ff.); evidence/results/matched_phase_check.json",
   "CONFLICT resolved 2026-10-28: arena labelled this Frozen / Controlled experimental result and said delayed phase/EMA history 'mediates' "
   "recovery; the statement is reworded and 'mediates' dropped. The audit says 'It stays exploratory' (resp2 #3); label per resp2 #7. "
   "evidence_scope is 'Finite numerical observation' because the verify_inventory.py vocabulary has no exploratory-design value. Audit numbers (re-run 2026-10-28, matched_phase_check.py): "
   "Weighted_similarity_late +0.06415 [0.0405, 0.0886], 31/40 positive; P_mean_late is NEGATIVE (-0.0176 [-0.0267, -0.0086]). "
   "Inputs are test_output/ (manifest sha 2a57bc25...); aief_1_4_matched_phase_memory_ablation/ is a separate FAILED 1-seed partial run. "
   "'Mediates' is causal language the audit does not support."),
 "EMP-AIEF14-03": ("Exploratory", "Controlled exploratory analysis with fixed recorded design (DID estimand not tested by the audit); not Frozen",
   "not adjudicated; same exploratory-label rule as EMP-AIEF14-02 (resp2 #3 (line 17), #7 (line 21)); related: resp1 §3 item 6 (line 45), salvage §3 row 5c (line 103), evidence/results/kappa_tw_summary.json; see AUD-KAPPA-TW",
   "The DID estimand / horizon-confounding statement was not tested by the audits. The audits only checked the kappa(T_w) rate law "
   "on the same runs (row AUD-KAPPA-TW). artifact_status moved Frozen -> Exploratory and evidence_scope to 'Finite numerical observation' "
   "on 2026-10-28 (MERGE_CHECK Q2); the run outputs themselves stay frozen. REPRODUCING.md §5 re-ran the v4 analysis: hashes match."),
 "IMPL-MODULAR-01": (None, "Supported (implementation identity; not re-tested by the audit)",
   "not adjudicated by the audits; resp2 Provenance gaps item 2 (line 146): the round-1 pytest output was not saved",
   "Researcher 001 re-ran tests_modular on 2026-10-28 with AIEF_RUN_SLOW_TESTS=1 and the repository root on PYTHONPATH: 41 passed, 1 skipped "
   "(default run: 40 passed, 2 skipped; see AUD-MODULAR-ORACLE) (Python 3.13.5, numpy 2.5.1, scipy 1.18.1, pandas 3.1.0). "
   "That does not by itself re-test the 344-array max_abs_diff=0 identity. 2026-10-28: the personal device name in the arena "
   "statement/caveat was replaced by 'a second Linux host (glibc 2.40)' (privacy; see PRIVACY_SCRUB_LIST.md P5)."),
 "LEAN-CF-01": (None, "Supported (audit-verified; trivial linear algebra, scope-limited)",
   "salvage §3 row 6 (line 104) + §3.6; resp1 §3 item 8 (line 47); resp3 §0 and §5 (lines 10, 121)",
   "Builds once the dangling import is fixed (fixed before round 4). The theorem is a 2x3 kernel identity; it says nothing "
   "about the dynamics. The Lean headers ('Copyright ... All rights reserved. Released under Apache 2.0 license ...' plus SPDX) are the standard Mathlib header form and do not conflict with the Apache-2.0 licence added on main on 2026-10-24 (commit 115e99e); corrected 2026-10-28 (earlier wording called it an open conflict)."),
 "CAVEAT-MS-8.4": (None, "Exploratory / caveat (arena's own correction; accepted, not audited)", "not adjudicated by the audits; related salvage §3 row 5b (line 102)",
   "Arena's own correction; the audits did not re-derive Corollary 8.4."),
 "CF01": (None, CFS, "not individually adjudicated; resp1 ledger #11 (line 24) says terminology is used in its standard sense; salvage row 5b",
   "Audit-wide caveat (salvage row 5b): 'valid linear algebra, oversold; non-generic'. The exceptional K3 is 1 of 40 seeds."),
 "CF02": (None, "Supported (audit-consistent) — wording caveat",
   "resp2 #1 (line 15) + §2.1; resp3 #5 (line 26) + §2.1; salvage row 4 (line 100)",
   "The audit independently found the clipped row interior (epsilon-level margin 6.7e-13). The arena wording 'projected output' used projection "
   "language the audit retired (the gate is node-strength multiplicative normalisation, not a metric/KL/Bregman projection); "
   "reworded to 'gated (node-strength-normalised) output' on 2026-10-28."),
 "CF03": (None, CFS, "not individually adjudicated; salvage row 5b (line 102)", "Single exceptional trajectory (1/40)."),
 "CF04": (None, CFS, "not individually adjudicated; salvage row 5b (line 102)", "Pure linear algebra; the audits did not re-check it."),
 "CF05": ("Supported", CFOBS, "not individually adjudicated; salvage §3.5 genericity (1/40); resp2 #2 (line 16)",
   "Single exceptional seed. resp2 #2 confirms a two-sided K3 fiber exists for the exceptional resolved K3 (rho=1, J={2,7}), but "
   "did not re-check the (7,2,7) winner map over 32,001 states."),
 "CF06": (None, "Supported (audit-consistent; conditional, single seed)",
   "resp2 #2 (line 16) + §2.4; resp3 #3 (line 24) + §2.4; LEAN-CF-01",
   "Kernel span(1,-1,-1) is formalised in Lean; the audit's census finds a two-sided fiber only for the exceptional resolved K3. "
   "Other K3s have zero lineality and one-sided rays only (resp3 §2.4)."),
 "CF07": (None, CFS, "not individually adjudicated; salvage row 5b", "Single exceptional trajectory."),
 "CF08": (None, CFS, "not individually adjudicated; salvage row 5b", "Single exceptional trajectory."),
 "CF09": (None, CFS, "not individually adjudicated; salvage row 5b", "Conditional limit statement; not re-derived by the audits."),
 "CF10": ("Supported", CFOBS, "not individually adjudicated; salvage §3.5", "Single exceptional trajectory."),
 "CF11": (None, "Conjecture / Exploratory (no proof or test in the repo)", "not adjudicated", "Conjecture status itself is not contested; listed for completeness."),
 "CF12": (None, "Conjecture / Exploratory (no proof or test in the repo)", "not adjudicated", "Conjecture status itself is not contested; listed for completeness."),
}
STATEMENT_OVERRIDE = {
 "EMP-AIEF14-02": "Under matched split-time phase configurations across 40 seeds (controlled exploratory analysis with fixed recorded design), "
   "the paired late-window contrast in Weighted_similarity_late is +0.064 [0.041, 0.089] (positive in 31/40 seeds), but P_mean_late is "
   "negative (-0.018 [-0.027, -0.009]) and the Retention_selected_late CI spans 0. No mediation (causal) claim is made.",
 "CF02": "A clipped row is strictly interior in the gated (node-strength-normalised) output at finite epsilon.",
 "IMPL-MODULAR-01": "On an identical host/libm environment, aief_modular reproduces monolithic AIEF_1_4_Twindow_sensitivity.py across all "
   "344 condition arrays with max_abs_diff = 0.000e+00; across distinct Linux glibc versions (2.36 vs a second Linux host with glibc 2.40), "
   "discrete topology arrays remain exact (0.0) while continuous 80k-step DDE trajectories differ by <= 4.405e-13.",
}
CAVEAT_OVERRIDE = {
 "IMPL-MODULAR-01": "Critical for CI design: cross-machine NPZ validation against archives from the second host requires explicit libm drift "
   "tolerance (1e-11) on continuous arrays while enforcing exact 0.0 on same-host comparisons and binary topology arrays.",
}
SCOPE_OVERRIDE = {"EMP-AIEF14-02": "Finite numerical observation", "EMP-AIEF14-03": "Finite numerical observation"}
S_SOURCE = "AIEF_1_4_superseded_claims.csv (hash-pinned, unedited); arena retirement, not contradicted by the audits"
S_EXTRA = {
 "S01": "CONFLICT: the replacement wording 'Memory is redundantly reconstructed' was itself struck by the audit (resp2 #4, line 18; "
        "resp1 §3 item 5). Use the EMP-AIEF14-01 audited wording instead.",
 "S02": "Retirement stands. Note: the replacement must not be read as 'projection' (gate is not a projection: resp3 #5, salvage row 4).",
 "S12": "'Resonance mode' is a repeated-root (Jordan) EMA term, not physical resonance (salvage §4 line 199).",
 "S15": "Also consistent with the 966-dimensional quarantine result (resp3 #8, §2.5).",
}
REJ_EXTRA = {
 "REJ-SPEC-02": "Cites aief_1_4_augmented_spectrum.py, whose 18-coordinate 'unique slow pole' verdict is quarantined (AUD-SLOWPOLE; resp3 #8).",
 "REJ-K3-04": "Audit's own K3 census: resp2 #2 (line 16) and resp3 #1 (line 22).",
}
HU = {"S01": 1, "S02": 2, "S03": 3, "S04": 4, "S05": 5, "S08": 6, "S09": 7, "S11": 8, "S10": 9, "S15": 10}
FP = {"S01": 1, "S02": 2, "S03": 3, "S04": 4, "S05": 5, "S08": 6, "S09": 7, "S10": 8, "S11": 9,
      "S12": 10, "S13": 11, "S14": 12, "S15": 13}

# ---- new rows: audit verdicts that had no row in the arena ledger -----------
A = "AI_AGENT_AUDITS_2026_10"
NEW = [
 ("AUD-CORR-0995", A, "Corr_physical ≈ 0.995 (AIEF-1.3 baseline) is specific to the repository's hand-picked natural frequencies; with random frequencies it is ~0.71 (uniform) and 0.59–0.63 (clustered). It is not a tautology, but it is dominated by persistence. The held-out target used by the audit was B_final > B_C, identical here to P_future > 0.5 in all 440 runs. Within-run edge-level prediction is driven largely by persistence of the split state, while the delay-history increment over the state-only model is small (ΔAUC ≈ +0.001–0.002). Across random-frequency seeds, Corr_physical does not predict persistence fraction at n=16 (AUC 0.457 vs 0.652).",
  "Supported", "Finite numerical observation", "AI Agent Audits/evidence/results/omega_random.json;AI Agent Audits/evidence/results/omega_multistab.json;AI Agent Audits/evidence/results/delay_heldout_analysis.json;ERRATA_2026-10-28.md",
  "Scope: chosen omega only; within-run edge-level prediction, not a cross-seed law.", "(was quoted unqualified as ~0.995)", "Supported (audit-qualified: chosen omega only)",
  "salvage §3 row 2 (line 96) + §3.2 (line 125); resp1 ledger #2-#3 (lines 15-16) + §3 item 3 (line 42); resp2 #6 (line 20)",
  "Statement = the 0.995 errata text (MERGE_CHECK Q5), also in ERRATA_2026-10-28.md E1. The brief's phrase 'near-circular' is the round-1 wording "
  "(audit.md H2, line 32) that was later corrected to 'not a tautology'. Re-run 2026-10-28: baseline Corr_physical 0.995217."),
 ("AUD-TOPO-OMEGA", A, "The persistent topology is largely set by the chosen frequencies: the closed-form rule R_pred(dw) > mu/(eta+mu) "
  "is an informative predictor (not a superset) of it, exact only for repo-omega no_delay; for generic omega selection is multistable.",
  "Supported", "Finite numerical observation", "AI Agent Audits/evidence/results/omega_random.json;AI Agent Audits/evidence/results/omega_multistab.json;AI Agent Audits/evidence/results/archived13_closedform.json", "Scope: N=12, repo parameters.",
  "(arena framed the topology as emergent from memory)", "Supported (audit-qualified)",
  "salvage §3 row 1 (line 95) + §3.1 (line 106) + §5 (i); resp1 ledger #1, #4 + §3 item 2 (line 41); audit.md H1",
  "Multistability on uniform random omega: mean pairwise Jaccard between seeds' final topologies 0.514; 1-4 distinct topologies per omega out of 4 seeds (salvage §3.1, line 121)."),
 ("AUD-GATE", A, "The capacity gate s_i = min(1, c/(q_i+eps)) is node-strength multiplicative normalisation. It is idempotent but it is "
  "not a metric, KL or Bregman projection onto the capacity set (no-go over the stated domain).",
  "Supported", "Conditional theorem", "AI Agent Audits/evidence/results/gate_idempotence.json;AI Agent Audits/AIEFS_audit_response_3.md §2.1",
  "Domain stated in resp3 §2.1.", "(arena/1.4 docs: 'projection', 'Bregman', 'entropy geometry')", "Supported (audit-derived); projection framing Rejected",
  "salvage §3 row 4 (line 100) + §3.4 (line 133); resp1 §3 item 7 (line 46); resp2 #1 (line 15) + §2.1; resp3 #5 (line 26) + §2.1 (line 35)",
  "Affects wording in CF02, S02, lineage rows 5-7, and HISTORIC_UNFOLDING terminology."),
 ("AUD-SCOPE-1.4", A, "AIEF-1.4 has two scopes: the split-state memory ablation is a 40-seed cohort result; the operator / cocycle / "
  "Duhamel / biorthogonal / controller-fiber pipeline is a single-seed case study (one exceptional seed, 1 of 40).",
  "Supported", "Finite numerical observation", "AI Agent Audits/AIEFS_salvage.md §3.5",
  "Do not generalise single-seed results to the cohort.", "(1.4 docs present the pipeline as the system's mechanism)",
  "Supported (audit scope ruling)",
  "salvage §3 row 5b (line 102) + §3.5 (line 139) + §5 plan item 8 (line 237); resp1 §6 Limits ('1.4 Duhamel pipeline not rerun on other seeds')",
  "Applies to lineage rows 14-32 and CF03-CF12."),
 ("AUD-SLOWPOLE", A, "[QUARANTINED] 'The EMA pole alpha is the unique slow pole' (18-coordinate augmented spectrum). The derivation is invalid: "
  "the 18-coordinate map is not a closed state (restore_state omits theta). The audit's proposal on the closed 966-dimensional state of the same "
  "replay gives NO: 10 rates lie in the gap (0.189328 x2, 0.252355 x5, 0.650378, 0.662045, 0.668921).",
  "Rejected", "Finite numerical observation", "aief_1_4_augmented_spectrum/augmented_spectrum_report.txt:28;AI Agent Audits/evidence/proposals/aief_1_4_full_state_spectrum.py;ERRATA_2026-10-28.md",
  "The audit labels its NO verdict a proposal (one replay, finite-difference, not a proof; resp3 line 105). Do not cite either the YES or the NO as a result. "
  "Limits of the 966-coordinate proposal (Arena AI review, 2026-10-28): (1) central differences at nonsmooth points (clipping, gate, endpoint minima, "
  "controller ties) give a generalized response matrix, not a Jacobian (the audit's own J+ vs J- differ by up to 0.49937); (2) the 500-step finite-time "
  "map's eigenvalues are not Floquet or equilibrium multipliers, so singular values are more defensible; (3) neutral phase-shift modes of the "
  "independently rotating components must be quotiented out before any 'slowest mode' claim; (4) block participation weights depend on the chosen "
  "coordinates; (5) only h = 1e-7 was used, so an amplitude sweep is needed. Status: evidence against the claimed spectral gap, not a "
  "branch-independent full-system spectrum; stays a proposal.",
  "(arena: Superseded / cited as a result; REJ-SPEC-02 rejected only the eps=1e-8 Jacobian)",
  'Quarantined — invalid derivation; do not cite. Audit proposal on the 966-dim state (one replay, finite-difference, not a proof) gives NO: 10 gap rates.', "resp3 #8 (line 29) + §2.5 (line 94) + §3 wording (line 112); evidence/proposals/augmented_spectrum_citations.md",
  "artifact_status is 'Rejected' because the verify_inventory.py vocabulary has no 'Quarantined' value (the derivation is withdrawn, not replaced, so "
  "'Superseded' was wrong). The report file keeps its pinned bytes; the caveat is ERRATA_2026-10-28.md E2. Numbers not edited."),
 ("AUD-RATELAW", A, "On complete, saturated, phase-locked components, for h in the unsigned-incidence controller kernel (row-sum-preserving edge kernel) K = ker A_J the exact one-step "
  "multiplier is lambda = (1 - gamma*dt) s_J, under conditions (a) gate on, (b) clamp x >= 0 inactive, (c) R does not respond within the step, "
  "(d) delta below the untied gaps (no controller change), (e) equal controlling scales s_i = s_J on J. Under the further ideal hypotheses R = 1 and "
  "row sum c at the controlling nodes, lambda_k = (1 - gamma*dt) c / (c + dt(k*eta - gamma*c) + eps); kappa_k = k*eta/c - 1/T_w is its "
  "dt, eps -> 0 limit. Checked on 374 resolved components: 264 two-sided fibers (lambda to 2.1e-8 relative, kappa to 2.1e-6 absolute) and "
  "110 all-tied K3s on one-sided controller-selection rays (lambda to 1.7e-7, kappa to 1.7e-5, 294 resolved rays). The observed ~2e-8 gap is "
  "unexplained (finite eps changes lambda by only ~1.6e-12; the audit says the gap is not isolated). Condition (c) holds automatically for a "
  "B-only perturbation: Engine v1 computes R from phase, history and EMA before B is updated, so a within-step R response is ruled out "
  "(ERRATA_2026-10-28.md E5). Remaining unverified candidates: finite-difference error, unequal controlling scales, finite-time departure "
  "from the ideal locked point, storage rounding. The maximum residual (2.04e-8) comes from a single component with a tiny "
  "finite-difference step (delta in [1e-9, 1e-8)); the other 263 well-resolved components agree within 2.1e-10, so finite-difference/rounding "
  "error is the most likely cause, and finite-time departure and unequal controlling scales are less likely. The gap stays unexplained "
  "until a step-size sweep is run.",
  "Supported", "Conditional theorem", "AI Agent Audits/evidence/results/rate_law_census_r4.json;AI Agent Audits/AIEFS_audit_response_3.md §2.2",
  "40 fixed seeds x 5 T_w; not independent replications. 32 poorly resolved two-sided fibers (rho = 2) agree only to lambda 4.8e-6 / kappa 4.8e-4.",
  "(stated more strongly in 1.4 docs)", "Supported (audit-derived, conditional)",
  "resp3 #1-#2 (lines 22-23) + §2.2 (line 41) + §3 wording (line 109); salvage row 5c (line 103); resp1 ledger #9-#10",
  "kappa is a spectral gap of a conditional operator whose value is fixed by parameters, not an emergent constant (resp1 #10). "
  "Condition (e), h in ker A_J, the closed form and both bound sets added 2026-10-28 (MERGE_CHECK Q1). "
  "2026-10-28 (Arena AI review of d041c69, verified against aief_experiment_engine_v1.py:779, :743-745, :790-794, :823, :833-838): "
  "resp3 line 62's candidate 'a within-step dependence of R on B' is ruled out by the update order; see ERRATA E5."),
 ("AUD-KAPPA-TW", A, "Per component, kappa_k(T_w) = k*eta/c - 1/T_w (k = number of controlling row edges, 2..5) matches the discrete "
  "rate within 5.3e-6 over 292 slow components (k=2: 1, k=3: 88, k=4: 24, k=5: 179) in 200 replays (160 bit-exact; max diff 2.5e-14), and the "
  "continuous form within 4.5e-4. 2*eta/c - 1/T_w (0.069182 at T_w = 17.503) is the k = 2 value and applies only to the single exceptional K3.",
  "Supported", "Conditional theorem", "AI Agent Audits/evidence/results/kappa_tw_summary.json",
  "Positive at all tested T_w; sign change below T_w ~7.9 (k = 2) is an untested prediction. Tighter bounds are in AUD-RATELAW.",
  "(1.4 lineage row 21: envelope 0.06913)", "Supported (audit-verified, conditional)",
  "evidence/results/kappa_tw_summary.json (by_k {2:1, 3:88, 4:24, 5:179}; max_abs_err vs discrete 5.26e-6; vs continuous 4.47e-4; twin-vs-frozen median 9.9e-6); resp1 §3 item 6 (line 45); resp2 #2 (line 16) + §2.3 (line 40)",
  "The kappa_tw_summary field 'fully saturated no slow channel = 114' is superseded by the controller-kernel census (resp2 #2; AUD-CYCLE-KERNEL). "
  "Per-k form replaces the earlier single 2*eta/c statement on 2026-10-28 (MERGE_CHECK Q1)."),
 ("AUD-FROZEN-TOPO", A, "After the split, 0 of 29,040 edges change threshold status, 0 of 29,040 have non-binary P_future, and 0 have a "
  "P_future label that differs from the split-state label, so B_split predicting the final topology is expected.",
  "Supported", "Finite numerical observation", "AI Agent Audits/evidence/results/frozen_topology_check.json",
  "40 seeds; finite horizon. Continuous weights may still move.", "(new)", "Supported (audit-verified)",
  "resp3 #4 (line 25) + §3 wording (line 111)", "Explains B_split AUC 1.0 as predictive, not causal."),
 ("AUD-DELAY", A, "Delay is not necessary but not inert: in sampled ensembles the delayed condition gave more distinct four-seed final "
  "topologies (a sample-diversity statistic, not a basin count).", "Supported", "Finite numerical observation", "AI Agent Audits/evidence/results/delay_paired_runs.json;AI Agent Audits/evidence/results/delay_heldout_analysis.json",
  "No delay-specific topology signature on random omega.", "(earlier wording 'delay increases multistability')", "Supported (audit wording)",
  "resp2 #5 (line 19); resp1 §3 item 4 (line 43)", "Replaces the struck 'increases multistability' wording."),
 ("AUD-K3", A, "Strict K3 components have zero lineality and one-sided controller-selection rays; they are not eigenmodes. A two-sided fiber "
  "exists only for the exceptional resolved K3.", "Supported", "Conditional theorem", "AI Agent Audits/evidence/results/kappa_cycle_kernel.json;AI Agent Audits/evidence/results/rate_law_census_r4.json",
  "Equal edge weights assumed where stated.", "(1.4 docs: spectral/eigenmode language for K3)", "Supported (audit-derived)",
  "resp3 #3 (line 24) + §2.4 (line 86); resp2 #2 (line 16) + §2.4 (line 60)", "Retires 'spectrally silent'/'no slow mode' phrasing."),
 ("AUD-TIES", A, "For an all-tied K_n (k = n - 1) with EQUAL EDGE WEIGHTS, the one-sided gate derivative has nonadditivity 1/sqrt(2k(k-1)) "
  "and odd defect sqrt(2/(k+1)); these ratios are derived, not empirical. They are not universal tied-clique formulas: for n >= 4 equal row sums do "
  "not imply equal edges, and an unequal-edge K4 (edge ratio 0.3 : 0.2 : 0.1, equal row sums) gives nonadditivity 0.2003 vs formula 0.2887 and odd "
  "defect 0.7254 vs 0.7071. The figures depend on which pair of adjacent edges is perturbed (other pairs: 0.2627 / 0.7254, "
  "0.3046 / 0.7140), and the unequal-edge state is not a fixed point of the ideal gate (max one-step change 2e-4), so it refutes "
  "universality but is not a fixed-point counterexample. For K3, equal row sums force equal edges.", "Supported", "Conditional theorem",
  "AI Agent Audits/AIEFS_audit_response_3.md §2.3", "Equal edge weights required (hypothesis, not a consequence of the tie). Replay "
  "components (373 resolved all-tied) agree to <= 5.8e-5 relative, so they are close to equal-edge; deviations not decomposed.",
  "(were reported as observed ratios)", "Supported (audit-derived)",
  "resp3 #3 (line 24) + §2.3 (lines 66, 83-84)", "Equal-edge hypothesis and the K4 counterexample made explicit 2026-10-28 (Arena AI review)."),
 ("AUD-REPRO13", A, "AIEF-1.3 reproduction: 500/500 runs bit-exact on the 7 arrays and 4 headline scalars; 78/500 bit-exact on all 38 keys "
  "(the rest differ in derived scalars by <=4.9e-15 abs).", "Supported", "Implementation identity", "AI Agent Audits/evidence/results/repro13.json",
  "Same machine class.", "(round-1 wording '500/500 bit-for-bit')", "Supported (audit-corrected wording)", "resp2 #8 (line 22); resp1 §3 item 1 (line 40)", ""),
 ("AUD-REPRO-B2A95", A, "Run b2a95dfbfbe3 reproduces the official run 5a9f093a2fe0 from the committed code (repository commit 6b49a7b): "
  "all 40 seeds; max absolute float difference 6.7e-16 (tolerance 1e-12); NaN patterns identical.", "Supported",
  "Implementation identity", "AI Agent Audits/evidence/reproductions/b2a95dfbfbe3_REPRODUCTION.md;AI Agent Audits/evidence/reproductions/compare_b2a95dfbfbe3.log",
  "One run hash; environment numpy 2.5.4, pandas 3.0.6, python 3.13.5 (from the log header).", "(new)",
  "Supported (audit-verified)", "evidence/reproductions/b2a95dfbfbe3_REPRODUCTION.md (line 7) + (line 63) + compare_b2a95dfbfbe3.log", ""),
 ("AUD-NOVELTY", A, "Novelty of the AIEF results is not established either way; the ingredients (delayed Kuramoto, Hebbian plasticity, "
  "normalisation) are prior art.", "Incomplete", "Conjecture", "AI Agent Audits/AIEFS_salvage.md §2", "First-pass literature search only.",
  "(project docs imply new mathematics)", "Not established (audit)", "resp1 ledger #12 (line 25) + §3 item 9 (line 48); salvage §2 (line 71)",
  "A proper literature review is an open owner decision."),
 ("AUD-LABEL", A, "Audit analyses are 'controlled exploratory analyses with a fixed recorded design'; nothing in the repo was preregistered. "
  "This is a labelling rule for the audit's own analyses, not a numerical result.",
  "Supported", "Finite numerical observation", "AI Agent Audits/AIEFS_audit_response_2.md",
  "Labelling rule only; applies to the audit analyses and to EMP-AIEF14-02/03.", "(round-2 'confirmatory')",
  "Supported (labelling rule; scope = audit analyses, not a result)", "resp2 #7 (line 21)",
  "evidence_scope is 'Finite numerical observation' only because the verify_inventory.py vocabulary has no labelling/policy value; it was "
  "'Implementation identity', which was wrong (MERGE_CHECK minor fix). Arena's evidence_scope 'Controlled experimental result' means a "
  "randomised multi-seed design, not preregistration."),
 ("AUD-HELDOUT-LABEL", A, "The audit's held-out prediction target was B_final > B_C, not P_future > 0.5. The two labels are identical in all 440 "
  "runs (0 of 29,040 edges differ; no P_future within 1e-6 of 0.5), so the AUC / log-loss tables hold for both. P_future is binary except "
  "under no_mu, so per-run 'Pearson' correlations with it are point-biserial.",
  "Supported", "Finite numerical observation", "AI Agent Audits/evidence/results/delay_heldout_analysis.json",
  "Label identity holds on these 440 runs only.", "(round-1 table said 'P_future > 0.5')", "Supported (audit-verified)",
  "resp2 #6 (line 20)", "Ledger row added 2026-10-28 (MERGE_CHECK minor fix)."),
 ("AUD-CYCLE-KERNEL", A, "At ties the capacity gate is piecewise linear and not differentiable, so the round-2 central-difference matrix was "
  "not a Jacobian. The correct object is the one-step multiplier on the controller kernel K = ker A_J (see note on naming); for an all-tied K_n, "
  "dim K = m - n = n(n-3)/2 (K3: 0, K4: 2, K5: 5, K6: 9), checked on 373/373 all-tied complete components; in 200 replays "
  "(406 components) 292 agree with the slow multiplier, max relative difference 4.5e-4.",
  "Supported", "Conditional theorem", "AI Agent Audits/evidence/results/kappa_tw_summary.json;AI Agent Audits/AIEFS_audit_response_2.md §2.2-§2.3",
  "Conditional on saturation, phase-locking and the tie pattern; K3 has no two-sided fiber (see AUD-K3).", "(round-2 'Jacobian' wording)",
  "Supported (audit-derived, conditional)", "resp2 #2 (line 16) + §2.2 (line 38) + §2.3 (line 40)",
  "Ledger row added 2026-10-28 (MERGE_CHECK minor fix). Tighter round-4 census: AUD-RATELAW. Naming (2026-10-28, Arena AI review): "
  "the claim ID keeps 'CYCLE-KERNEL' because other files reference it, but K is not the graph cycle space. It is the kernel of the "
  "UNSIGNED incidence matrix (row-sum-preserving edge kernel), of dimension m - n for a non-bipartite K_n, whereas the cycle space "
  "(oriented incidence) has dimension m - n + 1 (K4: 2 vs 3). The audit files' 'cycle kernel' wording is kept (pinned); see ERRATA E6."),
 ("LEAN-R4", A, "Round-4 Lean package lean/AIEFProofs (toolchain leanprover/lean4:v4.33.1; modules Basic, ControllerFiber, "
  "ControllerFiberProjector, ControllerFiberQuotient, CompleteGraphIncidence, Smoke, imported by AIEFProofs.lean) builds; check_lean.sh "
  "audited 115 project declarations using only the standard axioms propext, Classical.choice, Quot.sound; 0 sorry/admit markers in 7 files.",
  "Supported", "Formalized theorem", "lean/AIEFProofs/check_lean.sh;lean/AIEFProofs/AIEFProofs.lean;AI Agent Audits/evidence/logs/lean_r4/summary.txt",
  "The formal statements are linear-algebra / incidence facts about the controller fiber; they say nothing about the dynamics (see LEAN-CF-01).",
  "(new)", "Supported (audit-run build; RESULT PASS)", "evidence/logs/lean_r4/summary.txt",
  "Ledger row added 2026-10-28 (MERGE_CHECK minor fix). The 'All rights reserved ... Released under Apache 2.0' source headers are the standard Mathlib form, not a licence conflict. "
  "After the audit run, Smoke.lean (narrow imports instead of 'import Mathlib') and Basic.lean (header only) were changed and "
  "AIEF_LEAN_SOURCE_SHA256SUMS.txt updated (ERRATA E7). Re-run after that change: cached build by Auditor Seat 002 at 886daf6: 7/7 PASS, 115 declarations, 3 allowed axioms, 0 warnings, 1,591 build jobs (earlier cached run at 11de659: PASS, 12 warnings, all in Smoke.lean)."),

 # ---- Post-push review items, 2026-10-28 (branch work/post-push-1; local, not pushed, not audited) ----
 # These are NOT audit-round verdicts. Findings use audited_status 'Finite numerical observation' (not audited) or 'Supported' (audit evidence)
 # at the stated scope; AUD-TIMESTEP and AUD-B-SCAFFOLD are OPEN ITEMS ('Not established'), not findings
 # against existing claims.
 ("AUD-V4-HELDEVENT", "AIEF_1_4_TWINDOW_SENSITIVITY",
  "Blocker for citing Analysis v4 held-event rows at exact-duration boundaries (the fixed_physical_17p5 held events): "
  "_held_index (AIEF_1_4_Twindow_sensitivity_analysis_v4.py:555) "
  "uses searchsorted(times, times[index] + duration, side='left'). Floating-point rounding can put times[index] + duration "
  "just above the saved sample that is exactly `duration` later, so an event held exactly the required duration is rejected. "
  "On a synthetic indicator on v4's own saved grid (spacing 0.5), 32 of the 605 valid start positions held exactly 17.5 are missed "
  "(first: t = 16.01 to 33.51, where v4 effectively requires 18.0); misses also occur on np.arange(0, T, dt) grids with dt = 0.01, 0.05, 0.1.",
  "Supported", "Finite numerical observation",
  "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/AIEF_1_4_Twindow_sensitivity_analysis_v4.py;"
  "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/AIEF_1_4_Twindow_sensitivity_analysis_v4_1.py;"
  "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/tests/test_v4_1_held_event.py",
  "Synthetic indicator series only. Whether any saved v4 output row changes was NOT checked: the v4.1 candidate "
  "(tolerance 1e-6 x grid step on the end check) is unaudited and has not been run on real trajectories. "
  "Only grid-multiple hold durations (fixed_physical 17.5) can be hit; the T_window-nominal holds (17.5029 x rho) are not grid multiples, "
  "so they and the non-held (first-crossing / sustained) estimands are not affected by this defect. 605 = every start whose 17.5 hold ends "
  "on or before the last saved sample; the last start is held correctly by v4 (the test covers it).",
  "(new)", "Finite numerical observation (post-push review, synthetic test; not audited)",
  "not from audit rounds 1-4; post-push review 2026-10-28; tests/test_v4_1_held_event.py",
  "v4 is hash-pinned (registry/artifacts.csv ART-0063) and is not edited; the candidate fix is a new file. "
  "Until v4.1 is audited, or the affected fixed_physical_17p5 held rows are shown unchanged, cite those EMP-AIEF14-03 held-event "
  "numbers with this caveat."),
 ("AUD-V4-RECOVERY-WORDING", "AIEF_1_4_TWINDOW_SENSITIVITY",
  "Analysis v4 reports first-crossing and held events as 'recovery', but _first_index / _held_index return index 0 when the "
  "signal is already at or above target at the first saved sample, so a 'recovery' event can be retention (never dropped). "
  "Retention (held from the first saved sample without dropping) and recovery (dropped below, then re-crossed and held) "
  "should be worded and reported separately.",
  "Supported", "Finite numerical observation",
  "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/AIEF_1_4_Twindow_sensitivity_analysis_v4.py;"
  "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/AIEF_1_4_Twindow_sensitivity_analysis_v4_1.py;"
  "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/tests/test_v4_1_held_event.py",
  "Definition / wording finding from reading v4 (lines 531-558) and a synthetic classification test. How many saved v4 "
  "events are retention rather than recovery was not counted. The v4.1 candidate adds event types held_retention and "
  "held_recovery and a held_classification column; it is unaudited.",
  "(new)", "Finite numerical observation (post-push review; code reading plus synthetic test; not audited)",
  "not from audit rounds 1-4; post-push review 2026-10-28",
  "Applies to the 'recovery' wording around EMP-AIEF14-03 outputs; the run outputs themselves are not changed."),
 ("AUD-MODULAR-ORACLE", "PLATFORM_V1_V4",
  "The modular platform is not oracle-certified by the tests in this repository: tests_modular/test_twindow_oracle_equivalence.py "
  "is skipped unless AIEF_MODULAR_RUN is set and a pre-generated runs/b57562a8ee77 directory is supplied. The slow engine-comparison "
  "test (tests_modular/test_twindow_one_condition.py) needs AIEF_RUN_SLOW_TESTS=1 and the repository root on PYTHONPATH, and is "
  "otherwise skipped; pytest.ini sets pythonpath = ., so the rest of the suite imports without PYTHONPATH.",
  "Supported", "Implementation identity",
  "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/tests_modular/test_twindow_oracle_equivalence.py;README.md;REPRODUCING.md;"
  "audits/engineering/PATH_AND_LOCK_DEPENDENCY_AUDIT.md",
  "Re-run 2026-10-28 in the platform directory: default `pytest -q` gives 40 passed, 2 skipped; with AIEF_RUN_SLOW_TESTS=1 and the "
  "repository root on PYTHONPATH, 41 passed, 1 skipped (only the oracle test skipped). Neither run re-tests the 344-array max_abs_diff = 0 identity of IMPL-MODULAR-01; "
  "that identity rests on the arena record until the oracle test is run with the certification directory.",
  "(new)", "Finite numerical observation (post-push review; oracle test skipped by default; not audited)",
  "not from audit rounds 1-4; post-push review 2026-10-28; related: resp2 Provenance gaps item 2 (line 146)",
  "Qualifies IMPL-MODULAR-01; does not contradict it. Slow-test PYTHONPATH / AIEF_RUN_SLOW_TESTS setting: README.md (modular platform tests), "
  "REPRODUCING.md §3, PATH_AND_LOCK_DEPENDENCY_AUDIT.md item 3."),
 ("AUD-TIMESTEP", A,
  "OPEN ITEM: timestep accuracy is unverified. No timestep/safeguard convergence study (for example dt, dt/2, dt/4) has been "
  "run for Engine v1 or the modular platform; reported trajectories, rates and topologies hold for the dt used (0.01) only.",
  "Incomplete", "Conjecture",
  "AIEF_1_4_FORWARD_PLAN.md;AI_AGENT_HANDOFF_PROMPT.md",
  "Open item, not a finding against any existing claim. FORWARD_PLAN §2 'Timestep/safeguard study' (line 360) and "
  "HANDOFF prompt line 527 list the study as future work.",
  "(new)", "Not established (open item; no timestep study run)",
  "not from audit rounds 1-4; post-push review 2026-10-28",
  "What would test it: a separately versioned, regenerated dt sweep reporting topology agreement and trajectory "
  "differences across dt. Related: the ~2e-8 rate-law gap (AUD-RATELAW) also waits on a step-size sweep."),
 ("AUD-B-SCAFFOLD", A,
  "OPEN ITEM: 'B is a conditional (continuous-weight) scaffold' is audit wording (resp1 #6, line 19; resp2 #4). The conditions "
  "under which B acts as a scaffold have not been stated as a testable claim or tested.",
  "Incomplete", "Conjecture",
  "AI Agent Audits/AIEFS_audit_response.md;AI Agent Audits/AIEFS_audit_response_2.md",
  "Open item, not a finding against EMP-AIEF14-01: the reset_B reconstruction result and its audit-qualified wording stand.",
  "(new)", "Not established (open item; wording only, no test)",
  "resp1 #6 (line 19); resp2 #4 (line 18); post-push review 2026-10-28",
  "What would test it: state which state variables are held fixed and which B perturbations are applied, then run an "
  "ablation that varies B with phase/history/EMA fixed and reports the effect on later topology."),
 ("AUD-CORR-0995-SCOPE", A,
  "Corr_physical ~0.995 is scoped to the repository's fixed natural-frequency vector. First pass with random omega: mean "
  "~0.71 (uniform; 0.711/0.712, 20/20 and 40/40 runs defined) and 0.59-0.63 (clustered; 0.588/0.634, means over the defined runs only: "
  "15/20 no_delay and 30/40 baseline; source AI Agent Audits/evidence/logs/omega_random.log, results/omega_random.json, "
  "AIEFS_salvage.md §3.1). Replication (delay_heldout_analysis.json, "
  "per-run point-biserial corr(P, past R), mean / median): uniform baseline 0.745 / 0.978 and no_delay 0.747 / 0.986 "
  "(60/60 runs defined); clustered baseline 0.553 / 0.449 (37/60 defined) and no_delay 0.531 / 0.379 (39/60 defined).",
  "Supported", "Finite numerical observation",
  "AI Agent Audits/evidence/results/delay_heldout_analysis.json;AI Agent Audits/evidence/results/frozen_topology_check.json;"
  "AI Agent Audits/evidence/logs/omega_random.log;AI Agent Audits/evidence/results/omega_random.json;"
  "AI Agent Audits/AIEFS_salvage.md;AI Agent Audits/AIEFS_audit_response.md",
  "Scope: fixed repository omega only; the random-omega numbers are within-run correlations, not a cross-seed law. Pinned "
  "documents are not edited. The inline side branch fix/corr-0995-scope (and its v2 revision), which edits the pinned "
  "HANDOFF prompt / HISTORIC_UNFOLDING, is not being merged (owner decision 2026-10-28, option A); ERRATA_2026-10-28.md E9 is the record of the scope note.",
  "(new)", "Supported (audit evidence re-read; scope note)",
  "resp1 #3 (line 16) and §3 item 3 (line 42); §5 per-run correlations (lines 73-75); evidence/results/delay_heldout_analysis.json; see AUD-CORR-0995",
  "Extends AUD-CORR-0995 and ERRATA E1 with the replication numbers; scoped wording for the pinned docs is in ERRATA E9. No number in a pinned file changes."),
 ("AUD-RESP1-UNIFORM", A,
  "Erratum: AIEFS_audit_response.md §3 item 3 (line 42) says past R 'adds over Δω-only for uniform and repo ω'. For uniform "
  "no_delay this holds only on log loss (0.240 vs 0.396); on held-out AUC past R is worse (0.850 vs 0.883). For uniform "
  "baseline it holds on both (AUC 0.844 vs 0.833; log loss 0.261 vs 0.446).",
  "Supported", "Finite numerical observation",
  "AI Agent Audits/AIEFS_audit_response.md;AI Agent Audits/evidence/results/delay_heldout_analysis.json;ERRATA_2026-10-28.md",
  "The numbers are the audit's own (held-out table, lines 66-69; point2_heldout in the JSON). Only the summary wording at line 42 is corrected.",
  "(new)", "Supported (audit's own numbers; wording corrected in ERRATA E8)",
  "resp1 §3 item 3 (line 42) vs §5 table (lines 68-69); evidence/results/delay_heldout_analysis.json",
  "AIEFS_audit_response.md is hash-pinned (audit_manifest.json) and is not edited; the correction lives in ERRATA_2026-10-28.md E8."),
]
O = "HISTORICAL_PROJECT_ORIGINS"
UNS = "Speculative / untested origin hypothesis"
SSRH_SRC = "not adjudicated by any audit; only salvage §4 (line 199) notes the SSRH acronym conflates EMA 'resonance' with physical resonance; audit.md line 127 notes a flip-flopped SSRH verdict in a reviewer"
SSRH = [
 ("SSRH-ORIG-01", "Delay-coupled cross-feedback gives parametric amplification up to 10^8.",
  "Project Origins/SSRH stuff.pdf p.1:5, p.2:1, p.3:20 (self-contradiction p.7:15, p.8:20: Lyapunov >0 in 20-25% of runs); "
  "Project Origins/SSH history part 002461.pdf p.1:21, p.2:5, p.3:18, p.4:21 (AI self-critique p.42:36)"),
 ("SSRH-ORIG-02", "QBO imprints in sunspot records correlate with Rieger periods at r = 0.92 [0.84, 0.97], dAIC = 12.4.",
  "Project Origins/SSRH stuff.pdf p.1:37, p.3:1, p.5:19, p.6:33; Project Origins/SSH history part 002461.pdf p.3:40, p.11:17, p.24:14"),
 ("SSRH-ORIG-03", "60Fe deposits show r = 0.85 Fourier correlation with tidal beats.",
  "Project Origins/SSRH stuff.pdf p.3:41, p.5:34; Project Origins/SSH history part 002461.pdf p.11:14, p.24:14"),
 ("SSRH-ORIG-04", "Superionic ice phases correlate with piezoelectricity at r = 0.92.",
  "Project Origins/SSRH 001 stuff.pdf p.401:2, p.402:29, p.406:4, p.450:14 (same r value as SSRH-ORIG-02 for an unrelated quantity)"),
 ("SSRH-ORIG-05", "QBO-sunspot r = 0.75 [0.62, 0.85]; dAIC = 8.2 favouring a tidal model.",
  "Project Origins/SSRH stuff.pdf p.5:7, p.5:10, p.6:25, p.6:30"),
 ("SSRH-ORIG-06", "Faraday rotation measures (RM ~10-100 rad m^-2; 'RM variances ~20%') probe resonantly amplified fields.",
  "Project Origins/SSRH stuff.pdf p.1:13, p.5:10; Project Origins/SSH history part 002461.pdf p.3:31, p.11:17"),
 ("SSRH-ORIG-07", "SINDy hypergraph inference reaches F1 ~ 0.88.",
  "Project Origins/SSH history part 002461.pdf p.11:17; the same document says F1 is on controlled synthetic data only (p.46:22)"),
]
SSRH_NOTE = ("Numbers appear only in AI-chat text. Researcher 001 found no script, notebook or data file in the repo that computes them "
             "(git grep for sunspot/Rieger/Faraday/60Fe over *.py, *.ipynb, *.csv on 2026-10-28). Page:line = PDF page : line within page "
             "of pdftotext output. Owner decision 2026-10-28: kept as an origin and possible future direction, not "
             "retired (nothing was tested and failed). Not cited as a result until a testable form is stated and a test is run; can then be "
             "promoted. artifact_status 'Incomplete' / evidence_scope 'Conjecture' are the nearest verify_inventory.py vocabulary values.")
SSRH_TEST = {
 "SSRH-ORIG-01": "What would test it: testable form not yet stated. Needs the model equations and parameters, then a simulation reporting gain vs parameters with Lyapunov exponents (the source itself reports Lyapunov > 0 in 20-25% of runs).",
 "SSRH-ORIG-02": "What would test it: name the public QBO index and sunspot series, the band filter and lag; compute r with a phase-randomised surrogate null and the stated dAIC model comparison in a committed script.",
 "SSRH-ORIG-03": "What would test it: testable form not yet stated (which 60Fe record, which tidal-beat periods). Then a Fourier correlation against a spectrum-matched surrogate null.",
 "SSRH-ORIG-04": "What would test it: testable form not yet stated; which quantities and which data source are correlated is not specified.",
 "SSRH-ORIG-05": "What would test it: same pipeline as SSRH-ORIG-02; reconciling r = 0.75 here with r = 0.92 there is part of the test.",
 "SSRH-ORIG-06": "What would test it: testable form not yet stated; needs a quantitative RM-variance prediction from the model to compare with a published RM catalogue.",
 "SSRH-ORIG-07": "What would test it: commit the synthetic-data generator and the SINDy hypergraph inference script; report F1 over fixed seeds (the source says synthetic data only).",
}

NEW_IDS = {t[0] for t in NEW}

def main():
    rows = list(csv.DictReader(open(CLAIMS, newline="", encoding="utf-8")))
    have = {r["claim_id"] for r in rows}
    out = []
    for r in rows:
        cid = r["claim_id"]
        if cid.startswith(("AUD-", "SSRH-ORIG-")) or cid in NEW_IDS:
            continue  # rebuilt below (idempotence)
        prior = r.get("prior_status") or f'{r["artifact_status"]} / {r["evidence_scope"]}'
        r["prior_status"] = prior
        r["artifact_status"] = prior.split(" / ")[0]
        legacy = ""
        if cid in EXISTING:
            st, aud, src, note = EXISTING[cid]
            if st:
                r["artifact_status"] = st
            if cid in STATEMENT_OVERRIDE: r["statement"] = STATEMENT_OVERRIDE[cid]
            if cid in CAVEAT_OVERRIDE: r["scope_boundary_and_caveat"] = CAVEAT_OVERRIDE[cid]
            if cid in SCOPE_OVERRIDE: r["evidence_scope"] = SCOPE_OVERRIDE[cid]
        elif cid.startswith("S"):
            aud, src, note = "Retired / Superseded (unchanged)", S_SOURCE, S_EXTRA.get(cid, "")
            refs = [f"AIEF_1_4_superseded_claims.csv id {cid}"]
            if cid in HU: refs.append(f"AIEF_HISTORIC_UNFOLDING.md §XIX item {HU[cid]}")
            if cid in FP: refs.append(f"AIEF_1_4_FORWARD_PLAN.md §II item {FP[cid]}")
            legacy = "; ".join(refs)
        elif cid.startswith("REJ-"):
            aud, src, note = "Rejected (unchanged)", "arena rejection; not contradicted by the audits", REJ_EXTRA.get(cid, "")
        else:
            aud, src, note = ND, "no row mapping", ""
        r.update(audited_status=aud, audit_source=src, reconciliation_note=note, legacy_list_refs=legacy)
        out.append(r)
    for (cid, sid, stmt, st, sc, art, cav, prior, aud, src, note) in NEW:
        out.append(dict(claim_id=cid, study_id=sid, statement=stmt, artifact_status=st, evidence_scope=sc,
                        supporting_artifacts=art, scope_boundary_and_caveat=cav, prior_status=prior,
                        audited_status=aud, audit_source=src, reconciliation_note=note, legacy_list_refs=""))
    for cid, stmt, cites in SSRH:
        note = SSRH_NOTE + " " + SSRH_TEST[cid]
        out.append(dict(claim_id=cid, study_id=O, statement="[ORIGIN CLAIM] " + stmt, artifact_status="Incomplete",
                        evidence_scope="Conjecture", supporting_artifacts=cites,
                        scope_boundary_and_caveat="Pre-AIEF origin material; physical claim, not part of the AIEF model.",
                        prior_status="(no row; study HISTORICAL_PROJECT_ORIGINS was Exploratory / Conjecture)",
                        audited_status=UNS, audit_source=SSRH_SRC, reconciliation_note=note, legacy_list_refs=""))
    with open(CLAIMS, "w", newline="", encoding="utf-8") as f:
        for r in out:
            r["audited_status"], r["audited_qualifier"] = split_audited(r["audited_status"])
        cols = BASE_COLS + NEW_COLS
        cols.insert(cols.index("audited_status") + 1, "audited_qualifier")
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader(); w.writerows(out)
    print(f"claims.csv: {len(out)} rows ({len(rows)} input incl. any prior AUD/SSRH rows)")
    build_lineage()

# 2026-10-28: audited_status holds exactly one label from the "## Status vocabulary" block in
# registry/README.md (checked by CI); the free-text remainder goes in audited_qualifier.
AUDITED_LABELS = ["Speculative / untested origin hypothesis", "Controlled exploratory", "Conjecture / Exploratory",
                  "Finite numerical observation", "Not established", "Retired / Superseded", "Quarantined",
                  "Supported", "Exploratory", "Rejected"]

def split_audited(v):
    for lab in AUDITED_LABELS:
        if v == lab:
            return lab, ""
        if v.startswith(lab):
            rest = v[len(lab):].strip()
            if rest.startswith("(") and rest.endswith(")") and rest.count("(") == 1:
                rest = rest[1:-1]
            return lab, rest.lstrip(":,;—/ ").strip()
    raise ValueError(f"audited_status not in vocabulary: {v!r}")

def lineage_verdict(seq):
    if seq == 1:
        return ("Supported (audit-qualified, reworded)", "resp2 #4 (line 18); resp3 #4 (line 25)",
                "Use EMP-AIEF14-01 audited wording. 'Future edge identity is required for maintenance' was not adjudicated.")
    if seq == 2:
        return ("Superseded wording", "resp2 #4 (line 18); resp1 §3 item 5 (line 44)",
                "'State channels are redundant' is the wording the audit struck. Replace with EMP-AIEF14-01 audited wording.")
    if seq in (3, 4):
        return (ND, "not adjudicated", "40-seed cohort descriptive result.")
    if seq in (5, 6, 7):
        return ("Framing retired; replay facts " + ND, "salvage row 4 (line 100) + §3.4; resp3 #5 + §2.1",
                "Projection / mirror / entropy-geometry / 'soft regulariser' framing is retired: the gate is multiplicative normalisation, not a projection. "
                "The underlying numerical replay facts were not re-checked.")
    if seq == 8:
        return (ND + " (scope consistent with audit)", "salvage §3.5 (line 139)",
                "Audit agrees the exceptional seed is 1 of 40; the stationarity numbers were not re-checked.")
    if seq in (9, 10, 11, 12, 13):
        extra = {12: " Consistent with S06.", 13: " Related audit census: resp2 #2 (line 16), resp3 #1 (line 22) (264 two-sided + 110 one-sided K3 rays)."}.get(seq, "")
        return (ND, "not individually adjudicated", "40 split states." + extra)
    base = ("Single-seed case study (scope per audit); result " + ND,
            "salvage §3.5 (line 139) + §5 plan item 8 (line 237); resp1 §6 Limits")
    notes = {
        15: "Winner map: see CF05; S04.",
        18: "Augmented-state pipeline was not re-run on other seeds (resp1 §6).",
        19: "Duhamel pipeline not re-run on other seeds (resp1 §6).",
        20: "Duhamel pipeline not re-run on other seeds (resp1 §6).",
        21: "The 0.06913 envelope equals the k = 2 value kappa_2 = 2eta/c - 1/T_w = 0.069182 (conditional closed form; see AUD-KAPPA-TW, AUD-RATELAW; resp2 §2.3 gives 0.0691196 vs cf 0.0691217 at T_w 17.50). 'Nearly rank one' not adjudicated.",
        22: "'Spectral gap' = gap of a conditional operator fixed by parameters (resp1 #10). See S09.",
        29: "'Resonance mode' = repeated-root EMA term, not physical resonance (salvage §4 line 199). See S12.",
        30: "See S13.", 31: "'Resonant tracking' naming caveat as row 29.", 32: "See S18.",
    }
    return base + (notes.get(seq, "Single exceptional seed."),)

def build_lineage():
    rows = list(csv.DictReader(open(LINEAGE_IN, newline="", encoding="utf-8")))
    cols = ["sequence", "analysis_id", "scope", "evidence_class", "prior_freeze_status", "principal_result_short",
            "superseded_claim", "audited_status", "audit_source", "reconciliation_note"]
    with open(LINEAGE_OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n"); w.writeheader()
        for r in rows:
            seq = int(r["sequence"]); aud, src, note = lineage_verdict(seq)
            w.writerow(dict(sequence=seq, analysis_id=r["analysis_id"], scope=r["scope"], evidence_class=r["evidence_class"],
                            prior_freeze_status=r["freeze_status"], principal_result_short=r["principal_result"][:200],
                            superseded_claim=r["superseded_claim"], audited_status=aud, audit_source=src, reconciliation_note=note))
    print(f"lineage_reconciliation.csv: {len(rows)} rows (source file left unedited: {LINEAGE_IN.relative_to(ROOT)})")

if __name__ == "__main__":
    main()
