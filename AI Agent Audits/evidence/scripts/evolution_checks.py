"""NEW (round 3, 2026-10-24). Response-2 point 9 (optional evolution checks) on the repo's aief_1_4_augmented_spectrum.py.
Uses the repo's OWN functions (snapshot_state, restore_state, extract/inject_fundamental_vars, base_intermediates,
advance_base_state) at its defaults (run 5a9f093a2fe0, seed 4619122171158768524, perturbation 1e-8), and checks:
  1. theta restoration: restore_state() restores B, coherence_acc and history but not theta, while advance_base_state()
     replaces theta; so each Jacobian column starts from a different theta. We record the theta drift per column.
  2. column-order dependence: the repo procedure run in forward vs reversed column order.
  3. a corrected procedure (full clone incl. theta restored for every column) for comparison.
  4. non-closure of the 18-vector: perturbing state outside it (history[1] at the K3 nodes, or theta) changes the next
     18-vector, so the 18x18 matrix is not the Jacobian of a closed map on those coordinates.
Eigenvalue rates -log|lambda|/dt are reported for each matrix; the repo's gap window is (1.01 r_ema, 0.689918)."""
import sys, os, json, math, copy, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); from _common import *
import aief_1_4_augmented_spectrum as S
base, ca, aug = S.load_production_modules()
M = json.load(open(S.DEFAULT_MANIFEST)); model = M['model']; dt = float(model['dt'])
r_ema = -math.log(math.exp(-dt / float(model['T_window']))) / dt
cap = (float(model['a']) - float(model['delta'])) / float(model['q']); N = int(model['N'])
caps = np.full(N, cap); A, E = base.incidence_matrix(N); fs = int(M['protocol']['future_steps']); eps = S.DEFAULT_SCALE_EPSILON
pert = S.DEFAULT_PERTURBATION
with np.load(S.DEFAULT_NPZ, allow_pickle=False) as d: st = base.load_split_state(d, S.DEFAULT_SEED)
step = lambda s: aug.advance_base_state(s, aug.base_intermediates(s, model, caps, A, E, eps))
for _ in range(fs): step(st)
S0 = copy.deepcopy(st)                       # full state at step fs, incl. theta
def repo_procedure(order):
    s = copy.deepcopy(S0); snap = S.snapshot_state(s); step(s); after = S.extract_fundamental_vars(s)
    Jm = np.zeros((18, 18)); drift = []
    for col in order:
        S.restore_state(s, snap); drift.append(float(np.abs(np.angle(np.exp(1j * (s.theta - S0.theta)))).max()))
        v = S.extract_fundamental_vars(s); dl = pert * max(1.0, abs(v[col])); v[col] += dl
        S.inject_fundamental_vars(s, v); step(s); Jm[:, col] = (S.extract_fundamental_vars(s) - after) / dl
    return Jm, drift
def fixed_procedure():
    s = copy.deepcopy(S0); step(s); after = S.extract_fundamental_vars(s); Jm = np.zeros((18, 18))
    for col in range(18):
        s = copy.deepcopy(S0); v = S.extract_fundamental_vars(s); dl = pert * max(1.0, abs(v[col])); v[col] += dl
        S.inject_fundamental_vars(s, v); step(s); Jm[:, col] = (S.extract_fundamental_vars(s) - after) / dl
    return Jm, after
def rates(Jm):
    ev = np.linalg.eigvals(Jm); r = -np.log(np.maximum(np.abs(ev), 1e-300)) / dt
    gap = sorted(float(x) for x in r if 1.01 * r_ema < x < 0.689918)
    return dict(slowest_rates=sorted(float(x) for x in r)[:6], rates_in_repo_gap_window=gap)
Jf, drift_f = repo_procedure(list(range(18))); Jr, drift_r = repo_procedure(list(range(17, -1, -1))); Jx, after = fixed_procedure()
out = dict(defaults=dict(run=S.DEFAULT_RUN_HASH, seed=S.DEFAULT_SEED, perturbation=pert, future_steps=fs, r_ema=r_ema),
  theta_restoration=dict(restore_state_restores_theta=False, max_theta_drift_at_column_start_forward=max(drift_f),
                         theta_drift_first_columns=drift_f[:3]),
  column_order=dict(max_abs_diff_forward_vs_reversed=float(np.abs(Jf - Jr).max()), max_abs_entry=float(np.abs(Jf).max())),
  vs_corrected=dict(max_abs_diff_repo_vs_corrected=float(np.abs(Jf - Jx).max())),
  spectra=dict(repo_forward=rates(Jf), repo_reversed=rates(Jr), corrected=rates(Jx)))
nc = {}
for name, fn in [('history[1] at K3 nodes', lambda s: s.history.__setitem__(1, s.history[1] + np.isin(np.arange(N), S.K3_NODES) * 1e-8)),
                 ('theta at K3 nodes', lambda s: setattr(s, 'theta', s.theta + np.isin(np.arange(N), S.K3_NODES) * 1e-8))]:
    s = copy.deepcopy(S0); fn(s); step(s)
    nc[name] = dict(perturbation=1e-8,
                    max_abs_change_in_next_18_vector_over_delta=float(np.abs(S.extract_fundamental_vars(s) - after).max() / 1e-8))
out['nonclosure'] = nc
# sanity: perturbations above do not change the 18-vector itself at the start
s = copy.deepcopy(S0); v0 = S.extract_fundamental_vars(s); s.history[1] = s.history[1] + 1e-8; s.theta = s.theta + 1e-8
out['nonclosure']['check_start_18_vector_unchanged'] = bool(np.array_equal(v0, S.extract_fundamental_vars(s)))
print(json.dumps(out, indent=1))
dump('evolution_checks.json', out)
