# Reproducing the audit evidence

Run every command **from the AIEFS repository root**. All paths are relative. Scripts read repo inputs from the working directory and write to `AI Agent Audits/evidence/results/` and `.../logs/`. They do not modify any repo file. Set `PYTHONDONTWRITEBYTECODE=1` to avoid creating `__pycache__`.

```bash
python -m venv .venv && . .venv/bin/activate
pip install numpy==2.5.1 scipy==1.18.1 pandas==3.1.0
export PYTHONDONTWRITEBYTECODE=1
```

## Everything (about 15 min on 7 cores)
```bash
PY=python bash "AI Agent Audits/evidence/run_all.sh"
```

## Individual steps
| Step | Command | Runtime | Output (results/) | Response point |
|---|---|---|---|---|
| Math checks (projection, gate, KL, Jordan) | `python "AI Agent Audits/evidence/scripts/mathcheck.py"` | s | (log only) | 5 |
| Gate idempotence, ε=0 Euclidean/KL comparison | `python "AI Agent Audits/evidence/scripts/gate_idempotence.py"` | s | gate_idempotence.json | 5 |
| Closed-form ω predictor on archived 1.3 runs | `python "AI Agent Audits/evidence/scripts/freq_predictor.py"` | s | (log only) | 1, 4 |
| Archived 1.3: distinct topologies, ablation closed forms | `python "AI Agent Audits/evidence/scripts/archived13_closedform.py"` | s | archived13_closedform.json | 1, 4, 8 |
| κ row rates on the exceptional K3 | `python "AI Agent Audits/evidence/scripts/kappa_rows.py"` | s | kappa_rows.json | 9 |
| Matched-phase memory check (exploratory) | `python "AI Agent Audits/evidence/scripts/matched_phase_check.py"` | s | matched_phase_check.json | 6 |
| 1.4 ablation topologies | `python "AI Agent Audits/evidence/scripts/ablation14_topology.py"` | s | ablation14_topology.json | 6 |
| κ(T_w) replays (200 seed×ρ) | `python "AI Agent Audits/evidence/scripts/kappa_tw.py" all` | ~3 min | kappa_tw_all.json | 9 |
| κ(T_w) analysis | `python "AI Agent Audits/evidence/scripts/analyze_kappa_tw.py"` | s | kappa_tw_summary.json, kappa_tw_components.csv | 9 |
| Paired delay on/off on random ω (240 runs) | `python "AI Agent Audits/evidence/scripts/delay_paired_heldout.py"` | ~2.5 min | delay_paired_edges_{uniform,clustered}.csv, delay_paired_runs.json | 1, 2, 7 |
| Held-out prediction, delay statistics | `python "AI Agent Audits/evidence/scripts/analyze_delay_heldout.py"` | s | delay_heldout_analysis.json | 1, 2, 7 |
| Random-ω predictor (first-pass rerun) | `python "AI Agent Audits/evidence/scripts/omega_random.py"` | ~1.5 min | omega_random.json | 1, 3 |
| Random-ω multistability | `python "AI Agent Audits/evidence/scripts/omega_multistab.py"` | ~0.5 min | omega_multistab.json | 4, 7 |
| Bit-exact reproduction of 500 archived 1.3 runs | `python "AI Agent Audits/evidence/scripts/repro13.py"` | ~5 min | repro13.json | 13 |
| Terminology counts | `bash "AI Agent Audits/evidence/scripts/terminology_grep.sh"` | s | (log only) | 11 |
| Lean build (original fails, patched copy builds) | `bash "AI Agent Audits/evidence/scripts/lean_check.sh"` | ~5 min + cache download | logs/lean_build_*.log | 14 |

The Lean step needs elan. It builds a temporary copy of `lean/AIEFProofs`, so the repo is never patched. The committed logs come from the audit's own copy; its absolute temp paths were replaced with `<tmpcopy>`.

To check reproduction, compare your `results/*.json`/`*.csv` against the sha256 values in `audit_manifest.json`. The κ(T_w) and delay outputs are deterministic on the stack in `ENVIRONMENT.md`.
