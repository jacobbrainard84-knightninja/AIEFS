# Inline code for CF05 winner map verification
# Run with: python3 cf05_inline.py
# Requires: aief_experiment_engine_v1.py (sha256 ca4593fd...) on main @ 7ec6011d...
# CF05: audited_status = "Finite numerical observation" (not "Supported")
# Winner map (7,2,7) verified on 1 seed, 1000 steps -> PARTIAL (not full 32,001 saved states)
import sys
sys.path.insert(0, '/home/user')
from aief_engine_v1 import *
import numpy as np

config = DEFAULT_MODEL_CONFIG
protocol = DEFAULT_PROTOCOL_CONFIG
N = config.N
edges = compute_edges(N)
edge_list = list(zip(edges[0], edges[1]))

# K3 edges and expected winners: (7,2,7) for edges (25, 29, 59)
# Winner definition (from AIEFS_salvage.md L196):
#   "for each edge, which endpoint's s_i attains the min in min(s_i, s_j)"
#   s_i = min(1, c/(r_i + eps)) where r_i is row sum
#   Smaller s_i = larger row sum = winner
k3_spec = {25: 7, 29: 2, 59: 7}

split_state, prefix = simulate_prefix(4619122171158768524, config, protocol)
branch_rngs = make_branch_rngs(4619122171158768524, protocol.branches)
rng = branch_rngs['continue']
state = split_state.clone()

violations = 0
total = 0
for step in range(1000):
    R_physical, R_driver, info = advance_state(state, config, rng, shuffle_driver=False)
    row_sums = np.sum(state.B, axis=1)
    for edge_idx, expected in k3_spec.items():
        total += 1
        i, j = edge_list[edge_idx]
        if row_sums[i] > row_sums[j]:
            winner = i
        elif row_sums[j] > row_sums[i]:
            winner = j
        else:
            winner = -1
        if winner != expected:
            violations += 1

print(f"Steps checked: 1000 (out of 32,001 saved states in the claim)")
print(f"Total winner checks: {total}")
print(f"Winner violations: {violations}")
print(f"Winner map (7,2,7) holds: {violations == 0}")
print(f"Label: PARTIAL (1 seed, 1000 steps, not full 32,001 states)")
print(f"Note: CF05 audited_status on main is 'Finite numerical observation', not 'Supported'")
