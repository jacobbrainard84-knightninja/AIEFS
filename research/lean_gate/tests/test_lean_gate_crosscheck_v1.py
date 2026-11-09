"""Tests for research/lean_gate/lean_gate_crosscheck_v1.py (Lean P1 cross-check).

Run: /workspace/venv_req_cmp/bin/python -m pytest research/lean_gate/tests -q
"""
import json
import sys
from fractions import Fraction as Fr
from pathlib import Path
from types import SimpleNamespace

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import lean_gate_crosscheck_v1 as lg  # noqa: E402

REPO = HERE.parents[2]
COMMITTED = REPO / "research" / "lean_gate" / "results" / "lean_gate_crosscheck_v1.json"

# RedTeam.lean concrete instance: dt = 1/10, γ = 1, cap = 1, ε = 0, gate test 1 - q_i < 0, drive 0, B = 1 on K3.
P0 = lg.P(SimpleNamespace(dt=Fr(1, 10), gamma=Fr(1), capacity=Fr(1), scale_epsilon=Fr(0), a=Fr(1), q=Fr(1),
                          delta=Fr(0)), Fr)
K3 = [(0, 1), (0, 2), (1, 2)]
IDX = [lg.EDGES.index(e) for e in K3]


def k3vec(vals):
    v = [Fr(0)] * len(lg.EDGES)
    for k, x in zip(IDX, vals):
        v[k] = Fr(x)
    return v


DRIVE0 = [Fr(0)] * len(lg.EDGES)
B0 = k3vec([1, 1, 1])
VRAY2 = k3vec([1, -1, -1])


def on_k3(v):
    return [v[k] for k in IDX]


def test_transcription_matches_lean_stepB_B0():
    # RedTeam.stepB_B0: every K3 edge maps to 1/2.
    assert on_k3(lg.lean_step(P0, DRIVE0, B0)) == [Fr(1, 2)] * 3


def test_transcription_matches_lean_nonvacuous_plus():
    # RedTeam.nonvacuous_plus: stepB(B0 + (1/10) vRay 2) - stepB(B0) = (1/20) vRay 2.
    Bt = [b + Fr(1, 10) * v for b, v in zip(B0, VRAY2)]
    d = [a - b for a, b in zip(lg.lean_step(P0, DRIVE0, Bt), lg.lean_step(P0, DRIVE0, B0))]
    assert on_k3(d) == [Fr(1, 20), Fr(-1, 20), Fr(-1, 20)]


def test_transcription_matches_lean_false_drop_kernel():
    # RedTeam.false_drop_kernel: at t = 1 along e0, edge 0 gives 2/3 (claim would give 1).
    Bt = k3vec([2, 1, 1])
    assert on_k3(lg.lean_step(P0, DRIVE0, Bt))[0] == Fr(2, 3)


def test_transcription_matches_lean_false_two_sided():
    # RedTeam.false_two_sided: at t = -1/2 along vRay 2, edge 1 moves by 0 (formula: 1/4).
    Bt = [b - Fr(1, 2) * v for b, v in zip(B0, VRAY2)]
    d = [a - b for a, b in zip(lg.lean_step(P0, DRIVE0, Bt), lg.lean_step(P0, DRIVE0, B0))]
    assert on_k3(d)[1] == 0


def test_incAct_is_unsigned_incidence():
    Ah = lg.incAct(VRAY2)
    assert (Ah[0], Ah[1], Ah[2]) == (0, 0, -2) and all(x == 0 for x in Ah[3:])


@pytest.fixture(scope="module")
def report():
    return lg.run()


def test_run_passes(report):
    assert report["result"] == "PASS", report["fails"]


def test_committed_json_is_reproduced(report):
    assert json.loads(COMMITTED.read_text()) == json.loads(json.dumps(report, sort_keys=True))


def test_gate_branch_multiplier_matches_E22_exact_value(report):
    # ERRATA E22 (on main via PR #18) exact rational branch multiplier.
    assert report["components"]["GATE"]["lam_branch"] == 0.9987382469602354


def test_theorem_instances_have_zero_exact_residual(report):
    for c in report["components"].values():
        on = [s for s in c["samples"] if s["all_hypotheses"]]
        assert on and all(s["exact_residual_is_zero"] for s in on)


def test_negative_controls_detected(report):
    g = report["components"]["GATE"]
    assert g["N1_detected"] and g["N2_detected"]
    assert report["checks"]["N3_off_fiber"]["detected"]
    assert report["checks"]["N4_branch_crossing"]["detected"]
    # the crossing is the controller condition, not clip or gate
    for s in g["samples"]:
        if not s["all_hypotheses"]:
            assert s["hypotheses"]["is_ctrl_pert"] is False
            assert s["hypotheses"]["clip"] and s["hypotheses"]["same_gate"] and s["hypotheses"]["in_ctrl_ker"]


def test_fidelity(report):
    assert report["checks"]["F_base_max_abs_diff"] <= lg.FIDELITY_TOL
    for c in report["components"].values():
        assert all(s["fidelity_max_abs_diff"] <= lg.FIDELITY_TOL for s in c["samples"])


def test_known_false_wrong_constant_would_fail_engine_tolerance(report):
    for c in report["components"].values():
        assert c["N1_wrong_constant_rel_err"] > 100 * lg.ENGINE_TOL
        assert c["E"]["rel_err_engine_vs_lam_branch"] <= lg.ENGINE_TOL
