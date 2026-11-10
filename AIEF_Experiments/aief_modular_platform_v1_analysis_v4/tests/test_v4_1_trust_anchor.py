"""Trust-anchor tests for the Analysis v4.1 candidate (GPT6-P1 fix).

The positive control reads the genuine committed S01 run (runs/b57562a8ee77)
in place: no fixture, no copy. Each negative control works on a copy in a temp
directory named like the trusted run, so the guard has to reject it on its
content, not on the directory name. Every forgery below was ACCEPTED by
validate_run on main @ eb3933c (see audit_inbox on the audit-inbox branch,
2026-11-09_auditor-seat-002_v41-p1-reproduction). Nothing is written to the repo.

Scope (ERRATA E24, E25): these tests cover file contents and file-system swaps
after the guard. They do not and cannot show tamper resistance against code in
the same Python process (a caller-supplied policy, monkeypatching, or mutating
the policy proxy); nothing here claims that. The run directory name check is a
sanity check, not a security property.

Run explicitly (pytest.ini testpaths only covers tests_modular):
    python -m pytest tests/test_v4_1_trust_anchor.py
"""

from __future__ import annotations

import csv
import hashlib
import inspect
import json
import shutil
import sys
import types
from pathlib import Path

import numpy as np
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
    return v41.validate_run(v41.discover_inputs(d), policy=policy)


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


def test_policy_proxy_blocks_accidental_writes():
    """The read-only proxy stops accidental item assignment, nothing more.

    It is NOT a security boundary: in-process code can still reach the inner dict
    (e.g. via gc.get_referents) or monkeypatch the module (ERRATA E25).
    """
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


def test_wrong_run_directory_name_fails_the_sanity_check(tmp_path: Path):
    """Sanity check only: it catches pointing the tool at the wrong run by mistake."""
    other = tmp_path / "deadbeef0000"
    other.mkdir()
    for name in NEEDED:
        shutil.copyfile(RUN / name, other / name)
    with pytest.raises(v41.ArtifactIntegrityError, match="name sanity check failed"):
        _validate(other)


def test_run_directory_name_is_not_a_security_property(tmp_path: Path):
    """Genuine bytes reached through a symlink or an x/../ path are accepted.

    That is harmless because every byte is pinned; it is why the name check must
    not be described as a security property (R001 note N4).
    """
    other = tmp_path / "deadbeef0000"
    other.symlink_to(RUN)
    named = tmp_path / "sub"
    named.mkdir()
    (named / "b57562a8ee77").symlink_to(other)
    assert len(_validate(named / "b57562a8ee77").seeds) == 40
    (tmp_path / "x").mkdir()
    assert len(_validate(tmp_path / "x" / ".." / "sub" / "b57562a8ee77").seeds) == 40


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
    """A forged re-pinned run is rejected under the default policy.

    Trust lives in the reviewed default policy, so callers (run_analysis, the CLI)
    must never derive a policy from run data. See the next test for the limit.
    """
    _edit_scalar(run_copy)
    _repin(run_copy, "scalar_csv", _scalar(run_copy))
    assert _sha(run_copy / "manifest.json") != POLICY["manifest_sha256"]
    with pytest.raises(v41.ArtifactIntegrityError):
        _validate(run_copy)  # default policy


def test_caller_supplied_policy_is_trusted_by_design(run_copy: Path):
    """Documents a limit, not a defence: in-process callers are trusted.

    A policy derived from the forged run makes validate_run accept it. Python has
    no boundary against code in the same process, so this is accepted (ERRATA E25);
    the protection is that no production path passes a policy (next tests).
    """
    _edit_scalar(run_copy)
    _repin(run_copy, "scalar_csv", _scalar(run_copy))
    manifest = json.loads((run_copy / "manifest.json").read_text())
    weak = {
        **dict(POLICY),
        "manifest_sha256": _sha(run_copy / "manifest.json"),
        "output_hashes": dict(manifest["output_hashes"]),
    }
    assert len(_validate(run_copy, weak).seeds) == 40


@pytest.mark.parametrize("root", ["[]", '"x"', "42", "null"])
def test_non_object_certificate_root_is_rejected(run_copy: Path, root: str):
    """ERRATA E26: a non-object certificate root is an integrity error, not AttributeError.

    Under the default policy the manifest pin rejects such a file first, so a
    caller-supplied policy (trusted by design, E25) is needed to reach the check.
    """
    cert = run_copy / "baseline_equivalence_certificate.json"
    cert.write_text(root)
    _repin(run_copy, "baseline_certificate", cert)
    manifest = json.loads((run_copy / "manifest.json").read_text())
    weak = {
        **dict(POLICY),
        "manifest_sha256": _sha(run_copy / "manifest.json"),
        "output_hashes": dict(manifest["output_hashes"]),
    }
    with pytest.raises(v41.ArtifactIntegrityError, match="root must be an object"):
        _validate(run_copy, weak)


def test_missing_npz_bytes_raise_instead_of_reopening_the_path():
    """ERRATA E26: no silent fallback to the NPZ path when the verified bytes are absent."""
    import dataclasses

    run = _validate(RUN)
    bare = dataclasses.replace(run, branch_npz_bytes=None)
    key = v41._npz_key("continue", run.seeds[0], run.rho_values[0], "B_final")
    with pytest.raises(v41.ArtifactIntegrityError, match="branch_npz_bytes is missing"):
        v41._run_npz_keys(bare, [key])
    with pytest.raises(v41.ArtifactIntegrityError, match="branch_npz_bytes is missing"):
        v41.cross_t_topology(bare)


def test_policy_is_keyword_only():
    """Keyword-only, so a policy cannot be passed positionally by accident."""
    inputs = v41.discover_inputs(RUN)
    with pytest.raises(TypeError):
        v41.validate_run(inputs, POLICY)  # type: ignore[misc]
    with pytest.raises(TypeError):
        v41.verify_trusted_inputs(inputs, POLICY)  # type: ignore[misc]
    parameter = inspect.signature(v41.validate_run).parameters["policy"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is v41.TRUSTED_S01_POLICY


def test_run_analysis_does_not_pass_a_policy(monkeypatch, tmp_path: Path):
    """Regression guard (behavioural): run_analysis calls validate_run with no policy,
    so the reviewed default applies. Not a tamper-resistance claim."""
    calls = []
    sentinel = object()

    class Stop(Exception):
        pass

    def fake_validate(*args, **kwargs):
        calls.append((args, kwargs))
        raise Stop

    monkeypatch.setattr(v41, "discover_inputs", lambda run_dir: sentinel)
    monkeypatch.setattr(v41, "validate_run", fake_validate)
    with pytest.raises(Stop):
        v41.run_analysis(
            tmp_path, output_root=tmp_path, bootstrap_seed=1, n_bootstrap=1, command_line="t"
        )
    assert calls == [((sentinel,), {})]


# --- file-system swaps after the guard (R001 note N3, ERRATA E25) ---------------

def _forged_copy(tmp_path: Path) -> Path:
    """A forged run: edited scalar, failing status/certificate, re-pinned, NPZ with 42.0.

    Status and certificate forgeries deliberately fail validate_run's later checks if
    re-read from disk (non-success status / non-passing certificate), so a regression
    that re-opens those paths after the guard makes the swap test fail.
    """
    forged = tmp_path / "forged"
    forged.mkdir()
    for name in NEEDED:
        if name != NEEDED[2]:
            shutil.copyfile(RUN / name, forged / name)
    _edit_scalar(forged)
    status_path = forged / NEEDED[3]
    status = pd.read_csv(status_path, dtype={"seed": str})
    status.loc[0, "status"] = "failed"
    status.to_csv(status_path, index=False)
    (forged / NEEDED[4]).write_text('{"status":"failed","n_seeds":40}')
    _repin(forged, "scalar_csv", _scalar(forged))
    _repin(forged, "condition_status_csv", status_path)
    _repin(forged, "baseline_certificate", forged / NEEDED[4])
    run = _validate(RUN)
    key = v41._npz_key("continue", run.seeds[0], run.rho_values[0], "B_final")
    np.savez(forged / NEEDED[2], **{key: np.full((12, 12), 42.0)})
    return forged


def test_files_swapped_after_the_guard_are_not_used(run_copy: Path, tmp_path: Path, monkeypatch):
    """Swap all five S01 outputs on disk right after the guard returns.

    Before the follow-up, validate_run re-opened the manifest and scalar and the
    analysis re-opened the NPZ, so the forged data was used while input_hashes
    recorded the genuine digests (a false provenance record). E25 closed those
    three. The condition-status CSV and certificate were already parsed from the
    guard's bytes, but no test covered them (R001 note 1). Now every parse uses
    the guard's in-memory bytes, so the swap has no effect. The forged status and
    certificate fail validate_run's later checks if re-read from disk.
    """
    forged = _forged_copy(tmp_path)
    original = v41.verify_trusted_inputs

    def guard_then_swap(inputs, *, policy):
        verified = original(inputs, policy=policy)
        for name in (NEEDED[0], NEEDED[1], NEEDED[2], NEEDED[3], NEEDED[4]):
            shutil.copyfile(forged / name, run_copy / name)
        return verified

    monkeypatch.setattr(v41, "verify_trusted_inputs", guard_then_swap)
    run = _validate(run_copy)
    monkeypatch.setattr(v41, "verify_trusted_inputs", original)

    # The swap really happened on disk ...
    assert _sha(run_copy / "manifest.json") != POLICY["manifest_sha256"]
    assert _sha(_scalar(run_copy)) != POLICY["output_hashes"]["scalar_csv"]
    assert _sha(run_copy / NEEDED[2]) != POLICY["output_hashes"]["branch_npz"]
    assert _sha(run_copy / NEEDED[3]) != POLICY["output_hashes"]["condition_status_csv"]
    assert _sha(run_copy / NEEDED[4]) != POLICY["output_hashes"]["baseline_certificate"]
    # ... and the on-disk status/certificate would fail if parsed ...
    disk_status = pd.read_csv(run_copy / NEEDED[3], dtype={"seed": str})
    assert set(disk_status["status"]) != {"success"}
    disk_cert = json.loads((run_copy / NEEDED[4]).read_text())
    assert disk_cert.get("status") != "passed"
    # ... but none of it was used.
    genuine = _validate(RUN)
    pd.testing.assert_frame_equal(run.scalar, genuine.scalar)
    assert run.manifest == genuine.manifest
    assert run.input_hashes == genuine.input_hashes
    assert run.input_hashes["simulation_manifest"] == POLICY["manifest_sha256"]
    assert run.input_hashes["scalar_csv"] == POLICY["output_hashes"]["scalar_csv"]
    assert run.input_hashes["condition_status"] == POLICY["output_hashes"]["condition_status_csv"]
    assert run.input_hashes["baseline_certificate"] == POLICY["output_hashes"]["baseline_certificate"]
    assert hashlib.sha256(run.branch_npz_bytes).hexdigest() == POLICY["output_hashes"]["branch_npz"]
    pd.testing.assert_frame_equal(v41.cross_t_topology(run), v41.cross_t_topology(genuine))


def test_npz_swapped_after_validate_run_is_not_used(run_copy: Path, tmp_path: Path):
    """The late NPZ read: swap a valid forged NPZ (42.0) in after validate_run.

    The analysis must use the verified bytes, so the recorded hash is the digest of
    the arrays actually analysed. The forged file lacks the other keys, so any read
    from disk would also raise.
    """
    run = _validate(run_copy)
    key = v41._npz_key("continue", run.seeds[0], run.rho_values[0], "B_final")
    genuine_value = v41._run_npz_keys(run, [key])[key]
    np.savez(run_copy / NEEDED[2], **{key: np.full((12, 12), 42.0)})
    assert float(v41.load_npz_keys(run.inputs.branch_npz, [key])[key][0, 0]) == 42.0  # swap is real
    used = v41._run_npz_keys(run, [key])[key]
    np.testing.assert_array_equal(used, genuine_value)
    assert not np.any(used == 42.0)
    assert run.input_hashes["branch_npz"] == POLICY["output_hashes"]["branch_npz"]
    assert hashlib.sha256(run.branch_npz_bytes).hexdigest() == run.input_hashes["branch_npz"]
    assert len(v41.cross_t_topology(run)) == 160


def test_run_analysis_bundle_records_the_bytes_it_used(run_copy: Path, tmp_path: Path, monkeypatch):
    """End to end: swap a forged NPZ in after validate_run, then let run_analysis finish.

    The forged NPZ holds one 42.0 array and none of the other keys, so a late read
    from disk would raise. The bundle must complete and record the genuine digests,
    which are the digests of the bytes the analysis used. Output goes to tmp only.
    """
    original = v41.validate_run
    key = v41._npz_key("continue", POLICY["paired_seeds"][0], 0.5, "B_final")

    def validate_then_swap(inputs, **kwargs):
        run = original(inputs, **kwargs)
        np.savez(run_copy / NEEDED[2], **{key: np.full((12, 12), 42.0)})
        return run

    monkeypatch.setattr(v41, "validate_run", validate_then_swap)
    final = v41.run_analysis(
        run_copy, output_root=tmp_path / "out", bootstrap_seed=1, n_bootstrap=5, command_line="test"
    )
    assert _sha(run_copy / NEEDED[2]) != POLICY["output_hashes"]["branch_npz"]  # swap is real
    recorded = json.loads((final / "analysis_manifest.json").read_text())["input_run"]["input_hashes"]
    assert recorded["branch_npz"] == POLICY["output_hashes"]["branch_npz"]
    assert recorded["simulation_manifest"] == POLICY["manifest_sha256"]
    assert recorded["scalar_csv"] == POLICY["output_hashes"]["scalar_csv"]
