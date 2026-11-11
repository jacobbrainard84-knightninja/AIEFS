from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from aief_modular.authority import load_authority_lock, verify_authority_lock
from aief_modular.validation import ArtifactIntegrityError


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _make_lock(root: Path) -> Path:
    files = {
        "manifest": root / "runs/frozen/manifest.json",
        "branch_npz": root / "runs/frozen/data.npz",
        "scalar_csv": root / "runs/frozen/scalar.csv",
        "engine_v1": root / "engine.py",
        "twindow_driver_v1": root / "driver.py",
        "twindow_analysis_v3": root / "analysis.py",
    }
    for name, path in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(f"content:{name}".encode())
    payload = {
        "authority_schema": "aief-frozen-authority-lock-v1",
        "authority_id": "TEST_AUTHORITY",
        "certification_design": {
            "seed_count": 2,
            "branch_count": 2,
            "ordered_branch_namespace": ["continue", "future_shuffle"],
        },
        "frozen_artifacts": {
            "manifest": {
                "relative_path": "runs/frozen/manifest.json",
                "sha256": _sha(files["manifest"]),
            },
            "branch_npz": {
                "relative_path": "runs/frozen/data.npz",
                "sha256": _sha(files["branch_npz"]),
            },
            "scalar_csv": {
                "relative_path": "runs/frozen/scalar.csv",
                "sha256": _sha(files["scalar_csv"]),
            },
        },
        "legacy_sources": {
            "engine_v1": {"relative_path": "engine.py", "sha256": _sha(files["engine_v1"])},
            "twindow_driver_v1": {
                "relative_path": "driver.py",
                "sha256": _sha(files["twindow_driver_v1"]),
            },
            "twindow_analysis_v3": {
                "relative_path": "analysis.py",
                "sha256": _sha(files["twindow_analysis_v3"]),
            },
        },
        "authentication_note": "test lock",
    }
    lock_path = root / "authority.lock.json"
    lock_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return lock_path


def test_authority_lock_verifies_artifacts_sources_and_runtime_engine(tmp_path):
    lock_path = _make_lock(tmp_path)
    lock, lock_hash = load_authority_lock(lock_path)
    result = verify_authority_lock(
        lock,
        authority_root=tmp_path,
        supplied_artifacts={
            "manifest": tmp_path / "runs/frozen/manifest.json",
            "npz": tmp_path / "runs/frozen/data.npz",
            "scalar": tmp_path / "runs/frozen/scalar.csv",
        },
        runtime_engine_path=tmp_path / "engine.py",
    )
    assert len(lock_hash) == 64
    assert result["authority_id"] == "TEST_AUTHORITY"
    assert result["seed_count"] == 2
    assert set(result["verified_sources"]) == {
        "engine_v1",
        "twindow_driver_v1",
        "twindow_analysis_v3",
    }


def test_authority_lock_detects_coordinated_input_drift(tmp_path):
    lock_path = _make_lock(tmp_path)
    lock, _hash = load_authority_lock(lock_path)
    (tmp_path / "runs/frozen/scalar.csv").write_text("changed", encoding="utf-8")
    with pytest.raises(ArtifactIntegrityError, match="hash mismatch"):
        verify_authority_lock(
            lock,
            authority_root=tmp_path,
            supplied_artifacts={
                "manifest": tmp_path / "runs/frozen/manifest.json",
                "npz": tmp_path / "runs/frozen/data.npz",
                "scalar": tmp_path / "runs/frozen/scalar.csv",
            },
            runtime_engine_path=tmp_path / "engine.py",
        )


def test_project_authority_lock_contains_supplied_hashes():
    lock_path = Path(__file__).resolve().parents[1] / "AIEF_1_4_FROZEN_5a9f093a2fe0.authority.lock.json"
    lock, lock_hash = load_authority_lock(lock_path)
    assert lock.authority_id == "AIEF_1_4_FROZEN_5a9f093a2fe0"
    assert lock.artifact("manifest").sha256 == (
        "bf4d8c4152efafac352c8e1e56759ee7867fdd418cb04a8ee1f2fc87c2315a33"
    )
    assert lock.source("engine_v1").sha256 == (
        "ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede"
    )
    assert lock_hash == "57e4337c66f68eda116f32bbc446eb30bd068e0d39f1634eefdadcf02cfcbb5f"
