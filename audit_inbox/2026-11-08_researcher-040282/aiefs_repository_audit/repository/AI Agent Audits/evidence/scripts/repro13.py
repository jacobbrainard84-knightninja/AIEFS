"""Bit-exact reproduction of the archived AIEF-1.3 runs: 2 manifests x 5 conditions x 50 seeds = 500 runs.
Round 3 (2026-10-24): compares EVERY key stored in each archived .npz (all 7 matrices and all scalar/metadata fields),
not only the 4 headline scalars used before. Equality is exact (==), with NaN==NaN treated as equal. For mismatching scalar keys the abs/rel difference is recorded."""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); from _common import *
import AIEF_1_3_falsification_updated as f
from multiprocessing import Pool
HEAD = ['D_B', 'Corr_physical', 'Total_edge_weight', 'Effective_edges']
def eq(a, b):
    a = np.asarray(a); b = np.asarray(b)
    if a.shape != b.shape: return False
    if a.dtype.kind in 'fc' or b.dtype.kind in 'fc':
        a = a.astype(float); b = b.astype(float)
        return bool(np.all((a == b) | (np.isnan(a) & np.isnan(b))))
    return bool(np.all(a == b))
def job(a):
    run, cond, idx = a
    m = json.load(open(f'runs/{run}/manifest.json')); seed = m['randomization']['paired_seeds'][idx]
    r = f.run_aief(cond, seed=seed, seed_index=idx, config_hash=run)
    s = np.load(f'runs/{run}/{cond}_seed_{seed}.npz')
    keys = list(s.files); missing = [k for k in keys if k not in r]
    mism = [k for k in keys if k in r and not eq(r[k], s[k])]
    def dd(k):
        x, y = float(np.asarray(r[k])), float(np.asarray(s[k])); ad = abs(x - y)
        return dict(rerun=x, archived=y, abs_diff=ad, rel_diff=ad / max(abs(y), 1e-300))
    mism_mag = {k: dd(k) for k in mism if np.asarray(s[k]).ndim == 0 and np.asarray(s[k]).dtype.kind in 'fiu'}
    md = max(float(np.max(np.abs(np.asarray(r[k]) - s[k]))) for k in f.MATRIX_KEYS)
    sc = {k: (float(r[k]), float(s[k])) for k in HEAD}
    return dict(run=run, cond=cond, idx=idx, seed=int(seed), n_keys=len(keys), keys_missing_in_rerun=missing,
                keys_mismatched=mism, mismatch_magnitude=mism_mag, max_matrix_diff=md, scalars=sc)
if __name__ == '__main__':
    jobs = []
    for run in ['c3da1ac707bf', '73dca37cf93f']:
        m = json.load(open(f'runs/{run}/manifest.json')); n = len(m['randomization']['paired_seeds'])
        for cond in f.CONDITIONS:
            for idx in range(n): jobs.append((run, cond, idx))
    with Pool(7) as p: res = p.map(job, jobs)
    keysets = sorted({tuple(sorted(np.load(f"runs/{r['run']}/{r['cond']}_seed_{r['seed']}.npz").files)) for r in res[:1]})
    full = [r for r in res if not r['keys_missing_in_rerun'] and not r['keys_mismatched']]
    head = [r for r in res if r['max_matrix_diff'] == 0.0 and all(eq(*v) for v in r['scalars'].values())]
    summ = {}
    for c in f.CONDITIONS:
        rr = [r for r in res if r['cond'] == c]
        summ[c] = dict(n=len(rr), **{k: (float(np.nanmean(v)) if np.isfinite(v).any() else float('nan')) for k in HEAD for v in [np.array([r['scalars'][k][0] for r in rr])]})
        summ[c]['n_finite'] = {k: int(np.isfinite([r['scalars'][k][0] for r in rr]).sum()) for k in HEAD}
    nk = sorted({r['n_keys'] for r in res})
    print('runs', len(res), 'keys per npz', nk, 'all-keys bit-exact', len(full), 'matrices+4-scalars bit-exact', len(head))
    for c, v in summ.items(): print(c, v)
    bad = [r for r in res if r not in full]
    mag = {}
    for r in bad:
        for k, v in r['mismatch_magnitude'].items():
            g = mag.setdefault(k, dict(n_runs=0, max_abs_diff=0.0, max_rel_diff=0.0)); g['n_runs'] += 1
            g['max_abs_diff'] = max(g['max_abs_diff'], v['abs_diff']); g['max_rel_diff'] = max(g['max_rel_diff'], v['rel_diff'])
    print('mismatch magnitudes', mag)
    dump('repro13.json', dict(n_runs=len(res), keys_per_npz=nk, compared_keys=list(keysets[0]),
                              n_bit_exact_all_keys=len(full), n_bit_exact_matrices_and_4_headline_scalars=len(head), mismatch_summary_by_key=mag,
                              nonmatching_runs=[dict(run=r['run'], cond=r['cond'], seed=r['seed'], missing=r['keys_missing_in_rerun'], mismatched=r['keys_mismatched']) for r in bad],
                              per_condition_means=summ, runs=res), status='ok' if not bad else 'ok_with_warnings',
         warnings=[f"{len(bad)}/{len(res)} runs differ from the archive in at least one derived scalar ({', '.join(sorted(mag))}); "
                   f"max abs diff {max(g['max_abs_diff'] for g in mag.values()):.3g}, max rel diff {max(g['max_rel_diff'] for g in mag.values()):.3g}; "
                   f"matrices and the 4 headline scalars are bit-exact in {len(head)}/{len(res)}"] if bad else [])
