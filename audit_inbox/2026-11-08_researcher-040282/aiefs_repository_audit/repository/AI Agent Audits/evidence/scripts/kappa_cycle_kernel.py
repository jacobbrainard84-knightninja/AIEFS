"""NEW (round 3, 2026-10-24). Response-2 point 2: replaces the central-difference 'Jacobian' of kappa_tw.py with a
restricted fiber multiplier measured on the controller/cycle kernel.

Why: the capacity gate B'_ij = x_ij * min(s_i, s_j), s_i = min(1, c/(q_i + eps)), q_i = row sum of the proposal x,
is not differentiable where endpoint scales tie (s_i == s_j); a central difference there averages one-sided slopes.
On a saturated complete clique all endpoint scales tie, so kappa_tw.py's 'Jacobian eigenvalue' is not a derivative.

What this script does, at the same replayed states as kappa_tw.py (S01 run runs/b57562a8ee77, every seed x 5 T_w,
repo engine replay to t=250), for every connected component of supp(B) with >= 3 nodes:
  1. one actual engine step's proposal x = B + dt*((eta+mu)R - mu - gamma*B) (R does not depend on B within a step),
     endpoint scales s, controller set J = nodes that win (or tie for) the endpoint minimum on some component edge;
  2. A_J = unsigned edge-node incidence restricted to the component's edges and the rows J; fiber K = ker A_J
     (for an all-tied complete clique J = all nodes and K = the cycle kernel of the unsigned incidence, dim m - n);
  3. for each basis vector h of K (plus one random combination): ||A_J h|| and ||A h||; perturb B by +-delta*h,
     run ONE actual engine step (aief_experiment_engine_v1.advance_state) on clones, and measure the response:
     multiplier lam = <dB', h>/<h, h>, the relative residual ||dB' - lam h||/||dB'|| (0 => h is mapped to a multiple of
     itself), the +/- asymmetry, and leakage outside the component;
  4. compares lam with (a) the state formula (1 - gamma dt) * s_J and (b) the closed form (repo Prop 8.3 form)
     lam_k = (1 - gamma dt) c / (c + dt (k eta - gamma c) + eps), k = node degree, i.e.
     r_{B,k} = -log(lam_k)/dt = (1/dt) log(1 + (dt k eta + eps)/(c (1 - gamma dt))), kappa_k = r_{B,k} - 1/T_w;
  5. tie diagnostics: for components with tied controllers, one-sided directional derivatives along single-edge
     directions h1, h2 (sharing a node) to show non-additivity D(h1+h2) != D(h1)+D(h2) and D(-h) != -D(h);
  6. 3-node complete components (K3): K = ker A_J is {0} when all three scales tie. For each node c, the one-sided
     direction v_c (+1 on the edge opposite c, -1 on the two edges at c) keeps the other two rows fixed; we measure the
     one-sided multiplier along +v_c and -v_c. A strict (untied) K3 with |J| = 2 has a two-sided 1-dim fiber.
Output: results/kappa_cycle_kernel.json (per component) and results/kappa_cycle_kernel_summary.json."""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); from _common import *
import aief_experiment_engine_v1 as engine
import AIEF_1_4_Twindow_sensitivity as tw
from multiprocessing import Pool
RUN = 'runs/b57562a8ee77'; RHOS = [0.5, 0.75, 1.0, 1.5, 2.0]; EXC = 4619122171158768524
T_TARGET = 250.0; DELTA = 1e-7; TIE_TOL = 1e-9; SUPP = 1e-9
# Near ties: at T_w >= 1.5x many endpoint scales are equal only to ~1e-12..2e-9 at t=250 (still converging). A first
# run with TIE_TOL=1e-12 and a fixed DELTA=1e-7 crossed those near ties (the perturbation moved s by ~1e-7 >> gap) and
# returned spurious multipliers (~1/3, 'kappa' ~ 110). Now: edges with gap <= TIE_TOL are treated as tied, and each
# component uses its own step delta_c = geometric mean of (largest tied gap, smallest untied gap), clipped to
# [1e-11, 1e-5], so that delta_c >> tied gaps and << untied gaps; the scale separation is recorded and checked.
D_MIN, D_MAX = 1e-11, 1e-5
def components(B, tol=SUPP):
    N = len(B); A = B > tol; seen = set(); out = []
    for i in range(N):
        if i in seen: continue
        st = [i]; comp = set()
        while st:
            u = st.pop()
            if u in comp: continue
            comp.add(u); st += [v for v in range(N) if A[u, v]]
        seen |= comp
        if len(comp) >= 3: out.append(sorted(comp))
    return out
def step_B(S, cfg, dB=None):
    """One actual engine step from a clone of S (optionally with symmetric B perturbation dB); returns new B."""
    T = S.clone()
    if dB is not None: T.B = T.B + dB
    engine.advance_state(T, cfg, np.random.default_rng(0))
    return T.B
def vec2mat(v, ed, N=12):
    M = np.zeros((N, N))
    for c, (i, j) in enumerate(ed): M[i, j] = M[j, i] = v[c]
    return M
def mat2vec(M, ed): return np.array([M[i, j] for i, j in ed])
def nullspace(A, rtol=1e-10):
    if A.shape[0] == 0: return np.eye(A.shape[1])
    u, sv, vt = np.linalg.svd(A); r = int((sv > rtol * max(1.0, sv.max())).sum()); return vt[r:].T
def job(a):
    seed, rho = a
    cfg = tw.create_model_config(rho); prot = tw.create_protocol_config()
    st, _ = engine.simulate_prefix(seed, cfg, prot); rng = np.random.default_rng(0)
    for _ in range(int(round(T_TARGET / cfg.dt))): engine.advance_state(st, cfg, rng)
    S0 = st.clone(); R0 = engine.compute_R(S0.clone(), cfg)
    c, dt, eta, mu, gam, eps = cfg.capacity, cfg.dt, cfg.eta, cfg.mu, cfg.gamma, cfg.scale_epsilon
    x = S0.B + dt * ((eta + mu) * R0 - mu - gam * S0.B); x = np.maximum(x, 0); x = 0.5 * (x + x.T); np.fill_diagonal(x, 0)
    q = x.sum(1); gate_on = bool(np.min(cfg.a - cfg.q * q) < cfg.delta); s = np.minimum(1.0, c / (q + eps)) if gate_on else np.ones(12)
    base = step_B(S0, cfg)
    out = dict(seed=int(seed), rho=rho, T_w=cfg.T_window, r_g=-np.log(cfg.alpha) / dt, gate_on=gate_on, comps=[])
    vrng = np.random.default_rng(seed % (2**32))
    for comp in components(S0.B):
        ed = [(i, j) for ii, i in enumerate(comp) for j in comp[ii + 1:] if S0.B[i, j] > SUPP]; m = len(ed)
        deg = [int(sum(S0.B[i, j] > SUPP for j in range(12) if j != i)) for i in comp]; k = max(deg)
        complete = m == len(comp) * (len(comp) - 1) // 2
        A = np.zeros((len(comp), m))
        for e, (i, j) in enumerate(ed): A[comp.index(i), e] = A[comp.index(j), e] = 1
        J = set(); ties = 0; gt = [0.0]; gu = []
        for (i, j) in ed:
            g = abs(s[i] - s[j])
            if g <= TIE_TOL: J |= {i, j}; ties += 1; gt.append(g)
            else: J.add(i if s[i] < s[j] else j); gu.append(g)
        gt_max = max(gt); gu_min = min(gu) if gu else None
        if gu_min is None: dl = D_MAX
        else: dl = float(np.clip(np.sqrt(max(gt_max, 1e-16) * gu_min) if ties else gu_min / 100, D_MIN, min(D_MAX, gu_min / 100)))
        sep_lo = dl / gt_max if ties and gt_max > 0 else None; sep_hi = gu_min / dl if gu_min else None
        J = sorted(J); AJ = A[[comp.index(i) for i in J]]
        K = nullspace(AJ); kdim = K.shape[1]
        lam_cf = (1 - gam * dt) * c / (c + dt * (k * eta - gam * c) + eps)
        sJ = [float(s[i]) for i in J]; lam_state = (1 - gam * dt) * float(np.mean(sJ))
        rec = dict(nodes=comp, n_nodes=len(comp), n_edges=m, degrees=deg, k=k, complete=complete, J=J, n_tied_edges=ties,
                   s_spread_comp=float(max(s[comp]) - min(s[comp])), s_spread_J=float(max(sJ) - min(sJ)),
                   rowsum_margin=[float(c - S0.B[i].sum()) for i in comp], R_min=float(min(R0[i, j] for i, j in ed)),
                   delta=dl, max_tied_gap=gt_max, min_untied_gap=gu_min, delta_over_tied_gap=sep_lo, untied_gap_over_delta=sep_hi,
                   kernel_dim=kdim, expected_cycle_kernel_dim=(m - len(comp)) if complete and len(comp) >= 3 else None,
                   lam_closed_form=lam_cf, lam_state_formula=lam_state, r_closed_form=-np.log(lam_cf) / dt,
                   kappa_closed_form=-np.log(lam_cf) / dt - out['r_g'], fiber=[])
        dirs = [K[:, b] for b in range(kdim)]
        if kdim > 1: w = vrng.normal(size=kdim); dirs.append(K @ (w / np.linalg.norm(w)))
        for h in dirs:
            h = h / np.linalg.norm(h); H = vec2mat(h, ed)
            dp = (step_B(S0, cfg, dl * H) - base) / dl; dm = (step_B(S0, cfg, -dl * H) - base) / -dl
            vp = mat2vec(dp, ed); lam = float(vp @ h)
            mask = np.ones((12, 12), bool)
            for i, j in ed: mask[i, j] = mask[j, i] = False
            rec['fiber'].append(dict(AJh=float(np.linalg.norm(AJ @ h)), Ah=float(np.linalg.norm(A @ h)), lam=lam,
                                     rel_residual=float(np.linalg.norm(vp - lam * h) / np.linalg.norm(vp)),
                                     pm_asym=float(np.linalg.norm(dp - dm) / np.linalg.norm(dp)), leak=float(np.abs(dp[mask]).max())))
        if rec['fiber']:
            L = np.array([f['lam'] for f in rec['fiber']])
            rec['lam_fiber_mean'] = float(L.mean()); rec['lam_fiber_spread'] = float(L.max() - L.min())
            rec['r_fiber'] = float(-np.log(L.mean()) / dt); rec['kappa_fiber'] = rec['r_fiber'] - out['r_g']
            rec['rel_err_lam_vs_closed_form'] = float(abs(L.mean() - lam_cf) / lam_cf)
            rec['rel_err_lam_vs_state'] = float(abs(L.mean() - lam_state) / lam_state)
            rec['rel_err_r_vs_closed_form'] = float(abs(rec['r_fiber'] - rec['r_closed_form']) / rec['r_closed_form'])
        if ties and m >= 2:   # non-additivity of one-sided directional derivatives at the tie
            e1 = 0; e2 = next(e for e in range(1, m) if set(ed[e]) & set(ed[0]))
            def D(v): return mat2vec((step_B(S0, cfg, dl * vec2mat(v, ed)) - base) / dl, ed)
            h1 = np.eye(m)[e1]; h2 = np.eye(m)[e2]
            D1, D2, D12 = D(h1), D(h2), D(h1 + h2); Dm1 = D(-h1)
            rec['tie_nonadditivity'] = dict(edges=[list(ed[e1]), list(ed[e2])],
                rel_nonadditivity=float(np.linalg.norm(D12 - D1 - D2) / np.linalg.norm(D1 + D2)),
                rel_odd_defect=float(np.linalg.norm(D1 + Dm1) / np.linalg.norm(D1)))
        if len(comp) == 3 and complete:
            onesided = []
            for cn in comp:
                v = np.array([-1.0 if cn in e else 1.0 for e in ed]); v /= np.linalg.norm(v)
                r_ = {}
                for sg in [1, -1]:
                    dv = mat2vec((step_B(S0, cfg, sg * dl * vec2mat(v, ed)) - base) / (sg * dl), ed)
                    lam = float(dv @ v); r_['plus' if sg > 0 else 'minus'] = dict(lam=lam, rel_residual=float(np.linalg.norm(dv - lam * v) / np.linalg.norm(dv)))
                onesided.append(dict(node=cn, **r_))
            rec['K3_one_sided'] = onesided
        out['comps'].append(rec)
    return out
if __name__ == '__main__':
    import pandas as pd
    seeds = sorted(set(pd.read_csv(f'{RUN}/twindow_condition_status.csv')['seed'].astype(np.uint64).tolist()))
    if len(sys.argv) > 1 and sys.argv[1] == 'exceptional': seeds = [EXC]
    jobs = [(int(s), r) for s in seeds for r in RHOS]
    with Pool(7) as p: res = p.map(job, jobs)
    def rnd(o):  # 10 significant digits keeps the file < 1 MB; relative errors are stored as their own fields
        if isinstance(o, float): return float(f'{o:.10g}')
        if isinstance(o, dict): return {k: rnd(v) for k, v in o.items()}
        if isinstance(o, list): return [rnd(v) for v in o]
        return o
    res = rnd(res)
    dump('kappa_cycle_kernel.json', indent=None, obj=dict(delta_default=DELTA, delta_range=[D_MIN, D_MAX], tie_tol=TIE_TOL, support_tol=SUPP, replays=res))
    print('replays', len(res))
