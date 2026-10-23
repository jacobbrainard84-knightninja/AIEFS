"""NEW (response round). Point 9: test kappa(T_w) = k*eta/c - 1/T_w across the five S01 T_window values.
Inputs: S01 run runs/b57562a8ee77 (seed list + saved continue-branch B_final, used to check replay fidelity).
For each (seed, rho): replay the repo engine exactly (AIEF_1_4_Twindow_sensitivity.create_model_config(rho),
engine.simulate_prefix, then the unperturbed 'continue' dynamics via engine.advance_state) to future time
t_target=250 (the repo's kappa target time). At that state, for every connected component of supp(B) with >=3 nodes:
  (a) frozen-driver one-step Jacobian J of the B update+gate (R frozen at its current value), central differences;
      r_B = -log(max|eig J|)/dt  (exact discrete selected-channel rate, the collaborator's -log|lambda_B|/dt);
  (b) full nonlinear twin run: perturb B along the slowest eigenvector (eps=1e-6), run both copies 40 time units,
      fit log|projection| slope on [1,8] (early, intrinsic pole) and [25,40] (late);
  (c) kappa_exact = r_B - r_g with r_g = -log(alpha)/dt (EMA pole, exact by construction), vs kappa_formula = k*eta/c - 1/T_w,
      where k = component max degree... reported with the component's degree sequence and saturation.
Also checks replay fidelity: replayed B at t=320 (end) vs saved continue B_final.
Usage: python <bundle>/scripts/kappa_tw.py [--seeds all|exceptional]"""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); from _common import *
import aief_experiment_engine_v1 as engine
import AIEF_1_4_Twindow_sensitivity as tw
from multiprocessing import Pool
RUN = 'runs/b57562a8ee77'; NPZ = f'{RUN}/AIEF_1_4_Twindow_sensitivity_b57562a8ee77_branch_diagnostics.npz'
RHOS = [0.5, 0.75, 1.0, 1.5, 2.0]; EXC = 4619122171158768524
T_TARGET = 250.0; TWIN_T = 40.0; EPS = 1e-6
def components(B, tol=1e-9):
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
def bmap(B, R, cfg):
    Bu = B + cfg.dt * ((cfg.eta + cfg.mu) * R - cfg.mu - cfg.gamma * B)
    Bu = np.maximum(Bu, 0.0); Bu = 0.5 * (Bu + Bu.T); np.fill_diagonal(Bu, 0.0)
    rs = Bu.sum(1)
    if np.min(cfg.a - cfg.q * rs) < cfg.delta:
        s = np.minimum(1.0, cfg.capacity / (rs + cfg.scale_epsilon)); Bu = Bu * np.minimum.outer(s, s); np.fill_diagonal(Bu, 0.0)
    return Bu
def job(a):
    seed, rho = a
    cfg = tw.create_model_config(rho); prot = tw.create_protocol_config()
    st, prefix = engine.simulate_prefix(seed, cfg, prot)
    rng = np.random.default_rng(0)
    n_target = int(round(T_TARGET / cfg.dt)); n_fut = prot.future_steps(cfg)
    for _ in range(n_target): engine.advance_state(st, cfg, rng)
    S0 = st.clone()
    tmp = st.clone(); R0 = engine.compute_R(tmp, cfg)   # R that the next B update would see
    out = dict(seed=int(seed), rho=rho, T_w=cfg.T_window, alpha=cfg.alpha, r_g=-np.log(cfg.alpha) / cfg.dt, comps=[])
    rowsum = S0.B.sum(1)
    for comp in components(S0.B):
        ed = [(i, j) for ii, i in enumerate(comp) for j in comp[ii + 1:] if S0.B[i, j] > 1e-9]
        m = len(ed); J = np.zeros((m, m)); h = 1e-7
        for c, (i, j) in enumerate(ed):
            P = S0.B.copy(); M = S0.B.copy(); P[i, j] += h; P[j, i] += h; M[i, j] -= h; M[j, i] -= h
            d = (bmap(P, R0, cfg) - bmap(M, R0, cfg)) / (2 * h)
            J[:, c] = [d[p, q] for p, q in ed]
        ev, V = np.linalg.eig(J); o = np.argsort(-np.abs(ev)); ev = ev[o]; V = V[:, o]
        lam = float(np.abs(ev[0])); u = np.real(V[:, 0]); u /= np.linalg.norm(u)
        rB = float(-np.log(lam) / cfg.dt)
        deg = [int(sum(S0.B[i, j] > 1e-9 for j in range(12) if j != i)) for i in comp]
        sat = [float(cfg.capacity - rowsum[i]) for i in comp]
        Rmin = float(min(R0[p, q] for p, q in ed))
        # twin run in the full nonlinear dynamics
        A_ = S0.clone(); Bp = S0.clone()
        for c, (i, j) in enumerate(ed): Bp.B[i, j] += EPS * u[c]; Bp.B[j, i] += EPS * u[c]
        ra = np.random.default_rng(0); rb = np.random.default_rng(0)
        proj = []
        for n in range(int(round(TWIN_T / cfg.dt))):
            engine.advance_state(A_, cfg, ra); engine.advance_state(Bp, cfg, rb)
            if n % 10 == 9: proj.append(float(sum(u[c] * (Bp.B[i, j] - A_.B[i, j]) for c, (i, j) in enumerate(ed))))
        t = (np.arange(len(proj)) + 1) * 0.1; y = np.log(np.abs(np.array(proj)) + 1e-300)
        def slope(t0, t1):
            k = (t >= t0) & (t <= t1); return float(-np.polyfit(t[k], y[k], 1)[0])
        k_formula = max(deg) * cfg.eta / cfg.capacity
        out['comps'].append(dict(nodes=comp, n_edges=m, degrees=deg, rowsum_margin=sat, R_min_on_edges=Rmin,
                                 eigs_abs=[float(x) for x in np.abs(ev)], r_B_frozen=rB, kdeg_eta_over_c=k_formula,
                                 twin_rate_early_1_8=slope(1, 8), twin_rate_late_25_40=slope(25, 40),
                                 twin_amp_ratio_end=float(abs(proj[-1]) / EPS),
                                 kappa_exact_frozen=rB - out['r_g'], kappa_formula=k_formula - 1 / cfg.T_window,
                                 kappa_repo_formula_K3=0.1263 - 1 / cfg.T_window))
    for _ in range(n_fut - n_target): engine.advance_state(st, cfg, rng)
    saved = np.load(NPZ)[f'continue_seed_{seed}_rho_{rho}_B_final']
    out['replay_maxdiff_B_final'] = float(np.max(np.abs(st.B - saved)))
    return out
if __name__ == '__main__':
    import pandas as pd
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    seeds = sorted(set(pd.read_csv(f'{RUN}/twindow_condition_status.csv')['seed'].astype(np.uint64).tolist()))
    if mode == 'exceptional': seeds = [EXC]
    jobs = [(int(s), r) for s in seeds for r in RHOS]
    with Pool(7) as p: res = p.map(job, jobs)
    dump(f'kappa_tw_{mode}.json', res)
    for r in res:
        if r['seed'] == EXC: print('EXC', r['rho'], 'Tw=%.3f' % r['T_w'], 'replay diff', r['replay_maxdiff_B_final'], [(c['nodes'], c['degrees'], round(c['r_B_frozen'], 6), round(c['twin_rate_early_1_8'], 5), round(c['kappa_exact_frozen'], 5), round(c['kappa_formula'], 5)) for c in r['comps']])
