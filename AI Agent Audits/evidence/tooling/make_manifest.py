"""Round 3 (2026-10-24), updated round 4 (2026-10-25): regenerate evidence/audit_manifest.json (successor of tooling/round2/make_manifest_v2.py).
Run from the AIEFS repo root:  python "AI Agent Audits/evidence/tooling/make_manifest.py"
Hashes the repo inputs the evidence scripts read (relative to the current directory = repo root), lists every finding
with its command, outputs, design type and basis, and hashes every published file under "AI Agent Audits/" except the
manifest itself. Check the result with:  python "AI Agent Audits/evidence/verify_manifest.py" [--inputs]"""
import hashlib, json, os, glob, sys
from pathlib import Path
P = Path(__file__).resolve().parents[2]; E = P / "evidence"; R = Path.cwd()
if not (R / "AIEF_1_3_falsification_updated.py").exists(): sys.exit("run from the AIEFS repo root")
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
def agg(files):
    h = hashlib.sha256()
    for f in sorted(files): h.update(f"{os.path.relpath(f, R)} {sha(f)}\n".encode())
    return h.hexdigest()
single = ["AIEF_1_3_falsification_updated.py", "aief_experiment_engine_v1.py", "AIEF_1_4_Twindow_sensitivity.py",
  "AIEF_1_4_OPERATOR_THEORY_MANUSCRIPT.md", "AI_AGENT_HANDOFF_PROMPT.md",
  "runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz", "runs/5a9f093a2fe0/manifest.json",
  "runs/b57562a8ee77/AIEF_1_4_Twindow_sensitivity_b57562a8ee77_branch_diagnostics.npz",
  "aief_1_4_scalar_spectral_gap_reduction/scalar_spectral_gap_report.txt",
  "aief_1_4_matched_phase_memory_ablation/analysis_manifest.json",
  "test_output/analysis_manifest.json", "test_output/matched_phase_paired_contrasts.csv", "test_output/matched_phase_seed_status.csv",
  "aief_1_4_augmented_spectrum.py", "AIEF_1_4_stationarity_perturbation_analysis_updated.py",
  "AIEF_1_4_component_controller_audit.py", "AIEF_1_4_augmented_tangent_cocycle_analysis.py",
  "aief_1_4_augmented_spectrum/augmented_spectrum_report.txt",
  "lean/AIEFProofs/AIEFProofs.lean", "lean/AIEFProofs/AIEFProofs/ControllerFiber.lean",
  "lean/AIEFProofs/lean-toolchain", "lean/AIEFProofs/lake-manifest.json"]
inputs = {f: sha(R / f) for f in single if (R / f).exists()}
missing = [f for f in single if not (R / f).exists()]
for run in ["c3da1ac707bf", "73dca37cf93f"]:
    fs = glob.glob(str(R / f"runs/{run}/*"))
    inputs[f"runs/{run}/* (aggregate of {len(fs)} files: sha256 over sorted 'path sha256' lines)"] = agg(fs)
ATTEST = ["evidence/tooling/logs/verify_manifest.log", "evidence/tooling/logs/pii_scan.log"]  # written after the manifest, so not hashable in it
files = {}
for p in sorted(P.rglob("*")):
    if p.is_file() and p.name != "audit_manifest.json" and '__pycache__' not in p.parts and str(p.relative_to(P)) not in ATTEST:
        files[str(p.relative_to(P))] = dict(bytes=p.stat().st_size, sha256=sha(p))
S = "AI Agent Audits/evidence/scripts/"; T = "AI Agent Audits/evidence/tooling/"
CE = "controlled exploratory analysis with fixed recorded design"; RC = "reproduction check"; DN = "deterministic numerical check"
F = lambda pt, cmd, outs, kind, how, summary: dict(point=pt, command=cmd, outputs=outs, type=kind, basis=how, summary=summary)
findings = [
 F(["R1 13", "R1 14", "R2 8"], f'python "{S}repro13.py"', ["results/repro13.json", "logs/repro13.log"], RC, "RAN",
   "all 38 stored keys compared: 78/500 runs bit-exact on every key; 500/500 bit-exact on the 7 arrays and 4 headline scalars; the other 422 differ only in S_spectral, Weight_gini, Projection_norm_max/_mean_active (<=4.9e-15 abs, <=1.3e-12 rel); status ok_with_warnings"),
 F(["R1 1", "R1 4", "R1 8"], f'python "{S}archived13_closedform.py"', ["results/archived13_closedform.json", "logs/archived13_closedform.log"], DN, "RAN",
   "repo-omega baseline: 16 distinct topologies, equal to closed-form set 50/100, subset 95/100; no_delay 1 topology = set 100/100; no_gap active weight 2.6654 vs eta/gamma 2.667; shuffle mean R 0.371 < R* 0.4286"),
 F(["R1 1", "R1 4"], f'python "{S}freq_predictor.py"', ["logs/freq_predictor.log"], RC, "RAN",
   "per-manifest distinct topologies 11 and 11; per-seed corr(P,R_pred) 0.927/0.919; seed-averaged 0.990/0.988"),
 F(["R1 1", "R1 3"], f'python "{S}omega_random.py"', ["results/omega_random.json", "logs/omega_random.log"], RC, "RAN",
   "identical to round-1 pass: precision/recall uniform no_delay 0.717/0.575, baseline 0.600/0.508; clustered 0.933/0.282, 0.838/0.267"),
 F(["R1 4", "R1 7"], f'python "{S}omega_multistab.py"', ["results/omega_multistab.json", "logs/omega_multistab.log"], RC, "RAN",
   "mean Jaccard 0.514; baseline vs no_delay 0.516; distinct per omega [4,2,3,4,2,4,1,4,4,4]"),
 F(["R1 1", "R1 2", "R1 7", "R2 5", "R2 6"], f'python "{S}delay_paired_heldout.py" && python "{S}analyze_delay_heldout.py"',
   ["results/delay_paired_edges_uniform.csv", "results/delay_paired_edges_clustered.csv", "results/delay_paired_runs.json", "results/delay_heldout_analysis.json"], CE, "RAN",
   "held-out AUC/logloss for the final threshold edge (B_final > B_C; identical to P_future > 0.5 here: 0/29040 label differences); sample diversity: mean distinct four-seed topologies 2.93 vs 2.33 (uniform), 2.0 vs 1.4 (clustered); not basin counts"),
 F(["R1 5", "R2 1"], f'python "{S}gate_idempotence.py"', ["results/gate_idempotence.json", "logs/gate_idempotence.log"], DN, "RAN",
   "20000/20000 bitwise idempotent; jump 1.579e-12 = eps/cap; eps=0 differs from the Euclidean projection by 0.037-0.046 at the sampled points"),
 F(["R1 5", "R2 1"], f'python "{S}mathcheck.py"', ["logs/mathcheck.log"], DN, "RAN",
   "witness x outside C maps to the interior (margin 6.67e-13 = c*eps/(q+eps)) and A(x) != x: exact no-go for smooth strictly convex Bregman / PD-metric projection at eps=1e-12; KL projection differs 0.022-0.030 at the sampled points"),
 F(["R1 9"], f'python "{S}kappa_rows.py"', ["results/kappa_rows.json", "logs/kappa_rows.log"], DN, "RAN",
   "row rates sum F/c 0.12419, 0.12420, 0.12208; repo fitted gap 0.0699224 vs observed 0.0691225"),
 F(["R1 9", "R2 2"], f'python "{S}kappa_tw.py" all && python "{S}analyze_kappa_tw.py"',
   ["results/kappa_tw_all.json", "results/kappa_tw_summary.json", "results/kappa_tw_components.csv", "logs/kappa_tw.log", "logs/analyze_kappa_tw.log"], CE, "RAN",
   "central-difference matrix (not a Jacobian at ties): 292 slow components over 5 T_w, r_B vs discrete Prop 8.3 max rel err 3.1e-5; its K3 census is superseded by kappa_cycle_kernel"),
 F(["R2 2"], f'python "{S}kappa_cycle_kernel.py" && python "{S}analyze_kappa_cycle_kernel.py"',
   ["results/kappa_cycle_kernel.json", "results/kappa_cycle_kernel_summary.json", "logs/kappa_cycle_kernel.log", "logs/analyze_kappa_cycle_kernel.log"], DN, "RAN",
   "multiplier on ker A_J vs closed form lambda_k=(1-gamma dt)c/(c+dt(k eta-gamma c)+eps) [round 4: split as 264 two-sided + 110 one-sided K3, see rate_law_census_r4]: 374 resolved components, lambda to 2.07e-8 rel, kappa to 2.07e-6 abs; 32 poorly resolved (all rho=2); dim K = m-n on 373/373 all-tied complete components; all 110 all-tied K3 have a one-sided slow direction +v_c (0/110 along -v_c); tie nonadditivity K3 0.5 ... K6 0.1581; cohort: 40 fixed seeds x 5 T_w"),
 F(["R1 6", "R2 4"], f'python "{S}ablation14_topology.py"', ["results/ablation14_topology.json", "logs/ablation14_topology.log"], RC, "RAN",
   "reset_B Jaccard 1.000, reset_ema 0.992, reset_B_ema 0.913 (vs continue); reset_B_ema equals the closed-form set in 32/40 seeds"),
 F(["R2 4"], f'python "{S}frozen_topology_check.py"', ["results/frozen_topology_check.json", "logs/frozen_topology_check.log"], DN, "RAN",
   "0/29040 edges change threshold status (B > B_C) between split and end (13200 archived repo-omega, 15840 random-omega), so B_split's AUC 1.0 is expected by construction; round 4: nonbinary_P_future_count 0/29040 and P_future label vs split status differs 0/29040 (P_future averages B > B_C over every future step)"),
 F(["R3 1", "R3 2", "R3 3"], f'python "{S}rate_law_census_r4.py"', ["results/rate_law_census_r4.json", "logs/rate_law_census_r4.log"], DN, "RAN",
   "374 resolved = 264 two-sided fiber (lambda to 2.07e-8 rel, kappa to 2.07e-6) + 110 all-tied K3 one-sided rays (294 slow rays, lambda to 1.7e-7); 32 poorly resolved; finite-eps fixed point changes lambda by 1.6e-12 rel; derived tie patterns 1/sqrt(2k(k-1)), sqrt(2/(k+1)) match synthetic equal-weight K3-K8 to 4.4e-10, fail for unequal-edge K4; -v_c ray lambda/lambda_2 in [0.33333, 0.33337]"),
 F(["R3 8"], 'python "AI Agent Audits/evidence/proposals/aief_1_4_full_state_spectrum.py"', ["proposals/results/full_state_spectrum.json", "proposals/results/full_state_spectrum.log"], DN, "RAN (proposal; repo original not edited)",
   "closed 966-dim state (history 612 + B 66 + Re/Im C 288), one replay, central difference h=1e-7: EMA pole is NOT the unique slow pole (one step: 10 rates in the gap, 0.189328 x2, 0.252355 x5, 0.650-0.669 x3; T=500: 13); J+/J- differ by 0.49937 (mixed branch); citations of the 18-coordinate result: proposals/augmented_spectrum_citations.md"),
 F(["R3 L1-L6"], "cd lean/AIEFProofs && STRICT_ORPHANS=1 LOG_DIR=<dir> bash check_lean.sh", ["logs/lean_r4/"], DN, "RAN",
   "round 4 local clone, sources rebased onto main 43ce98f (new copyright/SPDX headers; see logs/lean_r4/NOTE.txt): 7/7 steps PASS, 8713 jobs, 12 warnings (all Smoke.lean header linter), 0 markers, 115 declarations, 0 disallowed axioms; source SHA256SUMS (8 files) enforced; negative tests fail at step 2"),
 F(["R1 6", "R2 3"], f'python "{S}matched_phase_check.py"', ["results/matched_phase_check.json", "logs/matched_phase_check.log"], CE, "RAN",
   "reads test_output/ (its analysis_manifest: 40/40 seeds, 0 failures, validation passing; hashes recorded); Weighted_similarity_late +0.0642 [0.0405, 0.0886], 31/40 positive; the FAILED manifest is a different 1-seed partial run (aief_1_4_matched_phase_memory_ablation)"),
 F(["R2 9"], f'python "{S}evolution_checks.py"', ["results/evolution_checks.json", "logs/evolution_checks.log"], DN, "RAN",
   "repo augmented-spectrum procedure: restore_state does not restore theta (drift 0.0156 -> 0.272); forward vs reversed column order max |dJ| 9896 (max entry 10491); slowest rates repo -1068, -542, corrected -9.57, 0.05713; 18-vector not closed (history[1]: 1.0 x delta, theta: 5.6e-4 x delta); no rate in the repo's gap window"),
 F(["R1 14"], f'bash "{S}lean_check.sh"', ["logs/lean_build_original.log", "logs/lean_build_patched.log", "logs/lean_sorry_grep.log"], DN, "RAN",
   "as committed BUILD_EXIT 1 (bad import ControllerFiberProjector); import removed: 1235 jobs OK; no sorry/axiom/admit (not rerun in round 3)"),
 F(["R1 11"], f'bash "{S}terminology_grep.sh"', ["logs/terminology_grep.log"], "descriptive", "RAN", "term counts; gauge appears once (comment); Ehresmann/holonomy/fiber bundle 0"),
 F(["R2 9"], 'bash "AI Agent Audits/evidence/run_all.sh"', ["logs/run_all_verify.log"], RC, "RAN",
   "runs every step above into a temp dir and cmp's each committed result; round 3: every step ok; round 4: 19 steps, UPDATE=1 run (logs/run_all_update_r4.log) differed only in frozen_topology_check.json (DIFFERS) and rate_law_census_r4.json (NEW), then a verify run reported ALL OK"),
 F(["R2 9"], 'python "AI Agent Audits/evidence/verify_manifest.py" --inputs', ["tooling/logs/verify_manifest.log"], DN, "RAN", "every listed file and repo input matches size/sha256; no unlisted files"),
 F(["packaging"], f'python "{T}pii_scan.py" --private <local file, not published>', ["tooling/logs/pii_scan.log", "tooling/logs/pii_scan_selftest.log"], DN, "RAN",
   "no e-mail addresses, local paths, token shapes, device codes, binaries, CR, or size-limit breaches; self-test catches 5/5 planted issues. SCOPE: 'AI Agent Audits/' only; says nothing about the rest of the repository (repo-wide privacy/copyright unresolved, owner decision)"),
 F(["packaging"], f'python "{T}verify_github_blobs.py" <tree JSON of c9907a6> "AI Agent Audits"', ["tooling/logs/verify_github_blobs_c9907a6.log"], DN, "RAN",
   "the round-2 staging tree is IDENTICAL (58/58 git blob sha1) to 'AI Agent Audits/' at github c9907a6"),
 F(["packaging"], f'python "{T}make_manifest.py"', ["audit_manifest.json"], "n/a", "RAN", "this manifest"),
 F(["R3 1-9"], f'python "{T}round4/corrections_r4.py"', [], "n/a", "RAN", "applies the dated [Correction 2026-10-25, response-3 #N] notes to response_2, README, salvage and response (anchors must match exactly once; refuses to run twice)"),
 F(["provenance"], "tooling/round1, round2, round3, adhoc_commands.md", [], "n/a", "RAN (scratch; redacted copies)",
   "scratch scripts and ad-hoc commands used to build rounds 1-3; redacted copies are for audit, not runnable verbatim; see AIEFS_audit_response_2.md 'Provenance gaps'"),
 F(["R1 10", "R1 11", "R2 2"], "read AIEF_1_4_OPERATOR_THEORY_MANUSCRIPT.md Prop 2.9, 8.1, 8.3, 9.2, 11.1", [], "n/a", "READ",
   "kappa is the eigenvalue log-modulus gap of the conditional triangular augmented operator; exact discrete rate is the repo's Prop 8.3"),
 F(["R1 12"], "web literature search 2026-10-23", [], "n/a", "SEARCHED (not exhaustive)",
   "prior art: Seliger et al. 2002; Timms & English 2014; Picallo & Riecke 2011; Berner et al. 2023; Miller & MacKay 1994. Exact combination not found"),
 F(["R1 2", "R1 7", "priority ordering"], "reasoning", [], "n/a", "INFERRED", "judgments on collaborator overreach and priority ordering are reasoning, not runs"),
]
m = dict(
 created="2026-10-25", audited_repo="github.com/jacobbrainard84-knightninja/AIEFS",
 audited_commit="e47bad150792425eb8e962ff636c69289eedd8b1",
 report_commits={"55be461f3da5b71c86fced8023a276f5868f4c23": "adds AI Agent Audits/AIEFS_audit.md (original)",
                 "f7246a364060237001fa35115f1ea691e620d048": "adds AI Agent Audits/AIEFS_salvage.md (original)",
                 "c9907a66d182b8bb95521ac29f83abecf4cd120c": "head of the round-2 publication (880e07e..c9907a6)",
                 "60e60297e6dd34887348e6f858c32b3829d72f69": "head of the round-3 publication (22 commits 7d752fd..60e6029)",
                 "0b5b1082561b7717a0ea465d76bb9ebefa26b770": "Lean: ControllerFiberProjector.lean",
                 "dc0250a0586c8316b594ed5e424fffb9c84e93e8": "head after tooling, lean_recovery and cleanup (56 commits 0f5ef7a..dc0250a)",
                 "43ce98fdeba2226e0869f7376dbe0a7bd67d94c2": "base of round 4: licence files, executable bits, Lean copyright/SPDX headers, licensing inventory, 4 third-party PDFs removed (1a81cb6..43ce98f); round 4 was committed on top of it on 2026-10-25, including the inventory re-encoding to inventory.json.gz.b64"},
 note_inputs="Inputs hashed from the read-only clone at e47bad1; later commits add only files under 'AI Agent Audits/'.",
 point_labels="'R1 n' = point n of the round-2 response (AIEFS_audit_response.md); 'R2 n' = point n of AIEFS_audit_response_2.md; 'R3 n' = point n of AIEFS_audit_response_3.md",
 run_from="repository root", environment="evidence/ENVIRONMENT.md",
 inputs_sha256=inputs, inputs_missing=missing, findings=findings, files_sha256=files,
 post_manifest_logs=ATTEST, post_manifest_logs_note='Written after this manifest by verify_manifest.py and pii_scan.py; they cannot be hashed here without circularity. verify_manifest.py treats them as listed but unhashed; regenerate them with the commands in findings.',
 publication_edits=[
  "Log header lines had the local interpreter path replaced by 'python' and absolute or relative-escape paths rewritten to 'AI Agent Audits/evidence/...'; Lean logs had the temporary build directory rewritten to '<tmpcopy>'. No other log content was altered.",
  "No logs were subsampled or truncated: every file is under 1 MB.",
  "No binary files are published. A local intermediate .npz from development of the delay experiment was excluded; the published scripts do not write it.",
  "AIEFS_audit.md / AIEFS_salvage.md / AIEFS_audit_response.md carry in-place marked corrections (2026-10-23, 2026-10-24 and 2026-10-25); absolute local paths and the author's user/host name were replaced by neutral descriptions.",
  "evidence/tooling/round*/ and adhoc_commands.md are redacted copies: local paths -> <placeholders>, the owner's e-mail -> <owner-email-redacted>, user/host-name literals -> <redacted>. The literal list is a local file that is not published.",
  "PII in the repository's own PDFs is referenced by path only and not reproduced."])
json.dump(m, open(E / "audit_manifest.json", "w"), indent=1)
print(len(files), "files hashed;", len(inputs), "inputs; missing inputs:", missing)
