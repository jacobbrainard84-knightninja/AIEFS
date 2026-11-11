"""NEW (round 3, 2026-10-24). Summarises results/kappa_cycle_kernel.json -> results/kappa_cycle_kernel_summary.json.
Compares the restricted fiber multiplier with the closed form, re-counts slow channels by fiber dimension, cross-checks the
old central-difference classification in results/kappa_tw_all.json, and records the tie non-additivity and K3 one-sided data.
Cohort caveat: the replays are 40 fixed seeds x 5 T_w of one S01 run; components are NOT independent replications."""
import sys, os, json, collections, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); from _common import *
D = json.load(open(inp('kappa_cycle_kernel.json'))); R = D['replays']
old = {(r['seed'], r['rho'], tuple(c['nodes'])): c for r in json.load(open(inp('kappa_tw_all.json'))) for c in r['comps']}
C = [(r, c) for r in R for c in r['comps']]
fib = [(r, c) for r, c in C if c['kernel_dim'] > 0]
S = dict(n_replays=len(R), n_seeds=len({r['seed'] for r in R}), n_components=len(C),
         cohort_caveat='40 fixed seeds x 5 T_w (one S01 run); the same seed contributes the same component pattern at several T_w; counts are not independent replications')
lbl = lambda c: f"K{c['n_nodes']}" if c['complete'] else f"noncomplete_{c['n_nodes']}nodes_{c['n_edges']}edges"
S['components_by_type'] = dict(collections.Counter(lbl(c) for _, c in C))
S['nonzero_fiber_by_type'] = dict(collections.Counter(f"{lbl(c)} (degree k={c['k']})" for _, c in fib))
S['nonzero_fiber_distinct_seeds_by_type'] = {t: len({r['seed'] for r, c in fib if lbl(c) == t}) for t in sorted({lbl(c) for _, c in fib})}
S['fiber_dim_check'] = dict(complete_all_tied_components=sum(1 for _, c in C if c['complete'] and c['n_tied_edges'] == c['n_edges']),
    all_tied_with_dim_eq_m_minus_n=sum(1 for _, c in C if c['complete'] and c['n_tied_edges'] == c['n_edges'] and c['kernel_dim'] == c['expected_cycle_kernel_dim']))
F = [f for _, c in fib for f in c['fiber']]
S['fiber_checks'] = dict(n_directions=len(F), max_AJh=max(f['AJh'] for f in F), max_rel_residual=max(f['rel_residual'] for f in F),
                         max_pm_asymmetry=max(f['pm_asym'] for f in F), max_leak_outside_component=max(f['leak'] for f in F),
                         max_lam_spread_within_component=max(c['lam_fiber_spread'] for _, c in fib))
S['multiplier_vs_closed_form'] = dict(max_rel_err_lam=max(c['rel_err_lam_vs_closed_form'] for _, c in fib),
    max_rel_err_lam_vs_state_formula=max(c['rel_err_lam_vs_state'] for _, c in fib),
    max_rel_err_rate=max(c['rel_err_r_vs_closed_form'] for _, c in fib),
    max_abs_err_kappa=max(abs(c['kappa_fiber'] - c['kappa_closed_form']) for _, c in fib),
    worst=max(({'seed': r['seed'], 'rho': r['rho'], 'type': lbl(c), 'R_min': c['R_min'], 'rel_err_rate': c['rel_err_r_vs_closed_form']} for r, c in fib), key=lambda z: z['rel_err_rate']))
S['per_rho'] = {}
for rho in sorted({r['rho'] for r in R}):
    g = [(r, c) for r, c in fib if r['rho'] == rho]; Tw = [r['T_w'] for r in R if r['rho'] == rho][0]
    S['per_rho'][str(rho)] = dict(T_w=Tw, by_k={str(k): dict(n=len(gk), kappa_closed_form=gk[0][1]['kappa_closed_form'],
        kappa_fiber_range=[min(c['kappa_fiber'] for _, c in gk), max(c['kappa_fiber'] for _, c in gk)])
        for k in sorted({c['k'] for _, c in g}) for gk in [[x for x in g if x[1]['k'] == k]]})
# cross-check against the old central-difference 'slow channel' flag (|eig| > 0.99)
agree = collections.Counter()
for r, c in C:
    o = old.get((r['seed'], r['rho'], tuple(c['nodes'])))
    if o is None: agree['no_match_in_kappa_tw_all'] += 1; continue
    agree[f"old_slow={max(o['eigs_abs']) > 0.99} new_fiber={c['kernel_dim'] > 0}"] += 1
    if c['kernel_dim'] > 0 and max(o['eigs_abs']) > 0.99:
        agree['max_rel_diff_old_rB_vs_fiber_rate'] = max(agree.get('max_rel_diff_old_rB_vs_fiber_rate', 0), abs(o['r_B_frozen'] - c['r_fiber']) / c['r_fiber'])
S['old_central_difference_vs_fiber'] = dict(agree)
# resolution: the step delta must sit well above every tied gap and well below every untied gap
res_ok = lambda c: (c['delta_over_tied_gap'] is None or c['delta_over_tied_gap'] >= 100) and (c['untied_gap_over_delta'] is None or c['untied_gap_over_delta'] >= 100)
poor = [(r, c) for r, c in C if not res_ok(c)]
S['step_resolution'] = dict(rule='tied if |s_i - s_j| <= tie_tol (1e-9); delta_c = geometric mean of max tied gap and min untied gap, capped at min untied gap/100, clipped to [1e-11, 1e-5]; resolved if delta_c >= 100 x max tied gap and min untied gap >= 100 x delta_c',
    n_resolved=len(C) - len(poor), n_poorly_resolved=len(poor),
    poorly_resolved_by_rho=dict(collections.Counter(str(r['rho']) for r, _ in poor)),
    poorly_resolved_by_type=dict(collections.Counter(lbl(c) for _, c in poor)),
    poorly_resolved_max_rel_err_rate=max((c.get('rel_err_r_vs_closed_form', 0) for _, c in poor), default=None),
    resolved_max_rel_err_rate=max(c['rel_err_r_vs_closed_form'] for _, c in fib if res_ok(c)),
    resolved_max_rel_err_lam=max(c['rel_err_lam_vs_closed_form'] for _, c in fib if res_ok(c)),
    resolved_max_abs_err_kappa=max(abs(c['kappa_fiber'] - c['kappa_closed_form']) for _, c in fib if res_ok(c)),
    note='poorly resolved components are near-ties still converging at t=250 (gaps ~1e-12..1e-8 at T_w=35); their tie/strict classification depends on the snapshot time and tolerance')
T = [c['tie_nonadditivity'] | {'type': lbl(c)} for _, c in C if 'tie_nonadditivity' in c and res_ok(c) and c['n_tied_edges'] == c['n_edges']]
S['tie_nonadditivity_all_tied_resolved'] = {t: dict(n=len(g), min_rel_nonadditivity=min(x['rel_nonadditivity'] for x in g), max_rel_nonadditivity=max(x['rel_nonadditivity'] for x in g),
                                  min_rel_odd_defect=min(x['rel_odd_defect'] for x in g), max_rel_odd_defect=max(x['rel_odd_defect'] for x in g))
                          for t in sorted({x['type'] for x in T}) for g in [[x for x in T if x['type'] == t]]}
k3 = [(r, c) for r, c in C if c['n_nodes'] == 3 and c['complete']]
def os_slow(c, side):
    lamk = c['lam_closed_form']; return [o['node'] for o in c['K3_one_sided'] if abs(o[side]['lam'] - lamk) / lamk < 1e-6 and o[side]['rel_residual'] < 1e-6]
S['K3'] = dict(n_K3_components=len(k3), n_distinct_seeds=len({r['seed'] for r, _ in k3}),
    all_tied=sum(1 for _, c in k3 if c['n_tied_edges'] == 3), all_tied_by_rho=dict(collections.Counter(str(r['rho']) for r, c in k3 if c['n_tied_edges'] == 3)),
    with_two_sided_fiber=[dict(seed=r['seed'], rho=r['rho'], J=c['J'], s_spread=c['s_spread_comp'], min_untied_gap=c['min_untied_gap'], delta=c['delta'], resolved=res_ok(c), kappa_fiber=c['kappa_fiber'], kappa_closed_form=c['kappa_closed_form']) for r, c in k3 if c['kernel_dim'] > 0],
    tied_with_one_sided_slow_direction_plus=sum(1 for _, c in k3 if c['n_tied_edges'] == 3 and os_slow(c, 'plus')),
    one_sided_plus_all_nodes_max_rel_err_lam_vs_closed_form_k2=max(abs(o['plus']['lam'] - c['lam_closed_form']) / c['lam_closed_form'] for _, c in k3 if c['n_tied_edges'] == 3 for o in c['K3_one_sided']),
    one_sided_plus_all_nodes_max_rel_residual=max(o['plus']['rel_residual'] for _, c in k3 if c['n_tied_edges'] == 3 for o in c['K3_one_sided']),
    one_sided_plus_slow_nodes_per_component_by_rho={str(rh): dict(collections.Counter(len(os_slow(c, 'plus')) for r, c in k3 if c['n_tied_edges'] == 3 and r['rho'] == rh)) for rh in sorted({r['rho'] for r, _ in k3})},
    one_sided_minus_all_nodes_min_rel_err_lam=min(abs(o['minus']['lam'] - c['lam_closed_form']) / c['lam_closed_form'] for _, c in k3 if c['n_tied_edges'] == 3 for o in c['K3_one_sided']),
    tied_with_one_sided_slow_direction_minus=sum(1 for _, c in k3 if c['n_tied_edges'] == 3 and os_slow(c, 'minus')),
    note='v_c = +1 on the edge opposite node c, -1 on the two edges at c. On an all-tied K3, +v_c lowers row c only, so c stops controlling and the other two rows are preserved: a ONE-SIDED slow direction at rate r_{B,2}; -v_c is not.')
print(json.dumps(S, indent=1, default=float))
dump('kappa_cycle_kernel_summary.json', S)
