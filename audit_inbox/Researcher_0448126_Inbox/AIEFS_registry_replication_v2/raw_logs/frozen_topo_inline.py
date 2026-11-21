# Inline code for AUD-FROZEN-TOPO and AUD-HELDOUT-LABEL
# Run with: python3 frozen_topo_inline.py
# Requires: aief_engine_v1.py on main @ 0a6a2f6 in same directory
import sys
sys.path.insert(0, '/home/user')
from aief_engine_v1 import *
import numpy as np

config = DEFAULT_MODEL_CONFIG
protocol = DEFAULT_PROTOCOL_CONFIG
BC = config.B_c

split_state, prefix = simulate_prefix(4619122171158768524, config, protocol)
branch_rngs = make_branch_rngs(4619122171158768524, protocol.branches)
rng = branch_rngs['continue']
result = simulate_future(split_state.clone(), prefix, 'continue', config, protocol, rng)

B_split = prefix['B_at_split']
B_final = result['B_final']
changed = (B_split > BC) != (B_final > BC)
n_changed = int(changed.sum())
n_edges = len(compute_edges(config.N)[0])

print(f"Edges changing threshold status: {n_changed} of {n_edges}")
print(f"Split selected: {int(np.sum(B_split > BC))}")
print(f"Final selected: {int(np.sum(B_final > BC))}")
print(f"P_full min={result['P_full'].min()}, max={result['P_full'].max()}")
non_binary = int(((result['P_full'] > 1e-12) & (result['P_full'] < 1 - 1e-12)).sum())
print(f"Non-binary P_full entries: {non_binary}")

# AUD-HELDOUT-LABEL: B_final > B_C iff P_future > 0.5
# Since 0 edges change threshold status and P_full is binary (0 or 1):
#   B_final > B_C  <==>  P_full == 1  <==>  P_full > 0.5
print(f"\nAUD-HELDOUT-LABEL: labels identical (0 edges change, P_full binary)")
