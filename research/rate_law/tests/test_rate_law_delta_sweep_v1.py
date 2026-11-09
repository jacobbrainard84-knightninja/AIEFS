"""Tests for research/rate_law/rate_law_delta_sweep_v1.py (AUD-RATELAW / ERRATA E22).

Run from the repository root:
    PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider research/rate_law/tests
The full predeclared sweep (46 deltas x 2 signs, exact rational path, controls) takes ~10 s, so it is run once per
session in the default path; there is no separate slow marker.
"""
import copy
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import rate_law_delta_sweep_v1 as m  # noqa: E402

REPO = m.REPO


# ---------------------------------------------------------------------------------------------------------------------
# 1. the frozen target is locked to the brief's numbers (editing the test to a "nicer" component must be visible)
# ---------------------------------------------------------------------------------------------------------------------
def test_pinned_inputs_unchanged():
    m.check_pins()


def test_frozen_target_component_locked():
    rep, x = m.load_frozen_component(m.TARGET)
    assert rep["seed"] == 4619122171158768524 and rep["rho"] == 1.0 and rep["T_w"] == 17.50291715
    assert x["nodes"] == [2, 7, 11] and x["J"] == [2, 7] and x["k"] == 2 and x["complete"]
    assert x["kernel_dim"] == 1 and x["n_tied_edges"] == 1
    assert x["delta"] == 1.062225811e-09
    assert x["delta_over_tied_gap"] == 438.5625016 and x["untied_gap_over_delta"] == 438.5625016
    assert x["rel_err_lam_vs_closed_form"] == 2.071385042e-08
    assert x["rel_err_lam_vs_state"] == 2.038720579e-08
    assert x["rel_err_r_vs_closed_form"] == 1.64063597e-05
    assert x["s_spread_J"] == 2.422062551e-12 and x["R_min"] == 0.9999997063


def test_target_is_the_whole_resolved_gap():
    """264 resolved two-sided components; the target is the only one with delta < 1e-6 and it carries the census max."""
    D = json.loads(m.KCK_JSON.read_text())
    ok = lambda x: (x["delta_over_tied_gap"] is None or x["delta_over_tied_gap"] >= 100) and (
        x["untied_gap_over_delta"] is None or x["untied_gap_over_delta"] >= 100)
    two = [(r, i, x) for r in D["replays"] for i, x in enumerate(r["comps"]) if x["kernel_dim"] > 0 and ok(x)]
    assert len(two) == 264
    small = [(r["seed"], r["rho"], i) for r, i, x in two if x["delta"] < 1e-6]
    assert small == [(m.TARGET["seed"], m.TARGET["rho"], m.TARGET["comp_index"])]
    rest = [x for r, i, x in two if x["delta"] >= 1e-6]
    assert len(rest) == 263 and max(x["rel_err_lam_vs_state"] for x in rest) == 2.095213469e-10
    C = json.loads(m.CENSUS_JSON.read_text())["two_sided_resolved_errors"]
    assert C["max_rel_err_lam_vs_closed_form"] == 2.071385042e-08
    assert C["max_rel_err_lam_vs_state_formula"] == 2.038720579e-08


def test_control_component_locked():
    _, x = m.load_frozen_component(m.CONTROL)
    assert x["nodes"] == [0, 1, 5, 6, 10] and x["delta"] == 1e-05 and x["kernel_dim"] == 5
    assert 1e-12 <= x["rel_err_lam_vs_state"] <= 2.1e-10


# ---------------------------------------------------------------------------------------------------------------------
# 2. full predeclared sweep (once per session)
# ---------------------------------------------------------------------------------------------------------------------
@pytest.fixture(scope="session")
def report():
    return m.run(quick=False, exact=True, verbose=False)


def test_historical_witness_bit_identical(report):
    w = report["witness"]
    assert w["ok"] and w["bit_identical"] and w["job_matches_stored_10sig"]
    assert w["sweep_rel_err_at_hist"] == w["job_rel_err_lam_vs_state"]
    assert float(f'{w["sweep_rel_err_at_hist"]:.10g}') == 2.038720579e-08


def test_grid_covers_1e12_to_1e4_with_dense_hist_decade(report):
    d = [p["delta"] for p in report["target_sweep"]["samples"]]
    assert min(d) == pytest.approx(1e-12) and max(d) == pytest.approx(1e-4)
    assert sum(1 for x in d if 1e-9 <= x < 1e-8) >= 16
    for p in report["target_sweep"]["samples"]:
        assert "plus" in p and "minus" in p             # both signs run separately


def test_samples_record_required_diagnostics(report):
    need_side = {"lam", "lam_fsum", "rel_residual", "leak", "gate_on", "n_clipped", "min_positivity_margin",
                 "min_untied_gap", "max_tied_gap", "s_spread_J", "lam_exact_float_input", "lam_exact_ideal_input"}
    for p in report["target_sweep"]["samples"]:
        assert need_side <= set(p["plus"]) and need_side <= set(p["minus"])
        for k in ("abs_err_plus_vs_state", "rel_err_plus_vs_state", "abs_err_plus_vs_closed_form", "rel_err_plus_vs_closed_form",
                  "admissible", "label", "pm_asym"):
            assert k in p
    b = report["frozen_target"]["base"]
    assert b["AJh"] <= m.AJH_TOL and b["Ah"] > 1 and b["gate_on"]


def test_exact_path_is_exact_branch(report):
    """On the branch the ideal-input exact multiplier is the same number at every delta and equals the exact
    branch formula (1 - gamma dt) sum h_e^2 s_ctrl(e)."""
    W = [p for p in report["target_sweep"]["samples"] if p["admissible"]]
    vals = {p["plus"]["lam_exact_ideal_input"] for p in W} | {p["minus"]["lam_exact_ideal_input"] for p in W}
    lam_bf = report["frozen_target"]["base"]["lam_exact_branch_formula"]
    assert max(abs(v - lam_bf) for v in vals) <= 1e-15


def test_branch_crossings_are_labelled_not_counted(report):
    S = report["target_sweep"]["samples"]
    bad = [p for p in S if not p["admissible"]]
    assert bad, "the +delta side must cross node 11's controller boundary at large delta"
    assert all(p["label"].startswith("branch_crossing:") for p in bad)
    win = report["decision"]["evidence"]["window"]
    assert all(p["delta"] > win["delta_hi"] for p in bad)
    assert report["control_crossed_boundary"]["pass"]
    assert report["control_crossed_boundary"]["off_fiber_all_rejected"]


def test_controls_pass(report):
    c = report["controls"]
    assert c == dict(witness=True, well_resolved=True, synthetic=True, crossed_boundary=True,
                     known_false_rejected=True, all_pass=True)
    wr = report["control_well_resolved"]
    assert wr["witness_bit_identical"] and wr["max_err_large_delta"] <= m.RESOLVED_BOUND
    assert wr["decision"]["label"] == m.NARROWED


def test_decision_is_consistent_with_samples(report):
    m.validate_report(report)
    assert report["decision"]["label"] in (m.NARROWED, m.UNEXPLAINED, m.INCONCLUSIVE)


def test_tampered_explained_label_is_rejected(report):
    r = copy.deepcopy(report)
    flip = m.UNEXPLAINED if r["decision"]["label"] == m.NARROWED else m.NARROWED
    r["decision"]["label"] = flip
    with pytest.raises(ValueError):
        m.validate_report(r)
    r2 = copy.deepcopy(report)
    for p in r2["target_sweep"]["samples"]:
        p.pop("admissible")
    with pytest.raises(ValueError):
        m.validate_report(r2)


def test_committed_result_matches_rerun(report):
    """The committed JSON is the deterministic output of the current script."""
    committed = json.loads((REPO / "research/rate_law/results/rate_law_delta_sweep_v1.json").read_text())
    fresh = json.loads(json.dumps(m._jsonable(report)))
    assert committed["decision"] == fresh["decision"]
    assert committed["controls"] == fresh["controls"]
    assert committed["target_sweep"]["samples"] == fresh["target_sweep"]["samples"]


# ---------------------------------------------------------------------------------------------------------------------
# 3. synthetic exact affine branch, mutation, crossed boundary
# ---------------------------------------------------------------------------------------------------------------------
def test_synthetic_affine_recovers_lambda():
    r = m.run_synthetic()
    assert r["recovers_lambda"] and r["top_err"] <= m.SYNTH_TOL and r["pass"]


def test_synthetic_mutated_multiplier_fails():
    r = m.run_synthetic(lam_ref=m.SYNTH_LAMBDA * (1 + 1e-8))
    assert not r["recovers_lambda"] and not r["pass"]


def test_synthetic_crossed_boundary_rejected():
    r = m.run_synthetic()
    crossed = [p for p in r["samples"] if not p["admissible"]]
    assert crossed and all(p["delta"] > 1e-5 for p in crossed)
    assert all(p["label"].startswith("branch_crossing:") for p in crossed)
    assert max(p["err"] for p in crossed) > 1e-2   # would have been a huge "residual" if accepted


# ---------------------------------------------------------------------------------------------------------------------
# 4. known-false fixtures through decide()
# ---------------------------------------------------------------------------------------------------------------------
def test_known_false_fixtures_rejected():
    kf = m.known_false_fixtures()
    assert kf["positive_fixture"] == m.NARROWED
    assert kf["cases"]["controls_failed"] == m.INCONCLUSIVE
    for name, lab in kf["cases"].items():
        assert lab != m.NARROWED, name


def test_single_cherry_picked_point_cannot_narrow():
    hd = m.TARGET["delta"]
    c, g = m.grid(False, hd)
    pts = [dict(delta=d, admissible=True, err=2e-8, ex=1e-13) for d in g]
    pts[-1]["err"] = 1e-14
    assert m.decide(pts, hd, 2e-8, True, exact_key="ex", coarse=c)["label"] == m.UNEXPLAINED


def test_decide_has_no_hardcoded_answer():
    """Same rule, two tables, two answers."""
    hd = m.TARGET["delta"]
    c, g = m.grid(False, hd)
    good = [dict(delta=d, admissible=True, err=2.2e-17 / d, ex=1e-13) for d in g]
    bad = [dict(delta=d, admissible=True, err=2e-8, ex=1e-13) for d in g]
    assert m.decide(good, hd, 2.04e-8, True, exact_key="ex", coarse=c)["label"] == m.NARROWED
    assert m.decide(bad, hd, 2.04e-8, True, exact_key="ex", coarse=c)["label"] == m.UNEXPLAINED
