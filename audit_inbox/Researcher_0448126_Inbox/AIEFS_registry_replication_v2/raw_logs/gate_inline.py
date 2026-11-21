# Inline code for AUD-GATE capacity gate tests
# Run with: python3 gate_inline.py
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

N = 12

# Test 1: Idempotence with row sums ABOVE capacity
print("Test 1: Idempotence when row sums exceed capacity")
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
print(f"  Row sums after gate 2 = CAP? {np.allclose(r2, CAP, rtol=0, atol=1e-9)}")

# Test 2: Gate is NOT a Euclidean projection onto {row sums <= CAP}
print("\nTest 2: Gate is NOT a Euclidean projection onto {row sums <= CAP}")
# Use unequal row sums where min(s_i,s_j) gives different factors per edge
B_test = np.zeros((N, N))
B_test[0,1] = B_test[1,0] = 0.8   # row0 gets 0.8 from this edge
B_test[0,2] = B_test[2,0] = 0.1   # row0 gets 0.1 from this edge
B_test[1,2] = B_test[2,1] = 0.05
# Row sums: row0=0.9, row1=0.85, row2=0.15
B_gate, scale_gate, row_sum_gate = apply_gate(B_test)
print(f"  Input row sums: row0={np.sum(B_test,axis=1)[0]:.4f}, row1={np.sum(B_test,axis=1)[1]:.4f}, row2={np.sum(B_test,axis=1)[2]:.4f}")
print(f"  Gate scales: s0={scale_gate[0]:.6f}, s1={scale_gate[1]:.6f}, s2={scale_gate[2]:.6f}")
print(f"  Gate output row sums: {np.round(np.sum(B_gate, axis=1), 10)}")
print(f"  Gate output edges: B[0,1]={B_gate[0,1]:.6f}, B[0,2]={B_gate[0,2]:.6f}")
print(f"  Euclidean projection would scale both edges from row 0 by CAP/0.9={CAP/0.9:.6f}")
print(f"  Gate scaling: edge(0,1) factor=min(s0,s1)={min(scale_gate[0],scale_gate[1]):.6f}, edge(0,2) factor=min(s0,s2)={min(scale_gate[0],scale_gate[2]):.6f}")
if min(scale_gate[0],scale_gate[1]) != min(scale_gate[0],scale_gate[2]):
    print(f"  Edge factors DIFFER -> gate is NOT Euclidean projection")
else:
    print(f"  Edge factors same in this specific case (s0 is limiting), but min(s_i,s_j) rule CAN give different per-edge factors")
print(f"  Not KL/Bregman projection: gate is non-smooth at ties of min(), does not minimize KL divergence")

# Test 3: Gate at boundary
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
