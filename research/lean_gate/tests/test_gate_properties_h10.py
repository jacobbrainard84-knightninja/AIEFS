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
    """Negative control for the witness. Without it, M500 still fails P5 (an always-projected row ends inside the
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
