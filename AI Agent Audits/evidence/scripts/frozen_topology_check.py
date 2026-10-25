"""NEW (round 3, 2026-10-24; extended round 4, 2026-10-25). Response-2 point 4: is B_split's AUC 1.0 for the final topology expected?
Counts edges whose threshold status B > B_C changes between the split and the end of the run:
  * archived AIEF-1.3 repo-omega runs (runs/c3da1ac707bf, runs/73dca37cf93f; baseline and no_delay; keys B_at_split, B_final, P_future);
  * the random-omega delay experiment (results/delay_paired_edges_{uniform,clustered}.csv; columns Bsplit, Bf, P).
If no edge changes status, the post-split topology is frozen and a B_split > B_C classifier is exact by construction:
B_split is then predictive of the final topology, which says nothing about whether B is causally necessary.
Round 4 (response-3 #4): endpoint equality alone does not exclude an edge crossing B_C and crossing back. The engine
(AIEF_1_3_falsification_updated.run_aief) accumulates P_sum += B > B_C at EVERY step of the future window (stride 1, not
sampled) and stores P_future = P_sum / future_count. So P_future in {0, 1} for an edge means its threshold status is constant
at every future step. We record nonbinary_P_future_count (P_future not exactly 0 or 1) and the count of edges whose
P_future label disagrees with the split status (B_split > B_C). Full per-step B trajectories are not saved by the engine; the
stride-1 P_future is the complete per-step threshold record that exists. CSV values are 9 significant digits, so 0/1 are exact."""
import sys, os, glob, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__)); from _common import *
BC = 0.12; iu = np.triu_indices(12, 1); out = {'B_C': BC, 'archived_repo_omega': {}, 'random_omega_delay_experiment': {}}
nonbin = lambda p: int(np.count_nonzero((p != 0.0) & (p != 1.0)))
for run in ['c3da1ac707bf', '73dca37cf93f']:
    for cond in ['baseline', 'no_delay']:
        fs = sorted(glob.glob(f'runs/{run}/{cond}_seed_*.npz')); e = d = nb = pd_ = 0
        for f in fs:
            with np.load(f) as z: a = z['B_at_split'][iu] > BC; b = z['B_final'][iu] > BC; p = z['P_future'][iu]
            e += a.size; d += int((a != b).sum()); nb += nonbin(p); pd_ += int(((p == 1.0) != a).sum())
        out['archived_repo_omega'][f'{run}/{cond}'] = dict(runs=len(fs), edges=e, edges_changing_status=d,
            nonbinary_P_future_count=nb, P_future_label_differs_from_split_status=pd_)
for kd in ['uniform', 'clustered']:
    df = pd.read_csv(inp(f'delay_paired_edges_{kd}.csv'))
    for cond, g in df.groupby('cond'):
        p = g.P.to_numpy(float); a = (g.Bsplit > BC).to_numpy()
        out['random_omega_delay_experiment'][f'{kd}/{cond}'] = dict(edges=len(g), edges_changing_status=int(((g.Bsplit > BC) != (g.Bf > BC)).sum()),
            nonbinary_P_future_count=nonbin(p), P_future_label_differs_from_split_status=int(((p == 1.0) != a).sum()))
groups = [v for s in ['archived_repo_omega', 'random_omega_delay_experiment'] for v in out[s].values()]
out['total_edges'] = sum(v['edges'] for v in groups)
out['total_edges_changing_status'] = sum(v['edges_changing_status'] for v in groups)
out['total_nonbinary_P_future_count'] = sum(v['nonbinary_P_future_count'] for v in groups)
out['total_P_future_label_differs_from_split_status'] = sum(v['P_future_label_differs_from_split_status'] for v in groups)
out['P_future_definition'] = 'fraction of ALL future-window steps (stride 1) with B > B_C (AIEF_1_3_falsification_updated.run_aief: P_sum += B > B_C)'
out['interpretation'] = ('if total_nonbinary_P_future_count == 0 and the label-difference count is 0, every tested edge keeps its split-time threshold '
                         'status at every step of the future window (finite-horizon threshold freezing); continuous weights may still move')
print(out); dump('frozen_topology_check.json', out)
