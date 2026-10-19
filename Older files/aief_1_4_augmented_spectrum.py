#!/usr/bin/env python3

"""
AIEF-1.4 Augmented Spectral Audit

Tests: Does the full augmented phase–history–weight–EMA linearization
      have any eigenvalue between r_EMA (0.057) and mu_phase (0.690)?

Method: At the final time step of the frozen replay, perturb each K3 state
variable by a small finite difference and measure the one-step response
of the production code.  The resulting matrix is the discrete-time
augmented Jacobian.

State variables (K3 subgraph only):
  theta_i     (i=2,7,11)              — reconstructed from history
  h_old_i     (i=2,7,11)              — oldest deque entry
  B_e         (e=25,29,59)            — undirected edge weights
  C_dir       (directed edges)        — EMA coherence, real+imag parts

If no eigenvalue lies in [0.057, 0.690] in continuous-time rate terms
(equivalently, no discrete eigenvalue between exp(-0.690*dt) and
exp(-0.057*dt) = [0.9931, 0.9994]), then alpha is the unique slow pole.

Evidence class: diagnostic mechanism exploration.
"""

from __future__ import annotations

import argparse, hashlib, json, math, os, sys, tempfile, copy
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

DEFAULT_RUN_HASH = "5a9f093a2fe0"
DEFAULT_NPZ = f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_branch_diagnostics.npz"
DEFAULT_MANIFEST = f"runs/{DEFAULT_RUN_HASH}/manifest.json"
DEFAULT_OUTPUT_DIR = "aief_1_4_augmented_spectrum"
DEFAULT_SEED = "4619122171158768524"
DEFAULT_DT = 0.01
DEFAULT_SCALE_EPSILON = 1e-12
DEFAULT_PERTURBATION = 1e-8

K3_NODES = [2, 7, 11]
K3_EDGE_LIST = [(2,7,25), (2,11,29), (7,11,59)]
# Directed edges for EMA coherence tracking
DIRECTED_PAIRS = [(2,7),(7,2),(2,11),(11,2),(7,11),(11,7)]

def file_sha256(path):
    d = hashlib.sha256()
    with open(path, "rb") as h:
        while b := h.read(1024*1024):
            d.update(b)
    return d.hexdigest()

def load_production_modules():
    import AIEF_1_4_stationarity_perturbation_analysis_updated as base
    import AIEF_1_4_component_controller_audit as ca
    import AIEF_1_4_augmented_tangent_cocycle_analysis as aug
    return base, ca, aug

def safe_atomic_write_text(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tp = tempfile.mkstemp(dir=path.parent, prefix=f"{path.name}_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content); f.flush(); os.fsync(f.fileno())
        os.replace(tp, path)
    except Exception:
        if os.path.exists(tp): os.remove(tp)
        raise

def safe_atomic_write_csv(path, df):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tp = tempfile.mkstemp(dir=path.parent, prefix=f"{path.name}_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            df.to_csv(f, index=False); f.flush(); os.fsync(f.fileno())
        os.replace(tp, path)
    except Exception:
        if os.path.exists(tp): os.remove(tp)
        raise

def snapshot_state(state):
    """Deep-copy the mutable parts of a DynamicState for perturbation."""
    return {
        "B": state.B.copy(),
        "coherence_acc": state.coherence_acc.copy(),
        "history": copy.deepcopy(state.history),
    }

def restore_state(state, snap):
    state.B[:] = snap["B"]
    state.coherence_acc[:] = snap["coherence_acc"]
    state.history.clear()
    for entry in snap["history"]:
        state.history.append(entry.copy())

def advance_one_step(state, base, aug, model, caps, A, edges, eps):
    """Run one production step: intermediates + advance."""
    inter = aug.base_intermediates(state, model, caps, A, edges, eps)
    aug.advance_base_state(state, inter)
    return inter

def extract_k3_variables(state, inter, model, tau_delay=0.5):
    """Extract K3 state as a flat vector for Jacobian construction."""
    omega_arr = np.asarray(model["omega"], dtype=float)
    B_mat = state.B
    C_mat = state.coherence_acc
    history_list = list(state.history)
    h_old = history_list[0] if len(history_list) > 0 else np.zeros(len(omega_arr))
    h_new = history_list[-1] if len(history_list) > 0 else np.zeros(len(omega_arr))
    pf = inter["phase_factor"]

    # Reconstruct theta from phase_factor
    theta = np.zeros(len(omega_arr))
    for node_i, partner in [(2,7),(7,2),(11,2)]:
        const_ik = 0.5*(omega_arr[node_i]+omega_arr[partner])*tau_delay
        theta[node_i] = float(np.angle(pf[node_i,partner])+h_old[partner]+const_ik)

    vec = []
    # theta_i (3 vars)
    for i in K3_NODES:
        vec.append(theta[i])
    # h_old_i (3 vars)
    for i in K3_NODES:
        vec.append(h_old[i])
    # B_e (3 vars, undirected edges 25,29,59)
    for _, _, e in K3_EDGE_LIST:
        ia, ib = (2,7) if e==25 else ((2,11) if e==29 else (7,11))
        vec.append(float(B_mat[ia, ib]))
    # C (directed, real+imag = 12 vars)
    for ia, ib in DIRECTED_PAIRS:
        c = C_mat[ia, ib]
        vec.append(float(c.real))
        vec.append(float(c.imag))
    return np.array(vec)

def set_k3_variables(state, vec, model, tau_delay=0.5):
    """Write a flat vector back into the state.  Only modifies K3 entries."""
    omega_arr = np.asarray(model["omega"], dtype=float)
    B_mat = state.B
    C_mat = state.coherence_acc
    pf_recon = np.ones((len(omega_arr), len(omega_arr)), dtype=complex)

    idx = 0
    theta = np.zeros(len(omega_arr))
    for i in K3_NODES:
        theta[i] = vec[idx]; idx += 1
    h_old = np.zeros(len(omega_arr))
    for i in K3_NODES:
        h_old[i] = vec[idx]; idx += 1
    for _, _, e in K3_EDGE_LIST:
        ia, ib = (2,7) if e==25 else ((2,11) if e==29 else (7,11))
        B_mat[ia, ib] = vec[idx]
        B_mat[ib, ia] = vec[idx]
        idx += 1
    for ia, ib in DIRECTED_PAIRS:
        re = vec[idx]; im = vec[idx+1]; idx += 2
        C_mat[ia, ib] = complex(re, im)

    # Update history: set oldest entry to h_old
    history_list = list(state.history)
    if len(history_list) > 0:
        history_list[0][:] = h_old
        state.history.clear()
        for entry in history_list:
            state.history.append(entry)

def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--npz", default=DEFAULT_NPZ)
    p.add_argument("--manifest", default=DEFAULT_MANIFEST)
    p.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    p.add_argument("--seed", default=DEFAULT_SEED)
    p.add_argument("--dt", type=float, default=DEFAULT_DT)
    p.add_argument("--scale-epsilon", type=float, default=DEFAULT_SCALE_EPSILON)
    p.add_argument("--perturbation", type=float, default=DEFAULT_PERTURBATION)
    return p.parse_args()

def main():
    args = parse_args()
    for path in (args.npz, args.manifest):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Missing: {path}")

    base, ca, aug = load_production_modules()
    with open(args.manifest) as h:
        manifest = json.load(h)
    model = manifest["model"]
    dt = float(model["dt"])
    alpha = math.exp(-dt/float(model["T_window"]))
    r_ema = -np.log(alpha)/dt

    omega_arr = np.asarray(model["omega"], dtype=float)
    cap = (float(model["a"])-float(model["delta"]))/float(model["q"])
    caps = np.full(int(model["N"]), cap)
    N = int(model["N"])
    A, edges_mat = base.incidence_matrix(N)
    fs = int(manifest["protocol"]["future_steps"])
    eps_sc = args.scale_epsilon
    pert = args.perturbation

    # Replay to final steps to get the mature state
    print("Replaying to final time step...")
    with np.load(args.npz, allow_pickle=False) as data:
        state = base.load_split_state(data, args.seed)

    # Advance all the way to the end
    for step in range(fs):
        inter = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
        aug.advance_base_state(state, inter)

    # Now we're at step fs.  Extract baseline and build Jacobian.
    print("Building augmented Jacobian via finite differences...")
    snap = snapshot_state(state)

    # Baseline: advance one more step (need intermediates from current state)
    # Actually, we need the baseline vector BEFORE the step to compare with AFTER.
    # Run one step from the current state and extract before/after.
    inter_base = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
    vec_before = extract_k3_variables(state, inter_base, model)

    # Save the state before advancing
    snap_pre = snapshot_state(state)
    aug.advance_base_state(state, inter_base)
    inter_after = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
    vec_after = extract_k3_variables(state, inter_after, model)

    n_vars = len(vec_before)
    print(f"  State vector dimension: {n_vars}")
    print(f"  (3 theta + 3 h_old + 3 B + 12 C_realimag)")

    # Build Jacobian column by column
    J = np.zeros((n_vars, n_vars))

    for col in range(n_vars):
        # Restore pre-step state
        restore_state(state, snap_pre)

        # Perturb one variable
        vec_pert = vec_before.copy()
        delta = pert * max(1.0, abs(vec_pert[col]))
        vec_pert[col] += delta

        # Write perturbed state
        set_k3_variables(state, vec_pert, model)

        # Advance one step
        inter_p = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
        aug.advance_base_state(state, inter_p)
        inter_p2 = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
        vec_pert_after = extract_k3_variables(state, inter_p2, model)

        # Jacobian column: (F(x+delta) - F(x)) / delta
        J[:, col] = (vec_pert_after - vec_after) / delta

        if (col + 1) % 5 == 0 or col == n_vars - 1:
            print(f"  Column {col+1}/{n_vars} done")

    # --- Analyze eigenvalues ---
    evals = np.linalg.eigvals(J)
    # Convert to continuous-time rates: r = -log(|lambda|)/dt
    # For complex eigenvalues, the decay rate is -log(|lambda|)/dt
    abs_evals = np.abs(evals)
    rates = -np.log(np.maximum(abs_evals, 1e-300)) / dt

    # Sort by rate (slowest first = smallest rate)
    sorted_idx = np.argsort(rates)
    sorted_evals = evals[sorted_idx]
    sorted_rates = rates[sorted_idx]
    sorted_abs = abs_evals[sorted_idx]

    # Filter: exclude eigenvalues with |λ| < 1e-14 (numerical zero)
    # and eigenvalues with rate > 10 (very fast, not relevant)
    relevant = sorted_abs > 1e-14

    # Check for eigenvalues between mu_phase and r_ema
    mu_phase_ref = 0.689918
    gap_lower = r_ema
    gap_upper = mu_phase_ref

    in_gap = (sorted_rates > gap_lower) & (sorted_rates < gap_upper) & relevant
    n_in_gap = int(np.sum(in_gap))

    # --- Output ---
    od = Path(args.output_dir); od.mkdir(parents=True, exist_ok=True)

    # Save eigenvalues
    eval_rows = []
    for i in range(n_vars):
        if relevant[i]:
            eval_rows.append({
                "index": i,
                "eval_real": float(sorted_evals[i].real),
                "eval_imag": float(sorted_evals[i].imag),
                "abs_eval": float(sorted_abs[i]),
                "rate": float(sorted_rates[i]),
                "in_gap": bool(in_gap[i]),
            })
    eval_df = pd.DataFrame(eval_rows)
    safe_atomic_write_csv(od/"augmented_eigenvalues.csv", eval_df)

    # --- Report ---
    lines = [
        "="*70,
        "AIEF-1.4 Augmented Spectral Audit",
        "="*70,
        "",
        f"r_EMA:     {r_ema:.6f}",
        f"mu_phase:  {mu_phase_ref:.6f}",
        f"alpha:     {alpha:.12g}",
        f"dt:        {dt}",
        f"perturb:   {pert:.1e}",
        f"dimension: {n_vars}",
        "",
        f"Gap interval: ({gap_lower:.6f}, {gap_upper:.6f})",
        f"  (equiv. discrete: [{math.exp(-gap_upper*dt):.6f}, {math.exp(-gap_lower*dt):.6f}])",
        "",
        "-"*70,
        f"Eigenvalues in the gap: {n_in_gap}",
        "-"*70,
        "",
    ]

    if n_in_gap == 0:
        lines.append("  VERDICT: NO eigenvalues found between r_EMA and mu_phase.")
        lines.append("  The EMA pole alpha IS the unique slow pole of the augmented system.")
        lines.append("  The interpretation is complete for this replay.")
    else:
        lines.append(f"  VERDICT: {n_in_gap} eigenvalue(s) found in the gap.")
        lines.append("  There IS a mode slower than phase sync but faster than EMA.")
        lines.append("  The bottleneck interpretation needs revision.")
        lines.append("")
        gap_evals = eval_df[eval_df["in_gap"]]
        for _, r in gap_evals.iterrows():
            lines.append(f"  λ = {r['eval_real']:.6e} + {r['eval_imag']:.6e}i")
            lines.append(f"    |λ| = {r['abs_eval']:.6e},  rate = {r['rate']:.6f}")

    lines.extend([
        "",
        "-"*70,
        "All Relevant Eigenvalues (sorted by rate, slowest first):",
        "-"*70,
        f"  {'idx':>4} {'real':>14} {'imag':>14} {'|λ|':>14} {'rate':>12} {'in_gap':>8}",
        f"  {'-'*4} {'-'*14} {'-'*14} {'-'*14} {'-'*12} {'-'*8}",
    ])
    for _, r in eval_df.head(15).iterrows():
        lines.append(
            f"  {r['index']:>4} {r['eval_real']:>14.6e} {r['eval_imag']:>14.6e} "
            f"{r['abs_eval']:>14.6e} {r['rate']:>12.6f} {str(r['in_gap']):>8}"
        )
    if len(eval_df) > 15:
        lines.append(f"  ... ({len(eval_df)-15} more eigenvalues)")

    lines.extend([
        "",
        "-"*70,
        "Reference rates:",
        "-"*70,
        f"  Phase transverse (fastest):  {mu_phase_ref:.6f}",
        f"  Phase transverse (slowest):  {mu_phase_ref:.6f}",
        f"  Weight cocycle (left):       {-math.log(0.998738)/dt:.6f}",
        f"  Weight cocycle (right):      {-math.log(0.499369)/dt:.6f}",
        f"  EMA (alpha):                 {r_ema:.6f}",
        "",
        "Evidence class: diagnostic mechanism exploration.",
        "No interpretation is forced.  The eigenvalues speak.",
    ])

    report = "\n".join(lines)
    safe_atomic_write_text(od/"augmented_spectrum_report.txt", report)

    mf = {
        "analysis": "AIEF-1.4 augmented spectral audit",
        "evidence_class": "diagnostic mechanism exploration",
        "seed": args.seed,
        "parameters": {"dt":dt, "r_EMA":r_ema, "alpha":alpha,
                        "mu_phase":mu_phase_ref,
                        "perturbation":pert},
        "outputs": ["augmented_eigenvalues.csv",
                     "augmented_spectrum_report.txt",
                     "analysis_manifest.json"],
        "tested_hypothesis": "No eigenvalue in (r_EMA, mu_phase)",
        "not_a_proof": True,
    }
    safe_atomic_write_text(od/"analysis_manifest.json",
                           json.dumps(mf, indent=2)+"\n")

    print(report)
    print(f"\n[SUCCESS] Artifacts saved to: '{od.resolve()}'")

if __name__ == "__main__":
    main()
