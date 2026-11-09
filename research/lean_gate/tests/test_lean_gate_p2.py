"""Lean P2: pin the concrete values proved in lean/AIEFGateCore (RedTeam.lean P2 section, EngineWitness.lean,
MatrixForm.lean) against the independent exact-rational transcription in lean_gate_crosscheck_v1.py, so a drift
between the Lean definitions and the transcription fails a test.

Run: /workspace/venv_req_cmp/bin/python -m pytest research/lean_gate/tests -q
"""
import sys
from fractions import Fraction as Fr
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import lean_gate_crosscheck_v1 as lg  # noqa: E402

P0 = lg.P(SimpleNamespace(dt=Fr(1, 10), gamma=Fr(1), capacity=Fr(1), scale_epsilon=Fr(0), a=Fr(1), q=Fr(1),
                          delta=Fr(0)), Fr)
# EngineWitness.pE: frozen production parameters as exact rationals.
PE = lg.P(SimpleNamespace(dt=Fr(1, 100), gamma=Fr(15, 1000), capacity=(1 - Fr(5, 100)) / Fr(3, 2),
                          scale_epsilon=Fr(1, 10**12), a=Fr(1), q=Fr(3, 2), delta=Fr(5, 100)), Fr)
K3 = [(0, 1), (0, 2), (1, 2)]
IDX = [lg.EDGES.index(e) for e in K3]


def k3vec(vals):
    v = [Fr(0)] * len(lg.EDGES)
    for k, x in zip(IDX, vals):
        v[k] = Fr(x)
    return v


def on_k3(v):
    return [v[k] for k in IDX]


def add(B, t, h):
    return [b + Fr(t) * x for b, x in zip(B, h)]


ZERO = [Fr(0)] * len(lg.EDGES)


def test_false_rel_x_only_values():
    # RedTeam.false_rel_x_only: B = (0,2,2), h = e0, t = 1, ctrl = (0,2,2): edge 0 maps 0 -> 1/3; claim 1/2.
    B, h = k3vec([0, 2, 2]), k3vec([1, 0, 0])
    assert on_k3(lg.lean_step(P0, ZERO, B))[0] == 0
    assert on_k3(lg.lean_step(P0, ZERO, add(B, 1, h)))[0] == Fr(1, 3)
    x = lg.prop(P0, ZERO, B)
    claim = 1 * (1 - P0.g * P0.dt) * lg.sc(P0, x)[0] * 1   # branchScale at ctrl 0 = node 0
    assert claim == Fr(1, 2)


def test_false_rel_h_only_values():
    # RedTeam.false_rel_h_only: B = (2,2,1), h = (1,-1,0), t = 1/10: edge 2 (h_2 = 0) moves 1/3 -> 10/31.
    B, h = k3vec([2, 2, 1]), k3vec([1, -1, 0])
    assert on_k3(lg.lean_step(P0, ZERO, B))[2] == Fr(1, 3)
    assert on_k3(lg.lean_step(P0, ZERO, add(B, Fr(1, 10), h)))[2] == Fr(10, 31)


def test_rel_strictly_weaker_identity():
    # RedTeam.rel_strictly_weaker: B = (0,2,2), h = (0,1,-1), t = 1/10, ctrl = (0,2,2): response (0, 1/40, -1/40).
    B, h = k3vec([0, 2, 2]), k3vec([0, 1, -1])
    d = [a - b for a, b in zip(lg.lean_step(P0, ZERO, add(B, Fr(1, 10), h)), lg.lean_step(P0, ZERO, B))]
    assert on_k3(d) == [0, Fr(1, 40), Fr(-1, 40)]
    # all-edge kernel fails for every controller choice on edge (0,1): (A h)_0 = 1, (A h)_1 = -1
    Ah = lg.incAct(h)
    assert Ah[0] == 1 and Ah[1] == -1 and Ah[2] == 0


def test_false_multiplier_no_gamma_values():
    # RedTeam.false_multiplier_no_gamma: estimator 1/2 vs mutant claim 5/9 at B0, vRay 2, t = 1/10.
    B, h = k3vec([1, 1, 1]), k3vec([1, -1, -1])
    t = Fr(1, 10)
    d = [a - b for a, b in zip(lg.lean_step(P0, ZERO, add(B, t, h)), lg.lean_step(P0, ZERO, B))]
    est = sum(di / t * hi for di, hi in zip(d, h)) / sum(hi * hi for hi in h)
    assert est == Fr(1, 2) and est != Fr(5, 9)


def test_engine_nonvacuous_value():
    # EngineWitness.engine_nonvacuous: drive = (eta+mu)*1 - mu = 1/25 on K3 edges, B = 8/3, h = vRay 2, t = 1/10.
    drive = k3vec([Fr(1, 25)] * 3)
    B, h = k3vec([Fr(8, 3)] * 3), k3vec([1, -1, -1])
    assert on_k3(lg.prop(PE, drive, B)) == [Fr(8, 3)] * 3
    sE = (1 - Fr(5, 100)) / Fr(3, 2) / (Fr(16, 3) + Fr(1, 10**12))
    assert sE < 1 and PE.eps > 0
    d = [a - b for a, b in zip(lg.lean_step(PE, drive, add(B, Fr(1, 10), h)), lg.lean_step(PE, drive, B))]
    k = Fr(1, 10) * (1 - Fr(15, 1000) * Fr(1, 100)) * sE
    assert on_k3(d) == [k, -k, -k]
    assert on_k3(d)[0] != Fr(1, 10) * sE      # engine_false_no_gamma


def matrix_step(p, D, Bm):
    """Engine matrix form (MatrixForm.stepM) in exact rationals, N x N lists."""
    n = len(Bm)
    clip = [[max(Bm[i][j] + p.dt * (D[i][j] - p.g * Bm[i][j]), Fr(0)) for j in range(n)] for i in range(n)]
    sym = [[Fr(0) if i == j else (clip[i][j] + clip[j][i]) / 2 for j in range(n)] for i in range(n)]
    row = [sum(r) for r in sym]
    on = any(p.gapA - p.gapQ * q < p.gapDelta for q in row)
    if not on:
        return sym
    s = [min(Fr(1), p.cap / (q + p.eps)) if q + p.eps != 0 else Fr(0) for q in row]
    return [[Fr(0) if i == j else sym[i][j] * min(s[i], s[j]) for j in range(n)] for i in range(n)]


def test_false_matrix_no_symm_values():
    # MatrixForm.false_matrix_no_symm: B01 = 1, B10 = 0, zero drive: matrix 9/20, edge-vector 9/10.
    PT = P0
    M = matrix_step(PT, [[Fr(0)] * 2] * 2, [[Fr(0), Fr(1)], [Fr(0), Fr(0)]])
    assert M[0][1] == Fr(9, 20)
    assert on_k3(lg.lean_step(PT, ZERO, k3vec([1, 0, 0])))[0] == Fr(9, 10)


def test_engine_rel_strictly_weaker_value():
    # EngineWitness.engine_rel_strictly_weaker: R = (3/7, 1, 1) -> drive (0, 1/25, 1/25); B = (0, 8/3, 8/3);
    # h = hw = (0, 1, -1); t = 1/10; ctrl = (0, 2, 2). Edge 0 has x_0 = h_0 = 0; response (0, k, -k), k = t a s_2.
    eta, mu = Fr(4, 100), Fr(3, 100)
    drive = k3vec([(eta + mu) * Fr(3, 7) - mu, (eta + mu) - mu, (eta + mu) - mu])
    B, h = k3vec([0, Fr(8, 3), Fr(8, 3)]), k3vec([0, 1, -1])
    x = lg.prop(PE, drive, B)
    assert on_k3(x) == [0, Fr(8, 3), Fr(8, 3)] and on_k3(h)[0] == 0
    Ah = lg.incAct(h)
    assert Ah[0] == 1 and Ah[1] == -1 and Ah[2] == 0          # all-edge kernel fails on edge (0,1)
    d = [a - b for a, b in zip(lg.lean_step(PE, drive, add(B, Fr(1, 10), h)), lg.lean_step(PE, drive, B))]
    s2 = (1 - Fr(5, 100)) / Fr(3, 2) / (Fr(16, 3) + Fr(1, 10**12))
    k = Fr(1, 10) * (1 - Fr(15, 1000) * Fr(1, 100)) * s2
    assert on_k3(d) == [0, k, -k]
