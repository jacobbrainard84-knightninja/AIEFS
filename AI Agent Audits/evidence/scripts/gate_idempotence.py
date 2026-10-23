"""NEW (response round). Point 5: is the gate idempotent? Size of the boundary jump? Is the eps-witness substantive?
Exact replica of AIEF_1_3_falsification_updated.py gate (also identical in engine advance_state)."""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); from _common import *
import AIEF_1_3_falsification_updated as f
from scipy.optimize import minimize
N = f.N; cap = (f.A - f.DELTA) / f.Q
def gate(B, eps=f.ZERO_TOL):
    B = B.copy(); rs = B.sum(1)
    if np.any(f.A - f.Q * rs < f.DELTA):
        s = np.minimum(1.0, cap / (rs + eps)); B *= np.minimum.outer(s, s); np.fill_diagonal(B, 0)
    return B
rng = np.random.default_rng(42); iu = np.triu_indices(N, 1); M = len(iu[0])
def sym(w): B = np.zeros((N, N)); B[iu] = w; return B + B.T
res = dict(n=0, triggered=0, bitwise_idempotent=0, max_abs_GG_minus_G=0.0, second_trigger=0, max_rowsum_out_minus_cap=-1.0,
           min_tight_margin=[], eps0_bitwise_idem=0, eps0_max_abs=0.0)
for trial in range(20000):
    kind = trial % 4
    if kind == 0: w = rng.uniform(0, 0.2, M)                                  # generic
    elif kind == 1: w = rng.uniform(0, 0.2, M) * (rng.random(M) < 0.3)         # sparse
    elif kind == 2:                                                            # just above boundary
        w = rng.uniform(0, 0.2, M); B = sym(w); w = w * cap / B.sum(1).max() * (1 + 10 ** rng.uniform(-15, -3))
    else:                                                                      # exactly at boundary (float)
        w = rng.uniform(0, 0.2, M); B = sym(w); w = w * cap / B.sum(1).max()
    X = sym(w); G = gate(X); GG = gate(G); res['n'] += 1
    res['triggered'] += int(np.any(f.A - f.Q * X.sum(1) < f.DELTA))
    res['second_trigger'] += int(np.any(f.A - f.Q * G.sum(1) < f.DELTA))
    res['bitwise_idempotent'] += int(np.array_equal(G, GG)); res['max_abs_GG_minus_G'] = max(res['max_abs_GG_minus_G'], float(np.abs(GG - G).max()))
    res['max_rowsum_out_minus_cap'] = max(res['max_rowsum_out_minus_cap'], float(G.sum(1).max() - cap))
    if np.any(f.A - f.Q * X.sum(1) < f.DELTA): res['min_tight_margin'].append(float(cap - G.sum(1).max()))
    G0 = gate(X, 0.0); GG0 = gate(G0, 0.0); res['eps0_bitwise_idem'] += int(np.array_equal(G0, GG0)); res['eps0_max_abs'] = max(res['eps0_max_abs'], float(np.abs(GG0 - G0).max()))
tm = np.array(res.pop('min_tight_margin'))
res['tightest_row_margin_after_gate'] = dict(min=float(tm.min()), max=float(tm.max()), median=float(np.median(tm)), eps_over_cap_times_cap=float(f.ZERO_TOL))
# boundary jump: scale factor as rowsum -> cap from above vs at/below cap
X = np.full((N, N), cap / (N - 1)); np.fill_diagonal(X, 0)
jumps = {}
for d in [1e-3, 1e-9, 1e-13, 0.0, -1e-9]:
    Xd = X * (1 + d); jumps[str(d)] = float(1 - gate(Xd)[0, 1] / Xd[0, 1])
res['one_minus_scale_vs_relative_excess'] = jumps; res['predicted_jump_eps_over_cap'] = f.ZERO_TOL / cap
# with eps=0: is the min-scaling map a Euclidean projection? compare to Euclidean projection (QP) on random proposals
Inc = np.zeros((N, M)); Inc[iu[0], range(M)] = 1; Inc[iu[1], range(M)] = 1
d_euc = []; d_obj = []
for k in range(5):
    x = rng.uniform(0, 2 * cap / (N - 1) * 1.6, M); wa = gate(sym(x), 0.0)[iu]
    r = minimize(lambda w: 0.5 * np.sum((w - x) ** 2), np.minimum(x, wa), jac=lambda w: w - x, method='SLSQP', bounds=[(0, None)] * M,
                 constraints=[{'type': 'ineq', 'fun': lambda w: cap - Inc @ w, 'jac': lambda w: -Inc}], options={'ftol': 1e-15, 'maxiter': 1000})
    d_euc.append(float(np.max(np.abs(r.x - wa)))); d_obj.append(float(0.5 * np.sum((wa - x) ** 2) - r.fun))
res['eps0_vs_euclidean_projection_max_abs_diff'] = d_euc; res['eps0_sqdist_excess_over_euclid'] = d_obj
for k, v in res.items(): print(k, v)
dump('gate_idempotence.json', res)
