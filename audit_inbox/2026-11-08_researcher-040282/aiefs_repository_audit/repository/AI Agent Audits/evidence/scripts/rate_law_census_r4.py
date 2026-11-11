"""NEW (round 4, 2026-10-25). Response-3 points 1-3. Reads results/kappa_cycle_kernel.json (no new simulation) and writes
results/rate_law_census_r4.json. Run from the AIEFS repo root (needs AIEF_1_4_Twindow_sensitivity for the model parameters).
  #1 census split: the 406 components fall into two disjoint classes -
       (a) components with a two-sided nonzero controller/cycle-kernel fiber (kernel_dim > 0), and
       (b) all-tied K3s (ker A_K3 = 0) whose slow directions are one-sided controller-selection rays +v_c.
     Counts, resolved counts (same resolution rule as analyze_kappa_cycle_kernel.py) and the error statistics are given
     separately per class, so "374 resolved" can be reported as (a)-resolved + (b)-resolved.
  #2 rate law: the exact state-dependent statement lam = (1 - gamma dt) s_J (equal controlling scales s_J) versus the
     parameter-only closed form lam_k = (1 - gamma dt) c / (c + dt (k eta - gamma c) + eps) (ideal R = 1, row sum c).
     We also solve the exact finite-eps scalar fixed point of the ideal locked/saturated clique (R = 1, all k edges of a
     row equal, all rows tied): S = q c/(q + eps), q = (1 - gamma dt) S + k eta dt, i.e.
        a S^2 + (b + eps - a c) S - b c = 0, a = 1 - gamma dt, b = k eta dt,
     lam_fp = a c / (q* + eps), and report |lam_fp - lam_k| / lam_k next to the observed deviations.
  #3 tie patterns: synthetic check of the derived formulas (see AIEFS_audit_response_3.md section 2.3)
        nonadditivity = 1/sqrt(2k(k-1)), odd defect = sqrt(2/(k+1))
     on an ideal all-tied K_n (n = k+1) with EQUAL edge weights, for n = 3..8, using an exact copy of the engine's gate
     step with R held fixed; plus one K4 with equal row sums but unequal edges, to show the formula needs equal edges.
     Also checks the one-sided K3 ray results D(+v_c) = lam v_c and <D(-v_c), v_c> = lam/3."""
import sys, os, json, math, collections, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); from _common import *
import AIEF_1_4_Twindow_sensitivity as tw
cfg = tw.create_model_config(1.0)
c, dt, eta, gam, eps = cfg.capacity, cfg.dt, cfg.eta, cfg.gamma, cfg.scale_epsilon
D = json.load(open(inp('kappa_cycle_kernel.json'))); R = D['replays']
C = [(r, x) for r in R for x in r['comps']]
res_ok = lambda x: (x['delta_over_tied_gap'] is None or x['delta_over_tied_gap'] >= 100) and (x['untied_gap_over_delta'] is None or x['untied_gap_over_delta'] >= 100)
lbl = lambda x: f"K{x['n_nodes']}" if x['complete'] else f"noncomplete_{x['n_nodes']}nodes"
two = [(r, x) for r, x in C if x['kernel_dim'] > 0]
k3t = [(r, x) for r, x in C if x['n_nodes'] == 3 and x['complete'] and x['n_tied_edges'] == 3]
other = [(r, x) for r, x in C if x['kernel_dim'] == 0 and not (x['n_nodes'] == 3 and x['complete'] and x['n_tied_edges'] == 3)]
def stats(g):
    return dict(n=len(g), max_rel_err_lam_vs_closed_form=max(x['rel_err_lam_vs_closed_form'] for _, x in g),
                max_rel_err_lam_vs_state_formula=max(x['rel_err_lam_vs_state'] for _, x in g),
                max_abs_err_kappa=max(abs(x['kappa_fiber'] - x['kappa_closed_form']) for _, x in g),
                max_rel_err_rate=max(x['rel_err_r_vs_closed_form'] for _, x in g),
                max_s_spread_J=max(x['s_spread_J'] for _, x in g), max_rel_residual=max(f['rel_residual'] for _, x in g for f in x['fiber']))
def os_nodes(x, side, tol=1e-6):
    lk = x['lam_closed_form']; return [o for o in x['K3_one_sided'] if abs(o[side]['lam'] - lk) / lk < tol and o[side]['rel_residual'] < tol]
out = {}
out['census'] = dict(
    n_components=len(C), by_type=dict(sorted(collections.Counter(lbl(x) for _, x in C).items())),
    two_sided_nonzero_fiber=dict(n=len(two), by_type=dict(sorted(collections.Counter(lbl(x) for _, x in two).items())),
                                 resolved=sum(res_ok(x) for _, x in two), poorly_resolved=sum(not res_ok(x) for _, x in two)),
    all_tied_K3_zero_lineality=dict(n=len(k3t), resolved=sum(res_ok(x) for _, x in k3t), kernel_dim_values=sorted({x['kernel_dim'] for _, x in k3t}),
                                    with_plus_ray_slow=sum(1 for _, x in k3t if os_nodes(x, 'plus')), with_minus_ray_slow=sum(1 for _, x in k3t if os_nodes(x, 'minus'))),
    other_components=len(other),
    complete_all_tied=dict(n=sum(1 for _, x in C if x['complete'] and x['n_tied_edges'] == x['n_edges']),
                           dim_ker_eq_n_n_minus_3_over_2=sum(1 for _, x in C if x['complete'] and x['n_tied_edges'] == x['n_edges'] and x['kernel_dim'] == x['n_nodes'] * (x['n_nodes'] - 3) // 2)),
    resolved_total=sum(res_ok(x) for _, x in C), poorly_resolved_total=sum(not res_ok(x) for _, x in C))
out['census']['split_identity'] = f"{out['census']['resolved_total']} resolved = {out['census']['two_sided_nonzero_fiber']['resolved']} resolved two-sided-fiber + {out['census']['all_tied_K3_zero_lineality']['resolved']} resolved all-tied K3 (one-sided rays)"
out['two_sided_resolved_errors'] = stats([z for z in two if res_ok(z[1])])
out['two_sided_poorly_resolved_errors'] = stats([z for z in two if not res_ok(z[1])])
slow = [(x, o) for _, x in k3t if res_ok(x) for o in os_nodes(x, 'plus')]
out['K3_one_sided_resolved_errors'] = dict(n_components=sum(1 for _, x in k3t if res_ok(x)), n_slow_node_rays=len(slow),
    max_rel_err_lam_vs_closed_form_slow_rays=max(abs(o['plus']['lam'] - x['lam_closed_form']) / x['lam_closed_form'] for x, o in slow),
    max_rel_residual_slow_rays=max(o['plus']['rel_residual'] for x, o in slow),
    max_rel_err_lam_vs_closed_form_all_plus_rays=max(abs(o['plus']['lam'] - x['lam_closed_form']) / x['lam_closed_form'] for _, x in k3t for o in x['K3_one_sided']),
    minus_ray_lam_over_lam_k_range=[min(o['minus']['lam'] / x['lam_closed_form'] for _, x in k3t for o in x['K3_one_sided']),
                                    max(o['minus']['lam'] / x['lam_closed_form'] for _, x in k3t for o in x['K3_one_sided'])])
# --- #2 exact finite-eps fixed point
a = 1 - gam * dt
fp = {}
for k in [2, 3, 4, 5]:
    b = k * eta * dt; B2 = b + eps - a * c
    S = (-B2 + math.sqrt(B2 * B2 + 4 * a * b * c)) / (2 * a); q = a * S + b
    lam_fp = a * c / (q + eps); lam_k = a * c / (c + dt * (k * eta - gam * c) + eps)
    fp[str(k)] = dict(row_sum_fixed_point=S, c_minus_row_sum=c - S, lam_fixed_point=lam_fp, lam_closed_form=lam_k,
                      rel_change_lam=abs(lam_fp - lam_k) / lam_k, abs_change_kappa=abs(math.log(lam_fp) - math.log(lam_k)) / dt)
out['finite_eps_fixed_point'] = dict(params=dict(c=c, dt=dt, eta=eta, gamma=gam, eps=eps), by_k=fp,
    note='lam_fp uses the exact finite-eps fixed-point row sum instead of c; relative changes are ~1e-12, i.e. far below the observed '
         'deviations (two_sided_resolved_errors.max_rel_err_lam_vs_closed_form) and below the 10-significant-digit storage of kappa_cycle_kernel.json. '
         'The observed deviations therefore come from the replayed state not being exactly at the ideal point (R < 1, finite time), not from eps.')
# --- #3 synthetic tie-pattern check with an exact copy of the gate step (R fixed at 1 within the step)
def gate_step(Bm, Rm):
    z = Bm + dt * ((cfg.eta + cfg.mu) * Rm - cfg.mu - gam * Bm); x = np.maximum(z, 0); x = 0.5 * (x + x.T); np.fill_diagonal(x, 0)
    s = np.minimum(1.0, c / (x.sum(1) + eps)); y = x * np.minimum.outer(s, s); np.fill_diagonal(y, 0); return y
def patterns(Bm, nodes):
    n = len(nodes); ed = [(nodes[i], nodes[j]) for i in range(n) for j in range(i + 1, n)]
    Rm = np.zeros_like(Bm)
    for i, j in ed: Rm[i, j] = Rm[j, i] = 1.0
    base = gate_step(Bm, Rm); dl = 1e-7
    def Dv(v):
        P = np.zeros_like(Bm)
        for e, (i, j) in enumerate(ed): P[i, j] = P[j, i] = v[e]
        y = (gate_step(Bm + dl * P, Rm) - base) / dl; return np.array([y[i, j] for i, j in ed])
    e2 = next(e for e in range(1, len(ed)) if set(ed[e]) & set(ed[0])); h1 = np.eye(len(ed))[0]; h2 = np.eye(len(ed))[e2]
    D1, D2, D12, Dm = Dv(h1), Dv(h2), Dv(h1 + h2), Dv(-h1)
    r = dict(nonadditivity=float(np.linalg.norm(D12 - D1 - D2) / np.linalg.norm(D1 + D2)), odd_defect=float(np.linalg.norm(D1 + Dm) / np.linalg.norm(D1)))
    if n == 3:
        lam = None; rays = []
        for cn in nodes:
            v = np.array([-1.0 if cn in e else 1.0 for e in ed]); v /= np.linalg.norm(v)
            dp = Dv(v); dm = -Dv(-v); lp = float(dp @ v); rays.append(dict(plus_lam=lp, plus_rel_residual=float(np.linalg.norm(dp - lp * v) / np.linalg.norm(dp)), minus_lam=float(dm @ v)))
        r['K3_rays'] = rays
    return r
def ideal_clique(n, w=None):
    """all-tied K_n near its locked/saturated fixed point: iterate the gate step with R = 1 from equal (or given) edges."""
    Bm = np.zeros((12, 12)); nodes = list(range(n)); k = n - 1
    for i in nodes:
        for j in nodes:
            if i != j: Bm[i, j] = c / k if w is None else w[min(i, j), max(i, j)]
    Rm = np.zeros((12, 12)); Rm[:n, :n] = 1.0; np.fill_diagonal(Rm, 0)
    for _ in range(20000): Bm = gate_step(Bm, Rm)
    return Bm, nodes
syn = {}
for n in range(3, 9):
    k = n - 1; Bm, nodes = ideal_clique(n); p = patterns(Bm, nodes)
    lam_k = a * c / (c + dt * (k * eta - gam * c) + eps)
    syn[f'K{n}'] = dict(k=k, nonadditivity=p['nonadditivity'], formula_nonadditivity=1 / math.sqrt(2 * k * (k - 1)),
                        odd_defect=p['odd_defect'], formula_odd_defect=math.sqrt(2 / (k + 1)),
                        abs_diff_nonadditivity=abs(p['nonadditivity'] - 1 / math.sqrt(2 * k * (k - 1))), abs_diff_odd_defect=abs(p['odd_defect'] - math.sqrt(2 / (k + 1))))
    if n == 3:
        syn['K3']['rays'] = [dict(plus_lam_over_lam_k=q['plus_lam'] / lam_k, plus_rel_residual=q['plus_rel_residual'], minus_lam_over_lam_k=q['minus_lam'] / lam_k) for q in p['K3_rays']]
# K4 with equal row sums but unequal edges: weights by perfect matching {01,23}=w1, {02,13}=w2, {03,12}=w3 (row sum w1+w2+w3)
w = np.zeros((4, 4)); w1, w2, w3 = 0.30, 0.20, 0.10
for (i, j), v in {(0, 1): w1, (2, 3): w1, (0, 2): w2, (1, 3): w2, (0, 3): w3, (1, 2): w3}.items(): w[i, j] = v
Bm = np.zeros((12, 12)); nodes = [0, 1, 2, 3]
for i in range(4):
    for j in range(i + 1, 4): Bm[i, j] = Bm[j, i] = w[i, j] * c / (w1 + w2 + w3)
pu = patterns(Bm, nodes)
syn['K4_unequal_edges_equal_row_sums'] = dict(edge_weights_relative=[w1, w2, w3], nonadditivity=pu['nonadditivity'], odd_defect=pu['odd_defect'],
    formula_nonadditivity=1 / math.sqrt(12), formula_odd_defect=math.sqrt(0.5),
    note='single step from a non-fixed-point tied state; shows the closed-form ratios assume equal edge weights')
out['tie_patterns_synthetic'] = syn
SM = json.load(open(inp('kappa_cycle_kernel_summary.json')))['tie_nonadditivity_all_tied_resolved']
obs = {}
for t, v in SM.items():
    k = int(t[1:]) - 1; fn, fo = 1 / math.sqrt(2 * k * (k - 1)), math.sqrt(2 / (k + 1))
    obs[t] = dict(n=v['n'], formula_nonadditivity=fn, formula_odd_defect=fo,
                  max_rel_dev_nonadditivity=max(abs(v['min_rel_nonadditivity'] - fn), abs(v['max_rel_nonadditivity'] - fn)) / fn,
                  max_rel_dev_odd_defect=max(abs(v['min_rel_odd_defect'] - fo), abs(v['max_rel_odd_defect'] - fo)) / fo)
out['tie_patterns_observed_vs_derived'] = dict(source='results/kappa_cycle_kernel_summary.json: tie_nonadditivity_all_tied_resolved', by_type=obs)
print(json.dumps(out, indent=1, default=float)); dump('rate_law_census_r4.json', out)
