"""Trust-anchor tests for the Analysis v4.1 candidate (GPT6-P1 fix).

The positive control reads the genuine committed S01 run (runs/b57562a8ee77)
in place: no fixture, no copy. Each negative control works on a copy in a temp
directory named like the trusted run, so the guard has to reject it on its
content, not on the directory name. Every forgery below was ACCEPTED by
validate_run on main @ eb3933c (see audit_inbox on the audit-inbox branch,
2026-11-09_auditor-seat-002_v41-p1-reproduction). Nothing is written to the repo.

Run explicitly (pytest.ini testpaths only covers tests_modular):
    python -m pytest tests/test_v4_1_trust_anchor.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sys
import types
from pathlib import Path

import pandas as pd
import pytest

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

import AIEF_1_4_Twindow_sensitivity_analysis_v4_1 as v41  # noqa: E402

RUN = REPO / "runs" / "b57562a8ee77"
POLICY = v41.TRUSTED_S01_POLICY
NEEDED = (
    "manifest.json",
    "AIEF_1_4_Twindow_sensitivity_b57562a8ee77_scalar_summary.csv",
    "AIEF_1_4_Twindow_sensitivity_b57562a8ee77_branch_diagnostics.npz",
    "twindow_condition_status.csv",
    "baseline_equivalence_certificate.json",
    "baseline_equivalence_by_seed.json",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def run_copy(tmp_path: Path) -> Path:
    target = tmp_path / "b57562a8ee77"
    target.mkdir()
    for name in NEEDED:
        shutil.copyfile(RUN / name, target / name)
    return target


def _scalar(d: Path) -> Path:
    return d / NEEDED[1]


def _repin(d: Path, label: str, path: Path) -> None:
    manifest = json.loads((d / "manifest.json").read_text())
    manifest["output_hashes"][label] = _sha(path)
    (d / "manifest.json").write_text(json.dumps(manifest, indent=2))


def _validate(d: Path, policy=POLICY):
    return v41.validate_run(v41.discover_inputs(d), policy)


def _edit_scalar(d: Path) -> None:
    frame = pd.read_csv(_scalar(d), dtype={"seed": str, "branch": str})
    frame.loc[0, "D_B_final"] = 0.123456
    frame.to_csv(_scalar(d), index=False)


# --- positive control: genuine S01, real files, in place ---------------------

def test_genuine_s01_is_accepted_in_place():
    run = _validate(RUN)
    assert len(run.seeds) == 40 and len(run.scalar) == 800
    assert run.seeds == POLICY["paired_seeds"]
    assert run.input_hashes["simulation_manifest"] == POLICY["manifest_sha256"]


def test_policy_matches_committed_manifest_and_inventory():
    """The in-code policy must equal the committed manifest and the inventory rows."""
    assert _sha(RUN / "manifest.json") == POLICY["manifest_sha256"]
    manifest = json.loads((RUN / "manifest.json").read_text())
    assert dict(manifest["output_hashes"]) == dict(POLICY["output_hashes"])
    assert tuple(str(s) for s in manifest["randomization"]["paired_seeds"]) == POLICY["paired_seeds"]
    assert manifest["study_name"] == POLICY["study_name"]
    assert manifest["config_hash"] == POLICY["config_hash"]
    with open(REPO / "registry" / "artifacts_current.csv", newline="") as handle:
        inventory = {row["path"]: row["sha256"] for row in csv.DictReader(handle)}
    rel = "runs/b57562a8ee77/"
    assert inventory[rel + "manifest.json"] == POLICY["manifest_sha256"]
    files = {
        "scalar_csv": NEEDED[1],
        "branch_npz": NEEDED[2],
        "condition_status_csv": NEEDED[3],
        "baseline_certificate": NEEDED[4],
        "baseline_seed_results": NEEDED[5],
    }
    for label, name in files.items():
        assert inventory[rel + name] == POLICY["output_hashes"][label], label


def test_policy_is_immutable():
    with pytest.raises(TypeError):
        POLICY["manifest_sha256"] = "0" * 64  # type: ignore[index]
    with pytest.raises(TypeError):
        POLICY["output_hashes"]["scalar_csv"] = "0" * 64  # type: ignore[index]


def test_unmodified_copy_is_accepted(run_copy: Path):
    assert len(_validate(run_copy).seeds) == 40


# --- negative controls: each was accepted before the fix ----------------------

def test_edited_scalar_with_repinned_manifest_is_rejected(run_copy: Path):
    _edit_scalar(run_copy)
    _repin(run_copy, "scalar_csv", _scalar(run_copy))
    with pytest.raises(v41.ArtifactIntegrityError, match="Manifest bytes do not match"):
        _validate(run_copy)


def test_stub_certificate_with_repinned_manifest_is_rejected(run_copy: Path):
    cert = run_copy / "baseline_equivalence_certificate.json"
    cert.write_text('{"status":"passed","n_seeds":40}')
    _repin(run_copy, "baseline_certificate", cert)
    with pytest.raises(v41.ArtifactIntegrityError, match="Manifest bytes do not match"):
        _validate(run_copy)


def test_foreign_seed_cohort_with_repinned_manifest_is_rejected(run_copy: Path):
    manifest = json.loads((run_copy / "manifest.json").read_text())
    seeds = [str(s) for s in manifest["randomization"]["paired_seeds"]]
    mapping = {s: f"9{i:018d}" for i, s in enumerate(seeds)}
    manifest["randomization"]["paired_seeds"] = [mapping[s] for s in seeds]
    frame = pd.read_csv(_scalar(run_copy), dtype={"seed": str, "branch": str})
    frame["seed"] = frame["seed"].map(mapping)
    frame.to_csv(_scalar(run_copy), index=False)
    status_path = run_copy / "twindow_condition_status.csv"
    status = pd.read_csv(status_path, dtype={"seed": str})
    status["seed"] = status["seed"].map(mapping)
    status.to_csv(status_path, index=False)
    manifest["output_hashes"]["scalar_csv"] = _sha(_scalar(run_copy))
    manifest["output_hashes"]["condition_status_csv"] = _sha(status_path)
    (run_copy / "manifest.json").write_text(json.dumps(manifest, indent=2))
    with pytest.raises(v41.ArtifactIntegrityError, match="Manifest bytes do not match"):
        _validate(run_copy)


# --- further fail-closed checks -------------------------------------------------

def test_edited_scalar_without_repin_is_rejected(run_copy: Path):
    _edit_scalar(run_copy)
    with pytest.raises(v41.ArtifactIntegrityError, match="scalar_csv does not match the trusted pin"):
        _validate(run_copy)


def test_edited_seed_results_is_rejected(run_copy: Path):
    path = run_copy / "baseline_equivalence_by_seed.json"
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(v41.ArtifactIntegrityError, match="baseline_seed_results does not match"):
        _validate(run_copy)


def test_whitespace_only_manifest_rewrite_is_rejected(run_copy: Path):
    path = run_copy / "manifest.json"
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(v41.ArtifactIntegrityError, match="Manifest bytes do not match"):
        _validate(run_copy)


def test_manifest_is_hashed_before_it_is_parsed(run_copy: Path):
    (run_copy / "manifest.json").write_bytes(b"{ this is not json")
    with pytest.raises(v41.ArtifactIntegrityError, match="Manifest bytes do not match"):
        _validate(run_copy)


def test_symlinked_child_is_rejected(run_copy: Path, tmp_path: Path):
    real = tmp_path / "elsewhere.npz"
    shutil.move(str(run_copy / NEEDED[2]), real)
    (run_copy / NEEDED[2]).symlink_to(real)
    with pytest.raises(v41.ArtifactIntegrityError, match="not a regular file"):
        _validate(run_copy)


def test_missing_seed_results_is_rejected(run_copy: Path):
    (run_copy / "baseline_equivalence_by_seed.json").unlink()
    with pytest.raises(v41.ArtifactIntegrityError, match="not a regular file"):
        _validate(run_copy)


def test_wrong_run_directory_name_is_rejected(tmp_path: Path):
    other = tmp_path / "deadbeef0000"
    other.mkdir()
    for name in NEEDED:
        shutil.copyfile(RUN / name, other / name)
    with pytest.raises(v41.ArtifactIntegrityError, match="is not the trusted run"):
        _validate(other)


def test_no_policy_is_rejected():
    with pytest.raises(v41.ArtifactIntegrityError, match="No trusted input policy"):
        _validate(RUN, None)


@pytest.mark.parametrize("mutate", ["drop_key", "bad_hash", "short_seeds", "extra_label"])
def test_malformed_policy_is_rejected(mutate: str):
    policy = {k: v for k, v in POLICY.items()}
    hashes = dict(POLICY["output_hashes"])
    if mutate == "drop_key":
        del policy["manifest_sha256"]
    elif mutate == "bad_hash":
        hashes["scalar_csv"] = "XYZ"
    elif mutate == "short_seeds":
        policy["paired_seeds"] = POLICY["paired_seeds"][:39]
    elif mutate == "extra_label":
        hashes["extra"] = "0" * 64
    policy["output_hashes"] = types.MappingProxyType(hashes)
    with pytest.raises(v41.ArtifactIntegrityError, match="policy is (incomplete|malformed)"):
        _validate(RUN, policy)


def test_policy_built_from_a_forged_manifest_is_not_the_default(run_copy: Path):
    """A forged run passes only if the caller hands in a policy built from it.

    This documents the boundary: trust lives in the reviewed default policy, so
    callers (run_analysis, the CLI) must never derive a policy from run data.
    """
    _edit_scalar(run_copy)
    _repin(run_copy, "scalar_csv", _scalar(run_copy))
    assert _sha(run_copy / "manifest.json") != POLICY["manifest_sha256"]
    with pytest.raises(v41.ArtifactIntegrityError):
        _validate(run_copy)  # default policy


def test_run_analysis_uses_the_default_policy():
    import inspect

    source = inspect.getsource(v41.run_analysis)
    assert "validate_run(discover_inputs(run_dir))" in source
    signature = inspect.signature(v41.validate_run)
    assert signature.parameters["policy"].default is v41.TRUSTED_S01_POLICY
