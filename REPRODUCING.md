# Reproducing AIEFS Benchmarks, Audits & Formal Proofs (`REPRODUCING.md`)

All commands below assume working directory `/home/user/AIEFS` (repository root).

---

## 1. Environment Setup (~15 seconds)

```bash
python3 -m venv .venv_repro
.venv_repro/bin/pip install numpy scipy pandas matplotlib pytest
```

*(Note: Keep `.venv_repro` outside Git tracking or in `/tmp/aief_venv`.)*

---

## 2. Verify Full Repository Conservation, SHA-256 Inventory & Authority Locks (~2 seconds)

Verifies all `2,760` tracked files + `138` `.zip` entries (`2,898` SHA-256 digests), controlled vocabularies across all `registry/*.csv` tables, all `12` Lean 4 source lock hashes, and `aief_modular.authority.verify_authority_lock()`:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv_repro/bin/python3 audits/engineering/verify_inventory.py
```

- **Expected result:** `ALL MILESTONE 1 CONSERVATION, VOCABULARY & AUTHORITY LOCK GATES PASSED.` (`exit 0`).

---

## 3. Run Modular Platform Unit + Live 176,000-Step Round-Trip Suite (~15 seconds)

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH="$PWD:$PWD/AIEF_Experiments/aief_modular_platform_v1_analysis_v4" \
AIEF_RUN_SLOW_TESTS=1 \
.venv_repro/bin/pytest AIEF_Experiments/aief_modular_platform_v1_analysis_v4/tests_modular
```

- **Expected result:** `41 passed, 1 skipped` in `~15s` (the single skip is an optional test requiring an externally pre-generated certification directory).

---

## 4. Reproduce AIEF-1.3 Disjoint $N = 100$ Paired Ablation Statistics (~1 second)

> **Important:** Always pass the two disjoint 50-seed production cohorts (`runs/c3da1ac707bf` and `runs/73dca37cf93f`) explicitly on the CLI so the script does not fall back to legacy Steam Deck paths.

```bash
PYTHONDONTWRITEBYTECODE=1 .venv_repro/bin/python3 AIEF_1_3_paired_statistics_updated.py \
  runs/c3da1ac707bf runs/73dca37cf93f \
  --output-dir /tmp/repro_aief13_100seed
```

- **Expected result (`paired_report.txt` & `paired_effects.csv`):**
  - `valid = 100 / 100` unique paired seeds (`overlap = 0`)
  - `shuffle_R`: `mean_delta (D_B) = +0.305909`, 95% CI `[0.298939, 0.313030]`, `dz = 8.434`
  - `no_mu`: `mean_delta (D_B) = +0.271061`, `dz = 4.900`
  - `no_delay`: `mean_delta (D_B) = -0.027424`, `dz = -0.756`

---

## 5. Reproduce AIEF-1.4 Dual-Horizon $T_{\text{window}}$ Sensitivity Analysis v4 (~0.5 seconds)

Runs deterministic bootstrap difference-in-differences across all `200` conditions (`40` seeds × `5` $\rho$ values) in frozen oracle `runs/b57562a8ee77`:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH="$PWD:$PWD/AIEF_Experiments/aief_modular_platform_v1_analysis_v4" \
.venv_repro/bin/python3 \
  AIEF_Experiments/aief_modular_platform_v1_analysis_v4/AIEF_1_4_Twindow_sensitivity_analysis_v4.py \
  runs/b57562a8ee77 \
  --output-root /tmp/repro_twindow_v4 \
  --bootstrap-seed 20260814 \
  --n-bootstrap 2000
```

- **Expected result:** Writes bundle `/tmp/repro_twindow_v4/analysis_v4_<timestamp>_<id>/` (`analysis_identity_sha256 = 6e6dea18881adb54286193ed7e0e52fe427d992d3437350d1547049976282355`, `24` regime rows, `72` DID rows, `12` topology rows, `9,600` recovery event rows, `144` conditional DID rows).

---

## 6. Verify Same-Host Exact Equivalence (`0.000e+00`) vs. Cross-`glibc` Trajectory Drift (`4.405e-13`) (~28 seconds)

- **On any host**, `aief_modular` and monolithic `AIEF_1_4_Twindow_sensitivity.py` produce **exact `0.000e+00` bit-for-bit equality** across all `344` condition output arrays (`0` ULP difference).
- **Across different Linux `glibc` `libm` versions** (e.g., Debian/Ubuntu `glibc 2.36–2.39` vs. the original SteamOS `glibc 2.40` environment that wrote `runs/5a9f093a2fe0` and `runs/b57562a8ee77`), binary selected-topology matrices (`P_*`) match at **`0.000e+00`**, whereas continuous 80,000-step coupled DDE floating-point trajectories exhibit **`max_abs_diff = 4.405e-13`** from 1-ULP transcendental `sin`/`exp` rounding. Full command and CI tolerance design are documented in [`audits/engineering/PATH_AND_LOCK_DEPENDENCY_AUDIT.md`](audits/engineering/PATH_AND_LOCK_DEPENDENCY_AUDIT.md).

---

## 7. Verify Lean 4 Formal Proof (`ControllerFiber.lean`)

Requires `elan` / Lean toolchain specified in `lean/AIEFProofs/lean-toolchain` (`leanprover/lean4:v4.29.0-rc8`):

```bash
cd lean/AIEFProofs
lake build
```

- **Expected result:** Compiles `AIEFProofs/Basic.lean`, `AIEFProofs/ControllerFiber.lean`, and `AIEFProofs/Smoke.lean` with `0` warnings, `0` `sorry`, and `0` `admit`, machine-verifying $\ker C_{\{2,7\}} = \operatorname{span}\{(1,-1,-1)\}$.
