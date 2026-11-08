"""Positive controls and known-defect characterizations for the pasted source.

xfail tests encode desired invariants not met by the unchanged source. Tests
use SYNTHETIC inputs and audit-only replacements for unavailable dependencies.
They do not validate the actual S01 data or the real aief_modular package.
"""
from __future__ import annotations

import itertools
import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from audit_support import ArtifactIntegrityError, file_sha256, load_analysis
from synthetic_fixture import refresh_manifest_hashes, write_fixture


@pytest.fixture
def m():
    return load_analysis()


@pytest.fixture(scope='session')
def fixture_root(tmp_path_factory):
    return write_fixture(tmp_path_factory.mktemp('synthetic_s01'), load_analysis())


@pytest.fixture
def root(fixture_root, tmp_path):
    dest = tmp_path / 'run'
    shutil.copytree(fixture_root, dest)
    return dest


@pytest.fixture
def run(m, fixture_root):
    return m.validate_run(m.discover_inputs(fixture_root))


@pytest.fixture(scope='session')
def recovered(fixture_root):
    module = load_analysis()
    run = module.validate_run(module.discover_inputs(fixture_root))
    return module.compute_recovery(run)


def test_exact_schedule_and_support(m):
    assert len(m.EXPECTED_SAMPLE_TIMES) == 640
    assert m.SUPPORT_START == .01
    assert m.SUPPORT_END == 319.51
    assert m.SUPPORT_END - m.SUPPORT_START == 319.5


def test_first_and_sustained_exhaustive(m):
    for bits in itertools.product((False, True), repeat=10):
        c = np.array(bits)
        first = next((i for i, x in enumerate(bits) if x), None)
        sustained = next((i for i in range(len(bits)) if all(bits[i:])), None)
        assert m._first_index(c) == first
        assert m._sustained_index(c) == sustained


def test_held_nonboundary_durations_exhaustive(m):
    t = m.EXPECTED_SAMPLE_TIMES[:10]
    for bits in itertools.product((False, True), repeat=10):
        c = np.array(bits)
        for duration in (1.25, 2.75):
            ref = None
            for i in range(len(c)):
                for j in range(i, len(c)):
                    if .5 * (j - i) >= duration and all(bits[i:j+1]):
                        ref = i
                        break
                if ref is not None:
                    break
            assert m._held_index(t, c, duration) == ref


@pytest.mark.xfail(strict=True, reason='addition/searchsorted rejects some exact 17.5-unit runs')
def test_fixed_hold_translation_invariant_on_declared_grid(m):
    t = m.EXPECTED_SAMPLE_TIMES
    for start in range(len(t) - 35):
        c = np.zeros(len(t), bool)
        c[start:start+36] = True
        assert m._held_index(t, c, 17.5) == start, (start, t[start], t[start+35])


@pytest.mark.xfail(strict=True, reason='implementation can disagree even with literal timestamp subtraction')
def test_hold_satisfying_literal_timestamp_contract(m):
    t = m.EXPECTED_SAMPLE_TIMES
    c = np.zeros(len(t), bool)
    c[32:103] = True
    assert t[102] - t[32] == 35.0
    assert m._held_index(t, c, 35.0) == 32


def test_invalid_hold_duration_rejected(m):
    for duration in (0., -1., float('nan'), float('inf')):
        with pytest.raises(ValueError):
            m._held_index(np.arange(3.), np.ones(3, bool), duration)


def test_auc_direction_and_saved_support(m):
    t = m.EXPECTED_SAMPLE_TIMES
    zeros, ones = np.zeros(len(t)), np.ones(len(t))
    assert m._auc(t, ones, zeros) == 319.5
    assert m._auc(t, zeros, ones) == 0
    assert m._auc(t, ones, ones) == 0


def test_trajectory_bad_ranges_and_schedule_rejected(m):
    t = m.EXPECTED_SAMPLE_TIMES
    d, s = np.ones(len(t)) * .5, np.ones(len(t)) * .5
    m._validate_trajectory(t, d, s, 'control')
    m._validate_trajectory(t, d, np.full(len(t), np.nan), 'allowed NaN')
    for bad_d in (np.full(len(t), np.nan), np.full(len(t), 1.01)):
        with pytest.raises(ArtifactIntegrityError):
            m._validate_trajectory(t, bad_d, s, 'bad density')
    for bad_s in (np.full(len(t), np.inf), np.full(len(t), 1.01)):
        with pytest.raises(ArtifactIntegrityError):
            m._validate_trajectory(t, d, bad_s, 'bad similarity')
    bad_t = t.copy(); bad_t[3] += .001
    with pytest.raises(ArtifactIntegrityError):
        m._validate_trajectory(bad_t, d, s, 'bad times')


def test_fixture_validates_all_800_conditions(run):
    assert len(run.scalar) == 800
    assert len(run.seeds) == 40


def test_input_hash_mismatch_is_caught_before_loading(m, root):
    p = m.discover_inputs(root).scalar_csv
    with open(p, 'a') as f:
        f.write('\n')
    with pytest.raises(ArtifactIntegrityError, match='hash mismatch'):
        m.validate_run(m.discover_inputs(root))


def test_missing_npz_key_rejected(m, root):
    path = root / 'tiny.npz'
    np.savez(path, present=np.array([1]))
    with pytest.raises(ArtifactIntegrityError, match='missing'):
        m.load_npz_keys(path, ('absent',))


def test_scalar_contrast_and_did_signs(m, run):
    regime = m.regime_contrasts(run.scalar, m.PRIMARY_OUTCOMES, 'fixed_physical')
    did = m.branch_interactions(run.scalar, m.PRIMARY_OUTCOMES, 'fixed_physical')
    for rho in (.5, .75, 1.5, 2.):
        np.testing.assert_allclose(
            regime.loc[regime.rho == rho, 'paired_regime_contrast'],
            .025 * (rho - 1), rtol=0, atol=1e-14,
        )
        for index, branch in enumerate(m.EXPECTED_BRANCHES):
            if branch == 'continue':
                continue
            np.testing.assert_allclose(
                did.loc[(did.rho == rho) & (did.branch == branch), 'difference_in_differences'],
                .01 * (rho - 1) * index, rtol=0, atol=1e-14,
            )


def test_recovery_counts_and_raw_nan_not_modified(m, run, recovered):
    events, auc = recovered
    assert len(events) == 9600 and len(auc) == 1600
    assert not events.duplicated([
        'seed', 'rho', 'branch', 'metric', 'target_definition', 'event_type', 'hold_duration_system'
    ]).any()
    assert np.all(np.isfinite(events['restricted_time']))
    assert np.all(np.isfinite(auc['auc_deficit']))
    assert (auc.loc[auc.branch == 'continue', 'auc_deficit'] == 0).all()
    assert (events.loc[(events.branch == 'reset_B') & (events.metric == 'similarity'),
                       'undefined_samples_imputed_zero'] > 0).all()
    assert file_sha256(run.inputs.branch_npz) == run.input_hashes['branch_npz']
    key = m._npz_key('reset_B', run.seeds[0], .5, 'similarity_trajectory')
    assert np.isnan(m.load_npz_keys(run.inputs.branch_npz, [key])[key]).any()


def test_four_cell_complete_case_gate(m, recovered):
    events, _ = recovered
    events = events.copy()
    one = ((events.seed == '1000') & (events.rho == .5) & (events.branch == 'reset_B')
           & (events.metric == 'density') & (events.event_type == 'first_crossing'))
    assert one.sum() == 1
    events.loc[one, 'event_time'] = np.nan
    events.loc[one, 'event_time_over_Twindow'] = np.nan
    events.loc[one, 'event_observed'] = False
    events.loc[one, 'restricted_time'] = m.SUPPORT_END
    events.loc[one, 'restricted_time_over_Twindow'] = m.SUPPORT_END / 8.75
    did = m.recovery_event_interactions(events)
    row = did.loc[(did.seed == '1000') & (did.rho == .5) & (did.branch == 'reset_B')
                  & (did.metric == 'density') & (did.event_type == 'first_crossing')].iloc[0]
    assert not row.four_cell_complete_case
    assert np.isnan(row.conditional_event_time_DID)
    assert np.isfinite(row.restricted_time_DID)
    assert len(did) == 5760


def _two_group_frame(seeds):
    rows = []
    for i, seed in enumerate(seeds):
        rows += [{'seed': seed, 'group': 'a', 'value': float(i)},
                 {'seed': seed, 'group': 'b', 'value': float(2 * i + 3)}]
    return pd.DataFrame(rows)


def test_joint_plan_and_seed_alignment(m):
    seeds = tuple(str(i) for i in range(40))
    draws = m.bootstrap_draws(seeds, 2000, 721)
    f = _two_group_frame(seeds)
    original = m.pointwise_summary(f, group_columns=('group',), value_column='value', seeds=seeds, draws=draws)
    shuffled = m.pointwise_summary(f.sample(frac=1, random_state=3), group_columns=('group',), value_column='value', seeds=seeds, draws=draws)
    pd.testing.assert_frame_equal(original, shuffled)
    a, b = original.set_index('group').loc['a'], original.set_index('group').loc['b']
    for field in ('mean', 'pointwise_ci_lower', 'pointwise_ci_upper'):
        assert b[field] == pytest.approx(2 * a[field] + 3)
    np.testing.assert_array_equal(draws, m.bootstrap_draws(seeds, 2000, 721))


def test_summary_duplicate_and_missing_seed_guards(m):
    seeds = ('one', 'two')
    draws = m.bootstrap_draws(seeds, 10, 2)
    f = pd.DataFrame({'seed': ['one', 'one'], 'group': ['a', 'a'], 'value': [1., 2.]})
    with pytest.raises(ArtifactIntegrityError, match='duplicate seeds'):
        m.pointwise_summary(f, group_columns=('group',), value_column='value', seeds=seeds, draws=draws)
    f = f.iloc[:1]
    with pytest.raises(ArtifactIntegrityError, match='not full cohort'):
        m.simultaneous_complete_summary(f, group_columns=('group',), value_column='value', seeds=seeds, draws=draws, family_id='test')


def test_nan_conditional_summary_counts(m):
    seeds = tuple(str(i) for i in range(40))
    f = pd.DataFrame({'seed': seeds, 'group': 'one', 'value': [1., 3.] + [np.nan] * 38})
    row = m.pointwise_summary(f, group_columns=('group',), value_column='value', seeds=seeds,
                              draws=m.bootstrap_draws(seeds, 2000, 41)).iloc[0]
    assert row.n == 2 and row['mean'] == 2.
    assert row.included_seed_fraction == .05


@pytest.mark.xfail(strict=True, reason='empirical bootstrap rate CI collapses at a sample boundary')
def test_zero_events_do_not_imply_zero_population_uncertainty(m):
    seeds = tuple(str(i) for i in range(40))
    f = pd.DataFrame({'seed': seeds, 'group': 'one', 'value': np.zeros(40)})
    row = m.pointwise_summary(f, group_columns=('group',), value_column='value', seeds=seeds,
                              draws=m.bootstrap_draws(seeds, 2000, 41)).iloc[0]
    assert row.pointwise_ci_upper > 0


def test_zero_reference_is_explicitly_characterized(m):
    raw = np.full(len(m.EXPECTED_SAMPLE_TIMES), np.nan)
    derived = np.nan_to_num(raw, nan=0.)
    condition = derived >= .9 * 0.
    assert m._first_index(condition) == 0
    assert m._sustained_index(condition) == 0
    assert m._held_index(m.EXPECTED_SAMPLE_TIMES, condition, 17.5) == 0
    assert m._auc(m.EXPECTED_SAMPLE_TIMES, derived, derived) == 0


def test_empty_topology_is_rejected_even_if_arrays_finite(m, run, monkeypatch):
    arrays = {
        m._npz_key('continue', seed, rho, 'B_final'): np.zeros((12, 12))
        for seed in run.seeds for rho in run.rho_values
    }
    monkeypatch.setattr(m, 'load_npz_keys', lambda *_: arrays)
    with pytest.raises(ArtifactIntegrityError, match='Nonfinite topology metric'):
        m.cross_t_topology(run)


def test_complete_synthetic_pipeline_and_bundle(m, root, tmp_path):
    final = m.run_analysis(root, output_root=tmp_path / 'output', bootstrap_seed=2026,
                           n_bootstrap=2000, command_line='SYNTHETIC AUDIT ONLY')
    manifest = json.loads((final / 'analysis_manifest.json').read_text())
    assert manifest['status'] == 'completed'
    assert len(manifest['output_hashes']) == 15
    for name, expected in manifest['output_hashes'].items():
        assert file_sha256(final / name) == expected
    assert len(list(final.iterdir())) == 16
    assert not list(final.parent.glob('.*.tmp'))
    for name, expected in {
        'twindow_paired_regime_contrasts_v4.csv': 960,
        'twindow_branch_interactions_v4.csv': 2880,
        'twindow_cross_condition_topology_v4.csv': 160,
        'twindow_recovery_events_by_seed_v4.csv': 9600,
        'twindow_recovery_auc_by_seed_v4.csv': 1600,
        'twindow_recovery_event_interactions_v4.csv': 5760,
        'twindow_recovery_auc_interactions_v4.csv': 960,
        'twindow_regime_summary_v4.csv': 24,
        'twindow_branch_DID_summary_v4.csv': 72,
        'twindow_topology_summary_v4.csv': 12,
        'twindow_recovery_event_summary_v4.csv': 1200,
        'twindow_recovery_auc_summary_v4.csv': 80,
        'twindow_recovery_event_interaction_summary_v4.csv': 720,
        'twindow_recovery_auc_interaction_summary_v4.csv': 24,
    }.items():
        assert len(pd.read_csv(final / name)) == expected


def _minimal_bundle(m, run, root):
    return m._write_bundle(
        run=run, frames={'small.csv': pd.DataFrame({'value': [1., 2.]})}, report='AUDIT ONLY\n',
        output_root=root, bootstrap_seed=1, n_bootstrap=10,
        draws=m.bootstrap_draws(run.seeds, 10, 1), command_line='SYNTHETIC AUDIT ONLY',
    )


def test_ordinary_prepublication_write_failure_is_contained(m, run, tmp_path, monkeypatch):
    def fail(*_):
        raise OSError('audit injected write failure')
    monkeypatch.setattr(m, 'save_dataframe_atomic', fail)
    with pytest.raises(OSError, match='injected'):
        _minimal_bundle(m, run, tmp_path)
    directories = list((tmp_path / 'v4').iterdir())
    assert len(directories) == 1
    assert directories[0].name.startswith('failed_')
    assert (directories[0] / 'FAILED_analysis_manifest.json').exists()
    assert not (directories[0] / 'analysis_manifest.json').exists()


@pytest.mark.xfail(strict=True, reason='input bytes are trusted after validate_run; published digest can describe different data')
def test_published_input_digest_matches_bytes_consumed(m, root, tmp_path, monkeypatch):
    validate = m.validate_run
    captured = {}
    def validate_then_change(inputs):
        run = validate(inputs)
        with np.load(inputs.branch_npz, allow_pickle=False) as archive:
            arrays = {key: archive[key].copy() for key in archive.files}
        key = m._npz_key('continue', run.seeds[0], .5, 'B_final')
        arrays[key][0, 1] += .1
        arrays[key][1, 0] += .1
        baseline = arrays[m._npz_key('continue', run.seeds[0], 1., 'B_final')]
        captured['expected_distance'] = m.normalized_distance(arrays[key], baseline)
        np.savez_compressed(inputs.branch_npz, **arrays)
        captured['consumed_digest'] = file_sha256(inputs.branch_npz)
        assert captured['consumed_digest'] != run.input_hashes['branch_npz']
        return run
    monkeypatch.setattr(m, 'validate_run', validate_then_change)
    try:
        final = m.run_analysis(root, output_root=tmp_path / 'mutated_output', bootstrap_seed=2026,
                               n_bootstrap=64, command_line='SYNTHETIC MUTATION FAULT INJECTION')
    except ArtifactIntegrityError:
        return  # Rejecting changed inputs is a valid resolution.
    observed = pd.read_csv(final / 'twindow_cross_condition_topology_v4.csv', dtype={'seed': str})
    value = observed.loc[(observed.seed == '1000') & (observed.rho == .5), 'cross_T_normalized_distance'].iloc[0]
    assert value == pytest.approx(captured['expected_distance'])
    manifest = json.loads((final / 'analysis_manifest.json').read_text())
    assert manifest['input_run']['input_hashes']['branch_npz'] == captured['consumed_digest']


def test_postrename_fsync_failure_leaves_completed_bundle(m, run, tmp_path, monkeypatch):
    original = m._fsync_directory
    def fail_parent(path):
        if Path(path) == tmp_path / 'v4':
            raise OSError('audit injected post-rename fsync failure')
        original(path)
    monkeypatch.setattr(m, '_fsync_directory', fail_parent)
    with pytest.raises(OSError, match='post-rename'):
        _minimal_bundle(m, run, tmp_path)
    completed = list((tmp_path / 'v4').glob('analysis_*'))
    assert len(completed) == 1
    assert json.loads((completed[0] / 'analysis_manifest.json').read_text())['status'] == 'completed'


def test_adjacent_saved_interval_does_not_identify_first_physical_crossing(m):
    fine_t = np.arange(1, 102, dtype=float) * .01
    late = (fine_t >= .76).astype(float)
    early = np.maximum(late, ((fine_t >= .11) & (fine_t < .21)).astype(float))
    saved = np.array([0, 50, 100])
    np.testing.assert_array_equal(late[saved], early[saved])
    event_index = m._first_index(early[saved] >= .9)
    row = m._event_row(seed='example', rho=1., t_window=17.5, branch='reset_B',
                       metric='similarity', target_definition='test', target_value=.9,
                       event_type='first_crossing', hold_system='not_applicable',
                       hold_duration=None, event_index=event_index, imputed_count=0)
    assert row['event_interval_lower'] == .51
    assert row['event_interval_upper'] == 1.01
    first_early = fine_t[np.flatnonzero(early >= .9)[0]]
    first_late = fine_t[np.flatnonzero(late >= .9)[0]]
    assert first_early < row['event_interval_lower']
    assert row['event_interval_lower'] < first_late <= row['event_interval_upper']


def test_hold_tail_is_not_fully_observed_for_physical_onset(m):
    t = m.EXPECTED_SAMPLE_TIMES
    duration, onset = 17.5, 310.01
    c = t >= onset
    index = m._held_index(t, c, duration)
    assert index is None
    row = m._event_row(seed='example', rho=1., t_window=17.5, branch='reset_B',
                       metric='density', target_definition='test', target_value=.5,
                       event_type='held', hold_system='fixed_physical_17p5',
                       hold_duration=duration, event_index=index, imputed_count=0)
    last_eligible = t[np.flatnonzero(.5 * (len(t) - 1 - np.arange(len(t))) >= duration)[-1]]
    assert last_eligible == 302.01
    assert last_eligible < onset < row['restricted_time']
    assert row['restricted_time'] == m.SUPPORT_END


@pytest.mark.xfail(strict=True, reason='ordinary pandas CSV round-trip can fail exact nominal-window equality')
def test_nominal_window_check_accepts_ordinary_numeric_roundtrip(m, root):
    t_star = 17.333
    inputs = m.discover_inputs(root)
    frame = m._load_scalar(inputs.scalar_csv)
    frame['T_window'] = frame['rho'] * t_star
    frame.to_csv(inputs.scalar_csv, index=False)
    manifest = json.loads(inputs.manifest.read_text())
    manifest['model']['T_star'] = t_star
    inputs.manifest.write_text(json.dumps(manifest))
    refresh_manifest_hashes(root, m)
    run = m.validate_run(inputs)
    assert run.t_star == t_star


@pytest.mark.xfail(strict=True, reason='read-back compares stored hash to in-memory payload, not serialized payload')
def test_staged_manifest_payload_is_checked_against_its_digest(m, run, tmp_path, monkeypatch):
    writer = m.atomic_write_json
    def alter_serialized_payload(path, value):
        if Path(path).name == 'analysis_manifest.json':
            value = json.loads(json.dumps(value))
            value['analysis_identity_payload']['analysis_contract']['sample_spacing'] = 999.
        writer(path, value)
    monkeypatch.setattr(m, 'atomic_write_json', alter_serialized_payload)
    try:
        final = _minimal_bundle(m, run, tmp_path)
    except ArtifactIntegrityError:
        return
    manifest = json.loads((final / 'analysis_manifest.json').read_text())
    assert manifest['analysis_identity_sha256'] == m.canonical_sha256(manifest['analysis_identity_payload'])


def test_fixed_se_max_statistic_matches_direct_reference(m):
    seeds = tuple(str(i) for i in range(40))
    draws = m.bootstrap_draws(seeds, 2000, 839)
    f = _two_group_frame(seeds)
    summary = m.simultaneous_complete_summary(f, group_columns=('group',), value_column='value',
                                              seeds=seeds, draws=draws, family_id='test')
    matrix = np.stack((np.arange(40.), 2 * np.arange(40.) + 3))
    se = matrix.std(axis=1, ddof=1) / np.sqrt(40)
    boot = np.stack([matrix[:, indices].mean(axis=1) for indices in draws], axis=1)
    c = np.percentile(np.max(np.abs((boot - matrix.mean(axis=1)[:, None]) / se[:, None]), axis=0), 95)
    np.testing.assert_allclose(summary['simultaneous_ci_lower'], matrix.mean(axis=1) - c * se)
    np.testing.assert_allclose(summary['simultaneous_ci_upper'], matrix.mean(axis=1) + c * se)
