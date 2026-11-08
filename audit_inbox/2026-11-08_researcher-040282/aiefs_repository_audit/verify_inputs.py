"""Verify selected snapshot files and the real input/source authority lock.

This does not execute the 40-seed numerical baseline equivalence gate.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import sys

from acquire_repository import BLOBS, selected

ROOT=Path(__file__).resolve().parent
REPO=Path(os.environ.get('AIEFS_AUDIT_REPO',ROOT/'repository')).resolve()
EXTRAS={
    'runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz',
    'runs/b57562a8ee77/AIEF_1_4_Twindow_sensitivity_b57562a8ee77_branch_diagnostics.npz',
    'runs/b57562a8ee77/baseline_equivalence_certificate.json',
}


def main():
    paths=sorted({p for p,e in BLOBS.items() if selected(p,e)}|EXTRAS)
    errors=[];count=0;total=0
    for name in paths:
        path=REPO/name;entry=BLOBS[name]
        if not path.is_file():errors.append([name,'missing']);continue
        count+=1;size=path.stat().st_size;total+=size
        digest=hashlib.sha1(f'blob {size}\0'.encode())
        with path.open('rb') as handle:
            for block in iter(lambda:handle.read(1024*1024),b''):digest.update(block)
        if size!=entry['size'] or digest.hexdigest()!=entry['sha']:
            errors.append([name,'content mismatch'])
        if bool(path.stat().st_mode&0o111)!=(entry['mode']=='100755'):
            errors.append([name,'executable mode mismatch'])
    summary={'file_count':count,'bytes':total,'integrity_errors':errors}
    evidence=ROOT/'evidence';evidence.mkdir(exist_ok=True)
    (evidence/'final_snapshot_integrity.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
    if errors:return 1
    pkg=REPO/'AIEF_Experiments/aief_modular_platform_v1_analysis_v4'
    sys.path[:0]=[str(pkg),str(REPO)]
    import aief_experiment_engine_v1 as engine
    from aief_modular.authority import load_authority_lock, verify_authority_lock
    lock,_=load_authority_lock(pkg/'AIEF_1_4_FROZEN_5a9f093a2fe0.authority.lock.json')
    artifacts={
        'manifest':REPO/'runs/5a9f093a2fe0/manifest.json',
        'npz':REPO/'runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz',
        'scalar':REPO/'runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_scalar_summary.csv',
    }
    result=verify_authority_lock(lock,authority_root=REPO,supplied_artifacts=artifacts,
                                 runtime_engine_path=engine.__file__)
    (evidence/'actual_authority_lock_check.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Actual authority input/source lock: verified. Numerical baseline gate NOT rerun.')
    return 0


if __name__=='__main__':raise SystemExit(main())
