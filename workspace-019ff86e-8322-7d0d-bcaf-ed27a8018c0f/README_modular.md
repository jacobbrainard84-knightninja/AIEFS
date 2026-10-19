# AIEF Modular Experiment Driver Platform v1

This package modularizes experiment orchestration while importing the existing
`aief_experiment_engine_v1.py` numerical authority. It does not copy or modify
the engine step map.

## Commands

```bash
python AIEF_modular_driver_v1.py list-studies
python AIEF_modular_driver_v1.py describe AIEF_1_4_S01
python AIEF_modular_driver_v1.py dry-run AIEF_1_4_S01
python AIEF_modular_driver_v1.py baseline-only AIEF_1_4_S01 \
  --frozen-manifest runs/5a9f093a2fe0/manifest.json \
  --frozen-npz runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz \
  --frozen-scalar runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_scalar_summary.csv \
  --output-root experiments
python AIEF_modular_driver_v1.py run AIEF_1_4_S01 \
  --frozen-manifest runs/5a9f093a2fe0/manifest.json \
  --frozen-npz runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz \
  --frozen-scalar runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_scalar_summary.csv \
  --output-root experiments
python AIEF_modular_driver_v1.py catalog --output-root experiments
```

`--resume` is deliberately unsupported. Production always reruns the complete
frozen baseline gate.

## Required authorities

The modular source tree must be placed beside the existing authoritative files:

- `aief_experiment_engine_v1.py`
- `AIEF_1_4_Twindow_sensitivity.py`
- `AIEF_1_4_Twindow_sensitivity_analysis_v3.py`
- frozen baseline artifacts and successful T_window oracle artifacts

The current scaffold was built without those workspace files. Consequently,
full baseline, smoke, and oracle-equivalence execution must still be performed
in the authoritative repository before replacement status is considered.
