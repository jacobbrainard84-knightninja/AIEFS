"""NEW (response round). Analyses for collaborator points 2 and 7.
Inputs: results/delay_paired_edges_{uniform,clustered}.csv + results/delay_paired_runs.json (from delay_paired_heldout.py),
        archived repo-omega runs runs/c3da1ac707bf, runs/73dca37cf93f (baseline + no_delay, 100 paired seeds).
Point 7: paired delay on/off: per-run scalar differences (cluster = omega set), topology Jaccard same-seed vs cross-seed,
         within-condition vs cross-condition (a systematic delay effect => J(base,base') > J(base,nodelay')).
Point 2: does the endogenous R_physical_past (the repo's Corr_physical input) beat the Delta-omega-only closed-form R_pred
         on HELD-OUT omega sets (leave-one-omega-set-out) and HELD-OUT seeds (repo omega, 10-fold by seed)?
         Targets: y = B_final > B_C (edge persists); continuous P_future (Spearman/Pearson). Logistic regression via IRLS."""
import sys, os, json, csv, itertools, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); from _common import *
import AIEF_1_3_falsification_updated as f
E = f.EDGES; BC = f.B_C
rows = []
for kd in ['uniform', 'clustered']:
    with open(OUT / f'delay_paired_edges_{kd}.csv') as fh: rows += list(csv.DictReader(fh))
runs = {}
for r in rows:
    key = (r['kind'], int(r['k']), r['cond'], int(r['seed']))
    runs.setdefault(key, {q: [] for q in ['dw', 'Rpred', 'Rpast', 'P', 'Bf', 'Bsplit']})
    for q in runs[key]: runs[key][q].append(float(r[q]))
runs = {k: {q: np.array(v) for q, v in d.items()} for k, d in runs.items()}
meta = {(r['kind'], r['k'], r['cond'], r['seed']): r for r in json.load(open(OUT / 'delay_paired_runs.json'))['runs']}
rng = np.random.default_rng(0)
def boot(x, n=10000):
    x = np.asarray(x, float); x = x[np.isfinite(x)]; m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(n)]
    return [float(x.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5)), int(len(x))]
def jac(a, b):
    u = (a | b).sum(); return 1.0 if u == 0 else float((a & b).sum() / u)
def auc(s, y):
    from scipy.stats import rankdata
    r = rankdata(s); n1 = y.sum(); n0 = len(y) - n1
    return float((r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)) if n1 and n0 else float('nan')
def logit_fit(X, y, lam=1e-3):
    X = np.column_stack([np.ones(len(X)), X]); w = np.zeros(X.shape[1])
    for _ in range(50):
        p = 1 / (1 + np.exp(-X @ w)); H = X.T @ (X * (p * (1 - p))[:, None]) + lam * np.eye(len(w)); g = X.T @ (p - y) + lam * w
        w -= np.linalg.solve(H, g)
    return w
def logit_pred(w, X): return 1 / (1 + np.exp(-(np.column_stack([np.ones(len(X)), X]) @ w)))
def logloss(p, y): p = np.clip(p, 1e-9, 1 - 1e-9); return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))
def heldout(groups, feats):
    """groups: list of (X dict, y) per group; leave-one-group-out. Returns pooled AUC / logloss per feature set."""
    out = {}
    for name, cols in feats.items():
        P, Y = [], []
        for g in range(len(groups)):
            tr = [groups[h] for h in range(len(groups)) if h != g]
            Xtr = np.vstack([np.column_stack([d[0][c] for c in cols]) for d in tr]); ytr = np.concatenate([d[1] for d in tr])
            mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-12; w = logit_fit((Xtr - mu) / sd, ytr)
            Xte = np.column_stack([groups[g][0][c] for c in cols]); P.append(logit_pred(w, (Xte - mu) / sd)); Y.append(groups[g][1])
        P, Y = np.concatenate(P), np.concatenate(Y).astype(bool)
        out[name] = dict(auc=auc(P, Y), logloss=logloss(P, Y), n=int(len(Y)), pos_rate=float(Y.mean()))
    return out
FEATS = {'Rpred_only (Delta-omega closed form)': ['Rpred'], 'Rpast_only (endogenous, = Corr_physical input)': ['Rpast'],
         'Rpred+Rpast': ['Rpred', 'Rpast'], 'Bsplit_only (weights at split)': ['Bsplit']}
from scipy.stats import spearmanr, pearsonr
res = {}
# ---------------- Point 7: paired delay on/off on random omega ----------------
p7 = {}
for kd in ['uniform', 'clustered']:
    d = {}
    diffs = {m: [] for m in ['D_B', 'Corr_physical', 'W', 'r_mean', 'n_active']}
    Jsame, Jcross_x, Jwithin_b, Jwithin_n, nb_distinct, nn_distinct, shared_basin = [], [], [], [], [], [], []
    for k in range(15):
        A = {c: {s: runs[(kd, k, c, s)]['Bf'] > BC for s in range(1, 5)} for c in ['baseline', 'no_delay']}
        om_d = {m: [] for m in diffs}
        for s in range(1, 5):
            mb, mn = meta[(kd, k, 'baseline', s)], meta[(kd, k, 'no_delay', s)]
            for m in ['D_B', 'Corr_physical', 'W', 'r_mean']: om_d[m].append(mb[m] - mn[m])
            om_d['n_active'].append(int(A['baseline'][s].sum()) - int(A['no_delay'][s].sum()))
        for m in diffs: diffs[m].append(float(np.nanmean(om_d[m])) if np.isfinite(om_d[m]).any() else float('nan'))
        Jsame.append(np.mean([jac(A['baseline'][s], A['no_delay'][s]) for s in range(1, 5)]))
        Jcross_x.append(np.mean([jac(A['baseline'][s], A['no_delay'][t]) for s in range(1, 5) for t in range(1, 5) if s != t]))
        Jwithin_b.append(np.mean([jac(A['baseline'][s], A['baseline'][t]) for s, t in itertools.combinations(range(1, 5), 2)]))
        Jwithin_n.append(np.mean([jac(A['no_delay'][s], A['no_delay'][t]) for s, t in itertools.combinations(range(1, 5), 2)]))
        tb = {A['baseline'][s].tobytes() for s in range(1, 5)}; tn = {A['no_delay'][s].tobytes() for s in range(1, 5)}
        nb_distinct.append(len(tb)); nn_distinct.append(len(tn)); shared_basin.append(len(tb & tn) > 0)
    d['paired_diff_baseline_minus_nodelay_mean_ci95_over_15_omega'] = {m: boot(v) for m, v in diffs.items()}
    d['jaccard'] = dict(same_seed_cross_condition=boot(Jsame), cross_seed_cross_condition=boot(Jcross_x),
                        cross_seed_within_baseline=boot(Jwithin_b), cross_seed_within_nodelay=boot(Jwithin_n),
                        same_minus_crossseed_crosscond=boot(np.array(Jsame) - np.array(Jcross_x)),
                        within_baseline_minus_crosscond=boot(np.array(Jwithin_b) - np.array(Jcross_x)))
    d['distinct_topologies_of_4_seeds'] = dict(baseline_mean=float(np.mean(nb_distinct)), no_delay_mean=float(np.mean(nn_distinct)),
        omega_sets_where_baseline_more=int(sum(b > n for b, n in zip(nb_distinct, nn_distinct))),
        omega_sets_where_nodelay_more=int(sum(b < n for b, n in zip(nb_distinct, nn_distinct))),
        omega_sets_sharing_any_topology=int(sum(shared_basin)))
    p7[kd] = d
# repo omega, archived 100 paired seeds
def load_archived():
    out = {'baseline': [], 'no_delay': []}
    for run in ['c3da1ac707bf', '73dca37cf93f']:
        m = json.load(open(f'runs/{run}/manifest.json'))
        for s in m['randomization']['paired_seeds']:
            for c in out:
                z = np.load(f'runs/{run}/{c}_seed_{s}.npz')
                out[c].append(dict(seed=int(s), Bf=z['B_final'][E], Rpast=z['R_physical_past'][E], P=z['P_future'][E], Bsplit=z['B_at_split'][E],
                                   D_B=float(z['D_B']), Corr_physical=float(z['Corr_physical']), W=float(z['Total_edge_weight'])))
    return out
AR = load_archived()
dwr = np.abs(np.subtract.outer(f.OMEGA, f.OMEGA))[E]; Rpr = np.abs((1 - f.ALPHA) / (1 - f.ALPHA * np.exp(1j * dwr * f.DT)))
Ab = [x['Bf'] > BC for x in AR['baseline']]; An = [x['Bf'] > BC for x in AR['no_delay']]
n = len(Ab)
p7['repo_omega_archived'] = dict(n_seeds=n,
    distinct_baseline=len({a.tobytes() for a in Ab}), distinct_no_delay=len({a.tobytes() for a in An}),
    paired_diff_D_B=boot([b['D_B'] - c['D_B'] for b, c in zip(AR['baseline'], AR['no_delay'])]),
    paired_diff_W=boot([b['W'] - c['W'] for b, c in zip(AR['baseline'], AR['no_delay'])]),
    paired_diff_Corr_physical=boot([b['Corr_physical'] - c['Corr_physical'] for b, c in zip(AR['baseline'], AR['no_delay'])]),
    seeds_topology_differs=int(sum((a != b).any() for a, b in zip(Ab, An))),
    jaccard_same_seed=boot([jac(a, b) for a, b in zip(Ab, An)]),
    jaccard_cross_seed_within_baseline=float(np.mean([jac(Ab[i], Ab[j]) for i in range(n) for j in range(i + 1, n)])))
res['point7_delay'] = p7
# ---------------- Point 2: held-out predictors ----------------
p2 = {}
for cond in ['baseline', 'no_delay']:
    for kd in ['uniform', 'clustered']:
        groups, cor = [], dict(pearson_P_Rpred=[], pearson_P_Rpast=[], spearman_P_Rpred=[], spearman_P_Rpast=[], partial_P_Rpast_given_Rpred=[])
        for k in range(15):
            X = {c: np.concatenate([runs[(kd, k, cond, s)][c] for s in range(1, 5)]) for c in ['Rpred', 'Rpast', 'Bsplit']}
            y = np.concatenate([runs[(kd, k, cond, s)]['Bf'] > BC for s in range(1, 5)]).astype(float)
            groups.append((X, y))
            for s in range(1, 5):
                r = runs[(kd, k, cond, s)]
                if np.std(r['P']) == 0: continue
                cor['pearson_P_Rpred'].append(pearsonr(r['P'], r['Rpred'])[0]); cor['pearson_P_Rpast'].append(pearsonr(r['P'], r['Rpast'])[0])
                cor['spearman_P_Rpred'].append(spearmanr(r['P'], r['Rpred'])[0]); cor['spearman_P_Rpast'].append(spearmanr(r['P'], r['Rpast'])[0])
                # partial correlation of P with Rpast controlling for Rpred (linear residualisation)
                ep = r['P'] - np.polyval(np.polyfit(r['Rpred'], r['P'], 1), r['Rpred']); er = r['Rpast'] - np.polyval(np.polyfit(r['Rpred'], r['Rpast'], 1), r['Rpred'])
                cor['partial_P_Rpast_given_Rpred'].append(float(np.corrcoef(ep, er)[0, 1]) if np.std(er) > 0 and np.std(ep) > 0 else float('nan'))
        p2[f'{kd}_{cond}'] = dict(heldout_omega_LOGO=heldout(groups, FEATS),
                                  per_run_correlations={q: [float(np.nanmean(v)), float(np.nanmedian(v)), len(v)] for q, v in cor.items()},
                                  rpast_beats_rpred_pearson_runs=int(sum(a > b for a, b in zip(cor['pearson_P_Rpast'], cor['pearson_P_Rpred']))))
# repo omega, held-out seeds (10 folds by seed)
for cond in ['baseline', 'no_delay']:
    L = AR[cond]; folds = [L[i::10] for i in range(10)]
    groups = [({'Rpred': np.concatenate([Rpr] * len(fo)), 'Rpast': np.concatenate([x['Rpast'] for x in fo]), 'Bsplit': np.concatenate([x['Bsplit'] for x in fo])},
               np.concatenate([x['Bf'] > BC for x in fo]).astype(float)) for fo in folds]
    pr = [pearsonr(x['P'], Rpr)[0] for x in L if np.std(x['P']) > 0]; pp = [pearsonr(x['P'], x['Rpast'])[0] for x in L if np.std(x['P']) > 0]
    p2[f'repo_omega_{cond}'] = dict(heldout_seed_10fold=heldout(groups, FEATS), mean_pearson_P_Rpred=float(np.mean(pr)), mean_pearson_P_Rpast=float(np.mean(pp)),
                                    rpast_beats_rpred_runs=int(sum(a > b for a, b in zip(pp, pr))), n=len(pp))
res['point2_heldout'] = p2
# ---------------- Point 1: closed-form set as subgraph? (replication on the new omega sets) ----------------
RSTAR = f.MU / (f.ETA + f.MU); p1 = {}
for kd in ['uniform', 'clustered']:
    for cond in ['baseline', 'no_delay']:
        tp = fp = fn = sub = ex = 0; nruns = 0
        for k in range(15):
            for s in range(1, 5):
                r = runs[(kd, k, cond, s)]; act = r['Bf'] > BC; pred = r['Rpred'] > RSTAR; nruns += 1
                tp += int((act & pred).sum()); fp += int((act & ~pred).sum()); fn += int((~act & pred).sum())
                sub += bool(np.all(pred[act])); ex += bool(np.all(act == pred))
        p1[f'{kd}_{cond}'] = dict(runs=nruns, subset=sub, exact=ex, precision_pooled=tp / max(tp + fp, 1), recall_pooled=tp / max(tp + fn, 1))
res['point1_subgraph_replication'] = p1
dump('delay_heldout_analysis.json', res)
print(json.dumps(res, indent=1))
