"""Synthetic-only tests for the Analysis v4.1 candidate held-event logic.

No real trajectory files are read and nothing is regenerated. The v4 module
is imported unchanged so its exact ``_held_index`` expression is exercised.

Run explicitly (pytest.ini testpaths only covers tests_modular):
    python -m pytest tests/test_v4_1_held_event.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import AIEF_1_4_Twindow_sensitivity_analysis_v4 as v4  # noqa: E402
import AIEF_1_4_Twindow_sensitivity_analysis_v4_1 as v41  # noqa: E402

DURATION = 17.5
GRIDS = {
    "arange_dt_0p01": np.arange(0.0, 40.0, 0.01),
    "arange_dt_0p05": np.arange(0.0, 40.0, 0.05),
    "arange_dt_0p1": np.arange(0.0, 40.0, 0.1),
    "v4_saved_grid": v4.EXPECTED_SAMPLE_TIMES,
}


def _steps(times: np.ndarray, duration: float) -> int:
    return int(round(duration / float(times[1] - times[0])))


def _run(n: int, start: int, steps: int) -> np.ndarray:
    """True on samples start..start+steps inclusive (span = steps * dt)."""
    condition = np.zeros(n, dtype=bool)
    condition[start : start + steps + 1] = True
    return condition


def _exact_cases(times: np.ndarray, duration: float):
    k = _steps(times, duration)
    # Every valid start, including the last one (start + k == len(times) - 1).
    for start in range(0, len(times) - k):
        yield start, _run(len(times), start, k)


def test_v4_misses_some_exactly_held_events():
    misses = {}
    for label, times in GRIDS.items():
        misses[label] = [
            start
            for start, condition in _exact_cases(times, DURATION)
            if v4._held_index(times, condition, DURATION) is None
        ]
    # Documented explicit case on v4's own saved grid: t=16.01 -> 33.51.
    times = v4.EXPECTED_SAMPLE_TIMES
    assert times[32] + DURATION > times[32 + 35]
    assert v4._held_index(times, _run(len(times), 32, 35), DURATION) is None
    # Ledger numbers (AUD-V4-HELDEVENT): 605 valid starts on the saved grid, 32 missed by v4;
    # the last valid start is held correctly by v4.
    saved = list(_exact_cases(times, DURATION))
    assert len(saved) == 605
    assert len(misses["v4_saved_grid"]) == 32
    last_start, last_condition = saved[-1]
    assert last_start + 35 == len(times) - 1
    assert v4._held_index(times, last_condition, DURATION) == last_start
    assert any(misses.values()), "v4 miss not reproduced on any constructed case"
    for label in GRIDS:
        assert misses[label], f"no v4 miss on {label}"


@pytest.mark.parametrize("label", sorted(GRIDS))
def test_v4_1_accepts_every_exactly_held_event(label):
    times = GRIDS[label]
    for start, condition in _exact_cases(times, DURATION):
        assert v41._held_index(times, condition, DURATION) == start, (label, start)


@pytest.mark.parametrize("label", sorted(GRIDS))
def test_v4_1_rejects_one_step_short(label):
    times = GRIDS[label]
    k = _steps(times, DURATION)
    for start in range(0, len(times) - k):
        condition = _run(len(times), start, k - 1)
        assert v41._held_index(times, condition, DURATION) is None, (label, start)


def test_v4_1_keeps_v4_behaviour_for_non_grid_durations():
    times = v4.EXPECTED_SAMPLE_TIMES
    condition = np.zeros(len(times), dtype=bool)
    condition[:36] = True  # span 17.5
    assert v41._held_index(times, condition, 17.5) == 0
    assert v41._held_index(times, condition, 17.502917152858814) is None
    condition[:37] = True  # span 18.0
    assert v41._held_index(times, condition, 17.502917152858814) == 0
    assert v41._hold_tolerance(times) == pytest.approx(0.5e-6)


def test_retention_vs_recovery_classification():
    times = np.arange(0.0, 6.0, 0.5)  # 12 samples
    duration = 1.0  # 2 steps
    T, F = True, False

    retained = np.array([T, T, T, F, F, F, F, F, F, F, F, F])
    assert v41._held_retention_index(times, retained, duration) == 0
    assert v41._held_recovery_index(times, retained, duration) is None
    assert v41.classify_held_event(times, retained, duration) == "retention"

    started_below = np.array([F, F, T, T, T, F, F, F, F, F, F, F])
    assert v41._held_retention_index(times, started_below, duration) is None
    assert v41._held_recovery_index(times, started_below, duration) == 2
    assert v41.classify_held_event(times, started_below, duration) == "recovery"

    # Above at start but too briefly, drops, then recovers and holds.
    brief_then_recovers = np.array([T, T, F, F, T, T, T, F, F, F, F, F])
    assert v41._held_retention_index(times, brief_then_recovers, duration) is None
    assert v41._held_recovery_index(times, brief_then_recovers, duration) == 4
    assert v4._held_index(times, brief_then_recovers, duration) == 4
    assert v41.classify_held_event(times, brief_then_recovers, duration) == "recovery"

    # Retained, later drops and recovers: retention wins the classification,
    # while the recovery estimand still records the later re-crossing.
    retained_then_recovers = np.array([T, T, T, F, T, T, T, F, F, F, F, F])
    assert v41._held_recovery_index(times, retained_then_recovers, duration) == 4
    assert v41.classify_held_event(times, retained_then_recovers, duration) == "retention"

    never_held = np.array([F, T, F, T, T, F, F, T, F, F, F, F])
    assert v41._held_retention_index(times, never_held, duration) is None
    assert v41._held_recovery_index(times, never_held, duration) is None
    assert v41.classify_held_event(times, never_held, duration) == "none"

    always = np.ones(12, dtype=bool)
    assert v41.classify_held_event(times, always, duration) == "retention"
    assert v41._held_recovery_index(times, always, duration) is None


def test_v4_1_synthetic_compute_recovery_row_counts(tmp_path):
    """Exercise compute_recovery/interactions on a fully synthetic cohort."""
    rng = np.random.default_rng(0)
    times = v4.EXPECTED_SAMPLE_TIMES
    seeds = tuple(f"s{i:02d}" for i in range(v4.EXPECTED_N_SEEDS))
    arrays = {}
    rows = []
    for seed in seeds:
        for rho in v4.EXPECTED_RHO_VALUES:
            for branch in v4.EXPECTED_BRANCHES:
                density = np.clip(0.5 + 0.1 * rng.standard_normal(len(times)), 0, 1)
                similarity = np.clip(0.5 + 0.2 * rng.standard_normal(len(times)), -1, 1)
                for field, value in (
                    ("sample_times", times),
                    ("density_trajectory", density),
                    ("similarity_trajectory", similarity),
                ):
                    arrays[v41._npz_key(branch, seed, rho, field)] = value
                rows.append(
                    {
                        "seed": seed,
                        "rho": rho,
                        "branch": branch,
                        "T_window": 17.502917152858814 * rho,
                        "D_B_final": 0.5,
                        "Weighted_similarity_late_fixed_physical": 0.5,
                        "Weighted_similarity_late_normalized_EMA": 0.5,
                    }
                )
    npz = tmp_path / "synthetic_branches.npz"
    np.savez(npz, **arrays)
    inputs = v41.RunInputs(tmp_path, tmp_path / "x.csv", npz, tmp_path / "m", tmp_path / "c", tmp_path / "b")
    run = v41.ValidatedRun(
        inputs=inputs,
        scalar=pd.DataFrame(rows),
        manifest={},
        seeds=seeds,
        rho_values=v4.EXPECTED_RHO_VALUES,
        branches=v4.EXPECTED_BRANCHES,
        b_c=0.12,
        t_star=25.0,
        input_hashes={},
    )
    events, auc = v41.compute_recovery(run)
    assert len(events) == 19200 and len(auc) == 1600
    assert set(events["event_type"]) == {
        "first_crossing",
        "sustained_through_last_saved_observation",
        "held",
        "held_retention",
        "held_recovery",
    }
    held = events[events["event_type"].isin(v41.HELD_EVENT_TYPES)]
    assert set(held["held_classification"]) <= {"retention", "recovery", "none"}
    assert len(v41.recovery_event_interactions(events)) == 11520


def test_main_refuses_without_acknowledgement(capsys):
    assert v41.main(["/nonexistent", "--bootstrap-seed", "1"]) == 2
    assert "UNAUDITED CANDIDATE" in capsys.readouterr().err
