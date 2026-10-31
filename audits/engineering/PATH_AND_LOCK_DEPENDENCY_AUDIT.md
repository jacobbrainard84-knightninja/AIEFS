# Stage 3 Engineering, AST Path Dependency, Source-Hash Lock & Cross-Host Reproducibility Audit

**Milestone 1 — Stage 3 Engineering Audit Report**  
**Machine-Readable Companion Table:** `audits/engineering/python_path_dependencies.csv` (`165` tracked Python files)  
**Automated Gate CLI:** `audits/engineering/verify_inventory.py`

---

## 1. Stationary Authority Locks (`LOCKED_DO_NOT_MOVE`)

`AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/authority.py` (`verify_authority_lock`) enforces **both exact relative path from `authority_root` and exact SHA-256 byte identity** across six artifacts defined in `AIEF_1_4_FROZEN_5a9f093a2fe0.authority.lock.json` (`lock_sha256 = 57e4337c66f68eda116f32bbc446eb30bd068e0d39f1634eefdadcf02cfcbb5f`), plus a seventh source-hash lock embedded inside `runs/5a9f093a2fe0/manifest.json`:

| Relative Path from Repository Root | Lock Mechanism | Verified SHA-256 | Stage 4 Rule |
|---|---|---|---|
| `aief_experiment_engine_v1.py` | `authority.lock.json` (`legacy_sources.engine_v1`) | `ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede` | **Keep stationary at root.** Studies reference via import/wrapper. |
| `AIEF_1_4_Twindow_sensitivity.py` | `authority.lock.json` (`legacy_sources.twindow_driver_v1`) | `633d1a21502598021d456bff7ff39b4065b5e5d053e0956ee` (`633d1a215025...`) | **Keep stationary at root.** Moving breaks `verify_authority_lock()`. |
| `AIEF_1_4_Twindow_sensitivity_analysis_v3.py` | `authority.lock.json` (`legacy_sources.twindow_analysis_v3`) | `348093079c37697a1b84a250aca2d0fa74180b39a1b62e20893190a974ffd919` | **Keep stationary at root** (even though `v4` supersedes it analytically). |
| `AIEF_1_4_memory_ablation_updated.py` | `runs/5a9f093a2fe0/manifest.json` (`source_sha256`) | `34d37908764a...` | **Keep stationary & unmodified at root.** Do NOT overwrite with whitespace-edited `.zip` copy (`4b792e88...`). |
| `runs/5a9f093a2fe0/manifest.json` | `authority.lock.json` (`frozen_artifacts.manifest`) | `bf4d8c4152efafac352c8e1e56759ee7867fdd418cb04a8ee1f2fc87c2315a33` | **Keep stationary in `runs/5a9f093a2fe0/`.** |
| `runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz` | `authority.lock.json` (`frozen_artifacts.branch_npz`) | `8fa9cc059117a7dbef0ed14e52907ec63f7626b50e4b3c8815977547e4590f0f` | **Keep stationary in `runs/5a9f093a2fe0/`.** |
| `runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_scalar_summary.csv` | `authority.lock.json` (`frozen_artifacts.scalar_csv`) | `f4bcdd1403796f0e2fa4f6fbedaee9d79fd5c970b4c33d49ac995b1f0c3bffda` | **Keep stationary in `runs/5a9f093a2fe0/`.** |

Additionally:
- `runs/b57562a8ee77/` (`Frozen` 200-condition $T_{\text{window}}$ oracle) and `runs/c3da1ac707bf/` + `runs/73dca37cf93f/` (`Frozen` 50+50 disjoint AIEF-1.3 cohorts) are referenced directly by test suites and CLI scripts and must remain at their exact `runs/<hex_id>/` paths while lightweight `studies/<study>/` entry points link/point to them cleanly.
- `lean/AIEFProofs/AIEF_LEAN_PROJECT_LOCK_HASHES.txt` locks 12 source/configuration files inside `lean/AIEFProofs/` (all 12 SHA-256 digests verified 100% intact).

---

## 2. AST & Path-Dependency Findings Across All `165` Python Files (`python_path_dependencies.csv`)

1. **Syntax Check Discovery (`164 / 165` valid Python ASTs; `1` shell-snippet file):**
   - `test_01.py` is **not valid Python syntax**: line 1 starts with a raw Steam Deck bash command (`df -h "/home/deck/AI_Programs/SSRH/"`) pasted above an interactive `python3` snippet (`SyntaxError` at line 1). Classified as `Superseded` -> `archive/scratch_and_probes/test_01.py`.
   - `probe_02.py` parses cleanly under `ast.parse` but fails at runtime with `NameError: name 'np' is not defined` because `import numpy as np` was omitted (`Superseded` scratch probe).
2. **Legacy Steam Deck Hardcoded Default Paths (`/home/deck/AI_Programs/SSRH/...`):**
   - Root `AIEF_1_3_paired_statistics.py`, `AIEF_1_3_paired_statistics_updated.py`, `AIEF_1_3_closure_diagnostics.py`, and `AIEF_1_3_closure_diagnostics_updated.py` carry default CLI paths pointing to `/home/deck/AI_Programs/SSRH/runs/...` (and in root `*_updated.py`, still default to the older duplicate 20-seed IDs `87dfe5798954` + `5a338105785a` unless overridden on the CLI!).
   - **Remediation:** Always pass explicit cohort paths `runs/c3da1ac707bf runs/73dca37cf93f` on the CLI (and see `audits/github_reconciliation/recovered_from_workspace_019ff402/zip_only_files/zip_updated_AIEF_1_3_*` for the relative-path versions recovered from `workspace-019ff402.zip`).
3. **Cross-Script Local Module Imports (`PYTHONPATH` Requirements):**
   - `AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/*` imports `aief_experiment_engine_v1` and `AIEF_1_4_Twindow_sensitivity` dynamically by module name and resolves authority locks against `--authority-root` (defaulting to current working directory). Invoking with `PYTHONPATH=".:AIEF_Experiments/aief_modular_platform_v1_analysis_v4"` from repo root succeeds cleanly across all tests.
   - `run_twindow_pivot_study.py`, `diagnose_import.py`, `probe_01.py`, `probe_02.py`, and several `AIEF_1_4_*` scripts import `AIEF_1_4_memory_ablation_updated` or `aief_experiment_engine_v1` from `sys.path`.

---

## 3. Critical Discovery — Cross-Host / Cross-`glibc` IEEE-754 Floating-Point Reproducibility (`0.000e+00` Same-Host vs. `4.405e-13` Cross-`glibc`)

Live execution of the modular test suite and direct array-by-array comparison on Linux x86_64 (`Debian Bookworm, glibc 2.36, Python 3.11.2, NumPy 2.4.6`) against the frozen artifacts generated on the original Steam Deck (`SteamOS / Arch, Linux 6.16.12-valve24, AMD Custom APU 0405 Zen 2, glibc 2.40, Python 3.13, NumPy 2.5.1`) revealed a critical distinction for Stage 7 GitHub Actions CI:

1. **Same-Host Modular-vs-Monolithic Equivalence is Bitwise Exact (`0.000e+00` across all 344 arrays):**
   - Running `_simulate_condition` (`aief_modular.runner`) and `simulate_seed_rho` (`AIEF_1_4_Twindow_sensitivity.py`) on the **same machine** produces **exact IEEE-754 bit-for-bit equality (`max_abs_diff = 0.000e+00`, 0 ULP difference across all `344 / 344` output arrays)**—even with `NPY_DISABLE_CPU_FEATURES` toggled!
   - Likewise, the live 176,000-step slow test (`AIEF_RUN_SLOW_TESTS=1 pytest` -> `41 passed, 1 skipped in 14.90s`) passes with zero error.
2. **Cross-Host / Cross-`glibc` Re-Execution Against Saved Steam Deck `.npz` Files Differs by `4.405e-13` on Continuous Arrays (`0.000e+00` on Discrete Topology Arrays):**
   - Across `48,000`–`80,000` coupled nonlinear delay-differential Euler steps evaluating transcendental `np.sin(...)` calls every step, a 1-ULP ($\sim 1.1 \times 10^{-16}$) libm difference between `glibc 2.36` and SteamOS `glibc 2.40` accumulates to **`max_abs_diff = 4.405e-13`** (~12.4 decimal digits of exact agreement), while **every binary selected-topology matrix (`P_*`) matches at `0.000e+00`**.
   - **Why This Matters for Stage 7 CI:** Both `aief_experiment_engine_v1.py` (`exact_array_equal_with_nan`, `atol=0, rtol=0`) and `aief_modular/oracle.py` (`exact_equal_with_nan`, `atol=0, rtol=0`) currently assert **0-ULP bitwise equality** against the saved Steam Deck `.npz` files. On GitHub Actions (`ubuntu-latest`, `glibc 2.39`), CI must therefore wire:
     - **Gate A (`atol=0.0, rtol=0.0` bitwise exact):** Authority lock SHA-256 verification + same-host modular-vs-monolithic `344`-array exact equivalence (`0.000e+00`) + discrete topology matrix (`P_*`) exact equality (`0.000e+00`) against frozen Steam Deck `.npz` + deterministic `Analysis v4` regeneration on frozen `runs/b57562a8ee77`.
     - **Gate B (`atol=1e-11, rtol=1e-11` cross-libm bounded drift):** Cross-platform trajectory comparison against Steam Deck `runs/5a9f093a2fe0` and `runs/b57562a8ee77` continuous floating-point arrays (`observed = 4.405e-13`), **without editing the SHA-256-locked `aief_experiment_engine_v1.py`**.

---

## 4. Non-Blocking Code & Build-Cache Hygiene Notes Flagged for Stage 5 / Post-Migration Maintenance

1. **`Pandas4Warning` in `AIEF_1_4_Twindow_sensitivity_analysis_v4.py` (lines `435, 641, 824, 910`):**
   - Under `pandas 3.1.0`, `DataFrame.set_index(..., verify_integrity=True)` emits `Pandas4Warning` (slated for removal in `pandas 4.0`; replace with `.index.is_unique` assertion in a separate post-migration code commit so organizational commits never mix with code edits).
2. **Inactive Nested Lean 4 CI Workflow (`lean/AIEFProofs/.github/workflows/lean_action_ci.yml`):**
   - GitHub Actions only discovers workflows inside root `.github/workflows/`. In Stage 7, promote/copy a root `.github/workflows/` CI suite covering (a) `verify_inventory.py`, (b) Python `pytest` + `Analysis v4` + `AIEF-1.3 N=100` revalidation, and (c) Lean 4 `lake build` inside `lean/AIEFProofs` (keeping `lean/AIEFProofs/.github/workflows/lean_action_ci.yml` intact so `AIEF_LEAN_PROJECT_LOCK_HASHES.txt` stays green!).
3. **Tracked Build Caches (`17` root `__pycache__/*.pyc` files + `~30` `lean/AIEFProofs/.lake/` files):**
   - Preserved untouched in Milestone 1; scheduled for clean archive/cache hygiene in Stage 4 with `.gitignore` protection against future re-introduction.
