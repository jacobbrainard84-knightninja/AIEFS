# AIEF Project Integration Map

This map is based on the project tree supplied by the project owner. Paths are relative to the project root on `deck@steamdeck`.

## Immutable compatibility authorities

### Engine v1

```text
aief_experiment_engine_v1.py
```

Role: certified AIEF-1.4 legacy numerical replay engine. Do not modify for modular-runner or Analysis-v4 work.

### Frozen AIEF-1.4 baseline authority

```text
runs/5a9f093a2fe0/manifest.json
runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz
runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_scalar_summary.csv
```

Role: mandatory 40-seed, seven-branch baseline authority.

### Successful T-window production oracle

```text
runs/b57562a8ee77/manifest.json
runs/b57562a8ee77/AIEF_1_4_Twindow_sensitivity_b57562a8ee77_scalar_summary.csv
runs/b57562a8ee77/AIEF_1_4_Twindow_sensitivity_b57562a8ee77_branch_diagnostics.npz
runs/b57562a8ee77/twindow_condition_status.csv
runs/b57562a8ee77/baseline_equivalence_certificate.json
runs/b57562a8ee77/baseline_equivalence_by_seed.json
runs/b57562a8ee77/condition_seed_*_rho_*.npz
```

Role: logical oracle for modular S01 equivalence. Compressed NPZ bytes are not expected to match; decompressed logical contents must match exactly.

### Existing Analysis v3 evidence

```text
AIEF_1_4_Twindow_sensitivity_analysis_v3.py
runs/b57562a8ee77/analysis/
```

Role: prespecified legacy-compatible analysis. Analysis v4 does not overwrite or replace it.

### Original production driver

```text
AIEF_1_4_Twindow_sensitivity.py
```

Role: successful monolithic S01 workflow oracle. Do not modify during modular certification.

## Frozen-authority lock

The supplied frozen-artifact and legacy-source hashes have been converted into:

```text
AIEF_1_4_FROZEN_5a9f093a2fe0.authority.lock.json
```

Lock-file SHA-256:

```text
57e4337c66f68eda116f32bbc446eb30bd068e0d39f1634eefdadcf02cfcbb5f
```

Source material:

```text
twindow_frozen_authority_hashes.txt
twindow_source_hashes_before.txt
```

The runner now requires this lock and verifies all three frozen artifacts plus Engine v1, the successful T-window driver, and Analysis v3. The lock becomes independently authoritative only after its own hash is pinned in source control, a signed release, or the protected evidence lineage. It must be placed at project root or supplied explicitly with `--authority-lock`.

## Modular platform source

Current modular scaffold is shown under:

```text
workspace-019ff86e-8322-7d0d-bcaf-ed27a8018c0f/
    aief_modular/
    AIEF_modular_driver_v1.py
    tests_modular/
    README_modular.md
    MODULAR_IMPLEMENTATION_REPORT.md
    pytest.ini
```

Recommended integration choices:

1. Copy the modular package, CLI, tests, and Analysis-v4 source into the project root under source control; or
2. Keep the workspace directory intact and set `PYTHONPATH` to include both project root and workspace directory.

Do not modify or overwrite the original engine, driver, Analysis v3, or oracle runs.

## Analysis v4 placement

Recommended source path:

```text
AIEF_1_4_Twindow_sensitivity_analysis_v4.py
```

Recommended design document:

```text
ANALYSIS_V4_DESIGN.md
```

Default output for the successful S01 run:

```text
runs/b57562a8ee77/analysis/v4/<analysis_execution_id>/
```

This safely coexists with the existing flat Analysis-v3 files under:

```text
runs/b57562a8ee77/analysis/
```

## Local commands from project root

### Analysis v4

If the v4 source and `aief_modular/` package are copied to project root:

```bash
python AIEF_1_4_Twindow_sensitivity_analysis_v4.py \
  runs/b57562a8ee77 \
  --bootstrap-seed 20260814 \
  --n-bootstrap 2000
```

If sources remain in the workspace directory:

```bash
PYTHONPATH="$PWD:$PWD/workspace-019ff86e-8322-7d0d-bcaf-ed27a8018c0f" \
python workspace-019ff86e-8322-7d0d-bcaf-ed27a8018c0f/AIEF_1_4_Twindow_sensitivity_analysis_v4.py \
  runs/b57562a8ee77 \
  --bootstrap-seed 20260814 \
  --n-bootstrap 2000
```

### Modular dry run

```bash
PYTHONPATH="$PWD:$PWD/workspace-019ff86e-8322-7d0d-bcaf-ed27a8018c0f" \
python workspace-019ff86e-8322-7d0d-bcaf-ed27a8018c0f/AIEF_modular_driver_v1.py \
  dry-run AIEF_1_4_S01
```

### Modular baseline-only execution

```bash
PYTHONPATH="$PWD:$PWD/workspace-019ff86e-8322-7d0d-bcaf-ed27a8018c0f" \
python workspace-019ff86e-8322-7d0d-bcaf-ed27a8018c0f/AIEF_modular_driver_v1.py \
  baseline-only AIEF_1_4_S01 \
  --frozen-manifest runs/5a9f093a2fe0/manifest.json \
  --frozen-npz runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz \
  --frozen-scalar runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_scalar_summary.csv \
  --authority-lock AIEF_1_4_FROZEN_5a9f093a2fe0.authority.lock.json \
  --output-root experiments
```

### Modular production execution

Use the same authority arguments with the `run` subcommand. Keep modular executions under a dedicated `experiments/` root.

## Catalog boundary

Run the modular catalog only on the dedicated modular output root:

```bash
python AIEF_modular_driver_v1.py catalog --output-root experiments
```

Do not point the modular catalog at the entire project root. The project contains many legacy `manifest.json` and `analysis_manifest.json` files with different schemas; those are separate evidence lineages and should not be misclassified as modular execution manifests.

## Existing related analyses

The following directories appear related to trajectory/recovery interpretation and should be treated as separate, previously generated evidence rather than merged automatically into Analysis v4:

```text
aief_1_4_trajectory_recovery/
aief_1_4_survival_outlier_spectral/
aief_1_4_results_analysis/
paired_seed_analysis/
runs_pivot_study/
```

Any comparison with Analysis v4 should be explicit and hash-linked. Do not pool outputs merely because names or estimands overlap.

## Archive and superseded material

```text
Older files/
workspace-019ff86e-8322-7d0d-bcaf-ed27a8018c0f.zip
AIEF_1_4_superseded_claims.csv
```

These are not default authorities. Use only when a manifest or evidence-lineage record explicitly identifies them.

## Current certification boundaries

Established externally by the supplied project history:

```text
monolithic frozen baseline: 40/40 seeds, 7/7 branches
successful T-window run:     200/200 conditions, 800 scalar rows
```

Still required for the new modular implementation:

```text
real modular one-condition smoke
modular 40-seed baseline certificate
selected modular-oracle comparisons
full 200-condition logical oracle comparison
authority-lock hash pinned independently and verified on the Steam Deck project tree
```

Still required for Analysis v4:

```text
real execution against runs/b57562a8ee77
input-hash validation
expected row-count validation
bundle read-back validation
scientific review of generated v4 summaries
```
