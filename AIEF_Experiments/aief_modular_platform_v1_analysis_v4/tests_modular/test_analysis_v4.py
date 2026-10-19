from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import AIEF_1_4_Twindow_sensitivity_analysis_v4 as v4


def test_timestamp_correct_held_event_distinguishes_saved_sample_count():
    times = v4.EXPECTED_SAMPLE_TIMES
    condition = np.zeros(len(times), dtype=bool)
    condition[:36] = True  # 36 samples span only 17.5 units.

    assert v4._held_index(times, condition, 17.5) == 0
    assert v4._held_index(times, condition, 17.502917152858814) is None

    condition[36] = True  # 37 samples span 18.0 units.
    assert v4._held_index(times, condition, 17.502917152858814) == 0


def test_saved_grid_event_indices():
    condition = np.array([False, True, True, False, True, True], dtype=bool)
    assert v4._first_index(condition) == 1
    assert v4._sustained_index(condition) == 4
    assert v4._first_index(np.zeros(4, dtype=bool)) is None


def test_joint_seed_bootstrap_summary_is_reproducible():
    seeds = ("s1", "s2", "s3", "s4")
    frame = pd.DataFrame(
        {
            "seed": [*seeds, *seeds],
            "rho": [0.5] * 4 + [2.0] * 4,
            "value": [1.0, 2.0, 3.0, 4.0, 2.0, 3.0, 4.0, 5.0],
        }
    )
    draws_a = v4.bootstrap_draws(seeds, 200, 123)
    draws_b = v4.bootstrap_draws(seeds, 200, 123)
    np.testing.assert_array_equal(draws_a, draws_b)

    summary_a = v4.simultaneous_complete_summary(
        frame,
        group_columns=("rho",),
        value_column="value",
        seeds=seeds,
        draws=draws_a,
        family_id="test",
    )
    summary_b = v4.simultaneous_complete_summary(
        frame,
        group_columns=("rho",),
        value_column="value",
        seeds=seeds,
        draws=draws_b,
        family_id="test",
    )
    pd.testing.assert_frame_equal(summary_a, summary_b)
    assert (summary_a["n"] == 4).all()
    assert set(summary_a["simultaneous_method"]) == {"joint-seed-bootstrap_max_t_95pct"}


def test_conditional_summary_records_selected_seed_set():
    seeds = ("s1", "s2", "s3", "s4")
    frame = pd.DataFrame(
        {
            "seed": seeds,
            "group": ["g"] * 4,
            "value": [1.0, np.nan, 3.0, np.nan],
        }
    )
    draws = v4.bootstrap_draws(seeds, 100, 44)
    summary = v4.pointwise_summary(
        frame,
        group_columns=("group",),
        value_column="value",
        seeds=seeds,
        draws=draws,
    )
    assert int(summary.loc[0, "n"]) == 2
    assert float(summary.loc[0, "included_seed_fraction"]) == 0.5
    assert summary.loc[0, "included_seed_set_sha256"] == v4.seed_set_sha256(["s1", "s3"])


def _minimal_run(tmp_path: Path) -> v4.ValidatedRun:
    inputs = v4.RunInputs(
        run_dir=tmp_path / "run",
        scalar_csv=tmp_path / "scalar.csv",
        branch_npz=tmp_path / "arrays.npz",
        manifest=tmp_path / "manifest.json",
        condition_status=tmp_path / "status.csv",
        baseline_certificate=tmp_path / "certificate.json",
    )
    return v4.ValidatedRun(
        inputs=inputs,
        scalar=pd.DataFrame(),
        manifest={"run_id": "abc", "spec_sha256": "d" * 64},
        seeds=("s1", "s2"),
        rho_values=(0.5, 1.0),
        branches=("continue",),
        b_c=0.12,
        t_star=17.5,
        input_hashes={"x": "a" * 64},
    )


def test_analysis_bundle_is_promoted_atomically(tmp_path):
    run = _minimal_run(tmp_path)
    draws = v4.bootstrap_draws(run.seeds, 10, 1)
    final = v4._write_bundle(
        run=run,
        frames={"table.csv": pd.DataFrame({"x": [1, 2]})},
        report="report\n",
        output_root=tmp_path / "analysis",
        bootstrap_seed=1,
        n_bootstrap=10,
        draws=draws,
        command_line="test",
    )
    assert final.is_dir()
    assert (final / "analysis_manifest.json").is_file()
    manifest = json.loads((final / "analysis_manifest.json").read_text())
    assert manifest["status"] == "completed"
    assert manifest["analysis_id"] == v4.ANALYSIS_ID
    assert not list((tmp_path / "analysis" / "v4").glob("*.tmp"))


def test_failed_bundle_never_replaces_a_completed_directory(tmp_path, monkeypatch):
    run = _minimal_run(tmp_path)
    draws = v4.bootstrap_draws(run.seeds, 10, 1)

    def fail_write(path, frame):
        raise RuntimeError("intentional write failure")

    monkeypatch.setattr(v4, "save_dataframe_atomic", fail_write)
    with pytest.raises(RuntimeError, match="intentional"):
        v4._write_bundle(
            run=run,
            frames={"table.csv": pd.DataFrame({"x": [1]})},
            report="report\n",
            output_root=tmp_path / "analysis",
            bootstrap_seed=1,
            n_bootstrap=10,
            draws=draws,
            command_line="test",
        )
    version_root = tmp_path / "analysis" / "v4"
    assert not [path for path in version_root.iterdir() if path.name.startswith("analysis_v4_")]
    failed = [path for path in version_root.iterdir() if path.name.startswith("failed_analysis_v4_")]
    assert len(failed) == 1
    assert (failed[0] / "FAILED_analysis_manifest.json").is_file()
