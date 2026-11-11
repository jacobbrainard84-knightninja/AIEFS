"""Summarise results/kappa_tw_all.json -> results/kappa_tw_summary.json and results/kappa_tw_components.csv.
ROUND-3 CORRECTION (2026-10-24, response-2 #2): 'Jacobian' below is a central-difference matrix, not a derivative (ties);
the K3 statement '(fully saturated K3s have none: ...)' is wrong as a statement about slow directions: every all-tied K3 has a
ONE-SIDED slow direction (see kappa_cycle_kernel_summary.json). Kept unchanged for provenance.
A component 'has a slow selected B-channel' if its frozen one-step Jacobian has an eigenvalue with |lambda| > 0.99
(fully saturated K3s have none: their lineality space is {0})."""
import sys, os, json, csv, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); from _common import *
eta, gam, dt, c = 0.04, 0.015, 0.01, 0.95 / 1.5
res = json.load(open(inp('kappa_tw_all.json')))
rows = []
for r in res:
    for cp in r['comps']:
        k = max(cp['degrees']); slow = max(cp['eigs_abs']) > 0.99
        x = k * eta / (c * (1 - gam * dt)); rdisc = np.log(1 + dt * x) / dt
        rows.append(dict(seed=r['seed'], rho=r['rho'], T_w=r['T_w'], nodes=' '.join(map(str, cp['nodes'])), m=len(cp['nodes']), n_edges=cp['n_edges'],
            degrees=' '.join(map(str, cp['degrees'])), max_rowsum_margin=max(cp['rowsum_margin']), R_min=cp['R_min_on_edges'], slow_channel=slow,
            n_slow_eigs=int(sum(e > 0.99 for e in cp['eigs_abs'])), r_B_frozen=cp['r_B_frozen'] if slow else float('nan'),
            k_eta_over_c=k * eta / c, r_B_discrete_R1=rdisc, twin_early=cp['twin_rate_early_1_8'], twin_late=cp['twin_rate_late_25_40'],
            kappa_exact=(cp['r_B_frozen'] - r['r_g']) if slow else float('nan'), kappa_formula_cont=k * eta / c - 1 / r['T_w'], kappa_formula_disc=rdisc - r['r_g']))
with open(OUT / 'kappa_tw_components.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator='\n'); w.writeheader(); w.writerows(rows)
S = dict(n_replays=len(res), replay_bitexact=sum(r['replay_maxdiff_B_final'] == 0.0 for r in res),
         replay_max_diff=max(r['replay_maxdiff_B_final'] for r in res), n_components=len(rows))
sl = [x for x in rows if x['slow_channel']]
S['slow_channel_components'] = dict(n=len(sl), by_k={int(k): sum(1 for x in sl if max(map(int, x['degrees'].split())) == k) for k in sorted({max(map(int, x['degrees'].split())) for x in sl})},
    max_rel_err_rB_frozen_vs_k_eta_c=max(abs(x['r_B_frozen'] - x['k_eta_over_c']) / x['k_eta_over_c'] for x in sl),
    max_rel_err_rB_frozen_vs_discrete=max(abs(x['r_B_frozen'] - x['r_B_discrete_R1']) / x['r_B_discrete_R1'] for x in sl),
    max_abs_err_kappa_vs_cont=max(abs(x['kappa_exact'] - x['kappa_formula_cont']) for x in sl),
    max_abs_err_kappa_vs_disc=max(abs(x['kappa_exact'] - x['kappa_formula_disc']) for x in sl),
    twin_vs_frozen_rel=dict(median=float(np.median([abs(x['twin_early'] - x['r_B_frozen']) / x['r_B_frozen'] for x in sl])),
                            frac_within_1em3=float(np.mean([abs(x['twin_early'] - x['r_B_frozen']) / x['r_B_frozen'] < 1e-3 for x in sl]))))
k3 = [x for x in rows if x['m'] == 3]
S['K3'] = dict(n=len(k3), with_slow_channel=[dict((q, x[q]) for q in ['seed', 'rho', 'T_w', 'max_rowsum_margin', 'r_B_frozen', 'twin_early', 'kappa_exact', 'kappa_formula_cont', 'kappa_formula_disc']) for x in k3 if x['slow_channel']],
               fully_saturated_no_slow_channel=sum(1 for x in k3 if not x['slow_channel']),
               fully_saturated_twin_early_median=float(np.median([x['twin_early'] for x in k3 if not x['slow_channel']])))
S['per_rho'] = {}
for rho in sorted({x['rho'] for x in rows}):
    g = [x for x in sl if x['rho'] == rho]; tw = [x['T_w'] for x in rows if x['rho'] == rho][0]
    S['per_rho'][str(rho)] = dict(T_w=tw, r_g=1 / tw, n_slow=len(g), by_k={})
    for k in sorted({max(map(int, x['degrees'].split())) for x in g}):
        gk = [x for x in g if max(map(int, x['degrees'].split())) == k]
        S['per_rho'][str(rho)]['by_k'][k] = dict(n=len(gk), kappa_formula_cont=k * eta / c - 1 / tw, kappa_formula_disc=gk[0]['kappa_formula_disc'],
            kappa_exact_mean=float(np.mean([x['kappa_exact'] for x in gk])), kappa_exact_range=[float(min(x['kappa_exact'] for x in gk)), float(max(x['kappa_exact'] for x in gk))],
            twin_minus_rg_median=float(np.median([x['twin_early'] - 1 / tw for x in gk])))
print(json.dumps(S, indent=1, default=float))
dump('kappa_tw_summary.json', S)
