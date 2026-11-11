import numpy as np
import AIEF_1_4_memory_ablation_updated as prod

with np.load('runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz') as npz:
    frozen_keys = set(npz.files)

required_keys = set()
for branch in ['B_carrier_only', 'full_reset', 'continue']:
    for matrix_key in prod.BRANCH_MATRIX_KEYS:
        required_keys.add(f"{branch}_seed_*_{matrix_key}")

missing = required_keys - frozen_keys
if missing:
    print(f"Missing keys in frozen data: {missing}")
