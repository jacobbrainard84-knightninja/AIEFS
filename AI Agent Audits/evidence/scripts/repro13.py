"""Bit-exact reproduction of archived AIEF-1.3 runs (5 conditions x 100 seeds, two run dirs split as in original audit).
Original audit invoked per (run,cond,idx); this wrapper does the same set in a Pool and writes a JSON summary."""
import sys, os, json, time, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); from _common import *
import AIEF_1_3_falsification_updated as f
from multiprocessing import Pool
def job(a):
    run, cond, idx = a
    m = json.load(open(f'runs/{run}/manifest.json')); seed = m['randomization']['paired_seeds'][idx]
    r = f.run_aief(cond, seed=seed, seed_index=idx, config_hash=run)
    s = np.load(f'runs/{run}/{cond}_seed_{seed}.npz')
    md = max(float(np.max(np.abs(np.asarray(r[k]) - s[k]))) for k in f.MATRIX_KEYS)
    sc = {k: (float(r[k]), float(s[k])) for k in ['D_B', 'Corr_physical', 'Total_edge_weight', 'Effective_edges']}
    return dict(run=run, cond=cond, idx=idx, seed=int(seed), max_matrix_diff=md, scalars=sc)
if __name__ == '__main__':
    jobs = []
    for run in ['c3da1ac707bf', '73dca37cf93f']:
        m = json.load(open(f'runs/{run}/manifest.json')); n = len(m['randomization']['paired_seeds'])
        for cond in f.CONDITIONS:
            for idx in range(n): jobs.append((run, cond, idx))
    with Pool(7) as p: res = p.map(job, jobs)
    def same(a, b): return (a == b) or (np.isnan(a) and np.isnan(b))
    exact = [r for r in res if r['max_matrix_diff'] == 0.0 and all(same(*v) for v in r['scalars'].values())]
    summ = {}
    for c in f.CONDITIONS:
        rr = [r for r in res if r['cond'] == c]
        summ[c] = dict(n=len(rr), **{k: float(np.nanmean([r['scalars'][k][0] for r in rr])) for k in ['D_B', 'Corr_physical', 'Total_edge_weight', 'Effective_edges']})
    print('runs', len(res), 'bit-exact', len(exact))
    for c, v in summ.items(): print(c, v)
    dump('repro13.json', dict(n_runs=len(res), n_bit_exact=len(exact), per_condition_means=summ, runs=res))
