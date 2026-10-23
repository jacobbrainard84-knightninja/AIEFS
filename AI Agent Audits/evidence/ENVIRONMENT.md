# Environment used for the audit runs (2026-10-23)

- OS: Linux 6.12 x86_64 (container), 7 worker processes (multiprocessing Pool ≤ 7), ~4 GB RAM.
- Python 3.13.5 (virtualenv)

## pip freeze
```
contourpy==1.4.0
cycler==0.12.1
fonttools==4.67.0
iniconfig==2.3.1
kiwisolver==1.5.1
matplotlib==3.11.2
numpy==2.5.1
packaging==26.3
pandas==3.1.0
pillow==13.0.0
pluggy==1.7.0
Pygments==2.21.0
pyparsing==3.3.3
pytest==9.1.1
python-dateutil==3.0.0
scipy==1.18.1
six==1.17.0
tzdata==2026.5
```
Only numpy, scipy and pandas are imported by the evidence scripts. scikit-learn is not used: the logistic regression and AUC are implemented in numpy.

## Lean
- elan 4.2.4 (227caca13 2026-08-25)
- Toolchain (from `lean/AIEFProofs/lean-toolchain`): leanprover/lean4:v4.33.1
- Lake 5.0.0-src+819816b (Lean 4.33.1)
- mathlib v4.33.1, rev 0df444a360eaa60ab8c11dca51a86af692955474. The prebuilt cache came from `lake exe cache get`: 8690 files.

## Repository state
- Simulations and analyses ran against a read-only clone at commit `e47bad1`. The audited model code (`AIEF_1_3_falsification_updated.py`, `aief_experiment_engine_v1.py`, `AIEF_1_4_Twindow_sensitivity.py`) and the archived `runs/` inputs are hashed in `audit_manifest.json` (`inputs`).
- Commits after `e47bad1`, checked read-only via the GitHub API: `55be461` adds only `AI Agent Audits/AIEFS_audit.md`, and `f7246a3` adds only `AI Agent Audits/AIEFS_salvage.md`. No model code or data changed after `e47bad1`.
- Determinism: archived AIEF-1.3 runs reproduce bit-exactly (500/500) on this stack. Other numpy/BLAS builds may differ at the 1e-14 level. Example: 40/200 κ(T_w) replays at ρ=0.5 differ from the archive by ≤2.5e-14 even here.
