"""Public oracle negative control on real S01 files; only a duplicate row changes.

Uses read-only hardlinks for CSV/NPZ files. The duplicate status CSV is a separate
new file. All temporary candidates are removed; repository files are not edited.
"""
from __future__ import annotations
import csv
from dataclasses import asdict
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parent
REPO=Path(os.environ.get('AIEFS_AUDIT_REPO',ROOT/'repository')).resolve()
PKG=REPO/'AIEF_Experiments/aief_modular_platform_v1_analysis_v4'
sys.path[:0]=[str(PKG),str(REPO)]
from aief_modular.oracle import compare_twindow_run


def main():
    raw=REPO/'runs/b57562a8ee77'
    with (raw/'twindow_condition_status.csv').open(newline='') as handle:
        reader=csv.DictReader(handle);fields=reader.fieldnames;rows=list(reader)
    with tempfile.TemporaryDirectory(prefix='oracle-negative-control-',dir=ROOT) as name:
        candidate=Path(name)
        for pattern in ['AIEF_1_4_Twindow_sensitivity_*_scalar_summary.csv',
                        'AIEF_1_4_Twindow_sensitivity_*_branch_diagnostics.npz']:
            source,=raw.glob(pattern)
            os.link(source,candidate/source.name)
        with (candidate/'twindow_condition_status.csv').open('w',newline='') as handle:
            writer=csv.DictWriter(handle,fieldnames=fields);writer.writeheader()
            writer.writerows([*rows,rows[0]])
        comparison=compare_twindow_run(candidate,raw)
        result={'scope':'known-false negative control, NOT a regenerated modular candidate',
                'mutation':'one duplicate condition-status record; real scalar CSV and NPZ unchanged',
                'oracle_condition_rows':len(rows),'candidate_condition_rows':len(rows)+1,
                'comparison':asdict(comparison)}
    (ROOT/'evidence/duplicate_public_oracle.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
