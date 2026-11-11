#!/usr/bin/env python3
"""PROPOSAL (round 4 audit, 2026-10-25). Corrected replacement for aief_1_4_augmented_spectrum.py (the original is NOT edited).
Run from the AIEFS repo root:  python "AI Agent Audits/evidence/proposals/aief_1_4_full_state_spectrum.py"

Why the original 18-coordinate result is quarantined (AIEFS_audit_response_3.md section 8):
  * restore_state() restores B, coherence_acc and history but NOT theta. After the baseline step, state.theta is the
    post-step theta, so every perturbed column starts from a different (advanced) theta than the baseline; the
    Jacobian columns are differences between steps from two different states.
  * The 18 coordinates (oldest history entry of 3 nodes, 3 K3 edge weights, 6 directed EMA entries) are not a closed
    state: the step map also reads theta (= history[-1]), the other 50 history entries (one of which becomes the next
    delayed phase), all other edges and all other EMA entries. The docstring's claim that theta "is derived from the
    phase_factor" is not what the code does: advance_base_state() sets theta = theta_new and appends it to history,
    so theta == history[-1] always.

What this script does instead (same production step functions, base_intermediates + advance_base_state):
  * closed state z = (history[0..50] (51 x 12 = 612; history[-1] is theta), B upper triangle (66),
    Re/Im coherence_acc (2 x 144 = 288)) = 966 coordinates; theta is restored as history[-1] on every unpack.
  * replays the same split state (run 5a9f093a2fe0, seed 4619122171158768524) for protocol.future_steps steps,
    exactly as the original;
  * one-step Jacobian by central differences (phase outputs differenced on the circle), plus the two one-sided
    Jacobians J+ and J- (the gate min() and max(.,0) are nonsmooth at ties/zeros);
  * a T-step finite-time map Phi_T (central differences through T production steps) for T = 500 (5 time units).
  * NOTE on J+ / J-: they are assembled column by column, so each column may sit on a different branch of the
    piecewise-smooth gate; their eigenvalues are NOT the spectrum of any single branch and are reported only as a
    nonsmoothness diagnostic (max |J+ - J-| by input block).
  * reports the rates r = -log|lambda|/dt (one-step) and -log|lambda|/(T dt) (finite-time), the count of rates inside
    the original script's gap window (1.01 r_EMA, 0.689918), the slow modes' block weights, and per-node frequency
    locking over the last 500 steps (a non-locked node makes the one-step spectrum a snapshot, not an invariant).
Evidence class: single replay, single state, finite-difference, finite-time diagnostic. Not a proof of anything."""
from __future__ import annotations
import json, math, os, sys, hashlib
from collections import deque
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.getcwd())
import AIEF_1_4_stationarity_perturbation_analysis_updated as base
import AIEF_1_4_augmented_tangent_cocycle_analysis as aug

RUN = "5a9f093a2fe0"; SEED = "4619122171158768524"
NPZ = f"runs/{RUN}/AIEF_1_4_{RUN}_branch_diagnostics.npz"; MAN = f"runs/{RUN}/manifest.json"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
EPS_SC = 1e-12; H = 1e-7; T_FT = 500; MU_PHASE_REF = 0.689918
model = json.load(open(MAN))["model"]; prot = json.load(open(MAN))["protocol"]
N = int(model["N"]); dt = float(model["dt"]); caps = np.full(N, (model["a"] - model["delta"]) / model["q"])
A, edges = base.incidence_matrix(N); iu = np.triu_indices(N, 1)
alpha = math.exp(-dt / float(model["T_window"])); r_ema = -math.log(alpha) / dt
L = None  # history length, set after load
def step(st):
    aug.advance_base_state(st, aug.base_intermediates(st, model, caps, A, edges, EPS_SC))
def pack(st):
    h = np.array(st.history); return np.concatenate([h.ravel(), st.B[iu], st.coherence_acc.real.ravel(), st.coherence_acc.imag.ravel()])
def unpack(z):
    nh = L * N; h = z[:nh].reshape(L, N); B = np.zeros((N, N)); B[iu] = z[nh:nh + len(iu[0])]; B = B + B.T
    o = nh + len(iu[0]); C = z[o:o + N * N].reshape(N, N) + 1j * z[o + N * N:o + 2 * N * N].reshape(N, N)
    return base.DynamicState(theta=h[-1].copy(), B=B, coherence_acc=C, history=deque((r.copy() for r in h), maxlen=L))
def diff(zp, zm, den):
    d = (zp - zm) / den; nh = L * N
    d[:nh] = np.angle(np.exp(1j * (zp[:nh] - zm[:nh]))) / den  # phases live on the circle
    return d
def advance(z, T):
    st = unpack(z)
    for _ in range(T): step(st)
    return pack(st)
Z0 = None
def column(args):
    j, T, mode = args
    e = np.zeros_like(Z0); e[j] = H
    if mode == "c": return diff(advance(Z0 + e, T), advance(Z0 - e, T), 2 * H)
    base_out = advance(Z0, T)
    return diff(advance(Z0 + e, T), base_out, H) if mode == "+" else diff(base_out, advance(Z0 - e, T), H)
def jac(T, mode, pool):
    return np.array(pool.map(column, [(j, T, mode) for j in range(len(Z0))], chunksize=8)).T
def blocks(v):
    nh = L * N; nb = len(iu[0]); w = np.abs(v) ** 2; s = w.sum()
    return dict(history=float(w[:nh].sum() / s), B=float(w[nh:nh + nb].sum() / s), C=float(w[nh + nb:].sum() / s))
def spectrum(J, Tsteps):
    ev, V = np.linalg.eig(J); ab = np.abs(ev); rate = -np.log(np.maximum(ab, 1e-300)) / (dt * Tsteps)
    o = np.argsort(rate); ev, V, ab, rate = ev[o], V[:, o], ab[o], rate[o]
    lo, hi = 1.01 * r_ema, MU_PHASE_REF
    ing = (rate > lo) & (rate < hi); near = (rate >= 0.99 * r_ema) & (rate <= 1.01 * r_ema); slower = rate < 0.99 * r_ema
    slow = []
    for i in np.where(rate < hi)[0][:60]:
        b = blocks(V[:, i]); slow.append(dict(rate=float(rate[i]), abs=float(ab[i]), re=float(ev[i].real), im=float(ev[i].imag),
                                              in_gap=bool(ing[i]), near_ema=bool(near[i]), **{f"w_{k}": round(x, 6) for k, x in b.items()}))
    def row(i):
        b = blocks(V[:, i]); return dict(rate=float(rate[i]), abs=float(ab[i]), re=float(ev[i].real), im=float(ev[i].imag), **{f"w_{k}": round(x, 6) for k, x in b.items()})
    return dict(in_gap_modes=[row(i) for i in np.where(ing)[0]], slower_than_ema_modes=[row(i) for i in np.where(slower)[0]],
                ema_cluster_rate_range=[float(rate[near].min()), float(rate[near].max())] if near.any() else None, dim=len(ev), n_rate_below_0p99_r_ema=int(slower.sum()), n_near_ema_1pct=int(near.sum()), n_in_gap=int(ing.sum()),
                n_rate_ge_mu_phase=int((rate >= hi).sum()), gap_window=[lo, hi], slowest_60_below_mu_phase=slow)
def main():
    global Z0, L
    os.makedirs(OUT, exist_ok=True)
    with np.load(NPZ, allow_pickle=False) as d: st = base.load_split_state(d, SEED)
    L = st.history.maxlen
    fs = int(prot["future_steps"]); unw = []
    for k in range(fs):
        step(st)
        if k >= fs - 501: unw.append(st.theta.copy())
    U = np.unwrap(np.array(unw), axis=0); freq = (U[-1] - U[0]) / (500 * dt)
    assert np.array_equal(st.theta, st.history[-1]), "theta != history[-1]"
    Z0 = pack(st)
    # rotation symmetry check: a common phase shift of the whole history must commute with the step
    sh = Z0.copy(); sh[:L * N] += 0.3; rot_err = float(np.max(np.abs(diff(advance(sh, 1), advance(Z0, 1), 1.0)[:L * N] - 0.3)))
    rot_err_other = float(np.max(np.abs((advance(sh, 1) - advance(Z0, 1))[L * N:])))
    res = dict(run=RUN, seed=SEED, closed_state_dim=len(Z0), history_len=L, h=H, r_ema=r_ema, alpha=alpha, mu_phase_ref=MU_PHASE_REF,
               replay_steps=fs, theta_equals_history_last=True,
               rotation_symmetry_check=dict(max_phase_err=rot_err, max_nonphase_change=rot_err_other),
               node_mean_frequency_last_500_steps=[float(f) for f in freq],
               frequency_spread_all_nodes=float(freq.max() - freq.min()),
               frequency_spread_K3_2_7_11=float(np.ptp(freq[[2, 7, 11]])))
    with Pool(7) as pool:
        Jc = jac(1, "c", pool); Jp = jac(1, "+", pool); Jm = jac(1, "-", pool)
        res["one_step_central"] = spectrum(Jc, 1); res["one_step_plus"] = spectrum(Jp, 1); res["one_step_minus"] = spectrum(Jm, 1)
        res["one_sided_max_abs_diff"] = float(np.max(np.abs(Jp - Jm)))
        nh = L * N; nb = len(iu[0]); R = np.abs(Jp - Jm)
        res["one_sided_max_abs_diff_by_input_block"] = dict(history=float(R[:, :nh].max()), B=float(R[:, nh:nh + nb].max()), C=float(R[:, nh + nb:].max()))
        PhiT = jac(T_FT, "c", pool); res[f"finite_time_T{T_FT}_central"] = spectrum(PhiT, T_FT)
    np.save(os.path.join(OUT, "full_state_J_one_step_central.npy"), Jc)
    res["sha256_J_one_step_central_npy"] = hashlib.sha256(open(os.path.join(OUT, "full_state_J_one_step_central.npy"), "rb").read()).hexdigest()
    os.remove(os.path.join(OUT, "full_state_J_one_step_central.npy"))  # 7 MB; hash kept for reproducibility, file not kept
    c1, ft = res["one_step_central"], res[f"finite_time_T{T_FT}_central"]
    res["verdict"] = ("EMA pole is the unique slow pole of the full closed state: "
                      + ("YES" if c1["n_in_gap"] == 0 and c1["n_rate_below_0p99_r_ema"] == 0 and ft["n_in_gap"] == 0 else "NO")
                      + f" (one-step: {c1['n_in_gap']} rates in gap, {c1['n_rate_below_0p99_r_ema']} slower than EMA; "
                      + f"T={T_FT}: {ft['n_in_gap']} in gap, {ft['n_rate_below_0p99_r_ema']} slower than EMA)")
    json.dump(res, open(os.path.join(OUT, "full_state_spectrum.json"), "w"), indent=1)
    for k in ["closed_state_dim", "rotation_symmetry_check", "frequency_spread_all_nodes", "frequency_spread_K3_2_7_11", "one_sided_max_abs_diff", "one_sided_max_abs_diff_by_input_block", "verdict"]:
        print(k, res[k])
    for name in ["one_step_central", "one_step_plus", "one_step_minus", f"finite_time_T{T_FT}_central"]:
        s = res[name]; print(name, {k: s[k] for k in ["n_rate_below_0p99_r_ema", "n_near_ema_1pct", "n_in_gap", "n_rate_ge_mu_phase"]})
        for m in s["slowest_60_below_mu_phase"][:25]: print("   ", m)
if __name__ == "__main__":
    main()
