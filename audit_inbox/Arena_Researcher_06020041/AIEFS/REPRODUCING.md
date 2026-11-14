# Reproducing AIEFS Benchmarks, Audits & Formal Proofs (`REPRODUCING.md`)

All commands below assume the working directory is the repository root.

> **Checked 2026-10-28 (local merge-prep, Researcher 001; Python 3.13.5, pins in `requirements.txt`).** Sections 3, 4 and 5 were re-run and match, after the corrections noted below. Section 2 currently FAILS on the merged tree (see the note there). Section 6 was not re-run in this pass. Section 7 was corrected on 2026-10-28 to match the round-4 Lean package and its audit log, and was re-run by Auditor Seat 002 (see the re-run note in §7).

---

## 1. Environment Setup (~15 seconds)

```bash
python3 -m venv .venv_repro
.venv_repro/bin/pip install -r requirements.txt
```

*(Note: Keep `.venv_repro` outside Git tracking or in `/tmp/aief_venv`.)*

---

## 2. Verify Full Repository Conservation, SHA-256 Inventory & Authority Locks (~2 seconds)

As designed on the arena branch, this checks the file list of commit `e47bad1` (`2,760` tracked files + `138` `.zip` entries = `2,898` SHA-256 digests), the controlled vocabularies across all `registry/*.csv` tables, the Lean lock hashes in `lean/AIEFProofs/AIEF_LEAN_PROJECT_LOCK_HASHES.txt` (12 entries on the arena tree; the current file has 3 lines, and the round-4 package's own source pins are the 8 entries of `AIEF_LEAN_SOURCE_SHA256SUMS.txt`, checked by `check_lean.sh` step 2), and `aief_modular.authority.verify_authority_lock()`. The merged tree no longer matches that design (see below):

```bash
PYTHONDONTWRITEBYTECODE=1 .venv_repro/bin/python3 audits/engineering/verify_inventory.py
```

- **Expected result (as written on the arena branch):** `ALL MILESTONE 1 CONSERVATION, VOCABULARY & AUTHORITY LOCK GATES PASSED.` (`exit 0`).
- **Actual result on the merged tree (2026-10-28):** the script fails at check `[1/5]` (conservation). It requires every file from commit `e47bad1`, and `main` has since deleted or moved files. Because of that it never reaches the vocabulary checks; those were run separately and pass. Per-path status is now in the `tree_check_2026_10_28` column of `registry/artifacts.csv` and `registry/relocation_map.csv` (`audits/engineering/validate_registry_against_tree.py`). The audit evidence has its own integrity check: `python "AI Agent Audits/evidence/verify_manifest.py"` (OK on 2026-10-28).

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

> **Important:** Always pass the two disjoint 50-seed production cohorts explicitly with `--cohort` so the script does not fall back to its built-in legacy absolute paths. (Corrected 2026-10-28: the earlier positional form `runs/c3da1ac707bf runs/73dca37cf93f` is rejected by the script with exit code 2.)

```bash
PYTHONDONTWRITEBYTECODE=1 .venv_repro/bin/python3 AIEF_1_3_paired_statistics_updated.py \
  --cohort validation_A=runs/c3da1ac707bf/AIEF_1_3_c3da1ac707bf_scalar_summary.csv \
  --cohort validation_B=runs/73dca37cf93f/AIEF_1_3_73dca37cf93f_scalar_summary.csv \
  --output-dir /tmp/repro_aief13_100seed
```

- **Expected result (`paired_report.txt` & `paired_effects.csv`):**
  - `valid = 100 / 100` unique paired seeds (`overlap = 0`)
  - `shuffle_R`: `mean_delta (D_B) = +0.305909`, 95% CI `[0.298939, 0.313030]`, `dz = 8.434`
  - `no_mu`: `mean_delta (D_B) = +0.271061`, `dz = 4.900`
  - `no_delay`: `mean_delta (D_B) = -0.027424`, `dz = -0.756`
- Re-run 2026-10-28 (about 12.5 s): all four lines match.
- **Interpretation (audit):** `shuffle_R` is a valid necessity test, but its outcome is forced by construction (shuffled mean R 0.371 < threshold 0.4286). See `registry/claims.csv` EMP-AIEF13-01.

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

- **Expected result:** Writes bundle `/tmp/repro_twindow_v4/v4/analysis_v4_<timestamp>_<id>/` (`analysis_identity_sha256 = 6e6dea18b81adb54286193ed7e0e52fe427d992d3437350d1547049976282355` — corrected 2026-10-28: the earlier text had a one-character typo, `...18881adb...`. The re-run value matches `audits/scientific/revalidated_summaries/twindow_v4_analysis_manifest.json`, and all 15 output hashes match that manifest; `24` regime rows, `72` DID rows, `12` topology rows, `9,600` recovery event rows. An earlier "`144` conditional DID rows" figure was removed on 2026-10-28: no output CSV of the re-run has 144 rows). Wall time on the re-run was about 6 s, including imports.

---

## 6. Verify Same-Host Exact Equivalence (`0.000e+00`) vs. Cross-`glibc` Trajectory Drift (`4.405e-13`) (~28 seconds)

- **On any host**, `aief_modular` and monolithic `AIEF_1_4_Twindow_sensitivity.py` produce **exact `0.000e+00` bit-for-bit equality** across all `344` condition output arrays (`0` ULP difference).
- **Across different Linux `glibc` `libm` versions** (e.g., Debian/Ubuntu `glibc 2.36–2.39` vs. the original `glibc 2.40` host environment that wrote `runs/5a9f093a2fe0` and `runs/b57562a8ee77`), binary selected-topology matrices (`P_*`) match at **`0.000e+00`**, whereas continuous 80,000-step coupled DDE floating-point trajectories exhibit **`max_abs_diff = 4.405e-13`** from 1-ULP transcendental `sin`/`exp` rounding. Full command and CI tolerance design are documented in [`audits/engineering/PATH_AND_LOCK_DEPENDENCY_AUDIT.md`](audits/engineering/PATH_AND_LOCK_DEPENDENCY_AUDIT.md).

---

## 7. Verify the Lean 4 Package (`lean/AIEFProofs/`)

Requires `elan`; the toolchain is pinned in `lean/AIEFProofs/lean-toolchain` (`leanprover/lean4:v4.33.1`), and Mathlib is pinned in `lake-manifest.json`. The package is the root `AIEFProofs.lean` plus 6 modules in `AIEFProofs/`: `Basic`, `CompleteGraphIncidence`, `ControllerFiber`, `ControllerFiberProjector`, `ControllerFiberQuotient`, `Smoke`.

```bash
cd lean/AIEFProofs
./check_lean.sh            # SKIP_CACHE=1 for offline re-runs; logs go to .check_logs/<UTC timestamp>/
```

- `check_lean.sh` runs 7 steps: toolchain pin, source/lock pins (`AIEF_LEAN_SOURCE_SHA256SUMS.txt`), imports, Mathlib cache, a clean `lake build`, a marker scan (no `sorry` / `admit` / user `axiom` etc.), and an axiom audit.
- **Expected result (audit round 4, `AI Agent Audits/evidence/logs/lean_r4/summary.txt`):** `RESULT: PASS`; `AUDITED 115 project declarations; allowed: propext Classical.choice Quot.sound`; marker scan `scanned 7 files, hits=0`.
- What it proves: linear-algebra / incidence facts about the controller fiber (including $\ker C_{\{2,7\}} = \operatorname{span}\{(1,-1,-1)\}$, `LEAN-CF-01`, and the round-4 package, `LEAN-R4`). It says nothing about the dynamics.
- **Re-run (2026-10-28):** cached build by Auditor Seat 002 at 886daf6: 7/7 PASS, 115 declarations, 3 allowed axioms, 0 warnings, 1,591 build jobs; `sha256sum -c` 8/8; audit_manifest pins OK. An earlier cached Seat 002 run, at merge-prep commit `11de659` (the Lean sources were identical through `9053b77`), also passed, with 12 style warnings, all in `Smoke.lean`. A from-source build without the Mathlib cache was started by Researcher 001 and stopped after about 11 minutes, so use the cache (step 4).
- **Changed after that re-run (2026-10-28, ERRATA E7):** `Smoke.lean` now imports `Mathlib.Data.Real.Basic` and `Mathlib.Tactic.Ring` instead of all of `Mathlib`, and `Smoke.lean` and `Basic.lean` have the standard header. The source hash file is updated. These sources are the ones built in the 886daf6 run above. The narrower imports cut the build from about 8,713 jobs to 1,591, and the warnings from 12 to 0.
- The Lean files' "Copyright … All rights reserved. Released under Apache 2.0 license …" headers are the standard Mathlib header form and do not conflict with the Apache-2.0 licence (corrected 2026-10-28; earlier wording called it an open conflict).
