"""H12: the joint-energy red team (research/hebbian_contrast) gives its predeclared outcomes, and the negative
controls behave: N600 (exact gradient drive) never increases, N601 (sign-flipped drive) does."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "hebbian_contrast"))
import energy_redteam_h12 as h  # noqa: E402


def test_predeclared_outcomes():
    res = h.run(verbose=False)
    assert set(res) == set(h.PREDECLARED)
    for k, v in h.PREDECLARED.items():
        assert res[k][0] == v, (k, res[k])
    # the increase is far above the rounding tolerance
    seed, n, s, scale = res["M600_engine_identical_omega_all_steps"][1]["worst"]
    assert s / scale > 0.1


def test_discrete_energy_rises_on_engine_steps():
    obs = h.discrete_energy_observation()
    assert all(v[0] is not None for v in obs.values())        # gate fires in every seed (bounds the regime)
    assert all(v[1] > 0 for v in obs.values())                # every seed has steps where E rises
    assert sum(v[4] > v[3] for v in obs.values()) >= 1        # and at least one seed ends higher than it started
