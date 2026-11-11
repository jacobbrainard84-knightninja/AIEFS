"""NEW (response round). Points 2 and 7.
Exploratory-but-preregistered-in-this-file design:
  omega sets: 15 uniform U(1,2)^12 + 15 clustered (2-4 centres, sd 0.02), rng seed 20261023
  per omega: seeds 1..4, each run with condition baseline (tau=0.5) AND no_delay (paired: identical init state)
  plus the repo omega with archived seeds (read from runs/c3da1ac707bf + runs/73dca37cf93f, not re-simulated).
Saves per-run per-edge arrays (|dw|, R_pred, R_physical_past, P_future, B_final, B_at_split) as text CSV
(results/delay_paired_edges_uniform.csv, results/delay_paired_edges_clustered.csv; 9 significant digits) and scalar summaries to results/delay_paired_runs.json. Analysis is in analyze_delay_heldout.py."""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); from _common import *
import AIEF_1_3_falsification_updated as f
from multiprocessing import Pool
E = f.EDGES
def setomega(om):
    f.OMEGA = np.array(om); f.T_WINDOW = 25.0 / float(np.mean(om)); f.ALPHA = float(np.exp(-f.DT / f.T_WINDOW))
def rpred(om):
    a = float(np.exp(-f.DT / (25.0 / np.mean(om)))); dw = np.abs(np.subtract.outer(om, om))[E]
    return dw, np.abs((1 - a) / (1 - a * np.exp(1j * dw * f.DT)))
def job(a):
    kind, k, om, cond, seed = a
    setomega(om); r = f.run_aief(cond, seed=seed, seed_index=0, config_hash='delay_paired')
    dw, rp = rpred(np.array(om))
    return dict(kind=kind, k=k, cond=cond, seed=seed, D_B=r['D_B'], Corr_physical=r['Corr_physical'], W=r['Total_edge_weight'],
                r_mean=r['r_mean'], dw=dw, Rpred=rp, Rpast=r['R_physical_past'][E], P=r['P_future'][E], Bf=r['B_final'][E], Bsplit=r['B_at_split'][E])
KEYS = ['dw', 'Rpred', 'Rpast', 'P', 'Bf', 'Bsplit']
def write_edges_csv(res):
    fh = {kd: open(OUT / f'delay_paired_edges_{kd}.csv', 'w') for kd in ['uniform', 'clustered']}
    for h in fh.values(): h.write('run,kind,k,cond,seed,i,j,' + ','.join(KEYS) + '\n')
    for n, r in enumerate(res):
        for e in range(len(E[0])):
            fh[r['kind']].write(f"{n},{r['kind']},{r['k']},{r['cond']},{r['seed']},{E[0][e]},{E[1][e]}," + ','.join(f'{float(r[q][e]):.9g}' for q in KEYS) + '\n')
        for q in KEYS: r.pop(q)
    for h in fh.values(): h.close()
if __name__ == '__main__':
    rng = np.random.default_rng(20261023); jobs = []
    for k in range(15):
        om = list(rng.uniform(1.0, 2.0, 12))
        for s in range(1, 5):
            for cond in ['baseline', 'no_delay']: jobs.append(('uniform', k, om, cond, s))
    for k in range(15):
        c = rng.uniform(1.0, 2.0, rng.integers(2, 5)); om = list(rng.choice(c, 12) + rng.normal(0, 0.02, 12))
        for s in range(1, 5):
            for cond in ['baseline', 'no_delay']: jobs.append(('clustered', k, om, cond, s))
    with Pool(7) as p: res = p.map(job, jobs)
    write_edges_csv(res)
    dump('delay_paired_runs.json', dict(omegas={f'{j[0]}_{j[1]}': j[2] for j in jobs}, runs=res))
    print('runs', len(res))
