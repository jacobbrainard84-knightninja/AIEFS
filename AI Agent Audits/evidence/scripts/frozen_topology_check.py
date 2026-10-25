"""NEW (round 3, 2026-10-24). Response-2 point 4: is B_split's AUC 1.0 for the final topology expected?
Counts edges whose threshold status B > B_C changes between the split and the end of the run:
  * archived AIEF-1.3 repo-omega runs (runs/c3da1ac707bf, runs/73dca37cf93f; baseline and no_delay; keys B_at_split, B_final);
  * the random-omega delay experiment (results/delay_paired_edges_{uniform,clustered}.csv; columns Bsplit, Bf).
If no edge changes status, the post-split topology is frozen and a B_split > B_C classifier is exact by construction:
B_split is then predictive of the final topology, which says nothing about whether B is causally necessary."""
import sys, os, glob, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__)); from _common import *
BC = 0.12; iu = np.triu_indices(12, 1); out = {'B_C': BC, 'archived_repo_omega': {}, 'random_omega_delay_experiment': {}}
for run in ['c3da1ac707bf', '73dca37cf93f']:
    for cond in ['baseline', 'no_delay']:
        fs = sorted(glob.glob(f'runs/{run}/{cond}_seed_*.npz')); e = d = 0
        for f in fs:
            with np.load(f) as z: a = z['B_at_split'][iu] > BC; b = z['B_final'][iu] > BC
            e += a.size; d += int((a != b).sum())
        out['archived_repo_omega'][f'{run}/{cond}'] = dict(runs=len(fs), edges=e, edges_changing_status=d)
for kd in ['uniform', 'clustered']:
    df = pd.read_csv(inp(f'delay_paired_edges_{kd}.csv'))
    for cond, g in df.groupby('cond'):
        out['random_omega_delay_experiment'][f'{kd}/{cond}'] = dict(edges=len(g), edges_changing_status=int(((g.Bsplit > BC) != (g.Bf > BC)).sum()))
out['total_edges'] = sum(v['edges'] for s in ['archived_repo_omega', 'random_omega_delay_experiment'] for v in out[s].values())
out['total_edges_changing_status'] = sum(v['edges_changing_status'] for s in ['archived_repo_omega', 'random_omega_delay_experiment'] for v in out[s].values())
print(out); dump('frozen_topology_check.json', out)
