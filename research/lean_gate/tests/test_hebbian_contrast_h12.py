"""H12: the joint-energy red team (research/hebbian_contrast) gives its predeclared outcomes, the negative controls
behave (N600 exact-gradient drive never increases, N601 sign-flipped drive does), and the deterministic numbers quoted
in NOTE.md are pinned (audit note R1), so a wrong variant of the computation cannot pass on labels alone."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "hebbian_contrast"))
import energy_redteam_h12 as h  # noqa: E402

SEEDS = list(range(5))
TRIGGER_STEPS = [1758, 1757, 1762, 1758, 1758]
RISING_STEPS = [718, 778, 519, 711, 738]


@pytest.fixture(scope="module")
def results():
    return h.run(verbose=False)


def test_engine_copy_full_sha():
    assert len(h.ENGINE_SHA256) == 64
    _, full = h.load_engine_copy()
    assert full == h.ENGINE_SHA256


def test_predeclared_outcomes(results):
    assert set(results) == set(h.PREDECLARED)
    for k, v in h.PREDECLARED.items():
        assert results[k][0] == v, (k, results[k])


def test_pinned_counts(results):
    m600 = results["M600_engine_identical_omega_all_steps"][1]
    assert (m600["counted"], m600["increases"]) == (8793, 3466)
    seed, n, s, scale = m600["worst"]
    assert (seed, n) == (1, 1554)
    assert s == pytest.approx(0.28777192022532544, rel=1e-9)
    assert scale == pytest.approx(1.4709180813006302, rel=1e-9)
    m602 = results["M602_engine_production_omega_all_steps"][1]
    assert (m602["counted"], m602["increases"]) == (11080, 0)
    assert results["M601_engine_identical_omega_after_warmup"][1] == {"counted": 0}
    n600 = results["N600_control_weight_drive_is_cos"][1]
    assert (n600["counted"], n600["increases"]) == (8793, 0)
    n601 = results["N601_control_weight_drive_is_minus_cos"][1]
    assert (n601["counted"], n601["increases"]) == (8793, 8793)


def test_discrete_energy_observation_pinned():
    obs = h.discrete_energy_observation()
    assert [obs[k][0] for k in SEEDS] == TRIGGER_STEPS
    assert [obs[k][1] for k in SEEDS] == RISING_STEPS
    assert [obs[k][2] for k in SEEDS] == TRIGGER_STEPS            # one energy difference per pre-trigger step
    assert [obs[k][4] > obs[k][3] for k in SEEDS] == [True, True, False, True, True]   # 4 of 5 end higher


def test_tau_dt_sibling_pinned():
    got, det = h.tau_dt_observation()
    assert got == "INCREASE FOUND"
    assert (det["counted"], det["increases"]) == (8792, 3469)


def test_clip_projection_in_rate():
    """Unit check of the documented clip: at an edge with B_ij = 0 and a negative weight drive, F_B is projected to 0.
    Added because the pinned counts alone do not kill a variant with the projection removed (audit variant 1)."""
    import dataclasses
    import numpy as np

    mod, _ = h.load_engine_copy()
    cfg = dataclasses.replace(mod.DEFAULT_MODEL_CONFIG, tau=0.0)
    N = cfg.N
    rng = np.random.default_rng(7)
    theta = rng.random(N) * 2 * np.pi
    B = 0.01 * np.ones((N, N))
    np.fill_diagonal(B, 0.0)
    B[0, 1] = B[1, 0] = 0.0
    R = 0.9 * np.ones((N, N))
    R[0, 1] = R[1, 0] = 0.0                       # drive at (0,1) = -mu < 0 with B = 0: must be clipped
    c = cfg.eta + cfg.mu
    d = theta[None, :] - theta[:, None]
    F_th = np.asarray(cfg.omega) - np.mean(cfg.omega) + np.sum(B * np.sin(d), axis=1)
    F_B = c * R - cfg.mu - cfg.gamma * B
    F_B[0, 1] = F_B[1, 0] = 0.0
    g_th = -np.sum(B * np.sin(d), axis=1)
    g_B = -np.cos(d) + (cfg.mu + cfg.gamma * B) / c
    iu = np.triu_indices(N, 1)
    expected = float(g_th @ F_th + np.sum(g_B[iu] * F_B[iu]))
    s, _ = h.rate(theta, B, R, None, cfg, "engine")
    assert s == pytest.approx(expected, rel=1e-12, abs=1e-15)
    assert abs(g_B[0, 1] * (-cfg.mu)) > 1e-4       # the clip changes s, so the check can fail
