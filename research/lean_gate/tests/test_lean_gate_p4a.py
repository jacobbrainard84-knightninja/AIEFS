"""Lean P4a: pin the exact-rational values behind the witnesses of lean/AIEFGateCore/AIEFGateCore/Capacity.lean
(port of the guarded-capacity statements of Researcher 040282, restated on Params / GateOnM / stepM) against an
independent exact-rational transcription of the gate on 2x2 matrices, and pin the shape of the P4a mutants of
lean_mutation_check.py (M14-M23) without running Lean.

Run: /workspace/venv_req_cmp/bin/python -m pytest research/lean_gate/tests -q
"""
import sys
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import lean_mutation_check as mc  # noqa: E402

REPO = HERE.parents[2]
CAPACITY = (REPO / "lean" / "AIEFGateCore" / "AIEFGateCore" / "Capacity.lean").read_text()

# pE (EngineWitness.pE) as exact rationals: dt, gamma, cap, eps, gapA, gapQ, gapDelta
DT, GAMMA, A, Q, DELTA, EPS = Fr(1, 100), Fr(15, 1000), Fr(1), Fr(3, 2), Fr(5, 100), Fr(1, 10**12)
CAP = (A - DELTA) / Q


def scale(cap, eps, q):
    return min(Fr(1), cap / (q + eps))


def xo(a):
    return [[Fr(0), a], [a, Fr(0)]]


def row(x, i):
    return sum(x[i])


def gate_on(a, q, delta, x):
    return any(a - q * row(x, i) < delta for i in range(2))


def kernel(cap, eps, x):
    s = [scale(cap, eps, row(x, i)) for i in range(2)]
    return [[Fr(0) if i == j else x[i][j] * min(s[i], s[j]) for j in range(2)] for i in range(2)]


def gate(cap, eps, a, q, delta, x):
    return kernel(cap, eps, x) if gate_on(a, q, delta, x) else x


def test_engine_gate_link_and_cap():
    assert CAP * Q == A - DELTA and CAP == Fr(19, 30) and EPS > 0


def test_boundary_guard_fixes_but_kernel_moves_it():
    x = xo(CAP)
    assert not gate_on(A, Q, DELTA, x)                       # row = cap: strict guard does not fire
    assert gate(CAP, EPS, A, Q, DELTA, x) == x               # gateM_Xo_boundary
    assert kernel(CAP, EPS, x) != x                          # false_kernel_fixes_boundary
    k1 = kernel(CAP, EPS, x)
    assert kernel(CAP, EPS, k1) != k1                        # false_kernel_idempotent


def test_gate_not_nonexpansive_jump():
    a, b = CAP, CAP + Fr(1, 10**15)
    ga = gate(CAP, EPS, A, Q, DELTA, xo(a))[0][1]
    gb = gate(CAP, EPS, A, Q, DELTA, xo(b))[0][1]
    assert abs(ga - gb) > abs(a - b)                         # false_gate_nonexpansive


def test_active_and_inactive_witnesses():
    x1 = xo(Fr(1))
    assert gate_on(A, Q, DELTA, x1)
    g = gate(CAP, EPS, A, Q, DELTA, x1)
    assert g != x1 and all(row(g, i) < CAP for i in range(2))   # witness_gate_active
    assert scale(CAP, EPS, Fr(1)) < 1
    xh = xo(Fr(1, 2))
    assert not gate_on(A, Q, DELTA, xh) and gate(CAP, EPS, A, Q, DELTA, xh) == xh   # witness_gate_inactive


def test_row_sum_after_gate_never_exceeds_cap_on_a_grid():
    for k in range(0, 41):
        a = Fr(k, 20)
        g = gate(CAP, EPS, A, Q, DELTA, xo(a))
        assert all(row(g, i) <= CAP for i in range(2))       # gateM_feasible (finite sample, not a proof)


def test_negative_eps_and_broken_link_witnesses():
    # pN: cap 1, eps -1/2: kernel row of Xo(3/2) exceeds cap (false_kernel_row_no_eps)
    k = kernel(Fr(1), Fr(-1, 2), xo(Fr(3, 2)))
    assert row(k, 0) > 1
    # pB: cap 1/2 but guard threshold (a - delta)/q = 1: row 3/4 not gated and above cap
    assert not gate_on(Fr(1), Fr(1), Fr(0), xo(Fr(3, 4))) and Fr(3, 4) > Fr(1, 2)


def test_stepm_witness_proposal():
    # symM pE (Xo 100) 0 = Xo 1: pre = 0 + dt (100 - gamma 0) = 1, clip, symmetrise
    assert max(Fr(0) + DT * (Fr(100) - GAMMA * 0), Fr(0)) == 1


def test_capacity_lean_has_no_banned_markers_and_credits_by_handle_only():
    for bad in ("sorry", "admit", "native_decide", "axiom ", "unsafe", "implemented_by", "extern"):
        body = [l for l in CAPACITY.splitlines() if not l.lstrip().startswith(("--", "/-", "*"))]
        assert not any(bad in l for l in body), bad
    assert "Researcher 040282" in CAPACITY and "b18a27d" in CAPACITY
    assert "@" not in CAPACITY.replace("@[", "")


def test_p4a_mutants_shape():
    names = [m[0] for m in mc.MUTANTS]
    assert len(names) == 23 and names[13].startswith("M14") and names[22].startswith("M23")
    assert {m[1] for m in mc.MUTANTS[13:]} == {"Capacity.lean"}
    assert [m[2] for m in mc.MUTANTS[13:]].count("gateM_feasible") == 2
