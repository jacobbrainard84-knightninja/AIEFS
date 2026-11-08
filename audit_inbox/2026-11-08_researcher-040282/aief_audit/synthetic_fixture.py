"""Shape-conforming SYNTHETIC audit fixture, NOT a reconstruction of S01.

It exercises the pasted program's validation/calculation/output paths. Values
are artificial and no inference from them is evidence about the actual run.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from audit_support import file_sha256


def refresh_manifest_hashes(root, module):
    root = Path(root)
    path = root / 'manifest.json'
    manifest = json.loads(path.read_text())
    manifest['output_hashes'] = {
        'scalar_csv': file_sha256(root / f'{module.STUDY_NAME}_AUDIT_scalar_summary.csv'),
        'branch_npz': file_sha256(root / f'{module.STUDY_NAME}_AUDIT_branch_diagnostics.npz'),
        'condition_status_csv': file_sha256(root / 'twindow_condition_status.csv'),
        'baseline_certificate': file_sha256(root / 'baseline_equivalence_certificate.json'),
    }
    path.write_text(json.dumps(manifest, indent=2))


def write_fixture(root, module, t_star=17.5):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    seeds = tuple(str(1000 + index) for index in range(40))
    times = module.EXPECTED_SAMPLE_TIMES.copy()
    rng = np.random.default_rng(20261017)
    edges = np.triu_indices(12, 1)
    scalar_rows, statuses, arrays = [], [], {}
    for seed_index, seed in enumerate(seeds):
        base_weights = rng.uniform(.05, .65, size=66)
        for rho in module.EXPECTED_RHO_VALUES:
            statuses.append({'seed': seed, 'rho': rho, 'status': 'success'})
            control_matrix = np.zeros((12, 12))
            control_weights = np.clip(base_weights + (rho - 1) * .03, 0, 1)
            control_matrix[edges] = control_weights
            control_matrix += control_matrix.T
            control_density = float(np.mean(control_weights > .2))
            for branch_index, branch in enumerate(module.EXPECTED_BRANCHES):
                interaction = .01 * (rho - 1) * branch_index
                row = {
                    'seed': seed, 'seed_index': seed_index,
                    'rho': rho, 'T_window': rho * t_star, 'branch': branch,
                    'D_B_final': control_density,
                }
                for outcome_index, outcome in enumerate((*module.PRIMARY_OUTCOMES, *module.SECONDARY_OUTCOMES)):
                    row[outcome] = (.65 + outcome_index * .01 + seed_index * .0002
                                    + (rho - 1) * .025 - branch_index * .02
                                    + interaction)
                scalar_rows.append(row)
                lag = branch_index * 10.0
                progress = 1 - np.exp(-np.maximum(times - lag, 0) / 15.0)
                density = np.round(control_density * progress * 66) / 66
                similarity = row[module.PRIMARY_OUTCOMES[0]] * progress
                if branch == 'reset_B':
                    similarity = similarity.copy()
                    similarity[times < lag] = np.nan
                for field, value in (
                    ('sample_times', times),
                    ('density_trajectory', density),
                    ('similarity_trajectory', similarity),
                    ('B_final', control_matrix),
                ):
                    arrays[module._npz_key(branch, seed, rho, field)] = value
    scalar_path = root / f'{module.STUDY_NAME}_AUDIT_scalar_summary.csv'
    npz_path = root / f'{module.STUDY_NAME}_AUDIT_branch_diagnostics.npz'
    pd.DataFrame(scalar_rows).to_csv(scalar_path, index=False)
    pd.DataFrame(statuses).to_csv(root / 'twindow_condition_status.csv', index=False)
    np.savez_compressed(npz_path, **arrays)
    (root / 'baseline_equivalence_certificate.json').write_text(json.dumps({
        'status': 'passed', 'n_seeds': 40,
        'note': 'SYNTHETIC TEST FIXTURE ONLY; not a real baseline certificate',
    }))
    (root / 'manifest.json').write_text(json.dumps({
        'run_id': 'SYNTHETIC_AUDIT_ONLY',
        'freezeable': True,
        'completion': {'status': 'completed'},
        'baseline_equivalence': {'status': 'passed'},
        'randomization': {'paired_seeds': list(seeds)},
        'study': {'rho_values': list(module.EXPECTED_RHO_VALUES)},
        'protocol': {'branches': list(module.EXPECTED_BRANCHES)},
        'model': {'T_star': t_star, 'B_c': .2},
    }, indent=2))
    refresh_manifest_hashes(root, module)
    return root
