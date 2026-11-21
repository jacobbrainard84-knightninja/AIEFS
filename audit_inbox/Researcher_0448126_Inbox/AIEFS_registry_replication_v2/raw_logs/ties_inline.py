# Inline code for AUD-TIES gate Jacobian computation
# Run with: python3 ties_inline.py
# Requires: aief_engine_v1.py on main @ 0a6a2f6 in same directory
import sys
sys.path.insert(0, '/home/user')
import numpy as np
from aief_engine_v1 import *

CAP = DEFAULT_MODEL_CONFIG.capacity
eps = DEFAULT_MODEL_CONFIG.scale_epsilon

def apply_gate(B_unproj):
    row_sum = np.sum(B_unproj, axis=1)
    scale = np.minimum(1.0, CAP / (row_sum + eps))
    B_proj = B_unproj * np.minimum.outer(scale, scale)
    np.fill_diagonal(B_proj, 0.0)
    return B_proj, scale, row_sum

def compute_gate_jacobian_equal_edge_Kn(n, w, h=1e-6):
    edge_list = [(i,j) for i in range(n) for j in range(i+1, n)]
    m = len(edge_list)
    B = np.zeros((n, n))
    for i, j in edge_list:
        B[i, j] = w
        B[j, i] = w
    B_proj, scale, row_sum = apply_gate(B)
    flat_proj = B_proj[np.triu_indices(n, k=1)]
    J = np.zeros((m, m))
    for input_idx, (ki, kj) in enumerate(edge_list):
        B_pert = B.copy()
        B_pert[ki, kj] += h
        B_pert[kj, ki] += h
        B_pert_proj, _, _ = apply_gate(B_pert)
        flat_pert = B_pert_proj[np.triu_indices(n, k=1)]
        J[:, input_idx] = (flat_pert - flat_proj) / h
    return B_proj, scale, J, edge_list

print("AUD-TIES: Gate Jacobian for equal-edge K_n (clipping active)")
print("n   k   computed_nonadd  formula_nonadd  formula_odd_defect")
for n in [3, 4, 5, 6]:
    k = n - 1
    w = CAP / (n-1) * 2.0
    B_proj, scale, J, edge_list = compute_gate_jacobian_equal_edge_Kn(n, w)
    diag_vals = np.abs(np.diag(J))
    off_diag_vals = []
    for out_idx in range(J.shape[0]):
        for in_idx in range(J.shape[1]):
            if in_idx != out_idx:
                oi, oj = edge_list[out_idx]
                ki, kj = edge_list[in_idx]
                if ki == oi or kj == oi or ki == oj or kj == oj:
                    off_diag_vals.append(abs(J[out_idx, in_idx]))
    mean_diag = np.mean(diag_vals)
    max_off = max(off_diag_vals) if off_diag_vals else 0
    computed = max_off / mean_diag if mean_diag > 0 else 0
    expected = 1.0 / np.sqrt(2 * k * (k - 1)) if k >= 2 else 0
    expected_odd = np.sqrt(2.0 / n)
    print(f"{n}   {k}   {computed:.6f}         {expected:.6f}           {expected_odd:.6f}")
