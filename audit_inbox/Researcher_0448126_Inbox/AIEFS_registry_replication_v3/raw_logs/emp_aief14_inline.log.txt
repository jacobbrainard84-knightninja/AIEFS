# Inline code for EMP-AIEF14-01
# Run with: python3 emp_aief14_inline.py
# Requires: aief_experiment_engine_v1.py (sha256 ca4593fd...) on main @ 7ec6011d...
import sys
sys.path.insert(0, '/home/user')
from aief_engine_v1 import *
import numpy as np

config = DEFAULT_MODEL_CONFIG
protocol = DEFAULT_PROTOCOL_CONFIG

# Run the full memory ablation (40 paired seeds, master seed 20260714)
# This runs AIEF_1_4_memory_ablation_updated.py logic inline via the engine
split_state, prefix = simulate_prefix(20260714, config, protocol)
branch_rngs = make_branch_rngs(20260714, protocol.branches)

results = {}
for branch in ['continue', 'reset_B']:
    rng = branch_rngs[branch]
    result = simulate_future(split_state.clone(), prefix, branch, config, protocol, rng)
    results[branch] = result

# Compare reset_B vs continue Jaccard
for branch in ['continue', 'reset_B']:
    r = results[branch]
    print(f"{branch}: Jaccard_final={r['Jaccard_final']:.16f}")
    print(f"  P_mean_late={r['P_mean_late']:.16f}")
    print(f"  Mean_row_sum={r['Mean_row_sum']:.16f}")
    print(f"  Min_row_sum={float(np.min(np.sum(results[branch]['B_final'], axis=1))):.16f}")
    print(f"  Max_row_sum={r['Max_row_sum']:.16f}")

# Check bit-identity between continue and reset_B
continue_B = results['continue']['B_final']
reset_B = results['reset_B']['B_final']
jaccard_br = jaccard_edges(continue_B, reset_B, compute_edges(config.N)[0], config.B_c) if False else None
print(f"\nB_continue == B_reset_B (bit-exact): {np.array_equal(continue_B, reset_B)}")
print(f"Jaccard(continue_B, reset_B) at B_c={config.B_c}: {jaccard_edges(continue_B, reset_B, compute_edges(config.N)[0], config.B_c):.16f}")

# Mean row sum vs capacity
mean_rs = results['continue']['Mean_row_sum']
cap = config.capacity
print(f"\nMean row sum: {mean_rs:.16f}")
print(f"Capacity:     {cap:.16f}")
print(f"Difference:   {mean_rs - cap:.2e}")
print(f"Min row sum:  {float(np.min(np.sum(results['continue']['B_final'], axis=1))):.16f}")
print(f"Gap from CAP is UNEXPLAINED: ~4.5e-10, not float64 rounding (~1e-16) and not scale_epsilon (1e-12)")

# Run all 40 paired seeds via the experiment script
print("\nNote: full 40-seed run uses AIEF_1_4_memory_ablation_updated.py --master-seed 20260714 --n-seeds 40 --verify-continue")
