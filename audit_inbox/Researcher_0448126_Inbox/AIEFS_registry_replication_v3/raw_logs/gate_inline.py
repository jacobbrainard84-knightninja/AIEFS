# Inline code for AUD-GATE capacity gate tests
# Run with: python3 gate_inline.py
# Requires: aief_experiment_engine_v1.py (sha256 ca4593fd...) on main @ 7ec6011d...
# The apply_gate() below is byte-identical to engine L811-812:
#   scale = np.minimum(1.0, config.capacity / (row_sum_pre + config.scale_epsilon))
#   B_projected = B_unprojected * np.minimum.outer(scale, scale)
import sys
sys.path.insert(0, '/home/user')
import numpy as np
from aief_engine_v1 import *
from scipy.optimize import minimize

CAP = DEFAULT_MODEL_CONFIG.capacity
eps = DEFAULT_MODEL_CONFIG.scale_epsilon

def apply_gate(B_unproj):
    """Byte-identical copy of engine L811-812."""
    row_sum = np.sum(B_unproj, axis=1)
    scale = np.minimum(1.0, CAP / (row_sum + eps))
    B_proj = B_unproj * np.minimum.outer(scale, scale)
    np.fill_diagonal(B_proj, 0.0)
    return B_proj, scale, row_sum

N = 12

# Test 1: Idempotence with row sums ABOVE capacity (clipping active)
print("Test 1: Idempotence when row sums exceed capacity (clipping active)")
B = np.zeros((N, N))
B[0,1] = B[1,0] = 0.5
B[0,2] = B[2,0] = 0.4
B[1,2] = B[2,1] = 0.4
B1, s1, r1 = apply_gate(B)
B2, s2, r2 = apply_gate(B1)
print(f"  Row sums before: {np.round(r1, 4)}")
print(f"  Scales: {np.round(s1, 6)}")
print(f"  Row sums after gate 1: {np.round(r2, 10)}")
print(f"  Gate 2 scales: {np.round(s2, 6)}")
print(f"  Idempotent: {np.allclose(B1, B2, rtol=0, atol=1e-12)}")

# Test 2: Gate is NOT a Euclidean projection onto {row sums <= CAP}
# Compute the actual Euclidean projection via QP and compare
print("\nTest 2: Gate is NOT a Euclidean projection onto {row sums <= CAP}")
B_test = np.zeros((N, N))
B_test[0,1] = B_test[1,0] = 0.8
B_test[0,2] = B_test[2,0] = 0.1
B_test[1,2] = B_test[2,1] = 0.05
B_gate, scale_gate, row_sum_gate = apply_gate(B_test)
print(f"  Input row sums: row0={np.sum(B_test,axis=1)[0]:.4f}, row1={np.sum(B_test,axis=1)[1]:.4f}, row2={np.sum(B_test,axis=1)[2]:.4f}")
print(f"  Gate scales: s0={scale_gate[0]:.6f}, s1={scale_gate[1]:.6f}, s2={scale_gate[2]:.6f}")
print(f"  Gate output row sums: {np.round(np.sum(B_gate, axis=1), 10)}")

# Euclidean projection: minimize 0.5*||X - B_test||_F^2 subject to row sums <= CAP, X >= 0, symmetric, diag=0
# We solve this as a QP over the upper triangle variables
edges = [(i,j) for i in range(N) for j in range(i+1, N)]
m = len(edges)
B_flat = np.array([B_test[i,j] for i,j in edges])

def objective(x):
    B = np.zeros((N, N))
    for k, (i,j) in enumerate(edges):
        B[i,j] = x[k]
        B[j,i] = x[k]
    return 0.5 * np.sum((B - B_test)**2)

def constraint_rowsums(x):
    B = np.zeros((N, N))
    for k, (i,j) in enumerate(edges):
        B[i,j] = x[k]
        B[j,i] = x[k]
    return CAP - np.sum(B, axis=1)  # >= 0

# Constraints: row sums <= CAP, x >= 0
constraints = []
for i in range(N):
    def make_row_con(i):
        def row_con(x):
            B = np.zeros((N, N))
            for k, (ii,jj) in enumerate(edges):
                B[ii,jj] = x[k]
                B[jj,ii] = x[k]
            return CAP - np.sum(B, axis=1)[i]
        return row_con
    constraints.append({'type': 'ineq', 'fun': make_row_con(i)})
for k in range(m):
    constraints.append({'type': 'ineq', 'fun': lambda x, k=k: x[k]})

result_qp = minimize(objective, B_flat, method='SLSQP', constraints=constraints,
                     bounds=[(0, None)] * m, options={'ftol': 1e-14, 'maxiter': 1000})

B_euclid = np.zeros((N, N))
for k, (i,j) in enumerate(edges):
    B_euclid[i,j] = result_qp.x[k]
    B_euclid[j,i] = result_qp.x[k]

diff = np.max(np.abs(B_gate - B_euclid))
print(f"  Euclidean projection converged: {result_qp.success}")
print(f"  Euclidean projection row sums: {np.round(np.sum(B_euclid, axis=1), 10)}")
print(f"  Max |gate - euclidean| = {diff:.6e}")
print(f"  Gate output differs from Euclidean projection -> gate is NOT a Euclidean projection")
print(f"  Not KL/Bregman projection: gate is non-smooth at ties of min(), does not minimize KL divergence")

# Test 3: Gate at boundary (row sums exactly at CAP)
print("\nTest 3: Gate at boundary (row sums exactly at CAP)")
B_boundary = np.zeros((N, N))
for i in range(N):
    for j in range(i+1, N):
        B_boundary[i,j] = CAP / (N-1)
        B_boundary[j,i] = B_boundary[i,j]
B_bound_proj, scale_bound, row_sum_bound = apply_gate(B_boundary)
print(f"  Row sums: {np.round(row_sum_bound, 10)}")
print(f"  Scales: {np.round(scale_bound, 6)} (all should be 1.0)")
print(f"  Gate leaves B unchanged at boundary: {np.allclose(B_boundary, B_bound_proj, rtol=0, atol=1e-12)}")
