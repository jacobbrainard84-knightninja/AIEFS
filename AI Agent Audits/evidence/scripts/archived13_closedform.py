"""Reproduces salvage-report closed-form ablation checks on archived AIEF-1.3 runs (c3da1ac707bf + 73dca37cf93f, 100 seeds):
no_gap active-edge weights vs eta/gamma; shuffled mean R vs R*; no_mu max edge; baseline/no_delay topology counts (audit H1)."""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); from _common import *
import AIEF_1_3_falsification_updated as f
E = f.EDGES; out = {}
dw = np.abs(np.subtract.outer(f.OMEGA, f.OMEGA))[E]; Rp = np.abs((1 - f.ALPHA) / (1 - f.ALPHA * np.exp(1j * dw * f.DT)))
pred = Rp > f.MU / (f.ETA + f.MU)
acc = {c: [] for c in f.CONDITIONS}
for run in ['c3da1ac707bf', '73dca37cf93f']:
    m = json.load(open(f'runs/{run}/manifest.json'))
    for s in m['randomization']['paired_seeds']:
        for c in f.CONDITIONS: acc[c].append(np.load(f'runs/{run}/{c}_seed_{s}.npz'))
ng = np.concatenate([x['B_final'][E][x['B_final'][E] > f.B_C] for x in acc['no_gap']])
out['no_gap_active_weight_mean_sd'] = [float(ng.mean()), float(ng.std())]; out['eta_over_gamma'] = f.ETA / f.GAMMA
out['no_gap_total_weight_mean'] = float(np.mean([x['B_final'][E].sum() for x in acc['no_gap']]))
out['shuffle_mean_R_driver_past'] = float(np.mean([x['R_driver_past'][E].mean() for x in acc['shuffle_R']])); out['R_star'] = f.MU / (f.ETA + f.MU)
out['no_mu_max_edge'] = float(max(x['B_final'][E].max() for x in acc['no_mu']))
for c in ['baseline', 'no_delay']:
    tops = [tuple(np.flatnonzero(x['B_final'][E] > f.B_C)) for x in acc[c]]
    out[c] = dict(n=len(tops), distinct=len(set(tops)), eq_pred=sum(t == tuple(np.flatnonzero(pred)) for t in tops),
                  subset=sum(all(pred[list(t)]) for t in tops), D_B_mean=float(np.mean([len(t) / 66 for t in tops])))
out['n_pred'] = int(pred.sum())
for k, v in out.items(): print(k, v)
dump('archived13_closedform.json', out)
