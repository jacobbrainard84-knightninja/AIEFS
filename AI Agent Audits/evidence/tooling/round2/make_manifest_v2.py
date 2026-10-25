# [publication copy, 2026-10-24] local paths and personal values replaced by <placeholders>; otherwise verbatim.
import hashlib, json, os, glob
from pathlib import Path
P = Path("<v2-staging>/AI Agent Audits"); E = P/"evidence"; R = Path("<repo-clone>")
sha = lambda p: hashlib.sha256(open(p,'rb').read()).hexdigest()
def agg(files):
    h = hashlib.sha256()
    for f in sorted(files): h.update(f"{os.path.relpath(f,R)} {sha(f)}\n".encode())
    return h.hexdigest()
single = ["AIEF_1_3_falsification_updated.py","aief_experiment_engine_v1.py","AIEF_1_4_Twindow_sensitivity.py",
  "AIEF_1_4_OPERATOR_THEORY_MANUSCRIPT.md","AI_AGENT_HANDOFF_PROMPT.md",
  "runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz","runs/5a9f093a2fe0/manifest.json",
  "runs/b57562a8ee77/AIEF_1_4_Twindow_sensitivity_b57562a8ee77_branch_diagnostics.npz",
  "aief_1_4_scalar_spectral_gap_reduction/scalar_spectral_gap_report.txt",
  "aief_1_4_matched_phase_memory_ablation/analysis_manifest.json",
  "lean/AIEFProofs/AIEFProofs.lean","lean/AIEFProofs/AIEFProofs/ControllerFiber.lean","lean/AIEFProofs/lean-toolchain","lean/AIEFProofs/lake-manifest.json"]
inputs = {f: sha(R/f) for f in single if (R/f).exists()}
missing = [f for f in single if not (R/f).exists()]
for run in ["c3da1ac707bf","73dca37cf93f"]:
    fs = glob.glob(str(R/f"runs/{run}/*"))
    inputs[f"runs/{run}/* (aggregate of {len(fs)} files: sha256 over sorted 'path sha256' lines)"] = agg(fs)
files = {}
for p in sorted(P.rglob("*")):
    if p.is_file() and p.name != "audit_manifest.json":
        files[str(p.relative_to(P))] = dict(bytes=p.stat().st_size, sha256=sha(p))
S = "AI Agent Audits/evidence/scripts/"
F = lambda pt, cmd, outs, kind, how, summary: dict(point=pt, command=cmd, outputs=outs, type=kind, basis=how, summary=summary)
findings = [
 F([13,14],f'python "{S}repro13.py"',["results/repro13.json","logs/repro13.log"],"confirmatory","RAN","500/500 archived AIEF-1.3 runs bit-exact; means equal audit section 3"),
 F([1,4,8],f'python "{S}archived13_closedform.py"',["results/archived13_closedform.json"],"confirmatory","RAN","repo-omega baseline: 16 distinct topologies (audit said 7), equal to closed-form set 50/100, subset 95/100; no_delay 1 topology = set 100/100; no_gap active weight 2.6654 vs eta/gamma 2.667; shuffle mean R 0.371 < R* 0.4286"),
 F([1,4],f'python "{S}freq_predictor.py"',["logs/freq_predictor.log"],"confirmatory","RAN","per-manifest distinct topologies 11 and 11; per-seed corr(P,R_pred) 0.927/0.919; seed-averaged 0.990/0.988"),
 F([1,3],f'python "{S}omega_random.py"',["results/omega_random.json","logs/omega_random.log"],"confirmatory (rerun of first pass)","RAN","identical to first pass: precision/recall uniform no_delay 0.717/0.575, baseline 0.600/0.508, clustered 0.933/0.282, 0.838/0.267"),
 F([4,7],f'python "{S}omega_multistab.py"',["results/omega_multistab.json"],"confirmatory (rerun)","RAN","mean Jaccard 0.514; baseline vs no_delay 0.516; distinct per omega [4,2,3,4,2,4,1,4,4,4]"),
 F([1,2,7],f'python "{S}delay_paired_heldout.py" && python "{S}analyze_delay_heldout.py"',["results/delay_paired_edges_uniform.csv","results/delay_paired_edges_clustered.csv","results/delay_paired_runs.json","results/delay_heldout_analysis.json"],"confirmatory (tests requested by the collaborator, designed before running)","RAN","held-out AUC/logloss and paired delay statistics; see AIEFS_audit_response.md section 5. Distinct-topology and Jaccard contrasts are exploratory."),
 F([5],f'python "{S}gate_idempotence.py"',["results/gate_idempotence.json"],"confirmatory","RAN","20000/20000 bitwise idempotent; jump 1.579e-12 = eps/cap; eps=0 Euclidean projection differs 0.037-0.046"),
 F([5],f'python "{S}mathcheck.py"',["logs/mathcheck.log"],"confirmatory (rerun)","RAN","interior witness margin 6.67e-13; KL projection differs 0.022-0.030"),
 F([9],f'python "{S}kappa_rows.py"',["results/kappa_rows.json"],"confirmatory","RAN","row rates sum F/c 0.12419, 0.12420, 0.12208 (label corrected); repo fitted gap 0.0699224 vs observed 0.0691225"),
 F([9],f'python "{S}kappa_tw.py" all && python "{S}analyze_kappa_tw.py"',["results/kappa_tw_all.json","results/kappa_tw_summary.json","results/kappa_tw_components.csv"],"confirmatory (prediction stated in salvage 3.5); twin_early K3 statistic exploratory","RAN","292 slow components over 5 T_w: r_B vs discrete Prop 8.3 max rel err 3.1e-5; kappa vs discrete closed form max abs err 5.3e-6; K3: 1 of 115 components has a slow channel (rho=1); 114 fully saturated"),
 F([6],f'python "{S}ablation14_topology.py"',["results/ablation14_topology.json"],"confirmatory (rerun of salvage table)","RAN","reset_B Jaccard 1.000, reset_ema 0.992, reset_B_ema 0.913 (Jaccard vs continue); reset_B_ema equals the closed-form set in 32/40 seeds"),
 F([6],f'python "{S}matched_phase_check.py"',["results/matched_phase_check.json"],"exploratory","RAN","Weighted_similarity_late +0.064 [0.041,0.089]; repo canonical analysis_manifest reports FAILED (provenance caveat)"),
 F([14],f'bash "{S}lean_check.sh"',["logs/lean_build_original.log","logs/lean_build_patched.log","logs/lean_sorry_grep.log"],"confirmatory","RAN","as committed BUILD_EXIT 1 (bad import ControllerFiberProjector); import removed: 1235 jobs OK; no sorry/axiom/admit"),
 F([11],f'bash "{S}terminology_grep.sh"',["logs/terminology_grep.log"],"descriptive","RAN","term counts; gauge appears once (comment); Ehresmann/holonomy/fiber bundle 0"),
 F([10,11],"read AIEF_1_4_OPERATOR_THEORY_MANUSCRIPT.md Prop 2.9, 8.1, 8.3, 9.2, 11.1",[],"n/a","READ","kappa is the eigenvalue log-modulus gap of the conditional triangular augmented operator; exact discrete rate is the repo's Prop 8.3"),
 F([12],"web literature search 2026-10-23",[],"n/a","SEARCHED (not exhaustive)","prior art: Seliger et al. 2002; Timms & English 2014; Picallo & Riecke 2011; Berner et al. 2023; Miller & MacKay 1994. Exact combination not found"),
 F([2,7,"priority ordering"],"reasoning",[],"n/a","INFERRED","judgments on collaborator overreach and priority ordering are reasoning, not runs"),
]
m = dict(
 created="2026-10-23", audited_repo="github.com/jacobbrainard84-knightninja/AIEFS",
 audited_commit="e47bad150792425eb8e962ff636c69289eedd8b1",
 report_commits={"55be461f3da5b71c86fced8023a276f5868f4c23":"adds AI Agent Audits/AIEFS_audit.md (original)","f7246a364060237001fa35115f1ea691e620d048":"adds AI Agent Audits/AIEFS_salvage.md (original)"},
 note_inputs="Inputs hashed from the read-only clone at e47bad1; the two later commits add only report files (checked via GitHub API).",
 run_from="repository root", environment="evidence/ENVIRONMENT.md",
 inputs_sha256=inputs, inputs_missing=missing,
 findings=findings,
 files_sha256=files,
 publication_edits=[
  "Log header lines and Python warning lines had absolute local paths rewritten to 'AI Agent Audits/evidence/...'; Lean logs had the temporary build directory rewritten to '<tmpcopy>'. No other log content was altered.",
  "No logs were subsampled or truncated: every file is under 1 MB.",
  "No binary files are published. A local intermediate .npz from development of the delay experiment was excluded; the published scripts do not write it. Rerunning delay_paired_heldout.py reproduced the published CSVs/JSON byte-identically.",
  "AIEFS_audit.md / AIEFS_salvage.md are the v2 texts: in-place marked corrections; absolute local paths and the author's user/host name were replaced by neutral descriptions.",
  "PII in the repository's own PDFs is referenced by path only and not reproduced."])
json.dump(m, open(E/"audit_manifest.json","w"), indent=1)
print(len(files), "files hashed; missing inputs:", missing)
