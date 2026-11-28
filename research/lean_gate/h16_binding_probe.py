#!/usr/bin/env python3
"""H16 binding-gate contraction probe (plan item H16; SPEC_P1_gate_identities.md section 18).

Author Auditor Seat 002, written fresh; stdlib + numpy only; does NOT import or edit the SHA-256-locked engine.
The map below mirrors aief_experiment_engine_v1.py lines 790-813 (B update, clip, symmetrise, zero diagonal, global
pre_violation trigger, scale = min(1, capacity/(row_sum_pre + scale_epsilon)), np.minimum.outer, zero diagonal),
with a FROZEN drive D = (eta + mu) R - mu (frozen R). Frozen engine parameters: dt 0.01, gamma 0.015, a 1, q 1.5,
delta 0.05, scale_epsilon 1e-12, eta 0.04, mu 0.03, N 12 (capacity 0.95/1.5).

Question (Auditor review b15c5e5, H16): is B -> F(B) a contraction when the gate fires? Method: (1) finite-difference
Jacobians at 200 seeded random gate-on states (seed 20261126), operator norms in l1 (edge-sum), entry-max (induced
inf) and l2; (2) exact fractions.Fraction confirmation of finite pairs B, B' (both gate-on) whose images are farther
apart than the states. A ratio > 1 at a pair refutes contraction in that metric; "not found" would not be proof.
Output: research/lean_gate/results/h16_binding_probe_v1.txt (python3 research/lean_gate/h16_binding_probe.py).
"""

import numpy as np, itertools, json, sys
from fractions import Fraction as Fr
dt, g, a, q, de, eps, eta, mu = 0.01, 0.015, 1.0, 1.5, 0.05, 1e-12, 0.04, 0.03
cap = (a - de) / q
N = 12

def F(B, D):
    U = B + dt * (D - g * B)
    U = np.maximum(U, 0.0); U = 0.5 * (U + U.T); np.fill_diagonal(U, 0.0)
    r = U.sum(1)
    on = bool(np.min(a - q * r) < de)
    if on:
        s = np.minimum(1.0, cap / (r + eps))
        U = U * np.minimum.outer(s, s); np.fill_diagonal(U, 0.0)
    return U, on

def norms(X):
    return dict(l1=np.abs(X).sum(), linf_entry=np.abs(X).max(), fro=np.linalg.norm(X),
                induced_inf=np.abs(X).sum(1).max())

def FrF(B, D):
    """exact rational version; B, D lists of lists of Fraction"""
    dtF, gF, aF, qF, deF, epsF = Fr(1,100), Fr(3,200), Fr(1), Fr(3,2), Fr(1,20), Fr(1,10**12)
    capF = (aF - deF) / qF
    n = len(B)
    P = [[max(B[i][j] + dtF*(D[i][j] - gF*B[i][j]), Fr(0)) for j in range(n)] for i in range(n)]
    U = [[Fr(0) if i == j else (P[i][j] + P[j][i]) / 2 for j in range(n)] for i in range(n)]
    r = [sum(U[i]) for i in range(n)]
    on = min(aF - qF*ri for ri in r) < deF
    if on:
        s = [min(Fr(1), capF / (ri + epsF)) for ri in r]
        U = [[Fr(0) if i == j else U[i][j] * min(s[i], s[j]) for j in range(n)] for i in range(n)]
    return U, on, r

rng = np.random.default_rng(20261126)
iu = np.triu_indices(N, 1)
def sym_from(v):
    M = np.zeros((N, N)); M[iu] = v; return M + M.T

# 1) Jacobian operator norms at random binding states (finite differences, edge parametrization)
res = {"cap": cap, "jacobian": []}
worst = {}
for trial in range(200):
    scale_r = rng.uniform(1.0, 1.5)
    v = rng.dirichlet(np.ones(len(iu[0]))) * cap * N / 2 * scale_r
    B = sym_from(v)
    Rm = sym_from(rng.uniform(0, 1, len(iu[0])))
    D = (eta + mu) * Rm - mu
    F0, on = F(B, D)
    if not on:
        continue
    J = np.zeros((len(v), len(v)))
    h = 1e-7
    for k in range(len(v)):
        e = np.zeros(len(v)); e[k] = h
        F1, on1 = F(sym_from(v + e), D)
        assert on1
        J[:, k] = (F1[iu] - F0[iu]) / h
    # edge-param norms: l1 (column sums), linf induced (row sums), spectral (Frobenius-metric Lipschitz)
    l1 = np.abs(J).sum(0).max(); li = np.abs(J).sum(1).max(); sp = np.linalg.norm(J, 2)
    res["jacobian"].append((l1, li, sp))
    for name, val, col in (("l1", l1, int(np.abs(J).sum(0).argmax())), ("linf", li, None), ("spectral", sp, None)):
        if name not in worst or val > worst[name][0]:
            worst[name] = (val, trial, col, v.copy(), D.copy())
J = np.array(res["jacobian"])
summary = {"n_binding_states": len(J),
           "l1_induced": [float(J[:,0].min()), float(J[:,0].max())],
           "linf_induced": [float(J[:,1].min()), float(J[:,1].max())],
           "spectral": [float(J[:,2].min()), float(J[:,2].max())],
           "rho_1_minus_gdt": 1 - g*dt}
print(json.dumps(summary, indent=1))

# 2) Exact finite pair in the l1 (edge-sum) metric from the worst l1 state: perturb one edge.
val, trial, col, v, D = worst["l1"]
t = 1e-6
Bv = sym_from(v); Bw = sym_from(v + t*np.eye(len(v))[col])
BF = [[Fr(x) for x in row] for row in Bv]; BW = [[Fr(x) for x in row] for row in Bw]
DF = [[Fr(x) for x in row] for row in D]
U0, on0, r0 = FrF(BF, DF); U1, on1, r1 = FrF(BW, DF)
din = sum(abs(BW[i][j]-BF[i][j]) for i in range(N) for j in range(N))
dout = sum(abs(U1[i][j]-U0[i][j]) for i in range(N) for j in range(N))
dinI = max(abs(BW[i][j]-BF[i][j]) for i in range(N) for j in range(N))
doutI = max(abs(U1[i][j]-U0[i][j]) for i in range(N) for j in range(N))
print(json.dumps({"exact_pair_l1": {"gate_on_both": on0 and on1,
      "min_rowsum_minus_cap_both": [float(min(r0) - Fr(19,30)), float(min(r1) - Fr(19,30))],
      "max_rowsum_minus_cap": [float(max(r0)-Fr(19,30)), float(max(r1)-Fr(19,30))],
      "l1_in": float(din), "l1_out": float(dout), "ratio": float(dout/din),
      "entrymax_in": float(dinI), "entrymax_out": float(doutI), "entrymax_ratio": float(doutI/dinI)}}, indent=1))

# 3) Exact finite pairs for entry-max (sign direction of worst J row) and Frobenius (top singular vector).
def exact_pair(v, D, dirv, t):
    Bv = sym_from(v); Bw = sym_from(v + t*dirv)
    BF = [[Fr(x) for x in row] for row in Bv]; BW = [[Fr(x) for x in row] for row in Bw]
    DF = [[Fr(x) for x in row] for row in D]
    U0, on0, r0 = FrF(BF, DF); U1, on1, r1 = FrF(BW, DF)
    dX = [[BW[i][j]-BF[i][j] for j in range(N)] for i in range(N)]
    dU = [[U1[i][j]-U0[i][j] for j in range(N)] for i in range(N)]
    mx = lambda A: max(abs(x) for row in A for x in row)
    fr2 = lambda A: sum(x*x for row in A for x in row)
    return {"gate_on_both": on0 and on1, "all_off_rows_nonneg": bool((Bw >= 0).all()),
            "entrymax_ratio": float(mx(dU)/mx(dX)), "fro_ratio": float(fr2(dU)/fr2(dX))**0.5}
for name in ("linf", "spectral"):
    val, trial, col, v, D = worst[name]
    J = np.zeros((len(v), len(v))); F0, _ = F(sym_from(v), D)
    for k in range(len(v)):
        e = np.zeros(len(v)); e[k] = 1e-7
        J[:, k] = (F(sym_from(v + e), D)[0][iu] - F0[iu]) / 1e-7
    if name == "linf":
        dirv = np.sign(J[int(np.abs(J).sum(1).argmax())])
    else:
        dirv = np.linalg.svd(J)[2][0]
    print(name, "jacobian_norm", float(val), json.dumps(exact_pair(v, D, dirv, 1e-7)))
