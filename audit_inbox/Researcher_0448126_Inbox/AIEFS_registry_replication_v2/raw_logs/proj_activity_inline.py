# Inline code for AIEFS_PROJ-01 (projection activity finding)
# Run with: python3 proj_activity_inline.py
# Requires: aief_engine_v1.py on main @ 0a6a2f6 in same directory
import sys
sys.path.insert(0, '/home/user')
from aief_engine_v1 import *

config = DEFAULT_MODEL_CONFIG
protocol = DEFAULT_PROTOCOL_CONFIG
split_state, prefix = simulate_prefix(4619122171158768524, config, protocol)
branch_rngs = make_branch_rngs(4619122171158768524, protocol.branches)
rng = branch_rngs['continue']
result = simulate_future(split_state.clone(), prefix, 'continue', config, protocol, rng)
print(f"Pre_gap_violation_fraction={result['Pre_gap_violation_fraction']}")
print(f"Projection_active_fraction={result['Projection_active_fraction']}")
print(f"G_min_future={result['G_min_future']:.16f}")
print(f"Mean_row_sum={result['Mean_row_sum']:.16f}")
print(f"Max_row_sum={result['Max_row_sum']:.16f}")
print(f"CAPACITY={config.capacity:.16f}")
print(f"DELTA={config.delta:.16f}")
