"""Lean P3: pin the values and statements proved in lean/AIEFGateCore (Bridge.lean, Persistence.lean,
PersistenceWitness.lean, EngineRedTeam.lean) against the independent exact-rational transcription in
lean_gate_crosscheck_v1.py, and pin the shape of the P3 mutation check (lean_mutation_check.py) without running
Lean.

Run: /workspace/venv_req_cmp/bin/python -m pytest research/lean_gate/tests -q
"""
import re
import sys
from fractions import Fraction as Fr
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import lean_gate_crosscheck_v1 as lg  # noqa: E402
import lean_mutation_check as mc  # noqa: E402

REPO = HERE.parents[2]
PE = lg.P(SimpleNamespace(dt=Fr(1, 100), gamma=Fr(15, 1000), capacity=(1 - Fr(5, 100)) / Fr(3, 2),
                          scale_epsilon=Fr(1, 10**12), a=Fr(1), q=Fr(3, 2), delta=Fr(5, 100)), Fr)
K3 = [(0, 1), (0, 2), (1, 2)]
IDX = [lg.EDGES.index(e) for e in K3]
A = 1 - PE.g * PE.dt                     # 1 - γ dt = 19997/20000


def k3vec(vals):
    v = [Fr(0)] * len(lg.EDGES)
    for k, x in zip(IDX, vals):
        v[k] = Fr(x)
    return v


def on_k3(v):
    return [v[k] for k in IDX]


def add(B, t, h):
    return [b + Fr(t) * x for b, x in zip(B, h)]


def sub(a, b):
    return [x - y for x, y in zip(a, b)]


VCTRL = [1, -1, -1]                       # pinned ControllerFiber.vCtrl
CCTRL = [[1, 1, 0], [1, 0, 1]]            # pinned ControllerFiber.CCtrl (rows = nodes 0, 1; cols = K3 edges)
DRIVE_E = k3vec([Fr(1, 25)] * 3)          # (η+μ)·1 − μ


# ---- Bridge.lean ---------------------------------------------------------------------------------------------

def test_pinned_vctrl_is_gate_vray_two_and_in_cctrl_kernel():
    # Bridge.vRay_two_eq_vCtrl and pinned CCtrl_mulVec_vCtrl, via the transcription's incidence action.
    h = k3vec(VCTRL)
    Ah = lg.incAct(h)
    assert (Ah[0], Ah[1], Ah[2]) == (0, 0, -2)
    assert [sum(r[e] * VCTRL[e] for e in range(3)) for r in CCTRL] == [0, 0]


def test_cctrl_rows_are_gate_incidence_rows():
    # Bridge.incAct_G3_ctrlRow: rows 0, 1 of the gate incidence on K3 are the rows of CCtrl.
    for e in range(3):
        unit = k3vec([1 if j == e else 0 for j in range(3)])
        Au = lg.incAct(unit)
        assert [Au[0], Au[1]] == [CCTRL[0][e], CCTRL[1][e]]


def test_wrong_bridge_vector_is_not_in_kernel_span():
    # Bridge.false_bridge_wrong_vector: pinned vRay 0 = (-1, -1, 1) is not a multiple of vCtrl, and is not in ker CCtrl.
    v0 = [-1, -1, 1]
    assert [sum(r[e] * v0[e] for e in range(3)) for r in CCTRL] != [0, 0]
    # Bridge.false_bridge_any_ctrl: with ctrl = (0, 0, 2), row 2 of A vCtrl is -2 != 0.
    assert lg.incAct(k3vec(VCTRL))[2] == -2


def test_bridge_lean_source_mentions_pinned_objects():
    src = (REPO / "lean/AIEFGateCore/AIEFGateCore/Bridge.lean").read_text()
    for name in ("inCtrlKer_iff_CCtrl", "inCtrlKer_iff_exists_smul_vCtrl", "inCtrlKer_iff_smul_vCtrl",
                 "vRay_two_eq_vCtrl", "stepB_add_smul_vCtrl", "false_bridge_wrong_vector", "false_bridge_any_ctrl"):
        assert re.search(rf"^theorem {name}\b", src, re.M), name
    assert "ControllerFiber.CCtrl_mulVec_eq_zero_iff_exists_smul" in src   # uses the pinned theorem


# ---- Persistence / PersistenceWitness ------------------------------------------------------------------------

def x_of(b):
    return b + PE.dt * (Fr(1, 25) - PE.g * b)


def test_engine_gated_persistence_values_first_steps():
    # PersistenceWitness.engine_gated_persistence: from B = 8/3, h = vRay 2, t = 1/10, R = 1 frozen. For the first
    # n steps the n-step response is exactly amp_n · vRay 2 with amp_n = t ∏ (1 − γdt) s_k, s_k = cap/(2 x_k + ε);
    # the gate fires and s_k < 1 at every step; the base state stays constant on K3 (bseq).
    h = k3vec(VCTRL)
    B, Bt = k3vec([Fr(8, 3)] * 3), add(k3vec([Fr(8, 3)] * 3), Fr(1, 10), h)
    b, amp = Fr(8, 3), Fr(1, 10)
    for _ in range(4):
        x = x_of(b)
        assert PE.cap < 2 * x                                  # Inv: gate fires (node rows 2x > cap)
        assert lg.gate_on(PE, lg.prop(PE, DRIVE_E, B))
        s = min(Fr(1), PE.cap / (2 * x + PE.eps))
        assert s < 1
        B, Bt = lg.lean_step(PE, DRIVE_E, B), lg.lean_step(PE, DRIVE_E, Bt)
        b, amp = x * s, amp * A * s
        assert on_k3(B) == [b] * 3                             # iterate_BE
        assert on_k3(sub(Bt, B)) == [amp, -amp, -amp]          # iterate_stepB_add_smul_of_branch
    assert amp < Fr(1, 10) * A ** 4                            # the perturbation decays (false_iterate_no_decay)


def test_engine_gated_persistence_invariant_float_long_run():
    # Float sanity check of inv_step over 10_000 steps (the Lean proof covers every n exactly).
    cap, eps, dt, g = 19 / 30, 1e-12, 0.01, 0.015
    b = 8 / 3
    for _ in range(10_000):
        x = b + dt * (1 / 25 - g * b)
        assert 2 * x - cap > 4e-4                              # margin ≈ 4.5e-4 in x, see inv_step
        b = x * min(1.0, cap / (2 * x + eps))


# ---- EngineRedTeam.lean --------------------------------------------------------------------------------------

def test_engine_false_drop_ker_values():
    # h = e0, t = 1/10 at B = 8/3: x' = (8/3 + u, 8/3, 8/3), u = 19997/200000; edge 1 moves.
    u = Fr(1, 10) * A
    assert u == Fr(19997, 200000)
    B, h = k3vec([Fr(8, 3)] * 3), k3vec([1, 0, 0])
    assert on_k3(lg.prop(PE, DRIVE_E, add(B, Fr(1, 10), h))) == [Fr(8, 3) + u, Fr(8, 3), Fr(8, 3)]
    after = on_k3(lg.lean_step(PE, DRIVE_E, add(B, Fr(1, 10), h)))[1]
    before = on_k3(lg.lean_step(PE, DRIVE_E, B))[1]
    assert after == Fr(8, 3) * PE.cap / (Fr(16, 3) + u + PE.eps)
    assert after != before                                     # claim: unchanged (h_1 = 0)


def test_engine_false_drop_hc1_values():
    u = Fr(1, 10) * A
    B, h = k3vec([Fr(8, 3)] * 3), k3vec(VCTRL)
    x1 = on_k3(lg.prop(PE, DRIVE_E, add(B, Fr(-1, 10), h)))
    assert x1 == [Fr(8, 3) - u, Fr(8, 3) + u, Fr(8, 3) + u]
    sE = PE.cap / (Fr(16, 3) + PE.eps)
    actual = on_k3(lg.lean_step(PE, DRIVE_E, add(B, Fr(-1, 10), h)))[1]
    claim = Fr(8, 3) * sE + Fr(-1, 10) * A * sE * (-1)
    assert actual == (Fr(8, 3) + u) * PE.cap / (Fr(16, 3) + 2 * u + PE.eps) and actual != claim


def test_engine_false_drop_clip_values():
    drive = k3vec([Fr(-3, 100)] * 3)                           # R = 0
    B, h, t = k3vec([0, 0, 0]), k3vec(VCTRL), Fr(1, 1000)
    assert on_k3(lg.prop(PE, drive, B)) == [0, 0, 0]
    assert on_k3(lg.prop(PE, drive, add(B, t, h))) == [Fr(13997, 20000000), 0, 0]
    assert not lg.gate_on(PE, lg.prop(PE, drive, B)) and not lg.gate_on(PE, lg.prop(PE, drive, add(B, t, h)))
    assert on_k3(lg.lean_step(PE, drive, add(B, t, h)))[1] == 0 != t * A * 1 * (-1)


# ---- lean_mutation_check.py shape (no Lean needed) ------------------------------------------------------------

def test_mutation_check_has_p3_mutants_and_engine_refutations():
    names = [m[0] for m in mc.MUTANTS]
    assert len(names) == 13 and names[10].startswith("M11") and names[12].startswith("M13")
    for m in mc.MUTANTS[:5]:
        assert m[6] is not None and "EngineRedTeam.engine_false_" in m[6] and "EngineWitness.pE" in m[6]
    for m in mc.MUTANTS[:3] + [mc.MUTANTS[7]]:
        assert all(": True)" in new for _, new, _ in m[3]), m[0]      # weakened to True, not deleted


def test_name_only_build_failure_does_not_count():
    errs = ["Mutant.lean:1:1: error(lean.unknownIdentifier): Unknown identifier `hker`"]
    kind = mc.classify(errs, "")
    assert kind.startswith("NAME-REFERENCE ONLY") and not mc.build_rejected(1, errs, kind)
    real = ["Mutant.lean:1:1: error: Application type mismatch: The argument"]
    assert mc.build_rejected(1, real, mc.classify(real, ""))
    assert not mc.build_rejected(0, [], "none")


def test_via_feeds_trivial_at_position():
    t = mc.via("@H X", "a b c", 1)
    assert t == "(fun a c => @H X a trivial c)"
