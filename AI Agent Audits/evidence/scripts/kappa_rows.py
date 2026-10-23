"""Reproduces the salvage-report row check (gamma + sum_j F_ij / c on rows 2,7,11 of the exceptional seed) and the
closed-form kappa numbers, and compares with the repo's scalar_spectral_gap_report.txt values. [inputs: runs/5a9f093a2fe0]"""
import sys, os, re, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); from _common import *
eta, mu, gam, dt = 0.04, 0.03, 0.015, 0.01; c = 0.95 / 1.5
om = np.array([1.00, 1.02, 1.50, 2.00, 2.01, 1.01, 1.03, 1.51, 2.02, 2.00, 1.00, 1.04]); Tw = 25 / om.mean(); al = np.exp(-dt / Tw)
d = np.load('runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz'); s = '4619122171158768524'
B = d[f'continue_seed_{s}_B_final']; R = d[f'continue_seed_{s}_R_physical_future']
rows = {}
for i in [2, 7, 11]:
    F = (eta + mu) * R[i] - mu; F[i] = 0; F[B[i] <= 1e-9] = 0
    # row drift of saturated row i is sum_j(F_ij - gam*B_ij) = sum F - gam*c; cap renormalisation adds rate drift/c,
    # so a row-sum-preserving perturbation decays at gam + (sumF - gam*c)/c = sumF/c  (= k*eta/c when R=1 on k edges)
    rows[i] = dict(sumF_over_c=float(F.sum() / c), gam_plus_sumF_over_c_WRONG_extra_gamma=float(gam + F.sum() / c))
x = 2 * eta / (c * (1 - gam * dt))
out = dict(T_w=Tw, alpha=al, two_eta_over_c=2 * eta / c, r_g=1 / Tw, kappa_cont=2 * eta / c - 1 / Tw,
           rB_discrete_R1=float(np.log(1 + dt * x) / dt), kappa_discrete_R1=float(np.log(1 + dt * x) / dt + np.log(al) / dt), row_rates=rows,
           repo=dict(observed_kappa_t320=0.0691225, rB_fit=0.127056, rg_fit=0.0571331, predicted_gap=0.0699224))
out['rel_err_cont_vs_obs'] = (out['kappa_cont'] - 0.0691225) / 0.0691225
out['repo_rB_minus_2eta_over_c'] = 0.127056 - 2 * eta / c
txt = open('aief_1_4_scalar_spectral_gap_reduction/scalar_spectral_gap_report.txt').read()
out['repo_report_lines_with_kappa'] = [l for l in txt.splitlines() if re.search(r'kappa|r_B|rB|gap', l, re.I)][:40]
for k, v in out.items(): print(k, v)
dump('kappa_rows.json', out)
