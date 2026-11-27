"""H10 gate properties (research/gate_properties): the unmutated engine block passes, every mutant/control matches its
predeclared outcome, and the ε-band witness really sits in the band. Stdlib + numpy only."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "gate_properties"))
import gate_h10 as g  # noqa: E402


def test_eps_band_witness_is_in_band():
    M = g.eps_band_witness()
    rs = M.sum(axis=1).max()
    assert 1.0 - 1.5 * rs >= 0.05                      # engine: no pre_violation
    assert (1.0 - 0.05) / 1.5 / (rs + 1e-12) < 1.0     # but the scale would be < 1


def test_predeclared_table_complete():
    assert set(g.PREDECLARED) == set(g.MUTANTS) | set(g.EQUIV)
    assert sorted(int(k[1:4]) for k in g.MUTANTS) == list(range(500, 507))


def test_run_matches_predeclared():
    ok, results, obs = g.run(verbose=False)
    assert results["UNMUTATED"] == "PASS"
    for k in g.PREDECLARED:
        assert results[k][0] == g.expected(k), (k, results[k])
    # the predeclared table itself is unchanged from commit 1; exactly one recorded deviation
    assert g.PREDECLARED["M504_scale_epsilon_dropped"] == "SURVIVES" and set(g.OBSERVED_DEVIATIONS) == {"M504_scale_epsilon_dropped"}
    assert ok


def test_witness_is_what_kills_always_project_on_values():
    """CHARACTERIZATION TEST, not a predeclared control (audit note N6): it was added in commit 2, failed on its first
    run, and was rewritten in commit 3 to assert what was observed. Without the witness, M500 still fails P5 (an always-projected row ends inside the
    eps band, so projecting again shrinks it), but it no longer fails P2: only the witness separates the two on a
    single application. Found on the first run of this test; recorded, not tuned."""
    block = g.engine_block()
    m500 = g.make_gate(g.mutate(block, g.MUTANTS["M500_always_project"]))
    cases = g.random_cases()
    real_witness = g.eps_band_witness
    try:
        g.eps_band_witness = lambda: cases[1]
        without = {p for p, _ in g.properties(m500, cases)}
    finally:
        g.eps_band_witness = real_witness
    with_w = {p for p, _ in g.properties(m500, cases)}
    assert without == {"P5_idempotent_float"}
    assert "P2_values_match_oracle" in with_w


# ---- audit follow-up (Auditor Seat 002, CLEAN WITH NOTES on f31da4c) ----
import h10_followup_checks as fc  # noqa: E402


def test_followup_predeclared_outcomes():
    """M507/M508 were predeclared in commit 4c275ca before these tests existed."""
    ok, results, _ = g.run(verbose=False)
    for k, v in g.PREDECLARED_FOLLOWUP.items():
        assert results[k][0] == v, (k, results[k])
    assert ok


def test_above_cap_witness_is_what_kills_m507():
    """Characterization (not predeclared): M507 survives the random cases + eps-band witness alone; the above-cap
    witness is what kills it, through the trigger (P1)."""
    w = g.above_cap_witness()
    x = w[0, 1]
    assert g.F(float(x)) > g.CAP and 1.0 - 1.5 * x < 0.05 and 1.0 - 1.5 * x >= 0.05 - 1e-9
    m507 = g.make_gate(g.mutate(g.engine_block(), g.MUTANTS_FOLLOWUP["M507_trigger_loosened_delta_minus_1e-9"]))
    real = g.witnesses
    try:
        g.witnesses = lambda: [g.eps_band_witness()]
        assert g.properties(m507, g.random_cases()) == []
    finally:
        g.witnesses = real
    assert ("P1_trigger_matches_oracle", 151) in g.properties(m507, g.random_cases())


def test_m504_breakdown_pinned():
    b = fc.m504_breakdown()
    assert (b["p2_cases"], b["p5_cases"]) == (84, 23)
    assert 1.5e-12 < b["max_rel_dev"] < 1.6e-12          # above rtol 1e-12: the predeclared arithmetic was wrong
    h = b["binding_row_ulps_vs_fl_cap"]
    assert (h.get(0), h.get(1), h.get(2)) == (62, 19, 4)


def test_spillover_rule_no_exceptions():
    r = fc.spillover_rule()
    assert (r["projected_cases"], r["below_cap_rows"], r["below_cap_rows_losing"]) == (89, 574, 457)
    assert r["losing_with_over_cap_neighbour"] == 457
    assert r["over_cap_neighbour_but_no_loss"] == 0 and r["losing_only_via_own_eps_band"] == 0
    assert abs(r["max_over_cap_row_gap_below_cap"] - 0.35158304296995124) < 1e-15


def test_m506_ulp_scan():
    r = fc.m506_ulp_scan()
    assert r["x_with_g_equal_delta"] == 0 and r["closest_g_in_ulps_of_delta"] == 6
