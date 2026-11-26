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
    for k, v in g.PREDECLARED.items():
        assert results[k][0] == v, (k, results[k])
    assert ok
