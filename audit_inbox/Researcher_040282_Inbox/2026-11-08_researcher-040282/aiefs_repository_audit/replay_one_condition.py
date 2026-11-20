"""Actual-engine, one-condition numerical replay and comparison to real oracle.

This is a bounded audit replay, not full 200-condition modular certification.
It writes audit evidence outside the checked-out repository.
"""
from __future__ import annotations

import csv
import json
import os
import platform
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
REPO = Path(os.environ.get('AIEFS_AUDIT_REPO', ROOT / 'repository')).resolve()
PKG = REPO / 'AIEF_Experiments/aief_modular_platform_v1_analysis_v4'
sys.path[:0] = [str(PKG), str(REPO)]
import aief_experiment_engine_v1 as engine
from aief_modular.collectors import TWindowLegacyCollectorV1
from aief_modular.factors import expand_conditions
from aief_modular.registry import REGISTRY, load_builtin_studies
from aief_modular.runner import _simulate_condition
from aief_modular.validation import exact_equal_with_nan, exact_scalar_equal_with_nan


def main():
    started = time.perf_counter()
    load_builtin_studies()
    spec = REGISTRY.get('AIEF_1_4_S01').build()
    condition = expand_conditions(spec)[0]
    print('Actual engine replay:',condition.condition_id,flush=True)
    rows, payload = _simulate_condition(engine=engine,spec=spec,condition=condition,
                                        collector=TWindowLegacyCollectorV1())
    import AIEF_1_4_Twindow_sensitivity as legacy
    print('Independent legacy orchestration replay in the same environment',flush=True)
    rho=float(condition.value('rho'))
    legacy_result=legacy.simulate_seed_rho(condition.seed,rho,legacy.create_model_config(rho),
                                           legacy.create_protocol_config(),legacy.STUDY_BRANCHES)
    legacy_payload=legacy.flatten_result(condition.seed,rho,legacy_result)
    modular_legacy_key_difference=sorted(set(payload)^set(legacy_payload))
    modular_legacy_mismatches=[key for key in set(payload)&set(legacy_payload)
                              if not exact_equal_with_nan(np.asarray(payload[key]),np.asarray(legacy_payload[key]))]
    legacy_rows=[legacy.extract_scalar_row(condition.seed,condition.seed_index,rho,name,result)
                 for name,result in legacy_result['branches'].items()]
    modular_legacy_scalar_mismatches=[]
    for row,other in zip(rows,legacy_rows):
        for key in set(row)|set(other):
            if key not in row or key not in other:
                modular_legacy_scalar_mismatches.append(key);continue
            equal=(row[key]==other[key]) if key=='branch' else exact_scalar_equal_with_nan(row[key],other[key])
            if not equal:modular_legacy_scalar_mismatches.append(key)
    raw = REPO / 'runs/b57562a8ee77'
    recorded_environment=json.loads((raw/'manifest.json').read_text()).get('environment')
    npz = next(raw.glob('*_branch_diagnostics.npz'))
    missing, mismatches = [], []
    with np.load(npz,allow_pickle=False) as archive:
        for key, value in payload.items():
            if key not in archive:
                missing.append(key);continue
            a,b=np.asarray(value),archive[key]
            if not exact_equal_with_nan(a,b):
                item={'key':key,'computed_shape':list(a.shape),'oracle_shape':list(b.shape),
                      'computed_dtype':str(a.dtype),'oracle_dtype':str(b.dtype)}
                if a.shape==b.shape and a.dtype.kind in 'fciu' and b.dtype.kind in 'fciu':
                    finite=np.isfinite(a)&np.isfinite(b)
                    item['max_abs_finite_difference']=float(np.max(np.abs(a[finite]-b[finite]))) if finite.any() else None
                mismatches.append(item)
    scalar = next(raw.glob('*_scalar_summary.csv'))
    with scalar.open(newline='') as handle:
        reference={(r['seed'],float(r['rho']),r['branch']):r for r in csv.DictReader(handle)}
    scalar_mismatches=[]
    for row in rows:
        reference_row=reference[(str(row['seed']),float(row['rho']),row['branch'])]
        for key,value in row.items():
            if key in {'seed','seed_index','branch'}:
                equal=str(value)==reference_row[key]
            else:
                equal=exact_scalar_equal_with_nan(value,reference_row[key])
            if not equal:scalar_mismatches.append({'branch':row['branch'],'field':key,
                                                   'computed':repr(value),'oracle':reference_row[key]})
    result={'scope':'actual engine, one rho=0.5 condition replayed through both modular and legacy orchestration; not a full baseline or full modular certificate',
            'condition_id':condition.condition_id,'integration_steps_per_orchestration':176000,
            'current_environment':{'python':platform.python_version(),'numpy':np.__version__,'platform':platform.platform()},
            'recorded_oracle_environment':recorded_environment,
            'same_environment_modular_legacy_comparison':{
                'key_difference':modular_legacy_key_difference,'array_mismatches':sorted(modular_legacy_mismatches),
                'scalar_mismatches':modular_legacy_scalar_mismatches,
                'status':'passed' if not (modular_legacy_key_difference or modular_legacy_mismatches or modular_legacy_scalar_mismatches) else 'failed'},
            'elapsed_seconds':time.perf_counter()-started,
            'branch_rows':len(rows),'npz_entries_compared':len(payload),
            'missing_entries':missing,'array_mismatches':mismatches,
            'scalar_mismatches':scalar_mismatches,
            'logical_comparison':'passed' if not (missing or mismatches or scalar_mismatches) else 'failed'}
    (ROOT/'evidence/one_condition_replay.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':
    main()
