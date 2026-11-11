"""Reproduces salvage-report section 3.5 multi-seed table: 1.4 branch final topologies (B_final > B_c) vs the closed-form
frequency-proximity set and vs the continue branch. Input: runs/5a9f093a2fe0 (40 seeds, archived)."""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); from _common import *
d = np.load('runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz')
m = json.load(open('runs/5a9f093a2fe0/manifest.json'))
seeds = sorted({k.split('_seed_')[1].split('_')[0] for k in d.keys() if k.startswith('continue_seed_') and k.endswith('_B_final')})
om = np.array([1.00, 1.02, 1.50, 2.00, 2.01, 1.01, 1.03, 1.51, 2.02, 2.00, 1.00, 1.04]); dt = 0.01; al = np.exp(-dt / (25 / om.mean()))
E = np.triu_indices(12, 1); dw = np.abs(np.subtract.outer(om, om))[E]
pred = np.abs((1 - al) / (1 - al * np.exp(1j * dw * dt))) > 0.03 / 0.07
J = lambda a, b: (a & b).sum() / max((a | b).sum(), 1)
br = ["continue", "reset_ema", "reset_B", "reset_B_ema", "B_carrier_only", "full_reset", "future_shuffle"]
out = dict(n_seeds=len(seeds), n_pred_edges=int(pred.sum()), table={})
for b in br:
    eq = sub = 0; jp = []; jc = []
    for s in seeds:
        a = d[f'{b}_seed_{s}_B_final'][E] > 0.12; c = d[f'continue_seed_{s}_B_final'][E] > 0.12
        eq += int(np.array_equal(a, pred)); sub += int(np.all(pred[a])); jp.append(J(a, pred)); jc.append(J(a, c))
    out['table'][b] = dict(eq_closed_form=eq, subset=sub, jaccard_pred=float(np.mean(jp)), jaccard_continue=float(np.mean(jc)))
    print(b, out['table'][b])
dump('ablation14_topology.json', out)
